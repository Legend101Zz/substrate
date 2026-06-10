
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
