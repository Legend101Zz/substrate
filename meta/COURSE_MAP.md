
# Course map (seed — Phase 2 turns this into a full dependency DAG + per-chapter specs)

The headline is **System Design + Agentic System Design**. Everything else is a
foundation sub-course (00–12) that the headline draws on, or a deep reference appendix
(A–O) that sub-courses cross-link into. Two-tier by design: spine teaches transferable
CONCEPTS + build labs; appendices go infinitely deep on a REAL SYSTEM, info-only.

## Part 0 — Orientation
- 00-how-to-use-this-course   (agent-paired learning prompts; the map; how to read this)

## Part I — Foundations (spine; concepts + build labs where they fit)
- 01-computers-from-first-principles      (0s/1s → logic gates → ALU → CPU → ISA)
- 02-terminal-shell-and-dev-environment   (shell, processes, pipes, tooling) [lab: own shell]
- 03-networking-from-first-principles     (links → IP → TCP → TLS → HTTP) [lab: own TCP/IP]
- 04-operating-systems-internals          (processes, memory, scheduling, fs, syscalls)
- 05-programming-language-runtime-internals (parsing, bytecode, VMs, GC, JIT — generic)
- 06-data-structures-for-systems          (B-trees, LSM, bloom, skiplist, ring buffer, HLL, consistent hashing)
- 07-database-internals                   (storage, indexes, query exec, txns) [lab: own DB]
- 08-caches-and-storage-systems           (cache strategies, eviction, write paths)
- 09-message-queues-logs-and-kafka        (the log abstraction, partitions, delivery) [lab: own MQ]
- 10-nginx-proxies-and-load-balancing     (reverse proxy, LB algos, event-driven servers) [lab: own HTTP server/LB]
- 11-distributed-systems-foundations      (time, replication, consensus, CAP, partitioning)
- 12-research-papers-for-engineers        (how to read a paper + walkthroughs of the canon)

## Part II — System Design (headline 1; concepts + design case studies as labs)
- 13-scaling-fundamentals                 (latency numbers, back-of-envelope, bottlenecks)
- 14-data-modeling-partitioning-sharding
- 15-replication-and-consistency-in-practice
- 16-caching-and-cdn-strategies
- 17-async-queues-and-event-driven-architecture
- 18-rate-limiting-backpressure-and-load-shedding   (SEDA)
- 19-observability-tracing-and-slos                 (Dapper)
- 20-resilience-failure-and-capacity-planning        (The Tail at Scale)
- 21-design-case-studies                            (URL shortener, feed, chat, search, payments, rate limiter…)

## Part III — Agentic System Design (headline 2; concepts + harness build track)
- 22-the-agent-loop                       (call → observe → decide → repeat)
- 23-tools-and-tool-contracts
- 24-prompts-and-context-engineering
- 25-memory-short-term-long-term-and-safety
- 26-state-persistence-and-resume
- 27-planning-and-multi-agent-orchestration  (supervisor, fan-out, teams, dynamic workflows)
- 28-build-your-own-coding-harness          [lab: capstone harness — loop→tools→memory→subagents→budgets→compaction]
- 29-mcp-skills-and-connectors
- 30-rag-retrieval-and-grounding
- 31-evaluation-tracing-and-guardrails
- 32-cost-observability-and-ops
- 33-safety-and-proactive-self-evolving-agents
- 34-design-your-own-agentic-system         (the capstone design canvas)

## Appendices (A–O; reference-grade DEEP info only, NO exercises)
- A-computer-architecture                  (NAND→CPU, real ISAs)
- B-linux-internals
- C-python-internals
- D-javascript-v8-nodejs-internals
- E-java-jvm-internals
- F-postgres-internals
- G-redis-internals
- H-kafka-internals
- I-docker-containers-cgroups-namespaces
- J-kubernetes-internals
- K-compilers-interpreters-and-jit
- L-consensus-replication-and-transactions
- M-ai-agent-memory-tools-and-evaluation
- N-math-for-systems                       (queueing/Little's Law, probability, hashing math, HLL/bloom math)
- O-cloud-infra-basics

## Candidate additions (propose in Phase 2; add only via an ADR)
- P-search-engines-and-indexing   - Q-columnar-and-time-series-storage   - R-security-and-cryptography-basics

## Build labs index (/build; spine references these)
own-shell · own-tcp-ip-stack · own-database · own-redis · own-git · own-docker ·
own-http-server-and-load-balancer · own-message-queue · own-interpreter/compiler ·
own-coding-agent-harness (capstone)
