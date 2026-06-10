# Research Brief — Sub-course 08: Admission, Dogpile Prevention, and Cache Consistency
## Source cluster: TinyLFU/W-TinyLFU/ARC, request collapsing, stale-while-revalidate, write-invalidate tradeoffs
## Researcher: researcher + brain validation | Date: 2026-06-10

---

## 1. Key Mechanisms

### 1.1 Eviction vs admission: two different decisions

Eviction asks: “which resident item should leave?” Admission asks: “should the missed item enter at all?”
That distinction matters because a cache can be evicted by a one-time scan even if it has a decent LRU
victim rule. TinyLFU’s core claim is that an approximate recent-frequency sketch can act as an admission
gate: compare a candidate miss to the eviction victim and admit only when expected hit ratio improves.

Verified source: Einziger and Friedman, “TinyLFU: A Highly Efficient Cache Admission Policy,” arXiv
1512.00727, `https://arxiv.org/abs/1512.00727`; extracted PDF text says TinyLFU maintains an approximate
representation of access frequency over a large recent sample, that admission decides whether a missed
item should replace a selected victim, and that W-TinyLFU combines a window cache with TinyLFU admission.

### 1.2 TinyLFU: approximate frequency history for items outside the cache

Pure in-cache LFU knows only resident items. Admission needs knowledge of non-resident misses too, because
a candidate has just missed and is not resident yet. TinyLFU therefore tracks a bounded recent-history
frequency summary instead of exact counters for the entire key universe.

Paper/source-backed mechanisms:

- TinyLFU augments an existing eviction policy; the eviction policy picks a victim and TinyLFU decides
  whether replacing that victim with the candidate is likely to help. Source: arXiv 1512.00727.
- The paper discusses compact approximate counting via Counting Bloom Filter / Count-Min style sketches,
  plus periodic reset/aging so old popularity fades.
- The Doorkeeper optimization is a Bloom filter in front of the counting structure: first-time/tail items
  pay one bit in the Doorkeeper instead of immediately consuming multi-bit counters. Source: arXiv text,
  section “Doorkeeper.”
- Caffeine’s `FrequencySketch` implements a 4-bit CountMinSketch with maximum counter 15 and periodic aging;
  `ensureCapacity()` sets `sampleSize = min(10 * maximumSize, Integer.MAX_VALUE)`, and `reset()` halves
  counters with `RESET_MASK = 0x7777777777777777L`. Source:
  `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/FrequencySketch.java`.

### 1.3 W-TinyLFU: give new items a recency window before the frequency gate

A strict frequency gate rejects first-time items, including genuinely new hot items. W-TinyLFU fixes that
with a small LRU admission window.

- The TinyLFU paper describes W-TinyLFU as two cache areas: a window cache using LRU and a main cache using
  SLRU plus TinyLFU admission. New arrivals enter the window; the window victim competes for admission to
  the main cache. Source: arXiv 1512.00727.
- The paper’s Caffeine 2.0 description says the window was 1% of total cache and the main cache was 99%,
  with the main SLRU split 80% hot/protected and 20% non-hot/probationary.
- Current Caffeine source still exposes `PERCENT_MAIN = 0.99d` and `PERCENT_MAIN_PROTECTED = 0.80d`, then
  computes `window = max - PERCENT_MAIN * max` and `mainProtected = PERCENT_MAIN_PROTECTED * (max - window)`.
  Source: `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java`.
- Caffeine `TinyLfu.admit()` compares `candidateFreq` and `victimFreq`; current `BoundedLocalCache.admit()`
  adds a small randomness path when `candidateFreq >= ADMIT_HASHDOS_THRESHOLD` to reduce hash-collision
  abuse. Sources: Caffeine `TinyLfu.java` and `BoundedLocalCache.java`.

### 1.4 ARC: adaptive recency/frequency without tuning, but with ghost history

ARC (“Adaptive Replacement Cache”) is a classic answer to “how much cache should be recency-biased vs
frequency-biased?” It maintains two real LRU lists and two ghost lists: recent-once items, frequent items,
and histories of recently evicted keys. A ghost hit tells ARC which side would have helped and adjusts the
recency/frequency target.

Verified source: Megiddo and Modha, “ARC: A Self-Tuning, Low Overhead Replacement Cache,” FAST 2003,
`https://www.usenix.org/legacy/events/fast03/tech/full_papers/megiddo/megiddo.pdf`, extracted with `/tmp`
`uv run --with pypdf`. This brief uses ARC at mechanism level only; exact pseudo-code and patent status
should be rechecked before course prose.

### 1.5 Dogpile/cache stampede: one hot miss becomes many origin calls

A dogpile happens when many concurrent requests miss or expire the same key and all recompute it. The fix
is not “better eviction”; it is coordination around refills.

- **Request collapsing / singleflight:** Go’s `x/sync/singleflight` source defines a `Group` whose `Do(key, fn)`
  suppresses duplicate concurrent calls. If a call for the key is in flight, later callers wait and receive
  the same result; when the call completes the entry is removed. Source:
  `https://raw.githubusercontent.com/golang/sync/master/singleflight/singleflight.go`.
- **Leases:** Facebook’s Memcache paper gives the first miss client a 64-bit lease token and makes later
  clients wait/retry or use stale values, reducing peak database query rate for one herd-prone key set from
  17K/s to 1.3K/s. Source: NSDI 2013 Memcache paper.
- **Stale-while-revalidate:** RFC 5861 defines `stale-while-revalidate=delta-seconds`: after freshness expires,
  caches MAY serve stale for that extra window while revalidating in the background. Source:
  `https://www.rfc-editor.org/rfc/rfc5861.txt`.
- **Stale-if-error:** RFC 5861 also defines `stale-if-error=delta-seconds`, allowing stale responses when the
  origin returns errors such as 500/502/503/504 within the allowed window.

### 1.6 HTTP cache consistency: freshness, validation, and unsafe-method invalidation

RFC 9111 is the primary anchor for HTTP cache semantics:

- Cache keys are method + target URI plus request fields named by `Vary`.
- Freshness is computed from response directives such as `s-maxage`, `max-age`, `Expires`, and heuristics.
- Stale serving is not free-form: RFC 9111 says a cache MUST NOT generate stale responses unless disconnected
  or explicitly permitted by directives such as `max-stale` or extensions like RFC 5861.
- Validation uses entity tags (`ETag` / `If-None-Match`) and modification dates (`Last-Modified` /
  `If-Modified-Since`); 304 updates stored response metadata without resending the body.
- Unsafe methods such as PUT/POST/DELETE trigger invalidation: a cache MUST invalidate the target URI when
  it receives a non-error response to an unsafe request method.

Source: `https://www.rfc-editor.org/rfc/rfc9111.txt`.

### 1.7 Application cache write patterns: useful taxonomy, weaker primary grounding

The pattern names `cache-aside`, `write-through`, and `write-back/write-behind` are useful teaching handles,
but this pass did not find a single standards document that defines them for Redis/Memcached. Use them as
taxonomy, not law:

- **Cache-aside:** application reads cache, fills on miss, and invalidates/updates cache after database writes.
  Facebook’s Memcache paper verifies this shape: web servers read memcache first, query MySQL on miss, and
  issue deletes to invalidate stale cache entries after writes.
- **Write-through:** write cache and backing store synchronously. Lower stale-read risk but higher write latency
  and tighter coupling. `[UNVERIFIED taxonomy source]`
- **Write-back/write-behind:** acknowledge writes to cache and flush later. Lower write latency but introduces
  data-loss risk if the cache fails before flush. `[UNVERIFIED taxonomy source]`

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| TinyLFU admission policy and W-TinyLFU paper | `https://arxiv.org/abs/1512.00727` / `https://arxiv.org/pdf/1512.00727` | VERIFIED via PDF extraction |
| Caffeine W-TinyLFU overview | `https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Efficiency.md` | VERIFIED |
| Caffeine 4-bit FrequencySketch | `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/FrequencySketch.java` | VERIFIED |
| Caffeine admission/window constants | `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java` | VERIFIED |
| Caffeine simulator admission comparator | `https://raw.githubusercontent.com/ben-manes/caffeine/master/simulator/src/main/java/com/github/benmanes/caffeine/cache/simulator/admission/TinyLfu.java` | VERIFIED |
| ARC paper | `https://www.usenix.org/legacy/events/fast03/tech/full_papers/megiddo/megiddo.pdf` | VERIFIED via PDF extraction; exact pseudo-code not yet reconciled |
| Go duplicate-call suppression | `https://raw.githubusercontent.com/golang/sync/master/singleflight/singleflight.go` | VERIFIED |
| HTTP stale controls | `https://www.rfc-editor.org/rfc/rfc5861.txt` | VERIFIED |
| HTTP caching semantics | `https://www.rfc-editor.org/rfc/rfc9111.txt` | VERIFIED |
| Facebook Memcache leases/cache-aside shape | `https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf` | VERIFIED |

---

## 3. Why It’s This Way — Forcing Constraints

- **Admission exists because scans poison recency caches.** One-time objects can evict the hot set if every
  miss is automatically admitted.
- **Approximate sketches exist because exact global frequency is too large.** The cache needs history about
  non-resident keys, but keeping exact counters for every possible key is not bounded by cache size.
- **Aging exists because popularity changes.** Without reset/decay, old hot keys can dominate forever.
- **A recency window exists because new hot keys start cold.** First access has no frequency history, so a
  window gives candidates a chance to prove themselves.
- **Request collapsing exists because TTL expiry creates synchronized misses.** The origin should pay for one
  recomputation, not one per concurrent client.
- **Stale-while-revalidate exists because freshness and latency fight.** Serving bounded-stale content can keep
  tail latency low while a background refresh restores freshness.
- **Invalidation is hard because writes and refills race.** A stale read can miss, a concurrent writer can update
  the database and delete the cache, and then the stale reader can refill the old value unless guarded by CAS,
  versions, leases, delayed retries, or shorter TTLs.

---

## 4. Common Misconceptions to Preempt

1. **“Eviction policy is the whole cache policy.”** Admission can matter as much as eviction for scan-heavy workloads.
2. **“LFU always beats LRU.”** LFU without aging can preserve yesterday’s hot keys forever.
3. **“TinyLFU stores exact frequencies.”** It stores approximate recent frequency; collisions and reset are deliberate tradeoffs.
4. **“Singleflight is a cache.”** It deduplicates concurrent function calls; it does not store results after completion.
5. **“Stale-while-revalidate means fresh soon for everyone.”** It permits bounded stale serving while refresh happens;
   if refresh fails or no request arrives in the window, behavior changes.
6. **“HTTP cache rules automatically solve Redis/Memcached consistency.”** RFC 9111 governs HTTP caches; application
   caches need app-level protocols.
7. **“Write-back is just faster write-through.”** It changes the durability contract and can lose acknowledged writes.

---

## 5. Build-Your-Own Targets

1. **TinyLFU gate** — approximate frequency sketch + `admit(candidate, victim)` comparator.
2. **W-TinyLFU toy** — LRU window, probation/protected SLRU main, frequency-sketch admission.
3. **ARC simulator** — T1/T2/B1/B2 and adaptive target; compare against LRU on scan and loop traces.
4. **Singleflight wrapper** — per-key in-flight map around an expensive loader; verify N concurrent misses make one origin call.
5. **Stale-while-revalidate middleware** — serve stale inside a configured window and refresh in background.
6. **Race demo for cache-aside** — show stale refill after write-invalidate, then fix with version/CAS/lease.

---

## 6. Open Questions / Source Gaps

- ARC exact pseudo-code, patent/licensing status, and modern implementations need a deeper pass before course prose.
- Count-Min Sketch formal error-bound derivation is not yet anchored to the Cormode/Muthukrishnan paper.
- Application pattern names `write-through` and `write-back` still need an official/source anchor; keep them as
  taxonomy with `[UNVERIFIED taxonomy source]` until found.
- Probabilistic early expiration / XFetch was not primary-sourced in this pass; do not teach exact formulas yet.
- Caffeine’s hill-climbing source is verified, but the SIGMETRICS 2018 paper behind it was not fetched.
