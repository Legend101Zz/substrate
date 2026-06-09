# Research Brief: Skip Lists · Ring Buffers · Consistent Hashing · HyperLogLog
**Sub-course:** 06-data-structures-for-systems  
**Cluster:** probabilistic-distributed-queues  
**Date:** 2026-06-09  
**Status:** Phase 1 complete — brief only, no chapter prose

---

## 1. Key Mechanisms

### 1.1 Skip Lists

**Forcing constraint:** Balanced BSTs (AVL, red-black) require O(log n) rotations on insert/delete,
which demand global structural locks for concurrent access. The constraint is: *can we get O(log n)
expected cost with only local modifications?* Pugh (1990) answered yes, probabilistically.

**Intuitive model:** A sorted linked list with express lanes. Level 1 = every element; level 2 =
every ~1/p elements; level k = every ~1/p^(k-1) elements. To search, start at the top lane and
drop down when you overshoot. The structure is never explicitly balanced—the probabilistic level
assignment *is* the balancing.

**Deep mechanism (Redis `t_zset.c`):**
- `ZSKIPLIST_MAXLEVEL = 32` — sufficient for 2^64 elements (comment-verified)
- `ZSKIPLIST_P = 0.25` — level promotion probability; each level has 1/4 the nodes of the level below
- Level generation (exact Redis source):
  ```c
  static const int threshold = ZSKIPLIST_P * RAND_MAX;
  int level = 1;
  while (random() < threshold) level += 1;
  return (level < ZSKIPLIST_MAXLEVEL) ? level : ZSKIPLIST_MAXLEVEL;
  ```
- Node layout: `{ double score; zskiplistNode *backward; zskiplistLevel level[]; /* + embedded sds */ }`
  - `level[i] = { forward*, unsigned long span }` — `span` counts how many base-level nodes the
    pointer skips; enables **O(log n) rank queries** (ZRANK command)
  - At level 0, `span` field is repurposed to store `zskiplistNodeInfo { uint16_t sdsoffset; uint8_t levels; }` — element string is embedded in the same allocation as the node (single-alloc, cache-friendly, recent change)
  - `backward` pointer only at level 0 → enables `ZREVRANGE` in O(k)
- Expected search: O((log n)/p) comparisons; at p=0.25 this is ≈2.5·log₄(n)
- Pugh's original used p=0.5 for time/space balance. Redis uses p=0.25 to save memory (fewer
  pointers per node on average: 1/(1-0.25) = 1.33 vs 1/(1-0.5) = 2.0 avg levels)

**RocksDB memtable skip list (`memtable/skiplist.h`):**
- `max_height=12, branching_factor=4` (same p=0.25)
- Writes require external mutex; reads are lock-free
- Node publish: `NoBarrier_SetNext` on non-head pointers, then `SetNext` (release-store) to publish
- Memory: arena allocator — nodes never individually freed, entire list freed at memtable flush
- `kScaledInverseBranching_ = (RAND_MAX+1)/branching_factor` for threshold comparison

**Java `ConcurrentSkipListMap` (lock-free, JDK):**
- Written by Doug Lea (JSR-166). Deletion is 3-step, CAS-based:
  1. CAS `node.value` → null (logical deletion; readers skip null-value nodes)
  2. CAS `node.next` → a "marker node" (no further nodes can be appended to `n`)
  3. CAS `predecessor.next` → `f`, skipping both `n` and marker
- Uses plain "marker nodes" instead of `AtomicMarkableReference` — avoids mark-bit masking on
  every read. "This technique would not work well in systems without garbage collection."
- Index levels are separate objects from data nodes (unlike Redis inline level array)

---

### 1.2 Ring Buffers / LMAX Disruptor

**Forcing constraint:** `LinkedBlockingQueue` and friends use:
(a) per-element allocation → GC pressure and latency spikes,
(b) head/tail locks → contention under high throughput,
(c) shared head+tail in same cache line → false sharing even with separate locks.
LMAX wanted < 1μs inter-thread messaging for financial order processing.

**Intuitive model:** A fixed-size circular array. A monotonically increasing 64-bit sequence number
wraps around via `seq & (size-1)`. Both producer and consumer only need to compare sequence numbers
— no locks needed when there is exactly one producer.

**Key design decisions (verified from `RingBuffer.java`, `Sequence.java`, `MultiProducerSequencer.java`):**

**a) Power-of-2 size:**
```java
if (Integer.bitCount(bufferSize) != 1) throw new IllegalArgumentException(...)
this.indexMask = bufferSize - 1;
// Slot lookup: entries[BUFFER_PAD + (sequence & indexMask)]
```
Avoids division; makes modulo a single bitwise AND.

**b) Cache-line padding on every sequence counter (`Sequence.java`):**
```java
class LhsPadding { protected byte p10,...,p77; }  // 56 bytes
class Value extends LhsPadding { protected long value; }  // +8 bytes = 64B
class RhsPadding extends Value { protected byte p90,...,p157; }  // +56 bytes = 120B total
public class Sequence extends RhsPadding { ... }
```
Each `Sequence` occupies at least one full cache line (64B or 128B) on each side. Without this,
producer cursor and consumer gating sequence share a cache line → false sharing → 4-7× throughput loss.

**c) Entry object padding in `RingBufferFields`:**
```java
private static final int BUFFER_PAD = 32;
this.entries = (E[]) new Object[bufferSize + 2 * BUFFER_PAD];
```
32 extra object references on each side of the real entries. On 64-bit JVM with compressed oops,
`Object[]` element = 4 bytes; 32 × 4 = 128 bytes = 2 cache lines of padding. Prevents array header
and first/last real entries from sharing a cache line with adjacent heap objects.

**d) Pre-allocation:**
- `fill()` calls `eventFactory.newInstance()` for all slots at construction time
- Producers never allocate; they mutate the pre-existing event object in-place
- Eliminates GC allocation during steady-state operation

**e) Single-producer path (`SingleProducerSequencer.java`):**
- `long nextValue` and `long cachedValue` are plain fields (no CAS needed)
- Producer: increment `nextValue`, check wrap (consumer hasn't caught up?), fill slot, call `cursor.setVolatile()` to publish
- Zero synchronization instructions on the fast path except the final store-release

**f) Multi-producer path (`MultiProducerSequencer.java`):**
- CAS on `cursor` to claim a range: `cursor.getAndAdd(n)` (atomic fetch-add)
- `availableBuffer[int[]]` tracks "wrap flag" per slot:
  - `calculateIndex(seq) = seq & indexMask` (which slot)
  - `calculateAvailabilityFlag(seq) = seq >>> indexShift` (how many times around the ring)
  - `setAvailable`: `AVAILABLE_ARRAY.setRelease(availableBuffer, index, flag)` 
  - `isAvailable`: `AVAILABLE_ARRAY.getAcquire(availableBuffer, index) == flag`
- Consumer calls `getHighestPublishedSequence` which scans from lowerBound forward until a gap

**g) Wait strategies (latency vs CPU tradeoff):**
- `BusySpinWaitStrategy`: `Thread.onSpinWait()` in loop — lowest latency, 100% CPU
- `YieldingWaitStrategy`: spin 100 times, then `Thread.yield()` — still high CPU
- `BlockingWaitStrategy`: `synchronized` + `mutex.wait()` — OS sleep, low CPU, high latency

**Disruptor technical paper:** Martin Thompson, Dave Farley et al. (2011).
"Disruptor: High performance alternative to bounded queues for exchanging data between concurrent threads."
LMAX tech note. Reported ~25ns per message vs ~100ns for `ArrayBlockingQueue` in single-producer benchmarks. [UNVERIFIED: exact benchmark numbers; paper not fetchable from proxy]

---

### 1.3 Consistent Hashing

**Forcing constraint:** With `n` servers, `hash(key) % n` assigns every key. Remove one server:
`(n-1)/n ≈ 100%` of keys must migrate. The constraint: *minimize key migration when server
count changes*. Ideal: O(K/N) migrations (only keys from the changed server).

**Karger et al. (1997) mechanism:**
- Hash both keys AND servers onto the same ring [0, 2^32) using any hash function
- Key → assigned to the **first server clockwise** on the ring
- Add server S': only keys in the arc (predecessor(S'), S'] migrate to S'
- Remove server S: only keys assigned to S migrate to S's clockwise successor
- Expected migrations: K/N (vs K(N-1)/N for modulo hashing)

**Virtual nodes (key practical addition):**
- With only N physical points, load distribution has high variance (by birthday paradox)
- Place each physical server at R distinct ring positions (virtual nodes) using different hash inputs
- Expected load per server = K/N ± σ where σ ≈ K/(N · √R)
- Typical R = 100–200 to get < 5% load standard deviation
- Lookup: `O(log(N·R))` binary search on sorted virtual node array

**Google groupcache implementation (verified, `consistenthash/consistenthash.go`):**
```go
type Map struct {
    hash     Hash     // default: crc32.ChecksumIEEE
    replicas int      // virtual nodes per server
    keys     []int    // sorted ring positions
    hashMap  map[int]string
}
// Add: for i in [0, replicas): hash(strconv.Itoa(i) + key) → insert into sorted keys
// Get: binary search for first key >= hash(query); wrap to 0 if no match
```

**Jump consistent hash (Lamping & Veach, 2014 Google):**
```go
func Hash(key uint64, numBuckets int) int32 {
    var b, j int64 = -1, 0
    for j < int64(numBuckets) {
        b = j
        key = key*2862933555777941757 + 1  // LCG step
        j = int64(float64(b+1) * (float64(1<<31) / float64((key>>33)+1)))
    }
    return int32(b)
}
```
O(log N) time, ~5 bytes state, perfect balance (no virtual nodes). Tradeoff: only supports
resize by adding/removing the last bucket — cannot remove arbitrary nodes.

**Redis Cluster (NOT consistent hashing — common confusion):**
- Uses 16384 fixed hash slots: `crc16(key) & 0x3FFF` (CLUSTER_SLOTS = 1<<14)
- Slots are statically assigned to nodes; no ring, no virtual nodes
- Migration is manual (CLUSTER MIGRATE) or automated by cluster rebalancer
- 16384 chosen because: "16384 slots provides enough granularity for typical cluster sizes
  (< 1000 nodes), and the gossip message with slot assignment fits in 2KB" [Antirez design note — UNVERIFIED exact wording, source: redis.io design doc]

**Rendezvous hashing (HRW, Thaler & Ravishankar 1998) — alternative:**
- For key k, assign to server s that maximizes hash(k, s)
- No ring, no binary search, no virtual nodes
- Lookup is O(N) (must compute hash for all servers) — acceptable for small N
- Add server: only keys where new server wins migrate (same K/N expected)
- Remove server: O(N) scan to find winner among remaining servers

---

### 1.4 HyperLogLog / Cardinality Sketches

**Forcing constraint:** Exact distinct count requires O(n) space in the worst case (information
theory lower bound). For n = 1 billion: ~4GB for a hash set. The constraint: can we estimate
with < 1% error using < 15KB? HyperLogLog (Flajolet et al. 2007) achieves 0.81% error in 12KB.

**Intuitive model:** In a uniformly random bit stream, the probability of seeing k consecutive
leading zeros is 2^(-k). So the maximum run of leading zeros in a stream of n hashes is ≈ log₂(n).
Problem: single estimator has massive variance. Solution: use m independent estimators and combine
via harmonic mean.

**Deep mechanism (Redis `hyperloglog.c` — fully verified):**

**Parameters:**
```c
#define HLL_P 14                    /* b = 14 bits for register index */
#define HLL_Q (64-HLL_P)            /* 50 bits for leading-zero position */
#define HLL_REGISTERS (1<<HLL_P)    /* m = 16384 registers */
#define HLL_BITS 6                  /* each register stores max val 0-63 */
#define HLL_ALPHA_INF 0.721347520444481703680  /* 0.5/ln(2), for m→∞ */
```

**Add element pipeline (`hllPatLen`):**
1. Hash element with MurmurHash2 64-bit → `uint64_t hash`
2. Low 14 bits → register index (0..16383)
3. Remaining 50 bits: count position of leftmost 1-bit (= number of leading zeros + 1)
4. `M[index] = max(M[index], count)` — only update if new max

**Cardinality estimation (uses Ertl 2017, NOT original Flajolet):**
```c
// hllCount() uses hllSigma and hllTau for boundary corrections
double z = m * hllTau((m - reghisto[HLL_Q+1]) / (double)m);
for (j = HLL_Q; j >= 1; --j) {
    z += reghisto[j];
    z *= 0.5;
}
z += m * hllSigma(reghisto[0] / (double)m);
E = llroundl(HLL_ALPHA_INF * m * m / z);
```
The register histogram `reghisto[v]` counts how many of the 16384 registers hold value `v`.
`hllSigma` corrects for all-zero registers (undercount bias); `hllTau` corrects for saturated
registers (overcount bias). Cited: Otmar Ertl, arXiv:1702.01284.

**Standard error:** 1.04/√m
- m=16384 → 0.81%
- m=1024  → 3.25%
- m=256   → 6.5%

**Memory layout — dense representation:**
- 16384 registers × 6 bits = 98,304 bits = 12,288 bytes = 12KB
- Registers packed across byte boundaries (6-bit fields straddle bytes):
  ```
  |11000000|22221111|33333322|...
  ```
- Clearing/setting requires 2-byte read-modify-write at most

**Memory layout — sparse representation (for low cardinality):**
- Run-length encoded using 3 opcodes:
  - `ZERO (00xxxxxx)`: 1–64 consecutive zero registers
  - `XZERO (01xxxxxx yyyyyyyy)`: 1–16384 zero registers (14-bit run + 1)
  - `VAL (1vvvvvxx)`: 1–32 non-zero value, repeated 1–4 times
- A fresh empty HLL is just: `XZERO:16384` (2 bytes)
- At cardinality ~10,000: sparse uses ~10.5KB; promotes to dense at 12KB threshold
- Threshold: `server.hll_sparse_max_bytes` (configurable)

**Merge operation:** `PFMERGE` = element-wise max of registers:
`M_merged[i] = max(M_A[i], M_B[i])` for all 16384 registers. Estimate on merged = estimate of union.

**16-byte header:**
```c
struct hllhdr {
    char magic[4];      /* "HYLL" */
    uint8_t encoding;   /* HLL_DENSE or HLL_SPARSE */
    uint8_t notused[3];
    uint8_t card[8];    /* cached cardinality (little-endian), MSBit = validity flag */
    uint8_t registers[];
};
```
Cached cardinality: MSBit of `card[7]` = 1 means stale (invalidated on any write).

---

## 2. Foundational Sources

| Claim | Source |
|---|---|
| Skip list algorithm, p=0.5 baseline, O(log n) expected | William Pugh (1990). "Skip Lists: A Probabilistic Alternative to Balanced Trees." *Communications of the ACM* 33(6):668–676. |
| Redis skip list source (p=0.25, MAXLEVEL=32, embedded sds) | `redis/redis` `src/t_zset.c` + `src/server.h` · raw.githubusercontent.com |
| RocksDB skip list (arena allocator, release-store publish) | `facebook/rocksdb` `memtable/skiplist.h` · raw.githubusercontent.com |
| Java lock-free skip list (marker-node deletion, 3-step CAS) | `openjdk/jdk` `src/.../ConcurrentSkipListMap.java` · raw.githubusercontent.com |
| Disruptor ring buffer source (padding, availableBuffer, VarHandle) | `LMAX-Exchange/disruptor` `src/main/java/com/lmax/disruptor/` · raw.githubusercontent.com |
| Disruptor paper (throughput claims) | Martin Thompson et al. (2011). "Disruptor: High performance alternative to bounded queues…" LMAX tech note. https://lmax-exchange.github.io/disruptor/disruptor.html [HTTP 404 from proxy — paper not fetched; claims marked UNVERIFIED] |
| Consistent hashing ring algorithm | David Karger et al. (1997). "Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots…" *STOC 1997*. ACM DOI: 10.1145/258533.258660 |
| Go groupcache consistent hash impl (replicas, binary search) | `golang/groupcache` `consistenthash/consistenthash.go` · raw.githubusercontent.com |
| Jump consistent hash (LCG-based, O(log N)) | John Lamping, Eric Veach (2014). "A Fast, Minimal Memory, Consistent Hash Algorithm." arXiv:1406.2294. |
| Redis Cluster: 16384 slots, CRC16, not consistent hashing | `redis/redis` `src/cluster.h` · CLUSTER_SLOTS = 1<<14 verified |
| HyperLogLog algorithm (harmonic mean, α_m, 1.04/√m error) | P. Flajolet, É. Fusy, O. Gandouet, F. Meunier (2007). "HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm." *Disc. Math. & Theor. Comput. Sci.* Proc. AH. http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf (HTTP 200 confirmed) |
| Ertl 2017 correction (hllSigma/hllTau, replaces bias table) | Otmar Ertl (2017). "New cardinality estimation algorithms for HyperLogLog sketches." arXiv:1702.01284. |
| Redis HLL source (HLL_P=14, dense/sparse, hllCount, hllPatLen) | `redis/redis` `src/hyperloglog.c` · raw.githubusercontent.com |
| HyperLogLog++ (bias correction, 5-bit registers) | Heule, Nunkesser, Hall (2013). "HyperLogLog in Practice: Algorithmic Engineering of a State of the Art Cardinality Estimation Algorithm." EDBT 2013. Cited in Redis hyperloglog.c as reference [1]. |

---

## 3. Why It's This Way — Constraints and Tradeoffs

### Skip list: why not always use a balanced BST?
- BST rotations touch O(log n) nodes — hard to make lock-free. Rebalancing requires
  a "last writer wins" invariant that's tricky with concurrent readers.
- Skip list insertions/deletions touch only nodes in the local neighborhood (the `update[]`
  predecessor array). With CAS on the `next` pointer, you get lock-free correctness with
  only a 3-step delete (Java) or writer-holds-mutex (RocksDB memtable).
- Tradeoff: random level assignment means worst-case O(n) possible (astronomically unlikely).

### Skip list p=0.25 (Redis) vs p=0.5 (Pugh's original):
- p=0.5: average levels per node = 2.0; optimal time constant.
- p=0.25: average levels per node = 1.33; 33% fewer pointers, 33% less memory.
- Redis chose p=0.25 because ZSET is memory-bound (millions of sorted sets in a cache server).

### Ring buffer: why power-of-2?
- Modulo is the obvious operation: `slot = seq % size`. On x86, integer division is 20-90 cycles.
- AND with `(size-1)` is 1 cycle. For 6M events/sec that's ~60ms vs ~0.6ms difference at 100M events/sec.
- Tradeoff: you cannot use arbitrary sizes; common sizes (1024, 4096, 65536) are all natural.

### Disruptor: why pre-allocate?
- Java GC stop-the-world pause = latency spike. Even G1 GC has "remark" pauses of ms order.
- Pre-allocated events + in-place mutation = zero allocation in steady state = no GC pressure.
- Tradeoff: event objects must be mutable; functional event records don't work.

### Disruptor: why `availableBuffer` for multi-producer?
- Multiple producers race to claim sequences via CAS. A producer might claim seq=5 but be slow.
- Producer for seq=7 must NOT publish seq=7 as visible until seq=5 is published.
- `availableBuffer[slot] = wrap_count` lets consumers check "is seq 7 in wrap 0 published?" without
  a shared cursor that would require producer coordination.

### Consistent hashing: why virtual nodes?
- Without virtual nodes, N servers → N points on ring. With small N, variance in arc sizes is
  huge (birthday paradox: some arcs 3× longer than others → 3× load imbalance).
- V virtual nodes per server: std dev of arc sizes ∝ 1/√V. At V=200, ~5% std dev.
- Tradeoff: ring size = N×V entries; binary search is O(log(N×V)). At N=100, V=200, that's
  log₂(20000) ≈ 14 comparisons — negligible.

### HyperLogLog: why harmonic mean (not arithmetic)?
- Arithmetic mean of `2^(-M[j])` is dominated by outlier registers with large M values.
- Harmonic mean of counts (`Σ 2^(-M[j])`)^(-1) gives less weight to large values.
- Flajolet's insight: harmonic mean of geometric samples is a min-variance estimator for this
  probability model. The bias correction constant α_m accounts for correlation bias at small m.

### HyperLogLog: why 6 bits per register?
- Hash is 64 bits. Register index uses 14 bits. Remaining 50 bits for leading-zero count.
- Maximum possible leading zeros in 50 bits: 50. Need to represent 0-50 → 6 bits (max 63 > 50).
- Redis uses HLL_Q=50, so max storable = 63 > 50. The 6-bit field is exact.

### HyperLogLog: why switch to Ertl (2017) from original Flajolet (2007)?
- Original Flajolet used empirical small-range correction and large-range correction with
  separate thresholds (n < 2.5m → LinearCounting; n > 2^32/30 → correction for 32-bit hash).
- Ertl (2017) derives exact closed-form corrections (σ/τ functions) for boundary cases,
  valid for 64-bit hashes without 32-bit overflow issues. Monotonic, no threshold discontinuities.
- Redis adopted Ertl because 64-bit MurmurHash2 never overflows, eliminating large-range correction,
  but small-range correction (all-zeros registers) still needed → hllSigma.

---

## 4. Common Misconceptions to Preempt

1. **"Skip lists are random / non-deterministic structures."**  
   The *structure* is randomized (node heights), but search is fully deterministic given that structure.
   Expected O(log n) is over the randomness of insertion order, not query execution. In practice,
   worst-case degradation is vanishingly unlikely (probability ∝ n·(1/p)^(-k)).

2. **"Disruptor is just a fancy BlockingQueue."**  
   Disruptor is a ring buffer with a sequencing protocol, not a queue. Key differences:
   (a) No head/tail pointers — just a cursor and gating sequences.
   (b) No per-event allocation. (c) Multiple consumers can each maintain their own position,
   reading the same event independently — impossible in a queue (events consumed once only).

3. **"Redis Cluster uses consistent hashing."**  
   Redis Cluster uses slot-based partitioning: 16384 fixed slots, `crc16(key) & 0x3FFF`.
   Consistent hashing is a different algorithm (ring of virtual nodes). Redis documentation
   historically used "consistent hashing" loosely before clarifying this.

4. **"PFMERGE estimates the union by summing cardinalities."**  
   Wrong. PFMERGE does element-wise `max` of the two register arrays, then estimates on the
   merged structure. Adding cardinalities would double-count elements present in both sets.

5. **"HyperLogLog has 0.81% error always."**  
   0.81% is the *standard error* (one sigma) for m=16384 registers. Actual error is a random
   variable; 95% confidence interval is ±1.6%, 99.7% is ±2.4%. Also: for very small cardinalities
   (< few hundred), the sparse representation's estimate is based on a different algorithm
   (LinearCounting-like via XZERO/VAL structure) and can be more accurate.

6. **"Consistent hashing is always O(1) lookup."**  
   O(1) only if you use direct probing (rendezvous/HRW). Ring-based consistent hashing needs
   a binary search over the sorted virtual node array: O(log(N×V)).

7. **"False sharing only happens when two variables are in adjacent memory."**  
   False sharing occurs when two variables are in the *same cache line* (64B on x86). Struct
   fields, array elements, or class fields can all cohabit a cache line. The Disruptor pads with
   56 bytes before AND after each `long value` for this reason.

8. **"Skip list p=0.5 is always better than p=0.25."**  
   Pugh's analysis shows p=0.5 minimizes time constant; p=0.25 uses 33% less memory at the cost
   of ~11% more comparisons per search. For in-memory databases (Redis), memory wins.

---

## 5. Best Build-Your-Own Targets

| Target | Complexity | What it teaches |
|---|---|---|
| **SPSC ring buffer** | ~80 lines (C or Rust) | Cache-line padding, memory ordering (release/acquire), wrap via AND |
| **Skip list with rank** | ~250 lines (C or Go) | Probabilistic level generation, `update[]` predecessor array, span tracking |
| **Consistent hash ring** | ~100 lines (Go or Python) | Virtual nodes, binary search on sorted ring, migration counting |
| **HyperLogLog (dense only)** | ~150 lines (C or Python) | 6-bit register packing, hash splitting, harmonic mean estimator, σ/τ corrections |
| **MPSC ring buffer** | ~180 lines (Java or Rust) | CAS for multi-producer, availableBuffer flag pattern, wrap prevention |

**Priority for course:** SPSC ring buffer first (most concrete, cache-line padding is vivid), then skip list (most "magical" feeling, randomness is surprising), then HyperLogLog (most mathematical).

**SPSC ring buffer key insight to demonstrate:**  
Write two versions: one with shared struct `{head, tail}` on same cache line, one padded. Measure with `perf stat` or `criterion`. The 5-10× throughput difference makes false sharing unforgettable.

---

## 6. Open Questions / Where Sources Disagree

1. **Optimal virtual node count for consistent hashing.**  
   Karger et al. (1997) provides the mathematical framework; practical guidance (100 vs 150 vs 200)
   is empirical. AWS DynamoDB used 200 tokens initially, then switched to a different strategy
   (partition-based, not token-ring) in DynamoDB v2 [UNVERIFIED: exact DynamoDB architecture].

2. **Ertl (2017) vs HyperLogLog++ (Heule et al. 2013) at low cardinality.**  
   Redis uses Ertl's σ/τ corrections. Google's BigQuery and other systems use HyperLogLog++
   (5-bit registers + empirical bias correction table from paper). At cardinalities < 5m,
   HyperLogLog++ claims lower error than original HLL due to empirical corrections; Ertl claims
   his analytic corrections are better asymptotically. Redis's choice to use Ertl is not
   documented with a head-to-head benchmark in the source code.

3. **Lock-free skip lists on TSO (x86) vs weaker memory models.**  
   Java's `ConcurrentSkipListMap` uses `VarHandle` with release/acquire semantics — correct on
   all JVM platforms. Doug Lea's comment notes "this technique would not work well in systems
   without GC." In C++, lock-free skip lists without GC require hazard pointers or epoch-based
   reclamation. The correct memory ordering for the level-array on ARM (where TSO doesn't hold)
   is debated in the literature.

4. **Rendezvous hashing (HRW) vs consistent ring hashing for small N.**  
   HRW: O(N) lookup, O(1) space per node, perfect balance without virtual nodes.
   Consistent ring: O(log(N×V)) lookup, O(N×V) sorted array space.
   For N < 20 servers, HRW is often strictly better. Sources disagree on the crossover point.

5. **Disruptor throughput benchmarks.**  
   LMAX's whitepaper (2011) reported 25M events/sec. The paper is not fetchable (404 from proxy).
   Later benchmarks comparing to `ArrayBlockingQueue`, Aeron, etc. show Disruptor winning on
   single-producer latency but modern lock-free MPSC queues (e.g., crossbeam-channel in Rust,
   Aeron in Java) close the gap significantly. No definitive neutral benchmark found.

6. **Skip list vs B+-tree for write-heavy concurrent workloads.**  
   RocksDB uses skip list for memtable (write-fast, concurrent readers). WiredTiger (MongoDB)
   uses a B-tree with its own cursor mechanism. At high write concurrency, the skip list's
   local modification property appears to win. At read-heavy workloads, B+-tree cache locality
   wins. Literature on exactly when to prefer which is inconclusive.

---

*Gaps not covered: Cuckoo hashing, Count-Min sketch, t-digest, Quotient filter, Chord/Kademlia DHT
finger tables, NUMA-aware ring buffer design. These are adjacent but outside the assigned cluster.*
