# 14 — data-modeling-partitioning-sharding — Cluster C: Cross-partition operations

> **Phase 1 research brief (NO course prose).** Standard six sections. Once data is partitioned
> (Cluster B), the operations that *span* partitions become the hard part — they re-introduce the
> distributed-systems problems that single-node databases hid. This cluster is the bridge from
> partitioning into 11 (atomic commit / consistency) and 13 (fan-out tail).
>
> **Verification posture:** the *coordination* mechanics (atomic commit, 2PC cost, consistency)
> are **reused from 11** (line-verified there against Gray & Lamport, Paxos, Spanner — not
> re-fetched). Fan-out tail math is **reused from 13** (verified by recomputation). Scatter-gather
> latency arithmetic is **verified by recomputation this session** (`_factcheck_clusterAB.md`).
> Vendor/system attributions are `[UNVERIFIED from fetched source]` (network HTTP 000, 6th session).

---

## 1. Key mechanisms

### 1.1 The core tension: partitioning makes single-partition ops cheap and multi-partition ops hard

Cluster B optimized the *common* path: a query that fixes the shard key hits one partition and is
fast. But three classes of operation inherently cross partitions, and each is a known-hard
distributed-systems problem in disguise:
1. a **read** that isn't keyed by the shard key (or spans many keys) → **scatter-gather**,
2. a **join** across data on different partitions → **distributed join**,
3. a **write/transaction** touching keys on different partitions → **distributed transaction**
   (atomic commit, handoff to 11).

The design goal of all of Cluster A+B was to make these *rare*. This cluster is about what to do
when they're unavoidable.

### 1.2 Scatter-gather (fan-out / fork-join read)

A query that can't be localized is **scattered** to all (or many) relevant partitions, each
computes its local part, and a coordinator **gathers** and merges the results. Used for:
local-secondary-index lookups (Cluster B §1.6), full-text / aggregate queries, range scans on a
hash-partitioned table.

The two costs, both load-bearing:
- **Tail-latency amplification (reuse 13).** The whole query is as slow as the **slowest**
  partition. With N partitions each having tail probability `q` of being slow, the probability
  the *overall* query is slow is `1−(1−q)^N` — 13's fan-out formula. **Verified by recomputation
  (reuse):** `q=0.01, N=100 → 1−0.99^100 ≈ 0.366` → ~37% of scatter-gather queries hit a slow
  partition even though each partition is fast 99% of the time. **This is the single most
  important reason to keep reads partition-local.** Mitigations: hedged/tied requests, only
  scatter to the partitions that can match (partition pruning), or redesign the key (Cluster B).
- **Throughput amplification.** One logical query becomes N physical queries → it consumes N×
  the backend work. A scatter-gather over all shards turns every node into a participant in every
  such query, which *destroys* the independence that made sharding scale (it re-couples the
  shards). **Verified by recomputation:** if a fraction `f` of queries scatter to all N shards,
  each shard's load includes `f × (total QPS)` regardless of N — a scatter-heavy workload doesn't
  scale with nodes.

> **Rule the brief should teach:** scatter-gather is acceptable for *rare* queries and *small* N;
> it is a scaling anti-pattern for *hot* queries or *large* N. Prefer pruning (hit few
> partitions) and global indexes (Cluster B) to convert scatter into a single-partition read.

### 1.3 Cross-shard joins and distributed query planning

A join needs matching rows *co-located*; partitioning scatters them. Options, from cheapest to
costliest:
- **Co-partitioning (the preferred fix):** shard both tables by the **same join key** so matching
  rows live on the same partition → the join is **partition-local** (each node joins its own
  slice, results concatenate). This is why "choose the shard key to match your joins" (Cluster A
  §1.4 / B §1.3) matters; it's a *modeling* decision that makes a *runtime* operation cheap.
  `[UNVERIFIED]` Vitess/Citus co-location, Spanner interleaved tables — blocked.
- **Broadcast (replicated-dimension) join:** if one side is small (a dimension/reference table),
  replicate it to **every** partition so the big-table side joins locally. Cheap read, but every
  partition stores + must keep the dimension updated (write-side cost). 
- **Repartition / shuffle join:** if neither side is co-partitioned, the system **re-hashes** one
  or both tables on the join key over the network into temporary partitions, then joins locally.
  This is the MapReduce/Spark "shuffle" — correct but network-bound and the dominant cost of
  big-data joins. `[UNVERIFIED from fetched source]` MapReduce (OSDI 2004), Spark — blocked (12
  carried-forward storage-trilogy list).

**Distributed query planning** is the optimizer (07) generalized across nodes: it must decide
*where* each operator runs, *what* moves over the network, and *push down* as much filtering /
aggregation as possible to the partitions (so only small partial results travel). The cost model
now includes **network transfer**, not just disk/CPU. The winning move is almost always
**"compute where the data is, move the answer not the data"** (predicate/aggregate pushdown) —
the same principle as a local secondary index. Two-phase aggregation (partial aggregates per
partition → final merge at the coordinator) is the canonical pushdown pattern; it works for
distributive aggregates (sum/count/min/max) and needs care for holistic ones (exact median,
distinct-count → reuse 06 HyperLogLog as the approximate, mergeable alternative).

### 1.4 Cross-shard transactions (atomic commit) — handoff to 11

A write touching keys on multiple partitions needs **atomicity across partitions**: all commit or
none do, despite partial failure. This is exactly the **atomic commit** problem reconciled in 11.
Reuse (line-verified in 11 against Gray & Lamport "Consensus on Transaction Commit," TODS 2006):
- **Two-phase commit (2PC):** a coordinator runs *prepare* (all participants vote, durably
  persist "prepared") then *commit/abort*. Cost ≈ `3N−1` messages and **two round-trips** of
  latency added to every cross-shard write; participants hold **locks across both phases**.
- **2PC's fatal flaw: blocking.** If the coordinator fails after participants vote "yes" but
  before delivering the decision, participants are stuck holding locks indefinitely (in-doubt) —
  availability loss. This is *the* reason cross-shard transactions are avoided.
- **Paxos/Raft Commit (non-blocking):** replace the single coordinator with a consensus group so
  the commit decision survives coordinator failure (Gray & Lamport: Paxos Commit; 2PC is the
  `F=0` degenerate case). Spanner does **2PC over Paxos groups** + 2PL + TrueTime commit-wait to
  get externally-consistent cross-shard transactions — the gold-standard, at the cost of
  commit-wait latency. `[UNVERIFIED]` Spanner exact numbers re-pin needed; reuse-verified in 11.

**The pragmatic ladder (what real systems choose, cheapest first):**
1. **Avoid it** — model so the transaction is single-partition (co-locate by entity / aggregate;
   DynamoDB single-item, Mongo single-document atomicity). The whole point of Cluster A's
   aggregate boundary.
2. **Sagas** — break the distributed transaction into a sequence of local transactions, each with
   a **compensating** action to undo on failure. Gives *eventual* atomicity, **no isolation**
   (intermediate states are visible), application-managed. Handoff to 17 (orchestration/
   choreography via events). `[UNVERIFIED]` Garcia-Molina & Salem "Sagas" (SIGMOD 1987) — blocked.
3. **2PC** — when you truly need atomic isolation across shards and can tolerate the latency +
   blocking risk (or use Paxos Commit to remove blocking).

> **The teaching spine:** cross-shard transactions are expensive *and* fragile, so the entire
> stack above them — aggregate modeling (A), shard-key choice (B), co-partitioning (C §1.3) —
> exists to make them **rare**. When unavoidable, the choice is "weaken atomicity" (saga/eventual)
> vs "pay for it" (2PC / Paxos-commit). This is the partition-level restatement of CAP/PACELC (11).

### 1.5 Read consistency across partitions

Even read-only multi-partition queries have a consistency question: a scatter-gather over
partitions that are *independently* replicated and updated can see a **mix of versions** (no
global snapshot) → a query can observe a state that never atomically existed. Fixes: a global
**snapshot read** (MVCC + a globally meaningful timestamp — Spanner TrueTime; reuse 11) gives a
consistent cut across partitions at a cost; without it, cross-partition reads are only
*eventually*/per-partition consistent. This is the read-side twin of §1.4 and hands back to 11
(consistency models) and 15 (replication in practice).

## 2. Foundational sources

**Verified by reuse (line-verified earlier — NOT re-fetched):**
- Fan-out tail `1−(1−q)^N` (`0.99^100≈0.366`) — 13 `_research_back-of-envelope-latency-queueing.md`
  + `_factcheck_clusterA.md`.
- 2PC cost (`3N−1`, two round-trips), 2PC blocking failure, Paxos Commit (`2F+1`, progress with
  `F+1`, 2PC = `F=0`), Spanner 2PC-over-Paxos + 2PL + commit-wait — 11
  `_research_cap-partitions-distributed-commit.md` + `_factcheck_cluster4.md` (Gray & Lamport
  TODS 2006, line-verified).
- Consistency models / linearizability / snapshot reads / TrueTime — 11 `_research.md`.
- The optimizer choosing access paths (generalized here to distributed planning) — 07
  `_research_optimizer-external-exec.md`.
- HyperLogLog as a mergeable approximate distinct-count for cross-partition aggregation — 06.

**Verified by recomputation this session** (`_factcheck_clusterAB.md`): scatter-gather throughput
amplification (a fraction `f` scattering to all N shards loads every shard by `f×QPS` regardless
of N); fan-out tail reuse check.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals):**
- Garcia-Molina & Salem, "Sagas" (SIGMOD 1987).
- Dean & Ghemawat, "MapReduce" (OSDI 2004) — shuffle/repartition join (12 storage-trilogy list).
- Dean & Barroso, "The Tail at Scale" (CACM 2013) — hedged/tied requests for scatter-gather tail
  (also on 13's carried-forward list; handoff to 20).
- Spanner (OSDI 2012) re-pin for exact commit-wait / two-phase numbers; DeCandia "Dynamo"
  (SOSP 2007) for quorum reads across partitions.
- Vendor docs to pin: Vitess/Citus distributed query planning + co-location, Spanner interleaved
  tables, Presto/Trino + Spark Catalyst distributed planning, MongoDB `$lookup`/aggregation
  across shards, CockroachDB distributed SQL.
- Kleppmann *DDIA* ch.7 (transactions) + ch.9 (consistency/consensus) for synthesis framing.

## 3. "Why it's this way" — the forcing functions

- **Cross-partition ops are hard because partitioning deliberately destroyed co-location** — the
  thing that makes single-partition ops cheap is exactly what makes spanning ops expensive.
- **Scatter-gather amplifies the tail (13)** because the slowest of N independent draws dominates,
  and amplifies throughput because one query becomes N — both re-couple shards that sharding tried
  to decouple.
- **Distributed planning optimizes for network transfer** because, post-partition, moving data is
  the dominant cost — hence pushdown / "move the answer, not the data."
- **2PC blocks because a single coordinator is a single point of failure for the decision**;
  consensus-replicating the decision (Paxos Commit) is the only way to be non-blocking — straight
  from 11.
- **Sagas exist because 2PC's latency + blocking are unacceptable for long/loosely-coupled
  workflows** — trading isolation for availability, the CAP/PACELC choice at the app level.
- **The whole stack pushes work upward to modeling** (A/B) precisely so these costly ops stay
  rare — that's the *point* of access-pattern-driven design.

## 4. Common misconceptions to preempt

- "A query over all shards is fine, it's parallel." It's as slow as the slowest shard (tail
  amplification) and loads every shard (throughput amplification) — it doesn't scale.
- "Cross-shard joins work like single-DB joins." Only if co-partitioned; otherwise they shuffle
  data over the network or broadcast a table — orders of magnitude costlier.
- "Just use distributed transactions when you need consistency." 2PC adds two round-trips, holds
  locks, and *blocks* on coordinator failure — model to avoid it first.
- "Sagas give you ACID across services." No — eventual atomicity, **no isolation**; intermediate
  states are visible and you must write compensations.
- "A consistent read is automatic across partitions." No — without a global snapshot you can read
  a mix of versions that never atomically existed.
- "The optimizer handles distribution for me." It can only push down what your partitioning
  allows; a bad shard key forces shuffles no planner can avoid.

## 5. Best build-your-own target(s)

- **Scatter-gather tail-amplification demo:** N partitions with injected `q` tail; measure
  overall p99 vs N and confirm `1−(1−q)^N`; add hedged requests and watch the tail drop
  (handoff to 20). Pairs with 13.
- **Co-partition vs shuffle-join lab:** same join with matching vs mismatched shard keys; measure
  network bytes moved (local concat vs full shuffle vs broadcast).
- **Saga vs 2PC mini-implementation:** a 2-service "transfer" done both ways — 2PC (with an
  injected coordinator crash to show blocking) and a saga (with a compensating reversal) — to
  feel the isolation/availability tradeoff. Feeds 17 + 21.

## 6. Open questions / gaps to close (preserved verbatim in intent)

- **All system/historical attributions are network-blocked** `[UNVERIFIED]`: Sagas (SIGMOD 1987),
  MapReduce (OSDI 2004), Tail at Scale (CACM 2013), Spanner re-pin, Dynamo, and the Vitess/Citus/
  Spanner/Presto/Spark/Mongo/CockroachDB docs above, plus Kleppmann DDIA ch.7/9. Teach mechanisms
  now (anchored by reused 11/13/06/07 line-verified canon); do NOT harden specifics into Phase-2
  prose until fetched.
- **Disagreement to resolve with sources:** saga isolation-anomaly taxonomy (the "lack of
  isolation" countermeasures — semantic locks, commutative updates, reread) — pin a primary;
  and exact hedged-vs-tied-request tradeoff numbers from Tail at Scale.
- **Boundary discipline (cross-link, do NOT duplicate):**
  - atomic-commit *internals* (2PC/3PC/Paxos Commit proofs) live in **11**; this cluster *uses*
    them and adds the "avoid it / saga / 2PC" ladder.
  - consistency-model *definitions* live in **11**; *replication in practice* (read replicas,
    lag, quorum tuning) is **15** — this cluster only states the read-snapshot requirement.
  - hedged/tied requests + tail-tolerant patterns are **20** (resilience, "Tail at Scale"); this
    cluster only notes them as scatter-gather mitigations.
  - saga *orchestration/choreography via events* is **17** (async/event-driven); this cluster
    defines the saga, 17 builds it.
  - the fan-out *math* lives in **13**; reused here, not re-derived.
  - full distributed-query-engine internals (Spark/Presto) belong to the relevant appendix
    (H-kafka / future query-engine appendix) — this cluster only states the pushdown principle.
