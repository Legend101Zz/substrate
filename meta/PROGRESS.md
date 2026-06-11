# Progress

Resume anchor. Every session begins by reading this file.
State enum: TODO → RESEARCHING → PLANNED → DRAFTING → REVIEW → DONE

> **Phase status:** Phase 1 (research corpus) COMPLETE for all 50 units. Phase 2 (per-sub-course
> `_structure.md`) COMPLETE for the 35 spine units (00–34). Appendices A–O are reference-only and
> carry NO `_structure.md` by design (ADR-003) — their bespoke shape lives in `<appendix>/_research.md`.
> **Awaiting Phase-2 sign-off before any chapter drafting (Phase 3).** No prose written.

## Phase-2 per-chapter table (spine 00–34 → PLANNED; appendices A–O → RECONCILED, reference-only)

`secs` = number of chapter/section specs in that unit's `_structure.md` (the drafting unit of work).
Full provenance + `[UNVERIFIED]` carry-forward per unit is preserved in the detailed archive below.

| id | title | state | secs | lab | next action |
|----|-------|-------|------|-----|-------------|
| 00 | how-to-use-this-course | PLANNED | 6 | — | Phase 3: `_plan.md` written — STOP for annotation before draft |
| 01 | computers-from-first-principles | PLANNED | 7 | — | Phase 3: `_plan.md` written — STOP for annotation before draft |
| 02 | terminal-shell-and-dev-environment | PLANNED | 7 | own-shell | Phase 3: draft on go |
| 03 | networking-from-first-principles | PLANNED | 8 | own-tcp-ip-stack | Phase 3: draft on go (ADR-002 lab choice) |
| 04 | operating-systems-internals | PLANNED | 9 | — | Phase 3: draft on go |
| 05 | programming-language-runtime-internals | PLANNED | 9 | own-interpreter | Phase 3: draft on go |
| 06 | data-structures-for-systems | PLANNED | 8 | — | Phase 3: draft on go |
| 07 | database-internals | PLANNED | 8 | own-database | Phase 3: draft on go |
| 08 | caches-and-storage-systems | PLANNED | 8 | own-redis | Phase 3: draft on go |
| 09 | message-queues-logs-and-kafka | PLANNED | 9 | own-message-queue | Phase 3: draft on go |
| 10 | nginx-proxies-and-load-balancing | PLANNED | 8 | own-http-server-and-lb | Phase 3: draft on go |
| 11 | distributed-systems-foundations | PLANNED | 8 | — | Phase 3: draft on go |
| 12 | research-papers-for-engineers | PLANNED | 6 | — | Phase 3: draft on go |
| 13 | scaling-fundamentals | PLANNED | 10 | — | Phase 3: draft on go |
| 14 | data-modeling-partitioning-sharding | PLANNED | 9 | — | Phase 3: draft on go |
| 15 | replication-and-consistency-in-practice | PLANNED | 10 | — | Phase 3: draft on go |
| 16 | caching-and-cdn-strategies | PLANNED | 7 | — | Phase 3: draft on go |
| 17 | async-queues-and-event-driven-architecture | PLANNED | 10 | — | Phase 3: draft on go |
| 18 | rate-limiting-backpressure-and-load-shedding | PLANNED | 8 | — | Phase 3: draft on go |
| 19 | observability-tracing-and-slos | PLANNED | 7 | — | Phase 3: draft on go |
| 20 | resilience-failure-and-capacity-planning | PLANNED | 8 | — | Phase 3: draft on go |
| 21 | design-case-studies | PLANNED | 8 | (case studies) | Phase 3: draft on go — Part II capstone |
| 22 | the-agent-loop | PLANNED | 6 | own-coding-agent-harness s0 | Phase 3: draft on go |
| 23 | tools-and-tool-contracts | PLANNED | 6 | harness s1 | Phase 3: draft on go |
| 24 | prompts-and-context-engineering | PLANNED | 7 | harness s3 | Phase 3: draft on go |
| 25 | memory-short-term-long-term-and-safety | PLANNED | 7 | harness s4 | Phase 3: draft on go |
| 26 | state-persistence-and-resume | PLANNED | 7 | harness s5 | Phase 3: draft on go |
| 27 | planning-and-multi-agent-orchestration | PLANNED | 7 | harness s6 | Phase 3: draft on go |
| 28 | build-your-own-coding-harness | PLANNED | 6 | own-coding-agent-harness | Phase 3: draft on go — Part III capstone LAB |
| 29 | mcp-skills-and-connectors | PLANNED | 7 | harness +MCP | Phase 3: draft on go |
| 30 | rag-retrieval-and-grounding | PLANNED | 8 | harness +RAG | Phase 3: draft on go |
| 31 | evaluation-tracing-and-guardrails | PLANNED | 7 | harness +trust | Phase 3: draft on go |
| 32 | cost-observability-and-ops | PLANNED | 7 | harness +cost | Phase 3: draft on go |
| 33 | safety-and-proactive-self-evolving-agents | PLANNED | 6 | harness +safety | Phase 3: draft on go |
| 34 | design-your-own-agentic-system | PLANNED | 6 | design canvas | Phase 3: draft on go — Part III capstone DESIGN |
| A–O | appendices (15) | RECONCILED | n/a | reference-only | Reference-grade; NO `_structure.md` by design (ADR-003) |

**Spine secs total = 264 chapter/section specs across 35 units** (the Phase-3 drafting backlog).

---

## Detailed provenance archive (Phase 1 — per-unit research/factcheck/recompute state; DO NOT prune)

| id | title | state | next action | owner |
|----|-------|-------|-------------|-------|
| 00 | how-to-use-this-course | TODO | Phase 2 design | — |
| 01 | computers-from-first-principles | RESEARCHING | Wave 1 briefs + factcheck report done; residual book/JS-rendered Eater/Scott/Petzold gaps logged | brain |
| 02 | terminal-shell-and-dev-environment | RESEARCHING | Wave 1 briefs + factcheck fixes done; keep glibc posix_spawn wording version-qualified | brain |
| 03 | networking-from-first-principles | RESEARCHING | Wave 1 briefs + factcheck fixes done; residual QUIC adoption/CPU and Sponge Lab 4 source gaps logged | brain |
| 04 | operating-systems-internals | RESEARCHING | Wave 2 briefs reconciled + factcheck blockers patched; residual source gaps logged | brain |
| 05 | programming-language-runtime-internals | RESEARCHING | Wave 2 briefs reconciled + factcheck blockers patched; residual moving-target runtime caveats logged | brain |
| 06 | data-structures-for-systems | RESEARCHING | Wave 2 briefs reconciled + factcheck blockers patched; residual blocked-paper gaps logged | brain |
| 07 | database-internals | RESEARCHING | Wave 3 07 briefs drafted, factchecked, blockers patched, and reconciled into `_research.md`; residual paper/source gaps logged | brain |
| 08 | caches-and-storage-systems | RESEARCHING | Phase 1 briefs deepened, factchecked via `_factcheck_phase1.md`, and reconciled into `_research.md`; residual taxonomy/source pinning gaps logged | brain |
| 09 | message-queues-logs-and-kafka | RESEARCHING | Phase 1 briefs deepened, factchecked via `_factcheck_phase1.md`, blockers patched, and reconciled into `_research.md`; residual Kafka paper/KIP/source-tracing gaps logged | brain |
| 10 | nginx-proxies-and-load-balancing | RESEARCHING | Phase 1 core briefs drafted, factchecked via `_factcheck_phase1.md`, blockers patched, and reconciled into `_research.md`; residual TLS/HTTP2/HTTP3/reuseport/docs wording gaps logged | brain |
| 11 | distributed-systems-foundations | RESEARCHING | Four clusters drafted/factchecked (time/clocks, vector-clocks/taxonomy, consistency/replication/quorums, CAP/partitions+distributed-commit) and reconciled into `_research.md`; residual CAP/PACELC/Herlihy-Wing/Dynamo/Skeen/ANSI-isolation primary gaps logged | brain |
| 12 | research-papers-for-engineers | RESEARCHING | Two clusters drafted/factchecked (reading-method + canon-walkthroughs) and reconciled into `_research.md`; 4 fresh Lamport primaries verified (Byzantine, Reaching Agreement, Part-Time Parliament, State-the-Problem); residual Keshav + storage-trilogy (MapReduce/GFS/Bigtable/Dynamo/Dapper/Tail) `[UNVERIFIED]` gaps logged | brain |
| 13 | scaling-fundamentals | RESEARCHING | FOUR clusters drafted/factchecked (A back-of-envelope/queueing, B USE/bottlenecks, C horiz-vert/AKF cube, D load-testing/coordinated-omission) and RECONCILED into `_research.md`; all math verified by recomputation; Dean/Drepper/Gregg/AKF/Tene empirical+historical attributions `[UNVERIFIED]` network-blocked (carried forward) | brain |
| 14 | data-modeling-partitioning-sharding | RESEARCHING | THREE clusters drafted/factchecked (A data modeling, B partitioning/sharding, C cross-partition ops) and RECONCILED into `_research.md`; all math verified by recomputation (mod-N vs consistent-hashing movement, hot-shard skew, fan-out tail, scatter throughput); 06/07/08/11/13 canon reused; Codd/Bigtable/Dynamo/Karger/Sagas/MapReduce/DDIA/vendor-doc attributions `[UNVERIFIED]` network-blocked (carried forward) | brain |
| 15 | replication-and-consistency-in-practice | RESEARCHING | FOUR clusters drafted/factchecked (A topologies+log, B lag anomalies+fixes, C conflicts+quorum-tuning, D failover/split-brain/real-systems) and RECONCILED into `_research.md`; quorum/staleness/failure-tolerance math VERIFIED by recomputation (W+R>N overlap, P(stale), majority tolerance); 06/07/11/13/14 canon reused; DDIA/Dynamo/Bayou/CRDT/CAP-PACELC/vendor-doc attributions `[UNVERIFIED]` network-blocked (carried forward) | brain |
| 16 | caching-and-cdn-strategies | RESEARCHING | FOUR clusters drafted/factchecked (A placement+patterns, B eviction+sizing, C consistency+invalidation, D CDN+edge) and RECONCILED into `_research.md`; all sizing/stampede math VERIFIED by recomputation; 03/06/08/10/13/14/15 canon reused; **UPGRADE 2026-06-10: RFC 9111/5861/7234/4786 + Nishtala NSDI 2013 FETCHED+VERIFIED (net healed) -> see `_factcheck_phase1.md` §F; also clears matching 08 attributions**; Breslau/XFetch/CMS/ARC/vendor-CDN still `[UNVERIFIED]` | brain |
| 17 | async-queues-and-event-driven-architecture | RESEARCHING | FOUR clusters drafted/factchecked (A messaging-models+delivery-semantics, B EDA-patterns, C producer/consumer-mechanics+failure, D delivery-infra+tradeoffs) and RECONCILED into `_research.md`; 6 math claims VERIFIED by recomputation (`_recompute.py`: dup certainty N*p, dedup-window=redelivery-horizon, batching tput 1/(c/B+m)->1/m, retention vs compaction floor, parallelism<=partitions, dual-write window); 09/11/13/14/15/16/06/08/03 canon reused; Nishtala NSDI'13 FETCHED+verified (leases 17K->1.3K herd, mcsqueal CDC delete-stream); AMQP/SQS/Kafka-KIP/Sagas-1987/Fowler-CQRS/Kreps-2011 attributions `[UNVERIFIED]` carried forward | brain |
| 18 | rate-limiting-backpressure-and-load-shedding | RESEARCHING | FOUR clusters drafted/factchecked (A rate-limiting algorithms, B backpressure/SEDA, C load-shedding/retry-storms, D timeouts/breakers/bulkheads/hedging/adaptive-concurrency) and RECONCILED into `_research.md`; 9 math claims VERIFIED by recomputation (`_recompute.py`: bucket sizing, fixed-window 2x boundary, sliding log-vs-counter, distributed over-admit (cells-1)*batch, bounded-queue Q/drain, retry amplification 1/(1-r), goodput collapse, adaptive-throttle p); PRIMARIES fetched+verified RFC 6585 §4 + Google SRE Handling-Overload + Cascading-Failures; 03/11/13/14/15/16/17/10 canon reused; SEDA/CoDel/Hystrix/GCRA/AWS-builders attributions `[UNVERIFIED]` (still blocked) | brain |
| 19 | observability-tracing-and-slos | RESEARCHING | FOUR clusters drafted/factchecked (A metrics/signal-taxonomy, B distributed-tracing/Dapper, C logs-events/three-pillars, D SLI/SLO/error-budgets/burn-rate) and RECONCILED into `_research.md`; 28/28 math VERIFIED by recomputation (`_recompute.py`: error-budget=(1-SLO)*window, burn_rate=P*period/window {36,14.4,6,1}, threshold=burn*(1-SLO), naive-window precision trap, 1/12 short windows, sampling RSE, cardinality 60->60M); PRIMARIES fetched+verified Dapper-2010 + SRE Ch.4 SLO + Ch.6 Monitoring + Workbook Ch.5 Alerting; 11/13/16/17/09/03/10/18 canon reused; OpenTelemetry/W3C-trace-context/exemplars/RED-credit/tail-sampling attributions `[UNVERIFIED]` carried forward | brain |
| 20 | resilience-failure-and-capacity-planning | RESEARCHING | FOUR clusters drafted/factchecked (A failure-models/partial-failure, B the-tail-at-scale, C resilience-patterns/cells/shuffle-sharding/chaos, D capacity/reliability-math) and RECONCILED into `_research.md`; 38/38 math VERIFIED by recomputation (`_recompute.py`: fan-out 1-0.99^100=0.634, hedge overhead=1-deadline-pct, hedged tail~p^2, Dean 994/50=19.88x, tied -43%/-38%, plain 1/K, C(8,2)=28/1/28/7x, C(2048,4)=730.9B, full-collision 1/C(n,k), overlap k^2/n, util-wall 2/5/10/20x, headroom C=D/rho*, USL knee 98.49, serial prod(a_i)=0.99501, parallel 1-(1-a)^n, CORRELATED-FAILURE 6-nines->3-nines 1001x, headroom f/n N+1/N+2, Little's-Law->5 servers, retry amp (1+r)^L=1024x); PRIMARIES fetched+verified Tail-at-Scale + AWS shuffle-sharding + AWS backoff/jitter + Brewer PODC2000 CAP + Kleppmann CAP + Netflix Simian Army; 11/12/13/14/15/16/18/19 canon reused; Nygard/Avizienis/Fallacies/CoDel(403)/Raft(000)/Gilbert-Lynch attributions `[UNVERIFIED]` carried | brain |
| 21 | design-case-studies | RECONCILED | Phase 1 CAPSTONE of Part II done — six case-study briefs (URL shortener, news feed, chat, search/typeahead, payments/ledger, distributed rate limiter), `_recompute.py` 32/32 back-of-envelope estimates verified, `_factcheck_phase1.md` (0 blockers), reconciled `_research.md` (bespoke per-case structure + cross-cutting design-method spine + toolkit-usage matrix). Gilbert-Lynch formal CAP + Abadi PACELC FETCHED+VERIFIED (Case 5); applies 13-20 toolkit, no new primitives. **Part II (13-21) COMPLETE.** | brain |
| 22 | the-agent-loop | RECONCILED | Phase 1 batch 3 OPENED — control-loop walkthrough (call→observe→decide→repeat); ReAct (arXiv 2210.03629) FETCHED+VERIFIED; `_recompute.py` 18/18 (quadratic token growth, budgets, window exhaustion); `_factcheck_phase1.md` 0 blockers; reconciled `_research.md`. Reuses 04/09/13/17/18/20. Carry-forward `[UNVERIFIED]`: CoT (arXiv 2201.11903), Reflexion, provider docs | brain |
| 23 | tools-and-tool-contracts | RECONCILED | Tool = contract between stochastic caller & deterministic code; Toolformer (arXiv 2302.04761) FETCHED+VERIFIED (four decisions which/when/what-args/how-incorporate); `_recompute.py` 15/15 (toolbox tax K·S, retrieval break-even, result budget, repair bound, selection compounding 1-(1-q)^N); `_factcheck_phase1.md` 0 blockers; reconciled `_research.md`. Reuses 03/07/17/18/22. Carry-forward `[UNVERIFIED]`: provider function-calling specs, JSON Schema, MCP (→29) | brain |
| 24 | prompts-and-context-engineering | RECONCILED | Refines the "assemble context" box; context = a fixed budget to engineer. CoT (arXiv 2201.11903) FETCHED+VERIFIED (format/ORDER changes capability: SST-2 54.3%->93.4% on exemplar permutation). `_recompute.py` 18/18 — HEADLINE: **compaction converts 22's O(T²)->O(T)** (cap transcript at C, summarize); + window budget, few-shot cost, prefix-cache discount, placement band. `_factcheck_phase1.md` 0 blockers; reconciled `_research.md`. Reuses 06/08/16/13/18/22/23. Carry-forward `[UNVERIFIED]`: Lost-in-the-Middle (2307.03172), provider prompt-caching specs, prompt-injection (→33) | brain |
| 25 | memory-short-term-long-term-and-safety | RECONCILED | What 24's compactor externalizes to; memory = OS storage hierarchy over tokens. MemGPT (arXiv 2310.08560) + Reflexion (arXiv 2303.11366) FETCHED+VERIFIED (virtual context mgmt = paging; main vs external context; episodic memory as learning signal). `_recompute.py` 13/13 (tier partition, 0.1% resident, recall cost, **AMAT over tokens**, consolidation O(T) disk, poisoning blast radius 1-write-many-reads, eviction sizing). `_factcheck_phase1.md` 0 blockers; reconciled `_research.md`. Reuses 04/06/08/16/09/15/22/23/24. Carry-forward `[UNVERIFIED]`: vector retrieval (→30), memory vendor frameworks, injection-via-memory (→33) | brain |
| 26 | state-persistence-and-resume | RECONCILED | Transcript = a Write-Ahead Log; agent resume IS DB crash recovery. PostgreSQL WAL docs FETCHED+VERIFIED (log-before-data; flush-on-commit; roll-forward/REDO) — receipt `_VERIFIED_2026-06-10_postgres-wal.md` (also confirms 07/15 WAL). `_recompute.py` 12/12 (write-ahead loss bound ≤1 step, **checkpoint knee I*=√(2N·c)**, RTO, idempotent replay 17/21, fsync/group-commit, replication quorum 15). `_factcheck_phase1.md` 0 blockers; reconciled `_research.md`. Reuses 07/09/15/17/20/22/24/25. Carry-forward `[UNVERIFIED]`: Temporal/Step-Functions/DBOS, LangGraph checkpointer, ARIES (Mohan 1992) | brain |
| 27 | planning-and-multi-agent-orchestration | RECONCILED | One loop → many; a multi-agent system IS a distributed system (laws = 11/13/17/20). No new load-bearing primary (applies the toolkit, like 21). `_recompute.py` 16/16 (plan size W^D, **Amdahl over agents** ceiling 1/s, **join tail 1-(1-p)^N=63.4%@N=100**, aggregation tax N·r, **error compounding + majority-of-3 voting 6.9× better**, payoff/YAGNI condition, C(N,2) conflict pairs). `_factcheck_phase1.md` 0 blockers; reconciled `_research.md`. Reuses 09/11/13/14/15/17/18/20/22/24/25/26. Carry-forward `[UNVERIFIED]`: planning papers (2305.04091/2205.10625/2305.10601), debate (2305.14325), MA frameworks | brain |
| 28 | build-your-own-coding-harness | RECONCILED | Phase 1 batch 3 — Part III CAPSTONE LAB; bespoke **BUILD PROGRESSION** (the "40-line agent" grown stage-by-stage, broken on purpose at each stage to motivate the next: loop22→tools23→budget(22/18/32)→compaction24→memory25→persistence26→orchestration27). NO new primary (capstone application, like 21). `_recompute.py` 31/31 (all 7 stage walls re-derived in the coding regime: O(T²) overflow sooner for code T*=83 vs 253; selection compounding; 1MB-file overflow; budget caps≠cures; compaction O(T²)→O(T) unbounded win; AMAT 4×; poisoning 1→15; checkpoint knee I*=20; idempotent replay; Amdahl/join-tail/YAGNI). `_factcheck_phase1.md` 0 blockers. Reuses 09/17/18/20/21/22/23/24/25/26/27. Carry `[UNVERIFIED]`: SWE-bench (2310.06770), coding-agent impls, sandbox/ACE (→App I), injection/poisoning (→33) | brain |
| 29 | mcp-skills-and-connectors | RECONCILED | Phase 1 batch 3 — 23's tool CONTRACT promoted to a wire PROTOCOL; bespoke protocol/connector walkthrough. **MCP architecture spec FETCHED+VERIFIED** (`mcp-arch.txt`, receipt `_VERIFIED_2026-06-10_mcp.md`): host/client/server; two layers; JSON-RPC 2.0 data layer; tools/resources/prompts + sampling/elicitation/logging + Tasks(durable exec); stdio vs Streamable-HTTP; lifecycle/capability negotiation; `*/list` + `list_changed`. `_recompute.py` 18/18 (N×M→N+M collapse; union-toolbox tax K·S; selection compounding; remote-dependency tail 1-(1-p)^s; version/schema compat). `_factcheck_phase1.md` 0 blockers. Reuses 02/03/07/11/17/18/19/20/22/23/24/26/28. Carry `[UNVERIFIED]`: formal /specification JSON-Schema (SPA shell), Agent-Skills depth, OAuth/auth, Registry/SEP, injection-via-server (→33) | brain |
| 30 | rag-retrieval-and-grounding | RECONCILED | Phase 1 batch 3 — the retrieval mechanism for 25's non-parametric memory tier; bespoke retrieval-pipeline walkthrough (corpus→chunk→embed→index→retrieve→rank→inject/ground). **RAG (Lewis et al. 2020, arXiv 2005.11401) FETCHED+VERIFIED** (`rag-2005.11401.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_rag.md`): parametric vs non-parametric memory; DPR bi-encoder; MIPS top-K sub-linear; FAISS+HNSW; latent-doc marginalize; cures hallucination + provenance + updatable knowledge. `_recompute.py` 15/15 (ANN-vs-scan ~430,000× at 10M; retrieve-vs-stuff budget; K precision/recall/cost knob; embedding cache 1000×; index staleness/lag). `_factcheck_phase1.md` 0 blockers. Reuses 06/07/08/14/15/16/22/23/24/25/28/29. Carry `[UNVERIFIED]`: DPR (2004.04906), FAISS/HNSW primaries, sparse/hybrid/rerank, RAG eval (→31), GraphRAG, injection-via-passage (→33) | brain |
| 31 | evaluation-tracing-and-guardrails | RECONCILED | Phase 1 batch 3 — the TRUST layer (does it work? / what did it do? / can it go off-rails?). Bespoke **trust-loop walkthrough** (Define correct→Measure offline→Grade un-gradeable→Watch live→Constrain inline→feed failures back). **SWE-bench (Jimenez/Yang et al., ICLR 2024, arXiv 2310.06770) FETCHED+VERIFIED** (`swe-bench-2310.06770.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_swe-bench.md`): execution-based "is it useful" — apply patch→run unit+system tests→all pass=resolved; metric=%resolved; tests-as-oracle (fail-to-pass+pass-to-pass); Claude-2 1.96%; lexical≠correctness; saturation motivation. Tracing REUSES local Dapper (19); judging REUSES 27 Condorcet; guardrails REUSE 18 defence-in-depth. `_recompute.py` **19/19** (binomial CI ~1067 tasks for ±3%; pass@k 0.936 vs pass^k 0.216; majority-of-3 judges 1.9–3.6×, backfires <0.5; 49 spans/run + sampling RSE; defence-in-depth 0.8% escape vs 5.9% over-refusal FP tax; lexical≠correct + %resolved; suite cost 837M tok = S·O(T²)). `_factcheck_phase1.md` 0 blockers. Reuses 13/18/19/20/22/23/24/25/27/28/30. **BONUS: SWE-bench fetch upgrades 28's carried `[UNVERIFIED]` → VERIFIED.** Carry `[UNVERIFIED]`: LLM-judge primary (MT-Bench/2306.05685)+bias taxonomy, SWE-bench-Verified/SWE-agent(2405.15793)/HumanEval, RAGAS, OTel-GenAI+W3C-trace-context, tail-based sampling, guardrail frameworks | brain |
| 32 | cost-observability-and-ops | RECONCILED | Phase 1 batch 3 — the 22 O(T²) economics made OPERATIONAL. Bespoke **cost-lifecycle walkthrough** (Account→Attribute→Budget/Cap→Optimize→Operate) = 19 observability + 18 control + 20 capacity denominated in $/tokens. **NO new primary** (operational synthesis like 21; prices already-VERIFIED mechanisms). `_recompute.py` **14/14** (cost O(T²) — doubling turns >2× bill, input term dominates; compaction O(T²)→O(T) saves ~$18.8/run@T=100, grows unbounded; prefix-cache 10× cheaper prefix but leaves quadratic; per-tenant quota=18 over $; cost tail mean 20× median, per-run cap cuts total 10×; cost=attributable signal LLM 80% of bill; model routing 70/30 → $1.04/M vs $3/M). `_factcheck_phase1.md` 0 blockers. Reuses 18/19/20/22/24/26/30/31. Carry `[UNVERIFIED]`: provider pricing/prompt-cache/batch specifics (illustrative knobs), FinOps, cost tooling (Helicone/Langfuse/OTel-GenAI), spot/commit infra (→App O) | brain |
| 33 | safety-and-proactive-self-evolving-agents | RECONCILED | Phase 1 batch 3 — the THREAT + EVOLUTION layer. Bespoke **threat-model → defence-in-depth → controlled-evolution walkthrough**. NEW primary **Greshake et al. Indirect Prompt Injection (AISec '23, arXiv 2302.12173) FETCHED+VERIFIED** (`greshake-injection-2302.12173.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_injection.md`): root cause "blur the line between data and instructions"; retrieved prompts = arbitrary code/API control; injection-method taxonomy (Passive/Active/User-driven/Hidden) + threat taxonomy (data-theft/fraud/intrusion/malware/manipulation/availability/**worming**) + persistence-via-memory + "Whack-A-Mole"/alignment-insufficient. Lands the carried injection `[UNVERIFIED]` pointers from 23/25/29/30 on ONE verified root cause. Self-evolution REUSES local Reflexion (2303.11366). `_recompute.py` 15/15 (blast-radius 1-write-many-reads; sandbox-as-cell 20×; defence-in-depth 0.8% escape vs 5.9% over-refusal; self-improve gated-by-31 / ungated reward-hacks; risk-based gate 20× cheaper; prompt-worm R0=2.0→0.5; composed defences multiply). `_factcheck_phase1.md` 0 blockers. Reuses 18/19/20/23/25/27/29/30/31/32. Carry `[UNVERIFIED]`: dual-LLM/CaMeL, Constitutional-AI(2212.08073)/RLHF(2203.02155), formal sandboxing(→App I), agent red-team benchmarks | brain |
| 34 | design-your-own-agentic-system | RECONCILED | Phase 1 batch 3 — PART III CAPSTONE DESIGN CANVAS (the agentic 21). Bespoke **forced-moves decision-tree / design canvas**. **NO new primary** (capstone application). Thesis: a design is a SEQUENCE OF FORCED MOVES — task shape + arithmetic pick the primitives (small forces {22}; big forces {22,24,33,26,27,31,32}). `_recompute.py` 13/13 (cross-cutting budget ledger: 22 O(T²); 24 compaction per-call-window vs cumulative-cost; 25 AMAT; 26 checkpoint knee I*=√(2N·c); 27 Amdahl/join-tail/YAGNI; 31 eval CI ≈1068; 32 $; 33 defence-per-channel). `_factcheck_phase1.md` 0 blockers; no NEW `[UNVERIFIED]` (inherits home-course gaps). Reuses 22-33. **PART III (22-34) COMPLETE.** | brain |
| A | computer-architecture | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **performance ladder** (the correct-but-slow CPU 01 built → each layer real HW adds to close the gap to peak: cache/AMAT → pipelining/hazards → branch prediction → superscalar/OOO/ILP → virtual memory/TLB → coherence). NO new primary (eater.net/CS:APP HTTP 000); reuses 01's line-verified nand2tetris+CS:APP+Eater reads + 06/13. `_recompute.py` **15/15** (two's-comp range+subtract-via-add; 5-stage pipe 4.98×; CPI 1+f·s; branch-mispredict CPI ∝ depth; superscalar IPC ceiling; AMAT 95%→6ns + locality cliff 3.5×; 64B line/stride; 4-level page table + 400ns TLB miss; 6-order latency ladder). Reuses 01/06/13/N. Carry `[UNVERIFIED]`: Hennessy-Patterson text, exact uarch (predictors/ROB/MESI tables), SAP-1 bit map (from 01) | brain |
| B | linux-internals | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **xv6-abstraction → Linux-reality → Linux-addition** diff (task/clone+COW → CFS/EEVDF → buddy/slab/page-cache → epoll/io_uring → **namespaces+cgroups substrate**). NO new primary (man7/kernel.org HTTP 000); reuses 04's line-verified xv6+TLPI+kernel-source reads + A. `_recompute.py` **14/14** (clone flag bitmask; COW 0-copy; CFS 1/n + nice^5≈3×; EEVDF deadline; MemFree-vs-MemAvailable; buddy order-5=128KB; epoll O(ready) 10000×; io_uring 256→1 syscall; cpu.max 50% + per-cgroup OOM; 8 namespaces; syscall ~100× call). Reuses 04/A/13/N + 03/10. **Establishes the ns+cgroups substrate for I/J.** Carry `[UNVERIFIED]`: kernel source/man-pages text, io_uring ring layout, exact CFS/EEVDF constants, NUMA/Spectre/THP depth | brain |
| C | python-internals | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **"life of a PyObject"** (header → refcount death → the GIL that protects the count → stack-VM eval loop that adapts itself (PEP 659) → cyclic GC for what refcount can't). NO new primary (docs.python.org/devguide 000); reuses 05's line-verified CPython source reads (object.h/ceval_gil.c/gc.c/InternalDocs) + appendix K. `_recompute.py` **15/15** (refcount cascade+tax; immortal savings; GIL CPU-vs-IO; EXTENDED_ARG; stack-VM 7; frame bump; specialize break-even+deopt; GC gen freq+700→2000; 2-cycle collect; int boxing). 0 blockers. | brain |
| D | javascript-v8-nodejs-internals | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **"one JS value through V8, one tick through the loop"** (hidden-class shape → inline-cache + 3 JIT tiers Ignition→Maglev→TurboFan → scavenger/mark-compact GC → libuv phases + microtasks). NO new primary (nodejs.org/v8.dev 000); reuses 05's line-verified V8+libuv source reads (map.h/feedback-vector.h/scavenger.h/core.c) + appendix K. `_recompute.py` **13/13** (shape sharing vs explosion; IC mono/poly/mega; register-VM 3; tier break-even+deopt; scavenger survivor-proportional; 4GB old-gen; libuv poll timeout; nextTick/microtask order; threadpool bound; minor-vs-major freq). 0 blockers. | brain |
| E | java-jvm-internals | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **"life of a class through the JVM"** (load → verify (StackMapTable single pass = security boundary) → link/init `<clinit>`-once → tier interp→C1→C2 + deopt → cross-cutting safepoints + G1/ZGC GC). NO new primary (docs.oracle.com/openjdk.org 000); reuses 05's line-verified HotSpot source reads (classFileParser/verifier/compilerDefinitions/safepoint/g1) + appendix K. `_recompute.py` **13/13** ((name,loader) distinct types; StackMapTable linear vs quad; <clinit> once; CompLevel ladder+break-even; C2 deopt; OSR; safepoint poll near-free+cooperative; G1 garbage-first; ZGC pause-vs-throughput; gen freq). 0 blockers. | brain |
| F | postgres-internals | RECONCILED | Phase 1 batch 4 (appendix) — "life of a row" pipeline (page→tuple→nbtree→cost-planner→executor→WAL→checkpoint→REDO recovery→MVCC→VACUUM/wraparound). NO new primary (postgresql.org HTTP 000); constants REUSED from 07's line-verified PostgreSQL master source + WAL intro (`postgres-wal-intro.txt`) VERIFIED verbatim (roll-forward/REDO; sequential log flush). `_recompute.py` 22/22→**14/14** (page density 64 tuples/100B; nbtree fanout 510→3-4 levels/1e9 rows; WAL 1 seq flush vs k random; checkpoint knee I*=√(2Nc); MVCC 1 dead version/update; XID wrap 2^31; planner seq-vs-index crossover ~0.5% w/ random=4×seq; hot-row 200tps; TOAST ~2KB). Reuses 06/07/15/26/L. Carry `[UNVERIFIED]`: MVCC heap detail (HOT/infomask/multixact/VM/FSM), VACUUM/freeze thresholds, WAL record format+FPW+replication slots, planner deep internals+JIT, exact TOAST threshold, ARIES (all pg.org/ACM blocked) | brain |
| G | redis-internals | RECONCILED | Phase 1 batch 4 (appendix) — "single-threaded in-memory machine" tier walkthrough (event loop→encodings→expiration→eviction→persistence→replication→cluster). **NEW primaries FETCHED+VERIFIED** (redis.io HTTP 200): eviction ("Approximated LRU", `maxmemory-samples 5`) + persistence (RDB point-in-time; AOF `appendfsync` everysec=1s loss/always=0/no=30s) — receipt `_VERIFIED_2026-06-11_redis-docs.md`. `_recompute.py` **14/14** (1M ops/s + O(N) 10ms HOL block; sampled LRU default 5; active expiry 20/loop, 25%/10%; durability windows; COW peak 2×; async-repl lost writes; 16384 slots/5461 per 3 nodes; listpack→hashtable @128). Reuses 06/08/16/L/15. Carry `[UNVERIFIED]`: `ae.c`/`networking.c` loop, encoding byte layouts (rax/listpack/quicklist/intset/skiplist; internals-rax 404), RESP grammar, cluster gossip+CRC16 poly, multi-part AOF 7.0 | brain |
| H | kafka-internals | RECONCILED | Phase 1 batch 4 (appendix) — "distributed-log machine" layer walkthrough (partitioned log→segments/retention/compaction→ISR replication→HW/epochs→groups/offsets→delivery→EOS/transactions→KRaft). NO new primary (kafka.apache.org HTTP 000; paper/KIP retry still owed); constants REUSED from 09's line-verified Kafka 3.9 source/docs + 17 delivery math + Nishtala herd. `_recompute.py` **13/13** (consumers≤partitions; segment unlink retention; RF=3/min.isr=2/acks=all tolerates 1; HW≤LEO; ISR f+1 vs majority 2f+1; offset=processed+1; 50 offsets partitions; dup certainty 1-(1-p)^N; idempotent pid/epoch/seq; EOS={records+offsets} not external; herd 13×). Reuses 09/17/11/15/L+Nishtala. Carry `[UNVERIFIED]`: Kafka paper (kafka.apache.org 000), KIPs (98/101/500/848/360), KRaft deep internals+ELR, fetch-from-follower, txn recovery+sticky assignor | brain |
| I | docker-containers-cgroups-namespaces | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **"there is no container" teardown** (a container = process + namespaces[SEE] + cgroups[USE] + overlayfs[RUN ON] + caps/seccomp[DO]; then reassemble by hand in ~4 syscalls). NO new primary (docs.docker.com HTTP 000); reuses just-reconciled B's ns+cgroups substrate + 04/A/03. `_recompute.py` **12/12** (VM-vs-ctr ~100× overhead + ms-vs-s start; 4-primitive composition; overlay RO+writable + 100MB copy-up; layer dedup 5.5×; cpu.max 25% throttle; memory.max per-ctr OOM; net-ns/veth :80; seccomp ~44/350; ~4-syscall hand-roll; PID-1 reaping). Reuses B/04/A/03/13/N. Forward-links to J. Carry `[UNVERIFIED]`: docker/OCI/runc/containerd docs+source, seccomp denylist size, overlayfs internals, rootless/gVisor-Kata | brain |
| J | kubernetes-internals | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **"loops all the way down"** (K8s = reconciliation loops over appendix I's container unit at every layer: store→schedule→run→expose→heal→roll). NO new primary (kubernetes.io/etcd HTTP 000); reuses appendix I + spine 11/15/20 + L. `_recompute.py` **13/13** (reconcile convergence + level-trigger; etcd Raft quorum 3→tol1/5→tol2/odd; scheduler request-fit→Pending; requests-vs-limits QoS; pod shared net+ipc ns; Service ~1/N; liveness→restart/readiness→de-route; rolling maxSurge/maxUnavail ≥8 Ready; apiserver fan-out 63.4%; async convergence lag; node-failure ~300s grace). Reuses I/B/11/15/20/L/10/03/13/N. **Closes the B→I→J arc.** Carry `[UNVERIFIED]`: k8s/etcd docs+source, Borg paper, object semantics, version-dependent constants, CNI/CSI/APF/operators | brain |
| K | compilers-interpreters-and-jit | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **3-stage + JIT pipeline** (front-end lex/parse → stack-vs-register VM → middle-end SSA opt → back-end codegen/regalloc → JIT profile/specialize/guard/deopt). NO new primary (llvm.org/gcc.gnu.org HTTP 000); reuses 05's line-verified CPython/V8/HotSpot/Crafting-Interpreters reads + 06. `_recompute.py` **15/15** (stack 7 vs register 3 instrs; AST 1000 vs bytecode 32 misses; JIT break-even N*=500; IC O(1) vs dict probe; const-fold/strength-reduce/inline; graph-coloring spills 20>16; deopt expected-cost 0.15 vs 25; EXTENDED_ARG encoding). Reuses 05/06/N. Feeds C/D/E. Carry `[UNVERIFIED]`: LLVM/GCC text, Chaitin/Cytron/Pratt papers, exact JIT thresholds | brain |
| L | consensus-replication-and-transactions | RECONCILED | Phase 1 batch 4 (appendix) — fault-model ladder (crash n≥2f+1 → Byzantine n≥3f+1 → quorum W+R>N → CAP/PACELC → 2PC/commit-wait → isolation). **NEW: Lamport Paxos + Byzantine Generals FETCHED+VERIFIED** (receipt `_VERIFIED_2026-06-11_consensus.md`); upgrades 12's Byzantine/Paxos `[UNVERIFIED]`→VERIFIED. `_recompute.py` 22/22. Reuses 07/11/14/15 + Dynamo/Spanner/Gilbert-Lynch/Brewer/Kleppmann/Abadi. Carry `[UNVERIFIED]`: Raft (raft.github.io 000), FLP, PBFT, Skeen 3PC | brain |
| M | ai-agent-memory-tools-and-evaluation | RECONCILED | Phase 1 batch 4 (appendix) — primitive-by-primary catalogue (memory→tools→reasoning→retrieval→evaluation→safety); reference companion to Part III spine. NO new primary (all 7 already local+VERIFIED: MemGPT/Reflexion/Toolformer/ReAct/RAG/SWE-bench/Greshake). `_recompute.py` 17/17. Reuses 22/23/25/27/30/31/33 + 06/N. Carry `[UNVERIFIED]`: DPR(2004.04906)/FAISS-HNSW, MT-Bench(2306.05685), SWE-agent(2405.15793), CaMeL/Constitutional-AI/RLHF | brain |
| N | math-for-systems | RECONCILED | Phase 1 batch 4 (appendix) — formula compendium by question (queueing/capacity→hashing/probabilistic→tail/availability→statistics). NO new primary (standard results RE-DERIVED, not asserted; Tail-at-Scale reused). `_recompute.py` 20/20 (Little; M/M/1; 1/(1−ρ) wall; birthday; consistent-hashing K/N; Bloom k*=(m/n)ln2; HLL 1.04/√m; fan-out 63.4%; availability; Amdahl/USL; eval CI 1068). Reuses 06/07/08/13/14/15/17/18/19/20/27/31. Carry `[UNVERIFIED]`: original-paper attributions (Little/Bloom/Flajolet/Karger/Amdahl/Gunther) — not load-bearing (recomputed) | brain |
| O | cloud-infra-basics | RECONCILED | Phase 1 batch 4 (appendix) — bespoke **"cloud = five rented planes"** (compute/storage/network/identity/control-plane), each a managed instance of a spine primitive + a meter + a blast-radius map. Vendor-neutral; NO vendor number load-bearing (all vendor docs 000); reuses spine 13 (Little/1−ρ/latency hierarchy) + 20 (A=1−(1−a)^n/serial/correlated-collapse) + 15/L (consistency) + appendices I/J. `_recompute.py` **14/14** (FaaS cold-start amort; autoscale ⌈L/μ⌉+1; durability parallel-redundancy; replica staleness vs commit-wait; CDN edge save; multi-AZ correlation collapse; serial avail; util knee; egress asymmetry; IaC idempotence; storage hierarchy; domain nesting; control/data split; compute ladder). 0 blockers. | brain |

---

## Canon-fetch upgrade note (2026-06-10, Wave 7 — network heal)

Opportunistic primaries fetched + verified to `meta/fetched_primaries/` (receipt
`_VERIFIED_2026-06-10_canon.md`) and applied as UPGRADE sections in the relevant factcheck files
(carry-forward `[UNVERIFIED]` -> VERIFIED; nothing erased):
- **Tail at Scale** CACM 2013 -> 13 (tail/fan-out, straggler), 18D (hedged/tied), 20 (headline), 12.
- **Dynamo** SOSP 2007 (`R+W>N` verbatim + sloppy quorum/hinted handoff/Merkle/read-repair/vnodes)
  -> 15, 14, 06 (consistent hashing), 11, 12.
- **MapReduce** OSDI 2004, **Bigtable** OSDI 2006, **GFS** SOSP 2003, **Spanner** OSDI 2012
  -> 14, 15, 11, 12 (canon walkthroughs).
Deep per-paper factchecks deferred to each sub-course's Phase 2; terms + one load-bearing quote per
paper verified verbatim this session. Still blocked: SEDA SOSP'01, CoDel ACM Queue'12, CAP/PACELC,
Herlihy-Wing, Bayou, CRDTs, Keshav, Codd, Kafka paper/KIPs, all vendor docs.

## Wave 8 (2026-06-10) — 19 reconciled + SEDA finally unblocked

- **19 observability-tracing-and-slos RECONCILED** (Part II SEVENTH sub-course; four clusters
  A-D). The sensing half of the control loop whose actuating half is 18: signals (Four Golden
  Signals, error-budget burn, queue depth, retry ratio, breaker state, latency percentiles)
  drive 18's controllers. Primaries fetched + verified to `meta/fetched_primaries/`:
  - **Dapper** (Google TR dapper-2010-1, 2010): `dapper-2010.{pdf,txt}` — span/trace tree,
    span name/id/parent id + 64-bit trace id, two-host RPC spans, thread-local + async context
    propagation, clock-skew via send-before-receive bounds, 1/1024 + adaptive sampling,
    overhead 204/176/9/40 ns + Table 2, out-of-band Bigtable collection median <15 s.
  - **SRE Book Ch.4** (`sre_slo.txt`): SLI/SLO/SLA, percentiles>means, 100% wrong, "few SLOs".
  - **SRE Book Ch.6** (`sre_monitoring.txt`): Four Golden Signals; black-box vs white-box.
  - **SRE Workbook Ch.5** (`sre_workbook_alerting.txt`): burn-rate + multiwindow multi-burn-rate
    canon (2%/1h/14.4, 5%/6h/6, 10%/3d/1; 1/12 short window; iterations 1->6).
  - All math RECOMPUTED in `19.../_recompute.py` (28/28 pass). Receipt:
    `meta/fetched_primaries/_VERIFIED_2026-06-10_observability.md`. **ALL of 01-19 reconciled.**
- **SEDA finally unblocked (BONUS):** `https://www.sosp.org/2001/papers/welsh.pdf` HTTP 200
  (blocked 8+ sessions). Fetched + verified `seda-sosp01.{pdf,txt}`; carry-forward `[UNVERIFIED]`
  in 18 Cluster B upgraded -> VERIFIED (stage=handler+bounded-queue+thread-pool+controller;
  well-conditioned=graceful degradation; dynamic controllers). UPGRADE appended to
  `18-.../_factcheck_phase1.md`; nothing erased.
- Network at session end: NEW HTTP 200 = research.google Dapper mirror, sre.google chapters,
  sosp.org + people.eecs.berkeley.edu (SEDA), martin.kleppmann.com (CAP blog, deferred),
  usenix.org/legacy (osdi04/osdi06 mirrors). STILL blocked: queue.acm.org 403 (CoDel),
  raft.github.io 000, arxiv, dl.acm, postgresql.org, kafka.apache.org, eecs.harvard.edu
  (SEDA path 404 — use sosp.org/berkeley instead), aws.amazon.com builders'.
- **20-21 remain untouched.**

## Wave 9 (2026-06-10) — 20 reconciled + CAP primaries (Brewer/Kleppmann) unblocked

- **20 resilience-failure-and-capacity-planning RECONCILED** (Part II EIGHTH sub-course; the
  synthesis course — four clusters A-D). Takes 18's overload controls + 19's signals/SLOs/error-
  budgets and turns them into a discipline for surviving partial failure + planning capacity.
  All 38/38 math RECOMPUTED in `20.../_recompute.py`. Headline result: the **correlated-failure
  correction** collapses naive six-nines parallel redundancy to ~three nines (1001x worse
  unavailability) — correlation, not replica count, sets real availability.
- **PRIMARIES fetched + verified to `meta/fetched_primaries/`** (receipt
  `_VERIFIED_2026-06-10_resilience.md`): Dean & Barroso Tail-at-Scale (already local); AWS
  Builders' "Workload isolation using shuffle-sharding" (C(8,2)=28->1/28->7x; Route 53 2048-choose-4
  ~730B); AWS Builders' "Timeouts, retries, backoff with jitter"; Brewer PODC 2000 CAP keynote;
  Kleppmann "Please stop calling databases CP or AP" (2015); Netflix "Simian Army".
- **CAP UPGRADE (bonus):** Brewer PODC 2000 + Kleppmann 2015 HTTP 200 (blocked for 8+ sessions).
  Upgraded carry-forward CAP `[UNVERIFIED]` -> VERIFIED in 11 (`_factcheck_cluster4.md`) and 15
  (`_factcheck_phase1.md`): "at most two" of {C,A,P}, Forfeit C/A/P, BASE, CAP-as-narrow-theorem.
  **Gilbert-Lynch 2002 formal proof + Abadi 2012 PACELC remain blocked/carried forward.**
- Network at session end: NEW HTTP 200 = aws.amazon.com builders' library, people.eecs.berkeley.edu
  (Brewer PODC), martin.kleppmann.com, netflixtechblog.com. STILL blocked: queue.acm.org 403
  (CoDel), raft.github.io 000, arxiv, dl.acm, postgresql.org, kafka.apache.org. **ALL of 01-20 now
  reconciled. Only 21 (design-case-studies) remains to finish Part II.**

## Wave 10 (2026-06-10) — 21 reconciled = PART II COMPLETE + Gilbert-Lynch/Abadi PACELC unblocked

- **21 design-case-studies RECONCILED** (Part II CAPSTONE; ninth and final Part-II sub-course).
  Introduces NO new primitives — it APPLIES the entire 13-20 toolkit to six concrete designs via a
  **bespoke per-case-study structure** (not abstract clusters): URL shortener, news feed/timeline,
  chat/messaging, web search/typeahead, payments/ledger, distributed rate limiter. Artifacts:
  `_case_url-shortener.md`, `_case_news-feed.md`, `_case_chat-messaging.md`,
  `_case_search-typeahead.md`, `_case_payments-ledger.md`, `_case_rate-limiter.md`,
  `_recompute.py` (32/32 back-of-envelope estimates pass), `_factcheck_phase1.md` (0 blockers),
  `_research.md` (RECONCILED: design-method spine + toolkit-usage matrix + cross-case
  reconciliations). Every QPS/storage/keyspace/cache/shard/fan-out-tail estimate RECOMPUTED;
  mechanisms REUSED from line-verified 06/09/11/12/13-20.
- **CAP/PACELC UPGRADE (Wave 10 — finally unblocked):** `groups.csail.mit.edu` (Gilbert-Lynch
  "Perspectives on the CAP Theorem" 2012) + `cs.umd.edu/~abadi` (Abadi PACELC 2012) HTTP 200.
  Fetched + text-extracted (throwaway uv venv + pypdf, removed after) + verified verbatim to
  `meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_cap-pacelc.md`). Upgraded carry-forward
  `[UNVERIFIED]` -> VERIFIED in 11 (`_factcheck_cluster4.md`: formal CAP = safety-vs-liveness
  impossibility on an atomic register, CAP⇒no-consensus-under-partition) and 15
  (`_factcheck_phase1.md`: PACELC "if P: A-vs-C; else: L-vs-C", PA/EL vs PC/EC vs PC/EL); also
  anchors 21 Case 5 payments. Nothing erased. NOTE: the original 2002 SIGACT News PDF specifically
  is still separately unfetched (the 2012 retrospective restates its formalization) — non-blocking.
- Network at session end: NEW HTTP 200 = groups.csail.mit.edu (Gilbert-Lynch), cs.umd.edu (Abadi),
  **arxiv.org, kafka.apache.org, postgresql.org** (200 but deferred to next session — time-boxed).
  STILL blocked: queue.acm.org 403 (CoDel), raft.github.io 000, dl.acm.org 403 (DOI landing).
  **ALL of 01-21 now reconciled — PART II (System Design, 13-21) IS COMPLETE. Next batch: Part III
  Agentic System Design (22-the-agent-loop onward), per COURSE_MAP "Phase 1 batch 3".**

## Wave 11 (2026-06-10) — Part III OPENED: 22 + 23 reconciled ("Phase 1 batch 3")

- **PART III Agentic System Design BEGUN.** First two sub-courses reconciled with bespoke
  (non-four-cluster) structures, the same recompute+factcheck discipline as 13-21:
  - **22 the-agent-loop** — the FOUNDATIONAL primitive: an agent is a CONTROL LOOP around an LLM
    (assemble→call→parse→act→observe→append→decide). Bespoke single-loop walkthrough. Primary
    **ReAct (Yao et al., ICLR 2023, arXiv 2210.03629) FETCHED+VERIFIED** (Thought/Action/Observation
    interleaving; acting grounds reasoning, cures CoT hallucination; +34%/+10% with 1-2 exemplars).
    `_recompute.py` 18/18 — headline: **input tokens are O(T²)** (`T*p + g*T*(T-1)/2`) because the
    transcript is re-sent and grows every turn; this quadratic motivates 24/25/32. Also: cost,
    step/cost/time budgets, window-exhaustion turn `T*=floor((W-p)/g)+1`, per-step retry. Each loop
    box maps to a downstream sub-course (the Part III dependency spine). Reuses 04/09/13/17/18/20.
  - **23 tools-and-tool-contracts** — a tool is an **API contract between a stochastic caller and
    deterministic code**. Bespoke contract walkthrough (schema→selection→validation/repair→
    execution→failure→security). Primary **Toolformer (Schick et al., NeurIPS 2023, arXiv
    2302.04761) FETCHED+VERIFIED** (the four decisions: which/when/what-args/how-incorporate; tools
    offload arithmetic/lookup; self-supervised baking vs in-context use). `_recompute.py` 15/15 —
    toolbox tax K·S/turn (feeds 22's quadratic), retrieval-over-tools break-even (→30), tool-result
    size budget, repair-retry bound, selection-error compounding `1-(1-q)^N` (the 13/20/21 identity
    over loop steps), idempotency retention (17/21). Reuses 03/07/08/16/17/18/22.
- **PRIMARIES fetched+verified to `meta/fetched_primaries/`** (network heal): ReAct + Toolformer
  arXiv PDFs + extracted text; receipt `_VERIFIED_2026-06-10_agentic.md`. Extraction used a throwaway
  `/tmp/pdfx-venv` (uv + pypdf 6.13.2 from Walmart external-pypi), REMOVED after; `.code-puppy-venv`
  never touched.
- Network at session end: arxiv.org / kafka.apache.org / postgresql.org / modelcontextprotocol.io
  (307) all reachable. STILL blocked: queue.acm.org 403 (CoDel), raft.github.io 000, dl.acm.org 403.
- **Deferred (time-boxed to keep ONE clean checkpoint over shallow briefs):** 24-34 untouched;
  opportunistic Kafka(09/17)/Postgres(07/15) upgrades NOT done this session (arxiv was spent on the
  load-bearing 22/23 primaries). 30 RAG primary (Lewis 2020, arXiv 2005.11401) + MCP spec + CoT
  (arXiv 2201.11903) noted for next session.
- **Next batch: 24-prompts-and-context-engineering** (refines the "assemble context" box; forced by
  22's quadratic + 23's toolbox tax), then 25 memory, 26 resume, 27 orchestration, ... through 34.

## Wave 12 (2026-06-10) — Part III batch 3 continued: 24, 25, 26, 27 reconciled

- **FOUR more agentic sub-courses reconciled** (24-27), all bespoke (non-four-cluster) structures,
  same recompute+factcheck discipline as 13-23. Part III now stands at **22-27 done (6 of 13)**.
  - **24 prompts-and-context-engineering** — refines the "assemble context" box; context = a fixed
    budget to engineer (allocate/compress/place). Primary **CoT (arXiv 2201.11903) FETCHED+VERIFIED**
    (prompts = programming-by-example; format allocates compute; exemplar ORDER swings SST-2
    54.3%→93.4%; emergent ~100B; style-robust). `_recompute.py` 18/18 — HEADLINE: **compaction
    converts 22's O(T²)→O(T)** (cap transcript at ceiling C, summarize); I* trigger; compaction
    ratio/payoff; prefix-cache discount (helps prefix, NOT the quadratic); placement/"lost-in-the-
    middle" band. Reuses 06/08/16/13/18/22/23.
  - **25 memory-short-term-long-term-and-safety** — what 24's compactor externalizes to; memory =
    OS storage hierarchy over tokens. Primaries **MemGPT (arXiv 2310.08560) + Reflexion (arXiv
    2303.11366) FETCHED+VERIFIED** (virtual context mgmt = paging between "physical memory and
    disk"; main vs external context; function-call pagers; episodic memory buffer as a learning
    signal w/o weight updates; 91% vs 80% HumanEval). `_recompute.py` 13/13 — **AMAT over tokens**
    (hit 0.80→0.95 cuts effective cost 4×), 0.1% resident, consolidation O(T) on disk, **poisoning
    blast radius** (1 write, ~15 reads). Reuses 04/06/08/16/09/15/22/23/24.
  - **26 state-persistence-and-resume** — the agent transcript IS a Write-Ahead Log; resume IS DB
    crash recovery. **PostgreSQL WAL docs FETCHED+VERIFIED** (log-before-data; flush-on-commit;
    roll-forward/REDO) — receipt `_VERIFIED_2026-06-10_postgres-wal.md` (corroborates 07/15 WAL,
    already source-verified in 07 via bufpage.h). `_recompute.py` 12/12 — write-ahead loss ≤1 step,
    **checkpoint knee I*=√(2N·c_ckpt)**, RTO, idempotent replay (17/21), fsync/group-commit,
    replication quorum (15). Reuses 07/09/15/17/20/22/24/25.
  - **27 planning-and-multi-agent-orchestration** — one loop → many; **a multi-agent system is a
    distributed system** (laws = 11/13/17/20). No new load-bearing primary (applies the toolkit,
    like 21's capstone). `_recompute.py` 16/16 — plan size W^D, **Amdahl over agents** (ceiling
    1/s), **join tail 1-(1-p)^N=63.4%@N=100**, aggregation tax N·r (compact → 6.7× less),
    **error compounding + majority-of-3 voting 6.9× better**, payoff/YAGNI condition (multi-agent
    LOSES on small tasks), C(N,2) conflict pairs. Reuses 09/11/13/14/15/17/18/20/22/24/25/26.
- **PRIMARIES fetched+verified to `meta/fetched_primaries/`**: cot-2201.11903, memgpt-2310.08560,
  reflexion-2303.11366 (.pdf+.txt; receipt appended to `_VERIFIED_2026-06-10_agentic.md`),
  postgres-wal-intro.txt (receipt `_VERIFIED_2026-06-10_postgres-wal.md`). Extraction via the same
  throwaway `/tmp/pdfx-venv` (uv+pypdf); `.code-puppy-venv` untouched.
- Network at session end: arxiv.org / kafka.apache.org / postgresql.org reachable (200);
  modelcontextprotocol.io 308. STILL blocked: queue.acm.org 403 (CoDel), raft.github.io 000.
- **Deferred (time-boxed):** 28-34 untouched. Opportunistic Kafka(09/17) upgrade NOT done (Postgres
  WAL done). 30 RAG primary (Lewis 2020, arXiv 2005.11401) + MCP spec (29) noted for next session.
- **Next batch: 28-build-your-own-coding-harness** (the capstone lab assembling loop→tools→context→
  memory→persistence→orchestration→budgets/compaction), then 29 MCP, 30 RAG (fetch 2005.11401),
  31 eval, 32 cost, 33 safety, 34 design-your-own.

## Wave 13 (2026-06-10) — Part III batch 3 continued: 28, 29, 30 reconciled (MCP + RAG fetched/verified)

- **THREE more agentic sub-courses reconciled** (28-30), all bespoke (non-four-cluster) structures,
  same recompute+factcheck discipline as 13-27. Part III now stands at **22-30 done (9 of 13)**.
  - **28 build-your-own-coding-harness** — Part III CAPSTONE LAB; bespoke **BUILD PROGRESSION** (the
    "40-line agent" grown stage-by-stage, **broken on purpose** at each stage to motivate the next:
    loop22→tools23→budget(22/18/32)→compaction24→memory25→persistence26→orchestration27). NO new
    primary (capstone application, like 21 — every mechanism cross-links to an already-VERIFIED
    anchor). `_recompute.py` 31/31 — all 7 stage walls re-derived in the CODING regime (bigger
    p=4000,g=1500): O(T²) overflows SOONER for code (T*=83 vs chat 253); selection compounding;
    1MB-file overflow; budget caps≠cures; compaction O(T²)→O(T) win grows unbounded; AMAT 4×;
    poisoning 1→15; checkpoint knee I*=20; idempotent replay; Amdahl/join-tail/YAGNI.
    `_factcheck_phase1.md` 0 blockers. Reuses 09/17/18/20/21/22/23/24/25/26/27.
  - **29 mcp-skills-and-connectors** — 23's tool CONTRACT promoted to a wire PROTOCOL; bespoke
    protocol/connector walkthrough. **MCP architecture spec FETCHED+VERIFIED** (host/client/server;
    two layers; JSON-RPC 2.0; tools/resources/prompts + sampling/elicitation/logging + Tasks; stdio
    vs Streamable-HTTP; lifecycle/capability negotiation; `*/list` + `list_changed`). `_recompute.py`
    18/18 (N×M→N+M collapse; union-toolbox tax; selection compounding; remote-dependency tail
    1-(1-p)^s; version/schema compat). `_factcheck_phase1.md` 0 blockers. Reuses
    02/03/07/11/17/18/19/20/22/23/24/26/28.
  - **30 rag-retrieval-and-grounding** — the retrieval mechanism for 25's non-parametric memory
    tier; bespoke retrieval-pipeline walkthrough. **RAG (Lewis et al. 2020, arXiv 2005.11401)
    FETCHED+VERIFIED** (parametric vs non-parametric memory; DPR bi-encoder; MIPS top-K sub-linear;
    FAISS+HNSW; latent-doc marginalize; cures hallucination + provenance + updatable knowledge).
    `_recompute.py` 15/15 (ANN-vs-scan ~430,000× at 10M; retrieve-vs-stuff budget; K
    precision/recall/cost knob; embedding cache 1000×; index staleness/lag). `_factcheck_phase1.md`
    0 blockers. Reuses 06/07/08/14/15/16/22/23/24/25/28/29.
- **PRIMARIES fetched+verified to `meta/fetched_primaries/`**: `mcp-arch.txt` (receipt
  `_VERIFIED_2026-06-10_mcp.md`), `rag-2005.11401.{pdf,txt}` (receipt `_VERIFIED_2026-06-10_rag.md`).
  RAG PDF extracted via the throwaway `/tmp/pdfx-venv` (uv+pypdf 6.13.2), REMOVED after;
  `.code-puppy-venv` never touched.
- Network at session end: arxiv.org / kafka.apache.org / postgresql.org reachable (200);
  modelcontextprotocol.io 307→200. STILL blocked: queue.acm.org 403 (CoDel), raft.github.io 000.
- **Deferred (time-boxed to keep ONE clean checkpoint over shallow briefs):** 31-34 untouched.
  Opportunistic Kafka(09/17) upgrade NOT done (the two plan-mandated primaries MCP+RAG were the
  budget). CoDel/raft retried, still blocked.
- **Next batch: 31-evaluation-tracing-and-guardrails** (↔ 19 observability/Dapper + 27 voting/critic
  + 18 guardrails), then 32 cost-observability-and-ops, 33 safety-and-proactive-self-evolving-agents,
  34 design-your-own-agentic-system. No chapters. No Phase 2.

## Wave 14 (2026-06-10) — Part III batch 3 continued: 31 + 32 reconciled (SWE-bench fetched/verified; 28 upgraded)

- **TWO more agentic sub-courses reconciled** (31, 32), both bespoke (non-four-cluster), same
  recompute+factcheck discipline as 13-30. Part III now stands at **22-32 done (11 of 13)**.
  - **31 evaluation-tracing-and-guardrails** — the TRUST layer. Bespoke **trust-loop walkthrough**
    (Define correct → Measure offline → Grade the un-gradeable → Watch live → Constrain inline →
    feed failures back). **SWE-bench (Jimenez/Yang et al., ICLR 2024, arXiv 2310.06770)
    FETCHED+VERIFIED** — the execution-based "is it useful" definition owed from 28/30 (apply
    patch → run unit+system tests → all pass = resolved; metric = % resolved; tests-as-oracle;
    Claude-2 1.96%; lexical≠correctness; saturation). Tracing REUSES local Dapper (19); LLM-as-judge
    REUSES 27's Condorcet majority-of-3; guardrails REUSE 18's defence-in-depth. `_recompute.py`
    **19/19** (binomial CI ~1067 tasks for ±3%; pass@k 0.936 vs pass^k 0.216; majority-of-3 judges
    1.9–3.6× fewer errors + backfires <0.5; 49 spans/run + Dapper sampling RSE; defence-in-depth
    0.8% escape vs 5.9% over-refusal FP tax; lexical≠correct + %resolved; suite cost 837M tok =
    S·O(T²)). `_factcheck_phase1.md` 0 blockers. Reuses 13/18/19/20/22/23/24/25/27/28/30.
  - **32 cost-observability-and-ops** — the 22 O(T²) economics made OPERATIONAL. Bespoke
    **cost-lifecycle walkthrough** (Account → Attribute → Budget/Cap → Optimize → Operate) = 19
    observability + 18 control + 20 capacity denominated in $/tokens. **NO new primary**
    (operational synthesis like 21; prices already-VERIFIED mechanisms). `_recompute.py` **14/14**
    (cost O(T²); compaction O(T²)→O(T) saves ~$18.8/run@T=100; prefix-cache 10× cheaper prefix but
    leaves the quadratic; per-tenant quota = 18 over $; cost tail mean 20× median, per-run cap cuts
    total 10×; cost = attributable signal, LLM 80% of bill; model routing 70/30 → $1.04/M vs $3/M).
    `_factcheck_phase1.md` 0 blockers. Reuses 18/19/20/22/24/26/30/31.
- **PRIMARY fetched+verified to `meta/fetched_primaries/`**: `swe-bench-2310.06770.{pdf,txt}`
  (52 pp, receipt `_VERIFIED_2026-06-10_swe-bench.md`). Extracted via the throwaway `/tmp/pdfx-venv`
  (uv+pypdf from Walmart external-pypi), REMOVED after; `.code-puppy-venv` never touched.
- **BONUS upgrade:** SWE-bench fetch cleared **28**'s carried `[UNVERIFIED]` SWE-bench note →
  VERIFIED (annotated in `28-.../_factcheck_phase1.md`; nothing erased).
- Network at session end: arxiv.org / kafka.apache.org / postgresql.org reachable (200). STILL
  blocked: queue.acm.org 403 (CoDel), raft.github.io 000 (retried).
- **Deferred (time-boxed to keep ONE clean checkpoint over shallow briefs):** 33-34 untouched.
  Opportunistic Kafka(09/17) upgrade NOT done (SWE-bench was the load-bearing budget this session).
  33 likely wants its own fetched primary (prompt-injection / sandboxing / alignment-oversight) and
  34 is the Part-III capstone canvas — both deserve careful treatment, not a rushed pass.
- **Next batch: 33-safety-and-proactive-self-evolving-agents** (prompt-injection via tool-result/
  memory/retrieved-passage carried from 23/25/29/30; sandboxing/ACE; self-improvement loops
  Reflexion 25; alignment/oversight), then **34-design-your-own-agentic-system** (the Part III
  CAPSTONE DESIGN CANVAS, applies all of 22-33 the way 21 applied 13-20; NO new primary). Finishing
  33+34 COMPLETES Part III (22-34) and thus the agentic-design spine. No chapters. No Phase 2.

## Wave 15 (2026-06-10) — Part III batch 3 COMPLETE: 33 + 34 reconciled — PART III (22-34) DONE

- **NOTE on baseline:** the launch prompt described the Wave-13 state ("22-30 reconciled; 31 NEXT
  untouched"), but disk/PROGRESS showed Wave 14 had already reconciled **31 + 32**. Per the
  constitution ("never guess — rehydrate from PROGRESS.md") the brain proceeded with the TRUE next
  untouched sub-course **33**, then **34**, and reported the discrepancy.
- **33 safety-and-proactive-self-evolving-agents RECONCILED** (the THREAT + EVOLUTION layer; bespoke
  threat-model → defence-in-depth → controlled-evolution walkthrough). NEW primary **Greshake et al.
  Indirect Prompt Injection (AISec '23, arXiv 2302.12173) FETCHED+VERIFIED** — settles the root
  cause ("data IS instructions") and the no-silver-bullet stance. The carried FORWARD injection
  `[UNVERIFIED]` pointers from 23/25/29/30 all land here on one verified root cause. Self-evolution
  REUSES local Reflexion (2303.11366). `_recompute.py` 15/15. Reuses 18/19/20/23/25/27/29/30/31/32.
- **34 design-your-own-agentic-system RECONCILED** (PART III CAPSTONE DESIGN CANVAS, the agentic 21;
  bespoke forced-moves decision-tree). **NO new primary**. `_recompute.py` 13/13 (cross-cutting
  budget ledger over 22/24/25/26/27/31/32/33). Reuses 22-33.
- **PRIMARY fetched+verified to `meta/fetched_primaries/`:** `greshake-injection-2302.12173.{pdf,txt}`
  (receipt `_VERIFIED_2026-06-10_injection.md`). Extracted via throwaway `/tmp/pdfx-venv` (uv+pypdf);
  `~/.code-puppy-venv` NEVER touched.
- `_recompute.py` tallies across Part III: **18/15/18/13/12/16/31/18/15/19/14/15/13** (22→34).
- **PART III (Agentic System Design, 22-34) is COMPLETE.** With 01-12 (Part I) + 13-21 (Part II)
  complete, the **entire Phase-1 spine corpus (01-34) is DONE.**
- opportunistic: Kafka doc fetch returned a thin JS-rendered shell (not a usable primary; discarded).
  CoDel (queue.acm.org 403) + raft.github.io (000) retried, still blocked. DPR (2004.04906) not
  fetched (time-boxed; non-load-bearing).
- **Next batch: Phase 1 batch 4 — the Appendices (A-O)**, OR move to Phase 2 (`_structure.md`, which
  STOPS for sign-off). No chapters yet.
