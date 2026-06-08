
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
