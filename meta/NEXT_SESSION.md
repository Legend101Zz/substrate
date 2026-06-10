# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 (16 reconciled — ALL foundations 01-12 + Part II 13, 14, 15 & 16 done) · Phase: 1 (deep research) · Harness: **code-puppy**

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

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
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
- that ALL of 01-16 are reconciled/factchecked (all foundations 01-12 PLUS Part II sub-courses
  13 scaling-fundamentals (A-D), 14 data-modeling-partitioning-sharding (A-C),
  15 replication-and-consistency-in-practice (A-D), and 16 caching-and-cdn-strategies (A-D)),
- that Part II 17-21 are still untouched,
- and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError recurs,
stop and tell me to grant Desktop/OneDrive access or move the repo to a non-OneDrive workspace. Do not reinstall
Code Puppy.

Current state to preserve (do NOT erase logged `[UNVERIFIED]`/residual gaps):
- 16 is reconciled; ALL its sizing/stampede math is VERIFIED BY RECOMPUTATION (Zipf hit ratio
  H(k,a)/H(N,a): top-1% of N=1e6,a=1 -> 0.68, top-10% -> 0.84; a=0.8/1.0/1.2 -> 0.36/0.68/0.91;
  concave monotone working-set curve; avg latency h*t_hit+(1-h)*t_miss with origin load=(1-h), so
  99->99.9% cuts origin load 10x; cache stampede herd ~ R*T_r up to 2000x, collapsing to 1 with
  request coalescing). Every canonical/RFC/vendor ATTRIBUTION stays blocked `[UNVERIFIED]` (network
  HTTP 000, now 8 sessions): RFC 9111/5861/7234/4786; Nishtala et al. "Scaling Memcache at Facebook"
  NSDI 2013; Breslau et al. "Web Caching and Zipf-like Distributions" INFOCOM 1999; Vattani et al.
  XFetch VLDB 2015; Cormode-Muthukrishnan 2005 (CMS bounds); ARC pseudo-code/patent; vendor CDN
  architecture/purge/edge-compute (Cloudflare/Fastly/Akamai/CloudFront) + anycast/BGP + DNS-steering
  specifics + exact RTT/propagation figures + real-world Zipf alpha values.
- 15 stays reconciled; math verified by recomputation (W+R>N overlap, W+R=N insufficient, P(stale),
  majority tolerance floor((N-1)/2)); DDIA ch.5/8/9, Dynamo, Bayou session guarantees, CRDT papers,
  CAP/PACELC, Postgres/MySQL/Mongo/Cassandra/Riak/etcd/CockroachDB/ZooKeeper/Patroni/Pacemaker docs
  still `[UNVERIFIED]`.
- 14 stays reconciled; math verified by recomputation; Codd/Bigtable/Dynamo/Karger/Sagas/MapReduce/
  DDIA/vendor-doc attributions still `[UNVERIFIED]`.
- 13 stays reconciled; math verified by recomputation; Dean/Drepper/Gregg/AKF/Tene empirical+
  historical attributions still `[UNVERIFIED]`.
- Network reality (8 sessions running): only `lamport.azurewebsites.net` + Walmart artifactory
  resolve; academic/ACM/arXiv/raw.github/research.google/postgresql.org/raft.github.io/rfc-editor/
  vendor CDN = HTTP 000. Carried-forward blocked primaries to fetch when the network is healthier:
  - 16: RFC 9111/5861/7234/4786; Nishtala NSDI 2013; Breslau INFOCOM 1999; XFetch VLDB 2015;
    Cormode-Muthukrishnan; ARC; vendor CDN/anycast/edge-compute (see 16 "Things LEFT").
  - 15: DDIA ch.5/8/9; Dynamo; Bayou session guarantees; CRDT papers; CAP/PACELC; the Postgres/
    MySQL/Mongo/Cassandra/Riak/etcd/CockroachDB/ZooKeeper/Patroni/Pacemaker docs.
  - 14: the A/B/C primaries (see "Things LEFT").
  - 13: Dean latency table, Drepper, Little/Kleinrock/Amdahl/Gunther USL/Tail-at-Scale (A); Gregg
    USE+flame graphs/RED/PSI (B); AKF Scale Cube/Art of Scalability/Twelve-Factor/Fowler (C); Tene
    coordinated omission/HdrHistogram/wrk2/NSDI-2006 open-vs-closed (D).
  - 12: Keshav "How to Read a Paper" CCR 2007; MapReduce/GFS/Bigtable/Dynamo; Dapper/Tail-at-Scale/
    Chubby/ZooKeeper; Herlihy/Wing, Saltzer/Reed/Clark End-to-End, Lampson "Hints".
  - 11: CAP/PACELC (Gilbert/Lynch 2002, Brewer 2000/2012, Abadi 2012), Herlihy/Wing TOPLAS 1990,
    Dynamo SOSP 2007, Fidge/Mattern/Charron-Bost/CBCAST/DLS, Skeen 1981 3PC, Berenson 1995 ANSI
    isolation, cleaner Chandra-Toueg.
  - 10: nginx.org wording recheck, reuseport/EPOLLEXCLUSIVE, thread pools, HTTP phase engine, TLS/HTTP2/HTTP3.

Run this plan, but only as much as can be completed well in one session. Prefer one clean factchecked checkpoint over
multiple shallow briefs.

1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. START 17-async-queues-and-event-driven-architecture (Phase 1 briefs ONLY - no chapters, no Phase 2).
   It absorbs the write-back flush (16 Cluster A), the cross-region cache invalidation transport
   (16 Clusters C/D), the CDC/logical-log fan-out (15 Cluster A logical replication -> CDC), and the
   saga/cross-shard orchestration (14 Cluster C) that earlier sub-courses hand off. Reuse the LOG
   abstraction already line-verified in 09 (message-queues-logs-and-kafka: the log, partitions,
   offsets, delivery semantics, consumer groups). Add tightly-scoped clusters, e.g.:
   - messaging models + delivery semantics: queue vs log vs pub/sub; at-most-once/at-least-once/
     effectively-once; idempotency + dedup keys; ordering (per-partition) reusing 09/11; the outbox
     pattern + CDC reusing 15's logical log.
   - event-driven architecture + patterns: events vs commands; choreography vs orchestration; sagas
     (reuse 14 Cluster C) + compensation; event sourcing + CQRS; materialized-view maintenance
     (reuse 14/16); backpressure handoff to 18.
   - producer/consumer mechanics + failure: consumer groups/rebalancing, commit/ack timing,
     redelivery, dead-letter queues, poison messages, exactly-once via idempotent consumers +
     transactional outbox; replay/reprocessing.
   - delivery infrastructure + tradeoffs: broker durability/replication (reuse 15), partitioning
     for throughput (reuse 14), fan-out, retention/compaction; latency-vs-throughput batching.
   Reuse canon already verified in 09 (the log/partitions/offsets/delivery), 11 (ordering/causality/
   consensus), 14 (sagas/partitioning), 15 (logical log/CDC/replication durability), 16 (invalidation
   transport, materialized-view staleness). Prefer primary sources; fetch via `curl`; mark anything
   unfetched `[UNVERIFIED]`.
3. Factcheck each new cluster's load-bearing claims (recompute any math - delivery-semantics
   probabilities, dedup-window sizing, throughput/batching, retention; cite source for empirical/
   historical claims). Patch blockers.
4. If 17 coverage is honest, reconcile into `17-async-queues-and-event-driven-architecture/_research.md`
   (standard six sections), preserving every logged `[UNVERIFIED]`/residual gap. If thin or a blocker
   can't clear, stop at a clean cluster checkpoint; do not fake completeness (raccoon-shaped docs
   forbidden).
5. Opportunistic: if the network is healthier, fetch the carried-forward blocked 16 + 15 + 14 + 13 +
   12 + 11 primaries above and upgrade the corresponding `[UNVERIFIED]` flags to verified, updating
   the relevant cluster + factcheck files.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md`, update `meta/NEXT_SESSION.md`
   with the exact next-session prompt, keep files under 600 lines where reasonable, run
   `git status --short`, commit, and report remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
