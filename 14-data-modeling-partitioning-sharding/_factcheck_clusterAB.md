# 14 — data-modeling-partitioning-sharding — Factcheck (Clusters A/B/C)

> **Phase 1 factcheck.** Method: load-bearing **math verified by independent recomputation**
> (pure-Python, no external deps, this session); **mechanism claims verified by reuse** of
> already-line-verified canon in sub-courses 06/07/08/11/13 (cited per claim); **empirical/
> historical/vendor attributions** that need a primary are flagged `[UNVERIFIED from fetched
> source]` because the network is HTTP 000 for all academic/vendor hosts (6th consecutive
> session — only `lamport.azurewebsites.net` + Walmart artifactory resolve).
>
> **Blockers: 0.** Two first-draft numeric errors were CAUGHT by recomputation and PATCHED in the
> briefs (logged below) — recomputation did its job.

---

## Recomputation receipts (this session)

Script: hashed 200k keys (MD5), simulated `mod N` remap, a 200-vnode consistent-hashing ring,
hot-shard skew, fan-out tail, and scatter throughput.

| # | Claim | Brief | Recomputed result | Verdict |
|---|-------|-------|-------------------|---------|
| 1 | `hash(k) mod N` remaps almost everything on resize | B §1.2b | N=4→5 moved **0.800** (20% stay); N=8→9 moved **0.888** |  VERIFIED |
| 2 | Consistent hashing moves ≈`1/N` on a single node add | B §1.2c, §1.5 | add 1 to N=10 (200 vnodes) moved **0.088** ≈ `1/(N+1)=0.091` |  VERIFIED |
| 2b | Vnodes smooth load | B §1.2c | N=10, 200 vnodes: load max/min ratio **1.26×** (a single point/node is far lumpier) |  VERIFIED |
| 3 | Hot key sets capacity by busiest, not average | B §1.4 | 30% hot key on 10 shards → busiest **0.378**, others **0.078**, ratio **4.86×** |  VERIFIED (corrected) |
| 4 | Scatter-gather fan-out tail (reuse 13) | C §1.2 | `1−(1−0.01)^100 = 0.634` → ~**63%** of scatter queries hit a slow shard |  VERIFIED (corrected) |
| 5 | Scatter throughput amplification re-couples shards | C §1.2 | fraction f=0.05 scattering to all N shards loads **every** shard at f·QPS = 5000/s for N=10/100/1000 (constant), while point load/shard falls 9500→950→95 |  VERIFIED |

### Errors caught and patched (the point of recomputing)
- **B §1.4 hot-shard ratio:** first draft said busiest ≈30%, ratio ~3.9×. **Wrong** — the busiest
  shard also carries its baseline ~7.8% share, so busiest ≈**37.8%**, ratio ≈**4.86×**. Patched.
- **C §1.2 fan-out tail:** first draft said `1−0.99^100 ≈ 0.366 → ~37%`. **Backwards** — `0.99^100
  ≈ 0.366` is the *survival* (all-fast) probability; the *slow* probability is `1−0.366 ≈ 0.634`
  → ~**63%**. Patched. (This matches 13's Cluster-A verified value `0.99^100≈0.366` ⇒ ~63% slow.)

---

## Mechanism claims verified by REUSE (not re-fetched — line-verified in cited sub-course)

| Claim | Brief | Reused-from (line-verified) | Verdict |
|-------|-------|------------------------------|---------|
| B+-tree sorted leaves → cheap range scans; LSM append → cheap writes/merge reads | A §1.1 | 06 `_research_indexes-lsm-bloom.md` (SQLite `btreeInt.h`, Postgres `nbtree/README`, LevelDB/RocksDB) | PASS |
| Logical model ⟂ storage engine (LSM wide-column, B-tree document) | A §1.1 | 06 + 07 | PASS (framing) |
| Relational optimizer chooses the plan/access path (not the app) | A §1.2d | 07 `_research_optimizer-external-exec.md` | PASS |
| Consistent hashing ring + virtual nodes mechanics | B §1.2c, §1.5 | 06 `_research_probabilistic-distributed-queues.md` | PASS |
| Hash uniformity / Bloom for routing | B §1.2b | 06 `_research_indexes-lsm-bloom.md` | PASS |
| A partition is itself replicated; partitioning ⟂ replication | B §1.2, C §1.5 | 11 `_research.md` | PASS |
| 2PC cost `3N−1`, two round-trips, locks across phases | C §1.4 | 11 `_research_cap-partitions-distributed-commit.md` + `_factcheck_cluster4.md` (Gray & Lamport TODS 2006) | PASS |
| 2PC blocking on coordinator failure (in-doubt) | C §1.4 | 11 cluster4 (line-verified) | PASS |
| Paxos Commit non-blocking; `2F+1`, progress `F+1`; 2PC = `F=0` | C §1.4 | 11 cluster4 (Gray & Lamport, line-verified) | PASS |
| Spanner = 2PC over Paxos + 2PL + commit-wait | C §1.4, §1.5 | 11 cluster4 / `_research.md` | PASS |
| Snapshot read / linearizability / consistency models | C §1.5 | 11 `_research.md` | PASS |
| HyperLogLog mergeable approx distinct-count for cross-partition agg | C §1.3 | 06 | PASS |
| Fan-out tail `1−(1−q)^N` formula | C §1.2 | 13 `_factcheck_clusterA.md` | PASS |
| Cache stampede / KV-as-cache for hot-key mitigation | B §1.4, A §1.2a | 08 `_research.md` | PASS |

---

## Claims correctly flagged `[UNVERIFIED from fetched source]` (network-blocked, carried forward)

These are *attributions/exact specifics*, not load-bearing mechanisms; the mechanism is verified
by reuse/recomputation above. None may harden into Phase-2 prose until fetched.

- **A (data modeling):** Codd CACM 1970 + normal-form papers; Kent CACM 1983; Bigtable OSDI 2006
  (wide-column model); Dynamo SOSP 2007 (KV); Avro/Protobuf/Thrift schema-evolution rules;
  Kleppmann DDIA ch.2–3.
- **B (partitioning/sharding):** Karger et al. STOC 1997 (consistent hashing original); Dynamo
  SOSP 2007 (vnodes, partition+replication composition); Bigtable OSDI 2006 (tablets/splits);
  vendor docs (DynamoDB partitioning/adaptive-capacity/LSI/GSI, Cassandra vnodes/partitioner/
  secondary indexes, HBase regions/splits, Elasticsearch shards/routing, Vitess/Citus, MongoDB
  hashed-vs-ranged shard keys/balancer); Kleppmann DDIA ch.6.
- **C (cross-partition ops):** Garcia-Molina & Salem "Sagas" SIGMOD 1987; MapReduce OSDI 2004
  (shuffle join); Dean & Barroso "The Tail at Scale" CACM 2013 (hedged/tied requests); Spanner
  OSDI 2012 re-pin; vendor docs (Vitess/Citus planning + co-location, Spanner interleaved tables,
  Presto/Trino + Spark Catalyst, MongoDB `$lookup` cross-shard, CockroachDB distributed SQL);
  Kleppmann DDIA ch.7/9.

**Network retry this session (step 5):** arXiv, raw.githubusercontent, allthingsdistributed,
research.google all HTTP 000; only `lamport.azurewebsites.net` (200). No new primary fetchable.
Every `[UNVERIFIED]` flag from 13/12/11 also stands unchanged — none erased.
