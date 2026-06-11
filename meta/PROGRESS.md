# Progress

Resume anchor. Every session begins by reading this file.
State enum: TODO → RESEARCHING → PLANNED → DRAFTING → REVIEW → DONE

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
| 21 | design-case-studies | TODO | Phase 1 batch 2 (NEXT — finishes Part II) | — |
| 22 | the-agent-loop | TODO | Phase 1 batch 3 | — |
| 23 | tools-and-tool-contracts | TODO | Phase 1 batch 3 | — |
| 24 | prompts-and-context-engineering | TODO | Phase 1 batch 3 | — |
| 25 | memory-short-term-long-term-and-safety | TODO | Phase 1 batch 3 | — |
| 26 | state-persistence-and-resume | TODO | Phase 1 batch 3 | — |
| 27 | planning-and-multi-agent-orchestration | TODO | Phase 1 batch 3 | — |
| 28 | build-your-own-coding-harness | TODO | Phase 1 batch 3 | — |
| 29 | mcp-skills-and-connectors | TODO | Phase 1 batch 3 | — |
| 30 | rag-retrieval-and-grounding | TODO | Phase 1 batch 3 | — |
| 31 | evaluation-tracing-and-guardrails | TODO | Phase 1 batch 3 | — |
| 32 | cost-observability-and-ops | TODO | Phase 1 batch 3 | — |
| 33 | safety-and-proactive-self-evolving-agents | TODO | Phase 1 batch 3 | — |
| 34 | design-your-own-agentic-system | TODO | Phase 1 batch 3 | — |
| A | computer-architecture | TODO | Phase 1 batch 4 (appendices) | — |
| B | linux-internals | TODO | Phase 1 batch 4 | — |
| C | python-internals | TODO | Phase 1 batch 4 | — |
| D | javascript-v8-nodejs-internals | TODO | Phase 1 batch 4 | — |
| E | java-jvm-internals | TODO | Phase 1 batch 4 | — |
| F | postgres-internals | TODO | Phase 1 batch 4 | — |
| G | redis-internals | TODO | Phase 1 batch 4 | — |
| H | kafka-internals | TODO | Phase 1 batch 4 | — |
| I | docker-containers-cgroups-namespaces | TODO | Phase 1 batch 4 | — |
| J | kubernetes-internals | TODO | Phase 1 batch 4 | — |
| K | compilers-interpreters-and-jit | TODO | Phase 1 batch 4 | — |
| L | consensus-replication-and-transactions | TODO | Phase 1 batch 4 | — |
| M | ai-agent-memory-tools-and-evaluation | TODO | Phase 1 batch 4 | — |
| N | math-for-systems | TODO | Phase 1 batch 4 | — |
| O | cloud-infra-basics | TODO | Phase 1 batch 4 | — |

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
