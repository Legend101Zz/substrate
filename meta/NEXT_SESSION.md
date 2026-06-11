# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 (21 reconciled — **PART II System Design (13-21) COMPLETE**; six capstone case-study briefs applying the 13-20 toolkit; Gilbert-Lynch formal CAP + Abadi PACELC fetched+verified and upgraded into 11 & 15) · Phase: 1 (deep research) · Harness: **code-puppy**

---

## Code Puppy recovery note (still relevant)

Start from the shorter Desktop path first:

```bash
cd /Users/m0t0hu6/Desktop/substrate
pwd
uvx code-puppy -i
```

Physical path may resolve through OneDrive:
`/Users/m0t0hu6/Library/CloudStorage/OneDrive-WalmartInc/Desktop/substrate`.

If `os.getcwd()` / `Path.cwd()` raises:

```text
PermissionError: [Errno 1] Operation not permitted
```

then **do not** edit or reinstall anything under `/Users/m0t0hu6/.code-puppy-venv`. Stop and tell the
user to grant the terminal/Code Puppy process Desktop/OneDrive access in macOS Privacy settings, or copy the repo
to a non-OneDrive workspace and continue there.

---

## Things DONE

- **Phase 1 / Wave 10 — 21 design-case-studies RECONCILED = PART II (System Design, 13-21) COMPLETE.**
  CAPSTONE application course (NO new primitives): six per-case-study briefs applying the 13-20
  toolkit — `_case_url-shortener.md`, `_case_news-feed.md`, `_case_chat-messaging.md`,
  `_case_search-typeahead.md`, `_case_payments-ledger.md`, `_case_rate-limiter.md`; `_recompute.py`
  (32/32 back-of-envelope estimates pass); `_factcheck_phase1.md` (0 blockers); `_research.md`
  (RECONCILED: 6-step design-method spine + toolkit-usage matrix + cross-case reconciliations).
  Gilbert-Lynch formal CAP + Abadi PACELC fetched+verified (Case 5 payments) and upgraded into 11 &
  15 (carry-forward `[UNVERIFIED]` -> VERIFIED; receipt `_VERIFIED_2026-06-10_cap-pacelc.md`).
- **Phase 0** — scaffold + constitution files + subagent personas + living-state files; git initialized.
- **Phase 1 / Wave 1 — 01, 02, 03 researched and reconciled.** Factcheck report
  `meta/factcheck_wave1_01-03.md` exists; fixes were applied in milestone commit `4a1cc71`. Residual gaps remain
  logged and must not be erased.
- **Phase 1 / Wave 2 — 04, 05, 06 researched, reconciled, and factchecked.** Factcheck report
  `meta/factcheck_wave2_04-06.md` exists; blockers were patched in milestone commit `4a1cc71`. Residual gaps remain
  logged.
- **Phase 1 / Wave 3 — 07, 08, and 09 researched, factchecked, and reconciled.** Artifacts include each sub-course's
  cluster briefs, `_factcheck_phase1.md`, and `_research.md`.
- **Phase 1 / Wave 4 / 10 nginx-proxies-and-load-balancing — core coverage researched, factchecked, and reconciled.**
  Artifacts:
  - `10-nginx-proxies-and-load-balancing/_research_event-driven-reverse-proxy.md`
  - `10-nginx-proxies-and-load-balancing/_research_load-balancing-peer-selection.md`
  - `10-nginx-proxies-and-load-balancing/_research_proxy-buffering-retries-timeouts.md`
  - `10-nginx-proxies-and-load-balancing/_factcheck_phase1.md`
  - `10-nginx-proxies-and-load-balancing/_research.md`
- 10 factcheck checked 43 load-bearing claims against NGINX `release-1.31.1` source. No unsupported claims remain.
  BRAIN patches applied after factcheck: release-pinned remaining URLs, added `ngx_posted_next_events` event-loop step,
  and annotated nginx.org doc-wording caveats.
- `meta/RESEARCH_INDEX.md` now includes verified 10 NGINX source anchors and residual 10 gaps.
- **Phase 1 / Wave 4 / 11 distributed-systems-foundations — FOUR clusters drafted/factchecked AND reconciled.**
  Artifacts:
  - `11-distributed-systems-foundations/_research_time-clocks-ordering-failure.md` + `_factcheck_phase1.md`
  - `11-distributed-systems-foundations/_research_vector-clocks-model-taxonomy.md` + `_factcheck_cluster2.md`
  - `11-distributed-systems-foundations/_research_consistency-replication-quorums.md` + `_factcheck_cluster3.md`
  - `11-distributed-systems-foundations/_research_cap-partitions-distributed-commit.md` + `_factcheck_cluster4.md`
  - `11-distributed-systems-foundations/_research.md` (RECONCILED, six sections)
- 11 cluster 4 fetched a NEW primary (Gray & Lamport "Consensus on Transaction Commit", TODS 2006) from
  `lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf` and verified 14 load-bearing 2PC/3PC/Paxos-
  Commit/Spanner claims with line receipts (0 blockers). CAP/PACELC primaries (Gilbert/Lynch, Brewer, Abadi) were
  network-blocked and stay `[UNVERIFIED from fetched source]`; Herlihy/Wing + Dynamo also still blocked.
- **Phase 1 / Wave 4 / 12 research-papers-for-engineers — TWO clusters drafted/factchecked AND reconciled.**
  Artifacts:
  - `12-research-papers-for-engineers/_research_how-to-read-a-paper.md` (reading method; verified Lamport "State the
    Problem" backbone; Keshav three-pass `[UNVERIFIED]`)
  - `12-research-papers-for-engineers/_research_paper-canon-walkthroughs.md` (canon catalog; 4 fresh-verified Lamport
    primaries + reuse of 06-11 receipts + blocked storage/ops canon flagged)
  - `12-research-papers-for-engineers/_factcheck_phase1.md` (Cluster A 4 VERIFIED + 2 flagged; Cluster B 9 VERIFIED +
    2 flagged; 0 blockers)
  - `12-research-papers-for-engineers/_research.md` (RECONCILED, six sections)
- 12 fetched FOUR new primaries from `lamport.azurewebsites.net/pubs/`: "State the Problem Before Describing the
  Solution", "The Byzantine Generals Problem" (TOPLAS 1982), "Reaching Agreement in the Presence of Faults" (JACM 1980),
  and "The Part-Time Parliament" (original Paxos, TOCS 1998). Verified `3m+1`/`>2/3`-loyal, conditions A/B,
  impossibility-then-`OM(m)`, interactive consistency, the state-machine approach, and the editor's-note exposition
  exemplar. Keshav + the Google storage trilogy (MapReduce/GFS/Bigtable/Dynamo) + Dapper/Tail-at-Scale stay
  `[UNVERIFIED from fetched source]` (network-blocked). **ALL foundations 01-12 now reconciled/factchecked.**
- **Phase 1 / Wave 5 / 13 scaling-fundamentals — Part II FIRST sub-course RECONCILED (four clusters A–D).**
  Artifacts:
  - `13-scaling-fundamentals/_research_back-of-envelope-latency-queueing.md` (Cluster A) + `_factcheck_clusterA.md`
    (Little's Law, M/M/1 utilization wall, M/G/1 P-K, Amdahl, USL, tail/fan-out, latency hierarchy).
  - `13-scaling-fundamentals/_research_bottlenecks-use-method.md` (Cluster B — USE method, resource-vs-workload,
    sampling profilers, flame graphs, on/off-CPU, bottleneck-moves).
  - `13-scaling-fundamentals/_research_horizontal-vertical-akf-cube.md` (Cluster C — scale up/out, statelessness,
    AKF X/Y/Z cube, axis→downstream handoffs).
  - `13-scaling-fundamentals/_research_load-testing-capacity-planning.md` (Cluster D — open vs closed models,
    coordinated omission, percentile/histogram discipline, capacity loop).
  - `13-scaling-fundamentals/_factcheck_clusterBCD.md` (B/C/D, 0 blockers).
  - `13-scaling-fundamentals/_research.md` (RECONCILED, six sections).
  All capacity MATH verified by independent recomputation (Python): `W/S=1/(1−ρ)`, Amdahl `1/(1−p)`, fan-out
  `1−(1−q)^N`, USL knee `N*=√((1−α)/β)`, Little's-Law derivation, closed `N=X·R`, and coordinated-omission
  percentiles (naive p99.9=1 ms vs CO-corrected ≈989 ms, ~3-orders-of-magnitude understatement). Memory-hierarchy/64B
  cache-line + consistent-hashing + replication/quorum + LB-peer-selection canon reused from verified 01/06/10/11.
  Empirical/historical attributions (Dean latency table, Drepper, Gregg USE+flame graphs, AKF cube, Tene CO,
  HdrHistogram/wrk2, NSDI-2006 open-vs-closed) stay `[UNVERIFIED]` — network-blocked. **ALL of 01-13 now reconciled.**
- **Phase 1 / Wave 5 / 14 data-modeling-partitioning-sharding — Part II SECOND sub-course RECONCILED (three clusters
  A–C); the AKF Z-axis handoff from 13.**
  Artifacts:
  - `14-data-modeling-partitioning-sharding/_research_data-modeling.md` (Cluster A — data model as access-pattern
    contract; relational/document/wide-column/KV orthogonal to B-tree-vs-LSM engine; normalization vs denormalization;
    read/write tradeoff; schema-on-write vs schema-on-read).
  - `14-data-modeling-partitioning-sharding/_research_partitioning-sharding.md` (Cluster B — range/hash/directory
    partitioning; consistent hashing reused from 06; shard keys; hot shard/celebrity; rebalancing; local vs global
    secondary indexes).
  - `14-data-modeling-partitioning-sharding/_research_cross-partition-operations.md` (Cluster C — scatter-gather;
    cross-shard joins + distributed query planning; cross-shard transactions handing off to 11; read snapshot).
  - `14-data-modeling-partitioning-sharding/_factcheck_clusterAB.md` (math by recomputation, mechanisms by reuse of
    06/07/08/11/13; 0 blockers; 2 first-draft numeric errors caught + patched).
  - `14-data-modeling-partitioning-sharding/_research.md` (RECONCILED, six sections).
  All load-bearing math verified by recomputation; canonical/vendor attributions `[UNVERIFIED]` (network HTTP 000, 6th
  session). **ALL of 01-14 now reconciled.**
- **Phase 1 / Wave 5 / 15 replication-and-consistency-in-practice — Part II THIRD sub-course RECONCILED (four clusters
  A-D); absorbs 14's denormalization + cross-partition consistency tax and turns 11's consistency THEORY into PRACTICE.**
  Artifacts:
  - `15-replication-and-consistency-in-practice/_research_replication-topologies-and-log.md` (Cluster A — why replicate
    (HA/read-scale/locality, orthogonal to partitioning); single/multi/leaderless topologies; sync/async/semi-sync
    durability dial; replication log statement/WAL-physical/logical-row/trigger + determinism; read replicas scale
    reads not writes).
  - `15-replication-and-consistency-in-practice/_research_replication-lag-anomalies-and-fixes.md` (Cluster B — lag
    window; read-your-writes / monotonic-reads / consistent-prefix anomalies + their session-guarantee fixes as a
    monotone ladder onto 11's consistency models).
  - `15-replication-and-consistency-in-practice/_research_conflicts-and-quorum-tuning.md` (Cluster C — conflict =
    concurrency detected by version vectors not clocks; LWW vs VV+merge vs CRDT semilattice merge; read-repair + Merkle
    anti-entropy + hinted handoff/sloppy quorum; quorum tuning W+R>N).
  - `15-replication-and-consistency-in-practice/_research_failover-split-brain-real-systems.md` (Cluster D — failover
    detect/elect/reconfigure; split-brain + fencing via quorum-gated commits + monotonic tokens + STONITH;
    Postgres/MySQL/Raft-based/Dynamo-style/Spanner topologies; CAP/PACELC made concrete).
  - `15-replication-and-consistency-in-practice/_factcheck_phase1.md` (math by recomputation, mechanisms by reuse of
    06/07/11/13/14; 0 blockers).
  - `15-replication-and-consistency-in-practice/_research.md` (RECONCILED, six sections).
  All load-bearing math verified by recomputation (exhaustive `W+R>N <=> guaranteed overlap`, and `W+R=N` INSUFFICIENT —
  strict `>`; stale-read prob 0 iff W+R>N, N=3,W=R=1 -> 2/3, N=5,W=R=1 -> 0.8; majority quorum tolerates floor((N-1)/2)
  failures, N in {3,5,7} -> {1,2,3}). DDIA ch.5/8/9, Dynamo, Bayou session guarantees, CRDT papers, CAP/PACELC
  primaries, Postgres/MySQL/Mongo/Cassandra/Riak/etcd/CockroachDB/ZooKeeper docs `[UNVERIFIED]` (network HTTP 000, 7th
  session, carried forward). **ALL of 01-15 now reconciled.**

- **Phase 1 / Wave 5 / 16 caching-and-cdn-strategies — Part II FOURTH sub-course RECONCILED (four clusters A-D); the
  shared sink for the hot-key + read-scale + staleness pressures that 14 (hot shards/Zipf) and 15 (read replicas/lag/
  staleness ladder) both hand off; a cache is a deliberately-stale replica (15) bounded by TTL/invalidation not a
  replication log.**
  Artifacts:
  - `16-caching-and-cdn-strategies/_research_cache-placement-and-patterns.md` (A — placement ladder client/CDN/proxy/
    app-local/remote/DB; five patterns cache-aside/read-through/write-through/write-back/write-around = cross-product
    of "write touches cache?" x "SoT write sync?"; read vs write path; near/far duplication tax).
  - `16-caching-and-cdn-strategies/_research_eviction-and-sizing.md` (B — eviction reuse from 08; hit ratio master
    metric, origin load=(1-h); Zipf working-set curve H(k,a)/H(N,a); skew sensitivity; size to the knee).
  - `16-caching-and-cdn-strategies/_research_consistency-and-invalidation.md` (C — cache=replica so caching IS a
    consistency problem; invalidation ladder TTL->versioned->explicit; validation/304; stampede R*T_r + coalescing/
    leases/SWR/jitter/XFetch; negative caching; stale-fill race fix=version/token).
  - `16-caching-and-cdn-strategies/_research_cdn-and-edge.md` (D — PoPs/anycast; pull vs push; cache key/`Vary`;
    origin shielding=coalescing across the fleet; Cache-Control/ETag/conditional-304/SWR; purge/soft-purge/versioned
    URLs; edge compute; latency floor is physics).
  - `16-caching-and-cdn-strategies/_factcheck_phase1.md` (math by recomputation; mechanisms by reuse of 03/06/08/10/
    13/14/15; 0 blockers).
  - `16-caching-and-cdn-strategies/_research.md` (RECONCILED, six sections).
  All sizing/stampede MATH verified by recomputation (top-1% of N=1e6,a=1 -> 0.68 hit ratio; a=0.8/1.0/1.2 ->
  0.36/0.68/0.91; concave monotone curve; origin load=(1-h), 99->99.9% cuts origin load 10x; stampede herd~R*T_r up
  to 2000x -> 1 with coalescing). RFC 9111/5861/7234/4786, Nishtala NSDI 2013, Breslau INFOCOM 1999, XFetch VLDB 2015,
  Cormode-Muthukrishnan, ARC, vendor CDN/anycast attributions `[UNVERIFIED]` (network HTTP 000, 8th session, carried
  forward). **ALL of 01-16 now reconciled.**

- **Phase 1 / Wave 6 / 17 async-queues-and-event-driven-architecture — Part II FIFTH sub-course RECONCILED (four
  clusters A-D); the async backbone every prior Part-II sub-course hands work to (14 cross-shard -> sagas; 15 logical
  log -> CDC; 16 write-back flush + cross-region invalidation transport).**
  Artifacts:
  - `17-async-queues-and-event-driven-architecture/_research_messaging-models-delivery-semantics.md` (A — queue vs log
    vs pub/sub; at-most/at-least/effectively-once; idempotency + dedup-window sizing; per-partition ordering; outbox +
    CDC; reuse 09/11/14/15).
  - `..._research_event-driven-architecture-patterns.md` (B — events vs commands; choreography vs orchestration; sagas
    + idempotent compensation; event sourcing + CQRS; materialized-view maintenance; backpressure handoff to 18).
  - `..._research_producer-consumer-mechanics-failure.md` (C — consumer groups/rebalancing; commit/ack timing;
    redelivery/backoff/retry-budget; DLQ/poison; exactly-once-effect; replay/reprocessing).
  - `..._research_delivery-infrastructure-tradeoffs.md` (D — broker durability/replication = 15 dial; partitioning for
    throughput = 14; fan-out; retention vs compaction; latency-vs-throughput batching).
  - `..._recompute.py` (pure stdlib, 0 errors) + `..._factcheck_phase1.md` (recompute/reuse/primary; 0 blockers) +
    `..._research.md` (RECONCILED, six sections).
  All 6 load-bearing math claims VERIFIED by recomputation (duplicate certainty E[dups]=N*p; dedup-window=redelivery
  horizon (213 s ex.) + store rate*window*bytes; batching tput 1/(c/B+m)->1/m; retention rate*bytes*ret*RF vs
  compaction floor keys*bytes history-independent; parallelism<=partitions, need=ceil(target/per); dual-write window
  ~38/1e9 ops at 100 ms). Mechanisms reused from line-verified 09/11/13/14/15/16/06/08/03. Nishtala NSDI '13 FETCHED
  + verified as the production EDA/CDC instance (leases 17K->1.3K herd cut; mcsqueal CDC delete-stream off the commit
  log). AMQP/JMS/SQS/RabbitMQ/Debezium, Sagas-1987/Fowler-CQRS/Richardson/DDD, Kafka-KIP-429/98/447 + knob wording,
  Kreps-2011/Kafka-defaults/Pulsar/NATS/Kinesis attributions `[UNVERIFIED]` carried forward. **ALL of 01-17 now
  reconciled.**

- **Phase 1 / Wave 7 / 18 rate-limiting-backpressure-and-load-shedding (SEDA) — Part II SIXTH sub-course RECONCILED
  (four clusters A-D); absorbs 17's lag/backpressure handoff and continues 13's queueing wall into deliberate
  overload control. Cross-cluster thesis: input -> buffer -> drop -> client.**
  Artifacts:
  - `18-.../_research_rate-limiting-algorithms.md` (A — token/leaky bucket; fixed/sliding window log+counter;
    distributed counters cell-based; fairness/burst; enforce at edge/LB/task; 429+Retry-After).
  - `18-.../_research_backpressure-and-seda.md` (B — bounded queues; block-vs-drop; credit/flow control = TCP
    window/request(n)/pull-lag; end-to-end vs hop-by-hop; SEDA stage/queue/controller).
  - `18-.../_research_load-shedding-and-retry-storms.md` (C — fail-early-503; CPU-not-QPS; criticality 4 tiers +
    per-customer limits; brownout/degrade; FIFO/LIFO/CoDel + deadline-drop; retry amplification 1/(1-r) -> storm
    -> goodput collapse; budgets 3/10%).
  - `18-.../_research_timeouts-breakers-bulkheads-hedging.md` (D — timeouts+deadline-propagation; circuit
    breakers; bulkheads; hedged/tied requests; adaptive concurrency AIMD + Google adaptive throttling).
  - `18-.../_recompute.py` (9/9 pass) + `_factcheck_phase1.md` (0 blockers) + RECONCILED `_research.md`.
  All 9 load-bearing math claims VERIFIED by recomputation. PRIMARIES fetched+verified: RFC 6585 §4 + Google
  SRE *Handling Overload* + *Addressing Cascading Failures*. Mechanisms reused from line-verified
  03/11/13/14/15/16/17/10. SEDA/CoDel/Hystrix/GCRA/AWS-builders attributions `[UNVERIFIED]` (still blocked).
  **ALL of 01-18 now reconciled.**

- **Phase 1 / Wave 8 / 19 observability-tracing-and-slos (Dapper) — Part II SEVENTH sub-course RECONCILED
  (four clusters A-D); the SENSING half of the control loop whose actuating half is 18. Signals (Four
  Golden Signals, error-budget burn, queue depth, retry ratio, breaker state, latency percentiles) drive
  18's controllers; tracing makes 17 choreographed flows + 13 fan-out tails legible.**
  Artifacts:
  - `19-.../_research_metrics-and-signal-taxonomy.md` (A — counter/gauge/histogram; Four Golden Signals
    vs RED vs USE; black-box/white-box; cardinality 60->60M; percentiles>means; bucket-additivity).
  - `19-.../_research_distributed-tracing-dapper.md` (B — Dapper trace-tree/spans/context-propagation/
    clock-skew-via-happens-before/sampling/overhead; head vs tail; reconstructs 13 tail + 17 async flow).
  - `19-.../_research_logs-events-three-pillars.md` (C — structured logging; three pillars cost/
    cardinality; exemplars metric->trace->log; sampling/retention reuse 09/16/17).
  - `19-.../_research_sli-slo-error-budgets.md` (D — SLI/SLO/SLA; error budget=(1-SLO)*window; burn
    rate; multiwindow multi-burn-rate alerting; SRE iterations 1->6).
  - `19-.../_recompute.py` (28/28 pass) + `_factcheck_phase1.md` (0 blockers) + RECONCILED `_research.md`.
  All 28 load-bearing math claims VERIFIED by recomputation. PRIMARIES fetched+verified to
  `meta/fetched_primaries/`: Dapper-2010 (research.google mirror), SRE Book Ch.4 SLO + Ch.6 Monitoring,
  SRE Workbook Ch.5 Alerting (sre.google); receipt `_VERIFIED_2026-06-10_observability.md`. Mechanisms
  reused from line-verified 11/13/16/17/09/03/10/18. OpenTelemetry/W3C-trace-context/exemplars/RED-credit/
  tail-sampling/Magpie-X-Trace-Pinpoint attributions `[UNVERIFIED]` carried forward. **ALL of 01-19 now
  reconciled.**

- **Phase 1 / Wave 9 / 20 resilience-failure-and-capacity-planning (The Tail at Scale) — Part II EIGHTH
  sub-course RECONCILED (four clusters A-D); the SYNTHESIS course. Takes 18's overload controls + 19's
  signals/SLOs/error-budgets and turns them into a discipline for surviving partial failure + planning
  capacity.**
  Artifacts:
  - `20-.../_research_failure-models-and-partial-failure.md` (A — fault/error/failure chain; partial
    failure = the defining property (FLP, reuse 11); crash/omission/timing(=tail)/Byzantine taxonomy;
    independent-vs-correlated failure; fallacies of distributed computing; blast radius; cascade vs
    single fault (reuse 18); CAP as a failure-model statement).
  - `20-.../_research_the-tail-at-scale.md` (B — fan-out 1-0.99^100=63%; faults-vs-variability;
    hedged/backup + tied requests w/ cross-server cancellation + measured Dean tables; micro-
    partitioning; selective replication; latency-induced probation; canary; tainted partial results).
  - `20-.../_research_resilience-patterns-and-redundancy.md` (C — 18 toolkit + redundancy N+1/N+2/2N +
    failover (15) + cells & shuffle-sharding (C(8,2)=28->1/28->7x; Route 53 730B; recursive) + chaos
    engineering (Netflix monkeys) as failure-injection verification).
  - `20-.../_research_capacity-planning-and-reliability-math.md` (D — capacity loop; utilization wall;
    headroom C=D/rho*; M/G/1 variance; USL knee; serial prod(a_i); parallel 1-(1-a)^n; correlated-
    failure correction; headroom-to-survive-f = f/n; capacity as an SLO input (reuse 19)).
  - `20-.../_recompute.py` (38/38 pass) + `_factcheck_phase1.md` (0 blockers) + RECONCILED `_research.md`.
  All 38 load-bearing math claims VERIFIED by recomputation. Headline: the correlated-failure correction
  collapses naive six-nines parallel redundancy to ~three nines (1001x worse) — correlation, not replica
  count, sets real availability. PRIMARIES fetched+verified to `meta/fetched_primaries/` (receipt
  `_VERIFIED_2026-06-10_resilience.md`): Dean Tail-at-Scale; AWS shuffle-sharding + backoff/jitter;
  Brewer PODC 2000 CAP; Kleppmann CAP 2015; Netflix Simian Army. Mechanisms reused from line-verified
  11/12/13/14/15/16/18/19. Nygard/Avizienis/fallacies/CoDel(403)/Raft(000)/Gilbert-Lynch/PACELC
  attributions `[UNVERIFIED]` carried forward. **ALL of 01-20 now reconciled; only 21 remains.**

- **CAP UPGRADE 2026-06-10 (Wave 9 — Brewer + Kleppmann unblocked):** `people.eecs.berkeley.edu`
  (Brewer PODC 2000 keynote) + `martin.kleppmann.com` (CAP blog 2015) returned HTTP 200 (blocked 8+
  sessions). Fetched + verified; upgraded carry-forward CAP `[UNVERIFIED]` -> VERIFIED in 11
  (`_factcheck_cluster4.md`) and 15 (`_factcheck_phase1.md`): "at most two" of {C,A,P}, Forfeit C/A/P,
  BASE, CAP-as-narrow-theorem. Gilbert-Lynch 2002 formal proof + Abadi 2012 PACELC remain blocked /
  carried forward; nothing erased.

- **SEDA UPGRADE 2026-06-10 (Wave 8 — finally unblocked):** `www.sosp.org/2001/papers/welsh.pdf` (also
  `people.eecs.berkeley.edu/~brewer/papers/SEDA-sosp.pdf`) returned HTTP 200 after 8+ sessions blocked.
  Fetched + verified `seda-sosp01.{pdf,txt}`; the carry-forward `[UNVERIFIED]` SEDA in 18 Cluster B is now
  VERIFIED (stage=event-handler+bounded-incoming-queue+thread-pool, each managed by a controller; well-
  conditioned=graceful degradation; dynamic resource controllers = thread-pool sizing/batching/admission;
  explicit bounded queues for load conditioning). UPGRADE appended to `18-.../_factcheck_phase1.md`;
  nothing erased. (Note: `eecs.harvard.edu/~mdw` SEDA path is 404 — use sosp.org / berkeley.)

- **BIG CANON HAUL 2026-06-10 (network heal — research.google mirrors + usenix.org/legacy + allthingsdistributed
  + sre.google all HTTP 200):** fetched + extracted (pypdf in a throwaway uv venv, removed after) + verified to
  `meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_canon.md`). Upgraded carry-forward `[UNVERIFIED]` ->
  VERIFIED in factcheck files of 18D/15/14/13/12 (appended UPGRADE sections; nothing erased):
  - **Tail at Scale** CACM 2013 — fan-out 63% (=1-0.99^100), backup=hedged + cancellation=tied, Backup Effects
    994ms->50ms -> 13/18D/20/12.
  - **Dynamo** SOSP 2007 — "R + W > N yields a quorum-like system" verbatim + consistent-hashing/vnodes/vector-
    clocks/sloppy-quorum/hinted-handoff/Merkle/read-repair/gossip -> 15/14/06/11/12.
  - **MapReduce** OSDI 2004 (straggler+backup tasks), **Bigtable** OSDI 2006 (SSTable/tablet/Chubby/compaction),
    **GFS** SOSP 2003 (chunk/64MB/lease/primary), **Spanner** OSDI 2012 (TrueTime/commit-wait/Paxos/external-
    consistency) -> 14/15/11/12. Deep per-paper factchecks deferred to each sub-course's Phase 2.

- **NETWORK UPGRADE 2026-06-10 (8 sessions of HTTP 000 partially lifted):** rfc-editor.org + usenix.org returned
  HTTP 200. Fetched + saved to `meta/fetched_primaries/`: RFC 9111/5861/7234/4786 and Nishtala NSDI '13 (PDF + text).
  Upgraded 16 (and matching 08) carry-forward `[UNVERIFIED]` -> VERIFIED: RFC 9111 s-maxage/Vary/Age/must-revalidate,
  RFC 5861 SWR+stale-if-error, RFC 4786 anycast BCP, Nishtala cache-aside/leases/17K->1.3K/mcsqueal-CDC/4%. See
  `16-caching-and-cdn-strategies/_factcheck_phase1.md` §F.

  **2026-06-10 Wave 7 further heal:** `research.google` (via `static.googleusercontent.com` mirrors),
  `usenix.org/legacy`, `allthingsdistributed.com`, `sre.google` now HTTP 200 — used to fetch the canon haul
  (Tail-at-Scale/Dynamo/MapReduce/Bigtable/GFS/Spanner + RFC 6585 + 2 SRE chapters). **Still HTTP 000 / blocked:**
  arxiv, dl.acm (queue.acm.org 403), raft.github.io, postgresql.org, kafka.apache.org, martin.kleppmann,
  `eecs.harvard.edu` (SEDA), `aws.amazon.com` (builders' library), non-legacy `usenix.org`.

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **CURRENT FRONTIER (post-Wave-10):** Foundations 01-12 + **all of Part II System Design 13-21 are
  reconciled/factchecked — Part II is COMPLETE.** The next batch is **Part III Agentic System Design
  (22-the-agent-loop → 34-design-your-own-agentic-system)** per COURSE_MAP "Phase 1 batch 3", then
  Appendices A-O (batch 4). 21's residual `[UNVERIFIED]` are community design idioms (KGS, push/pull
  feed, vendor chat/search/payment designs, GCRA) — mechanisms grounded in line-verified 06-20, none
  load-bearing. 21 Case 5 is primary-anchored on CAP (Gilbert-Lynch) + PACELC (Abadi), both fetched
  this session.
- **Opportunistic for next session (newly HTTP 200, deferred/time-boxed this session):** arxiv.org,
  kafka.apache.org, postgresql.org. Use to upgrade carried `[UNVERIFIED]` in 09/17 (Kafka paper/KIPs),
  07/15 (Postgres WAL/replication docs), and any arxiv-hosted canon. STILL blocked: queue.acm.org 403
  (CoDel), raft.github.io 000, dl.acm.org 403 (DOI landing).
- **10 residual gaps:** reverify exact nginx.org wording before Phase 2 prose; trace `reuseport`/`EPOLLEXCLUSIVE`
  operational interaction, `ngx_thread_pool.c`, full HTTP phase engine, `X-Accel-Buffering`, cache-specific proxy paths,
  TLS termination/OpenSSL, HTTP/2 stream multiplexing/flow control, HTTP/3/QUIC, and commercial/open-source boundaries
  for `slow_start`, active health checks, sticky, queue, random, least_time, and dynamic membership.
- **11 distributed-systems-foundations is reconciled.** Four clusters factchecked and synthesized into `_research.md`.
  Remaining 11 carry-forward gaps (do NOT erase; fetch before Phase 2 prose): CAP/PACELC primaries (Gilbert/Lynch 2002,
  Brewer 2000/2012, Abadi 2012), Herlihy/Wing TOPLAS 1990 object-level linearizability, Dynamo SOSP 2007,
  Fidge/Mattern/Charron-Bost/CBCAST + DLS/JACM 1988, Skeen 1981 original 3PC, Berenson 1995 ANSI isolation levels,
  cleaner Chandra-Toueg text, source pin for the `f+1` synchronous rotating-coordinator claim, and re-pin Gray &
  Lamport to ACM TODS 2006 pagination.
- **12 research-papers-for-engineers is reconciled.** Two clusters (reading-method + canon-walkthroughs) factchecked
  and synthesized into `_research.md`. Carry-forward 12 gaps (do NOT erase; fetch before Phase 2 prose): Keshav "How to
  Read a Paper" CCR 2007 + Roscoe/Mitzenmacher/Smith reviewing guidance; the storage trilogy MapReduce/GFS/Bigtable/
  Dynamo; ops classics Dapper/Tail-at-Scale/Chubby/ZooKeeper; method cross-cuts Herlihy/Wing, Saltzer/Reed/Clark
  End-to-End, Lampson "Hints"; and re-pin Byzantine/Reaching-Agreement pagination to the ACM record.
- **ALL foundations 01-12 are now research-complete** (reconciled `_research.md` + factcheck artifacts each), subject to
  the logged `[UNVERIFIED]` gaps. **Part II System Design FIRST sub-course 13 is also reconciled/factchecked (four
  clusters A–D).** 14-21 remain untouched.
- **13 scaling-fundamentals gaps (RECONCILED, but carry-forward `[UNVERIFIED]` primaries remain — do NOT erase, do NOT
  harden into prose until fetched):** all four clusters' math is verified by recomputation, but every empirical/
  historical *attribution* is network-blocked. Fetch when the network heals:
  - Cluster A: Jeff Dean "Latency Numbers Every Programmer Should Know" exact ns/ms table (jboner gist 2841832 /
    Colin Scott interactive / Stanford-295 talk PDF); Drepper "What Every Programmer Should Know About Memory"
    (akkadia/LWN 2007); Little 1961; Kleinrock *Queueing Systems v1* (M/M/1, M/G/1 P-K); Amdahl 1967; Gunther USL;
    Dean & Barroso "Tail at Scale" CACM 2013.
  - Cluster B: Gregg "The USE Method" + per-resource checklist/tools; flame-graph pages + FlameGraph scripts (incl.
    off-CPU); _Systems Performance_ (2nd ed.); RED method (Wilkie/Weaveworks); Linux PSI `/proc/pressure`.
  - Cluster C: AKF "Scale Cube" articles (akfpartners.com); Abbott & Fisher _The Art of Scalability_ (2nd ed.);
    Twelve-Factor App factor VI; Fowler microservices/distributed-monolith.
  - Cluster D: Gil Tene "How NOT to Measure Latency"; HdrHistogram `recordValueWithExpectedInterval`; `wrk2`;
    Schroeder/Wierman/Harchol-Balter "Open Versus Closed" (NSDI 2006); Harchol-Balter _Performance Modeling..._.
  Next Phase-1 work: **15-21** (Part II). 15 (replication-and-consistency-in-practice) is the natural next start — it
  absorbs the consistency tax that 14's denormalization (A) and cross-partition operations (C) both hand off.
-partitioning-sharding is RECONCILED (three clusters A/B/C — do NOT erase carry-forward
  `[UNVERIFIED]`):** all load-bearing math verified by recomputation this session (`mod N` 4->5 moves 0.800 vs
  consistent-hashing add-1-to-N=10 moves 0.088 ~ 1/(N+1); vnode load spread 1.26x; hot key 30%-on-10-shards busiest
  0.378 / ratio 4.86x; fan-out `1-0.99^100=0.634` ~63% slow; scatter throughput f*QPS per shard constant in N).
  Mechanisms reused from line-verified 06/07/08/11/13. Carry-forward blocked primaries to fetch when network heals:
  Codd CACM 1970 + normal forms + Kent 1983 (A); Bigtable OSDI 2006, Dynamo SOSP 2007, Karger consistent-hashing STOC
  1997 (A/B); Sagas SIGMOD 1987, MapReduce OSDI 2004, Tail at Scale CACM 2013, Spanner re-pin (C); Avro/Protobuf/Thrift
  evolution; DynamoDB/Cassandra/HBase/Elasticsearch/Mongo/Vitess/Citus/Presto/Spark/CockroachDB docs; Kleppmann DDIA
  ch.2-3/6/7/9.

- **15 replication-and-consistency-in-practice is RECONCILED (four clusters A/B/C/D — do NOT erase carry-forward
  `[UNVERIFIED]`):** all load-bearing math verified by recomputation this session (exhaustive `W+R>N <=> guaranteed
  read/write overlap`, with `W+R=N` proven INSUFFICIENT — strict `>` required; stale-read prob = 0 iff W+R>N, e.g.
  N=3,W=R=1 -> 2/3 stale, N=5,W=R=1 -> 0.8 stale; majority quorum W=R=floor(N/2)+1 tolerates floor((N-1)/2) failures,
  N in {3,5,7} -> {1,2,3}). Mechanisms reused from line-verified 06/07/11/13/14 (leader=ordering device, quorum=
  majority intersection, version vectors, FLP, Raft term-fencing, CAP/PACELC, Spanner, Merkle/WAL). Carry-forward
  blocked primaries to fetch when network heals: Kleppmann DDIA ch.5/8/9; Dynamo SOSP 2007 (leaderless quorum, sloppy
  quorum, hinted handoff, Merkle anti-entropy, read-repair, sibling version vectors); Terry et al. "Session Guarantees"
  (Bayou) PDIS 1994 (A/B); Shapiro et al. CRDTs INRIA RR-7506 / SSS 2011 (C); CAP/PACELC Gilbert-Lynch 2002 / Brewer
  2000-2012 / Abadi 2012 (D, also carried in 11); vendor docs Postgres (streaming/physical repl, `synchronous_commit`
  levels, logical decoding/`pgoutput`, Patroni), MySQL (binlog STATEMENT/ROW/MIXED, semi-sync, GTID, Group Replication),
  MongoDB (replica sets, oplog, write concern), Cassandra (LWW default, tunable consistency, hinted handoff, read
  repair), Riak (siblings, dotted version vectors, CRDT types), etcd/CockroachDB/Consul/TiKV (Raft ranges/leases),
  ZooKeeper (Zab/`zxid`)/Chubby, Pacemaker/STONITH.

---

## Running this project in code-puppy

- Start from `/Users/m0t0hu6/Desktop/substrate`.
- Rehydrate first from `AGENTS.md`, `START_HERE.md`, `meta/CONSTITUTION.md`, `meta/RESEARCH_PROTOCOL.md`,
  `meta/COURSE_MAP.md`, `meta/RESEARCH_INDEX.md`, `meta/PROGRESS.md`, `meta/SESSION_LOG.md`,
  `meta/DECISIONS.md`, and this file. Do not guess.
- Use tools, not vibes. Read files before modifying them. Keep diffs small.
- No parallel sub-agents in this harness. Switch agents sequentially or use multiple terminals.
- Phase 1 = research briefs only. No chapter prose.
- Validate source claims before accepting them. Primary sources first. `[UNVERIFIED]` is allowed in briefs but must
  not harden into course prose.
- End every session: append `SESSION_LOG.md`, update `PROGRESS.md` and `NEXT_SESSION.md`, run status, and commit.

---

## PROMPT TO RUN NEXT

```text
You are the BRAIN agent for the Substrate course project. Start safely from
`/Users/m0t0hu6/Desktop/substrate`. Read AGENTS.md, START_HERE.md, meta/CONSTITUTION.md,
meta/RESEARCH_PROTOCOL.md, meta/COURSE_MAP.md, meta/RESEARCH_INDEX.md, meta/PROGRESS.md,
meta/SESSION_LOG.md, meta/DECISIONS.md, and meta/NEXT_SESSION.md. Confirm in 3-4 lines:
- current Phase 1 state,
- Wave 2 milestone `4a1cc71`,
- current checkpoint commit from `git rev-parse --short HEAD`,
- that ALL of 01-21 are reconciled/factchecked: foundations 01-12 PLUS Part II 13-21
  COMPLETE (13 scaling-fundamentals, 14 data-modeling-partitioning-sharding, 15
  replication-and-consistency, 16 caching-and-cdn, 17 async-queues-and-EDA, 18 rate-limiting-
  backpressure-shedding/SEDA, 19 observability-tracing-SLOs/Dapper, 20 resilience-failure-
  capacity/Tail-at-Scale, 21 design-case-studies CAPSTONE with six case-study briefs +
  `_recompute.py` 32/32 + design-method matrix),
- that Part III Agentic System Design (22-the-agent-loop onward) is the NEXT untouched batch
  ("Phase 1 batch 3" per COURSE_MAP),
- and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError
recurs, stop and tell me to grant Desktop/OneDrive access or move the repo to a non-OneDrive
workspace. Do not reinstall Code Puppy.

Current state to preserve (do NOT erase logged `[UNVERIFIED]`/residual gaps):
- 21 is reconciled (CAPSTONE; bespoke per-case-study structure, NOT abstract clusters). All 32
  back-of-envelope estimates VERIFIED BY RECOMPUTATION (`21.../_recompute.py`): URL shortener
  (writes 1157 QPS, reads 115741 QPS @100:1, base62^7=3.52e12 -> 5.2% full after 5yr, 91 TB,
  5 GB hot cache, origin read 11574 @90% hit); news feed (feed reads 34722 QPS, fan-out-on-write
  69444/s =200x, celebrity 1e8 single-post fan-out); chat (23148 msg QPS, 73 TB/yr, 1000 gateway
  nodes, 500 group fan-out); search/typeahead (23148 prefix QPS, 100 index shards, scatter-gather
  tail 1-(1-0.01)^100=63.4%); payments (116 txn QPS, 3.74 TB/yr, W+R>N 4>3 strict, idempotency
  86400s); rate limiter (1M checks/s, over-admit (M-1)*B=35, 64 MB counters). No new primitives -
  applies 06/09/11/12/13-20; mechanisms REUSED from those line-verified sub-courses.
- CAP/PACELC UPGRADE done 2026-06-10 (Wave 10): Gilbert-Lynch "Perspectives on the CAP Theorem"
  (2012) + Abadi PACELC (2012) HTTP 200 after many blocked sessions; fetched+verified to
  meta/fetched_primaries/ (receipt `_VERIFIED_2026-06-10_cap-pacelc.md`); upgraded carry-forward
  `[UNVERIFIED]` -> VERIFIED in 11 (`_factcheck_cluster4.md`: formal CAP safety-vs-liveness,
  atomic register, CAP=>no-consensus-under-partition) and 15 (`_factcheck_phase1.md`: PACELC
  "if P: A-vs-C; else: L-vs-C", PA/EL vs PC/EC vs PC/EL); anchors 21 Case 5 payments. NOTE the
  original 2002 SIGACT News PDF is still separately unfetched (2012 retrospective restates it).
- 21 residual `[UNVERIFIED]` (none load-bearing): community design idioms - KGS key-gen,
  push/pull/hybrid feed, websocket/XMPP/MQTT + vendor chat (WhatsApp/Signal), search internals
  (Lucene/Elasticsearch/BM25 = Appendix-P candidate), vendor payment designs (Stripe/Square),
  GCRA + vendor rate-limiter posts. Mechanisms grounded in line-verified 06-20.
- 20/19/18/17/16/15/14/13 stay reconciled; math verified by recomputation; remaining canon/vendor
  attributions still `[UNVERIFIED]` except those upgraded.
- Network reality at last check (2026-06-10 Wave 10): NEW HTTP 200 = groups.csail.mit.edu
  (Gilbert-Lynch), cs.umd.edu (Abadi PACELC), arxiv.org, kafka.apache.org, postgresql.org (last
  three deferred/time-boxed). Earlier-healed: aws.amazon.com builders', berkeley/sosp.org,
  martin.kleppmann.com, netflixtechblog.com, research.google mirrors, sre.google, usenix.org/legacy,
  rfc-editor.org. STILL HTTP 403/000/blocked: queue.acm.org 403 (CoDel), raft.github.io 000,
  dl.acm.org 403 (DOI landing).

Run this plan, but only as much as can be completed well in one session. Prefer one clean
factchecked checkpoint over multiple shallow briefs.

1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. START Part III Agentic System Design "Phase 1 batch 3" (briefs ONLY - no chapters, no Phase 2).
   Begin with 22-the-agent-loop (the foundational primitive: call -> observe -> decide -> repeat),
   then proceed in dependency order through 23-tools-and-tool-contracts, 24-prompts-and-context-
   engineering, 25-memory-short-term-long-term-and-safety, etc., as far as one clean checkpoint
   allows. Part III has its OWN bespoke structures per sub-course (the agent loop is a control-loop
   walkthrough; tools is a contract/schema walkthrough; etc.) - do NOT blindly reuse the four-
   cluster shape. Cross-link DOWN into the Part I/II primitives where an agent system reuses them
   (e.g. 25 memory <-> 08/16 caching + 06 data structures; 26 state-persistence-and-resume <->
   15 replication/durability + 09 the log; 27 multi-agent orchestration <-> 11 consensus/ordering +
   17 async/EDA + 20 resilience/tail; 31 evaluation/tracing <-> 19 observability; 32 cost-obs <->
   13 capacity + 18 rate-limiting/budgets).
3. For each sub-course: draft cluster/section briefs; RECOMPUTE any quantitative claims (context-
   window token budgets, cost-per-call math, retry/timeout budgets, memory eviction sizing) in a
   `_recompute.py`; factcheck load-bearing claims; reuse line-verified Part I/II canon; fetch
   primaries where a specific claim needs one (e.g. ReAct, Toolformer, MCP spec, RAG/retrieval
   papers, function-calling docs). Mark anything unfetched `[UNVERIFIED]`.
4. Reconcile each finished sub-course into `<subcourse>/_research.md` (bespoke structure fine).
   Preserve every logged `[UNVERIFIED]`/residual gap. If thin or blocked, stop at a clean
   checkpoint; do not fake completeness.
5. Opportunistic: fetch the newly-unblocked primaries (arxiv.org, kafka.apache.org,
   postgresql.org) to upgrade carried `[UNVERIFIED]` in 09/17 (Kafka paper/KIPs), 07/15 (Postgres
   WAL/replication), and arxiv-hosted canon. Retry still-blocked CoDel/raft/dl.acm. Save receipts
   to meta/fetched_primaries/ and update the relevant cluster + factcheck files.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md`, update
   `meta/NEXT_SESSION.md` with the exact next-session prompt. Keep files under 600 lines where
   reasonable, run `git status --short`, commit, and report remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
