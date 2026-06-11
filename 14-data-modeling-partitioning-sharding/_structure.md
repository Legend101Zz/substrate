# 14 — Data Modeling, Partitioning, and Sharding · _structure.md

**Identity:** the Z-axis of 13's scale cube made concrete — everything the line "shard by key"
hides. How to shape data around access patterns, place it across N nodes by a key, and pay the
bill whenever an operation refuses to stay inside one node.

**Bespoke shape — "shape → place → span" (logical → physical → the bill)."** NOT a tour of
NoSQL products. One idea at three layers, taught as an arc where each layer pushes work UP to the
one before it: **A shapes the data around the access patterns; B places that shape across nodes by
a key; C pays whenever an operation leaves one node — and the whole stack exists to make C rare.**
The through-line (same as 13): a bad key can't be rescued by more nodes, more indexes, or a
smarter planner — "a shared bottleneck defeats scale-out." Math verified by recomputation; labs
are visualizers and bake-offs.

## Dependency position
- **Depends on:** 13 (the Z-axis framing + fan-out tail + capacity loop), 06 (B-tree/LSM/Bloom
  storage physics, consistent hashing, HyperLogLog), 07 (relational query exec + optimizer —
  generalized to distributed planning at the pushdown level), 11 (atomic commit 2PC/Paxos Commit,
  cross-partition snapshot), 08 (KV-as-cache hot-key mitigation).
- **Feeds into:** 15 (replication absorbs denormalization's write-side consistency tax + cross-
  partition read consistency), 16 (hot-key caching), 17 (saga orchestration + CDC fan-out), 20
  (hedged/tied for scatter tail), 21 (every case study models + shards).
- **Appendix links DOWN:** F-postgres (relational instantiation), H-kafka (partitioned log),
  06 (the structures), future query-engine/columnar appendix. 14 owns the method; appendices own
  the engine internals.

## Chapter specs (3–5 lines each)
### A — shape (logical)
1. **The data model is an access-pattern contract** — a model makes some queries O(1) and others
   O(join/scan); logical model (relational/document/wide-column/KV) is ORTHOGONAL to storage
   engine (B-tree vs LSM, reuse 06). The discipline: enumerate the queries FIRST, then shape.
2. **Normalization vs denormalization = the read/write tradeoff** — normalize = one home per fact,
   join at read (cheap/safe writes, costly reads); denormalize = duplicate/pre-join (cheap read,
   write-time consistency tax). Work is conserved — you only choose WHEN to pay it (read, write,
   or async-precompute). Schema-on-write vs schema-on-read; evolvability (Avro/Protobuf/Thrift).

### B — place (physical)
3. **Partition strategies** — range (sorted, cheap scans, append hot-spot), hash (uniform, scans
   destroyed, `mod N` remaps ~everything), consistent hashing (≈`1/N` movement, vnodes to smooth),
   directory (flexible, its own distributed system). The strategy decides spread + which queries
   stay partition-local.
4. **The shard key is destiny** — high cardinality + even access + matches the dominant query ⇒
   partition-local hot path. Computed placement has NO optimizer — a wrong key fans the query out
   and no index/planner saves it. The single highest-leverage decision in the sub-course.
5. **Skew, hot shards & rebalancing** — partitioning spreads KEYS, not LOAD; access skew (Zipf/
   celebrity) lands on one partition and the busiest shard sets capacity (more nodes don't help).
   Mitigate: salting (→scatter), caching/replicas (16/08/15), directory pinning. Rebalance with
   minimal movement, serve-during-move, avoid cascade (aggressive rebalancing = outage amplifier).
6. **Secondary indexes** — inherit the read/write tradeoff: local (doc-partitioned: cheap write,
   scatter read) vs global (term-partitioned: cheap read, cross-partition usually-async write).

### C — span (the bill)
7. **Scatter-gather** — as slow as the slowest shard (13's fan-out tail) AND re-couples shards by
   loading all of them (throughput amplification, constant in N). OK rare/small-N; anti-pattern
   hot/large-N. Avoid via predicate pruning + global index.
8. **Cross-shard joins & distributed planning** — co-partition (best) > broadcast small dimension
   > shuffle/repartition over the network. Distributed planning = pushdown (move the answer, not
   the data) + two-phase aggregation (HyperLogLog for distinct, 06).
9. **Cross-shard transactions & read consistency** — avoid (single-partition model) > saga
   (eventual atomicity, NO isolation, manual compensations) > 2PC/Paxos Commit (atomic, costly/
   blocking-or-not, reuse 11). Without a global snapshot, cross-partition reads see a mix of
   versions; snapshot/MVCC + global timestamp (Spanner/TrueTime) fixes it at a cost.

## Paired build labs (/build — visualizers + bake-offs)
Model-the-same-domain-four-ways (relational/document/wide-column/KV; which query each makes O(1)
vs O(scan)) → read/write-tradeoff simulator (normalized vs denormalized: read-join cost vs
write-fan-out + inconsistency window) → `mod N` vs consistent-hashing rebalance visualizer (+
vnode load-variance drop) → hot-shard simulator (Zipfian load saturates one shard → salting/
dedicated shard; measure rebalanced load + new scatter cost) → local-vs-global secondary-index lab
→ scatter-gather tail-amplification demo (confirm `1−(1−q)^N`; add hedged requests) → co-partition
vs shuffle-join lab (network bytes moved) → saga vs 2PC mini-implementation (inject coordinator
crash to feel blocking; compensations for the saga).

## Diagrams needed
- The shape→place→span arc as the spine motif (work pushed upward to modeling).
- Four logical models over one domain; which query is O(1) vs O(scan) in each.
- `mod N` remap (almost everything moves) vs consistent-hash ring + vnodes (≈1/N moves).
- Shard-key spreads keys not load → Zipf head saturates one shard (busiest sets capacity).
- Local vs global secondary index (write fan-out vs read scatter).
- Scatter-gather: slowest-shard tail + every-shard load amplification.
- Co-partition vs broadcast vs shuffle join (data movement).
- Saga (local txns + compensations) vs 2PC (prepare/commit + coordinator-failure blocking).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED BY RECOMPUTATION:** `mod N` move fraction (4→5: 0.800; 8→9: 0.888); consistent-hash/
  vnode move ≈`1/(N+1)` + vnode spread 1.26×; hot-shard busiest 0.378 / ratio 4.86×; fan-out tail
  `1−0.99^100=0.634`; scatter throughput amplification (constant in N).
- **`[UNVERIFIED]` — all canonical/vendor/historical attributions network-blocked:** Codd 1970 +
  normal forms, Kent 1983, Bigtable 2006, Dynamo 2007, Karger 1997 (consistent hashing), Sagas
  1987, MapReduce 2004, Tail-at-Scale (later VERIFIED in 20), Spanner re-pin, Avro/Protobuf/Thrift
  rules, DynamoDB/Cassandra/HBase/Elasticsearch/Mongo/Vitess/Citus/Presto/Spark/CockroachDB docs,
  Kleppmann DDIA ch.2–3/6/7/9. Teach mechanisms now; do NOT harden vendor specifics until fetched.
- **Disagreements to resolve:** "aggregate boundary" (DDD) vs classic normalization vocabulary;
  plain consistent hashing vs bounded-load vs rendezvous/HRW + vnode-count guidance; saga
  isolation-anomaly countermeasure taxonomy + exact hedged-vs-tied numbers.
- **Boundary discipline:** storage-engine physics + consistent-hashing internals + HyperLogLog →
  06; relational query exec + optimizer → 07; denormalization write-tax + cross-partition snapshot
  + atomic-commit internals → 11; replication-in-practice → 15; hot-key caching → 16/08; saga
  orchestration via events + CDC → 17; hedged/tied → 20; fan-out math → 13. Don't duplicate.
