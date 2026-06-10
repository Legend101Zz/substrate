# Session log

Append-only, reverse-chronological. Each entry: shipped / decisions / stopped-at.

## 2026-06-10 — Phase 1 Wave 3: reconcile/factcheck 08; start 09 starter cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean;
  no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv` was not modified.
- shipped: deepened 08 Redis claims from primary sources: `server.h`, `evict.c`, `expire.c`, Redis eviction
  docs, and Redis persistence docs. Verified approximate sampled eviction, active expiry constants/effort,
  and RDB/AOF/fsync/rewrite/multi-part AOF details.
- shipped: extracted Facebook Memcached NSDI 2013 PDF using a throwaway `/tmp` `uv run --with pypdf`
  environment; verified leases, stale values, pools, Gutter, regional pools, and 17K/s→1.3K/s lease experiment.
- shipped: added two 08 cluster briefs: `_research_memcached-internals.md` and
  `_research_admission-dogpile-consistency.md`; covered slabs, segmented LRU, crawler, slab automove,
  extstore, threading, CAS/stale flags, TinyLFU/W-TinyLFU/ARC, Go singleflight, RFC 5861, and RFC 9111.
- shipped: attempted `factchecker` subagent on 08; it failed with `httpx.ReadTimeout`. Manual primary-source
  fallback produced `08-caches-and-storage-systems/_factcheck_phase1.md`; no blockers remain, warnings logged.
- shipped: reconciled all 08 briefs into `08-caches-and-storage-systems/_research.md` with the standard six
  sections; expanded `meta/RESEARCH_INDEX.md` with new verified 08 sources and residual gaps.
- shipped: started 09 with one starter brief: `09-message-queues-logs-and-kafka/_research_log-abstraction-kafka-storage.md`
  covering Kafka log abstraction, partitions, offsets, segments, retention, and compaction from the Kafka paper
  and Apache Kafka source. 09 is not factchecked or reconciled.
- decisions: no ADR. Operational note: subagent read-timeout was treated like prior network stream failures;
  no Code Puppy reinstall or venv edit attempted.
- stopped-at: Phase 1 Wave 3 with 08 reconciled/factchecked; 09 has exactly one starter cluster and needs
  factcheck + deeper clusters for replication/ISR/high watermark, consumer groups/offset commits, delivery
  semantics/idempotence/transactions, and then reconciliation. No chapters. No Phase 2.

## 2026-06-09 — Phase 1 Wave 3: finish/reconcile sub-course 07; start 08 starter cluster
- shipped: recovered from the prior callback crash safely from `/Users/m0t0hu6/Desktop/substrate`
  (physical repo path resolves through OneDrive) with clean working tree and no `cwd` PermissionError.
- shipped: validated the load-bearing 07 storage/query-exec claims against BusTub/PostgreSQL sources:
  BusTub page/config constants, `TablePage`, `TupleInfo`, `TupleMeta`, B+ tree headers,
  `AbstractExecutor` batching, ARC vs legacy LRU-K, PostgreSQL page/line-pointer/heap tuple headers.
- shipped: patched the BusTub WAL wording: `LogRecord::HEADER_SIZE=20` is the source-defined
  header/serialized-size contract, not native C++ member-size math, because current `txn_id_t=int64_t`.
- shipped: wrote `07-database-internals/_research_transactions-recovery.md` and
  `07-database-internals/_research_optimizer-external-exec.md`; ran `factchecker` and saved
  `07-database-internals/_factcheck_phase1.md`; patched all three factcheck blockers:
  BusTub Project 3 2PL vs Project 4 MVCC split, `DISABLE_LOCK_MANAGER`, and unsupported deadlock
  victim-selection claim.
- shipped: reconciled all 07 cluster briefs into `07-database-internals/_research.md` using the
  standard six sections; expanded `meta/RESEARCH_INDEX.md` with genuinely new 07 sources.
- shipped: started 08 with `08-caches-and-storage-systems/_research_cache-eviction-consistency.md`
  after the researcher subagent failed with an `httpx.ReadError`; manual fallback used Redis/Memcached
  source/docs and left Facebook Memcached paper-body claims `[UNVERIFIED from text]`.
- decisions: no ADR. Operational note only: subagent `httpx.ReadError` did not touch the Code Puppy venv;
  no reinstall attempted. 08 remains only partially started and not reconciled.
- stopped-at: Phase 1 Wave 3 with 07 reconciled/factchecked and 08 one-cluster started. Next session should
  factcheck/deepen 08 (Redis eviction source, Memcached paper extraction, TinyLFU/ARC/admission, write paths),
  reconcile 08, then start 09. No chapters. No Phase 2.

## 2026-06-09 — Recovery checkpoint after code-puppy cwd-permission crash; Wave 3 sub-course 07 cluster 1
- shipped: recovered the repo state after a Code Puppy callback crash triggered immediately after
  `curl -s --max-time 15 https://raw.githubusercontent.com/sqlite/sqlite/master/src/pager.c | sed -n 1,120p`.
  The crash was in Code Puppy prompt callbacks calling `os.getcwd()` / `Path.cwd()`
  (`PermissionError: [Errno 1] Operation not permitted`), not in course content.
- shipped: confirmed latest committed work `4a1cc71` = Phase 1 Wave 2 research and factcheck fixes:
  - Wave 1 factcheck report: `meta/factcheck_wave1_01-03.md`; applied fixes to 02/03 briefs and left
    source gaps logged for Eater/Scott/Petzold, QUIC adoption/CPU, and Sponge Lab 4.
  - Wave 2 briefs for 04/05/06 are reconciled in `_research.md` files; factcheck report
    `meta/factcheck_wave2_04-06.md` exists and blockers were patched.
- shipped: pre-checkpoint Wave 3 artifact identified and committed:
  `07-database-internals/_research_storage-query-exec.md` (463 lines). It covers slotted pages,
  tuple layout, buffer pool/ARC, disk scheduler, WAL, B+ tree pages, Volcano/batched executors,
  core operators, rule optimizer, and BusTub MVCC. Verified facts include BusTub 8192B pages,
  TablePage/TupleInfo sizes, Postgres 24B page header, 4B ItemIdData, 23B HeapTupleHeaderData,
  WAL LogRecord 20B header, and BusTub `BUSTUB_BATCH_SIZE=20`.
- shipped: updated `meta/PROGRESS.md` to reflect reality: 01–06 have briefs + factcheck reports;
  07 is in progress with one cluster drafted; 08/09 are queued, not actually started. Updated
  `meta/NEXT_SESSION.md` with a resume prompt and Code Puppy cwd-permission workaround.
- decisions: no ADR; this is an operational recovery/checkpoint. Do not touch the Code Puppy install
  directory (`~/.code-puppy-venv`). If the permission error recurs, launch from
  `/Users/m0t0hu6/Desktop/substrate` or grant the terminal/Code Puppy process Desktop/OneDrive access;
  the repo itself is readable and writable.
- stopped-at: before validating the 07 database brief or creating `07-database-internals/_research.md`.
  Next session should first spot-check/factcheck the 07 cluster, then finish remaining 07 clusters,
  reconcile 07, and only then proceed to 08/09. No chapters. No Phase 2.

## 2026-06-09 — Phase 1 Wave 2: sub-course 06 (data-structures-for-systems), source cluster 1
- shipped: `06-data-structures-for-systems/_research_indexes-lsm-bloom.md` (382 lines). Source cluster: B-trees/B+-trees + LSM-trees + Bloom filters. Primary sources: sqlite/sqlite btreeInt.h (cell layout, page header, overflow, intKey vs BLOBKEY), postgres/postgres nbtree/README (Lehman & Yao, suffix truncation, deduplication, L&Y extensions), google/leveldb doc/impl.md (write path, level sizes, compaction timing), google/leveldb doc/table_format.md (SST format, magic bytes, filter block), google/leveldb util/bloom.cc (k=bpk*0.69, double-hashing), facebook/rocksdb options.h (write_buffer_size=64MB, trigger=4, level_base=256MB), facebook/rocksdb dbformat.h (56-bit seq + 8-bit type internal key), facebook/rocksdb util/bloom_impl.h (FPR formula, cache-local Bloom, 3 implementations, AVX2), EighteenZi/rocksdb_wiki Tuning Guide (WA~34x, RA, SA), EighteenZi/rocksdb_wiki Leveled-Compaction.md (scoring, parallel sub-compaction). O'Neil LSM PDF fetched (www.cs.umb.edu/~poneil/lsmtree.pdf, HTTP 200) but not extractable without pdftotext — mechanisms verified from LevelDB implementation instead.
- decisions: none (research-only session, no ADRs).
- stopped-at: sub-course 06 source cluster 1 complete. Remaining for wave 2: sub-courses 04/05 ongoing (2 clusters each previously written; need reconcile briefs into _research.md). Sub-course 06 may need additional clusters (e.g., skip lists, hash tables, count-min sketch). Check RESEARCH_INDEX for planned clusters.
- unverified flags: SQLite 4096 default page size (since 3.12.0 2016); exact PG fill factor; Ribbon filter details; O'Neil 1996 body text; Bloom 1970 body.
- gaps: Bayer/McCreight (Springer blocked), Comer survey (ACM captcha), MySQL InnoDB, Ribbon filter source, concurrent B+-tree insert code in nbtinsert.c.

## 2026-06-08 — Phase 1 deep research (Wave 1; FORCED PARTIAL STOP — spend limit)
- shipped: Wave 1 research for foundations 01–03. Fanned out 7 `researcher` subagents in parallel
  (general-purpose + researcher persona — the only available agent type with web tools), one per
  source cluster:
  - 01: nand2tetris+Petzold+Scott (13 srcs) · Ben Eater SAP-1 + CS:APP (10 srcs)
  - 02: Missing Semester+TLCL+Bash manual (19 srcs) · shell internals+brennan+xv6+CodeCrafters (11 srcs)
  - 03: CS144/Minnow+RFC9293/6298 (9 srcs) · Kurose+Beej+E2E paper (18 srcs) · Stevens+HPBN+TLS1.3 (8 srcs)
  Validated all 7 against RESEARCH_PROTOCOL (6 sections, primary-sources-first, [UNVERIFIED] flags) —
  all pass. Reconciled each sub-course's clusters into `<subcourse>/_research.md`. Expanded
  RESEARCH_INDEX.md (Minnow-vs-Sponge, RFC 9293/6298/8446/9000/9114, brennan.io, GNU libc job-control,
  SAP-1/Malvino, gaia.cs.umass free companion, hpbn.co free, End-to-End paper, CUBIC/BBR, XarkLabs VHDL).
- decisions: ADR-001 (per-cluster files reconciled by brain to avoid parallel-write clobber);
  ADR-002 (spend limit hit mid-wave → forced stop, `factchecker` DEFERRED to next session).
- stopped-at: END OF WAVE 1, blocked by monthly spend limit ("You've hit your monthly spend limit").
  Phase 1 is ~3 of ~50 sub-courses deep. NOT a "corpus done" stop — an external blocker. No chapters
  written. Resume needs the spend limit raised (claude.ai/settings/usage), then:
  (1) run `factchecker` on Wave 1 load-bearing claims, (2) Wave 2 = sub-courses 04, 05, 06.
  Awaiting user: raise limit + sign-off on the resume plan before continuing.

## 2026-06-08 — Phase 0 bootstrap
- shipped: scaffolded the project — meta constitution files, subagent definitions,
  living-state files, README; initialized git and committed as "scaffold".
- decisions: none beyond following START_HERE.md Phase 0 verbatim.
- stopped-at: end of Phase 0. Awaiting "go" to begin Phase 1 (deep research). No research
  or course content written yet.
