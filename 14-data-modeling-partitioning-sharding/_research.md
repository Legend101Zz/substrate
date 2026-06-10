# 14 — data-modeling-partitioning-sharding — RECONCILED research (`_research.md`)

> **Phase 1 deliverable (NO course prose).** Synthesis of three factchecked clusters into the
> standard six sections. Full depth lives in the cluster files; this file reconciles overlaps,
> states the cross-cluster thesis, and consolidates sources + gaps. Every `[UNVERIFIED from
> fetched source]` / residual gap from the clusters is preserved here verbatim in intent.
>
> **Cluster files (read for full depth):**
> - A — `_research_data-modeling.md` (relational/document/wide-column/KV; normalization vs
>   denormalization; access-pattern-driven modeling; the read/write tradeoff; schema-on-read/write)
> - B — `_research_partitioning-sharding.md` (range/hash/directory partitioning; consistent
>   hashing reused from 06; shard keys; hot shards/celebrity; rebalancing; local vs global indexes)
> - C — `_research_cross-partition-operations.md` (scatter-gather; cross-shard joins + distributed
>   query planning; cross-shard transactions handing off to 11; cross-partition read consistency)
> - Factcheck — `_factcheck_clusterAB.md` (math verified by recomputation; mechanisms verified by
>   reuse of 06/07/08/11/13; attributions flagged `[UNVERIFIED]`; **0 blockers**; 2 first-draft
>   numeric errors caught + patched)
>
> **Reconciliation verdict:** 14 is reconciled on the basis that its load-bearing content — the
> *method and mathematics* of shaping, placing, and spanning partitioned data — is verified
> end-to-end (by recomputation or by reuse of earlier line-checked sources), **0 factcheck
> blockers across A–C**. The remaining gaps are *canonical/vendor/historical attributions* (Codd,
> Bigtable, Dynamo, Karger consistent-hashing, Sagas, MapReduce, DDIA, and the DynamoDB/Cassandra/
> Spanner/etc. docs), all uniformly network-blocked and carried forward `[UNVERIFIED]`. None is
> load-bearing for the *method*; none may harden into Phase-2 prose until fetched.

---

## The cross-cluster thesis (what this sub-course actually teaches)

14 is the **Z-axis of 13's AKF cube** made concrete: "shard by key" is one line in 13; this
sub-course is everything that line hides. It's one idea seen at three layers — logical, physical,
and spanning — and the three clusters are a single arc:

> **A shapes the data around the access patterns; B places that shape across N nodes by a key; C
> pays the bill whenever an operation refuses to stay inside one node.**

1. **A — shape (logical).** A data model is a contract: it makes some queries O(1) and others
   O(join/scan). Relational normalizes (one home per fact, join at read time); document/
   wide-column/KV pre-join by embedding/duplication (single fetch, pay on write). That is the
   **read/write tradeoff** — work is conserved, you only choose *when* to pay it (read, write, or
   async precompute). The discipline is **access-pattern-first**: enumerate queries, then shape.
2. **B — place (physical).** Pick a **shard key** and a placement strategy: range (sorted, cheap
   scans, append hot-spots), hash (uniform, scans destroyed, `mod N` remaps ~everything → use
   **consistent hashing**, ≈`1/N` movement, vnodes to smooth), or directory (flexible, but a
   distributed system of its own). The shard key is destiny: it decides spread, hot spots, and
   which queries are partition-local. **Skew (celebrity keys) defeats key-uniformity** — the
   busiest shard sets capacity, and more nodes don't help it. Secondary indexes inherit the
   read/write tradeoff: **local** = cheap write / scatter read; **global** = cheap read /
   cross-partition (usually async) write.
3. **C — span (the bill).** Any op that leaves one partition is a known-hard distributed problem:
   **scatter-gather** (as slow as the slowest shard — 13's fan-out tail; and re-couples shards by
   loading all of them), **cross-shard joins** (co-partition if you can; else broadcast or shuffle
   over the network), **cross-shard transactions** (atomic commit — 11: 2PC blocks, Paxos Commit
   doesn't; or weaken to **sagas** = eventual atomicity, no isolation). The entire stack above
   exists to make these **rare**.

The through-line: **every layer pushes work *upward* to modeling.** Good shape (A) + good key (B)
keeps the hot path single-partition so the expensive spanning ops (C) almost never fire. A bad
key can't be rescued by more nodes, more indexes, or a smarter planner — the same lesson as 13's
"a shared bottleneck defeats scale-out."

---

## 1. Key mechanisms (consolidated)

- **Model = access-pattern contract**; logical model (relational/document/wide-column/KV) is
  *orthogonal* to storage engine (B-tree vs LSM, reuse 06). *(A §1.1–1.2)*
- **Normalization** = one home per fact, join at read (cheap/safe writes, costly reads);
  **denormalization** = duplicate/pre-join (cheap read, write-time consistency tax). *(A §1.3)*
- **Read/write tradeoff** = conservation: pay the join/aggregate at read, write, or async-precompute
  time; choose by read:write ratio + latency SLO. *(A §1.4)*
- **Schema-on-write vs schema-on-read**; evolvability via Avro/Protobuf/Thrift. *(A §1.5)*
- **Partition strategies:** range (sorted, scans, append hot-spot), hash (uniform, scans broken,
  `mod N` trap), consistent hashing (≈`1/N` move, vnodes), directory (flexible, own distributed
  system). *(B §1.2)*
- **Shard key** = high cardinality + even access + matches dominant query ⇒ partition-local hot
  path. *(B §1.3)*
- **Hot shard / celebrity:** access skew lands on one partition; busiest sets capacity; mitigate
  by salting (→ scatter), caching/replicas (16/08/15), or directory pinning. *(B §1.4)*
- **Rebalancing:** minimal movement (consistent hashing / fixed partitions), serve-during-move,
  avoid cascade; fixed-partition vs dynamic-split vs vnode-proportional. *(B §1.5)*
- **Secondary indexes:** local (doc-partitioned: cheap write, scatter read) vs global
  (term-partitioned: cheap read, cross-partition async write). *(B §1.6)*
- **Scatter-gather:** slowest-shard tail (13 fan-out) + throughput amplification (loads every
  shard) ⇒ ok rare/small-N, anti-pattern hot/large-N; prune + global index to avoid. *(C §1.2)*
- **Cross-shard join:** co-partition (best) > broadcast small dimension > shuffle/repartition;
  distributed planning = pushdown (move the answer, not the data) + two-phase aggregation. *(C §1.3)*
- **Cross-shard transaction:** avoid (single-partition model) > saga (eventual, no isolation) >
  2PC / Paxos Commit (atomic, costly/blocking-or-not) — reuse 11. *(C §1.4)*
- **Cross-partition read consistency:** without a global snapshot you read a mix of versions;
  snapshot/MVCC + global timestamp (Spanner/TrueTime, 11) fixes it at a cost. *(C §1.5)*

## 2. Foundational sources (consolidated)

**Verified by recomputation this session** (`_factcheck_clusterAB.md`): `mod N` move fraction
(4→5: 0.800; 8→9: 0.888); consistent-hashing/vnode move ≈`1/(N+1)` (0.088 at N=10) + vnode load
spread 1.26×; hot-shard busiest 0.378 / ratio 4.86× (30% key on 10 shards); fan-out tail
`1−0.99^100=0.634` (~63% slow); scatter throughput amplification (f·QPS per shard, constant in N).

**Verified by reuse (line-checked in earlier sub-courses — NOT re-fetched):**
- B-tree/B+-tree + LSM + Bloom storage-engine physics — 06 `_research_indexes-lsm-bloom.md`.
- Consistent hashing ring + virtual nodes — 06 `_research_probabilistic-distributed-queues.md`.
- HyperLogLog (mergeable approx distinct-count for cross-partition aggregation) — 06.
- Relational query execution + optimizer choosing access paths — 07
  `_research_storage-query-exec.md`, `_research_optimizer-external-exec.md`.
- KV-as-cache / stampede (hot-key mitigation) — 08 `_research.md`.
- Replication + consistency models + atomic commit (2PC `3N−1`/two-RT/blocking; Paxos Commit
  `2F+1`/`F+1`/`F=0`; Spanner 2PC-over-Paxos + 2PL + commit-wait; snapshot reads) — 11
  `_research.md`, `_research_cap-partitions-distributed-commit.md`, `_factcheck_cluster4.md`
  (Gray & Lamport TODS 2006, line-verified).
- Fan-out tail `1−(1−q)^N` — 13 `_research_back-of-envelope-latency-queueing.md` + `_factcheck_clusterA.md`.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals):**
- *(A)* Codd CACM 1970 + normal-form papers; Kent CACM 1983; Bigtable OSDI 2006 (wide-column);
  Dynamo SOSP 2007 (KV); Avro/Protobuf/Thrift schema-evolution rules; Kleppmann DDIA ch.2–3.
- *(B)* Karger et al. STOC 1997 (consistent hashing original); Dynamo SOSP 2007 (vnodes,
  partition+replication composition); Bigtable OSDI 2006 (tablets/splits); vendor docs (DynamoDB
  partitioning/adaptive-capacity/LSI/GSI, Cassandra vnodes/partitioner/secondary indexes, HBase
  regions/splits, Elasticsearch shards/routing, Vitess/Citus, MongoDB hashed-vs-ranged shard
  keys/balancer); Kleppmann DDIA ch.6.
- *(C)* Garcia-Molina & Salem "Sagas" SIGMOD 1987; MapReduce OSDI 2004 (shuffle join); Dean &
  Barroso "The Tail at Scale" CACM 2013 (hedged/tied requests); Spanner OSDI 2012 re-pin; vendor
  docs (Vitess/Citus planning + co-location, Spanner interleaved tables, Presto/Trino + Spark
  Catalyst, MongoDB `$lookup` cross-shard, CockroachDB distributed SQL); Kleppmann DDIA ch.7/9.

## 3. "Why it's this way" — the forcing functions (consolidated)

- **No model is free across all queries** — storage is laid out one order at a time; modeling
  allocates that single layout to the dominant query. *(A)*
- **Normalization makes a fact atomic by construction; duplication makes atomicity a distributed
  write** — that's the consistency tax denormalization owes (11/15/17). *(A)*
- **Partitioning exists because one node has the `1/(1−ρ)` wall (13)** — the Z-axis is the only
  move that scales dataset + write capacity. *(B)*
- **`mod N` is unusable because it remaps ~everything on resize** — consistent hashing /
  fixed-partitions exist to make movement ≈`1/N`. *(B)*
- **Hot shards exist because placement spreads *keys*, not *load*** — access skew (Zipf/celebrity)
  defeats key-uniformity; the busiest shard caps you. *(B)*
- **The shard key is destiny because computed placement has no optimizer** — wrong key ⇒ the
  query fans out, and no index/planner saves it. *(B/C)*
- **Spanning ops are hard because partitioning deliberately destroyed co-location** — scatter
  amplifies the tail + re-couples shards; joins shuffle; 2PC blocks. *(C)*
- **The stack pushes work to modeling** so the costly spanning ops stay rare — the point of
  access-pattern-first design. *(A→B→C)*

## 4. Common misconceptions to preempt (consolidated)

- "NoSQL = no schema / faster than SQL." Schema moved to read-time; speed is the *engine*
  (B-tree/LSM), not the logical model. *(A)*
- "Normalize always / denormalize always." Normalize for write integrity; denormalize the hot
  read; pay the consistency tax knowingly. *(A)*
- "Denormalization just costs disk." It costs write-time consistency (fan-out + disagreement
  window). *(A)*
- "Pick the data model first." Pick the access patterns first. *(A)*
- "Sharding = add nodes and it scales." Only with a good shard key; a bad one caps you at the
  busiest shard. *(B)*
- "Hash partitioning fixes hot spots." It fixes key skew, not access skew. *(B)*
- "`hash(k) mod N` is fine." It remaps ~all keys on resize. *(B)*
- "Consistent hashing is even out of the box." Needs vnodes; one point/node is lumpy. *(B)*
- "More shards always help / a secondary index is free." Not the hot shard; and indexes are
  scatter-read (local) or cross-partition-write (global). *(B)*
- "Partitioning and replication are the same." Orthogonal; you do both. *(B)*
- "Rebalance automatically and aggressively." That's an outage amplifier. *(B)*
- "A query over all shards is fine, it's parallel." Slowest-shard tail + loads every shard. *(C)*
- "Cross-shard joins work like single-DB joins." Only if co-partitioned; else shuffle/broadcast. *(C)*
- "Just use distributed transactions for consistency." 2PC: two round-trips, locks, blocks on
  coordinator failure — model to avoid first. *(C)*
- "Sagas give ACID across services." Eventual atomicity, no isolation, manual compensations. *(C)*
- "Reads are consistent across partitions automatically." Not without a global snapshot. *(C)*

## 5. Best build-your-own target(s) (consolidated)

- **Model-the-same-domain-four-ways lab** (relational/document/wide-column/KV); show which query
  each makes O(1) vs O(scan). *(A; feeds B + 21)*
- **Read/write-tradeoff simulator** (normalized vs denormalized: read-join cost vs write-fan-out +
  inconsistency window). *(A; pairs with 13 capacity loop)*
- **`mod N` vs consistent-hashing rebalance visualizer** (+ vnodes load-variance drop). *(B; pairs with 06)*
- **Hot-shard simulator** (Zipfian load saturates one shard → salting/dedicated-shard + measure
  rebalanced load and new scatter cost). *(B; pairs with 13)*
- **Local-vs-global secondary-index lab** (write cost vs read fan-out vs staleness window). *(B)*
- **Scatter-gather tail-amplification demo** (confirm `1−(1−q)^N`; add hedged requests). *(C; pairs with 13, feeds 20)*
- **Co-partition vs shuffle-join lab** (network bytes moved). *(C)*
- **Saga vs 2PC mini-implementation** (inject coordinator crash to feel blocking; compensations
  for the saga). *(C; feeds 17 + 21)*

## 6. Open questions / gaps to close (consolidated — preserved verbatim in intent)

- **All canonical/vendor/historical attributions are network-blocked** `[UNVERIFIED]` (6th
  session, HTTP 000 on every academic/vendor host; only `lamport.azurewebsites.net` resolves):
  Codd 1970 + normal forms, Kent 1983, Bigtable OSDI 2006, Dynamo SOSP 2007, Karger STOC 1997,
  Sagas SIGMOD 1987, MapReduce OSDI 2004, Tail at Scale CACM 2013, Spanner re-pin, Avro/Protobuf/
  Thrift evolution rules, the DynamoDB/Cassandra/HBase/Elasticsearch/Mongo/Vitess/Citus/Presto/
  Spark/CockroachDB docs, and Kleppmann DDIA ch.2–3/6/7/9. The *math/method* is verified by
  recomputation + reuse; the *citations/exact wording/vendor specifics* need primaries when the
  network heals. Teach mechanisms now; do NOT harden specifics into Phase-2 prose until fetched.
- **Disagreements to resolve with sources:** "aggregate boundary" (DDD/Evans + DDIA) vs classic
  normalization vocabulary (A); load-balance quality of plain consistent hashing vs bounded-load
  vs rendezvous/HRW + per-system vnode-count guidance (B); saga isolation-anomaly countermeasures
  taxonomy (semantic locks / commutative updates / reread) + exact hedged-vs-tied numbers (C).
- **Boundary discipline (cross-link, do NOT duplicate downstream mechanics):**
  - storage-engine physics (B-tree/LSM/Bloom) + consistent-hashing internals + HyperLogLog ⇒ **06**.
  - relational query execution + the optimizer ⇒ **07**; this sub-course generalizes it to
    distributed planning only at the pushdown-principle level.
  - the write-side consistency tax of denormalization + cross-partition read snapshot + atomic
    commit internals ⇒ **11**; *replication in practice* (read replicas, lag, quorum tuning) ⇒ **15**.
  - hot-key *caching/CDN* mitigation ⇒ **16/08**; *read-replica* mitigation ⇒ **15**.
  - saga *orchestration/choreography via events* + CDC/materialized-view fan-out ⇒ **17**.
  - hedged/tied requests + tail-tolerant patterns ⇒ **20** (resilience, "Tail at Scale"); the
    fan-out *math* ⇒ **13**.
  - the AKF Z-axis framing this sub-course implements ⇒ **13** (`_research_horizontal-vertical-akf-cube.md`).
  - full distributed-query-engine internals (Spark/Presto) + DB-specific sharding internals ⇒
    relevant appendices (F-postgres / H-kafka / future query-engine + columnar appendix) — per the
    two-tier design, don't duplicate.
- **Next 14 work (optional, before Phase 2 prose):** fetch the blocked A/B/C primaries when a
  healthier network exists and upgrade the `[UNVERIFIED]` flags; otherwise 14 is research-complete
  at the *method/math* level. Next Phase-1 batch: **15–21** (Part II); 15
  (replication-and-consistency-in-practice) is the natural next start — it absorbs the consistency
  tax that A's denormalization and C's cross-partition operations both hand off.
