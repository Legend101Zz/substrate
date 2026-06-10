# Research Brief — Sub-course 09: Kafka Consumer Groups and Offsets
## Source cluster: group coordinator, `__consumer_offsets`, commits, rebalances, lag, replay, fetch isolation
## Researcher: researcher + brain validation | Date: 2026-06-10

---

## 1. Key Mechanisms

### 1.1 Consumer groups separate two scaling axes

Kafka retains records by topic policy, not by per-consumer acknowledgement. A consumer group gives one application
a logical shared position over a topic while allowing many consumer processes to split the partitions. Different
groups read the same retained log independently; members inside one group divide work so one partition is assigned
to at most one member at a time.

The Kafka 3.9 design doc describes this as the consumer specifying offsets in fetch requests and controlling its
position; it also notes that each partition is consumed by exactly one consumer within a subscribing group at a
given time. Source: `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md`.

### 1.2 Group coordinator ownership comes from `__consumer_offsets` partition leadership

Kafka stores group state in the internal topic `__consumer_offsets` (`Topic.GROUP_METADATA_TOPIC_NAME`). A group
maps to one offsets partition using:

```java
Utils.abs(groupId.hashCode()) % numPartitions
```

The broker leading that offsets partition coordinates the group. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorService.java`.

Important verified defaults and configs:
- `GroupCoordinatorConfig.OFFSETS_TOPIC_PARTITIONS_DEFAULT = 50`.
- `GroupCoordinatorConfig.OFFSETS_TOPIC_SEGMENT_BYTES_DEFAULT = 100 * 1024 * 1024`.
- `OFFSETS_RETENTION_MINUTES_DEFAULT = 7 * 24 * 60`.
- `GroupCoordinatorService` sets `TopicConfig.CLEANUP_POLICY_CONFIG` to `TopicConfig.CLEANUP_POLICY_COMPACT` for
  the offsets topic; classic `GroupCoordinator.offsetsTopicConfigs()` also sets compact cleanup.
Sources:
`https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorConfig.java`,
`https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/coordinator/group/GroupCoordinator.scala`.

### 1.3 `__consumer_offsets` is a compacted log of offsets and group metadata

Offset commit records key by `(groupId, topic, partition)` and value includes committed offset, leader epoch,
metadata, commit timestamp, and version-dependent expiration fields. Null values/tombstones delete offsets.
`CoordinatorRecordHelpers.newOffsetCommitRecord(...)` constructs these records using `OffsetCommitKey` and
`OffsetCommitValue`. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/CoordinatorRecordHelpers.java`.

The offsets topic also stores modern group metadata and target/current assignment records. So it is not merely a
small checkpoint table; it is the coordinator's durable state log.

### 1.4 Committed offset and fetch position are different clocks

Kafka clients maintain a **position**: the next offset the consumer will fetch. The group coordinator stores a
**committed offset**: the restart checkpoint. When a consumer processes record offset `N`, the value it should
commit after processing is `N + 1` — the next record to read.

A Kafka client metric confirms the distinction: `FetchMetricsRegistry.records-lag-max` says lag is based on
current offset, not committed offset. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchMetricsRegistry.java`.

Implication: a consumer can show low fetch lag while still having risky commit lag if it reads far ahead but has
not durably committed positions.

### 1.5 Offset commit/fetch path

The consumer sends `OffsetCommitRequest` to the group coordinator. The request schema has
`GenerationIdOrMemberEpoch`, `MemberId`, optional `GroupInstanceId`, and per-partition committed offsets.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/resources/common/message/OffsetCommitRequest.json`.

`OffsetMetadataManager.commitOffset(...)` validates the group/member state and returns coordinator records to be
appended to `__consumer_offsets`. `OffsetMetadataManager.fetchOffsets(...)` reads from its timeline state and can
return `UNSTABLE_OFFSET_COMMIT` when a stable fetch sees a pending transactional offset commit. Missing offsets
return `INVALID_OFFSET`. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/OffsetMetadataManager.java`.

Auto commit is a client behavior, not broker magic. `CommitRequestManager` performs interval-based async commits
and can sync commit before partition revocation. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/internals/CommitRequestManager.java`.

### 1.6 Classic group rebalance: join, assign, sync, heartbeat

Classic groups use a group-level state machine verified in `ClassicGroupState.java`:

```text
EMPTY → PREPARING_REBALANCE → COMPLETING_REBALANCE → STABLE
  ↘                                      ↗
    DEAD can be reached from active states
```

Valid transitions include:
- `PREPARING_REBALANCE` from `STABLE`, `COMPLETING_REBALANCE`, or `EMPTY`.
- `COMPLETING_REBALANCE` from `PREPARING_REBALANCE`.
- `STABLE` from `COMPLETING_REBALANCE`.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/classic/ClassicGroupState.java`.

The classic protocol separates membership discovery (`JoinGroup`) from assignment distribution (`SyncGroup`). In
classic groups, the leader consumer computes assignment client-side using the chosen partition assignor and sends
the assignment map through `SyncGroup`.

### 1.7 Eager vs. cooperative classic rebalance

`ConsumerPartitionAssignor.RebalanceProtocol` has:
- `EAGER((byte) 0)`: revoke owned partitions before reassignment; stop-the-world for the group.
- `COOPERATIVE((byte) 1)`: retain partitions that do not need to move; moved partitions require revocation then
  reassignment across one or more rounds.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/ConsumerPartitionAssignor.java`.

`CooperativeStickyAssignor.supportedProtocols()` returns `[COOPERATIVE, EAGER]` and warns that upgrades from older
versions need a specific path. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/CooperativeStickyAssignor.java`.

### 1.8 New consumer group protocol in 3.9: early access, not default production guidance

Kafka 3.9 includes a modern `CONSUMER` group protocol (`GroupProtocol.CONSUMER`) and
`ConsumerGroupHeartbeat` API key 68. It uses member epochs and server-side assignment/reconciliation instead of
classic `JoinGroup`/`SyncGroup` leader-side assignment. Sources:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/GroupProtocol.java`,
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/resources/common/message/ConsumerGroupHeartbeatRequest.json`.

But be conservative: `GroupCoordinatorConfig` says the consumer rebalance protocol is early access and "must not
be used in production." Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorConfig.java`.

Modern member states include `STABLE`, `UNREVOKED_PARTITIONS`, and `UNRELEASED_PARTITIONS`. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/modern/MemberState.java`.
Migration policy values are `disabled`, `upgrade`, `downgrade`, and `bidirectional`; default needs exact config
trace before teaching as a hard claim.

### 1.9 Fetch isolation, lag, and replay

`FetchRequest.json` adds `IsolationLevel` in version 4:
- `READ_UNCOMMITTED` (`0`) exposes all records up to the high watermark.
- `READ_COMMITTED` (`1`) exposes non-transactional and committed transactional records; it uses last stable offset.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/resources/common/message/FetchRequest.json`.

`FetchResponse.json` defines `LastStableOffset` as the last offset such that all prior transactional records have
been decided, and carries `AbortedTransactions`. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/resources/common/message/FetchResponse.json`.

`CompletedFetch.java` filters aborted transactional batches for `READ_COMMITTED` consumers using aborted producer
IDs. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/internals/CompletedFetch.java`.

Replay is a first-class consequence of retained logs: the consumer can seek to earlier offsets if the data remains
within retention. With no valid committed offset, `OffsetResetStrategy` provides `LATEST`, `EARLIEST`, and `NONE`.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/consumer/OffsetResetStrategy.java`.

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| Design: consumers control position, group partition ownership | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md` | VERIFIED |
| Internal topic name | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/common/internals/Topic.java` | VERIFIED |
| Coordinator routing + offsets topic config | `GroupCoordinatorService.java`, `GroupCoordinatorConfig.java`, `GroupCoordinator.scala` under Kafka 3.9 | VERIFIED |
| Offset commit/fetch manager | `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/OffsetMetadataManager.java` | VERIFIED snippets |
| Offset record construction | `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/CoordinatorRecordHelpers.java` | VERIFIED |
| Classic rebalance state machine | `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/classic/ClassicGroupState.java` | VERIFIED |
| Eager/cooperative protocol | `ConsumerPartitionAssignor.java`, `CooperativeStickyAssignor.java` under Kafka 3.9 | VERIFIED |
| Modern consumer protocol | `ConsumerGroupHeartbeatRequest.json`, `MemberState.java`, `GroupProtocol.java` | VERIFIED source presence; production status = early access |
| Fetch isolation and lag | `FetchRequest.json`, `FetchResponse.json`, `CompletedFetch.java`, `FetchMetricsRegistry.java` | VERIFIED |

---

## 3. Why It’s This Way — Forcing Constraints

- **Offsets live in Kafka to avoid split-brain delivery state.** The same replicated log machinery stores group
  checkpoints and can be replayed after coordinator failover.
- **Hashing group IDs to offsets partitions avoids a separate coordinator directory.** Partition leadership already
  gives ownership and failover.
- **Committed offset = next-to-read.** This makes restart simple: fetch begins exactly where the consumer says.
- **Classic rebalance uses a barrier because assignment needs all subscriptions.** The cost is stop-the-world churn.
- **Cooperative rebalance exists to reduce unnecessary revocation.** It accepts multi-round convergence to keep
  unaffected partitions running.
- **LSO exists because transactional data may be physically present before its commit/abort decision is known.**

---

## 4. Common Misconceptions to Preempt

1. **“Offsets are stored in ZooKeeper.”** Modern Kafka stores consumer group offsets in `__consumer_offsets`; be
   version-specific if discussing old Kafka.
2. **“Committed offset is the last processed offset.”** It is the next offset to fetch after restart.
3. **“Lag always means high watermark minus committed offset.”** Kafka client `records-lag` is based on current
   fetch position, not committed offset.
4. **“Every group gets a unique coordinator broker.”** Many groups hash to the same offsets partition/coordinator.
5. **“Cooperative rebalance means no pausing.”** Only partitions not moving keep running.
6. **“The new consumer group protocol is safe to recommend broadly in 3.9.”** Kafka 3.9 source labels it early
   access and not for production.
7. **“Read committed consumers just hide aborted records.”** They are bounded by LSO; long open transactions can
   stall progress before filtering even happens.

---

## 5. Build-Your-Own Targets

1. **Offset store:** compacted log keyed by `(group, topic, partition)` with commit/fetch APIs.
2. **Coordinator sharding:** hash group IDs to N partitions and move ownership on partition leadership changes.
3. **Classic rebalance simulator:** implement EMPTY/PREPARING/COMPLETING/STABLE states, join/sync/heartbeat.
4. **Cooperative rebalance visualizer:** revoke only moved partitions, converge over rounds.
5. **Lag calculator:** show fetch-position lag vs committed-position lag.
6. **Fetch isolation toy:** implement HW vs LSO read boundaries and aborted-transaction filtering.

---

## 6. Open Questions / Gaps

- Trace `CoordinatorRuntime` threading/snapshot mechanics before teaching internal concurrency.
- Trace exact offset expiration scanner path; defaults and docs are verified, scheduler internals are not.
- Read/verify full sticky assignor algorithm if assignment strategy details become chapter material.
- Trace static membership (`group.instance.id`) fencing behavior before teaching it deeply; basic source hooks are visible but not fully followed.
- Recheck modern consumer group protocol status when pinning course version; Kafka 3.9 says early access.
