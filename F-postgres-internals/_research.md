# Appendix F · postgres-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). F is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for "how ONE production
> relational engine — PostgreSQL — actually works end to end," instantiating the transferable theory
> taught in spine **07** (DB internals), **06** (B-trees), **15/26** (WAL/replication/checkpoint),
> and appendix **L** (transactions/isolation). Spine chapters cross-link DOWN into F for the real
> mechanism. Bespoke structure: **the life of a row** through the engine, NOT four clusters and NOT a
> build progression. Math: `_recompute.py` (14/14). Factcheck: `_factcheck_phase1.md` (0 blockers).
> Network: postgresql.org HTTP **000** this wave → constants reused from 07's line-verified source
> reads + the local WAL intro; nothing new hardened.

## 1. Thesis
PostgreSQL is a **process-per-connection, MVCC, WAL-logged, cost-based** relational engine. Every
design choice traces to ONE forcing function: **random disk I/O is ~orders slower than sequential,
and a crash can strike between any two writes.** So Postgres (a) packs rows into fixed pages, (b)
indexes with high-fanout B+ trees to turn random lookups into a handful of reads, (c) logs *before*
it writes (WAL) so commit is one sequential flush and recovery is a replay, and (d) keeps multiple
row versions so readers never block writers — paying for it later with VACUUM.

## 2. The life of a row (the bespoke spine)

### Stage 1 — The page and the tuple (storage layer; 07)
- Unit of I/O = an **8 KB page** (`BLCKSZ`). A page is a slotted structure: `PageHeaderData` (24B,
  carries the **page LSN**), a forward-growing `ItemIdData` line-pointer array (4B each:
  `lp_off:15/lp_flags:2/lp_len:15`), tuples growing backward, free space between.
- A heap tuple = 23B header (`xmin`, `xmax`, `ctid`, `t_infomask`…) + null bitmap + aligned data.
- RECOMPUTED: an 8 KB page holds **~64 tuples** of 100B payload, **~7** of 1000B → row width drives
  page count → I/O amplification. The **line pointer** gives a stable RID even when tuples move on
  compaction (the slot indirection).
- **TOAST**: attributes that would push a tuple past ~¼ page (~2 KB) are compressed and/or moved
  out-of-line to a TOAST table → huge values don't bloat the main heap page.

### Stage 2 — Finding the row: the B+ tree (nbtree; 06/07)
- nbtree internal nodes store separator keys + child block numbers; leaves store key→RID and link to
  the next leaf (range scans go page-sequential). High fanout collapses random I/O.
- RECOMPUTED: ~16B index entries → **fanout ~510** → a **3-4 level** tree indexes **~1e9 rows**, so a
  point lookup is 3-4 page reads, not a billion-row scan. nbtree adds right-links + high keys for
  concurrent splits (Lehman-Yao style; mechanism cited via 07).

### Stage 3 — Choosing HOW to read it: the cost-based planner (07)
- Postgres is **cost-based** (unlike a pure rule rewriter): it builds `RelOptInfo`/`Path` candidates,
  keeps cheapest paths + usefulrderings (`PathKey`/EquivalenceClass), compares with
  `STD_FUZZ_FACTOR=1.01`, falls back to GEQO at `geqo_threshold=12` joins.
- Cost units (07-verified defaults): `seq_page_cost=1.0`, `random_page_cost=4.0`,
  `cpu_tuple_cost=0.01`.
- RECOMPUTED: the **seq-scan vs index-scan crossover** — an index scan only wins below **~0.5%
  selectivity** on a 10K-page/1M-row table, *because* `random_page_cost` is **4× seq** (one heap
  fetch per matched row). This is WHY high-selectivity predicates correctly seq-scan. Statistics
  (`pg_statistic`/`pg_stats`, MCV/histograms) are the fragile hinge feeding selectivity.

### Stage 4 — Executing it: iterator/Volcano executor (07)
- Logical plan → physical operator tree; pull-based `Next()`. Streaming operators (SeqScan,
  IndexScan, Filter, Projection) vs **blocking** ones (Sort, HashJoin build, Aggregation) that
  materialize. Production additions: hybrid hash join (power-of-two batches, spill),
  `tuplesort.c` quicksort + balanced k-way merge, optional **JIT** (LLVM) for expression eval.

### Stage 5 — Making it durable: WAL (postgres-wal-intro.txt, VERIFIED verbatim; 15/26)
- **Write-Ahead Logging**: the WAL record describing a page change must be flushed *before* the data
  page; a commit record must be durable before commit is acknowledged.
- RECOMPUTED + VERBATIM: commit flushes **only the WAL** (written **sequentially**), not the k
  random data pages dirtied — those flush later. This turns many random writes into one sequential
  flush. The page header's **LSN** records how far WAL has been applied to that page (makes REDO
  idempotent).

### Stage 6 — Bounding recovery work: checkpoints (26/WAL)
- A checkpoint flushes dirty pages and records a known-good start point so REDO needn't replay all
  history. RECOMPUTED: checkpoint spacing has a **√ knee I*=√(2Nc)** (reuse 26) — too frequent =
  I/O storms; too rare = long REDO after crash.

### Stage 7 — Surviving a crash: roll-forward / REDO (wal-intro.txt, VERIFIED)
- On restart Postgres replays WAL from the last checkpoint: **"any changes that have not been applied
  to the data pages can be redone from the WAL records … roll-forward recovery, also known as REDO"**
  (verbatim). ⇒ journaled filesystems are not required for the data files (also verbatim). Conceptual
  model = ARIES (Analysis/Redo/Undo); exact ARIES formalism `[UNVERIFIED]` (carried from 07, ACM
  blocked).

### Stage 8 — Concurrency without blocking: MVCC (07/L)
- Each row carries `xmin` (creating txn) / `xmax` (deleting/superseding txn). A snapshot
  (`xmin`,`xmax`,`xip[]`) decides per-tuple **visibility** → readers never block writers and writers
  never block readers.
- RECOMPUTED: an UPDATE writes a NEW version and leaves the OLD one **dead** until reclaimed → 1000
  updates to one row = 1000 dead tuples = **table bloat**. MVCC helps readers, NOT write-write: a
  single hot row still caps at **~1/hold_time ≈ 200 tps** (reuse L/07 contention wall).

### Stage 9 — Garbage collection: VACUUM + wraparound (07)
- **VACUUM** reclaims dead tuples; **autovacuum** runs it on thresholds. **XID wraparound**: the XID
  space is **32-bit** → RECOMPUTED horizon **2^31 ≈ 2.1B** txns before old rows would appear "in the
  future"; **VACUUM FREEZE** rewrites ancient `xmin` to FrozenXID to prevent data loss. This is the
  uniquely-Postgres operational hazard the spine should cross-link to.

## 3. The "one forcing function, many mechanisms" reconciliation (appendix payload)
| stage | mechanism | forcing function | anchor |
|---|---|---|---|
| store | 8 KB slotted page + TOAST | random I/O is coarse; rows vary in size | 07 |
| find | nbtree fanout ~510 | random I/O dominates CPU | 06/07 |
| plan | cost model, random=4×seq | physical choice depends on selectivity | 07 |
| durable | WAL, sequential log flush | crash between any two writes | wal-intro (VERIFIED) |
| recover | checkpoint + REDO roll-forward | bound replay work | wal-intro/26 |
| concurrent | MVCC xmin/xmax snapshots | readers mustn't block writers | 07/L |
| GC | VACUUM + FREEZE (32-bit XID) | versions accumulate; XID is finite | 07 |

## 4. Common misconceptions to preempt
- "Commit flushes the data pages." No — commit flushes the **WAL** (sequential); data pages flush
  later at checkpoint (verbatim wal-intro).
- "MVCC means no locks." Writes/DDL/unique checks still lock; MVCC only removes read-write blocking.
- "Index scans are always faster." Only below the selectivity crossover (~0.5% here); above it the
  seq scan wins because `random_page_cost=4×`.
- "VACUUM is optional tuning." Without it you get bloat AND eventual XID-wraparound data loss.
- "A DB page is a disk sector." No — it's an 8 KB logical slotted unit spanning many sectors.
- "Snapshot isolation = serializable." No — SI permits write skew (→ SSI / Serializable in 07/L).

## 5. Provenance summary
- **VERIFIED verbatim:** WAL roll-forward/REDO + sequential-log-flush (`postgres-wal-intro.txt`,
  local primary).
- **REUSED (line-verified in 07):** page/tuple layout, planner cost defaults, MVCC visibility,
  nbtree, executor, hybrid hash join, external sort. Spine 06/07/15/26 + appendix L.
- **RECOMPUTED:** `_recompute.py` (14/14).
- **`[UNVERIFIED]` carry-forward (not load-bearing):** MVCC heap-internals detail (HOT/`t_infomask`/
  multixact/VM/FSM), VACUUM/freeze exact thresholds, WAL record format + full-page-writes +
  replication slots, planner deep internals + JIT numbers, exact TOAST threshold, ARIES formalism —
  all blocked behind postgresql.org (HTTP 000) / ACM; logged, none hardened.

---
**Appendix F reconciled.** Reference-grade, exercise-free, 14/14 recomputed, WAL core verified
verbatim. No chapters yet.
