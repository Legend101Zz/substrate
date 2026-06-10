# Session log

Append-only, reverse-chronological. Each entry: shipped / decisions / stopped-at.

## 2026-06-10 — Phase 1 Wave 4: add 11 vector-clocks/model-taxonomy cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current checkpoint
  was `81f0769`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv` was
  not modified.
- shipped: used the `researcher` subagent sequentially (no parallel fan-out) to draft
  `11-distributed-systems-foundations/_research_vector-clocks-model-taxonomy.md`; then independently fetched/checked
  sources in `/tmp/substrate-11-sources`. Paxos Made Simple was fetched and extracted with a throwaway
  `uv run --with pypdf` command using the Walmart PyPI index; Fidge/Mattern/DLS/Dynamo/CBCAST direct PDFs remained
  blocked and are kept `[UNVERIFIED from fetched source]` in the brief.
- shipped: ran the `factchecker` subagent on the new cluster and saved
  `11-distributed-systems-foundations/_factcheck_cluster2.md`; patched both blockers: the synchronous rotating-
  coordinator process bound now says `N >= f+1` with source-needed caveat, and Paxos/Raft wording now distinguishes
  Paxos Made Simple's asynchronous model from the teaching "behaves as if partial synchrony" framing.
- shipped: patched follow-up warnings: FLP now uses the exact "totally correct" wording, vector-clock "Strong Clock
  Condition" now notes the Lamport naming collision, and stale Paxos extraction metadata was corrected.
- shipped: expanded `meta/RESEARCH_INDEX.md` with cluster-2 verified anchors/gaps, updated `meta/PROGRESS.md`, and
  updated `meta/NEXT_SESSION.md` with the exact next-session prompt.
- decisions: no ADR. Chose not to reconcile 11 because it still lacks consistency/replication/quorums/Raft-Paxos/CAP/
  distributed-commit coverage; one clean factchecked cluster is better than a raccoon-shaped `_research.md`.
- stopped-at: Phase 1 with 11 having two factchecked clusters but no reconciled `_research.md`. 12 remains untouched.
  Next session should add the consistency + replication vocabulary cluster, factcheck it, then decide whether 11 has
  enough coverage to reconcile. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: start 11 time/clocks/partial-failure cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current checkpoint
  was `e227319`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv` was
  not modified.
- shipped: created `11-distributed-systems-foundations/` and added
  `11-distributed-systems-foundations/_research_time-clocks-ordering-failure.md` (starter cluster only) covering
  happened-before, Lamport logical clocks, arbitrary total-order extension, physical-clock bounds, Chandy-Lamport
  consistent global snapshots, FLP partial failure/asynchrony, Spanner TrueTime uncertainty, and Chandra-Toueg failure
  detector framing.
- shipped: fetched primary sources into `/tmp/substrate-11-sources` and extracted PDFs with a throwaway
  `uv run --with pypdf` environment: Lamport 1978, Chandy-Lamport 1985, FLP/JACM 1985, Spanner OSDI 2012; fetched
  Chandra-Toueg JACM 1996 as PostScript and inspected noisy text with `strings`.
- shipped: manually factchecked 22 load-bearing claims and saved
  `11-distributed-systems-foundations/_factcheck_phase1.md`; blockers: 0. Warning: Chandra-Toueg exact definitions need
  a cleaner text/PDF before Phase 2 prose.
- shipped: expanded `meta/RESEARCH_INDEX.md` with verified 11 starter anchors and residual gaps; updated
  `meta/PROGRESS.md` to mark 11 as RESEARCHING.
- decisions: no ADR. Chose not to start the second 11 cluster in this session; one clean factchecked checkpoint beats
  two mushy ones, because we are building a course, not a content slurry machine.
- stopped-at: Phase 1 with 11 started but not reconciled. Next should add vector clocks/model taxonomy and/or the
  consistency + replication vocabulary cluster, then factcheck and only reconcile 11 when coverage is solid. 12 remains
  untouched. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: factcheck/deepen/reconcile 10 NGINX core
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `ef3528d`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not touched.
- shipped: manually spot-checked the existing 10 starter brief against NGINX `release-1.31.1`; patched it to pin NGINX
  source URLs to the release tag, corrected/clarified `accept_mutex` default (`0`) and `accept_mutex_delay` (`500ms`),
  and added the missing `ngx_posted_next_events` event-loop step after factchecker warning.
- shipped: added `10-nginx-proxies-and-load-balancing/_research_load-balancing-peer-selection.md` covering smooth
  weighted round-robin, passive failure accounting, `max_fails`, `fail_timeout`, `least_conn`, `ip_hash`, generic and
  consistent hash, upstream zones/shared state, and `slow_start` availability caveats from NGINX `release-1.31.1`
  source and official docs where available.
- shipped: added `10-nginx-proxies-and-load-balancing/_research_proxy-buffering-retries-timeouts.md` covering request
  buffering, response buffering, event-pipe temp files, `proxy_next_upstream`, connect/read/send timeouts, and slow
  client/upstream backpressure behavior from NGINX source.
- shipped: ran `factchecker` on 10; saved `10-nginx-proxies-and-load-balancing/_factcheck_phase1.md`. It checked 43
  load-bearing claims against NGINX `release-1.31.1`; no unsupported/misattributed claims remained after patches.
  nginx.org doc wording was blocked in the factchecker environment, so doc wording is explicitly flagged for Phase 2
  recheck while source-level behavior is confirmed.
- shipped: reconciled all 10 core clusters into `10-nginx-proxies-and-load-balancing/_research.md` with the standard
  six sections; expanded `meta/RESEARCH_INDEX.md` with verified 10 source anchors and residual gaps.
- decisions: no ADR. Chose not to force the optional TLS/HTTP2/HTTP3 cluster or start 11 in this session; stopped at a
  clean 10 factchecked/reconciled checkpoint rather than doing drive-by distributed systems research. Shocking restraint,
  frankly.
- stopped-at: Phase 1 with 07, 08, 09, and 10 reconciled/factchecked. 10 residual gaps: nginx.org wording recheck,
  `reuseport`/`EPOLLEXCLUSIVE`, thread pools, full HTTP phase engine, `X-Accel-Buffering`, cache-specific paths,
  TLS/OpenSSL, HTTP/2, HTTP/3/QUIC, and product-boundary checks for commercial-only directives. 11 and 12 untouched.
  No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 3/4: finish 09; start 10 starter cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; confirmed git HEAD `f5e4069` and clean
  working tree before edits; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not touched.
- shipped: spot-checked the existing 09 Kafka storage starter against Kafka 3.9 source/docs; patched source links
  to pin Kafka 3.9 and later corrected `LocalLog` to the actual 3.9 path
  `core/src/main/scala/kafka/log/LocalLog.scala`.
- shipped: added 09 replication/availability cluster
  `09-message-queues-logs-and-kafka/_research_replication-availability.md` covering leader/follower replication,
  ISR, high watermark, `acks`, min ISR, unclean leader election, leader epochs, and KRaft/controller caveats.
- shipped: added 09 consumer groups/offsets cluster
  `09-message-queues-logs-and-kafka/_research_consumer-groups-offsets.md` covering group coordinator routing,
  `__consumer_offsets`, committed vs current offsets, classic/cooperative rebalance, early-access 3.9 consumer
  protocol, lag/replay, and fetch isolation.
- shipped: added 09 delivery semantics/transactions cluster
  `09-message-queues-logs-and-kafka/_research_delivery-semantics-transactions.md` covering at-most/at-least/EOS
  caveats, idempotent producer IDs/epochs/sequences, transaction coordinator, `__transaction_state`, markers,
  LSO, `read_committed`, and transactional offset commits.
- shipped: ran `factchecker` on 09; saved `09-message-queues-logs-and-kafka/_factcheck_phase1.md`; patched the
  one blocker and two precision warnings. No 09 factcheck blockers remain.
- shipped: reconciled all 09 clusters into `09-message-queues-logs-and-kafka/_research.md` with the standard six
  sections; expanded `meta/RESEARCH_INDEX.md` with verified Kafka 3.9 source anchors and residual gaps.
- shipped: created `10-nginx-proxies-and-load-balancing/` and starter brief
  `10-nginx-proxies-and-load-balancing/_research_event-driven-reverse-proxy.md`, covering NGINX master/worker,
  event loop, epoll dispatch, accept mutex/backoff, HTTP request state, upstream reverse-proxy path, and keepalive.
  This 10 starter is not factchecked or reconciled.
- decisions: no ADR. Chose to start only one tightly scoped 10 cluster after 09 was clean, rather than rushing all
  of Wave 4 like a caffeinated squirrel with `grep`.
- stopped-at: Phase 1 with 07, 08, and 09 reconciled/factchecked; 10 has exactly one starter cluster and needs
  factcheck + deeper clusters on load-balancing/peer selection, proxy buffering/timeouts/retries/backpressure,
  optionally TLS/HTTP2/HTTP3, then reconciliation. 11–12 untouched. No chapters. No Phase 2.

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
