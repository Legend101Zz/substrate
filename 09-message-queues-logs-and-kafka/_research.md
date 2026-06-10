# Sub-course 09 Research Synthesis — Message Queues, Logs, and Kafka
## Phase 1 reconciled corpus | Date: 2026-06-10

Source cluster briefs reconciled:
- `_research_log-abstraction-kafka-storage.md`
- `_research_replication-availability.md`
- `_research_consumer-groups-offsets.md`
- `_research_delivery-semantics-transactions.md`
- `_factcheck_phase1.md`

Scope note: this synthesis pins Apache Kafka **3.9** source/docs where version-sensitive. Trunk/4.x paths and
ZooKeeper/KRaft status differ. Course prose must preserve those version caveats instead of pretending Kafka is one
unchanging golden retriever. It is not. It has opinions and migrations.

---

## 1. Key Mechanisms

### 1.1 Kafka's core abstraction is a retained partitioned log

Kafka treats a topic as one or more partitions. Each partition is an ordered append-only log addressed by offsets.
Offsets are positions within one partition, not global message IDs. Ordering is therefore per partition, not per
multi-partition topic.

The original Kafka paper and Kafka design docs ground the important inversion: instead of a broker deleting a
message after one consumer acknowledges it, the broker retains records by policy and consumers track where they
are. This enables replay and independent consumer groups, but shifts responsibility for processing correctness to
consumer offset management.

Kafka 3.9 source preserves the storage model:
- `LocalLog.scala`: append-only local log made of `LogSegment`s, each with a base offset.
- `LogSegment.java`: segment-level records plus offset/time indexes.
- `LogConfig.java`: segment sizing/rolling, retention time/size, compaction controls.

### 1.2 Storage is segment-based because retention and compaction need coarse units

A partition log is split into closed segments plus an active segment. Segment boundaries make retention practical:
Kafka can delete whole closed segments by time/size policy rather than rewriting a giant file. Sparse indexes map
logical offsets to file positions; reads locate the segment then read sequentially.

Log compaction is a second retention mode for keyed streams. `LogCleaner.scala` says a record with key K at offset
O is obsolete if a later record with key K exists at O′ where O < O′. Cleaner threads build a key→last_offset map
for dirty sections and recopy segments, omitting obsolete records. Tombstones mark deletes and have retention
rules. Active segments are not cleaned.

### 1.3 Replication: one leader orders writes; ISR defines committed data

Kafka replicates per topic partition. Under normal operation one replica is leader. Producers write to the leader;
followers fetch from the leader and append locally. Kafka 3.9 docs allow reads from leaders or followers, but this
must be taught as modern nearest/rack-aware follower fetching behavior, not as the historical default mental model.

The in-sync replica set (ISR) is Kafka's dynamic commit set. The high watermark (HW) is the consumer-visible
boundary: records at or below HW are committed; leader log-end offset can be ahead of HW. `Partition.scala`
advances leader HW by considering ISR/maximal-ISR replica log-end offsets; `ReplicaFetcherThread.scala` updates
follower HW from leader fetch responses.

`acks` and `min.insync.replicas` form the producer-facing durability contract:
- `acks=0`: no broker acknowledgement.
- `acks=1`: leader local append acknowledgement.
- `acks=all`/`-1`: acknowledgement after current ISR replicas have replicated.
- `min.insync.replicas`: rejects `acks=-1` writes before append if ISR is below threshold.

Kafka 3.9 defaults checked: `acks="all"` for producer config, `enable.idempotence=true`,
`min.insync.replicas=1`, `replica.lag.time.max.ms=30000`, unclean leader election disabled.

### 1.4 Leader epochs repair divergence after failures

Offsets alone do not encode which leader wrote which range. Leader epochs add a leadership-history coordinate
system. `LeaderEpochFileCache` stores epoch entries; `AbstractFetcherThread` uses leader-epoch responses to find
safe truncation points after a follower reconnects to a new leader. If epoch data is unavailable, Kafka can fall
back to high watermark, but exact course claims about this path must cite the source logic.

### 1.5 KRaft separates metadata replication from data-partition replication

Kafka's data partitions use the leader/ISR/HW model above. KRaft uses a separate metadata quorum and metadata log
for cluster metadata. In Kafka 3.9, servers can be brokers, controllers, or combined; production guidance generally
selects 3 or 5 controllers. `QuorumController.java`, `KafkaRaftClient.java`, and `ReplicationControlManager.java`
anchor the source view. Do not conflate a data partition HW with a KRaft metadata log HW.

### 1.6 Consumer groups make retained logs behave like scalable subscriptions

A consumer group is a logical reader made of one or more members. One partition is assigned to at most one member
inside a group at a time; different groups consume independently.

`__consumer_offsets` stores group offsets and group metadata as a compacted Kafka topic. Group IDs route to
coordinators by hashing to an offsets partition:

```java
Utils.abs(groupId.hashCode()) % numPartitions
```

The broker leading that offsets partition coordinates the group. Kafka 3.9 defaults checked: 50 offsets topic
partitions, 100MB offsets topic segments, 7-day offsets retention.

### 1.7 Offset position and committed offset are not the same

A consumer's **position** is the next offset it will fetch; it advances as records are returned by `poll()`. A
**committed offset** is the durable restart checkpoint stored in `__consumer_offsets`. The committed value should
be the next offset to read after successful processing: after processing offset N, commit N+1.

Kafka client `records-lag` metrics are based on current fetch position, not committed offset. This means fetch lag
and commit lag can diverge.

### 1.8 Rebalancing trades availability for assignment correctness

Classic consumer groups use a state machine (`EMPTY`, `PREPARING_REBALANCE`, `COMPLETING_REBALANCE`, `STABLE`,
`DEAD`) and a join/sync/heartbeat protocol. Classic assignment is client-side: the group leader computes the
assignment and sends it through `SyncGroup`.

Rebalance protocols:
- **Eager:** revoke all partitions before reassignment; simple but stop-the-world.
- **Cooperative:** revoke only partitions that must move; unaffected partitions continue; convergence may take
  multiple rounds.

Kafka 3.9 also contains a modern `CONSUMER` group protocol with `ConsumerGroupHeartbeat` API key 68, member
epochs, and server-side assignment/reconciliation. But Kafka 3.9 source labels it early access and not for
production, so it is a "know it exists" topic, not a default recommendation.

### 1.9 Delivery semantics are scoped failure contracts

Kafka's delivery semantics depend on producer ack/retry/idempotence, consumer processing/commit order, and whether
side effects stay inside Kafka.

- **At-most-once:** commit/advance before processing or fire-and-forget producer writes; loss is possible.
- **At-least-once:** process then commit, or retry ambiguous producer writes without idempotence; duplicates are possible.
- **Exactly-once/effectively-once in Kafka:** requires idempotent producer + transactions + `read_committed` consumers
  + transactional offset commits for consume-transform-produce loops. External sinks still require idempotence or
  external transaction coordination.

### 1.10 Idempotence and transactions are log protocols layered on the log

Idempotent producer records include producer id, producer epoch, and base sequence. Broker-side producer state
tracks last sequence/offset per partition to reject duplicate or out-of-order appends. Epochs fence zombie
producer instances.

Transactions add a coordinator and `__transaction_state`. Transaction state moves through `Empty`, `Ongoing`,
`PrepareCommit`, `PrepareAbort`, `CompleteCommit`, `CompleteAbort`, `Dead`, and `PrepareEpochFence`. Commit/abort
markers are written as control batches to affected partitions. Aborted data remains physically in the log; read
visibility is controlled by LSO and aborted-transaction indexes.

`UnifiedLog.lastStableOffset` equals the first unstable transaction offset if below HW, otherwise HW. `read_committed`
consumers read to LSO and skip aborted transactions; `read_uncommitted` consumers read to HW.

---

## 2. Foundational Sources

| Area | Source | Why it matters |
|---|---|---|
| Kafka paper | Kreps, Narkhede, Rao, “Kafka: a Distributed Messaging System for Log Processing” (`https://notes.stephenholiday.com/Kafka.pdf`; canonical URL still preferred if accessible) | Original partitioned-log design and performance motivation |
| Kafka design doc | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md` | Official design narrative: log, consumer position, semantics, replication, compaction |
| Kafka implementation log doc | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/implementation/log.md` | Offset-as-id, segment/index mechanics |
| Local log | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LocalLog.scala` | Kafka 3.9 append-only log/segment model |
| Segment/log config | `LogSegment.java`, `LogConfig.java` under Kafka 3.9 | Segments, indexes, retention and compaction knobs |
| Log cleaner | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LogCleaner.scala` | Compaction mechanics |
| Partition replication | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/cluster/Partition.scala` | Leader append, ISR shrink/expand, HW, min ISR |
| Follower fetch | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/ReplicaFetcherThread.scala` | Pull replication and follower HW update |
| Leader epochs | `LeaderEpochFileCache.java`, `AbstractFetcherThread.scala` under Kafka 3.9 | Divergence repair/truncation |
| Producer config | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java` | `acks`, idempotence defaults and constraints |
| KRaft | `docs/operations/kraft.md`, `QuorumController.java`, `KafkaRaftClient.java`, `ReplicationControlManager.java` | Metadata quorum/controller model |
| Consumer groups | `GroupCoordinatorService.java`, `GroupCoordinatorConfig.java`, `OffsetMetadataManager.java`, `ClassicGroupState.java` | Coordinator routing, offsets, commits, rebalance states |
| Consumer protocol schemas | `OffsetCommitRequest.json`, `FetchRequest.json`, `FetchResponse.json`, `ConsumerGroupHeartbeatRequest.json` | Wire-level fields for commits, fetch isolation, modern protocol |
| Transactions | `TransactionCoordinator.scala`, `TransactionLog.scala`, `TransactionMetadata.scala`, `TransactionStateManager.scala` | Transaction coordinator and durable state machine |
| Idempotence | `DefaultRecordBatch.java`, `ProducerAppendInfo.java`, `ProducerStateManager.java` | Producer ids, epochs, sequence validation |
| LSO/markers | `UnifiedLog.scala`, `FetchIsolation.java`, `EndTransactionMarker.java`, `TransactionIndex.java`, `AbortedTxn.java` | Read-committed mechanics and abort filtering |
| KIP-98 | `https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging` | Design rationale for idempotence/transactions; cross-check with code |

---

## 3. Why It’s This Way — Constraints

- **Sequential IO and batching dominate broker design.** A log maps producer appends and consumer scans to storage
  patterns that disks, SSDs, and OS page cache handle well.
- **Retention decouples consumption from deletion.** Consumers can replay and multiple groups can consume at
  different speeds; the price is offset management and storage lifecycle policy.
- **Partitions are the scalability unit.** One total order would bottleneck throughput and recovery; partitioning
  trades global order for parallelism.
- **Segments make lifecycle operations cheap.** Delete and compact closed chunks instead of rewriting a monolith.
- **ISR is a practical quorum compromise.** Kafka avoids full majority consensus on every data append but must
  manage ISR, min ISR, and unclean election carefully.
- **HW/LSO hide unsafe data.** HW hides under-replicated records; LSO hides undecided transactional records.
- **Consumer groups need durable membership and offset state.** Storing it in a compacted Kafka topic lets the
  coordinator rebuild state by replay rather than depending on a separate database.
- **Rebalances must avoid double ownership.** Eager rebalance is simple but disruptive; cooperative rebalance keeps
  stable ownership but needs multiple rounds.
- **Idempotence needs compact producer state, not per-message memory.** Producer id + epoch + sequence gives enough
  information to detect retry duplicates and fence zombies.
- **Exactly-once needs atomic offset + output commit.** Otherwise consume-transform-produce has a crash window between
  producing output and saving input position.

---

## 4. Misconceptions

1. **“Kafka is just a queue.”** Queue behavior is one pattern over a retained log.
2. **“A topic has one total order.”** Ordering is per partition unless the application imposes a higher-level order.
3. **“Offsets are message IDs.”** They are partition positions; meaningful only with topic+partition context.
4. **“Consumed means deleted.”** Kafka deletion is retention/compaction policy, not per-consumer acknowledgement.
5. **“Compaction runs immediately and deletes everything old.”** It is background, segment-based, skips active
   segments, respects lag/tombstone/transaction constraints.
6. **“`acks=all` means all assigned replicas.”** It means all current ISR replicas; min ISR controls how small ISR may be.
7. **“High watermark equals leader end offset.”** HW is the committed/visible boundary and can lag leader LEO.
8. **“ISR is just majority quorum.”** ISR is dynamic and can shrink below majority.
9. **“Unclean leader election is normal failover.”** It can lose committed-looking data if stale replicas become leaders.
10. **“Committed offset is last processed offset.”** It is the next offset to fetch after restart.
11. **“Consumer lag is always committed-offset lag.”** Kafka client record lag is based on fetch position.
12. **“Cooperative rebalance means no pause.”** Only unmoved partitions continue; moved partitions still pause.
13. **“Kafka 3.9's new consumer group protocol is the production default.”** Source labels it early access.
14. **“Exactly-once means no duplicates anywhere.”** Kafka's EOS boundary is Kafka topics plus transactional offsets;
    external effects still need idempotence/coordination.
15. **“Aborted transaction records are removed.”** They remain in the log; markers/indexes control visibility.

---

## 5. Build-Your-Own Targets

1. **Append-only partition log:** segment files named by base offset; append records; read from offset.
2. **Sparse offset index:** map logical offsets to physical file positions and locate segment+position on fetch.
3. **Retention cleaner:** delete closed segments by time/size policy.
4. **Compaction cleaner:** build key→latest-offset map and recopy segments without obsolete records.
5. **Replicated partition:** leader append, follower fetch, follower LEO tracking, HW advancement.
6. **ISR/min-ISR simulator:** shrink/expand ISR, implement `acks=all` purgatory, demonstrate min-ISR rejections.
7. **Leader epoch truncation lab:** simulate divergent leaders and repair with epoch metadata.
8. **Group coordinator toy:** hash group IDs to shards, store committed offsets in compacted log records.
9. **Classic rebalance state machine:** join/sync/heartbeat/timeout and assignment recomputation.
10. **Cooperative rebalance visualizer:** only revoke moved partitions; converge over two rounds.
11. **Lag calculator:** compare fetch-position lag vs committed-offset lag.
12. **Idempotent producer:** track `(producerId, epoch, sequence)` and reject duplicates/gaps.
13. **Transaction coordinator:** compacted `transactionalId → state` log, prepare/complete transitions, marker writes.
14. **LSO/read-committed toy:** open transaction holds LSO; commit/abort markers release visibility.
15. **Consume-transform-produce lab:** atomically commit output records plus input offsets.

---

## 6. Open Questions / Gaps

- Replace mirrored Kafka paper URL with canonical primary source if accessible; current paper claims are conservative.
- Read KIP-101, KIP-497, KIP-500/KRaft, KIP-848, KIP-360 directly before quoting their rationale in course prose.
- Trace KRaft `PartitionChangeBuilder` / eligible leader replicas and feature defaults before teaching ELR.
- Trace preferred-replica election and controlled shutdown paths if needed.
- Trace fetch-from-follower / rack-aware replica selection path before detailed read-routing claims.
- Trace `CoordinatorRuntime` threading/snapshot mechanics and offset expiration scheduler before teaching internals.
- Trace sticky assignor algorithm and static membership fencing if consumer assignment becomes a deep chapter section.
- Trace `TransactionMarkerChannelManager.scala` retry behavior and `__transaction_state` expiration/tombstones before
  detailed transaction recovery prose.
- Trace long open transaction interactions with log compaction before claiming compaction behavior around LSO.
- Pin all Kafka source citations to a release tag/commit SHA before Phase 2 if the course needs stable permalinks.
- Do not start Phase 2 from 09 until these gaps are either scoped to appendix H or explicitly marked as residual.
