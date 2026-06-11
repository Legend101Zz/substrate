# 06 — Data Structures for Systems · _structure.md

**Identity:** the data structures that actually run inside databases, caches, queues, and
distributed systems — chosen for hardware and operational reality, not Big-O on a whiteboard.

**Bespoke shape — "catalogue organized by the constraint each structure beats."** NOT a
narrative ascent and NOT one-mechanism-per-altitude. It is a problem-driven CATALOGUE:
each chapter is one structure, framed by the *physical/operational constraint that makes the
textbook answer wrong* (random I/O dominates CPU; membership change must not remap
everything; counting distinct things must fit in fixed memory…). Opening chapter states the
meta-thesis; each entry then runs the same internal beat — **constraint → structure →
mechanism → real-system instantiation → tradeoff/misconception → tiny build.** Bridges 04
(pages/cache lines) up into 07/08/09/11/14.

## Dependency position
- **Depends on:** 01 (memory/cache-line/locality), 04 (pages, page cache, allocation), light
  N (the math — Bloom k, HLL error, consistent-hashing variance live in N).
- **Feeds into:** 07 (B+tree/LSM ARE the DB storage engine), 08 (eviction/ring buffers),
  09 (the log = ring buffer + segments), 11/14 (consistent hashing = partitioning),
  16 (cache structures), 30 (HNSW/ANN echoes skip-list ideas).
- **Appendix links DOWN:** F-postgres (nbtree deep), G-redis (skiplist/listpack/HLL deep),
  H-kafka (the log), N-math (all the formulas re-derived). 06 teaches the structure; the
  appendices show the production instantiation in full.

## Chapter specs (3–5 lines each)
0. **Why systems data structures differ** (short opener) — the meta-thesis: page/cache-line
   locality, allocation behavior, concurrency, crash recovery, distribution, bounded error
   beat Big-O. A B+tree and skip list are both O(log n); one minimizes page reads, the other
   rebalancing/lock complexity. This frame governs every entry.
1. **B+trees — page-local search & range scans** — random I/O dominates ⇒ high-fanout tree
   collapses ~30 hops to 3–4. Internal=separators, leaves=data+linked for ranges. SQLite
   page anatomy (header, cell-pointer array, content area, overflow); PostgreSQL nbtree
   Lehman-Yao high keys + right links (lock-free-ish concurrent reads), suffix truncation,
   dedup. Tradeoff vs LSM. → F.
2. **LSM trees — random writes → sequential merges** — memtable + WAL → immutable sorted
   SSTs → leveled compaction (L0 may overlap; L1+ don't ⇒ ≤1 file/level per point read).
   Tombstones for deletes. Write/read/space amplification + compaction stalls. LevelDB/
   RocksDB as reference. → G/H.
3. **Bloom filters — fast "definitely absent"** — k hash probes in a bit array; no false
   negatives, only false positives ⇒ perfect for immutable SSTs (skip disk on "absent").
   Double-hashing for k positions, `k ≈ bits_per_key·ln2`, per-SST not global, cache-local
   variant. Math → N. Misconception: it CAN'T return a false negative.
4. **Skip lists — probabilistic balancing, local mutations** — sorted linked list +
   sampled express lanes; Pugh p=0.5, Redis/RocksDB p=0.25. Search descends, insert via
   `update[]`, deletion local. Redis `span` for `ZRANK`; RocksDB arena skiplist memtable
   (lock-free reads). Why chosen over B-tree for memtables (no page rebalance, simple
   concurrency).
5. **Ring buffers & queues — cache lines, allocation, ordering** — monotonic seq + power-of-
   two mask (no modulo). LMAX Disruptor: preallocated slots (no steady-state GC), padding
   vs false sharing, claim/publish/consume sequencing; SPSC avoids CAS, MPMC uses CAS +
   availability buffer. Wait strategies = latency/CPU knob. Feeds 09/17.
6. **Consistent hashing — minimize key movement on membership change** — modulo remaps
   ~everything; ring maps key→first server clockwise so only adjacent arcs move. Virtual
   nodes cut variance (σ ∝ 1/√V). Jump hash = minimal movement, no ring, tail-only bucket
   changes. **Redis Cluster is NOT consistent hashing** — 16,384 fixed CRC16 slots. Feeds
   11/14.
7. **HyperLogLog — cardinality in fixed memory** — hash → register index + leading-zero
   run; register stores max run; harmonic-mean aggregation + bias correction. Redis p=14
   (m=16384), 6-bit registers, ~12KB, sparse→dense, merge = element-wise max. The famous
   ~0.81% is STANDARD error, not a bound. Math → N.

## Paired build labs (/build — each entry has a small one)
1. Bloom filter (~200 LOC): optimal m/k, double-hash, prove zero false negatives, measure FP.
2. SPSC ring buffer (~80 LOC): release/acquire ordering, power-of-two wrap, padded-vs-unpadded
   false-sharing benchmark.
3. Skip list with rank (~250 LOC): level generation, update array, spans.
4. Consistent hash ring (~100 LOC): virtual nodes, sorted ring, binary search, migration
   measurement on add/remove.
5. Dense HyperLogLog (~150 LOC): register index, leading-zero count, 6-bit packing, merge=max.
6. (Stretch) mini-LSM (~1000 LOC): WAL + memtable + SST(index+Bloom) + compaction + MANIFEST.
7. (Stretch) single-threaded file-backed B+tree (~2000 LOC): node split, linked leaves, range
   scan; add WAL only after correctness.

## Diagrams needed
- B+tree (internal separators + linked leaves) with a range scan path; SQLite page layout.
- LSM write path (WAL→memtable→L0→leveled compaction) + read path checking Bloom per level.
- Bloom filter bit-array with k probes (one "maybe" vs one "definitely absent").
- Skip list with express lanes + a search descent; span/rank annotation.
- Ring buffer with seq + mask wrap; padded counters (false-sharing illustration).
- Consistent-hash ring before/after adding a node (only adjacent arc moves) + virtual nodes.
- HLL: hash split into index+run-length; registers; merge=max.

## Sources / gaps to honor (from _research.md)
- Implementation sources are the reliable anchors (Bayer-McCreight/Comer/Bloom-1970/LMAX
  whitepaper were blocked/paywalled). `[UNVERIFIED]` if quoting SQLite default page size or
  PostgreSQL exact fill factor — confirm from source.
- Empirical, no canonical number: consistent-hashing virtual-node counts. Genuine design
  fork: Ertl HLL vs HLL++ at low cardinality — don't declare a universal winner.
- Lock-free skip lists need memory reclamation (hazard pointers/epochs); Java GC examples
  don't transfer to C/C++ directly — note in the skip-list build.
- Math claims (Bloom k, HLL 1.04/√m, consistent-hashing variance, fan-out) are RE-DERIVED in
  appendix N — cross-link rather than re-prove in 06.
- Out of scope (note as "see also," not covered): cuckoo/quotient/ribbon filters, count-min,
  t-digest, CRDT counters, Chord/Kademlia fingers.
