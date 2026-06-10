# 16 — caching-and-cdn-strategies — Cluster B: eviction + sizing (hit ratio vs working set)

> **Phase 1 research brief (NO course prose).** Standard six sections. Eviction *internals*
> (sampled LRU, segmented LRU, slabs, TinyLFU/W-TinyLFU sketch) were line-verified in 08 and are
> REUSED here, not re-derived. The load-bearing NEW content of this cluster is the **sizing
> mathematics** — hit ratio as a function of cache size under a Zipf working set — and all of it is
> **VERIFIED BY RECOMPUTATION this session** (pure Python, no deps; see `_factcheck_phase1.md`).
> Empirical Zipf exponents for real workloads are `[UNVERIFIED from fetched source]` (network HTTP
> 000, 8th session).

Cluster scope: given a bounded cache, *which* entry to evict and *how big* to make the cache. The
two questions are linked: eviction quality and cache size both move the hit ratio along the same
working-set curve.

---

## 1. Key mechanisms

### 1.1 Eviction policies (REUSED from 08 — the menu, with the property that matters)

- **LRU** — evict least-recently-used. Captures *recency*; one-pass scans pollute it (a big sequential
  read evicts the whole hot set). Real systems approximate it (Redis sampled pool size 16; Memcached
  segmented HOT/WARM/COLD) — 08 §1.3, line-verified.
- **LFU** — evict least-frequently-used. Captures *frequency*; needs aging or it ossifies on
  yesterday's hot keys. Redis uses an 8-bit log counter with decay (08 §1.3).
- **2Q / ARC** — two lists (recency + frequency) with ghost history adapting the split; ARC (FAST
  2003) self-tunes the recency/frequency balance. Mechanism verified in 08 §1.5; exact ARC
  pseudo-code/patent status still a deferred gap there.
- **TinyLFU / W-TinyLFU** — *admission* in front of eviction: a 4-bit Count-Min frequency sketch
  decides whether a miss even deserves to evict a resident; W-TinyLFU adds a small LRU window so a
  newly-hot key can build evidence before competing (Caffeine `PERCENT_MAIN=0.99`,
  `PERCENT_MAIN_PROTECTED=0.80`) — 08 §1.5, line-verified. This is the current best general policy
  because it directly attacks scan pollution + one-hit-wonders.

### 1.2 Eviction vs admission are different decisions (REUSED, load-bearing for sizing)

08 §1.5: eviction picks a resident *victim*; admission decides whether a miss *deserves* space at
all. The cost model is: a one-hit-wonder admitted under pure LRU evicts something useful to cache
something never read again. Admission (TinyLFU) protects the working set from the long tail — which
is exactly what makes a *small* cache punch above its size on a Zipf workload (§1.4).

### 1.3 Hit ratio is the master metric; latency and origin load both derive from it

For hit ratio `h`, hit cost `t_hit`, miss cost `t_miss`:

- **Average latency** `t_avg = h·t_hit + (1−h)·t_miss`.
- **Origin load fraction** = `(1−h)` (the miss rate is exactly the fraction of traffic the cache
  fails to absorb).

**VERIFIED BY RECOMPUTATION** (illustrative `t_hit=1ms`, `t_miss=100ms` — the *ratio* is the lesson,
the absolute ms are `[UNVERIFIED]` workload values):

| h | t_avg (ms) | origin fraction (1−h) |
|------|-----------|-----------------------|
| 0.90 | 10.900 | 0.1000 |
| 0.95 | 5.950 | 0.0500 |
| 0.99 | 1.990 | 0.0100 |
| 0.999| 1.099 | 0.0010 |

**The load-bearing consequence: the last nines matter most.** Going 99% → 99.9% barely moves average
latency (1.99 → 1.10 ms) but cuts **origin load 10×** (0.01 → 0.001). Cache sizing is usually
justified by origin protection, not by mean latency. (This is the cache twin of 13's tail argument:
the rare miss, fanned out, is what melts the backend.)

### 1.4 Working set vs cache size — the Zipf hit-ratio curve (the core NEW result)

Real key popularity is heavily skewed; the standard model is **Zipf**: the i-th most popular of `N`
keys gets probability `∝ 1/i^α`. Caching the top-`k` keys (what a good LRU/LFU+admission policy
converges to) yields hit ratio = `H(k,α) / H(N,α)` where `H(n,α)=Σ_{i=1..n} 1/i^α` (generalized
harmonic number).

**VERIFIED BY RECOMPUTATION** (α = 1.0):

| keyspace N | cache top 1% | top 10% | top 20% |
|-----------|-------------|---------|---------|
| 1,000 | 0.3913 | 0.6930 | 0.7853 |
| 1,000,000 | 0.6800 | 0.8400 | 0.8882 |

Two structural lessons fall straight out of the numbers:

1. **A tiny cache captures most of the load** — at N=1e6, α=1, caching just **1%** of keys yields a
   **68%** hit ratio; 10% yields 84%. This is *why caching works at all*: the working set ≪ keyspace.
   It is the same head/tail skew that creates 14's hot shards, now turned into an asset.
2. **Diminishing returns are steep** — going from 1% → 50% of keyspace (50× more memory) only moves
   the hit ratio 0.68 → 0.95 (verified, §monotone table below). The first few percent of cache are
   worth far more than the rest; sizing is a knee-finding exercise, not "bigger is always better."

**Monotone working-set curve (VERIFIED, N=1e6, α=1):**

| cache fraction | hit ratio |
|----------------|-----------|
| 0.10% | 0.5201 |
| 1.00% | 0.6800 |
| 10.00% | 0.8400 |
| 50.00% | 0.9518 |
| 100.00% | 1.0000 |

(monotone increasing — confirmed by recomputation.)

### 1.5 Skew (α) dominates everything

The hit ratio at fixed cache size is extremely sensitive to how skewed the workload is.
**VERIFIED BY RECOMPUTATION** — cache top 1% of N=1e6:

| α (skew) | top-1% hit ratio |
|----------|------------------|
| 0.8 | 0.3624 |
| 1.0 | 0.6800 |
| 1.2 | 0.9096 |

A flatter workload (α=0.8) makes the *same* cache far less effective (36% vs 91%). Practical
consequence: **measure your α before promising a hit ratio.** The same skew that hurts partitioning
(14: flat → no hot shard but huge keyspace to spread; peaked → hot shard) *helps* caching (peaked →
small cache, high hit ratio). Caching and sharding read the same skew with opposite signs.

### 1.6 Sizing in practice: capacity = working set, not keyspace

Combine §1.3–§1.5: pick the hit ratio your **origin can survive** (from `(1−h)` × peak QPS ≤ origin
capacity, reuse 13 back-of-envelope), read the cache fraction off the working-set curve for your
measured α, multiply by mean object size for bytes. Slab/segment overhead (08 Memcached slabs) and
metadata are then added on top. The cache is sized to the *knee of the working-set curve at the
origin-survivable hit ratio*, never to the full keyspace.

## 2. Foundational sources (consolidated)

**VERIFIED BY RECOMPUTATION this session** (`_factcheck_phase1.md`, pure Python):
generalized-harmonic Zipf hit ratio `H(k,α)/H(N,α)` (all tables in §1.4–§1.5); `t_avg = h·t_hit +
(1−h)·t_miss` and origin fraction `(1−h)` (§1.3); monotonicity of hit ratio in cache size (§1.4).

**Verified by REUSE (line-checked in 08, NOT re-fetched):**
- LRU/LFU/2Q/ARC/TinyLFU/W-TinyLFU mechanisms + sampled/segmented approximations + admission-vs-
  eviction + slab sizing — 08 `_research.md` §§1.3–1.5, `_factcheck_phase1.md` (Redis `server.h`/
  `evict.c`, Memcached `items.c`/`slabs.c`, Caffeine `FrequencySketch.java` line anchors).
- Tail/origin-protection framing (rare miss × fan-out melts backend) — 13 fan-out math (verified).
- Zipf/celebrity skew as the source of hot shards — 14 `_research.md`.

**Blocked primaries — `[UNVERIFIED from fetched source]` (HTTP 000 this session):**
- Empirical Zipf exponents for real caching workloads (e.g. Breslau et al. "Web Caching and Zipf-like
  Distributions" INFOCOM 1999; CDN/CMS popularity studies). The *model* and *math* are verified;
  the *real-world α values* are not fetched — do not assert a specific production α in prose.
- Count-Min Sketch error bounds (Cormode & Muthukrishnan 2005) — carried from 08 §6.
- ARC exact pseudo-code/patent status — carried from 08 §6.

## 3. "Why it's this way" — the forcing functions

- **Caching works because working set ≪ keyspace.** The Zipf head means a small resident set serves
  most requests (§1.4); without skew, caching would need to be nearly as big as the data to help.
- **Diminishing returns force a knee, not a maximum.** The harmonic curve is concave (§1.4): the
  marginal hit ratio per added byte falls fast, so there is an economically optimal size, never
  "cache everything."
- **The last nines protect the origin, not the user's average.** Because origin load = `(1−h)`,
  halving the miss rate halves backend load even when average latency barely moves (§1.3) — sizing is
  justified by survival under 13's tail/fan-out, not by mean latency.
- **Admission exists because the tail is adversarial.** One-hit-wonders and scans (the Zipf tail)
  would evict the working set under naive LRU; admission (TinyLFU) is what lets the small cache hold
  the head (§1.2) — eviction policy quality and cache size are substitutes along the same curve.
- **You must measure α.** Hit ratio is dominated by skew (§1.5); a sizing promise without a measured
  exponent is a guess.

## 4. Common misconceptions to preempt

- "Bigger cache ⇒ proportionally better." No — concave working-set curve; 50× the memory bought only
  0.68→0.95 (verified). Find the knee.
- "Hit ratio is a latency metric." It is *also* (and more importantly) an origin-load metric:
  origin fraction = `(1−h)`; the last nines are about backend survival (§1.3).
- "LRU is good enough everywhere." Scans pollute LRU; admission (TinyLFU/W-TinyLFU) is what makes a
  small cache survive the Zipf tail (§1.2, 08).
- "Eviction policy doesn't matter much." At a *fixed* small size near the knee, a better policy
  (admission + frequency) is worth a large jump in hit ratio — the same lever as adding memory.
- "A 90% hit ratio is great, ship it." 90% means 10% of traffic hits origin; under 13's fan-out that
  can still melt the backend. The target is set by origin capacity, not by a round number.
- "Workload skew is a detail." α is the single biggest driver of hit ratio (§1.5); flat workloads
  cache poorly no matter the policy.
- "Cache size = keyspace size." Cache to the working set (the knee), never the keyspace (§1.6).

## 5. Best build-your-own target(s)

- **Zipf hit-ratio simulator:** generate a Zipf(α) request trace over N keys; run exact-LRU, sampled-
  LRU, LFU, and a TinyLFU gate at several cache sizes; plot the measured hit-ratio-vs-size curve and
  overlay the analytic `H(k,α)/H(N,α)` — confirm the recomputed tables (§1.4) and the policy gap.
- **Knee-finder / sizer:** given measured α, peak QPS, and origin capacity, solve for the minimum
  cache fraction that keeps `(1−h)·QPS ≤ origin_capacity`; report bytes via mean object size + slab
  overhead. Operationalizes §1.6.
- **Scan-pollution demo:** interleave a hot Zipf head with a big sequential scan; show LRU collapse
  vs TinyLFU admission survival. Pairs 08 §1.5.

## 6. Open questions / gaps to close (preserved)

- Real-world Zipf exponents `[UNVERIFIED]` — model + math verified, but no fetched production α
  (Breslau INFOCOM 1999 et al. HTTP 000). Do not state a specific α as empirical fact in prose.
- The `top-k = LRU/LFU steady state` assumption is exact for IRM (independent reference model);
  temporal locality / bursts make real LRU deviate — note the model's assumption when teaching, and
  prefer the *simulator* (§5) for the realistic number.
- Count-Min error bounds + ARC pseudo-code/patent carried from 08 §6 (still HTTP 000).
- Boundary: eviction *internals* stay in 08/appendix G; this cluster owns *sizing math* only.
