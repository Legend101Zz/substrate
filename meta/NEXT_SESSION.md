# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 (14 reconciled — ALL foundations 01-12 + Part II 13 & 14 done) · Phase: 1 (deep research) · Harness: **code-puppy**

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

- **14 data-modeling-partitioning-sharding is RECONCILED (three clusters A/B/C — do NOT erase carry-forward
  `[UNVERIFIED]`):** all load-bearing math verified by recomputation this session (`mod N` 4->5 moves 0.800 vs
  consistent-hashing add-1-to-N=10 moves 0.088 ~ 1/(N+1); vnode load spread 1.26x; hot key 30%-on-10-shards busiest
  0.378 / ratio 4.86x; fan-out `1-0.99^100=0.634` ~63% slow; scatter throughput f*QPS per shard constant in N).
  Mechanisms reused from line-verified 06/07/08/11/13. Carry-forward blocked primaries to fetch when network heals:
  Codd CACM 1970 + normal forms + Kent 1983 (A); Bigtable OSDI 2006, Dynamo SOSP 2007, Karger consistent-hashing STOC
  1997 (A/B); Sagas SIGMOD 1987, MapReduce OSDI 2004, Tail at Scale CACM 2013, Spanner re-pin (C); Avro/Protobuf/Thrift
  evolution; DynamoDB/Cassandra/HBase/Elasticsearch/Mongo/Vitess/Citus/Presto/Spark/CockroachDB docs; Kleppmann DDIA
  ch.2-3/6/7/9.

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
- that ALL of 01-14 are reconciled/factchecked (all foundations 01-12 PLUS Part II sub-courses
  13 scaling-fundamentals (clusters A-D) and 14 data-modeling-partitioning-sharding (clusters A-C)),
- that Part II 15-21 are still untouched,
- and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError recurs,
stop and tell me to grant Desktop/OneDrive access or move the repo to a non-OneDrive workspace. Do not reinstall
Code Puppy.

Current state to preserve (do NOT erase logged `[UNVERIFIED]`/residual gaps):
- 14 is reconciled; ALL its math is VERIFIED BY RECOMPUTATION (mod-N vs consistent-hashing
  movement, vnode load spread, hot-shard skew ratio, scatter-gather fan-out tail, scatter
  throughput amplification). Every canonical/vendor/historical ATTRIBUTION stays blocked
  `[UNVERIFIED]` (network HTTP 000, now 6 sessions): Codd CACM 1970 + normal forms + Kent 1983 (A);
  Bigtable OSDI 2006, Dynamo SOSP 2007, Karger consistent-hashing STOC 1997 (A/B); Sagas SIGMOD
  1987, MapReduce OSDI 2004, Tail at Scale CACM 2013, Spanner re-pin (C); Avro/Protobuf/Thrift
  evolution; DynamoDB/Cassandra/HBase/Elasticsearch/Mongo/Vitess/Citus/Presto/Spark/CockroachDB
  docs; Kleppmann DDIA ch.2-3/6/7/9.
- 13 stays reconciled with its math verified by recomputation and its Dean/Drepper/Gregg/AKF/Tene
  empirical+historical attributions still blocked `[UNVERIFIED]`.
- Network reality (6 sessions running): only `lamport.azurewebsites.net` + Walmart artifactory
  resolve; academic/ACM/arXiv/raw.github/research.google/gregg/akfpartners = HTTP 000.
  Carried-forward blocked primaries to fetch when the network is healthier:
  - 14: the A/B/C primaries listed above (see NEXT_SESSION "Things LEFT" for the full list).
  - 13: Dean latency table, Drepper, Little/Kleinrock/Amdahl/Gunther USL/Tail-at-Scale (A); Gregg
    USE+flame graphs/RED/PSI (B); AKF Scale Cube/Art of Scalability/Twelve-Factor/Fowler (C); Tene
    coordinated omission/HdrHistogram/wrk2/NSDI-2006 open-vs-closed (D).
  - 12: Keshav "How to Read a Paper" CCR 2007 (+ Roscoe/Mitzenmacher/Smith); MapReduce/GFS/
    Bigtable/Dynamo; Dapper/Tail-at-Scale/Chubby/ZooKeeper; Herlihy/Wing, Saltzer/Reed/Clark
    End-to-End, Lampson "Hints".
  - 11: CAP/PACELC (Gilbert/Lynch 2002, Brewer 2000/2012, Abadi 2012), Herlihy/Wing TOPLAS 1990,
    Dynamo SOSP 2007, Fidge/Mattern/Charron-Bost/CBCAST/DLS, Skeen 1981 3PC, Berenson 1995 ANSI
    isolation, cleaner Chandra-Toueg.
  - 10: nginx.org wording recheck, reuseport/EPOLLEXCLUSIVE, thread pools, HTTP phase engine, TLS/HTTP2/HTTP3.

Run this plan, but only as much as can be completed well in one session. Prefer one clean factchecked checkpoint over
multiple shallow briefs.

1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. START 15-replication-and-consistency-in-practice (Phase 1 briefs ONLY - no chapters, no Phase 2).
   It absorbs the consistency tax that 14's denormalization (Cluster A) and cross-partition
   operations (Cluster C) both hand off, and turns 11's consistency THEORY into PRACTICE. Add
   tightly-scoped clusters, e.g.:
   - replication topologies: single-leader vs multi-leader vs leaderless; sync vs async; the
     replication log (statement / WAL-ship / logical/row); read replicas + read-scaling.
   - replication lag + read-your-writes / monotonic-reads / consistent-prefix anomalies and the
     reads-from-leader / sticky-routing / causal fixes (reuse 11 consistency models).
   - conflict handling: multi-leader/leaderless write conflicts, LWW vs version vectors vs CRDTs,
     read-repair + anti-entropy + hinted handoff, quorum tuning (W+R>N) (reuse 11 quorums/Dynamo).
   - failover + practice: leader election, split-brain/fencing, replication in real systems
     (Postgres/MySQL/Raft-based/Dynamo-style), and the CAP/PACELC choice made concrete.
   Reuse canon already verified in 11 (consistency models, quorum=majority-intersection,
   leader/follower replication, Paxos/Raft, Spanner) and 14 (the denormalization + cross-partition
   consistency obligations that land here). Prefer primary sources; fetch via `curl`; mark anything
   unfetched `[UNVERIFIED]`.
3. Factcheck each new cluster's load-bearing claims (recompute any math; cite source for empirical/
   historical claims). Patch blockers.
4. If 15 coverage is honest, reconcile into
   `15-replication-and-consistency-in-practice/_research.md` (standard six sections), preserving
   every logged `[UNVERIFIED]`/residual gap. If thin or a blocker can't clear, stop at a clean
   cluster checkpoint; do not fake completeness (raccoon-shaped docs forbidden).
5. Opportunistic: if the network is healthier, fetch the carried-forward blocked 14 + 13 + 12 + 11
   primaries above and upgrade the corresponding `[UNVERIFIED]` flags to verified, updating the
   relevant cluster + factcheck files.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md`, update `meta/NEXT_SESSION.md`
   with the exact next-session prompt, keep files under 600 lines where reasonable, run
   `git status --short`, commit, and report remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
