# 16 — caching-and-cdn-strategies — Cluster D: CDN + edge

> **Phase 1 research brief (NO course prose).** Standard six sections. The CDN is the geographic
> instantiation of the placement ladder (A), governed by the invalidation taxonomy (C), sized by the
> working-set math (B), and absorbing the read fan-out / locality pressure of 13. HTTP-caching
> semantics (RFC 9111/5861), anycast/BGP details, and vendor specifics are `[UNVERIFIED from fetched
> source]` (HTTP 000, 8th session); mechanisms are reasoned from first principles + reuse of
> line-verified 03 (networking), 08, 10, 13, 15.

Cluster scope: pushing the cache to the network edge — why proximity matters, how requests reach the
nearest PoP (anycast), how content gets there (push vs pull), how the cache key is computed, how
origins are protected (shielding), and how edge content is kept fresh + purged.

---

## 1. Key mechanisms

### 1.1 A CDN is the placement ladder's top rungs, geo-distributed (REUSE A + 13)

A CDN is a fleet of **Points of Presence (PoPs)** — shared reverse-proxy caches (10) placed in many
physical locations near users. It is rung 2 of Cluster A's ladder (CDN/edge), made planet-scale. Its
entire reason to exist is the 13 latency hierarchy: cross-region RTT is tens-to-hundreds of ms and is
bounded by the speed of light, so the only way to cut it is to **move the bytes physically closer**.
A CDN trades many-copies (and thus C's invalidation problem at global scale) for ~local-RTT reads.

### 1.2 Why edge proximity is load-bearing, not a nicety (REUSE 13)

- **Latency floor is physical.** Light in fiber ≈ 200,000 km/s; a 10,000 km round trip is ~100 ms of
  pure propagation no protocol can remove. A PoP 50 km away turns that into sub-ms propagation. `[ms
  values illustrative; exact RTTs UNVERIFIED]`.
- **TCP/TLS handshakes multiply RTT.** Connection setup is several round trips (03: TCP 3-way, TLS
  1.2 = 2 RTT, TLS 1.3 = 1 RTT); terminating them at the edge instead of the origin saves
  *handshake × RTT*, often more than the transfer itself for small objects.
- **Read fan-out absorption.** The edge serves the Zipf head (B) for a whole region from one PoP,
  collapsing regional read fan-out before it crosses the backbone (the 13/14 hot-key pressure, now
  geo-scoped).

### 1.3 Anycast routing — how a request finds the nearest PoP

The same IP prefix is announced from many PoPs via BGP; the network routes each client to the
*topologically nearest* announcement (anycast). The client opens one connection to one address; the
network decides which PoP answers. **Pro:** no client-side logic, automatic failover (withdraw a
PoP's announcement and traffic reroutes). **Con:** "nearest" is BGP-topological, not geographic, and
can flap; long-lived connections can in principle re-route (mostly a non-issue for short HTTP).
Alternative/complement: **DNS-based steering** (GeoDNS returns a PoP-specific address per resolver
location). Mechanism reasoned from 03 (IP/BGP/DNS); `[BGP/anycast specifics UNVERIFIED from fetched
source]`.

### 1.4 Pull (lazy) vs push (eager) CDNs (REUSE A's demand-fill vs pre-warm)

- **Pull CDN (origin pull).** PoP is cache-aside (A §1.4): on a miss it fetches from origin,
  caches per the object's `Cache-Control`/TTL, serves. Demand-filled — only requested objects are
  cached (B working-set logic at the edge). Default for web content; first request per object per PoP
  pays the origin round trip (a built-in cold-miss + potential stampede, C §1.4 — hence shielding,
  §1.6).
- **Push CDN.** You upload objects to the CDN ahead of demand (pre-warm). Good for large, predictably
  hot files (video segments, release assets) where the first-request penalty is unacceptable.
  Trades storage + upload coordination for no cold miss.

### 1.5 The cache key — what makes two requests "the same object" (REUSE C/08 `Vary`)

A PoP must decide which requests share a cached entry. The cache key is normally the URL, but can
include/exclude: host, query-string params (include `?id=` but strip tracking `?utm_*`), selected
headers (`Vary: Accept-Encoding` → separate gzip/br copies; `Vary: Accept-Language`), and cookies
(usually stripped — cookied responses are often uncacheable). **Key design is a hit-ratio lever
(B):** an over-specific key (keying on a volatile header/cookie) shatters one object into many
near-duplicate entries and collapses the hit ratio; an over-broad key serves the wrong variant. This
is `Vary` semantics (RFC 9111, 08 §1.7 `[UNVERIFIED]`) made operational.

### 1.6 Origin shielding — a mid-tier to protect the origin (REUSE C stampede + A ladder)

With many edge PoPs each doing pull, a cold object or a purge can produce *one origin miss per PoP*
— a distributed stampede (C §1.4) scaled by PoP count. **Origin shield**: designate one PoP (or a
mid-tier cache) that all other PoPs miss *through*, so the origin sees at most one miss per object
regardless of PoP count. This is request coalescing (C §1.5) applied across the PoP fleet — collapse
N PoP misses to 1 origin fetch. It is also another rung inserted into Cluster A's ladder.

### 1.7 Freshness at the edge — Cache-Control, validators, conditional requests (REUSE C/08)

The origin governs edge caching with HTTP headers (RFC 9111 `[UNVERIFIED]`, carried from 08):
- `Cache-Control: max-age` / `s-maxage` (shared-cache TTL) / `public|private` / `no-store` /
  `no-cache` (cache but always revalidate) — the TTL strategy (C §1.2).
- Validators `ETag` + `If-None-Match`, `Last-Modified` + `If-Modified-Since` → `304 Not Modified`
  revalidation without re-transfer (C §1.3) — lets an expired edge entry be confirmed cheaply.
- `stale-while-revalidate` / `stale-if-error` (RFC 5861 `[UNVERIFIED]`) → serve stale at the edge
  during refresh / origin outage; removes the edge herd + latency cliff (C §1.5).

### 1.8 Purge and soft-purge — explicit edge invalidation (REUSE C §1.2)

The edge is the hardest place to do explicit invalidation (C): copies live in every PoP. Mechanisms:
- **Hard purge** — evict the object from all PoPs now (next request re-pulls). Immediate but causes a
  global cold miss + potential stampede (mitigated by shielding, §1.6).
- **Soft purge** — mark stale rather than evicting, so `stale-while-revalidate` serves the old copy
  until a fresh pull lands — no cold-miss cliff.
- **Versioned / content-addressed URLs** (C §1.2 versioned keys) — the preferred CDN pattern:
  `bundle.8a3f.js` is immutable + long-TTL + never purged; a deploy changes the *reference* (a small,
  controllable HTML/manifest invalidation), not the asset. This is why static-asset pipelines
  fingerprint filenames.

### 1.9 Edge compute — moving logic, not just bytes, to the PoP

Modern CDNs run code at the edge (Cloudflare Workers, Lambda@Edge, Fastly Compute) to do per-request
work near the user: cache-key normalization, A/B routing, auth checks, personalization-at-edge,
assembling cacheable fragments (edge-side includes). Lets *dynamic* responses become partly edge-
cacheable. `[Vendor specifics UNVERIFIED]`; teach the pattern (compute co-located with the cache to
keep more traffic from reaching origin), not a vendor's API.

## 2. Foundational sources (consolidated)

**Verified by REUSE (line-checked earlier, NOT re-fetched):**
- Latency hierarchy / propagation floor / RTT-bound cross-region cost / read fan-out — 13
  `_research.md` (+ Cluster A fan-out math, verified).
- TCP 3-way + TLS 1.2/1.3 handshake RTT counts; IP/BGP/DNS routing substrate — 03
  `_research.md` (networking-from-first-principles).
- Reverse-proxy cache (`proxy_cache`), event-driven proxy as the PoP building block — 10
  (NGINX `release-1.31.1`).
- `Vary`/cache-key, `ETag`/`304` validation, TTL vs invalidation, stampede + coalescing, stale-
  while-revalidate, versioned keys — 08 §1.7 + 16 Cluster C (RFC 9111/5861 mechanisms verified by
  reuse; the RFCs themselves flagged below).
- Cache-as-replica staleness ladder; "truth is the origin" — 15 Clusters A/B + 16 Cluster C.

**Blocked primaries — `[UNVERIFIED from fetched source]` (HTTP 000 this session):**
- RFC 9111 (HTTP caching: `Cache-Control`, `s-maxage`, `Age`, `Vary`, validators, invalidation after
  unsafe methods) — `https://www.rfc-editor.org/rfc/rfc9111.txt`. Carried from 08.
- RFC 5861 (`stale-while-revalidate`, `stale-if-error`) — `https://www.rfc-editor.org/rfc/rfc5861.txt`.
- RFC 7234 (predecessor, for historical wording) — HTTP 000.
- Anycast/BGP behavior + DNS-steering specifics (RFC 4786 anycast operations; vendor CDN docs:
  Cloudflare/Fastly/Akamai/CloudFront architecture + purge APIs + edge-compute). All HTTP 000.
- Exact propagation/RTT figures — illustrative only; not fetched.

## 3. "Why it's this way" — the forcing functions

- **The edge exists because latency has a physical floor (13).** Speed of light bounds cross-region
  RTT; the only lever is moving bytes closer, so caches go to PoPs near users — proximity is physics,
  not optimization.
- **Anycast exists to make "nearest PoP" automatic.** One IP, many announcements; the network's own
  routing picks the closest and reroutes on failure — no client logic, at the cost of BGP-topological
  (not geographic) nearness.
- **Pull is the default because demand reveals the working set (B).** You cannot pre-push the whole
  keyspace to every PoP; let traffic fill each PoP's working set, push only the predictably-hot large
  objects.
- **Cache-key design is a hit-ratio lever (B) disguised as config.** Too-specific keys shatter the
  working set across PoP memory; this is the single most common CDN misconfiguration.
- **Shielding exists because many PoPs multiply the stampede (C).** N PoPs pulling cold = N origin
  misses; a shield collapses them to 1 — coalescing across the fleet.
- **Versioned URLs win at the edge** because explicit global purge is the hardest invalidation (C):
  immutable content-addressed assets need no purge; you invalidate only the tiny reference.

## 4. Common misconceptions to preempt

- "A CDN just makes the site faster." It is a globally-distributed cache tier — it inherits *all* of
  C's consistency/invalidation problems, now multiplied by PoP count.
- "Anycast sends users to the geographically nearest PoP." It routes to the BGP-*topologically*
  nearest announcement, which is usually but not always the geographically closest.
- "Push CDNs are better (eager > lazy)." Pull is right for the long tail (demand-fill, B); push only
  pays for predictably-hot large objects — same eager-vs-lazy trade as A's patterns.
- "The cache key is just the URL." Headers/cookies/query params change it via `Vary`; mis-keying is
  the top cause of a collapsed CDN hit ratio (§1.5).
- "Purge is instant and free." Hard purge causes a global cold miss + stampede; prefer soft-purge or
  versioned URLs (§1.8).
- "Dynamic content can't be cached at the edge." Conditional requests, short TTL + SWR, fragment/ESI
  caching, and edge compute make much of it edge-cacheable (§1.7/§1.9).
- "More PoPs = strictly better." More PoPs = more copies = harder invalidation and more origin misses
  without shielding (§1.6) — proximity helps reads, multiplies coherence cost.
- "TLS at the edge is just security." Terminating handshakes at the edge saves *handshake × RTT*,
  often the dominant cost for small objects (§1.2, 03).

## 5. Best build-your-own target(s)

- **Mini multi-PoP CDN:** N reverse-proxy caches (10) + one origin; route requests to the "nearest"
  PoP by a latency table (13); implement pull caching with `Cache-Control`/`ETag`/`304`; measure
  hit ratio per PoP and origin load. Then add an **origin shield** and watch origin misses collapse
  from N→1 (§1.6).
- **Cache-key lab:** replay a trace while varying the key (URL only vs +query vs +`Vary` header vs
  +cookie); plot hit ratio collapse from over-specific keys (§1.5, B).
- **Purge vs versioned-URL demo:** deploy v1→v2 of an asset via hard purge (observe global cold miss/
  stampede) vs content-addressed filename (no purge, instant cutover) (§1.8, C).
- **Edge-revalidation harness:** expired edge entry + `If-None-Match` → `304`; measure bytes saved vs
  full refetch (§1.7).

## 6. Open questions / gaps to close (preserved)

- All HTTP-caching RFCs (9111, 5861, 7234) `[UNVERIFIED]` (HTTP 000) — carried from 08; the load-
  bearing freshness/validator/`Vary` semantics are reused-verified at the mechanism level but the
  exact header wording must NOT harden into prose until fetched.
- Anycast/BGP + DNS-steering + vendor CDN architecture/purge/edge-compute specifics all `[UNVERIFIED]`
  — teach the *patterns* (proximity, anycast, pull/push, shield, versioned URLs, edge compute), not
  any vendor's API or exact routing behavior.
- RTT/propagation figures are illustrative; do not assert specific ms in prose without a source.
- Boundary: TCP/TLS/HTTP2/HTTP3 *internals* => 03 + 10 (10's TLS/HTTP2/HTTP3 gaps still open);
  anycast/BGP *internals* => 03 + appendix O (cloud-infra); CDN as a real-system deep dive could be a
  future appendix. 16 owns the *caching* view of the edge only.
- Cross-region invalidation transport (purge fan-out) overlaps 17 (event-driven) — cross-link.
