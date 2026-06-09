# Research Brief — Sub-course 07: Storage Engine + Query Execution Foundations
## Source cluster: CMU 15-445/645 BusTub, PostgreSQL source, cstack db_tutorial, Graefe/Selinger references
## Researcher: researcher-b68ca9 | Date: 2026-06-09

---

## 1. Key Mechanisms

### 1.1 Page Layout — the unit of I/O

**Forcing constraint:** disk reads/writes must be atomic at a page boundary. The page is the
smallest coherent unit the buffer manager transfers. Making it larger than a disk sector (512B
or 4096B) wastes bandwidth on partial reads; making it too large increases write amplification on
partial updates. 8KB is the conventional sweet spot (PostgreSQL default; BusTub uses 8192B).

**BusTub TablePage slotted format** (verified: `src/include/storage/page/table_page.h`):
```
Header: NextPageId(4B) | NumTuples(2B) | NumDeletedTuples(2B)  → 8B total
Slot array (grows forward): TupleInfo[0] | TupleInfo[1] | ...   → 24B each
                            (TupleInfo = uint16 offset + uint16 size + TupleMeta)
Free space (between slot array and tuples)
Tuple data (grows backward from page end)
```
TupleMeta (16B) = `timestamp_t ts_` (8B) + `bool is_deleted_` (1B) + padding.
TupleInfo size confirmed: `static_assert(sizeof(TupleInfo) == TUPLE_INFO_SIZE)` where
`TUPLE_INFO_SIZE = 24` (`src/include/storage/page/table_page.h`).

**PostgreSQL heap page format** (verified: `src/include/storage/bufpage.h`):
```
PageHeaderData (24B): pd_lsn(8) | pd_checksum(2) | pd_flags(2) |
                      pd_lower(2) | pd_upper(2) | pd_special(2) |
                      pd_pagesize_version(2) | pd_prune_xid(4)
Line pointer array (pd_linp[], grows forward from byte 24)
Free space (between pd_lower and pd_upper)
Tuple data (grows backward)
"Special space" at end (for index opaque data)
```
**Line pointer = ItemIdData** (4B total, `src/include/storage/itemid.h`):
```c
unsigned lp_off:15,   // offset to tuple from page start
         lp_flags:2,  // LP_UNUSED=0, LP_NORMAL=1, LP_REDIRECT(HOT)=2, LP_DEAD=3
         lp_len:15;   // byte length of tuple
```
15-bit lp_off/lp_len means max addressable page size = 32KB (2^15 = 32768). Confirmed in
`bufpage.h` comment: "limited to 2^15 because we have limited ItemIdData.lp_off and
ItemIdData.lp_len to 15 bits."

**Page header LSN and WAL rule** (`bufpage.h` comment): "A dirty buffer cannot be dumped to
disk until xlog has been flushed at least as far as the page's LSN." This is the write-ahead
logging invariant enforced at page granularity.

**SQLite page (via cstack)**: 4KB default; each B-tree node is one page. Page header stores
node_type (1B), is_root (1B), parent_pointer (4B). Data pages are never partially read — the
whole page is always read into the pager cache (`cstack/db_tutorial`, `_parts/part8.md`).

### 1.2 Tuple Layout

**BusTub tuple** (`src/include/storage/table/tuple.h`):
Fixed-size columns stored at known offsets. Variable-size columns (VARCHAR) stored at end with
a fixed-size offset slot at the known position pointing into the variable area. Format:
`| fixed-size fields or var-offset | variable-size payload |`
Serialization/deserialization via `SerializeTo` / `DeserializeFrom`.

**PostgreSQL HeapTupleHeaderData** (`src/include/access/htup_details.h`):
Fixed 23-byte prefix before the null bitmap:
```
HeapTupleFields t_heap:
  TransactionId t_xmin (4B) — inserting transaction
  TransactionId t_xmax (4B) — deleting/locking transaction
  union { CommandId t_cid; TransactionId t_xvac; } (4B)
ItemPointerData t_ctid (6B) — self or newer version TID
uint16 t_infomask2 (2B) — attribute count + MVCC flags
uint16 t_infomask  (2B) — HASNULL, HASVARWIDTH, HOT flags
uint8  t_hoff      (1B) — header size incl. null bitmap + padding
```
= 23 bytes fixed. Then `t_bits[]` null bitmap (1 bit/column), then optional OID, then
MAXALIGN-padded user data at t_hoff. `MaxHeapAttributeNumber = 1600`.

### 1.3 Buffer Pool Manager

**Forcing constraint:** databases cannot map their entire working set into virtual memory (files
may be larger than RAM; OS page eviction ignores DBMS access patterns). The BPM provides the
DBMS-controlled cache.

**BusTub BPM architecture** (`src/include/buffer/buffer_pool_manager.h`):
- Fixed array of `FrameHeader` objects; `FrameHeader` holds `data_` (page-sized vector),
  `pin_count_` (atomic), `is_dirty_`, `rwlatch_` (shared_mutex).
- API: `NewPage() -> page_id_t`, `DeletePage(page_id)`, `CheckedWritePage(page_id) ->
  WritePageGuard`, `CheckedReadPage(page_id) -> ReadPageGuard`.
- RAII guards (`ReadPageGuard`, `WritePageGuard`) auto-unpin/unlatch on destruction.
- Page table: `unordered_map<page_id_t, frame_id_t>` mapping page IDs to frame positions.
- Replacer: `ArcReplacer` implementing ARC (Adaptive Replacement Cache).

**ARC Replacer** (`src/include/buffer/arc_replacer.h`):
Four lists: MRU, MFU, MRU_GHOST, MFU_GHOST. `mru_target_size_` (p) balances recency vs.
frequency. Ghost lists track recently evicted pages to adapt `p` dynamically. AccessType
enum: Unknown, Lookup, Scan, Index — used to tune admission policy.
Constants: `LRUK_REPLACER_K = 10`, `BUFFER_POOL_SIZE = 128` (`src/include/common/config.h`).

**Disk Scheduler** (`src/include/storage/disk/disk_scheduler.h`):
Background worker thread processes `DiskRequest` objects (is_write_, data_, page_id_,
`callback_` = `std::promise<bool>`). Caller gets `std::future<bool>` and can block or
continue. `DiskManager` handles file I/O with lazy allocation (maps page_id to file offset
on first write) (`src/include/storage/disk/disk_manager.h`).

### 1.4 WAL Boundary (Write-Ahead Logging)

**Forcing constraint:** durability requires log records reach stable storage before the data
page that embodies that change. Otherwise a crash between page flush and log flush corrupts the
database with unrecoverable in-place changes.

**BusTub WAL structures** (`src/include/recovery/`):
- **LogRecord** format (`log_record.h`): HEADER = 20B (size:4, LSN:4, transID:4, prevLSN:4,
  LogType:4). LogRecordType: BEGIN, COMMIT, ABORT, INSERT, MARKDELETE, APPLYDELETE,
  ROLLBACKDELETE, UPDATE, NEWPAGE. prevLSN chains records per transaction (undo chain).
- **LogManager** (`log_manager.h`): `log_buffer_` (in-memory ring), `flush_buffer_`
  (double-buffer for concurrent flush), `next_lsn_` (atomic), `persistent_lsn_` (atomic).
  Background flush thread wakes on timeout or buffer full.
- **Invariant:** page.SetLSN() stores the LSN of the last modifying log record inside the
  page (at offset OFFSET_LSN=4 in the page header). A dirty frame may not be evicted until
  `persistent_lsn_ >= page.GetLSN()`.
- `LOG_BUFFER_SIZE = (BUFFER_POOL_SIZE + 1) * BUSTUB_PAGE_SIZE` (config.h).

### 1.5 B+ Tree Index

**Forcing constraint:** B-trees keep height O(log_B N) where B = branching factor ≈ page_size /
key_size. A 4-byte key in an 8KB page gives B ≈ 1000, so 3 levels covers a billion rows.
All record access goes through the buffer pool — the tree is page-resident.

**BusTub B+ tree structures** (verified: `src/include/storage/page/`):
- **BPlusTreePage** (base, 12B header): PageType(4) | CurrentSize(4) | MaxSize(4).
- **BPlusTreeInternalPage** (header 12B):
  ```
  KEY(1=INVALID) | KEY(2) | ... | KEY(n)      — n keys
  PAGE_ID(1) | PAGE_ID(2) | ... | PAGE_ID(n)  — n child pointers
  ```
  K(i) <= search_key < K(i+1) routes to PAGE_ID(i). First key is always invalid.
  `INTERNAL_PAGE_SLOT_CNT = (8192-12) / (sizeof(KeyType)+sizeof(page_id_t))`.
- **BPlusTreeLeafPage** (header 16B = 12 base + NextPageId):
  Sorted KEY[], RID[] pairs. Tombstone buffer for lazy deletion.
  `LEAF_PAGE_SLOT_CNT = (8192-16-sizeof(size_t)-tombs*sizeof(size_t)) / (sizeof(KeyType)+sizeof(ValueType))`.
  Linked list of leaf pages (NextPageId) supports range scan.
- **Concurrency**: `Context` holds `write_set_` (deque of WritePageGuard) for latch coupling
  (crabbing): acquire child before releasing parent on descent.

**cstack SQLite-model B-tree** (`_parts/part7.md`, `_parts/part8.md`):
B-tree (internal nodes store values) for indexes; B+ tree for tables. Node = one page. Split
at overflow: median key bubbles to parent; root split creates new root level.

### 1.6 Volcano / Iterator Model

**Forcing constraint:** query plans are trees of relational operators. Each operator must be able
to feed tuples to its parent without requiring the parent to know the operator's internals. The
iterator interface decouples operators: each calls `Next()` on children as needed.

**BusTub AbstractExecutor** (`src/include/execution/executors/abstract_executor.h`, comment):
> "The AbstractExecutor implements the Volcano tuple-at-a-time iterator model."

Interface:
```cpp
virtual void Init() = 0;
virtual bool Next(vector<Tuple>* batch, vector<RID>* rids, size_t batch_size) = 0;
virtual const Schema& GetOutputSchema() const = 0;
```
Note: BusTub evolved to **batch-at-a-time** — `Next()` fills a batch of `batch_size` tuples
rather than one. `BUSTUB_BATCH_SIZE = 20` (config.h). Still structurally Volcano (iterator
composition), but vectorized in a minor way.

**Plan node tree mirrors executor tree** (`abstract_plan.h`):
`AbstractPlanNode` children = executor children. `ExecutorFactory::CreateExecutor` recursively
instantiates executors matching each PlanType: SeqScan, IndexScan, Insert, Update, Delete,
Aggregation, Limit, NestedLoopJoin, NestedIndexJoin, HashJoin, Filter, Values, Projection,
Sort, TopN, TopNPerGroup, Window.

**Volcano paper reference** (Graefe 1994):  
G. Graefe, "Volcano — An Extensible and Parallel Query Evaluation System," IEEE TKDE 6(1):
120–135, 1994. [UNVERIFIED: exact page numbers — doi 10.1109/69.273032 not directly fetched
due to domain restrictions; paper identity confirmed from BusTub source comment.]

### 1.7 Operators: Scans, Joins, Sort, Aggregation

**Sequential scan** (`seq_scan_executor.h`): Iterates TableHeap page by page, yielding
non-deleted tuples. Filter predicate pushed down via `filter_predicate_` in plan node
(`seq_scan_plan.h`). O(n) full page traversal.

**Index scan** (`index_scan_executor.h`): Uses B+ tree iterator starting from point lookup or
range; follows leaf next-page chain. Returned RIDs then fetch tuples from TableHeap.

**Nested loop join**: Two child executors; outer loops, for each outer tuple re-init inner and
loop all inner tuples. O(n×m). Optimizer rule `OptimizeNLJAsHashJoin` or
`OptimizeNLJAsIndexJoin` rewrites to cheaper variant if possible.

**Hash join** (`hash_join_executor.h`): Build phase — fully materialize left child into a hash
table keyed by join attributes. Probe phase — for each right-child tuple, look up the hash
table. Expected O(n+m). BusTub uses in-memory hash table (no grace hash / partitioning).

**Sort** (`sort_executor.h`): Materializes all input tuples from child, sorts in-memory.
BusTub does not implement external sort. Rule `OptimizeSortLimitAsTopN` converts
Sort+Limit to TopN executor using a priority queue (heap of size k).

**Aggregation** (`aggregation_executor.h`): `SimpleAggregationHashTable` keyed by GROUP BY
expressions. Supported aggregates: CountStar (init 0), Count/Sum/Min/Max (init NULL).
`CombineAggregateValues` merges incoming rows. Single-pass hash aggregate; no partial
aggregation / spill-to-disk in the default BusTub implementation.

**TopN** (`topn_executor.h`): Maintains a bounded priority queue of size k. When child is
exhausted, emits the top-k in order. O(n log k).

### 1.8 Optimizer Cost Basics

**BusTub optimizer** (`optimizer.h`) is **rule-based**, not cost-based. Rules applied:
1. `OptimizeMergeProjection`: eliminate redundant projections.
2. `OptimizeMergeFilterNLJ`: push predicates into NLJ.
3. `OptimizeNLJAsHashJoin`: convert NLJ with equality predicate to HashJoin.
4. `OptimizeNLJAsIndexJoin`: convert NLJ to index join when inner has a matching B+ tree index.
5. `OptimizeEliminateTrueFilter`: remove trivially-true filters.
6. `OptimizeMergeFilterScan`: push filter into SeqScan as inline predicate.
7. `OptimizeOrderByAsIndexScan`: replace Sort+SeqScan with IndexScan when sorted column is indexed.
8. `OptimizeSeqScanAsIndexScan`: replace SeqScan with point-lookup IndexScan for equality predicates.
9. `OptimizeSortLimitAsTopN`: Sort+Limit → TopN.
10. `OptimizeColumnPruning`: eliminate unused column evaluations.

`EstimatedCardinality(table_name)` looks up pre-computed statistics from the catalog. No
dynamic programming join reorder (Selinger 1979) is implemented in the default starter.

**Selinger 1979 (System R)** origin of cost-based optimization: [UNVERIFIED for direct
access; widely cited] Access Path Selection in a Relational Database Management System,
Selinger et al., SIGMOD 1979. Introduced left-deep plan enumeration, cost = weighted I/O +
CPU, selectivity estimation from column statistics.

**Graefe 1993 survey** for comprehensive operator catalog: "Query Evaluation Techniques for
Large Databases," ACM Computing Surveys 25(2):73–170, 1993. [UNVERIFIED for exact page
range — domain blocked; identity well-established.]

### 1.9 MVCC in BusTub

BusTub Project 4 implements MVCC with in-memory undo chains
(`src/include/concurrency/transaction.h`):
- **UndoLink**: `{prev_txn_, prev_log_idx_}` — pointer to the previous version of the tuple.
- **UndoLog**: `{is_deleted_, modified_fields_[], tuple_, ts_}` — delta of changed columns.
- **TupleMeta.ts_**: visible timestamp (commit timestamp or in-flight txn_id).
- **Isolation levels**: READ_UNCOMMITTED, SNAPSHOT_ISOLATION, SERIALIZABLE.
- **TransactionState**: RUNNING → TAINTED → COMMITTED or ABORTED.

---

## 2. Foundational Sources

| Claim | Source | Verified? |
|-------|--------|-----------|
| BusTub page size = 8192B, BPM size = 128 frames | `github.com/cmu-db/bustub/blob/master/src/include/common/config.h` | YES |
| TablePage slotted layout, TupleInfo=24B | `github.com/cmu-db/bustub/blob/master/src/include/storage/page/table_page.h` | YES |
| TupleMeta = 16B (ts_ + is_deleted_) | `github.com/cmu-db/bustub/blob/master/src/include/storage/table/tuple.h` | YES |
| BPM API: CheckedReadPage/CheckedWritePage, FrameHeader | `github.com/cmu-db/bustub/blob/master/src/include/buffer/buffer_pool_manager.h` | YES |
| ARC replacer: MRU/MFU/ghost lists, LRUK_REPLACER_K=10 | `github.com/cmu-db/bustub/blob/master/src/include/buffer/arc_replacer.h` | YES |
| DiskScheduler: background thread, promise/future | `github.com/cmu-db/bustub/blob/master/src/include/storage/disk/disk_scheduler.h` | YES |
| B+ tree internal header 12B, leaf header 16B | `github.com/cmu-db/bustub/blob/master/src/include/storage/page/b_plus_tree_internal_page.h` | YES |
| WAL HEADER=20B, LogRecordType enum, prevLSN chain | `github.com/cmu-db/bustub/blob/master/src/include/recovery/log_record.h` | YES |
| LogManager: log_buffer_, persistent_lsn_, flush thread | `github.com/cmu-db/bustub/blob/master/src/include/recovery/log_manager.h` | YES |
| AbstractExecutor = Volcano tuple-at-a-time model; BATCH_SIZE=20 | `github.com/cmu-db/bustub/blob/master/src/include/execution/executors/abstract_executor.h` + config.h | YES |
| Optimizer rules list (rule-based, not cost-based) | `github.com/cmu-db/bustub/blob/master/src/include/optimizer/optimizer.h` | YES |
| PlanType enum (SeqScan..Window) | `github.com/cmu-db/bustub/blob/master/src/include/execution/plans/abstract_plan.h` | YES |
| MVCC: UndoLink, UndoLog, IsolationLevel enum | `github.com/cmu-db/bustub/blob/master/src/include/concurrency/transaction.h` | YES |
| PostgreSQL PageHeaderData: pd_lsn..pd_prune_xid | `github.com/postgres/postgres/blob/master/src/include/storage/bufpage.h` | YES |
| ItemIdData 4B, lp_off:15, lp_flags:2, lp_len:15 | `github.com/postgres/postgres/blob/master/src/include/storage/itemid.h` | YES |
| PostgreSQL max page size = 32KB (15-bit offset limit) | `github.com/postgres/postgres/blob/master/src/include/storage/bufpage.h` | YES |
| HeapTupleHeaderData: xmin/xmax/cid/ctid/infomask; 23B fixed | `github.com/postgres/postgres/blob/master/src/include/access/htup_details.h` | YES |
| WAL rule "dirty page can't flush until xlog flushed to page LSN" | `github.com/postgres/postgres/blob/master/src/include/storage/bufpage.h` comment | YES |
| SQLite arch: tokenizer→parser→codegen→VM→B-tree→pager→OS | `github.com/cstack/db_tutorial/blob/master/_parts/part1.md` | YES |
| SQLite/cstack B-tree node = one page, pager = buffer pool | `github.com/cstack/db_tutorial/blob/master/_parts/part8.md` | YES |
| Graefe 1994 Volcano paper (IEEE TKDE 6(1)) | IEEE doi:10.1109/69.273032 | UNVERIFIED (blocked) |
| Graefe 1993 survey (ACM Surveys 25(2)) | ACM doi:10.1145/152610.152611 | UNVERIFIED (blocked) |
| Selinger 1979 System R access path selection | SIGMOD 1979, ACM | UNVERIFIED (paywalled) |

---

## 3. Why It's This Way — Forcing Constraints

**Slotted page with indirection array:**  
Tuples can vary in size and be deleted/updated. The slot array (line pointers) lets tuples be
physically rearranged during VACUUM/page compaction without invalidating external references
(which use slot number, not byte offset). The indirection layer is the minimum overhead to
support stable TIDs while allowing in-page reorganization.

**WAL before data:**  
Once a dirty page flushes without a corresponding log record, a crash leaves an irrecoverable
on-disk state. Log records are small, sequential writes (cheap on HDD/NVMe); data page writes
are random (expensive). WAL amortizes durability cost onto log writes; data writes can be
batched (group commit). Without this ordering, ARIES/REDO cannot reconstruct lost changes.

**Buffer pool instead of mmap:**  
`mmap` delegates eviction to the OS, which ignores DBMS access patterns (e.g., sequential
scan should evict MRU, not LRU). The DBMS BPM enables: (a) DBMS-controlled eviction for
query-aware policies; (b) dirty-page tracking tied to WAL LSN; (c) page latching (OS doesn't
provide record-level latch integration). This tradeoff is discussed in "Are You Sure You Want
to Use MMAP in Your Database Management System?" (Crotty et al., CIDR 2022) [UNVERIFIED
for exact citation — paper identity well-established].

**B+ tree, not B-tree, for tables:**  
Internal nodes store only keys (routing), not values — more keys per page = shallower tree =
fewer I/Os per lookup. Leaf chaining enables range scans without traversing back to parent.
B (not B+) tree stores values in internal nodes: fewer routing keys per page = deeper tree.
SQLite uses B-tree for indexes (value at internal node OK for small datasets), B+ tree for
table rows (cstack `_parts/part7.md`).

**Volcano iterator model:**  
Enables composable operator trees with O(1) additional memory per operator (except blocking
operators like sort/hash-agg). Pull-based: parent controls pacing; downstream operators
produce only what's consumed. Downside: function-call overhead per tuple; modern DBMS replace
with vectorized (vector-at-a-time, e.g., DuckDB) or compiled (LLVM JIT, e.g., HyPer/Umbra)
execution models. Volcano is the teachable baseline.

**In-memory hash aggregate, no spill:**  
Spill-to-disk (grace hash, partitioned sort-merge) requires external sort / partitioned I/O —
significant complexity. BusTub is an educational system; in-memory with bounded GROUP BY
cardinality is sufficient for the course. Production DBMS (PostgreSQL, DuckDB, Spark SQL)
implement two-phase hash aggregation with spill.

**Rule-based optimizer over cost-based:**  
Cost-based requires cardinality estimation, histogram statistics, join order enumeration (DP
or greedy). Rule-based is deterministic and easier to reason about for teaching. BusTub's
rules cover the most impactful rewrites (filter pushdown, NLJ→HashJoin, index election) while
keeping the optimizer code readable as a teaching artifact.

---

## 4. Common Misconceptions to Preempt

1. **"Pages are just raw disk sectors."** No — pages have internal structure (header, slot
   array, free space pointer). A disk sector may be 512B or 4096B; a database page is 4–16KB
   and is always transferred whole to/from disk.

2. **"The buffer pool is just a cache."** The BPM does more: it tracks dirty/pin state, enforces
   WAL ordering (no flush without log durability), manages page latches, and assigns stable page
   IDs independent of physical file layout.

3. **"B-tree and B+ tree are the same thing."** B-tree stores values in internal nodes;
   B+ tree stores values only in leaf nodes. Most database indexes are B+ trees; calling them
   "B-trees" colloquially is common but imprecise.

4. **"Volcano always processes one tuple at a time."** Classic Volcano (Graefe 1994) does.
   BusTub's current `Next()` fills a batch (`BUSTUB_BATCH_SIZE=20`), making it vectorized
   Volcano. DuckDB and MonetDB go further with full column-at-a-time / vectorized execution.

5. **"Hash join always beats nested loop join."** Hash join requires the build table to fit in
   memory; on tiny tables NLJ may be cheaper (no hash build cost). Index NLJ beats hash join
   for low-selectivity probes. The optimizer must choose.

6. **"Sort is just QuickSort."** Database sort is external sort (multiple passes + merge) for
   large data. BusTub's sort is in-memory only — a simplification for teaching. PostgreSQL uses
   replacement selection + polyphase merge for large sorts.

7. **"WAL only exists for crash recovery."** WAL also enables: point-in-time recovery (archive
   logs), replication (streaming WAL to replicas), logical replication (interpret log records).

8. **"VACUUM deletes tuples."** VACUUM reclaims space from dead tuple versions left by MVCC
   updates. PostgreSQL MVCC marks deleted tuples with `t_xmax`; the actual space reclaim is
   deferred to VACUUM. "DELETE" does not free space immediately.

9. **"Index scans are always faster than sequential scans."** For high-selectivity predicates
   retrieving many rows, sequential scan (prefetch entire table) beats index scan (random I/O
   per row, each needing a buffer pool fetch). PostgreSQL's optimizer chooses based on estimated
   selectivity vs. estimated random vs. sequential I/O ratio.

10. **"The slot number IS the tuple's position in the page."** The slot number (ItemPointerData
    slot offset) indexes into the line-pointer array; the actual byte offset is stored in
    ItemIdData.lp_off. This indirection is what allows in-page defragmentation.

---

## 5. Best Build-Your-Own Targets

### 5.1 BusTub (CMU 15-445) — Gold Standard Lab
**Repo:** `https://github.com/cmu-db/bustub`  
**Structure:** 4 progressively dependent projects:
- **Project 0** (C++ primer): trie structure, warm-up.
- **Project 1** (Storage): Implement `ArcReplacer` (eviction policy) + `DiskScheduler`
  (async I/O) + `BufferPoolManager` (frame management, page table, pinning).
- **Project 2** (B+ Tree Index): Implement `BPlusTree::Insert`, `Remove`, `GetValue`;
  concurrent safe via latch couplings in `Context.write_set_`.
- **Project 3** (Query Execution): Implement executors for SeqScan, Insert, Delete, Update,
  IndexScan, NLJ, HashJoin, Aggregation, Sort, TopN.
- **Project 4** (Concurrency/MVCC): Implement MVCC with undo log chain, timestamp ordering,
  snapshot isolation and serializable isolation with detection/abort.

**Build target quality:** Each project builds on the previous. The autograder is publicly
available on Gradescope after CMU deadlines. This is the canonical "build your own DBMS" lab
for serious learners.

### 5.2 cstack/db_tutorial — Beginner SQLite-model
**Repo:** `https://github.com/cstack/db_tutorial`  
**Tech:** C, ~13 incremental parts.  
**Shape:** REPL → row layout → in-memory pages → B-tree leaf nodes → B-tree splits → internal
nodes → cursor abstraction → pager (persistence + fsync) → binary search.  
**Strength:** Each part is tiny (100–200 lines of diff). Good for understanding raw page/pager
mechanics from zero without a large codebase.  
**Weakness:** Stops before implementing WAL, transactions, or query execution. Good for
storage layer only.

### 5.3 SimpleDB (CS186/6.830) — Query Execution Focus
**Course:** MIT 6.5830 / CS186 Berkeley (older).  
**Language:** Java.  
**Scope:** Covers HeapFile/HeapPage, buffer pool, B+ tree, iterator-model operators (SeqScan,
Filter, Join, Aggregate), and basic transaction/lock management.  
**Caveat:** Source varies by semester; check current availability [UNVERIFIED for current URL].

### 5.4 Recommended Minimal Build-Your-Own Sequence
For Substrate: use BusTub Projects 1–3 as the reference lab shape. Order:
1. Page layout + slotted page (implement from spec)
2. Buffer pool + LRU-K replacer (Project 1 style)
3. B+ tree index (Project 2 style)
4. Volcano executors: SeqScan, Filter, HashJoin, Aggregation, Sort (Project 3 style)
5. Optional: MVCC + undo log (Project 4 style)

---

## 6. Open Questions / Where Sources Disagree

1. **Vectorized vs. Compiled execution boundaries for teaching:** BusTub uses batched Volcano
   (minor vectorization). Whether to teach pure Volcano first then show DuckDB-style vectorized
   is an open pedagogical question. Graefe 1994 = Volcano; DuckDB (Raasveldt & Muhleisen 2019)
   = vectorized. When does the course introduce compiled/JIT execution models?

2. **External sort omission in BusTub:** BusTub Project 3 sort is in-memory only. A student
   building a "production-like" DB would need external sort. The course notes reference it but
   don't implement it. Should the Substrate lab include a two-pass external sort exercise?

3. **ARC vs. LRU-K for replacement policy:** Historical BusTub used LRU-K; current master
   (`arc_replacer.h`) uses ARC. The config constant `LRUK_REPLACER_K=10` appears to be a
   legacy constant from when LRU-K was used. ARC is superior for mixed workloads (recency +
   frequency), but LRU-K is simpler to teach. The course slides may lag the codebase.

4. **Cost-based optimizer not implemented in BusTub:** Selinger 1979 DP join ordering is
   described in lectures but BusTub uses rule-based only. Should the Substrate course include a
   minimal cardinality-estimator + join-order-DP exercise? No consensus in sources.

5. **Postgres page checksums optional:** `bufpage.h` notes "if a checksum is not in use then we
   leave the field unset" — checksums are off by default in many deployments, creating a class
   of silent data corruption risks. SQLite always checksums (WAL mode). Tradeoff worth flagging.

6. **MVCC visibility rules vary by isolation level:** BusTub's UndoLog chain differs from
   PostgreSQL's heap-tuple xmin/xmax approach. Postgres keeps all versions in the heap; BusTub
   keeps current version in heap and deltas in per-transaction undo log. Different tradeoff:
   Postgres's approach is simpler for point-in-time reads; BusTub's approach is closer to InnoDB/
   MySQL style. Which model to teach as "canonical" is not settled in the references.

7. **Graefe 1993 survey depth:** The 98-page ACM Computing Surveys paper covers far more than
   Volcano: sort-merge join, hybrid hash join, Gamma/Grace, parallel query evaluation, inter-
   operator parallelism. Cannot directly verify page ranges; treat as foundational reference but
   do not cite specific page numbers until verified.

---

## Gaps Not Covered in This Brief

- PostgreSQL planner internals (pg_stats, row estimation, cost_cpu/cost_io parameters) — would
  need `src/backend/optimizer/` source.
- External sort algorithm (replacement selection, polyphase merge) — not in BusTub source.
- Grace hash join / partitioned hash join — not in BusTub.
- Write-ahead logging: ARIES (Mohan et al. 1992) for full recovery protocol beyond BusTub's
  simpler log manager.
- Query compilation / LLVM JIT (HyPer, Umbra) — outside scope of this cluster.
- Column stores (DSM vs. NSM) — outside scope of this cluster.
