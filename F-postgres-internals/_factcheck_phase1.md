# Appendix F · Phase-1 factcheck — postgres-internals

> Method (spine discipline): every load-bearing claim is (a) RECOMPUTED in `_recompute.py` (14/14) or
> (b) VERIFIED verbatim against a local primary. F is a **reference appendix** (no exercises). **0
> blockers.** Network: postgresql.org HTTP **000** this wave (still blocked) → NO new pg.org fetch;
> all PostgreSQL constants reused from **07** (which cited postgres master source verbatim) + the
> WAL intro fetched 2026-06-10. Anything not line-verified in 07/WAL-intro is flagged `[UNVERIFIED]`.

## Bespoke structure note
F is a **"life of a row" pipeline** (page byte → tuple → index → planner/executor → WAL → checkpoint
→ crash recovery → MVCC/VACUUM → wraparound), NOT the 13-20 four-cluster shape and NOT a build
progression. Reference-grade, deep on ONE engine (PostgreSQL).

## Primaries verified verbatim
- **WAL intro** (`meta/fetched_primaries/postgres-wal-intro.txt`, fetched 2026-06-10 from
  postgresql.org/docs/current/wal-intro.html): "changes to data files … must be written only after
  those changes have been logged"; "we will be able to recover the database using the log: any
  changes that have not been applied to the data pages can be **redone** from the WAL records. (This
  is **roll-forward recovery, also known as REDO**.)"; "only the WAL file needs to be flushed to disk
  to guarantee that a transaction is committed"; "The WAL file is written **sequentially**." — all
  VERBATIM. ⇒ commit forces the log not the data pages; recovery = REDO.
- **07 `_research.md` (line-verified PostgreSQL master source)** — reused, not re-fetched:
  - `PageHeaderData` 24B, `ItemIdData` 4B (`lp_off:15/lp_flags:2/lp_len:15`), heap tuple header 23B,
    8 KB default page — used in tuple-density recompute.
  - MVCC visibility via `xmin`/`xmax`/`ctid`/infomask + snapshot (`xmin`,`xmax`,`xip[]`).
  - Planner cost defaults: `seq_page_cost=1.0`, `random_page_cost=4.0`, `cpu_tuple_cost=0.01`,
    `STD_FUZZ_FACTOR=1.01`, GEQO at `geqo_threshold=12` — used in seq-vs-index crossover recompute.
  - nbtree right-links/high-keys, hybrid hash join (power-of-two batches), `tuplesort.c`
    quicksort/k-way merge — reused as mechanism anchors.

## Recomputed claims (`_recompute.py`, 14/14)
- Page density: 8 KB page → 64 tuples/100B (and 7/1000B) — I/O amplification. PASS×2.
- nbtree fanout ~510 (16B entries) → 3-4 levels index 1e9 rows. PASS×2.
- WAL: 1 sequential log flush replaces k random page flushes; recovery=REDO. PASS×2.
- Checkpoint sqrt knee I*=√(2Nc) (reuse 26). PASS.
- MVCC: 1 dead version/update → bloat → autovacuum; visibility rule. PASS×2.
- 32-bit XID wraparound horizon 2^31 → VACUUM FREEZE. PASS.
- Planner: index loses above ~0.5% selectivity; `random_page_cost=4×seq` drives it. PASS×2.
- Hot-row wall ~1/hold_time = 200 tps (reuse L/07). PASS.
- TOAST at ~1/4 page (2 KB). PASS.

## Reused (line-verified spine + local primaries)
07 (page/tuple/buffer pool/WAL/LSN/MVCC/2PL/planner/executor — the home course), 06 (B+ tree
fanout/access paths), 15 + 26 (WAL/checkpoint/replication), L (isolation/2PL contention wall, quorum
replication for streaming/HA). WAL intro local primary.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- **MVCC heap-internals detail** (HOT updates, `t_infomask` bit semantics, `pg_multixact`,
  `VM`/visibility-map, FSM) — beyond what 07 line-verified; postgresql.org blocked (000).
- **VACUUM/autovacuum thresholds** (`autovacuum_vacuum_scale_factor`, freeze ages
  `vacuum_freeze_min_age`/`autovacuum_freeze_max_age`) — illustrative; not fetched verbatim.
- **WAL record format detail** (`XLogRecord` rmgr dispatch, full-page-writes/torn-page protection,
  `wal_level`, streaming/logical replication slots) — conceptual; pg.org blocked.
- **Planner deep internals** (`RelOptInfo`/`Path`/`PathKey`/EquivalenceClass, MCV/histogram
  selectivity, extended statistics, JIT via LLVM) — cited from 07 as mechanism, exact numbers not
  re-derived here.
- **TOAST exact threshold** (`TOAST_TUPLE_THRESHOLD` ≈ 2 KB) modeled as PAGE/4, not quoted verbatim.
- ARIES (Mohan 1992) CLR/page-LSN formalism — `[UNVERIFIED]` carried from 07 (ACM blocked).
All logged, none load-bearing (numbers are recomputed or come from 07's line-verified source reads).

## Verdict
F is honest and appendix-appropriate: the durability core (WAL roll-forward/REDO, sequential log
flush) is VERIFIED verbatim against the local WAL intro; page/tuple/planner constants come from 07's
line-verified PostgreSQL source reads and every derived number is recomputed (14/14). Reconcile into
`_research.md`. **0 blockers.**
