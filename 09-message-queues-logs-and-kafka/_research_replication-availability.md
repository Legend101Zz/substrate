# Research Brief — Sub-course 09: Kafka Replication and Availability
## Source cluster: leader/follower replication, ISR, high watermark, acks, min ISR, leader epochs, KRaft/controller
## Researcher: researcher + brain validation | Date: 2026-06-10

---

## 1. Key Mechanisms

### 1.1 One leader orders each partition; followers pull

Kafka replicates at the topic-partition granularity. Under normal operation each partition has one leader and
zero or more followers. Producers write to the partition leader; followers replicate by issuing fetch requests
from the leader and appending the returned records to their own logs. The design doc also says reads can go to
leaders or followers; teach this carefully as rack-aware/nearest-replica fetch behavior in modern Kafka, not the
historical default assumption that followers routinely serve every consumer read.

Primary source anchors:
- Kafka 3.9 design doc: `docs/design/design.md` says the unit of replication is the topic partition, writes go
  to the leader, reads may go to followers, and followers consume from the leader like ordinary consumers.
  Source: `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md`.
- `ReplicaFetcherThread.processPartitionData()` appends fetched records through
  `partition.appendRecordsToFollowerOrFutureReplica(...)` and updates the follower high watermark from the
  leader response. Source:
  `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/ReplicaFetcherThread.scala`.
- `Partition.appendRecordsToLeader(...)` is the leader append path and calls `maybeIncrementLeaderHW(...)` after
  append. Source: `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/cluster/Partition.scala`.

### 1.2 ISR: Kafka's dynamic quorum, not a fixed majority quorum

Kafka maintains an in-sync replica set (ISR): replicas that are alive enough and caught up enough to the leader.
The design doc states that a write is not considered committed until all replicas in the ISR have received it,
and only ISR members are eligible for clean leader election.

Mechanics verified from `Partition.scala`:
- `maybeShrinkIsr()` removes followers that are not caught up within `replica.lag.time.max.ms`.
- `ReplicationConfigs.REPLICA_LAG_TIME_MAX_MS_DEFAULT = 30000L` in Kafka 3.9.
  Source: `https://raw.githubusercontent.com/apache/kafka/3.9/server/src/main/java/org/apache/kafka/server/config/ReplicationConfigs.java`.
- `maybeExpandIsr()` can re-add a follower after it reaches the leader high watermark and catches up to the
  current leader epoch start offset.
- ISR changes are not merely local variables: `Partition.scala` submits `AlterPartition` to the controller so the
  cluster agrees on the ISR update.

Kafka also has `maximalIsr` in `PartitionState`: a superset of committed ISR containing newly caught-up replicas
whose ISR expansion has been proposed but not yet committed. `maybeIncrementLeaderHW()` uses this to avoid
stalling high-watermark advancement while the `AlterPartition` response is in flight.

### 1.3 High watermark: the consumer-visible commit boundary

The high watermark (HW) is Kafka's per-partition "safe to expose" offset boundary. Consumers should not see
records that can be lost if the leader fails. In `Partition.scala`, the leader advances HW by taking the minimum
log-end offset across ISR/maximal-ISR replicas, and `UnifiedLog.maybeIncrementHighWatermark(...)` only moves it
forward. Followers do not calculate the same value independently; `ReplicaFetcherThread` updates follower HW from
the leader's fetch response.

Important nuance: a leader's log end offset can be ahead of HW. Those above-HW records are appended but not yet
committed from the consumer visibility perspective.

### 1.4 `acks` and `min.insync.replicas` are the producer-side safety knobs

Producer `acks` controls what acknowledgement means:

| `acks` | Meaning | Failure consequence |
|---|---|---|
| `0` | producer does not wait for broker acknowledgement | fire-and-forget; loss is invisible to the producer |
| `1` | leader acknowledges after local append | can lose records if leader dies before followers replicate |
| `all` / `-1` | leader waits for current ISR acknowledgement | strongest broker-side acknowledgement Kafka exposes |

Source: `ProducerConfig.ACKS_DOC` in
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java`.

`acks=all` means all **current ISR replicas**, not all assigned replicas. If ISR shrinks to one leader,
`acks=all` can degrade to leader-only durability. `min.insync.replicas` gates that case:
`Partition.appendRecordsToLeader(...)` throws `NotEnoughReplicasException` before append when
`requiredAcks == -1` and ISR size is below the effective min ISR. Kafka 3.9 default
`MIN_IN_SYNC_REPLICAS_DEFAULT = 1`, verified in
`https://raw.githubusercontent.com/apache/kafka/3.9/server-common/src/main/java/org/apache/kafka/server/config/ServerLogConfigs.java`.

### 1.5 Unclean leader election: explicit availability-over-consistency tradeoff

When every ISR member is unavailable, Kafka can either wait for an ISR replica to return or elect a non-ISR
replica and risk data loss. The design doc frames this as an availability vs. consistency tradeoff. Kafka 3.9
sets `LogConfig.DEFAULT_UNCLEAN_LEADER_ELECTION_ENABLE = false`.

ZK-mode controller code in `PartitionStateMachine.offlinePartitionLeaderElection(...)` first chooses a live ISR
replica; only if none exists and `uncleanLeaderElectionEnabled` is true does it choose any live assigned replica.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/controller/PartitionStateMachine.scala`.

KRaft internally tracks an unclean-election check interval in `ReplicationConfigs`:
`UNCLEAN_LEADER_ELECTION_INTERVAL_MS_DEFAULT = TimeUnit.MINUTES.toMillis(5)`. This config is registered with
`defineInternal(...)`, so do not teach it as a normal user-facing operator knob. The exact KRaft unclean-election
operator path was only partially traced; keep detailed operational claims `[UNVERIFIED]` unless the relevant
controller path is fetched.

### 1.6 Leader epochs repair log divergence after leader change

Leader epochs record which leader wrote which offset range. `LeaderEpochFileCache` stores a `TreeMap<Integer,
EpochEntry>`, where an `EpochEntry` records an epoch and the first offset for that epoch. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/epoch/LeaderEpochFileCache.java`.

On reconnect after leader change, `AbstractFetcherThread` can truncate using leader-epoch information:
- send/handle `OffsetsForLeaderEpoch` data,
- if the leader returns an undefined epoch offset, fall back to local high watermark,
- otherwise truncate to the safe epoch boundary or the min of leader and follower offsets for the epoch.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/AbstractFetcherThread.scala`.

Why this matters: HW can propagate asynchronously, so "truncate to your remembered HW" is not a complete
solution after leader changes. Epochs give a leadership-history coordinate system.

### 1.7 KRaft/controller split: data replication vs. metadata replication

KRaft replaces ZooKeeper-backed metadata coordination with a Kafka-managed metadata quorum. The 3.9 operations doc
states KRaft servers can be `controller`, `broker`, or combined; controllers participate in a metadata quorum, and
3 or 5 controllers are typically selected. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/docs/operations/kraft.md`.

Source anchors:
- `QuorumController.java` class comment: implements the main logic of KRaft mode controller.
  `https://raw.githubusercontent.com/apache/kafka/3.9/metadata/src/main/java/org/apache/kafka/controller/QuorumController.java`.
- `KafkaRaftClient.java` implements the controller metadata-log replication mechanics.
  `https://raw.githubusercontent.com/apache/kafka/3.9/raft/src/main/java/org/apache/kafka/raft/KafkaRaftClient.java`.
- `ReplicationControlManager.java` processes partition/ISR changes and emits metadata records.
  `https://raw.githubusercontent.com/apache/kafka/3.9/metadata/src/main/java/org/apache/kafka/controller/ReplicationControlManager.java`.

Do not conflate KRaft's metadata log HW with a topic partition's data HW. They are separate replicated logs with
similar vocabulary but different roles.

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| Replication design, ISR, committed messages, unclean election, acks | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md` | VERIFIED |
| Leader append, ISR shrink/expand, HW, min ISR | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/cluster/Partition.scala` | VERIFIED snippets |
| Follower fetch + HW update | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/ReplicaFetcherThread.scala` | VERIFIED snippets |
| Leader-epoch truncation | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/AbstractFetcherThread.scala`; `https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/epoch/LeaderEpochFileCache.java` | VERIFIED snippets |
| Producer ack semantics | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java` | VERIFIED |
| Defaults: lag time, unclean election interval, min ISR, unclean election | `ReplicationConfigs.java`, `ServerLogConfigs.java`, `LogConfig.java` under Kafka 3.9 | VERIFIED |
| ZK-mode clean/unclean election algorithm | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/controller/PartitionStateMachine.scala` | VERIFIED snippets |
| KRaft operations/controller sources | `docs/operations/kraft.md`, `QuorumController.java`, `ReplicationControlManager.java`, `KafkaRaftClient.java` | PARTIAL but source-backed |
| KIPs 101/497/500/595 | Apache cwiki KIPs | NOT all fetched; cite source code unless KIP body is directly read |

---

## 3. Why It’s This Way — Forcing Constraints

- **A single partition leader creates one ordering point.** Multi-writer per-partition ordering would require a
  consensus round per append; Kafka chooses leader-ordered append for throughput.
- **Followers pull to match their own capacity.** Pull lets followers batch and backpressure themselves instead of
  making the leader manage a push queue per follower.
- **ISR is a cost/performance compromise.** Majority protocols give crisp quorum math; Kafka's ISR model lets the
  effective commit set shrink, preserving availability and throughput, but puts more responsibility on min-ISR and
  unclean-election configuration.
- **HW prevents consumers seeing rollback-prone data.** Above-HW data exists but is not yet safe.
- **Leader epochs exist because offsets alone do not encode leadership history.** After failure, followers need to
  know not just "how far" they are but "which leader wrote this range."
- **KRaft moves metadata correctness into Kafka's own replicated log.** It removes a separate ZooKeeper dependency
  but introduces a second log/control plane to understand.

---

## 4. Common Misconceptions to Preempt

1. **“`acks=all` means all replicas.”** It means all in-sync replicas, not all assigned replicas.
2. **“High watermark equals leader log end offset.”** HW is a commit/visibility boundary and may lag LEO.
3. **“ISR is the same as a majority quorum.”** ISR is dynamically maintained and can shrink below a majority.
4. **“Unclean leader election is a harmless failover.”** It can permanently lose records not present on the elected replica.
5. **“Follower lag time means offline time only.”** ISR shrink uses caught-up-ness; a slow but alive follower can be removed.
6. **“KRaft means Kafka no longer has consensus concepts.”** KRaft *adds* a metadata Raft log while data partitions keep
   Kafka's leader/ISR model.

---

## 5. Build-Your-Own Targets

1. **Replicated partition toy:** one leader log, follower fetch loops, follower LEO tracking.
2. **High watermark calculator:** HW = min(LEO across ISR); consumers only read below HW.
3. **Acks purgatory:** hold `acks=all` responses until HW covers the appended offset; add min-ISR precheck.
4. **ISR shrink/expand simulator:** use lag timers and epoch-start offsets.
5. **Leader epoch truncation lab:** simulate divergent logs and repair with epoch→startOffset metadata.
6. **Unclean-election simulator:** prefer live ISR, optionally fall back to any live assigned replica and demonstrate loss.

---

## 6. Open Questions / Gaps

- Directly read KIP-101, KIP-497, KIP-500, and KIP-595 before using their design rationale as course claims.
- Trace the KRaft `PartitionChangeBuilder` / eligible-leader-replica behavior and feature defaults before teaching ELR.
- Trace preferred-replica election and controlled shutdown paths if they become course material.
- Distinguish exact Kafka version: this brief pins Kafka 3.9; Kafka 4.x removes/changes older ZooKeeper paths.
