# Reconciled Research Brief — 06 Data Structures for Systems

Cluster briefs reconciled:
- `_research_indexes-lsm-bloom.md` — B+/B-trees, LSM trees, Bloom filters.
- `_research_probabilistic-distributed-queues.md` — skip lists, ring buffers, consistent hashing, HyperLogLog.

Phase 1 artifact only. No chapters. Use cluster briefs for full detail and exact source tables.

---

## 1. Key mechanisms — consolidated spine

### Why systems data structures differ from textbook data structures
Systems data structures optimize for hardware and operational constraints: page/cache-line locality, branch prediction, memory allocation behavior, concurrency, crash recovery, distribution, and bounded error. Big-O alone is not enough. A B+tree and skip list are both `O(log n)`, but one minimizes disk/page reads while the other minimizes rebalancing and lock complexity.

### B+trees: page-local search and range scans
B+trees exist because random I/O dominates CPU. A binary tree over a billion records needs ~30 pointer hops/page reads; a page-sized high-fanout tree collapses that to 3–4. Production databases usually mean B+tree when they say B-tree: internal nodes store separator keys and child pointers; leaves store data and are linked for range scans. SQLite exposes page anatomy directly: page header, sorted cell pointer array growing downward, cell content area growing upward, overflow pages for large payloads. PostgreSQL nbtree uses Lehman-Yao high keys and right links so readers can follow concurrent splits without locking the whole path; it adds left links, heap TID tiebreakers, suffix truncation, dedup/posting lists, and bottom-up deletion.

### LSM trees: convert random writes into sequential merges
LSM trees buffer writes in memory (memtable), append to WAL, flush sorted immutable SST files, and merge/compact levels in the background. LevelDB/RocksDB make the write path explicit: WAL + memtable → immutable memtable → level-0 SST → leveled compaction into non-overlapping key ranges. L0 files may overlap because flushes must be fast; L1+ files do not overlap so point reads check at most one file per level. Tombstones represent deletes until compaction proves no older value remains. Tradeoff: LSMs reduce random write latency but introduce write amplification, read amplification, and compaction stalls.

### Bloom filters: fast “definitely absent” answers
Bloom filters store membership in a bit array using k hash-derived probes. They never produce false negatives, only false positives. This matches immutable SST files: if the filter says absent, skip disk; if maybe present, read the SST and verify. LevelDB/RocksDB derive k positions from one hash via double hashing (`k ≈ bits_per_key * ln(2)`) and store filters per SST/filter block, not globally. Cache-local Bloom filters trade a slightly higher false-positive rate for fewer cache-line loads.

### Skip lists: probabilistic balancing with local mutations
Skip lists are sorted linked lists with probabilistically sampled express lanes. Pugh's baseline uses p=0.5; Redis/RocksDB use p=0.25 to save pointers/memory. Search descends top-down; insert records predecessor pointers in `update[]`; deletion is local. Redis adds `span` fields for rank queries (`ZRANK`) and level-0 backward pointers for reverse scans. RocksDB uses an arena-backed skiplist for memtables: writes are externally synchronized, reads can be lock-free because nodes are never individually freed until memtable flush. Java's `ConcurrentSkipListMap` uses marker-node deletion and CAS, relying on GC for safe reclamation.

### Ring buffers and queues: cache lines, allocation, and memory ordering
A ring buffer uses monotonic sequence numbers and power-of-two masks (`seq & (size-1)`) instead of modulo. The LMAX Disruptor preallocates event slots to eliminate steady-state allocation/GC, pads sequence counters and arrays to avoid false sharing, and separates claim/publish/consume sequencing. Single-producer mode avoids CAS on the hot path; multi-producer mode uses CAS plus an availability buffer that tracks wrap flags. Wait strategies encode latency/CPU tradeoffs: busy spin, yield, or blocking wait.

### Consistent hashing: minimize key movement under membership change
Modulo hashing remaps almost every key when N changes. Ring-based consistent hashing hashes servers and keys onto the same ring; a key maps to the first server clockwise. Adding/removing a server only moves keys in adjacent arcs. Virtual nodes reduce load variance (`σ ∝ 1/√V`) by giving each real server many ring points. Jump consistent hash gives minimal movement with no ring but only supports tail-style bucket count changes. Redis Cluster is **not** ring consistent hashing; it uses 16,384 fixed CRC16 slots.

### HyperLogLog: cardinality with fixed memory
HyperLogLog estimates distinct count by splitting a hash into register index + leading-zero run length. Each register stores the maximum observed run length for its bucket; estimate uses a harmonic-mean-like aggregation with bias correction. Redis uses p=14 (`m=16384`), 6-bit registers, ~12KB dense representation, MurmurHash2 64-bit, sparse encoding for small cardinalities, cached cardinality with validity bit, merge as element-wise max, and Ertl 2017 correction functions (`hllSigma`, `hllTau`). The famous ~0.81% is standard error, not a hard bound.

---

## 2. Foundational sources — canonical anchors

- B+tree/B-tree: SQLite `btreeInt.h`, SQLite file format docs, PostgreSQL `src/backend/access/nbtree/README`, PostgreSQL `configure` for BLCKSZ. Bayer & McCreight/Comer papers were blocked/paywalled; implementation sources are the reliable anchors here.
- LSM: O'Neil et al. 1996 PDF URL `cs.umb.edu/~poneil/lsmtree.pdf` fetched but text not extracted; LevelDB `doc/impl.md` and `doc/table_format.md`; RocksDB `options.h`, `advanced_options.h`, `dbformat.h`, compaction picker, and tuning wiki mirror.
- Bloom: LevelDB `util/bloom.cc`; RocksDB `util/bloom_impl.h`; Kirsch-Mitzenmacher 2006 cited by RocksDB; Bloom 1970 not directly fetched.
- Skip list: Pugh 1990 CACM paper; Redis `src/t_zset.c` / `server.h`; RocksDB `memtable/skiplist.h`; OpenJDK `ConcurrentSkipListMap.java`.
- Ring buffer: LMAX Disruptor Java source (`RingBuffer`, `Sequence`, sequencers, wait strategies); LMAX whitepaper benchmark numbers remain `[UNVERIFIED]` due fetch issues.
- Consistent hashing: Karger et al. 1997; Go groupcache `consistenthash.go`; Jump consistent hash paper; Redis Cluster `cluster.h` for 16,384 slots.
- HyperLogLog: Flajolet et al. 2007 PDF, Ertl 2017, Redis `hyperloglog.c`, HyperLogLog++ paper cited in Redis source.

---

## 3. Why it's this way — constraints/tradeoffs

- **B+tree fanout:** one disk/page read per level dominates; internal nodes hold only separators to maximize fanout and minimize height.
- **Leaf linking:** range scans should move leaf-to-leaf, not repeatedly ascend/descend.
- **Lehman-Yao links/high keys:** concurrent splits must not make readers miss keys; right links and high keys let readers recover from stale descent decisions.
- **LSM immutability:** sorted immutable SSTs make sequential writes and merge compaction simple; deletes require tombstones because old values may exist in lower levels.
- **Leveled compaction:** non-overlap in L1+ bounds point-read work; compaction cursor rotation avoids repeatedly compacting one hot range.
- **Bloom no-deletion:** immutable SSTs perfectly fit standard Bloom filters because membership never changes after construction.
- **Skiplist p=0.25:** fewer pointers save memory in Redis/RocksDB at small comparison-cost penalty.
- **Ring power-of-two:** bitmask wrap avoids expensive division; padding prevents cache-line invalidation storms.
- **Virtual nodes:** ring hashing with few physical nodes has high arc-size variance; virtual nodes smooth load at O(NV) ring storage.
- **HLL harmonic mean:** leading-zero samples are geometric and outlier-heavy; harmonic-style aggregation plus correction reduces bias.

---

## 4. Common misconceptions to preempt

- B-tree and B+tree are identical — false; databases usually use B+tree leaves-for-data.
- LSM eliminates write amplification — false; it trades random writes for compaction/write amplification.
- Bloom filters can return false negatives — false for standard Bloom; absent is definitive.
- LevelDB/RocksDB use one global Bloom filter — false; filters are per SST/filter block.
- Skip lists are “random at query time” — false; randomness occurs during insertion height selection.
- Disruptor is just a queue — false; it is a sequencing/ring protocol with multicast-style consumers.
- Redis Cluster uses consistent hashing — false; it uses fixed CRC16 slots.
- HLL 0.81% is max error — false; it is standard error for Redis's m=16384.
- `PFMERGE` sums counts — false; it merges registers by element-wise max then estimates.
- Consistent hashing lookup is always O(1) — ring implementations binary-search virtual nodes.

---

## 5. Best build-your-own targets

1. **Bloom filter** (~200 LOC): compute optimal m/k, add/contains with double hashing, measure FP rate and prove zero false negatives.
2. **SPSC ring buffer** (~80 LOC): release/acquire ordering, power-of-two wrap, padded vs unpadded benchmark to show false sharing.
3. **Skip list with rank** (~250 LOC): p-level generation, update array, spans for rank queries.
4. **Consistent hash ring** (~100 LOC): virtual nodes, sorted ring, binary search, add/remove migration measurement.
5. **Dense HyperLogLog** (~150 LOC): p-bit register index, leading-zero count, 6-bit register packing, merge=max, Ertl correction if ambitious.
6. **Mini-LSM** (~1000 LOC): WAL, memtable, SST with index+Bloom, simple compaction, MANIFEST.
7. **Single-threaded B+tree** (~2000 LOC): file-backed pages, internal/leaf node split, linked leaves, range scan; add WAL only after correctness.

---

## 6. Open questions / gaps

- Original Bayer & McCreight, Comer, Bloom 1970, and some LMAX whitepaper details were blocked/paywalled; use implementation sources unless direct paper access is obtained.
- SQLite default page size and PostgreSQL exact fill factor were not confirmed from source in this pass; keep as `[UNVERIFIED]` if quoted.
- RocksDB Ribbon filters, universal vs leveled compaction crossover, L0 subcompaction behavior, and WiscKey/value-log separation need more source work if included.
- Consistent hashing virtual-node counts are empirical; no single canonical “right number.”
- Ertl HLL vs HyperLogLog++ at low cardinality is a genuine design fork; avoid declaring one universally superior.
- Lock-free skip lists in C/C++ need memory reclamation (hazard pointers/epochs); Java examples rely on GC and do not transfer directly.
- Adjacent structures not covered: cuckoo hashing, quotient/ribbon filters, count-min sketch, t-digest, CRDT counters, Chord/Kademlia finger tables, NUMA-aware queues.
