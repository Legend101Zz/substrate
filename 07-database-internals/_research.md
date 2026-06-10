# Reconciled Research Brief — 07 Database Internals

Cluster briefs reconciled:
- `_research_storage-query-exec.md` — pages, tuples, buffer pool, WAL boundary, B+ tree, Volcano/batched executors, core operators, BusTub rule optimizer.
- `_research_transactions-recovery.md` — WAL/LSN, ARIES model, MVCC, isolation, 2PL/OCC, locking/deadlocks, PostgreSQL/BusTub/InnoDB anchors.
- `_research_optimizer-external-exec.md` — System R/Selinger, PostgreSQL optimizer/statistics/costing, external sort, hash join variants, vectorized/compiled execution, storage models.
- `_factcheck_phase1.md` — spot-check report; blockers were patched in the briefs with resolution notes.

Phase 1 artifact only. No chapters. Use cluster briefs for full detail and exact source tables.

---

## 1. Key mechanisms — consolidated spine

### Page layout, tuple identity, and the unit of I/O
Database internals start at the page because durability, caching, indexing, and recovery all attach to page-sized units. BusTub uses `BUSTUB_PAGE_SIZE = 8192` and PostgreSQL defaults to 8KB builds, while PostgreSQL's `ItemIdData` bit fields cap supported page sizes at 32KB. A slotted page splits the page into a header, a forward-growing slot/line-pointer array, backward-growing tuple bytes, and free space between them. The slot number becomes the stable in-page identity; tuple bytes can move during compaction without invalidating tuple IDs.

BusTub's `TablePage` is the teaching-clean version: 8B header (`NextPageId`, `NumTuples`, `NumDeletedTuples`), `TupleInfo` entries of 24B, and `TupleMeta` entries of 16B. PostgreSQL's heap page is production-grade: `PageHeaderData` is 24B (`pd_lsn`, checksum, flags, free-space offsets, special-space offset, page-size/version, prune XID), `ItemIdData` is 4B (`lp_off:15`, `lp_flags:2`, `lp_len:15`), and heap tuple headers are 23B before null bitmap and aligned data. The page header's LSN is the bridge from storage layout to WAL correctness.

### Buffer pool, replacement, and dirty-page control
The buffer pool is not “just a cache.” It is the DBMS-owned authority for page identity, pin counts, latches, dirty state, replacement, and WAL-safe eviction. BusTub's current master uses `ArcReplacer` with MRU/MFU and MRU/MFU ghost lists; legacy `LRUK_REPLACER_K = 10` still exists in `config.h`, so do not teach current BusTub as LRU-K without caveat. PostgreSQL exposes the same forcing constraint differently: a dirty page cannot be flushed until WAL has reached that page's LSN. This is the core reason a DBMS cannot delegate everything to OS page cache / `mmap` without losing query-aware replacement and recovery ordering control. Crotty et al. 2022 mmap paper identity remains `[UNVERIFIED]` until directly fetched.

### WAL, LSNs, and recovery boundary
WAL exists because page writes are random, partial, and crashable; log writes are sequential and become the authoritative history. The rule has two parts: the log record describing a page change must reach stable storage before the changed page, and a commit record must be durable before commit is acknowledged. BusTub's `LogRecord` source defines `HEADER_SIZE = 20` with fields `size | LSN | transID | prevLSN | LogType`; because current `txn_id_t = int64_t`, treat 20B as BusTub's serialized/header-size contract from source, not native C++ object layout math. PostgreSQL WAL records are resource-manager-dispatched (`XLogRecord`) and carry record length, XID, previous record pointer, info, resource manager ID, and CRC.

ARIES is the conceptual recovery model: Analysis rebuilds the dirty-page and transaction tables; Redo repeats history from the earliest recLSN; Undo follows loser transactions backward and writes CLRs. Exact ARIES paper details, CLR field names, and page references remain `[UNVERIFIED]` because the ACM source was blocked; keep them as conceptual anchors until primary text is fetched.

### B+ trees and access paths
B+ trees exist because high fanout collapses random I/O. Internal pages store separator keys and child pointers; leaves store key/RID pairs and link to the next leaf for range scans. BusTub's B+ tree page headers are source-verified: base/internal header 12B, leaf header 16B with `next_page_id_`; internal-page slot count and leaf slot count derive from `BUSTUB_PAGE_SIZE` minus headers and tombstone metadata. PostgreSQL's nbtree (covered in 06) adds concurrency-grade mechanisms such as right links/high keys, but for 07 the key DBMS point is optimizer-visible access paths: a B+ tree is useful only when the predicate/order can exploit its physical key order.

### Volcano, batch-at-a-time execution, and blocking operators
The execution engine turns a logical plan tree into physical operators. Classic Volcano is pull-based: each parent calls `Next()` on children. BusTub's comment still says “Volcano tuple-at-a-time,” but current `AbstractExecutor::Next(vector<Tuple>*, vector<RID>*, size_t batch_size)` is batch-at-a-time and `BUSTUB_BATCH_SIZE = 20`. Teach this as iterator composition with small batches, not pure one-row-at-a-time Volcano.

Operators divide into streaming and blocking. SeqScan/IndexScan/Filter/Projection can stream. HashJoin, Aggregation, Sort, TopN have materialization points: build hash table, group hash table, sort full input, or maintain bounded heap. BusTub intentionally keeps many operators in memory only; production systems add external sort, partitioned/hybrid hash join, spill, and parallel execution.

### Transaction isolation: MVCC, 2PL, OCC, and project splits
MVCC keeps multiple row versions so readers do not block writers. PostgreSQL encodes visibility in heap tuple headers (`xmin`, `xmax`, `ctid`, infomask bits) plus snapshots (`xmin`, `xmax`, `xip[]`, `xcnt`). InnoDB uses ReadView boundaries (`m_up_limit_id`, `m_low_limit_id`, active ID list) and undo chains. BusTub Project 4 uses timestamp MVCC: in-flight tuple timestamps are high-bit transaction IDs (`TXN_START_ID = 1LL << 62`), committed versions receive commit timestamps, and prior versions live in undo logs linked through `UndoLink`.

Do not blur BusTub's teaching projects: current `transaction.h` has only `READ_UNCOMMITTED`, `SNAPSHOT_ISOLATION`, and `SERIALIZABLE`; `config.h` includes `DISABLE_LOCK_MANAGER`; and `lock_manager.h` contains Project 3 2PL spec comments mentioning `READ_COMMITTED`/`REPEATABLE_READ`, not active Project 4 enum values. This distinction is load-bearing for the course. 2PL remains the pessimistic-locking concept; OCC validates read/write conflicts at commit; BusTub's `VerifyTxn()` is currently a stub and must not be presented as a complete serializable implementation.

### Cost-based optimization, statistics, and plan search
Rule optimizers apply deterministic rewrites; cost optimizers enumerate alternatives and estimate cost. BusTub is rule-based (filter pushdown, NLJ→HashJoin, SeqScan→IndexScan, Sort+Limit→TopN, column pruning, etc.). PostgreSQL is the production anchor: it constructs `RelOptInfo` objects, stores candidate `Path`s, keeps cheapest paths plus useful orderings (`PathKey`/EquivalenceClass), compares costs with `STD_FUZZ_FACTOR = 1.01`, and falls back to GEQO around `geqo_threshold = 12` joins. Cost units are relative to `seq_page_cost = 1.0`; defaults include `random_page_cost = 4.0`, `cpu_tuple_cost = 0.01`, and `effective_cache_size = 524288` pages. Statistics (`pg_class`, `pg_statistic`, `pg_stats`, extended stats) are the fragile hinge between logical predicates and physical plans.

Selinger/System R is the historical anchor for DP over join subsets and interesting orders, but exact paper text remained scanned/unextracted. Keep Selinger-specific algorithm-text claims `[UNVERIFIED from text]` until read directly.

### External execution and modern CPU-oriented execution
Production DBMSs must spill. PostgreSQL `tuplesort.c` now uses quicksort/radix sort for run generation and balanced k-way merge; before PostgreSQL 15 it used replacement selection and polyphase merge. PostgreSQL `nodeHashjoin.c` implements hybrid hash join with power-of-two batches, serial lazy batch growth, and parallel hash join phases. These are the missing production mechanisms behind BusTub's in-memory-only sort/hash join simplifications.

Modern analytical engines reduce Volcano overhead. DuckDB processes `DataChunk`s with `STANDARD_VECTOR_SIZE = 2048` enforced by compile-time `#error` if not power-of-two; selection vectors avoid copying filtered rows. PostgreSQL JIT compiles expression evaluation and tuple deforming with LLVM. HyPer/Neumann produce/consume pipeline fusion and MonetDB/X100 vector-size details remain `[UNVERIFIED from text]` or secondary-sourced; do not harden them without primary text.

---

## 2. Foundational sources — canonical anchors

- **BusTub current master:**
  - `common/config.h` — page size, buffer pool size, `BUSTUB_BATCH_SIZE`, `LRUK_REPLACER_K`, `TXN_START_ID`, `DISABLE_LOCK_MANAGER`: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/common/config.h
  - `storage/page/table_page.h`, `storage/table/tuple.h` — slotted page, `TupleInfo`, `TupleMeta`: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/storage/page/table_page.h and https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/storage/table/tuple.h
  - `buffer/arc_replacer.h`, `buffer_pool_manager.h`, `disk_scheduler.h` — BPM and replacement: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/buffer/arc_replacer.h
  - `recovery/log_record.h`, `log_manager.h` — WAL header, log buffers, persistent LSN: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/recovery/log_record.h
  - `storage/page/b_plus_tree_*page.h` — B+ tree page layout: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/storage/page/b_plus_tree_leaf_page.h
  - `execution/executors/abstract_executor.h`, `execution/plans/abstract_plan.h`, `optimizer/optimizer.h` — executor interface, plan types, rule optimizer: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/execution/executors/abstract_executor.h
  - `concurrency/transaction.h`, `transaction_manager.cpp`, `lock_manager.h`, `watermark.h` — MVCC/undo/locks/spec caveats: https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/concurrency/transaction.h

- **PostgreSQL current master and docs:**
  - `storage/bufpage.h`, `storage/itemid.h`, `access/htup_details.h` — page/item/tuple layout and WAL pageLSN rule: https://raw.githubusercontent.com/postgres/postgres/master/src/include/storage/bufpage.h
  - `utils/snapshot.h`, `access/heap/heapam_visibility.c`, `access/transam.h` — snapshots, visibility, XID constants: https://raw.githubusercontent.com/postgres/postgres/master/src/include/utils/snapshot.h
  - `access/xlogrecord.h`, `access/xlog.h`, `catalog/pg_control.h`, `access/transam/xact.c` — WAL records, checkpoint, commit path: https://raw.githubusercontent.com/postgres/postgres/master/src/include/access/xlogrecord.h
  - `storage/lockdefs.h` — table lock modes: https://raw.githubusercontent.com/postgres/postgres/master/src/include/storage/lockdefs.h
  - `backend/optimizer/README`, `path/costsize.c`, `optimizer/cost.h`, `path/pathkeys.c`, `utils/adt/selfuncs.c` — planner, cost model, path keys, selectivity: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/README
  - Planner docs: https://www.postgresql.org/docs/current/planner-stats.html and https://www.postgresql.org/docs/current/runtime-config-query.html
  - `utils/sort/tuplesort.c`, `executor/nodeHashjoin.c`, `backend/jit/README` — external sort, hash join, JIT: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/utils/sort/tuplesort.c

- **InnoDB / MySQL 8.4 source:**
  - `read0types.h`, `trx0trx.h`, `trx0undo.h`, `lock0types.h`, `lock0lock.h`, `log0sys.h` — ReadView, transaction states, undo, locks/gaps, LSNs: https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/read0types.h

- **DuckDB source and docs:**
  - `vector_size.hpp`, `data_chunk.hpp`, `physical_hash_join.hpp`; official design attribution: https://duckdb.org/why_duckdb

- **Papers / classic references:**
  - Graefe 1994 Volcano, Graefe 1993 query evaluation survey, Selinger 1979 System R, Mohan 1992 ARIES, Crotty 2022 mmap, MonetDB/X100, HyPer/Neumann 2011, PAX 2001. Several were identity-confirmed but text/page claims remain `[UNVERIFIED]` or `[UNVERIFIED from text]`; see cluster briefs for exact status.

---

## 3. Why it's this way — forcing constraints

- **Pages:** The page is the smallest coherent unit over which the DBMS can combine I/O, caching, latching, and recovery. Smaller units waste metadata; larger units increase read/write amplification.
- **Slot indirection:** Variable-length tuples and deletions force in-page movement; stable tuple IDs require line-pointer indirection.
- **Page LSN:** Recovery needs to know whether an on-disk page already reflects a log record; pageLSN makes redo idempotent and WAL flushing enforceable.
- **Buffer pool:** DBMSs need query-aware eviction, pin/latch semantics, dirty tracking, and WAL-safe flush checks; OS cache alone cannot express these invariants.
- **B+ tree fanout:** Random I/O dominates CPU; internal nodes should maximize child pointers per page. Leaf links make range scans page-sequential.
- **WAL steal/no-force:** Flushing every page at commit is too slow, and forbidding dirty-page eviction is too memory-hungry. WAL enables high throughput while preserving recovery.
- **MVCC:** Read-mostly workloads cannot afford readers blocking writers; version retention shifts cost to storage, visibility checks, vacuum/purge, and old-version GC.
- **2PL/predicate locks:** Row locks alone do not cover absence/ranges; phantoms force predicate/gap locks or SSI-style dependency tracking.
- **Cost optimizer:** Physical plan choice depends on data size, selectivity, ordering, indexes, memory, and I/O cost; rules alone cannot choose correctly across skewed workloads.
- **External operators:** Blocking operators can exceed memory; production systems partition, spill, merge, and resume rather than assume everything fits.
- **Vectorization/JIT:** Once data is memory-resident, CPU dispatch, branch prediction, cache locality, and SIMD become the bottlenecks; execution format must match hardware.
- **Storage model:** Row stores optimize point updates/full-row OLTP; column/PAX layouts optimize column-subset scans and CPU cache/SIMD in OLAP.

---

## 4. Common misconceptions to preempt

- “A database page is a disk sector.” False; DB pages are structured logical units, typically several sectors.
- “The slot number is the byte offset.” False; the slot indexes a line pointer that stores the byte offset.
- “The buffer pool is just a hashmap cache.” False; it owns pins, latches, dirty state, replacement, disk scheduling, and WAL-safe flush.
- “Current BusTub uses LRU-K.” False for current master; it uses ARC, with a legacy LRU-K constant still present.
- “BusTub is pure Volcano tuple-at-a-time.” False; current `Next()` is batch-at-a-time with `BUSTUB_BATCH_SIZE = 20`.
- “Hash join always beats nested loop.” False; indexes, tiny inputs, memory pressure, and selectivity can favor NLJ/index NLJ.
- “Sort is quicksort.” False for database-scale data; production sort is external run generation + merge when memory is insufficient.
- “WAL means dirty pages flush on commit.” False; commit flushes log, not necessarily data pages.
- “Snapshot isolation is serializable.” False; SI permits write skew unless augmented with SSI/OCC validation.
- “MVCC removes locks.” False; writes, DDL, index changes, and conflict detection still need locks/latches or validation.
- “BusTub's Project 3 lock levels are current Project 4 isolation levels.” False; this is an explicit source caveat.
- “Index scans are always faster.” False; high-selectivity predicates often prefer sequential scans due to random I/O and heap fetch cost.
- “Statistics are truth.” False; they are sampled/stale approximations and can compound join cardinality errors.
- “Vectorized execution equals SIMD.” False; vectorized means batch/array processing; SIMD is one optimization it enables.
- “Compiled execution is always better.” False; JIT latency and complexity can lose on short queries.

---

## 5. Best build-your-own targets

1. **Slotted page + table heap** — implement header, slot array, tuple insert/delete/update, compaction, stable RID. Anchor: BusTub `TablePage` and PostgreSQL `ItemIdData`.
2. **Buffer pool + WAL-safe eviction** — page table, pin counts, dirty flags, ARC or simpler LRU-K, disk scheduler, and “do not flush page past persistent LSN.” Anchor: BusTub Project 1 + WAL headers.
3. **B+ tree index** — internal/leaf pages, split/merge, leaf links, point lookup, range scan; later add latch coupling. Anchor: BusTub Project 2.
4. **Iterator/batched executor** — SeqScan, Filter, Projection, NLJ, HashJoin, Aggregation, Sort, TopN. First in-memory; then add external sort and partitioned hash join.
5. **Minimal rule optimizer** — predicate pushdown, NLJ→HashJoin, Sort+Limit→TopN, SeqScan→IndexScan, column pruning. Anchor: BusTub optimizer rules.
6. **Tiny cost optimizer** — table stats, MCV/histogram selectivity, cost model, DP join enumeration with interesting orders. Anchor: PostgreSQL optimizer README/costsize/selfuncs plus Selinger caveat.
7. **WAL + crash recovery toy** — LSNs, prevLSN chain, pageLSN, checkpoints, redo idempotence, undo chain; inject crashes between log/page writes. Keep ARIES-specific CLRs `[UNVERIFIED]` until primary text is fetched.
8. **MVCC toy** — timestamp snapshots, undo chain, visibility checks, watermark GC, write-write conflict handling; compare PostgreSQL heap versions, InnoDB undo, and BusTub undo links.
9. **Vectorized expression evaluator** — DataChunk-like arrays, selection vector filter, projection without copying, simple hash aggregation over vectors.

---

## 6. Open questions / gaps

- Graefe 1994 Volcano, Graefe 1993 survey, Selinger 1979, Mohan ARIES 1992, Crotty mmap 2022, MonetDB/X100, HyPer/Neumann 2011, and PAX 2001 still need direct primary text extraction before exact quotes/page claims are allowed.
- BusTub `LogRecord::HEADER_SIZE = 20` conflicts with naive native-member summing because current `txn_id_t` is int64; treat as source-defined serialized/header-size contract unless implementation serialization is traced further.
- BusTub Project 3 lock manager and Project 4 MVCC are distinct teaching designs. `DISABLE_LOCK_MANAGER` and the missing `READ_COMMITTED`/`REPEATABLE_READ` enum values must stay prominent in any course prose.
- BusTub deadlock victim-selection rule needs `lock_manager.cpp` or CMU Project 3 spec before claiming youngest/highest txn ID.
- PostgreSQL SSI/predicate locking (`predicate.c`), deadlock source (`deadlock.c`), VACUUM freeze thresholds, and InnoDB purge internals were not fully traced.
- PostgreSQL planner internals beyond one-level selectivity—multi-join cardinality estimation, extended statistics failure modes, and optimizer benchmark papers—remain future research if 07 goes deeper.
- External sort and hybrid hash join are production mechanisms not implemented in BusTub; decide in Phase 2 whether Substrate's own DB lab adds them.
- Columnar storage/HTAP belongs partly in 07 and partly in later system-design/data-modeling sections; Phase 2 should place boundaries carefully.
- Exact performance numbers (fanout examples, cache/vector size sweet spots, random/sequential I/O ratios) are hardware/date dependent; use measured labs or source-configured defaults, not folklore constants.
