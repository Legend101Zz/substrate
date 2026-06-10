
# Research index (seed — researchers expand this)

## Study these DEEPLY before designing the course (primary inspiration)
system-design-primer (donnemartin) · karanpratapsingh/system-design ·
ashishps1/awesome-system-design-resources · bryanyzhu/agentic-ai-system-course
(steal the spine + real-system-note skeleton; invert its depth stance) ·
pingcap/awesome-database-learning · codecrafters-io/build-your-own-x · Teach Yourself CS.

## Reference courses (canonical, free where noted)
CS:APP / CMU 15-213 · OSTEP · Berkeley CS162 · MIT 6.5840 (formerly 6.824) Distributed
Systems · CMU 15-445/645 Database Systems · Stanford CS144 Networking ·
MIT 6.172 Performance Engineering of Software Systems.

## Per sub-course anchors
01 computers-first-principles: nand2tetris · Ben Eater (8-bit + 6502) · Petzold "Code" ·
   "But How Do It Know" · CS:APP · (the linked "how a CPU works" video as on-ramp).
02 terminal-shell: MIT Missing Semester · Shotts "The Linux Command Line" · Julia Evans
   zines · [build: own-shell].
03 networking: Stanford CS144 · Kurose & Ross Top-Down · Beej's Guide · Grigorik HPBN ·
   Stevens TCP/IP Illustrated v1 · [build: own-tcp-ip, CS144 sponge].
04 os-internals: OSTEP · Berkeley CS162 · MIT 6.S081/xv6 · Kerrisk TLPI · Love LKD ·
   Brendan Gregg "Systems/Linux Performance".
05 language-runtime: Crafting Interpreters · Thorsten Ball (interpreter/compiler in Go) ·
   CPython Internals · V8 blog → appendices C/D/E/K.
06 data-structures-for-systems: CLRS · Skiena · B-tree/LSM/bloom/HLL/consistent-hashing papers.
07 database-internals: CMU 15-445 · Petrov "Database Internals" · DDIA ·
   Hellerstein/Stonebraker "Architecture of a DB System" · Red Book · Use The Index Luke ·
   pingcap · [build: own-database (cstack)] → appendix F.
08 caches-storage: "Memcached at Facebook" · Redis design · LSM-vs-B-tree write paths → appendix G.
09 mq-logs-kafka: Kreps "The Log" · Kafka paper · Kafka Definitive Guide · Kafka design docs ·
   Kafka broker storage/log source (`LocalLog`, `LogSegment`, `LogCleaner`, `LogConfig`, `Partition`) ·
   [build: own-message-queue] → appendix H.
10 nginx-proxies-lb: aosabook nginx chapter · nginx docs · SEDA paper · LB algorithms ·
   [build: own-http-server-and-load-balancer].
11 distributed-foundations: MIT 6.5840 · DDIA · van Steen & Tanenbaum · Lamport "Time,
   Clocks" · Aphyr Jepsen → appendix L + the paper canon below.
12 research-papers: Keshav "How to Read a Paper" · Papers We Love · the full canon below.

## Paper canon (for 11, 12, L, and cross-cutting)
MapReduce · GFS · Bigtable · Dynamo · Spanner · Raft · Paxos Made Simple · ZooKeeper ·
Chubby · Kafka paper + design docs · Memcached at Facebook · The Tail at Scale ·
Out of the Tar Pit · CALM theorem + consistency papers · Borg / Omega / Kubernetes ·
SEDA · Dapper (tracing) · Lampson "Hints for Computer System Design" ·
Saltzer/Reed/Clark "End-to-End Arguments" · Dean "Latency Numbers" · Drepper "What Every
Programmer Should Know About Memory".

## Appendix anchors
A computer-architecture: nand2tetris · Ben Eater · CS:APP · Petzold.
B linux-internals: TLPI · Love LKD · Bovet "Understanding the Linux Kernel" · Brendan
   Gregg Linux Performance · /proc, eBPF.
C python-internals: Shaw "CPython Internals" · "Inside the Python VM" · dis · Fluent Python.
D js-v8-node: V8 blog · Mathias Bynens engine fundamentals · libuv · Node internals ·
   event-loop talks (Roberts, Archibald).
E java-jvm: JVM spec · Oaks "Java Performance" · Shipilëv blogs · HotSpot JIT · GC.
F postgres-internals: Suzuki "The Internals of PostgreSQL" (free) · Postgres docs · MVCC · WAL.
G redis-internals: Redis source + docs · "Redis in Action" · single-thread event loop · RDB/AOF.
H kafka-internals: Kafka design docs · ISR/replication · log compaction · Definitive Guide internals.
I docker-containers: Liz Rice "Containers from Scratch" · cgroups/namespaces · runc/OCI ·
   [build: own-docker].
J kubernetes-internals: Borg/Omega/K8s papers · K8s docs · reconciliation/controllers · etcd.
K compilers-interpreters-jit: Crafting Interpreters · Thorsten Ball · Dragon Book · JIT.
L consensus-replication-transactions: Raft · Paxos Made Simple · ZooKeeper · Spanner ·
   2PC/3PC · isolation levels · Jepsen · CALM.
M ai-agent-memory-tools-eval: Anthropic "Building Effective Agents" + context engineering +
   multi-agent writeup · LangGraph docs · OpenAI Agents SDK docs · LlamaIndex
   workflows/agents · DSPy · RAG papers + RAG evaluation · ReAct · Reflexion · MemGPT ·
   CoALA · SWE-agent · OpenHands · Aider · Claude Code workflows · byoharness.dev ·
   Superpowers/RPI · agent tracing & guardrails resources · Chip Huyen "AI Engineering".
N math-for-systems: queueing theory + Little's Law · probability/tail latencies ·
   hashing math · Bloom/HyperLogLog math · info-theory basics · linear algebra for embeddings.
O cloud-infra-basics: AWS/GCP primitives · regions/AZs · object storage · IaC · 12-factor.

## Build-your-own catalogue
build-your-own-x repo · CodeCrafters (Redis/Git/SQLite/Docker/HTTP server/shell/interpreter) ·
own database · own Redis · own Git · own shell · own Docker · own TCP/IP stack ·
own compiler/interpreter · own search engine · own message queue · own coding-agent harness.

────────────────────────────────────────────────────────
# Phase 1 expansions (researchers append below; primary sources first)
────────────────────────────────────────────────────────

## Wave 1 — new/confirmed primary sources (sub-courses 01, 02, 03)

### 01 computers-from-first-principles
- nand2tetris free chapters 1–5 PDFs (Boolean logic, Boolean arithmetic/ALU, memory, machine
  language, computer architecture) — nand2tetris.org; the Hack ISA `111a cccc ccdd djjj` encoding.
- Petzold *Code* 2nd-ed companion site (Ch.17 et al.); note chapter numbers differ from 1st ed.
- J. Clark Scott *But How Do It Know?* — CPU GitHub implementation + author design write-up
  (exact per-step control wiring is in the paywalled book).
- Ben Eater 8-bit = **SAP-1 (Malvino "Simple-As-Possible")** architecture; eater.net/8bit/{clock,
  registers,alu,ram,pc,output,control}; SAP-1 control-word signal reference mirror at
  ullright.org (community, [UNVERIFIED] vs eater.net page text).
- Ben Eater 6502: eater.net/6502; address-decoding WHY at wilsonminesco.com/6502primer/addr_decoding.html.
- CS:APP 3e (csapp.cs.cmu.edu/3e) + 15-213 F15 lecture→chapter schedule + labs page (Data/Bomb/
  Attack/Cache/Arch). Memory mountain = ch.6 signature demo. System V AMD64 ABI for calling convention.
- XarkLabs/BenEaterVHDL (FPGA/sim port) as a no-breadboard build path.

### 02 terminal-shell-and-dev-environment
- **Bash Reference Manual** (gnu.org/software/bash/manual) — *Shell Expansions* (canonical expansion
  ORDER), *Word Splitting* (IFS), *Environment* (export→child inheritance). The spec-level WHY.
- MIT Missing Semester 2020 lecture URLs (course-shell, shell-tools, command-line, data-wrangling,
  version-control). Shotts TLCL free chapters (linuxcommand.org lc3_* pages).
- POSIX man pages (man7.org): fork(2), execve(2), wait(2), pipe(2), dup2(2).
- Stephen Brennan "Write a Shell in C" (brennan.io). GNU libc manual *Job Control* +
  *Implementing a Shell* (sourceware.org mirror; gnu.org 302-redirects there).
- xv6 sh.c (github mit-pdos/xv6) as a tiny real shell. CodeCrafters "Build your own shell" track.
- Julia Evans jvns.ca — correct live post is 2016/10/04 "exec-will-eat-your-brain"
  (the 2016/02/20 "how-to-run-a-program" URL 404s).

### 03 networking-from-first-principles
- Stanford CS144 cs144.github.io — current framework is **Minnow** (rewrite of older **Sponge**);
  build ladder ByteStream→Reassembler→Wrap32+TCPReceiver→TCPSender; check0–3 lab PDFs.
  Sponge "Lab 4: the summit" (hand-authored TCPConnection state machine) was DROPPED in Minnow.
  Use github.io PDFs (cs144.keithw.org mirror has a TLS cert-name mismatch).
- **RFC 9293** (TCP, consolidated; supersedes RFC 793) — state machine, 3-way handshake, ISN,
  TIME-WAIT=2·MSL. **RFC 6298** (RTO computation; CS144 simplifies it: fixed initial RTO + doubling,
  no adaptive SRTT/RTTVAR).
- Kurose & Ross free companion gaia.cs.umass.edu (online_lectures index + per-section videos +
  downloadable .pptx slide decks; full text paywalled). Beej's Guide to Network Programming
  (beej.us/guide/bgnet) — sockets API, byte order, select/poll (epoll/kqueue light/platform-specific).
- **HPBN free at hpbn.co** (Grigorik) — latency primer, building-blocks-of-tcp, TLS, http2 chapters.
- Stevens *TCP/IP Illustrated v1* (cite by chapter title; 2nd-ed Fall&Stevens renumbers).
- **RFC 8446** (TLS 1.3, 1-RTT/0-RTT). **RFCs 9000/9001/9002** (QUIC) + **9114** (HTTP/3) — the
  QUIC/HTTP-3 gap not covered by HPBN/Stevens; ADD as cross-cutting transport sources.
- Saltzer/Reed/Clark "End-to-End Arguments in System Design" (1984) MIT PDF — the layering WHY.

## Cross-cutting additions discovered (promote as needed)
- CUBIC (Linux default) and BBR (Google) congestion control — name alongside Reno/AIMD in 03/11/13.
- QUIC/HTTP-3 transport (RFC 9000/9114) — relevant to 03, 16, and appendix O.

## Wave 2 — new/confirmed primary sources (sub-courses 04, 05, 06)

### 04 operating-systems-internals
- MIT 6.1810/xv6-riscv source + rev4 book + 2024 labs: syscall, pgtbl, traps, cow, lock, fs,
  mmap. xv6 is the clean mechanism anchor for trap/trampoline, scheduler, Sv39, locks, WAL/fs.
- OSTEP chapter corpus and projects via `remzi-arpacidusseau/ostep-homework` + `ostep-projects`;
  direct PDFs were proxy-blocked, so quote exact OSTEP prose only after direct PDF access.
- Berkeley CS162/Pintos + Anderson & Dahlin OSPP as broader OS project/reference anchors.
- Linux current primaries: `mkerrisk/man-pages` for fork/mmap/signal/epoll/perf/proc; Linux kernel
  docs/source for CFS/EEVDF, procfs, pagemap, cgroup v2, bpf verifier, perf security, memory alloc.
- Brendan Gregg tooling via GitHub: FlameGraph, perf-tools, bpf-perf-tools-book. USE Method primary
  page blocked; verify formal checklist before quoting.

### 05 programming-language-runtime-internals
- `munificent/craftinginterpreters` book/source as primary for scanner, recursive descent, Pratt,
  AST visitor, bytecode chunk, stack VM, closures/upvalues, Obj header, NaN boxing, mark-sweep GC.
- Thorsten Ball Monkey architecture verified through community ports; original book/code is paywalled,
  so do not quote exact Ball text/stage order without access.
- CPython primaries: `python/cpython` `Include/object.h`, `InternalDocs/interpreter.md`,
  `InternalDocs/frames.md`, `Python/generated_cases.c.h`, `Python/ceval_gil.c`, `Python/gc.c`.
- V8/libuv primaries: V8 Maps/FeedbackVector/Ignition/Maglev/Scavenger source; libuv design.rst and
  `src/unix/core.c` for event-loop phases.
- OpenJDK primaries: compiler levels, class parser/verifier, safepoint polling, G1 heap. Tier/JIT
  thresholds and CPython Tier-2 JIT claims are version-sensitive.

### 06 data-structures-for-systems
- SQLite `btreeInt.h` + fileformat2, PostgreSQL `nbtree/README`, LevelDB `doc/impl.md` and
  `doc/table_format.md`, RocksDB options/dbformat/compaction/Bloom sources as storage DS anchors.
- Bloom filters: LevelDB `util/bloom.cc`, RocksDB `util/bloom_impl.h`; Bloom 1970 and some survey
  papers were blocked, so implementation sources carry the exact mechanics.
- Skip lists: Pugh 1990, Redis `t_zset.c`, RocksDB `memtable/skiplist.h`, OpenJDK
  `ConcurrentSkipListMap.java`.
- Ring buffers: LMAX Disruptor source (`Sequence`, RingBuffer, sequencers, wait strategies); whitepaper
  benchmark numbers not fetched, keep [UNVERIFIED].
- Consistent hashing/HLL: Karger 1997, groupcache implementation, Jump consistent hash paper,
  Redis Cluster `cluster.h` (slots, not consistent hashing), Flajolet HLL 2007, Ertl 2017,
  Redis `hyperloglog.c`.

## Wave 3 — new/confirmed primary sources (sub-course 07 started)

### 07 database-internals
- BusTub current master as teaching implementation anchor: `config.h` (8192B pages, 128-frame buffer
  pool, batch size 20, legacy `LRUK_REPLACER_K=10`, `TXN_START_ID`, `DISABLE_LOCK_MANAGER`),
  `table_page.h`/`tuple.h` (slotted page, `TupleInfo=24`, `TupleMeta=16`), `arc_replacer.h`,
  `buffer_pool_manager.h`, `disk_scheduler.h`, `log_record.h`/`log_manager.h`, B+ tree page headers,
  `abstract_executor.h`, `optimizer.h`, `transaction.h`, `transaction_manager.cpp`, `watermark.h`,
  and `lock_manager.h` (Project 3 spec caveat, not active Project 4 MVCC runtime).
- PostgreSQL current master as production anchor: `bufpage.h`, `itemid.h`, `htup_details.h`,
  `snapshot.h`, `heapam_visibility.c`, `transam.h`, `xlogrecord.h`, `xlog.h`, `pg_control.h`,
  `lockdefs.h`, `optimizer/README`, `costsize.c`, `cost.h`, `pathkeys.c`, `pathnode.c`, `selfuncs.c`,
  `tuplesort.c`, `nodeHashjoin.c`, and `backend/jit/README`; docs for planner stats and query GUCs.
- MySQL/InnoDB 8.4 source: `read0types.h` (ReadView), `trx0trx.h` (states/isolation), `trx0undo.h`,
  `lock0types.h`, `lock0lock.h` (gap/next-key/insert-intention locks), and `log0sys.h`.
- DuckDB source/docs: `vector_size.hpp` (`STANDARD_VECTOR_SIZE=2048`, compile-time power-of-two
  check), `data_chunk.hpp`, `physical_hash_join.hpp`, and `duckdb.org/why_duckdb` for design lineage.
- Classic papers needing direct-text verification before exact quote/page use: Graefe 1994 Volcano,
  Graefe 1993 query evaluation survey, Selinger 1979 System R (Duke scanned PDF fetched but not text
  extracted), Mohan 1992 ARIES, Crotty et al. 2022 mmap, MonetDB/X100, HyPer/Neumann 2011, PAX 2001.

### 08 caches-and-storage-systems
- Redis current source/docs anchors: `src/server.h` (maxmemory policy constants including LRU/LFU/LRM,
  DB `keys`/`expires`, `maxmemory_samples`, LFU knobs), `src/evict.c` (candidate pool `EVPOOL_SIZE=16`,
  sampled eviction with `kvstoreDictGetSomeKeys`, LRU/LFU/LRM/TTL scoring, `performEvictions()`),
  `src/expire.c` (active expiration constants: 20 keys/loop, 1000µs fast duration, 25% slow CPU baseline,
  10% acceptable stale baseline, effort tuning), official Redis eviction docs (approximate LRU/LFU,
  `maxmemory-samples`, LRM), and persistence docs (RDB, AOF, fsync modes, rewrite, Redis 7 multi-part AOF).
- Memcached anchors: `doc/protocol.txt` (TTL, CAS, touch/gat/gats, meta/stale metadata), `items.c`
  (HOT/WARM/COLD/TEMP segmented LRU, `lru_pull_tail`, maintainer/crawler), `slabs.c` (slab classes,
  chunk sizing, `perslab`), `slab_automove.c` (class rebalancing), `thread.c` (worker threads and item
  locks), `doc/storage.txt` + `extstore.c` (optional external storage path). Facebook Memcached NSDI 2013
  PDF text extracted via `/tmp` pypdf; leases, stale values, pools, Gutter, regional pools, and 17K/s→1.3K/s
  lease experiment are verified from text.
- Admission/dogpile/consistency anchors: TinyLFU/W-TinyLFU paper (`arxiv.org/abs/1512.00727`), Caffeine
  `FrequencySketch.java`, `BoundedLocalCache.java`, simulator `TinyLfu.java`, Caffeine Efficiency wiki,
  ARC FAST 2003 PDF (`usenix.org/legacy/events/fast03/.../megiddo.pdf`, extracted), Go
  `x/sync/singleflight.go`, RFC 5861 (`stale-while-revalidate`, `stale-if-error`), and RFC 9111 (HTTP
  cache keys/freshness/validation/stale constraints/unsafe-method invalidation). Remaining gaps: release-pin
  Redis/Memcached source, ARC pseudo-code/patent status, Count-Min formal error bounds, write-through/write-back
  taxonomy source, and XFetch/probabilistic early expiration primary source.

### 09 message-queues-logs-and-kafka
- Kafka 3.9 repo docs as primary anchors: `docs/design/design.md` (log abstraction, consumer position,
  delivery semantics, replication/ISR/acks/unclean election, compaction), `docs/implementation/log.md`
  (offset-as-id, segment/index mechanics), and `docs/operations/kraft.md` (KRaft roles/controller quorum).
  Public `kafka.apache.org/*/documentation.html` currently resolves to a redirect/JS shell in this harness;
  use repo Markdown for exact text.
- Kafka 3.9 log/storage source anchors: `core/src/main/scala/kafka/log/LocalLog.scala` (3.9 path;
  trunk later has Java/storage `LocalLog`), `storage/.../LogSegment.java`, `storage/.../LogConfig.java`,
  and `core/src/main/scala/kafka/log/LogCleaner.scala` for segments, retention, and compaction.
- Kafka 3.9 replication/availability anchors: `core/.../cluster/Partition.scala` (leader append,
  ISR shrink/expand, high watermark, min ISR), `core/.../server/ReplicaFetcherThread.scala`,
  `core/.../server/AbstractFetcherThread.scala`, `storage/.../epoch/LeaderEpochFileCache.java`,
  `server/.../ReplicationConfigs.java`, `server-common/.../ServerLogConfigs.java`,
  `core/.../controller/PartitionStateMachine.scala`, plus KRaft `metadata/.../QuorumController.java`,
  `metadata/.../ReplicationControlManager.java`, and `raft/.../KafkaRaftClient.java`.
- Kafka 3.9 consumer-group anchors: `clients/.../common/internals/Topic.java` (`__consumer_offsets`),
  `group-coordinator/.../GroupCoordinatorService.java` (group→offsets-partition formula),
  `GroupCoordinatorConfig.java` (50 partitions, 100MB segments, 7-day retention, consumer protocol early
  access warning), `OffsetMetadataManager.java`, `CoordinatorRecordHelpers.java`, `ClassicGroupState.java`,
  `ConsumerPartitionAssignor.java`, `CooperativeStickyAssignor.java`, `ConsumerGroupHeartbeatRequest.json`,
  `OffsetCommitRequest.json`, `FetchRequest.json`, `FetchResponse.json`, and `CompletedFetch.java`.
- Kafka 3.9 idempotence/transaction anchors: KIP-98 (cwiki, fetched), `ProducerConfig.java` (`acks="all"`,
  `enable.idempotence=true`, max in-flight ≤5), `DefaultRecordBatch.java`, `ProducerAppendInfo.java`,
  `ProducerStateManager.java`, `TransactionCoordinator.scala`, `TransactionLog.scala`,
  `TransactionMetadata.scala`, `TransactionStateManager.scala`, `EndTransactionMarker.java`,
  `TransactionIndex.java`, `AbortedTxn.java`, `UnifiedLog.scala` (`lastStableOffset`), `FetchIsolation.java`,
  `KafkaProducer.java`, and `TransactionManager.java`.
- Remaining 09 gaps: replace mirrored Kafka paper URL with canonical if accessible; read KIP-101/497/500/848/360
  before quoting rationale; trace `CoordinatorRuntime`, offset-expiration scheduler, fetch-from-follower routing,
  sticky assignor/static membership fencing, `TransactionMarkerChannelManager`, `__transaction_state` expiry,
  and long-open-transaction/log-cleaner interactions before Phase 2 prose.

### 10 nginx-proxies-and-load-balancing
- NGINX event-driven reverse-proxy anchors, factchecked against `nginx/nginx` `release-1.31.1`: AOSA Vol. 2
  NGINX chapter (`raw.githubusercontent.com/aosabook/.../nginx.html`), `src/os/unix/ngx_process_cycle.c`
  (master/worker lifecycle), `src/event/ngx_event.c` (`ngx_process_events_and_timers`, accept mutex defaults,
  `ngx_posted_next_events`), `src/event/modules/ngx_epoll_module.c` (epoll dispatch and stale instance bit),
  `src/event/ngx_event_accept.c` (`ngx_accept_disabled`), `src/event/ngx_event.h`, `src/core/ngx_connection.h`,
  `src/http/ngx_http_request.c/.h`, `src/http/ngx_http_upstream.c`, `src/http/modules/ngx_http_proxy_module.c`,
  and `src/http/modules/ngx_http_upstream_keepalive_module.c`.
- NGINX upstream load-balancing anchors (`release-1.31.1`): `src/http/ngx_http_upstream_round_robin.h/.c`
  (smooth weighted round-robin, `weight`/`effective_weight`/`current_weight`, passive failure accounting,
  `max_fails=1`, `fail_timeout=10` defaults), `src/http/modules/ngx_http_upstream_least_conn_module.c`,
  `src/http/modules/ngx_http_upstream_ip_hash_module.c`, `src/http/modules/ngx_http_upstream_hash_module.c`, and
  `src/http/modules/ngx_http_upstream_zone_module.c` (shared-memory upstream zones). Official docs anchors:
  `nginx.org/en/docs/http/ngx_http_upstream_module.html` and `nginx.org/en/docs/http/load_balancing.html`; factchecker
  could not fetch nginx.org, so doc wording must be rechecked before Phase 2 prose.
- NGINX proxy buffering/retry/timeout anchors (`release-1.31.1`): `src/http/modules/ngx_http_proxy_module.c`
  (defaults: request/response buffering on, connect/send/read 60s, buffer sizes, temp-file max 1GiB,
  `proxy_next_upstream` default `error timeout`), `src/http/ngx_http_upstream.c` (retry gates, non-buffered paths,
  timers), and `src/event/ngx_event_pipe.c/.h` (buffer chains, temp files, slow-client backpressure). Official docs
  anchor: `nginx.org/en/docs/http/ngx_http_proxy_module.html`; recheck wording before Phase 2 prose.
- Remaining 10 gaps: trace `reuseport`/`EPOLLEXCLUSIVE` operational interaction, `ngx_thread_pool.c`, full HTTP phase
  engine, `X-Accel-Buffering`, cache-specific proxy paths, TLS termination/OpenSSL, HTTP/2 stream multiplexing/flow
  control, HTTP/3/QUIC, and exact commercial/open-source boundaries for `slow_start`, active health checks, sticky,
  queue, random, least_time, and dynamic membership before operational config prose.

### 11 distributed-systems-foundations
- Time/clocks/ordering/partial-failure starter anchors, factchecked manually from fetched primary sources:
  Lamport 1978 `time-clocks.pdf` (happened-before, Clock Condition, IR1/IR2 logical clocks, arbitrary total-order
  extension, physical-clock drift/synchronization bounds, failure needing physical-time context), Chandy-Lamport 1985
  `chandy.pdf` (global state = process + channel states, no shared clocks/memory, inconsistent naive cuts, meaningful
  recorded state via reachability), FLP/JACM 1985 `jacm85.pdf` (completely asynchronous model, no synchronized clocks
  or death detector, no deterministic consensus termination with one unannounced crash), Spanner OSDI 2012
  `spanner-osdi2012.pdf` (TrueTime interval, bounded uncertainty, wait out uncertainty), and Chandra-Toueg JACM 1996
  `CT96-JACM.ps` (unreliable failure detectors; completeness/accuracy framing; exact definitions need cleaner text).
- Vector-clocks/model-taxonomy cluster anchors, factchecked in `_factcheck_cluster2.md`: Lamport 1978 scalar-clock
  converse limitation; Fidge 1988 and Mattern 1989 vector-clock algorithm / bidirectional clock condition remain
  `[UNVERIFIED from fetched source]` because primary PDFs were blocked; Charron-Bost 1991 O(N) lower bound remains
  `[UNVERIFIED]`; Dynamo SOSP 2007 version vectors and Birman/Schiper/Stephenson 1991 CBCAST remain `[UNVERIFIED]`
  due to blocked PDFs; FLP/JACM 1985 anchors asynchronous model and DLS/PODC 1984 citation; DLS/JACM 1988 partial
  synchrony model taxonomy remains `[UNVERIFIED from fetched source]`; Paxos Made Simple was fetched/extracted and
  verifies asynchronous non-Byzantine model plus liveness requiring randomness or real time/timeouts.
- Consistency/replication/quorums cluster anchors, factchecked in `_factcheck_cluster3.md` with exact line receipts:
  Lamport IEEE TC 1979 `lamport-multiprocessor.txt` (sequential consistency definition); Spanner OSDI 2012 (external
  consistency ≡ linearizability, T1-commits-before-T2-starts ⇒ smaller commit timestamp; single Paxos state machine
  per tablet; writes initiate Paxos at leader; reads from any sufficiently-up-to-date replica; 10s time-based leader
  leases; 2PC over Paxos; commit wait `TT.after(si)`; Bigtable eventually-consistent contrast); Paxos Made Simple
  (asynchronous non-Byzantine model; value chosen by a majority; any two majorities intersect; safety properties;
  progress needs a distinguished proposer + randomness/real time, citing FLP); Raft USENIX ATC 2014 (majority votes →
  leader, AppendEntries replication, entry committed once replicated on a majority, Log Matching, Leader Completeness,
  replicated-state-machine framing). Herlihy/Wing TOPLAS 1990 and Dynamo SOSP 2007 remain `[UNVERIFIED from fetched
  source]` (network-blocked); MIT 6.5840 notes blocked, supporting context only.
- CAP/partitions/PACELC + distributed-commit cluster anchors, factchecked in `_factcheck_cluster4.md`: Gray & Lamport
  "Consensus on Transaction Commit" ACM TODS 2006 (fetched tech-report PDF from
  `lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`) verifies — 2PC blocks if the coordinator
  fails; non-blocking-commit definition; classic 3PC split-brain/no-proven-correctness critique; 2PC cost `3N-1`/four
  message delays (`3N-3`/three co-located); stable-storage durability; Paxos Commit uses `2F+1` coordinators, progress
  with `F+1`; consensus lower bound `2F+1` to tolerate `F` without synchrony; Paxos safety under multiple leaders;
  **2PC = degenerate `F=0` Paxos Commit (single acceptor)**. Spanner OSDI 2012 (cached) verifies 2PC-over-Paxos,
  two-phase locking for RW txns, snapshot-isolation read-only txns, commit wait. CAP (Gilbert/Lynch 2002, Brewer
  2000/2012) and PACELC (Abadi 2012) remain `[UNVERIFIED from fetched source]` — academic/ACM hosts network-blocked
  this session (only `lamport.azurewebsites.net` resolved).
- **11 is now reconciled into `_research.md`** (four clusters, standard six sections). Remaining 11 gaps carried to
  Phase 2: fetch CAP/PACELC primaries (Gilbert/Lynch, Brewer, Abadi); Herlihy/Wing object-level linearizability;
  Dynamo SOSP 2007; Fidge/Mattern/Charron-Bost/CBCAST/DLS; Skeen 1981 original 3PC; Berenson 1995 ANSI isolation
  levels; cleaner Chandra-Toueg text; source pin for the `f+1` synchronous rotating-coordinator claim; and re-pin
  Gray & Lamport to ACM TODS 2006 pagination.

### 12 research-papers-for-engineers
- Reading-method cluster, factchecked in `_factcheck_phase1.md`: verified backbone is Lamport, "State the Problem
  Before Describing the Solution" (`lamport.azurewebsites.net/pubs/state-the-problem.pdf`, full text extracted) —
  flawed-vs-urged paper organization, correctness-conditions-stated-independently-of-the-solution, comprehension !=
  correctness. Keshav "How to Read a Paper" CCR 2007 (three-pass, five Cs, citation-convergence survey) and
  Roscoe/Mitzenmacher/Smith reviewing guidance remain `[UNVERIFIED from fetched source]` (HTTP 000 across 5 mirrors).
- Canon cluster, factchecked in `_factcheck_phase1.md`: FOUR fresh Lamport primaries verified from
  `lamport.azurewebsites.net/pubs/` — Byzantine Generals (`byz.pdf`: oral `>2/3` loyal / `3m+1`, signed any number,
  conditions A/B, impossibility-then-`OM(m)`), Reaching Agreement (`reaching.pdf`: `n>=3m+1` iff, interactive
  consistency, omission faults arbitrary `n>=m>=0`), Part-Time Parliament (`lamport-paxos.pdf`: original Paxos,
  state-machine approach, majority for progress, editor's-note exposition-failure exemplar). Agreement chain
  (Reaching Agreement -> Byzantine -> PTP -> Paxos Made Simple -> Raft) is the verified teaching spine; canon already
  verified in 06-11 is reused. Remaining gaps `[UNVERIFIED]` (fetch before Phase 2): Keshav/Roscoe/Mitzenmacher/Smith;
  MapReduce/GFS/Bigtable/Dynamo; Dapper/Tail-at-Scale/Chubby/ZooKeeper; Herlihy/Wing, End-to-End, Lampson Hints.
  12 is now reconciled into `_research.md` (two clusters, six sections). Opportunistic 11-primary retry stayed HTTP 000.

## Wave 5 — Part II System Design begins (sub-course 13 started)

### 13 scaling-fundamentals
- Cluster A anchor file: `13-scaling-fundamentals/_research_back-of-envelope-latency-queueing.md`
  + `_factcheck_clusterA.md`. The capacity *method/math* is VERIFIED BY RECOMPUTATION this
  session (Python): Little's Law `L=λW` (distribution-free, area derivation); M/M/1
  `L=ρ/(1−ρ)`, `W=S/(1−ρ)`, utilization wall `W/S=1/(1−ρ)` (ρ=.5→2×,.8→5×,.9→10×,.95→20×,.99→100×);
  Amdahl `1/((1−p)+p/N)`, ceiling `1/(1−p)` (p=.95→20×); USL
  `C(N)=N/(1+α(N−1)+βN(N−1))`, knee `N*=√((1−α)/β)`; fan-out tail `1−(1−q)^N`
  (q=.01,N=100→63%). Memory-hierarchy + 64B cache-line + false-sharing canon REUSED from
  verified 01 (CS:APP ch.6) and 06 (Disruptor/RocksDB `bloom_impl.h`) rather than re-fetched.
- Network reality (4th consecutive session): only `lamport.azurewebsites.net` + Walmart
  artifactory (PyPI / github-*releases*) resolve. Blocked `[UNVERIFIED from fetched source]`
  Cluster-A primaries to fetch when network heals: Jeff Dean "Latency Numbers Every Programmer
  Should Know" (jboner gist 2841832 / Colin Scott interactive page / Stanford-295 talk PDF —
  the exact ns/ms table); Drepper "What Every Programmer Should Know About Memory"
  (akkadia.org / LWN 2007); Little 1961 (Operations Research); Kleinrock *Queueing Systems v1*
  (M/M/1, M/G/1 / Pollaczek–Khinchine); Amdahl 1967 (AFIPS); Gunther *Guerrilla Capacity
  Planning* (USL); Dean & Barroso "The Tail at Scale" CACM 2013 (also in 12 canon). Do NOT
  harden any exact latency number into Phase-2 prose until fetched.
- **13 is now RECONCILED** (`13-scaling-fundamentals/_research.md`, six sections) on the basis
  of FOUR factchecked clusters (A–D), 0 factcheck blockers. Added this session:
  - Cluster B — `_research_bottlenecks-use-method.md`: USE method (Utilization/Saturation/
    Errors per resource), resource-vs-workload analysis, sampling profilers, flame graphs
    (width = cost, x-axis = merged stacks NOT time), on/off-CPU = all of `W`, "bottleneck
    moves" corollary. Saturation is the operational face of the `1/(1−ρ)` queue from Cluster A.
  - Cluster C — `_research_horizontal-vertical-akf-cube.md`: scale up (Amdahl/USL/physics cap)
    vs. scale out (passes ceiling, owes 11's coordination = USL `β`); statelessness as the
    lever that relocates state (session→token/cache, durable→DB(14), hot reads→cache(16));
    AKF Scale Cube X (clone) / Y (functional split) / Z (shard by key), orthogonal+composable;
    axis→downstream handoffs (X→10/15, Y→17/19, Z→14/15).
  - Cluster D — `_research_load-testing-capacity-planning.md`: open vs. closed load models
    (closed self-limits `N=X·R`; open can overload; internet ≈ open); coordinated omission
    (Tene) VERIFIED BY RECOMPUTATION this session (Python): naive closed measurement of
    9999×1 ms + 1×1000 ms gives p99.9 = 1.0 ms, but CO-corrected back-fill gives p99.9 ≈ 989 ms
    (~3 orders of magnitude understatement); percentile/histogram discipline (merge HDR
    histograms, never average percentiles); capacity loop (find bottleneck → measure wall
    open+CO-corrected → target ρ with headroom → size via Little's Law → re-test).
  - Factcheck: `13-scaling-fundamentals/_factcheck_clusterBCD.md` (B/C/D logic verified by
    recomputation + reuse of 01/06/10/11/Cluster-A; 0 blockers).
- Blocked `[UNVERIFIED from fetched source]` B/C/D primaries (network HTTP 000, 5th consecutive
  session — `brendangregg.com`, `akfpartners.com`, Tene/HdrHistogram/wrk2 hosts, NSDI 2006):
  Gregg "The USE Method" + flame-graph pages + _Systems Performance_; RED method
  (Wilkie/Weaveworks); Linux PSI `/proc/pressure`; AKF "Scale Cube" + Abbott&Fisher _The Art
  of Scalability_; Twelve-Factor factor VI; Fowler microservices/distributed-monolith; Gil Tene
  "How NOT to Measure Latency"; HdrHistogram `recordValueWithExpectedInterval`; `wrk2`;
  Schroeder/Wierman/Harchol-Balter "Open Versus Closed" (NSDI 2006); Harchol-Balter
  _Performance Modeling..._. Do NOT harden any attribution/exact wording into Phase-2 prose
  until fetched. Cross-link down into appendix N-math-for-systems for full queueing/probability
  derivations and B-linux-internals for the actual USE counters. Next Phase-1 batch: **14–21**.
