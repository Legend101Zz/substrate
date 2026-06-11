# 16 — Caching and CDN Strategies · _structure.md

**Identity:** the shared sink for the read-side pressures 13/14/15 hand off — and a special case
of 15's replication, where a cache is just a deliberately-stale replica whose staleness is bounded
by TTL/invalidation instead of a replication log. You want a faster, cheaper copy of the truth.

**Bespoke shape — "the four questions of any cache, ending at the geographic edge."** NOT a
product tour. A cache must answer four questions in order, and the sub-course is those questions:
**A — where do you put it? (placement + write pattern) → B — how much of the truth fits? (sizing
on the Zipf curve) → C — how wrong may it be, and how do you stop it melting the origin?
(consistency + stampede) → D — how do you push it to the geographic edge? (CDN).** Three primitives
do double duty throughout: request coalescing (stampede control = origin shielding), versioned keys
(cleanest invalidation = content-addressed CDN assets), and the staleness ladder (15's anomalies,
re-pointed at cache layers). Sizing math verified by recomputation; labs are simulators + a mini-CDN.

## Dependency position
- **Depends on:** 08 (the cache MACHINE — eviction/admission/slabs/leases/SWR/stale-fill; 16
  reuses, owns only sizing math), 06 (Bloom for negative caching, Merkle intuition), 10 (reverse-
  proxy `proxy_cache`, event-driven PoP), 03 (TCP/TLS RTTs, IP/BGP/DNS substrate), 13 (latency
  hierarchy, propagation floor, fan-out), 14 (hot shards/celebrity = the Zipf head), 15 (cache-as-
  stale-replica + staleness ladder), 11 (consistency models the cache inherits).
- **Feeds into:** 17 (cross-region invalidation TRANSPORT = delete streams/CDC/pub-sub), 19 (SLOs
  on hit ratio/origin load), 20 (origin protection under tail), 21 (every read-heavy case).
- **Appendix links DOWN:** G-redis (the remote-tier machine), O-cloud-primitives (anycast/edge),
  10 (the reverse-proxy deep ref). 16 owns placement + sizing + edge strategy.

## Chapter specs (3–5 lines each)
### A — where
1. **The placement ladder & write contracts** — caching is a LADDER (client → CDN/edge → reverse-
   proxy → app-local → remote Redis/Memcached → DB buffer); each rung trades reach vs proximity, so
   you cache at several. App-local vs remote = proximity vs coherence. The five patterns (cache-
   aside, read-through, write-through, write-back, write-around) = the cross-product of "does the
   write touch the cache?" × "is the SoT write sync?" — i.e. WHERE you pay (write latency,
   durability window, or stale-read risk). Reuse 08.

### B — how much fits
2. **Why caching works: the Zipf working set** — caching works BECAUSE working set ≪ keyspace: at
   N=1e6, α=1, caching 1% of keys buys 68% hit ratio (VERIFIED). The curve is concave (50× memory →
   0.68→0.95), so size to the KNEE, never the keyspace. Skew (α) dominates everything — measure α
   before promising anything.
3. **Hit ratio is an origin-load metric** — origin load = `(1−h)`; `t_avg=h·t_hit+(1−h)·t_miss`
   (VERIFIED). The last nines (99→99.9%) barely move latency but cut origin load 10× — sizing
   protects the ORIGIN (13's tail), not the average. Eviction/admission reuse from 08 (LRU/LFU/2Q/
   ARC/TinyLFU/W-TinyLFU; admission ≠ eviction).

### C — how wrong + don't melt the origin
4. **A cache is a replica → caching IS a consistency problem (15)** — invalidation is a ladder of
   coordination cost: TTL (no coordination, bounded staleness) → versioned/immutable keys (one tiny
   pointer, nothing to purge) → explicit invalidation (must reach EVERY copy on every rung/region).
   Validation/304 (ETag/If-None-Match, Last-Modified) = cheap revalidation. Negative caching (cache
   absence) + Bloom pre-filter (06). Stale-fill race fix = lease/CAS/double-delete (15's conflict
   shape).
5. **The stampede: caches batch quiet into bursts** — a hot key's expiry dumps `herd≈R·T_r`
   synchronized origin calls (VERIFIED, up to 2,000×) — the cache can RAISE peak origin load
   exactly when the origin is hot. Collapse to ~1 via coalescing/singleflight/leases/stale-while-
   revalidate/TTL jitter. (XFetch noted but formula UNVERIFIED — don't teach the formula.)

### D — the geographic edge
6. **The CDN: the ladder's top rungs, geo-distributed** — the edge exists because latency has a
   PHYSICAL floor (13, speed of light bounds RTT); the only lever is moving bytes closer. PoPs
   (reverse-proxy caches, 10) near users, reached by anycast (one prefix, many BGP announcements →
   nearest PoP, auto-failover; DNS-steering alternative, 03). Pull (demand reveals the working set,
   B) vs push (predictably-hot large objects).
7. **Edge correctness at scale** — the cache key (`Vary`) is a hit-ratio lever disguised as config
   (over-specific keys shatter the working set). Origin shielding = coalescing across the PoP fleet
   (N misses → 1). Freshness = Cache-Control/s-maxage + validators + SWR/stale-if-error. The clean
   global invalidation answer = versioned/content-addressed URLs (nothing to purge); soft-purge >
   hard purge. Edge compute makes dynamic responses partly edge-cacheable.

## Paired build labs (/build — simulators + mini-CDN)
Pattern bake-off (all five patterns over one SoT; measure read/write latency, durability window via
kill-during-write-back, stale-read count) → placement-ladder simulator (client→CDN→proxy→app→
remote→DB with 13 latency costs; replay Zipf; hit ratio + latency per rung) → Zipf hit-ratio
simulator + knee-finder (trace → exact/sampled-LRU/LFU/TinyLFU; overlay analytic `H(k,α)/H(N,α)`;
solve min cache for origin-survivable `(1−h)·QPS`) → stampede reproducer + mitigations (confirm
`R·T_r`; collapse to 1) → invalidation bake-off (TTL vs explicit vs versioned; expose a missed
invalidation = monotonic-reads violation) → stale-fill race harness (CAS/lease/double-delete) →
mini multi-PoP CDN (N reverse-proxy caches + origin; nearest-PoP routing; pull + Cache-Control/
ETag/304; add origin shield → N→1) → cache-key lab (URL vs +query vs +Vary vs +cookie → hit-ratio
collapse) → purge vs versioned-URL demo.

## Diagrams needed
- The four-questions arc (placement→sizing→consistency/stampede→edge) as spine motif.
- The placement ladder with reach-vs-proximity per rung; five write patterns (where the ack lands).
- Zipf hit-ratio curve (concave, knee marked) + α sensitivity; origin load `(1−h)` vs hit ratio.
- Invalidation ladder (TTL → versioned → explicit) by coordination cost.
- Stampede: hot-key expiry → `R·T_r` synchronized misses → coalescing collapses to 1.
- CDN PoPs + anycast (one prefix, many announcements → nearest); pull vs push fill.
- Cache key / `Vary` shattering the working set; origin shielding (PoP fleet N→1).
- Versioned/content-addressed URL = nothing to purge.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED BY RECOMPUTATION:** Zipf hit ratio `H(k,α)/H(N,α)` (1% of 1e6 → 68% at α=1; monotone);
  `t_avg` + origin fraction `(1−h)`; stampede `herd≈R·T_r` (up to 2,000×) + coalescing-to-1.
- **`[UNVERIFIED]` — RFC/canonical/vendor attributions network-blocked at reconcile time:** RFC
  9111/5861/7234/4786 (NOTE: 9111/5861/7234/4786 were FETCHED+VERIFIED in 17's session — reconcile
  receipts at draft), Nishtala NSDI 2013 (also fetched in 17), Breslau INFOCOM 1999 (web α), Vattani
  XFetch VLDB 2015, Cormode-Muthukrishnan 2005, ARC pseudo-code/patent, vendor CDN/anycast/edge-
  compute specifics + exact RTT figures. Teach mechanisms now; do NOT harden exact RFC wording /
  vendor routing / real-world α / exact ms RTTs until reconciled-or-fetched.
- **Disagreements to resolve:** default stale-fill fix (lease vs CAS vs double-delete — likely all
  three on the version/token through-line); Zipf via IRM analytic (exact, assumes independence) vs
  simulator (realistic locality) — likely simulator-first; anycast/BGP depth before deferring to 03/O.
- **Boundary discipline:** eviction/admission internals → 08 (+ appendix G); remote-tier sharding/
  replication → 14/15; TCP/TLS/HTTP2/3 → 03/10; anycast/BGP/DNS → 03 + appendix O; cross-region
  invalidation TRANSPORT → 17 (don't re-derive messaging); origin protection under tail + hedging →
  13/20; SLOs on hit ratio → 19; staleness theory → 11/15.
