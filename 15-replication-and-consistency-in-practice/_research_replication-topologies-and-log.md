# 15 · Cluster A — Replication topologies & the replication log

> **Phase 1 brief (NO course prose).** Standard six sections. Cluster A of sub-course 15
> (replication-and-consistency-in-practice). This sub-course turns 11's consistency *theory* into
> *practice* and absorbs the consistency tax that 14's denormalization (Cluster A) and
> cross-partition operations (Cluster C) both hand off. Reuses line-verified canon from 11
> (consistency models, quorum = majority intersection, leader/log replication, Paxos/Raft, Spanner)
> and 14 (the write-side consistency obligation of duplicated data). Anything not fetched from a
> primary this session is marked `[UNVERIFIED from fetched source]` (network: only
> `lamport.azurewebsites.net` resolves; all DB-vendor/DDIA/academic hosts HTTP 000, 7th session).

## 1. Key mechanisms

### 1.1 Why replicate at all (the three independent goals)
Replication = keep a copy of the same data on more than one node. Three orthogonal motivations,
each of which alone justifies it and which pull design in different directions:
- **Availability / fault tolerance** — survive a node loss without losing the data or the service.
- **Read throughput / scale** — serve reads from many copies (the X-axis clone from 13).
- **Latency / locality** — put a copy near the reader (geo-replication).

Replication is **orthogonal to partitioning (14)**: you partition to fit the dataset + write load
across N nodes, and you replicate *each partition* R-ways for the three goals above. A real system
does both; this sub-course is the replication axis. *(Reuse 14 §"partitioning ≠ replication"; 11
§1.5 leader/log.)*

### 1.2 The three topologies (who may accept a write)
The single most important design choice is **where writes are allowed**:

1. **Single-leader (master–slave / primary–replica).** One node is the leader; all writes go to it;
   it streams a change log to followers; reads may go to leader or followers. Writes are *totally
   ordered by the leader* — no write conflicts by construction. This is the default of Postgres,
   MySQL, MongoDB replica sets, and (per-partition) most Raft-based systems. *(Reuse 11 §1.5: a
   leader is an ordering device.)*
2. **Multi-leader (master–master).** More than one node accepts writes (typically one leader per
   datacenter/region), and leaders replicate to each other. Buys write-availability + local write
   latency across regions, but **two leaders can accept conflicting writes** → conflict resolution
   becomes mandatory (Cluster C). Used for multi-DC active/active and offline-capable clients.
3. **Leaderless (Dynamo-style).** The client (or a coordinator) writes to *several* replicas
   directly and reads from *several*; correctness comes from **quorum overlap (W+R>N)** plus
   anti-entropy, not from a distinguished leader. No failover step — any node can take any request.
   Used by Dynamo, Cassandra, Riak, Voldemort. *(Reuse 11 §1.5 quorum = majority intersection;
   Dynamo primary `[UNVERIFIED]`.)*

The trade is **conflict-freedom vs write-availability**: single-leader avoids conflicts but the
leader is a write bottleneck + a failover liability; multi-leader/leaderless gain write
availability but must *resolve* concurrent writes.

### 1.3 Synchronous vs asynchronous (the durability/latency dial)
For each follower, the leader either waits for its ack before acking the client (**synchronous**)
or doesn't (**asynchronous**):
- **Sync** — guarantees the follower has the write; a client ack means ≥2 copies exist; but the
  write latency = slowest synchronous follower, and if that follower is down the write *stalls*.
- **Async** — leader acks immediately; lowest latency + stays available if followers lag/die; but
  if the leader fails after acking and before the write propagates, **that write is lost**
  (the durability window — recomputation note in §2 is structural, not numeric).
- **Semi-synchronous (the practical middle)** — make *one* follower synchronous and the rest async
  (Postgres `synchronous_standby_names`, MySQL semi-sync `[UNVERIFIED]`): you always have ≥1 extra
  durable copy without waiting on all followers. If the sync follower dies, another is promoted to
  sync.
- **Chain/quorum-ack** — ack after K of N followers (this is exactly the W knob in §1.4).

This is the same durability-vs-latency conservation 13 teaches for capacity: you can move the cost,
not erase it.

### 1.4 The replication log — what actually gets shipped
Followers stay in sync by replaying an ordered stream of changes. Four log formats, each with a
sharp trade:
- **Statement-based** — ship the SQL/command verbatim. Compact, but **nondeterministic statements
  diverge replicas**: `NOW()`, `RAND()`, autoincrement, triggers, `UPDATE ... LIMIT` without order
  evaluate differently on each node. (MySQL `STATEMENT` binlog; largely abandoned for this reason.)
- **Write-ahead-log shipping (physical)** — ship the storage engine's WAL (the byte-level page
  changes the engine already writes for crash recovery — reuse 07 storage/WAL + 06 B-tree pages).
  Exact and cheap, but **couples follower to the leader's exact storage format/version** → usually
  no cross-version replication, no cross-engine. (Postgres physical streaming replication.)
- **Logical / row-based** — ship the *logical row changes* (this row's columns went from X to Y),
  decoupled from physical layout. Allows version-skew, different storage, and **feeds change-data-
  capture (CDC)** to other systems — the bridge to 14's denormalization/materialized views and to
  17's event-driven fan-out. (MySQL `ROW` binlog; Postgres logical decoding / `pgoutput`.)
- **Trigger-based** — application-level capture; flexible, slowest, most error-prone; last resort.

The recurring lesson: **determinism is the whole game.** A replica is correct only if replaying the
log reproduces the leader's state exactly; statement-based breaks determinism, physical/logical
restore it at the cost of coupling/format work.

### 1.5 Read replicas & read-scaling (and the trap)
Pointing reads at followers is the cheapest scale-out (13 X-axis): reads grow with replica count
while all writes still serialize at one leader. The trap: **followers are asynchronously behind**,
so reading from them exposes replication lag → the anomalies in Cluster B. Read-scaling and
read-your-writes are in direct tension; you buy read throughput with staleness, then pay it back
with the routing fixes in Cluster B. Write throughput does **not** scale this way — for that you
must partition (14) or go multi-leader/leaderless.

## 2. Foundational sources

**Verified by recomputation this session** (`_factcheck_phase1.md`): the W-as-ack-threshold framing
is the same quorum object proven in Cluster C — `W+R>N ⇔ guaranteed overlap` (exhaustive). The
async durability window is structural (acked-but-unreplicated writes are lost on leader failure);
no numeric claim is made here.

**Verified by reuse (line-checked earlier — NOT re-fetched):**
- Leader = ordering device; quorum = majority intersection; Paxos/Raft turn a chosen value into a
  replicated log — 11 `_research.md` §1.5, `_research_consistency-replication-quorums.md`.
- WAL + page-level storage the physical log ships — 07 `_research_storage-query-exec.md`; B-tree
  pages — 06 `_research_indexes-lsm-bloom.md`.
- Replication ≠ partitioning; denormalized/duplicated data owes a write-side consistency tax that
  lands here — 14 `_research.md`, `_research_data-modeling.md`.
- X-axis (clone for read scale) vs Z-axis (shard) — 13 `_research_horizontal-vertical-akf-cube.md`.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carry forward:**
- Kleppmann, *DDIA* ch.5 (Replication) — the canonical taxonomy (single/multi/leaderless, sync/
  async, statement/WAL/logical/trigger logs, read-scaling).
- DeCandia et al., **Dynamo**, SOSP 2007 — leaderless model + quorum + N/R/W (also 11/14 carry).
- PostgreSQL docs — streaming/physical replication, `synchronous_standby_names`, logical decoding /
  `pgoutput` / `wal_level=logical`.
- MySQL docs — binlog formats (`STATEMENT`/`ROW`/`MIXED`), semi-synchronous replication.
- MongoDB docs — replica sets, oplog, write concern `w`/`j`.

## 3. Why it is this way — forcing functions
- **You replicate because one node is a single point of failure AND a `1/(1−ρ)` capacity wall (13)**
  — replication answers availability + read-scale + locality, three independent pressures.
- **Where writes land is the root choice** because it decides whether write *conflicts* can even
  exist: one leader ⇒ a total order for free; many writers ⇒ conflicts you must resolve.
- **Sync vs async exists because durability and latency are conserved** — you cannot have an
  instant ack *and* a guaranteed second copy; semi-sync picks the knee.
- **The log must be deterministic** because a replica is "correct" iff replay reproduces leader
  state — which kills statement-based and forces physical or logical formats.
- **Read replicas scale reads but not writes** because writes still serialize at the leader; that
  asymmetry is why 14 (partitioning) is the only write-scaling axis.

## 4. Common misconceptions to preempt
- "Replication gives you consistency." No — it gives you *copies*; consistency is the ordering/
  quorum/lag-handling rules layered on top (11). Replication alone gives eventual-at-best.
- "Replication and sharding are the same scaling move." Orthogonal: replication = copies of a
  partition (read-scale/HA); sharding = split the data (write-scale). You do both.
- "Async replication is just sync but faster." It has a real **data-loss window** on leader failure;
  the speed is paid in durability.
- "Statement-based replication is the obvious efficient choice." Nondeterministic statements
  silently diverge replicas; that's why row/logical formats won.
- "Read replicas scale the whole database." They scale *reads*; every write still hits one leader.
- "More read replicas = fresher reads." More replicas = more *lag surface*; freshness needs Cluster
  B's routing, not more copies.
- "Synchronous replication can't lose data, period." It still loses uncommitted writes; and a dead
  sync follower stalls writes unless you fail it out (availability cost).

## 5. Best build-your-own target(s)
- **Single-leader replicator**: a leader appends to an ordered log; followers tail and replay;
  measure follower lag under write load. (Pairs with 09 log, 07 WAL.)
- **Three-log bake-off**: replay the same workload via statement vs row vs WAL formats; inject
  `NOW()`/`RAND()` and watch statement-based replicas diverge.
- **Sync/async/semi-sync dial**: toggle ack threshold; plot write latency vs the durability window
  (kill the leader mid-flight to show async data loss).
- **Read-replica router stub**: route reads to followers and *see* a stale read appear — sets up
  Cluster B's fixes.

## 6. Open questions / gaps (do NOT erase)
- All DB-vendor + DDIA ch.5 + Dynamo primaries above are `[UNVERIFIED]` (network HTTP 000, 7th
  session). The *mechanisms/trade-offs* are verified by reuse of line-checked 06/07/11/13/14;
  the *exact vendor knobs/wording* (e.g. Postgres `synchronous_commit` levels, MySQL semi-sync
  ack timing, MongoDB oplog idempotence) must be pinned to docs before Phase 2 prose.
- Disagreement to resolve with sources: precise definition of "synchronous" across vendors (commit
  vs flush vs apply on the follower) — Postgres `synchronous_commit = remote_write|on|remote_apply`
  differ materially. Flag, do not flatten.
- Boundary: the *consensus internals* of Raft-based replicated logs ⇒ 11 (and appendix L); the
  *event/CDC fan-out* of the logical log ⇒ 17; *materialized-view* maintenance ⇒ 14/17. Cross-link,
  don't duplicate.
