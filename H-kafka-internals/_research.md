# Appendix H · kafka-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). H is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for "how ONE production
> distributed commit log — Apache Kafka (3.9) — actually stores, replicates, delivers, and does
> exactly-once," instantiating the transferable theory taught in spine **09** (MQ/logs/Kafka) and
> **17** (async/EDA), with quorum theory from **11/15** and appendix **L**. Spine 09/17 cross-link
> DOWN into H. Bespoke structure: **the distributed-log machine, layer by layer**, NOT four clusters
> and NOT a build progression. Math: `_recompute.py` (13/13). Factcheck: `_factcheck_phase1.md` (0
> blockers). Network: kafka.apache.org HTTP **000** this wave → constants reused from 09's
> line-verified Kafka 3.9 source/docs reads; the Kafka paper/KIPs stay `[UNVERIFIED]` (owed).

## 1. Thesis
Kafka is not a queue; it is a **replicated, partitioned, retained append-only log**. Everything
follows from inverting the classic broker: instead of deleting a message after one consumer acks,
Kafka **retains records by policy and makes consumers track their own position (offset)**. That single
inversion buys replay, multiple independent consumers, and disk-friendly **sequential** I/O — and
shifts correctness (offsets, delivery semantics) onto the client. Durability comes from **ISR
replication + high watermark**; exactly-once comes from **idempotent producers + transactions** layered
on the log.

## 2. The distributed-log machine (the bespoke spine)

### Layer 1 — The partitioned, retained log (09)
- A topic = N **partitions**; each partition is an ordered append-only log addressed by **offsets**.
  Ordering is **per-partition only** (no global topic order). Offsets are positions, not message IDs.
- RECOMPUTED: partitions are the **unit of parallelism** — a partition is assigned to at most one
  consumer in a group → max useful consumers = #partitions (a 13th on 12 partitions sits idle). Global
  order would serialize throughput; partitioning trades order for parallelism.

### Layer 2 — Segments + retention/compaction (09)
- A partition log = closed **segments** + one active segment, each with a base offset and sparse
  offset/time indexes (locate segment, then read sequentially).
- RECOMPUTED: retention deletes **whole closed segments** (O(1) unlink), not row-by-row — a 10 GiB
  log = 10 segments, expire oldest = 1 unlink. WHY segments exist: cheap lifecycle ops.
- **Log compaction** (keyed streams, `LogCleaner.scala`): record with key K at offset O is obsolete if
  a later K exists at O′>O; cleaner builds key→last_offset and recopies segments omitting obsoletes.
  Tombstones delete; active segment is never cleaned.

### Layer 3 — ISR replication + the durability contract (09/11/15/L)
- Per partition: one **leader** orders writes; followers **fetch** from the leader (pull). The
  **in-sync replica set (ISR)** is Kafka's dynamic commit set.
- Producer contract: `acks=0` (none) / `acks=1` (leader local) / `acks=all` (current ISR);
  `min.insync.replicas` rejects `acks=all` writes if ISR is too small.
- RECOMPUTED: `RF=3, min.insync.replicas=2, acks=all` (the canonical durable config) survives **1**
  broker failure with **no data loss** and still accepts writes; lose 2 → writes rejected (availability
  sacrificed for durability).
- **Why ISR, not majority?** RECOMPUTED: to tolerate f failures, **ISR needs f+1 replicas** (all
  in-sync ack) vs **majority's 2f+1** (f=2 → 3 vs 5). ISR trades "latency of the slowest in-sync
  replica" for fewer nodes — a different quorum than Paxos/Raft majority (cf 11/L).

### Layer 4 — High watermark + leader epochs (09)
- The **high watermark (HW)** is the consumer-visible boundary: records ≤HW are committed/replicated.
  RECOMPUTED: **HW ≤ leader LEO** — a leader may hold 1005 records but HW=1000 hides the 5
  un-replicated ones → no dirty reads, safe failover.
- **Leader epochs** add a leadership-history coordinate so a reconnecting follower truncates to a safe
  point after a leader change (offsets alone don't say which leader wrote which range).
- **Unclean leader election** (disabled by default): promoting a stale out-of-ISR replica can lose
  committed-looking data — the analogue of Redis promoting a stale replica (G).

### Layer 5 — Consumer groups + offsets (09)
- A consumer group is a logical reader; one partition → at most one member per group; different groups
  consume independently. Group state + committed offsets live in the compacted topic
  `__consumer_offsets`.
- RECOMPUTED routing: `abs(groupId.hashCode()) % 50` (50 offsets partitions) → the broker leading
  that partition is the group's **coordinator**.
- **Position vs committed offset**: position = next offset to fetch; committed = durable restart
  checkpoint. RECOMPUTED: after processing offset 42, commit **43** (next to read). Client
  `records-lag` is based on fetch position, not committed offset — they diverge.
- **Rebalance**: eager (revoke all, stop-the-world) vs cooperative (revoke only moved partitions).
  The 3.9 server-side `CONSUMER` protocol (KIP-848) is early-access (`[UNVERIFIED]` rationale).

### Layer 6 — Delivery semantics (09/17)
- RECOMPUTED: under at-least-once with retries, **duplicates are near-certain at scale** —
  P(≥1 dup) = 1−(1−p)^N ≈ 1.000 for N=1e5, p=1e-4. This is WHY the idempotent producer exists.
- **At-most-once** (commit before processing) / **at-least-once** (process then commit) /
  **exactly-once** (idempotent producer + transactions + `read_committed`).

### Layer 7 — Idempotence + transactions = EOS (09/17)
- **Idempotent producer**: records carry `(producerId, epoch, sequence)`; broker tracks last sequence
  per `(pid, partition)` to reject retry duplicates; **epoch fences zombies**. → exactly-once *into*
  Kafka.
- **Transactions**: a coordinator + `__transaction_state` make **consume-transform-produce** atomic —
  output records + input offset commit land together (or not). `read_committed` consumers read to the
  **LSO** (last stable offset) and skip aborted txns; aborted data stays physically in the log,
  visibility controlled by markers/indexes.
- RECOMPUTED + crucial caveat: Kafka's EOS boundary is **Kafka topics + offsets only**. A side effect
  to an external sink (DB row, email) is **outside** the transaction → still needs idempotence or
  external coordination.

### Layer 8 — KRaft (09)
- Data partitions use the leader/ISR/HW model above; **KRaft** replaces ZooKeeper with a **separate
  Raft metadata quorum** + metadata log (3 or 5 controllers). Do NOT conflate a data-partition HW with
  the KRaft metadata-log HW. Deep KRaft internals `[UNVERIFIED]` (carried from 09).

## 3. The "retained log inverts the broker" reconciliation (appendix payload)
| layer | mechanism | what the inversion buys / costs | anchor |
|---|---|---|---|
| log | partitioned offsets | parallelism vs global order | 09 |
| storage | segments + compaction | cheap retention vs offset mgmt | 09 |
| replication | ISR + acks + min.isr | f+1 nodes vs majority's 2f+1 | 09/11/15/L |
| safety | HW ≤ LEO + epochs | no dirty reads vs hidden tail | 09 |
| consumers | groups + `__consumer_offsets` | independent replay vs client correctness | 09 |
| delivery | at-least/most/exactly-once | dups certain → idempotence | 09/17 |
| EOS | idempotent producer + txns | atomic in-Kafka, NOT external | 09/17 |
| metadata | KRaft Raft quorum | no ZK vs separate consensus | 09 |

## 4. Common misconceptions to preempt
- "Kafka is a queue." Queue behavior is one pattern over a **retained log**.
- "A topic has one total order." Ordering is **per-partition**.
- "Offsets are message IDs." They're partition positions (need topic+partition context).
- "`acks=all` means all replicas." It means all **current ISR** replicas; `min.insync.replicas` sets
  the floor.
- "HW = leader end offset." HW ≤ LEO; HW hides under-replicated records.
- "ISR is a majority quorum." ISR is dynamic and can shrink below majority.
- "Committed offset = last processed." It's the **next** offset to fetch (processed + 1).
- "Exactly-once means no duplicates anywhere." EOS covers Kafka topics + offsets; external sinks need
  idempotence.
- "Unclean leader election is normal failover." It can lose committed-looking data.

## 5. Provenance summary
- **REUSED (line-verified in 09, apache/kafka 3.9 source/docs):** segmented log, ISR/HW/acks/min.isr,
  leader epochs, `__consumer_offsets` routing, idempotent producer + transactions + LSO, KRaft model.
- **REUSED (local primaries):** 17 delivery-semantics math; Nishtala NSDI'13 (herd 17K→1.3K, reused
  for failover refresh storms). Quorum intersection from 11/15/L.
- **RECOMPUTED:** `_recompute.py` (13/13).
- **`[UNVERIFIED]` carry-forward (not load-bearing):** Kafka original paper (kafka.apache.org HTTP
  000, mirror retry still owed); KIP rationale (KIP-98/101/500/848/360); KRaft deep internals + ELR;
  fetch-from-follower path; transaction recovery + sticky assignor; exact `segment.bytes`. Logged,
  none hardened.

---
**Appendix H reconciled.** Reference-grade, exercise-free, 13/13 recomputed, log/ISR/EOS cores from
09's line-verified Kafka 3.9 source reads. Kafka paper/KIP fetches still blocked (kafka.apache.org
000), carried `[UNVERIFIED]`. No chapters yet.
