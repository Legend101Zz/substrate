# Session log

Append-only, reverse-chronological. Each entry: shipped / decisions / stopped-at.

## 2026-06-10 — Phase 1 Wave 4: research + factcheck + RECONCILE 12 (research-papers-for-engineers)
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `ac2d61e`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv`
  was not modified; Code Puppy was not reinstalled.
- shipped: confirmed network reality (matches prior two sessions): only `lamport.azurewebsites.net` resolves (HTTP 200);
  every academic/ACM/arXiv/raw.github host = HTTP 000, including the Keshav "How to Read a Paper" PDF across 5 mirrors
  (Stanford, SIGCOMM CCR, UNB, ACM DOI, Harvard). Invoked the `researcher` subagent for Cluster A; it independently
  confirmed ZERO method-source fetches, so all Keshav/Roscoe/Mitzenmacher/Smith claims are `[UNVERIFIED from fetched source]`.
- shipped: fetched + extracted FOUR fresh Lamport primaries into `/tmp/substrate-12-sources/` via a throwaway
  `uv run --with pypdf` (Walmart index): "State the Problem Before Describing the Solution" (method backbone),
  "The Byzantine Generals Problem" (TOPLAS 1982), "Reaching Agreement in the Presence of Faults" (JACM 1980), and
  "The Part-Time Parliament" (original Paxos, TOCS 1998).
- shipped: wrote two cluster briefs — `12-.../_research_how-to-read-a-paper.md` (reading method, anchored on the
  verified Lamport expository rule; Keshav three-pass honestly flagged `[UNVERIFIED]`) and
  `12-.../_research_paper-canon-walkthroughs.md` (canon catalog: 4 fresh-verified Lamport papers + a status map of
  canon already line-verified in 06-11 + the still-blocked storage/ops trilogy flagged `[UNVERIFIED]`).
- shipped: factchecked both clusters in `12-.../_factcheck_phase1.md` with exact line receipts against the extracted
  text — Cluster A: 4 VERIFIED + 2 properly-flagged; Cluster B: 9 VERIFIED (incl. `3m+1`, conditions A/B,
  impossibility-then-`OM(m)`, PTP state-machine/majority/editor's-note, cross-refs) + 2 flagged groups; **0 blockers**.
- shipped: RECONCILED both clusters into `12-.../_research.md` (standard six sections) with the cross-cluster thesis
  (reader's rule from writer's rule -> three-pass triage -> the agreement chain as the exposition-quality teaching spine
  -> canon maps onto the headline course -> impossibility-first), preserving every `[UNVERIFIED]`/residual gap.
- shipped: expanded `meta/RESEARCH_INDEX.md` with verified 12 Lamport anchors + the residual 12 gap list; updated
  `meta/PROGRESS.md` (12 = RESEARCHING/reconciled).
- shipped: attempted the opportunistic step-5 fetch of the blocked 11 primaries (Gilbert/Lynch, Brewer, Abadi,
  Herlihy/Wing, Dynamo) — all still HTTP 000 on every academic/ACM host. The 11 `[UNVERIFIED]` flags stand unchanged;
  none erased.
- decisions: no ADR. Chose a TWO-cluster honest 12 (method backbone + verified canon spine) over a method-only stub
  that would have been entirely `[UNVERIFIED]`. Pivoted the verifiable depth onto the reachable Lamport host rather than
  faking Keshav/Google-trilogy coverage. One clean factchecked/reconciled checkpoint over raccoon-shaped completeness.
- stopped-at: Phase 1 with 07, 08, 09, 10, 11, AND **12 reconciled/factchecked**. All of foundations 01-12 now have
  reconciled `_research.md` + factcheck artifacts. Next batch = Phase 1 Wave 5 (Part II System Design 13-21), plus
  opportunistic fetches of the still-blocked method + storage canon (Keshav, MapReduce/GFS/Bigtable/Dynamo, Dapper,
  Tail at Scale) and the carried-forward 11 CAP/PACELC/Herlihy-Wing/Dynamo primaries when a healthier network exists.
  No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: add 11 CAP/distributed-commit cluster + RECONCILE 11
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `0fe860e`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified.
- shipped: fetched a NEW primary this session despite heavy network blocking (only `lamport.azurewebsites.net` and
  `example.com` resolved; MIT/CMU/Cornell/UMD/UCSB/UW/Brown timed out, ACM `dl.acm.org` returned Cloudflare/403,
  arXiv + `raw.githubusercontent.com` `HTTP 000`): Gray & Lamport "Consensus on Transaction Commit" (37-page
  tech-report PDF) from `lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`, extracted with a
  throwaway `uv run --with pypdf` (Walmart index) into `/tmp/substrate-11-cap`.
- shipped: wrote `11-distributed-systems-foundations/_research_cap-partitions-distributed-commit.md` (cluster 4, 329
  lines) covering CAP (linearizable-C, partition C-vs-A, Brewer's 2-of-3 correction), PACELC (EL-vs-EC latency tax),
  2PC (cost `3N-1`/four message delays, stable-storage durability), the 2PC blocking failure, classic 3PC
  split-brain critique, Paxos Commit (`2F+1` coordinators, progress with `F+1`, 2PC = `F=0` degenerate case), and the
  Spanner commit×replication×isolation intersection (2PC-over-Paxos, 2PL, snapshot-isolation read-only txns, commit
  wait).
- shipped: factchecked the cluster and saved `11-distributed-systems-foundations/_factcheck_cluster4.md` — 14
  load-bearing claims verified with exact line receipts against Gray & Lamport + cached Spanner/Paxos text; 0 blockers;
  2 citation-precision warnings (TODS-vs-tech-report pagination; missing ANSI/Berenson isolation source), both already
  logged as residual gaps. CAP/PACELC claims (Gilbert/Lynch, Brewer, Abadi) correctly state-and-flag as `[UNVERIFIED
  from fetched source]` because those primaries were network-blocked.
- shipped: RECONCILED all four 11 clusters into `11-distributed-systems-foundations/_research.md` (227 lines, standard
  six sections) with a cross-cluster synthesis arc (time/causality → vector clocks → model taxonomy → consistency
  models → quorums/consensus → CAP/PACELC → atomic commit → Spanner), preserving every logged `[UNVERIFIED]`/residual
  gap and the deliberate BFT/membership-change scope boundary.
- shipped: expanded `meta/RESEARCH_INDEX.md` with cluster-4 verified anchors + the consolidated reconciled-11 gap list;
  updated `meta/PROGRESS.md` (11 = reconciled; 12 = next).
- decisions: no ADR. Chose NOT to start 12 this session: network was heavily blocked, so 12 briefs would be
  source-starved and shallow. One clean reconciled-11 checkpoint beats a raccoon-shaped 12 stub. Per the plan, prefer a
  clean factchecked checkpoint over multiple shallow briefs.
- stopped-at: Phase 1 with 07, 08, 09, 10 reconciled/factchecked AND **11 now reconciled/factchecked** (four clusters).
  12 research-papers-for-engineers remains untouched. Next session: start 12 Phase-1 briefs (how-to-read-a-paper +
  canon walkthroughs), and opportunistically fetch the blocked 11 primaries (CAP/PACELC, Herlihy/Wing, Dynamo, Skeen,
  ANSI isolation) if a healthier network is available to close the `[UNVERIFIED]` gaps. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: add 11 consistency/replication/quorums cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; current checkpoint was `78c79ae`. A transient
  `git: Unable to read current working directory: Operation not permitted` (OneDrive/macOS privacy gremlin) appeared
  mid-session but cleared on retry; `/Users/m0t0hu6/.code-puppy-venv` was not modified and Code Puppy was not reinstalled.
- shipped: invoked the `researcher` subagent once (sequential, no fan-out); it failed with `httpx.ReadTimeout`. Fell
  back to a manual BRAIN primary-source pass rather than touching the venv.
- shipped: fetched/extracted primary PDFs into `/tmp/substrate-11-sources` with a throwaway `uv run --with pypdf`
  (Walmart index): Lamport "How to Make a Multiprocessor Computer" (sequential consistency), Paxos Made Simple,
  Raft USENIX ATC 2014, and Spanner OSDI 2012. Herlihy/Wing, Dynamo, and MIT 6.5840 notes were blocked by network
  resets (ACM/Brown/CMU/Cornell/Princeton/UW/pdos/allthingsdistributed) and remain `[UNVERIFIED from fetched source]`.
- shipped: wrote `11-distributed-systems-foundations/_research_consistency-replication-quorums.md` (266 lines, standard
  six brief sections) covering consistency-as-contract, sequential vs linearizability vs eventual, leader/follower
  replication, quorum=majority-intersection, Paxos chooses values / Raft+Multi-Paxos build the log, and the Spanner
  bridge to externally-consistent transactions.
- shipped: manual factcheck saved as `11-distributed-systems-foundations/_factcheck_cluster3.md` — 13 load-bearing
  claims verified against primary text with exact line receipts, 0 blockers, 2 citation line-drift warnings (Paxos
  progress 282–293; Spanner commit-wait 603/731 + tightened Paxos majority/chosen lines) patched in the brief.
- decisions: no ADR. Chose **not** to reconcile 11 into `_research.md`: it now has three clean clusters but still
  lacks CAP/partitions and distributed-commit coverage, and Herlihy/Wing + Dynamo primaries are unfetched. One clean
  cluster checkpoint beats a raccoon-shaped `_research.md`.
- stopped-at: Phase 1 with 11 having THREE factchecked clusters but no reconciled `_research.md`. 12 untouched. Next
  session adds CAP/partitions + distributed-commit/transactions, then reconciles 11 if coverage is honestly enough.

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
