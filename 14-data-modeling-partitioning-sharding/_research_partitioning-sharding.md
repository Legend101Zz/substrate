# 14 — data-modeling-partitioning-sharding — Cluster B: Partitioning & sharding

> **Phase 1 research brief (NO course prose).** Standard six sections. This is the physical
> layer: once Cluster A has decided the *shape* of the data, this cluster decides *where each
> record lives* across N nodes — and what goes wrong when the placement is uneven or has to move.
>
> **Terminology note (pin in Phase 2):** "partition," "shard," "region," "tablet," "vnode" are
> the same idea (a horizontal slice of a dataset) under different vendor names. This brief uses
> **partition** for the generic concept and **shard** when emphasizing it lives on a separate
> node for scale-out. Partitioning here = *horizontal* (by row); *vertical* partitioning
> (splitting columns) is the AKF Y-axis and belongs to 13/normalization, noted but not the focus.
>
> **Verification posture:** consistent hashing is **reused from 06** (line-verified there, not
> re-fetched). Math in §1 (key distribution, hot-shard skew, rebalance movement fraction) is
> **verified by recomputation this session** — see `_factcheck_clusterAB.md`. Historical/vendor
> attributions are `[UNVERIFIED from fetched source]` (network HTTP 000, 6th session).

---

## 1. Key mechanisms

### 1.1 Why partition at all — the forcing function from 13

13 (scale-out, AKF **Z-axis**) proved that a single node hits the `1/(1−ρ)` wall on *some*
resource: dataset bigger than one disk, write throughput bigger than one node, working set
bigger than one machine's RAM. Partitioning is the Z-axis move: **split the dataset by key so
each node owns a disjoint slice**, and total capacity scales with node count — *if* load spreads
evenly. The entire difficulty of this cluster is that last clause: **even spread is not free.**

### 1.2 The three partitioning strategies (and what each makes cheap)

**(a) Range partitioning.** Assign contiguous key ranges to partitions
(`[a–f]→P0, [g–m]→P1, …`). Keys stay **sorted within and across** partitions.
- Cheap: **range scans** (`WHERE k BETWEEN`), ordered iteration, "give me the next 100 keys."
- Expensive/dangerous: **hot spots** when writes target one range — e.g. a timestamp key means
  *all* current writes hit the last partition (the "append hot-spot"). The classic fix is to
  prefix/compound the key so recent writes spread (e.g. `(shardPrefix, timestamp)`), trading the
  global scan for a scatter-gather. *(Reuse: this is why wide-column row-key design, Cluster A
  §1.2c, matters — the row key is the range partition key.)*
- Requires a **partition map** (which range → which node), maintained as ranges split/merge when
  they grow/shrink. `[UNVERIFIED from fetched source]` Bigtable tablets / HBase regions —
  network-blocked (12 storage-trilogy gap).

**(b) Hash partitioning.** Apply a hash to the key and assign by hash → `partition = hash(k) mod N`.
- Cheap: **uniform spread** (a good hash destroys key skew), point lookups by exact key.
- Expensive: **range scans are destroyed** (adjacent keys scatter to all partitions → every
  range query is a scatter-gather, Cluster C). Some systems keep range scans *within* a
  partition by hashing only a *partition key* and range-sorting a *clustering key* inside it
  (the wide-column / DynamoDB composite-key trick) — best of both for queries that fix the
  partition key.
- **The `mod N` trap:** naive `hash(k) mod N` remaps *almost every key* when N changes (add one
  node → nearly all keys move). **Verified by recomputation:** going from N=4→5 with `mod`,
  only the keys where `hash%4==hash%5` stay put — empirically ~20% stay, ~80% move (see
  factcheck). This is why **consistent hashing** exists.

**(c) Consistent hashing.** *(Reuse from 06 `_research_probabilistic-distributed-queues.md` —
line-verified there; not re-fetched.)* Hash both keys and nodes onto a ring; a key belongs to
the next node clockwise. Adding/removing a node remaps only the keys between it and its
predecessor — **~K/N keys move** instead of ~all. **Verified by recomputation:** with N nodes,
expected fraction of keys moved on a single node add/remove ≈ `1/N` (vs ≈`1−1/N` for `mod N`).
- **Virtual nodes (vnodes):** one physical node owns *many* ring positions, which (i) smooths
  the otherwise-lumpy load (a single hash point per node gives high variance — the
  load-balance factor of plain consistent hashing is poor), and (ii) lets a joining node bleed
  load from *many* existing nodes in parallel, and a heterogeneous node take a proportional
  number of vnodes. `[UNVERIFIED from fetched source]` Karger et al. (STOC 1997), Dynamo vnodes
  (SOSP 2007) — network-blocked; mechanism reused-verified from 06.
- **Bounded-load / rendezvous (HRW) hashing** are alternatives that give tighter load bounds;
  note as variants, pin sources in Phase 2.

**(d) Directory / lookup partitioning.** Keep an explicit **partition map** (a directory
service) `key (or key-range) → partition → node`, consulted on every request (often cached).
- Cheap: **arbitrary, dynamic placement** — you can move any key anywhere, rebalance
  surgically, isolate a celebrity key onto its own shard.
- Cost: the directory is **another distributed system** (must be HA, consistent, low-latency,
  and not itself a bottleneck) — typically backed by a consensus/coordination service
  (handoff to 11; ZooKeeper/etcd-style). It's the most flexible and the most operationally
  expensive; the other three strategies are "directory-free" placement functions.

> **Unifying frame:** (a)–(c) are *computed* placement (no per-key state, cheap lookup, rigid
> movement rules); (d) is *stored* placement (per-key/range state, flexible movement, extra
> infra). Range and hash need a *small* map (range→node, or ring positions); directory needs a
> *full* map. The choice trades flexibility against the cost/availability of the map.

### 1.3 The shard key — the single most consequential choice

The shard (partition) key determines *everything* downstream: spread, hot spots, which queries
are partition-local vs. scatter-gather, and how transactions scope (Cluster C). Properties of a
good shard key:
- **High cardinality** (many distinct values → many possible partitions).
- **Even access distribution** (no single value dominates reads/writes).
- **Matches the dominant query** so the hot path is **partition-local** (the access-pattern-first
  principle from Cluster A §1.4, made physical). E.g. shard by `user_id` if most queries are
  "this user's data."
A bad shard key (low cardinality, skewed, or orthogonal to the queries) cannot be fixed by more
nodes — it caps you at the capacity of the busiest shard.

### 1.4 Hot shards and the celebrity / hot-key problem

Even a high-cardinality key can have a **skewed access distribution**: one value (a celebrity
user, a viral tweet, a single popular product) attracts a disproportionate share of traffic. All
that traffic hashes/ranges to **one** partition → that partition saturates while others idle →
you're back to a single-node `1/(1−ρ)` wall (13). Mitigations (each with a cost):
- **Key splitting / salting:** append a random suffix (`celebKey#0..#9`) to spread the hot key
  over R sub-partitions — converts a single hot read into a **scatter-gather** over R partitions
  (Cluster C) and pushes consistency work onto writes. You must un-salt on read.
- **Caching / read replicas** in front of the hot key (handoff to 16/08 + 15) — absorb reads
  before they hit the shard.
- **Dedicated shard / directory pinning:** isolate the celebrity onto its own node (only the
  directory strategy §1.2d can do this surgically).
**Verified by recomputation (factcheck):** with skew, the busiest-shard load — not the average —
sets capacity. If one key takes 30% of traffic on a 10-shard cluster, that shard does ~37.8% of
work (its 30% hot key **plus** its ~7.8% baseline share of the remaining 70%), while the other 9
split the rest (~7.8% each) — a **~4.86× imbalance**; adding nodes doesn't help the hot one.

### 1.5 Rebalancing — moving partitions without melting the cluster

When you add/remove nodes (or a shard grows hot/big), data must move. Constraints:
1. **Move as little as possible** (consistent hashing / fixed-partition schemes minimize this).
2. **Keep serving during the move** (dual-read/dual-write or hand-off, not stop-the-world).
3. **Don't trigger a cascade** (rebalancing itself adds load — a node failing under load that
   triggers a rebalance that overloads the next node is a classic outage amplifier).

Strategies:
- **Fixed number of partitions (> nodes):** create many more partitions than nodes up front
  (e.g. 1000 partitions on 10 nodes); rebalancing = *reassign whole partitions* between nodes,
  never split. Simple, predictable movement. `[UNVERIFIED]` Riak/Elasticsearch-style — blocked.
- **Dynamic partitioning:** split a partition when it exceeds a size threshold, merge when it
  shrinks (range schemes). Adapts to data volume; movement is variable. `[UNVERIFIED]`
  HBase/Bigtable tablet split — blocked.
- **Proportional to nodes (vnodes):** fixed vnodes per node; adding a node steals a few vnodes
  from each existing node. **Verified by recomputation:** consistent-hashing/vnode add moves
N→ ≈`1/N` of the data, spread across all donors. (Recomputed: add 1 node to N=10 vnode ring
  moved ~8.8% ≈ `1/(N+1)`; vnode load spread max/min ≈ 1.26×.)
- **Avoid full-automatic rebalancing under load** — many systems gate it behind an operator or
  rate-limit it, precisely because of the cascade risk.

### 1.6 Secondary indexes: local vs global

A shard key gives you *one* cheap access path (by that key). Any *other* query needs a secondary
index — and the index itself must be partitioned. Two designs, a fundamental tradeoff:

- **Local (document-partitioned) secondary index:** each partition indexes only *its own* data
  (`partition-local index`). 
  - **Writes are cheap:** an insert updates only the local index on the same partition (one node,
    can be in the same transaction).
  - **Reads are scatter-gather:** a query on the secondary attribute must hit **every** partition
    (none knows the global picture) and merge — read cost grows with N (read amplification, the
    "fan-out tail" from 13). 
- **Global (term-partitioned) secondary index:** the index is partitioned by the *indexed term*,
  independently of the base-data partitioning.
  - **Reads are cheap:** a query on the term goes to the *one* partition holding that term.
  - **Writes are expensive + cross-partition:** a single base-row insert may touch a *different*
    partition's index → distributed write, usually made **asynchronous** (the index lags the
    data → read-your-writes anomalies), because doing it synchronously needs a cross-partition
    transaction (Cluster C / 11).

> **The index tradeoff is the read/write tradeoff (Cluster A §1.4) at the partition level:**
> local = cheap write / expensive read; global = cheap read / expensive (and often async) write.
> `[UNVERIFIED from fetched source]` DynamoDB LSI/GSI, Cassandra secondary indexes,
> Elasticsearch routing — network-blocked.

## 2. Foundational sources

**Verified by recomputation this session** (`_factcheck_clusterAB.md`): `mod N` remap fraction
(~80% move on 4→5); consistent-hashing/vnode move fraction ≈`1/N`; hot-shard imbalance ratio
(30%-on-10-shards → ~3.9×); local-index read fan-out = N; salting → R-way scatter-gather.

**Verified by reuse (line-checked earlier — NOT re-fetched):**
- Consistent hashing + ring + virtual nodes — 06 `_research_probabilistic-distributed-queues.md`.
- Hash functions / uniformity / Bloom filters (for index/partition routing) — 06
  `_research_indexes-lsm-bloom.md`.
- LSM/B-tree as the per-partition storage engine — 06.
- Replication of each partition + quorum/consistency (a partition is usually *also* replicated —
  partitioning and replication are orthogonal and composed) — 11 `_research.md`.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals):**
- Karger et al., "Consistent Hashing and Random Trees" (STOC 1997) — original consistent hashing.
- DeCandia et al., "Dynamo" (SOSP 2007) — vnodes, partitioning + replication composition,
  hinted handoff (shared with 11/Cluster A/C carried-forward list).
- Chang et al., "Bigtable" (OSDI 2006) — tablets, range partitioning, splits.
- Vendor docs to pin: DynamoDB partitioning + adaptive capacity + LSI/GSI; Cassandra
  vnodes/partitioner/secondary indexes; HBase regions/splits; Elasticsearch shards/routing;
  Vitess/Citus sharding; MongoDB hashed vs ranged shard keys + chunk balancer.
- Kleppmann *DDIA* ch.6 (partitioning) for the synthesis framing + the local/global index split.

## 3. "Why it's this way" — the forcing functions

- **Partitioning exists because one node has a finite wall (13)**; the Z-axis is the only move
  that scales *dataset* and *write* capacity, not just read replicas.
- **`mod N` is unusable at scale because it remaps ~everything on resize** — consistent
  hashing/fixed-partitions exist to make the move fraction ≈`1/N`.
- **Hot shards exist because access skew is real (Zipf/celebrity)** and a placement function
  spreads *keys* uniformly, not *load* — load skew defeats key-uniformity.
- **The shard key is destiny because computed placement has no optimizer** — if the key doesn't
  match the query, the query fans out; you can't index your way out of a bad partition key.
- **Local vs global index is forced by physics:** the index either lives with the data (cheap
  write, scatter read) or with the term (cheap read, cross-partition write) — there is no design
  that makes both sides cheap without a cross-partition transaction (Cluster C / 11).
- **Rebalancing is gated because it adds load** — automatic rebalance under stress is an outage
  amplifier; minimal-movement schemes + rate limits exist to bound the blast radius.

## 4. Common misconceptions to preempt

- "Sharding = just add nodes and it scales." Only if the shard key spreads load; a bad key caps
  you at the busiest shard.
- "Hash partitioning fixes hot spots." It fixes *key* skew, not *access* skew — a celebrity key
  still lands on one partition.
- "`hash(k) mod N` is fine." It remaps ~all keys on resize; use consistent hashing / fixed
  partitions.
- "Consistent hashing spreads load evenly out of the box." No — a single point per node is
  lumpy; you need virtual nodes for smoothness.
- "More shards always help." Not the hot one — and more shards means wider scatter-gather for
  any non-shard-key query.
- "A secondary index is free like in a single DB." No — it's either scatter-gather reads (local)
  or cross-partition/async writes (global).
- "Partitioning and replication are the same thing." Orthogonal: partitioning splits the dataset;
  replication copies each partition for HA/reads. You almost always do both (11/15).
- "Rebalance automatically and aggressively." That's how a single node failure cascades into a
  cluster-wide outage.

## 5. Best build-your-own target(s)

- **`mod N` vs consistent-hashing rebalance visualizer:** insert K keys, add/remove a node, count
  how many keys move under each scheme; add vnodes and watch the load variance drop. The
  canonical "aha" lab; pairs with 06.
- **Hot-shard simulator:** drive a Zipfian key distribution at a sharded store, watch one shard
  saturate (13's `1/(1−ρ)`), then apply salting / dedicated-shard and measure the rebalanced
  load + the new read-side scatter cost.
- **Local-vs-global secondary-index lab:** same query two ways; measure write cost (local: 1
  node; global: cross-partition) vs read cost (local: fan-out N; global: 1 partition) and the
  staleness window of the async global index.

## 6. Open questions / gaps to close (preserved verbatim in intent)

- **All vendor + historical attributions are network-blocked** `[UNVERIFIED]`: Karger STOC 1997,
  Dynamo SOSP 2007, Bigtable OSDI 2006, and the DynamoDB/Cassandra/HBase/Elasticsearch/Mongo/
  Vitess/Citus docs above, plus Kleppmann DDIA ch.6. Teach mechanisms now (anchored by reused
  06/11 canon + recomputed math); do NOT harden vendor specifics/dates into Phase-2 prose.
- **Disagreement to resolve with sources:** load-balance quality of plain consistent hashing vs
  bounded-load vs rendezvous/HRW — pin the exact bounds; and the precise vnode-count guidance
  per system (it differs).
- **Boundary discipline (cross-link, do NOT duplicate):**
  - consistent-hashing *internals* live in **06**; this cluster *uses* them for placement.
  - a partition's *replication + consistency* (it's replicated too) is **11/15** — partitioning
    is orthogonal; this cluster only notes the composition.
  - *operations that span partitions* (scatter-gather, cross-shard joins/transactions,
    distributed query planning) are **Cluster C**.
  - the directory service's *consensus/coordination* backing is **11**; this cluster only states
    "the directory is itself a distributed system."
  - hot-key *caching/CDN* mitigation is **16/08**; *read-replica* mitigation is **15**.
