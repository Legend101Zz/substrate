# 16 — caching-and-cdn-strategies — Cluster C: consistency + invalidation

> **Phase 1 research brief (NO course prose).** Standard six sections. The staleness *theory* (the
> consistency/anomaly ladder) is REUSED from 15 (Cluster B) and 11 (consistency models); the
> stampede *mechanisms* (leases, singleflight, stale-while-revalidate) are REUSED from 08 (line-
> verified). The NEW load-bearing content is (a) the **invalidation taxonomy** for a *distributed*
> cache ladder, and (b) the **stampede load-multiplier math**, which is **VERIFIED BY
> RECOMPUTATION** this session. Vendor/RFC attributions are `[UNVERIFIED from fetched source]`
> (HTTP 000, 8th session).

Cluster scope: a cache is a deliberately-stale replica. This cluster answers *how stale may it be*
(invalidation policy) and *how do you stop the cache from amplifying load when it misses* (stampede
control) — the two correctness problems that placement (A) and sizing (B) create.

---

## 1. Key mechanisms

### 1.1 A cache is a replica, so caching IS a consistency problem (REUSE 15/11)

15 §thesis: once a fact lives in more than one place, you must decide how stale a reader may be. A
cache is exactly that — an extra, deliberately-stale copy of the SoT, whose staleness is bounded by
**TTL or invalidation** instead of a replication log. So 16's consistency story is 15's staleness
ladder re-pointed at caches: read-your-writes ("I updated my profile but the cache shows the old
one"), monotonic-reads ("two page loads, the value went backwards because two cache nodes disagree"),
and consistent-prefix all reappear, and the *same cheapest-guarantee-that-hides-the-anomaly*
discipline applies. Strong cache coherence is available but expensive; most caches deliberately buy
a weaker rung.

### 1.2 The three invalidation strategies (the core NEW taxonomy)

- **TTL / expiry (time-based).** Every entry carries a max age; after it, the entry is stale and
  refetched. **Pro:** zero coordination — the cache and SoT never talk about invalidation. **Con:**
  bounded staleness = the TTL; short TTL → fresh but low hit ratio + stampede risk (§1.4), long TTL →
  high hit ratio but stale. TTL is the *default* because it is the only strategy with no write-path
  coupling (08 §1.2: logical invalidity before reclamation).
- **Explicit invalidation (event-based).** On a SoT write, actively delete/update the cached key
  (cache-aside delete, §A; or a CDN purge, §D; or a pub/sub invalidation stream, e.g. Facebook's
  cross-region delete stream, 08 §1.7 `[UNVERIFIED Nishtala]`). **Pro:** near-immediate freshness.
  **Con:** you must *find every copy* — every rung of the ladder (A), every region, every app
  instance. Missed invalidations = silent permanent staleness. This is the "there are only two hard
  problems" problem.
- **Versioned / immutable keys (key-as-version).** Make the cache key include a version/content hash
  (`avatar_v37.png`, `bundle.8a3f.js`); a write produces a *new key*, so the old cached value is
  never served again and there is *nothing to invalidate*. **Pro:** trivially correct, infinitely
  cacheable (long TTL), CDN-friendly (Cluster D content-addressed assets). **Con:** requires the
  reader to learn the new version (a pointer indirection that itself must be invalidated — you push
  the small invalidation up to a tiny version pointer). This is the cleanest strategy and the reason
  static-asset CDNs work.

The three are a ladder of coordination cost: TTL (none) → versioned (one tiny pointer) → explicit
(every copy). Pick the least coordination that meets the freshness the user can perceive (15's
discipline).

### 1.3 Validation / conditional requests — staleness without re-transfer (REUSE 08 §1.7)

Orthogonal to invalidation: even an expired entry can be cheaply *revalidated* rather than refetched.
HTTP `ETag`/`If-None-Match` and `Last-Modified`/`If-Modified-Since` let a cache ask "still valid?"
and get a tiny `304 Not Modified` instead of the full body (RFC 9111 `[UNVERIFIED]`, carried from
08). This decouples "is it fresh?" from "resend the bytes" — central to the CDN/edge story (D).

### 1.4 Cache stampede / thundering herd, and the load-multiplier math (NEW, VERIFIED)

When a hot key expires (TTL) or is invalidated, naive cache-aside lets **every** concurrent miss go
to the origin until the first refill lands. With arrival rate `R` req/s for the key and origin
recompute time `T_r` s, the herd size ≈ `R · T_r` concurrent origin calls instead of 1.

**VERIFIED BY RECOMPUTATION** (`_factcheck_phase1.md`):

| R (req/s) | recompute T_r (s) | naive herd (≈ R·T_r) | with coalescing |
|-----------|-------------------|----------------------|-----------------|
| 1,000 | 0.05 | 50 | 1 |
| 1,000 | 0.20 | 200 | 1 |
| 10,000 | 0.05 | 500 | 1 |
| 10,000 | 0.20 | 2,000 | 1 |

The multiplier is `R·T_r` — it grows with both popularity and origin slowness, so the **hottest,
slowest keys stampede worst** (exactly 14's celebrity keys). This is why a cache can *increase* peak
origin load at the moment of expiry: it batches a quiet period into a synchronized thundering herd.

### 1.5 Stampede mitigations (REUSE 08 §1.6) — collapse the herd to 1

- **Request coalescing / singleflight** — first miss per key does the fetch; concurrent misses wait
  and share the result. Collapses the herd to 1 (the "with coalescing" column). Go
  `x/sync/singleflight` line-verified in 08; not a cache, just dedup.
- **Leases** — first miss gets a token and is the only client allowed to fill; others briefly serve
  stale or wait (Facebook Memcache: 17K/s → 1.3K/s peak DB rate, 08 §1.6 `[UNVERIFIED Nishtala]`).
- **Stale-while-revalidate / stale-if-error** — serve the expired value while one background refresh
  runs (RFC 5861, 08 §1.6 `[UNVERIFIED]`); turns a hard expiry into a soft one, removing the herd
  *and* the latency spike at the cost of bounded extra staleness.
- **Probabilistic early expiration (XFetch)** — refresh a key slightly *before* its TTL with rising
  probability, so one request volunteers to refresh while others still hit, avoiding the synchronized
  cliff. Mechanism noted in 08 §6 but formula NOT primary-sourced — `[UNVERIFIED]`, teach intuition
  only.
- **TTL jitter** — randomize TTLs so a batch of keys cached together does not all expire at the same
  instant (mass-expiry stampede). First-principles; no source needed.

### 1.6 Negative caching — cache the absence too

A miss that resolves to "does not exist" (404, empty result) should be cached briefly, or every
lookup for a non-existent key bypasses the cache and hits the origin every time (a stampede that
never ends — exactly how some DDoS / cache-penetration patterns work). Bound it with a short TTL so a
later create is seen. (Reuse 06 Bloom filter as a complementary "definitely-absent" pre-filter to
avoid even the negative-cache lookup.)

### 1.7 The stale-fill race and its fixes (REUSE 08 §1.7, completing Cluster A's deferral)

Cluster A §1.4 deferred this: in cache-aside, a reader can miss, a writer can then write SoT + delete
the key, and the slow reader can repopulate the *old* value after the delete — silent permanent
staleness. Fixes (08 §1.7): **leases/CAS** (the fill is rejected if an invalidation intervened —
version check), **delayed double-delete** (delete, write, wait > read window, delete again), or short
TTL (bounds the damage). This is the cache analogue of 15's concurrent-write conflict; the cure is
the same shape — a version/token that detects the intervening write.

## 2. Foundational sources (consolidated)

**VERIFIED BY RECOMPUTATION this session** (`_factcheck_phase1.md`): stampede load multiplier
`herd ≈ R·T_r` and the coalescing-to-1 reduction (§1.4 table).

**Verified by REUSE (line-checked earlier, NOT re-fetched):**
- Staleness ladder / read-your-writes / monotonic-reads / consistent-prefix + cheapest-guarantee
  discipline — 15 `_research.md` Cluster B; consistency models — 11.
- Leases / singleflight / stale-while-revalidate / stale-fill race / delete-on-write cache-aside /
  active-vs-lazy expiry — 08 `_research.md` §§1.2/1.6/1.7 (`singleflight.go`, RFC 5861/9111,
  Nishtala NSDI 2013 — the *mechanisms* verified; the cited *sources* flagged below).
- Bloom filter for definite-absence (negative-cache pre-filter) — 06.
- Hot/celebrity keys that stampede worst — 14.

**Blocked primaries — `[UNVERIFIED from fetched source]` (HTTP 000 this session):**
- RFC 9111 (HTTP caching, `ETag`/`304`/`Vary`/freshness) + RFC 5861 (stale-while-revalidate/
  stale-if-error) — carried from 08; load-bearing for §1.3/§1.5 and Cluster D.
- Nishtala et al. NSDI 2013 (leases, cross-region delete stream, 17K→1.3K herd numbers) — carried
  from 08.
- XFetch / probabilistic early expiration (Vattani, Chierichetti, Lowenstein "Optimal Probabilistic
  Cache Stampede Prevention" VLDB 2015) — NOT fetched; teach intuition only.

## 3. "Why it's this way" — the forcing functions

- **A cache is a replica, so it inherits replication's consistency tax (15).** You cannot have a
  cheap, always-fresh, coordination-free cache — TTL trades freshness for zero coordination, explicit
  invalidation trades coordination for freshness, versioned keys trade an indirection for both.
- **Invalidation is hard because copies are everywhere (A's ladder).** Explicit invalidation must
  reach every rung/region/instance; the difficulty is proportional to how many places you cached,
  which is why versioned keys (nothing to invalidate) are the clean escape.
- **Caches batch quiet into bursts.** A hot key absorbs load silently, then dumps a synchronized herd
  at expiry (`R·T_r`, §1.4) — the cache can *raise* peak origin load exactly when the origin is
  already hot (14's celebrity key). Coalescing/leases/SWR exist to re-flatten that burst to ~1.
- **Absence is a value too.** Without negative caching, non-existent keys are an un-cacheable
  permanent miss stream — a self-inflicted stampede and a DDoS amplifier.
- **The stale-fill race is a write/read ordering bug, so it needs a version, not a bigger cache.**
  Same shape as 15's concurrent-write conflict; the fix is a token/CAS that detects the intervening
  write.

## 4. Common misconceptions to preempt

- "Set a TTL and you're consistent." TTL bounds staleness to the TTL; it is *eventual* consistency
  with a known window, not freshness (15).
- "Explicit invalidation makes the cache always fresh." Only if it reaches *every* copy; a missed
  rung/region is silent permanent staleness (§1.2).
- "Cache invalidation after a write is enough." The stale-fill race can repopulate the old value
  after your delete; you need a lease/CAS/double-delete (§1.7, 08).
- "A cache only reduces origin load." At expiry of a hot key it can *spike* origin load `R·T_r`× via
  stampede (§1.4); mitigation is mandatory for hot keys.
- "Short TTL is the safe choice." Short TTL raises miss rate (lower hit ratio, B) *and* stampede
  frequency; freshness and origin-protection trade off.
- "singleflight is a cache." It only dedups concurrent calls; the value isn't retained after the call
  returns (08).
- "stale-while-revalidate is strong consistency." It explicitly serves stale during refresh — a
  deliberate weaker rung that removes the herd + latency spike (15 discipline).
- "Versioned keys are a hack." They are the cleanest invalidation strategy — nothing to invalidate;
  the indirection is the only (tiny) thing left to update (§1.2). The basis of static-asset CDNs (D).
- "Caching non-existent keys is pointless." Negative caching prevents an un-ending miss stream / cache
  penetration (§1.6).

## 5. Best build-your-own target(s)

- **Stampede reproducer + mitigations:** drive `R` concurrent requests at one key with origin
  recompute `T_r`; count origin calls naive vs singleflight vs lease vs stale-while-revalidate;
  confirm the `R·T_r` herd and the collapse-to-1 (§1.4). Pairs 08.
- **Invalidation-strategy bake-off:** same workload under TTL, explicit-delete, and versioned-key;
  measure staleness window, hit ratio, and invalidation messages sent; expose a missed-invalidation
  on a second cache node (monotonic-reads violation, 15). Makes §1.2 tangible.
- **Stale-fill race harness:** concurrent writer (SoT write + delete) and slow reader (miss + late
  fill); show the old value resurrected, then fix with CAS/lease/double-delete (§1.7).
- **Negative-cache + Bloom pre-filter:** show non-existent-key flood hitting origin, then absorbed
  by negative cache, then pre-empted by a Bloom filter (06).

## 6. Open questions / gaps to close (preserved)

- RFC 9111 / RFC 5861 / Nishtala NSDI 2013 `[UNVERIFIED]` (HTTP 000) — carried from 08; needed before
  §1.3/§1.5 and Cluster D harden into prose.
- XFetch formula NOT primary-sourced (VLDB 2015) — teach intuition only; do not write the equation.
- Decision (carried to reconcile): default cache-aside stale-fill fix to teach — lease vs CAS vs
  delayed double-delete; likely teach all three with the version/token through-line (15).
- Boundary: cross-region invalidation *transport* (delete streams, pub/sub) overlaps 17 (async/
  event-driven) — cross-link, don't re-derive the messaging layer here.
- Multi-layer coherence across the full A-ladder (browser + CDN + proxy + app + remote) is genuinely
  hard; teach the *discipline* (versioned keys for the far/uncontrollable layers, explicit
  invalidation only where you control every copy), not a false "globally coherent cache" promise.
