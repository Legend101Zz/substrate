# 16 — caching-and-cdn-strategies — RECONCILED research (`_research.md`)

> **Phase 1 deliverable (NO course prose).** Synthesis of four factchecked clusters into the
> standard six sections (ADR-001: each cluster keeps its deep `_research_<cluster>.md`; this file
> reconciles overlaps, states the cross-cluster thesis, consolidates sources + gaps). Every
> `[UNVERIFIED from fetched source]` / residual gap from the clusters is preserved here in intent.
>
> **Cluster files (read for full depth):**
> - A — `_research_cache-placement-and-patterns.md` (the placement ladder client→CDN→proxy→app→
>   remote→DB; cache-aside / read-through / write-through / write-back / write-around; read vs write path)
> - B — `_research_eviction-and-sizing.md` (eviction reuse from 08; hit-ratio-vs-working-set Zipf
>   math; skew sensitivity; sizing to the knee) — **all math VERIFIED BY RECOMPUTATION**
> - C — `_research_consistency-and-invalidation.md` (TTL vs explicit vs versioned keys; validation/
>   304; stampede `R·T_r` + coalescing/leases/SWR; negative caching; stale-fill race fix)
> - D — `_research_cdn-and-edge.md` (PoPs/anycast; pull vs push; cache key/`Vary`; origin shielding;
>   Cache-Control/ETag/conditional; purge/soft-purge/versioned URLs; edge compute)
> - Factcheck — `_factcheck_phase1.md` (math by recomputation; mechanisms by reuse of 03/06/08/10/13/
>   14/15; attributions `[UNVERIFIED]`; **0 blockers**)
>
> **Reconciliation verdict:** 16 is reconciled on the basis that its load-bearing content — *where*
> to cache (A), *how big + which victim* (B), *how stale + how to stop stampedes* (C), and *how to
> push it to the geographic edge* (D) — is verified end-to-end: recomputation for all sizing/stampede
> math, reuse of line-checked 03/06/08/10/13/14/15 for every mechanism, **0 factcheck blockers**. The
> remaining gaps are *canonical/RFC/vendor attributions* (RFC 9111/5861, Nishtala NSDI 2013, Breslau
> INFOCOM 1999, XFetch VLDB 2015, vendor CDN/anycast specifics), all uniformly network-blocked (8th
> session, HTTP 000 on every non-Lamport host) and carried forward `[UNVERIFIED]`. None is
> load-bearing for the method; none may harden into Phase-2 prose until fetched.

---

## The cross-cluster thesis (what this sub-course actually teaches)

16 is **the shared sink for the read-side pressures 13/14/15 hand off, and a special case of 15's
replication.** 14 ends with hot shards / celebrity keys (a Zipf head no shard-key can spread); 15
ends with read replicas that scale reads only by accepting replication lag (staleness). A cache sits
in front of both and is *itself another deliberately-stale replica* — one whose staleness is bounded
by TTL/invalidation instead of a replication log. So the whole sub-course is one question:

> **You want a faster, cheaper copy of the truth. Where do you put it, how much of the truth fits,
> how wrong is it allowed to be, and how do you keep it from melting the origin when it misses?**

The four clusters answer that in order:

1. **A — placement decides reach vs proximity, and the write pattern decides where you pay.** Caching
   is a *ladder* (client → CDN → reverse-proxy → app-local → remote → DB buffer), each rung trading
   how many users share it against how cheap the hit is — you cache at several rungs because no rung
   is both close to everyone and coherent for everyone. The five read/write patterns (cache-aside,
   read-through, write-through, write-back, write-around) are the cross-product of "does the write
   touch the cache?" × "is the SoT write synchronous?" — i.e. *where* you pay: write latency,
   durability window, or stale-read risk.
2. **B — sizing is knee-finding on the Zipf working-set curve.** Caching works *because the working
   set ≪ keyspace*: at N=1e6, α=1, caching 1% of keys buys a **68%** hit ratio (verified). The curve
   is concave (50× memory only moves 0.68→0.95), so you size to the knee, never the keyspace. Hit
   ratio is the master metric: origin load = `(1−h)`, so the last nines (99→99.9%) barely move latency
   but cut origin load 10× — sizing protects the origin (13's tail), not the average. And skew (α)
   dominates everything (top-1% hit ratio: 0.36 at α=0.8 → 0.91 at α=1.2) — measure α before
   promising anything.
3. **C — a cache is a replica, so caching IS a consistency problem (15).** Invalidation is a ladder
   of coordination cost: TTL (no coordination, bounded staleness) → versioned/immutable keys (one
   tiny pointer to update, nothing to purge) → explicit invalidation (must reach *every* copy on
   every rung/region). The cache's nastiest emergent behavior is the **stampede**: a hot key's expiry
   dumps `R·T_r` synchronized origin calls (verified: up to 2,000×), so the cache can *raise* peak
   origin load exactly when the origin is hot — collapsed back to 1 by coalescing/leases/
   stale-while-revalidate. Plus negative caching (cache absence) and the stale-fill race fix (a
   version/token, same shape as 15's conflict detection).
4. **D — the CDN is that ladder's top rungs, geo-distributed, because latency has a physical floor.**
   Speed of light bounds cross-region RTT, so the only lever is moving bytes closer: PoPs near users,
   reached by anycast (one IP announced from many places; the network picks the nearest), filled by
   pull (demand → working set, B) or push (predictably-hot large objects). The cache key (`Vary`) is
   a hit-ratio lever disguised as config; origin shielding is coalescing across the PoP fleet (N
   misses → 1); freshness is Cache-Control/ETag/conditional-304 + SWR; and the clean invalidation
   answer at global scale is **versioned/content-addressed URLs** (nothing to purge).

The through-line, identical to 13/14/15: **push the hard work toward the edge of the system so the
expensive case stays rare** — cache the Zipf head close to the user, let demand reveal the working
set, buy the weakest freshness guarantee the user can't perceive, and never let a miss fan out into a
herd. Three primitives do double duty across clusters: **request coalescing** (C stampede control =
D origin shielding = one fetch per cold object), **versioned keys** (C cleanest invalidation = D
content-addressed CDN assets), and the **staleness ladder** (15's read-your-writes/monotonic/
consistent-prefix, re-pointed at cache layers).

---

## 1. Key mechanisms (consolidated)

- **Placement ladder** client → CDN/edge → reverse-proxy → app-local → remote (Redis/Memcached) → DB
  buffer; reads fall down the ladder until a hit; each rung = reach-vs-proximity trade. *(A §1.2)*
- **App-local vs remote** = proximity vs coherence; per-instance caches duplicate + multiply
  invalidation surfaces; near/far two-tier = head/tail (W-TinyLFU window across machines). *(A §1.3)*
- **Five patterns:** cache-aside (lazy, app-owned, stale-fill race), read-through (cache-owned miss
  path), write-through (sync SoT, no stale-fill on key, write latency), write-back (async SoT, lowest
  latency, durability window), write-around (skip cache on write). *(A §1.4; reuse 08)*
- **Eviction (reuse 08):** LRU/LFU/2Q/ARC/TinyLFU/W-TinyLFU; admission ≠ eviction; sampled/segmented
  approximations; slabs. *(B §1.1–1.2)*
- **Hit ratio is master metric:** `t_avg=h·t_hit+(1−h)·t_miss`, origin load `=(1−h)`; last nines
  protect origin. **VERIFIED.** *(B §1.3)*
- **Zipf working-set curve:** hit ratio `=H(k,α)/H(N,α)`; 1% of N=1e6 → 68% (α=1); concave →
  diminishing returns → size to the knee; α dominates. **ALL VERIFIED BY RECOMPUTATION.** *(B §1.4–1.6)*
- **Invalidation taxonomy:** TTL (no coordination) → versioned keys (tiny pointer) → explicit
  (every copy). *(C §1.2)*
- **Validation/304:** ETag/If-None-Match, Last-Modified/If-Modified-Since → cheap revalidation
  without re-transfer. *(C §1.3; D §1.7)*
- **Stampede `herd≈R·T_r`** (VERIFIED) → coalescing/singleflight/leases/stale-while-revalidate/TTL
  jitter/XFetch collapse to ~1. *(C §1.4–1.5; reuse 08)*
- **Negative caching** (cache absence) + Bloom pre-filter (06). *(C §1.6)*
- **Stale-fill race fix** = lease/CAS/delayed-double-delete (version detects intervening write; same
  shape as 15 conflict). *(C §1.7; reuse 08)*
- **CDN = geo-distributed PoPs** (reverse-proxy caches, 10) near users because RTT has a physical
  floor (13). *(D §1.1–1.2)*
- **Anycast** (one prefix, many BGP announcements → nearest PoP, auto-failover); DNS-steering
  alternative. *(D §1.3; reuse 03)*
- **Pull vs push** = demand-fill (working set, B) vs pre-warm (predictably-hot large objects). *(D §1.4)*
- **Cache key/`Vary`** = hit-ratio lever; over-specific keys shatter the working set. *(D §1.5; reuse 08)*
- **Origin shielding** = request coalescing across the PoP fleet (N misses → 1). *(D §1.6)*
- **Edge freshness:** Cache-Control/s-maxage + validators + SWR/stale-if-error. *(D §1.7)*
- **Purge / soft-purge / versioned URLs** — versioned/content-addressed assets = the clean edge
  invalidation (nothing to purge). *(D §1.8)*
- **Edge compute** — co-locate logic with the cache to make dynamic responses partly edge-cacheable. *(D §1.9)*

## 2. Foundational sources (consolidated)

**VERIFIED BY RECOMPUTATION this session** (`_factcheck_phase1.md`, pure Python, no deps):
Zipf hit ratio `H(k,α)/H(N,α)` (1%/10%/20% at N=1e3,1e6; α=0.8/1.0/1.2; monotone curve);
`t_avg=h·t_hit+(1−h)·t_miss` + origin fraction `(1−h)`; stampede multiplier `herd≈R·T_r` (up to
2,000×) and coalescing-to-1.

**Verified by REUSE (line-checked earlier — NOT re-fetched):**
- Cache invariant, cache-aside, TTL=logical-invalidity, eviction/admission, slabs, leases/
  singleflight/SWR, stale-fill race + fixes — **08** `_research.md` §§1.1–1.7 (Redis `server.h`/
  `evict.c`/`expire.c`, Memcached `items.c`/`slabs.c`, Caffeine `FrequencySketch.java`,
  `singleflight.go`).
- Bloom filter (negative-cache pre-filter), Merkle/hashing intuition — **06**.
- Reverse-proxy `proxy_cache`, event-driven PoP — **10** (NGINX `release-1.31.1`).
- TCP 3-way + TLS 1.2/1.3 handshake RTTs, IP/BGP/DNS substrate — **03**.
- Latency hierarchy / propagation floor / read fan-out (`1−(1−q)^N`) — **13** (verified).
- Hot shards / celebrity keys / Zipf skew — **14**.
- Cache-as-replica staleness ladder (read-your-writes/monotonic-reads/consistent-prefix) — **15**
  Cluster B + **11** consistency models.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when net heals):**
- *(A,C,D)* RFC 9111 (HTTP caching: Cache-Control/s-maxage/Age/Vary/validators/304/unsafe-method
  invalidation) + RFC 5861 (stale-while-revalidate/stale-if-error) + RFC 7234 — carried from 08.
- *(A,C)* Nishtala et al. "Scaling Memcache at Facebook" NSDI 2013 (cache-aside default, leases,
  17K→1.3K herd, cross-region delete stream) — carried from 08.
- *(B)* Breslau et al. "Web Caching and Zipf-like Distributions" INFOCOM 1999 (empirical web α);
  Cormode & Muthukrishnan 2005 (CMS bounds); ARC pseudo-code/patent — carried from 08.
- *(C)* Vattani et al. "Optimal Probabilistic Cache Stampede Prevention" VLDB 2015 (XFetch).
- *(D)* RFC 4786 (anycast ops); vendor CDN architecture/purge/edge-compute (Cloudflare/Fastly/
  Akamai/CloudFront); anycast/BGP + DNS-steering specifics; exact RTT/propagation figures.

## 3. "Why it's this way" — the forcing functions (consolidated)

- **No single best place to cache** — the latency hierarchy (13) is a ladder; each rung trades reach
  vs proximity, so you cache at several. *(A)*
- **Reads and writes have different costs** — the five patterns are conservation-of-pain: you can't
  minimize write latency, guarantee durability, and guarantee no stale reads at once (15's
  durability-vs-latency dial in cache form). *(A)*
- **Caching works because working set ≪ keyspace** (Zipf head) — and the curve is concave, forcing a
  knee, not a maximum; α dominates the answer. *(B)*
- **Hit ratio is an origin-load metric** — origin load `=(1−h)`; the last nines are about backend
  survival under 13's fan-out, not the mean. *(B)*
- **A cache is a replica → inherits the consistency tax (15)** — no cheap always-fresh
  coordination-free cache; TTL/versioned/explicit each pay differently. *(C)*
- **Caches batch quiet into bursts** — a hot key's expiry dumps `R·T_r` synchronized misses; the
  cache can raise peak origin load → coalescing/leases/SWR mandatory for hot keys. *(C)*
- **The edge exists because latency has a physical floor (13)** — speed of light bounds RTT; move
  bytes closer; anycast makes "nearest" automatic; pull lets demand reveal the per-PoP working set;
  shielding collapses the multiplied stampede; versioned URLs dodge global purge. *(D)*

## 4. Common misconceptions to preempt (consolidated)

- "Add a cache = one box." It's a *ladder*; the bug is the layer you forgot (browser, CDN). *(A)*
- "More layers = more correct." More layers = more stale copies = harder coherence. *(A,C)*
- "Write-through makes everything consistent." Only the written key vs SoT; other layers keep their
  own TTLs. "Write-back is a faster write-through." It acks non-durable data (15 lost-write). *(A)*
- "Bigger cache ⇒ proportionally better." Concave curve; find the knee. "Hit ratio is a latency
  metric." It's an origin-load metric `(1−h)`; the last nines protect the backend. *(B)*
- "LRU is good enough everywhere." Scans pollute it; admission (TinyLFU) saves the small cache. "A
  90% hit ratio is great." 90% = 10% to origin, which 13's fan-out can still melt. "Skew is a
  detail." α is the biggest driver. *(B)*
- "Set a TTL and you're consistent." Bounded eventual staleness, not freshness (15). "Invalidate on
  write = always fresh." Only if it reaches every copy; missed rung = silent staleness. *(C)*
- "Invalidation after a write is enough." Stale-fill race needs a lease/CAS/double-delete. "A cache
  only reduces origin load." Stampede `R·T_r` can spike it. "singleflight is a cache." It only
  dedups. "stale-while-revalidate is strong." Deliberately serves stale. "Versioned keys are a
  hack." They're the cleanest invalidation. *(C)*
- "A CDN just makes the site faster." It's a global cache tier — inherits all of C's problems × PoP
  count. "Anycast = geographically nearest." BGP-topologically nearest. "Push > pull." Pull fits the
  long tail. "Cache key = URL." `Vary`/cookies/query change it; mis-keying collapses hit ratio.
  "Purge is instant + free." Global cold miss + stampede; prefer soft-purge/versioned URLs. "Dynamic
  can't be edge-cached." SWR/short-TTL/ESI/edge-compute say otherwise. "More PoPs = strictly
  better." More copies = harder invalidation + more origin misses without shielding. *(D)*

## 5. Best build-your-own target(s) (consolidated)

- **Pattern bake-off** (all five patterns over one SoT; measure read/write latency, durability
  window via kill-during-write-back, stale-read count). *(A; pairs 07/08)*
- **Placement-ladder simulator** (client→CDN→proxy→app→remote→DB with 13 latency costs; replay Zipf;
  hit ratio + latency per rung). *(A,B,D)*
- **Zipf hit-ratio simulator + knee-finder** (trace → exact/sampled-LRU/LFU/TinyLFU at many sizes;
  overlay analytic `H(k,α)/H(N,α)`; solve min cache for origin-survivable `(1−h)·QPS`). *(B; pairs 13)*
- **Stampede reproducer + mitigations** (confirm `R·T_r`; collapse to 1 via singleflight/lease/SWR).
  **Invalidation bake-off** (TTL vs explicit vs versioned; staleness window + messages; expose a
  missed invalidation = monotonic-reads violation). **Stale-fill race harness** (resurrect old value,
  fix with CAS/lease/double-delete). *(C; pairs 08/15)*
- **Mini multi-PoP CDN** (N reverse-proxy caches + origin; nearest-PoP routing by latency table; pull
  + Cache-Control/ETag/304; add origin shield → origin misses N→1). **Cache-key lab** (URL vs +query
  vs +`Vary` vs +cookie → hit-ratio collapse). **Purge vs versioned-URL demo.** *(D; pairs 10/03/13)*

## 6. Open questions / gaps to close (consolidated — preserved verbatim in intent)

- **All canonical/RFC/vendor attributions are network-blocked** `[UNVERIFIED]` (8th session, HTTP 000
  on every non-Lamport host): RFC 9111 / 5861 / 7234 / 4786, Nishtala NSDI 2013, Breslau INFOCOM
  1999, Vattani XFetch VLDB 2015, Cormode-Muthukrishnan 2005, ARC pseudo-code/patent, and vendor
  CDN/anycast/edge-compute specifics. The *math/method* is verified by recomputation + reuse; the
  *citations / exact RFC header wording / vendor routing behavior / real-world α / exact ms RTTs*
  need primaries when the network heals. Teach mechanisms now; do NOT harden specifics into Phase-2
  prose until fetched.
- **Carried from 08 (still HTTP 000):** RFC 9111/5861, Nishtala, Count-Min bounds, ARC details, XFetch
  formula, write-through/write-back taxonomy primary anchor.
- **Disagreements to resolve with sources:** default cache-aside stale-fill fix to teach (lease vs CAS
  vs delayed double-delete — likely all three on the version/token through-line); whether to teach the
  Zipf hit ratio via the IRM analytic model (exact, but assumes independent references) or the
  simulator (realistic temporal locality) — likely simulator-first; how deep to go on anycast/BGP
  before deferring to 03 + appendix O.
- **Boundary discipline (cross-link, do NOT duplicate):**
  - eviction/admission *internals* (slabs, sampled LRU, TinyLFU sketch, Redis/Memcached source) =>
    **08** (+ appendix G Redis). 16 reuses; owns only sizing *math*.
  - distributed-cache *sharding/replication* of the remote tier => **14/15**.
  - TCP/TLS/HTTP2/HTTP3 internals => **03/10** (10's TLS/HTTP2/HTTP3 gaps still open); anycast/BGP +
    DNS internals => **03** + appendix **O**.
  - cross-region invalidation *transport* (delete streams, purge fan-out, pub/sub) => **17**
    (async/event-driven) — cross-link, don't re-derive the messaging layer.
  - origin-protection under tail/fan-out + hedged requests => **13/20**; SLOs on hit ratio/origin load
    => **19**; capacity headroom => **13/20**.
  - the consistency/staleness *theory* the cache inherits => **11/15**; CDN as a real-system deep dive
    is a candidate future appendix.
- **Next 16 work (optional, before Phase 2 prose):** fetch the blocked RFCs + Nishtala + Breslau +
  XFetch + vendor CDN specifics when a healthier network exists and upgrade the `[UNVERIFIED]` flags;
  otherwise 16 is research-complete at the *method/math* level. **Next Phase-1 batch: 17-21** (Part
  II). **17 (async-queues-and-event-driven-architecture)** is the natural next start — it absorbs the
  write-back flush, cross-region invalidation transport, and CDC/log fan-out that 15 (logical log →
  CDC) and 16 (Cluster C/D invalidation transport) both hand off.
