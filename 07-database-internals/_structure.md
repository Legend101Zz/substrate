# 07 — Database Internals · _structure.md

**Identity:** what's actually inside a relational database — built component by component
until a SQL query flows through a storage engine, executor, optimizer, and transaction
manager you understand. The first "real system" the foundations assemble into.

**Bespoke shape — "follow one row, then one query, then one transaction, up the stack."**
NOT a topic survey. The sub-course is a CONSTRUCTIVE stack built bottom-up, where each
component exists because the one below it forces a problem: page → buffer pool → index →
executor → optimizer → WAL/recovery → MVCC/isolation. Two reference points throughout:
BusTub (teaching-clean source you can read whole) and PostgreSQL/InnoDB (production reality).
Each chapter: the constraint → the clean mechanism (BusTub) → the production mechanism
(Postgres) → the misconception it kills. This is the spine; appendix F goes infinitely
deep on Postgres specifically.

## Dependency position
- **Depends on:** 04 (files, buffer cache, WAL echo xv6 fs), 06 (B+tree/LSM — the index is
  ch.3 here), 01 (pages/cache lines), light 11 (isolation previews distributed commit).
- **Feeds into:** 08 (buffer pool ↔ cache eviction), 14 (data modeling/partitioning),
  15 (replication/WAL shipping), 26 (agent resume = ARIES recovery), 30 (query exec ↔ RAG
  pipeline).
- **Appendix links DOWN:** F-postgres-internals ("life of a row" — the full Postgres
  instantiation of this exact stack), L-consensus (distributed commit/isolation), 06 (the
  structures). 07 teaches the component; F shows the production guts.

## Chapter specs (3–5 lines each)
1. **The page — the unit of everything** — durability, caching, indexing, recovery all
   attach to page-sized units. Slotted page: header + forward slot/line-pointer array +
   backward tuple bytes + free space. The slot is stable in-page identity (tuples move on
   compaction, RIDs don't). BusTub `TablePage` (clean) vs Postgres `PageHeaderData`/
   `ItemIdData` (production); pd_lsn bridges to WAL.
2. **The buffer pool — not just a cache** — DBMS-owned authority for page identity, pins,
   latches, dirty state, replacement, WAL-safe eviction. The forcing rule: a dirty page
   can't flush until WAL reached its LSN — which is WHY you can't just `mmap` and let the
   OS decide. BusTub ARC (note: legacy LRU-K constant still present — caveat).
3. **Indexes & access paths** — high fanout collapses random I/O (06 recap); internal =
   separators, leaves = key/RID + linked for range scans. The DBMS point: an index helps
   ONLY when the predicate/order can exploit physical key order. Sets up the optimizer's
   access-path choice. → 06, F.
4. **Query execution — the iterator model** — logical plan tree → physical operators.
   Volcano pull-based `Next()`; BusTub is actually batch-at-a-time (`BUSTUB_BATCH_SIZE=20`)
   — teach iterator composition with small batches, not pure one-row Volcano. Streaming
   (SeqScan/Filter/Projection) vs blocking (HashJoin/Aggregation/Sort/TopN) operators.
5. **External operators — when it doesn't fit in memory** — blocking operators can exceed
   RAM, so production must spill: external sort (run generation + k-way merge), hybrid/
   partitioned hash join (power-of-two batches). The missing production mechanism behind
   BusTub's in-memory simplifications. Postgres `tuplesort.c`/`nodeHashjoin.c`.
6. **The optimizer — choosing a plan** — rule rewrites (filter pushdown, NLJ→HashJoin,
   Sort+Limit→TopN, column pruning) vs cost-based search. Postgres: RelOptInfo/Paths,
   PathKeys/interesting orders, cost units (seq_page_cost=1.0, random=4.0…), GEQO around 12
   joins. Statistics are the fragile hinge — sampled/stale, errors compound across joins.
   Selinger/System R as historical anchor.
7. **WAL & recovery** — page writes are random/partial/crashable; log writes are sequential
   and authoritative. Two rules: log-record-before-page, commit-record-before-ack. LSN +
   prevLSN chain + pageLSN make redo idempotent. ARIES as the conceptual model
   (Analysis→Redo→Undo + CLRs). Steal/no-force is WHY. → 26 (agent resume).
8. **Transactions, MVCC & isolation** — keep multiple versions so readers don't block
   writers. Postgres heap visibility (xmin/xmax/ctid/infomask + snapshots); InnoDB
   ReadView + undo chains; BusTub timestamp MVCC + undo links. 2PL (pessimistic) vs OCC
   (validate at commit). Snapshot isolation ≠ serializable (write skew) — needs SSI.
   Don't blur BusTub Project 3 lock levels with Project 4 isolation enums.

## Paired build lab (/build → own-database)
The keystone lab of Part I. Ladder mirrors chapters: slotted page + table heap → buffer
pool + WAL-safe eviction → B+tree index (split/merge, leaf links, latch coupling) →
iterator/batched executor (SeqScan…HashJoin/Sort/TopN; then external sort + partitioned
hash join) → minimal rule optimizer → tiny cost optimizer (stats/selectivity/DP join
enumeration) → WAL + crash-recovery toy (inject crashes between log/page writes) → MVCC
toy (snapshots, undo chain, watermark GC, write-write conflict). Anchored on BusTub
Projects 1–4 + Postgres source.

## Diagrams needed
- Slotted page anatomy (header / slot array → / ← tuple bytes / free space) + RID indirection.
- Buffer pool: page table, pin/dirty/latch, WAL-safe flush gate (pageLSN ≤ flushedLSN).
- B+tree access path chosen by predicate (index scan vs seq scan crossover).
- Volcano/batched operator tree with streaming vs blocking nodes marked.
- External merge sort (runs → k-way merge); hybrid hash join partitioning.
- Optimizer: logical plan → candidate paths → cheapest path w/ interesting orders.
- WAL: LSN/prevLSN chain + pageLSN; ARIES Analysis→Redo→Undo timeline with CLRs.
- MVCC version chain + snapshot visibility; write-skew anomaly under SI.

## Sources / gaps to honor (from _research.md)
- `[UNVERIFIED]`/`[UNVERIFIED from text]`: Graefe Volcano 1994 + survey 1993, Selinger 1979,
  Mohan ARIES 1992 (CLR field names/page refs), Crotty mmap 2022, MonetDB/X100, HyPer/
  Neumann 2011, PAX 2001 — need direct primary text before exact quotes.
- Load-bearing source caveats to PRESERVE in prose: BusTub uses ARC not LRU-K (legacy
  constant remains); BusTub `Next()` is batch-at-a-time not pure Volcano; `LogRecord::
  HEADER_SIZE=20` is a serialized-contract not native struct math; `DISABLE_LOCK_MANAGER` +
  missing READ_COMMITTED/REPEATABLE_READ enums mean Project 3 ≠ Project 4; `VerifyTxn()` is
  a stub (not complete serializable).
- Scope decisions for Phase 3: whether own-DB lab adds external sort/hybrid hash join;
  columnar/HTAP boundary split between 07 and 14. Perf numbers are hardware-dependent — use
  measured labs/source defaults, not folklore.
