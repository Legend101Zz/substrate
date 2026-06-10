# Factcheck Report — Sub-course 09 Phase 1 Research Briefs
## Scope: Kafka log/storage, replication, consumer groups/offsets, delivery semantics
## Factchecker: factchecker + brain validation | Date: 2026-06-10

---

## Summary Verdict

09 is **factchecked with blockers patched** for the Phase 1 research corpus.

- Checked against Apache Kafka 3.9 primary sources unless noted.
- One blocker was found: the starter brief pinned `LocalLog` to the wrong Kafka 3.9 path after replacing a trunk URL.
- The blocker was patched to `core/src/main/scala/kafka/log/LocalLog.scala`.
- Remaining items are warnings/gaps, not reconciliation blockers.

---

## Blockers Patched

| ID | Claim / file | Finding | Patch applied |
|---|---|---|---|
| B1 | `_research_log-abstraction-kafka-storage.md` cited Kafka 3.9 `LocalLog` as `storage/src/main/java/.../LocalLog.java`. | Kafka 3.9 returns 404 for that path. Kafka trunk has Java/storage `LocalLog`, but Kafka 3.9 has Scala/core `LocalLog.scala`. The quoted Javadoc exists in the Scala file. | Replaced source URL with `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LocalLog.scala` and noted the version/path distinction. |

---

## Warnings / Precision Patches

| ID | Area | Finding | Status |
|---|---|---|---|
| W1 | KRaft unclean-election interval | `UNCLEAN_LEADER_ELECTION_INTERVAL_MS_DEFAULT = 5 min` is correct, but it is registered via `defineInternal(...)`; do not describe it as a normal user-facing knob. | Patched wording in `_research_replication-availability.md`. |
| W2 | Follower reads | Kafka 3.9 design doc says reads can go to leader or followers. This reflects modern rack-aware/nearest-replica fetch behavior; do not imply this was always the historical default. | Clarifying sentence added to `_research_replication-availability.md`. |
| W3 | Leader epoch wording | `EpochEntry` Javadoc frames mapping as "epoch to the first offset of the subsequent epoch". The course should quote/source carefully if using exact wording. | Logged as gap; no blocker because brief uses mechanism-level wording and cites source. |

---

## PASS Items Checked

| Area | Claim | Source |
|---|---|---|
| Storage/log | `LocalLog.scala` says a log is append-only and a sequence of `LogSegment`s, each with a base offset. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LocalLog.scala` |
| Storage/log | `LogConfig` includes segment and retention knobs (`segmentSize`, `segmentMs`, `retentionSize`, `retentionMs`) and compaction flags. | `https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/LogConfig.java` |
| Compaction | `LogCleaner.scala` says a record for key K at offset O is obsolete if another record for K exists at higher offset O′; cleaner builds key→last_offset map and recopies segments. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LogCleaner.scala` |
| Replication | Design doc confirms partition leader/follower model, ISR, committed-message semantics, unclean leader election tradeoff, and `acks` framing. | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md` |
| Replication | `REPLICA_LAG_TIME_MAX_MS_DEFAULT = 30000L`. | `https://raw.githubusercontent.com/apache/kafka/3.9/server/src/main/java/org/apache/kafka/server/config/ReplicationConfigs.java` |
| Replication | `MIN_IN_SYNC_REPLICAS_DEFAULT = 1`. | `https://raw.githubusercontent.com/apache/kafka/3.9/server-common/src/main/java/org/apache/kafka/server/config/ServerLogConfigs.java` |
| Replication | `DEFAULT_UNCLEAN_LEADER_ELECTION_ENABLE = false`. | `https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/LogConfig.java` |
| Replication | `Partition.appendRecordsToLeader(...)` rejects `acks=-1` writes below min ISR with `NotEnoughReplicasException`. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/cluster/Partition.scala` |
| Replication | `ReplicaFetcherThread.processPartitionData()` appends follower data and updates follower HW from leader response. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/ReplicaFetcherThread.scala` |
| Replication | `LeaderEpochFileCache` uses `TreeMap<Integer, EpochEntry>`; `AbstractFetcherThread` performs leader-epoch truncation/fallback to HW for undefined epoch offsets. | `LeaderEpochFileCache.java`, `AbstractFetcherThread.scala` under Kafka 3.9 |
| KRaft | KRaft operations doc confirms broker/controller roles and typical 3 or 5 controllers. | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/operations/kraft.md` |
| Consumer groups | `__consumer_offsets` name is `Topic.GROUP_METADATA_TOPIC_NAME`. | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/common/internals/Topic.java` |
| Consumer groups | Group coordinator partition formula is `Utils.abs(groupId.hashCode()) % numPartitions`. | `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorService.java` |
| Consumer groups | Defaults: offsets partitions=50, segment bytes=100MB, retention=7 days. | `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorConfig.java` |
| Consumer groups | Kafka 3.9 labels `CONSUMER` rebalance protocol early access and not for production. | `GroupCoordinatorConfig.java` |
| Consumer groups | Classic group state machine states/transitions are represented in `ClassicGroupState.java`. | `https://raw.githubusercontent.com/apache/kafka/3.9/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/classic/ClassicGroupState.java` |
| Consumer groups | `ConsumerGroupHeartbeatRequest` API key is 68. | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/resources/common/message/ConsumerGroupHeartbeatRequest.json` |
| Fetch isolation | `FetchRequest.json` defines isolation level; `FetchResponse.json` defines LSO; `CompletedFetch.java` filters aborted producers for `READ_COMMITTED`. | Kafka 3.9 client schema/source files |
| Delivery | `ProducerConfig` defaults `acks="all"` and `enable.idempotence=true`; idempotence requires nonzero retries, `acks=all`, and max in-flight ≤ 5. | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java` |
| Delivery | Producer batch metadata has producer id, epoch, base sequence, transactional/control flags. | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/common/record/DefaultRecordBatch.java` |
| Delivery | Transaction states Empty→PrepareEpochFence IDs 0–7 are verified. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/coordinator/transaction/TransactionMetadata.scala` |
| Delivery | `__transaction_state` enforces compact cleanup, no compression, unclean election disabled, and required acks=-1. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/coordinator/transaction/TransactionLog.scala` |
| Delivery | `UnifiedLog.lastStableOffset` equals first unstable offset if below HW, else HW. | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/UnifiedLog.scala` |
| Delivery | `KafkaProducer.sendOffsetsToTransaction(Map, String)` overload is deprecated since 3.0 in favor of `ConsumerGroupMetadata`. | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/KafkaProducer.java` |

---

## Residual Gaps to Preserve

- Replace mirrored Kafka paper URL with canonical paper URL if accessible; current paper claims are conservative.
- Read KIP-101, KIP-497, KIP-500/KRaft, KIP-848, and KIP-360 directly before quoting KIP rationale in course prose.
- Trace `TransactionMarkerChannelManager.scala` retry behavior before teaching marker recovery in detail.
- Trace `CoordinatorRuntime` and offset expiration scheduler internals before teaching coordinator threading/cleanup.
- Trace fetch-from-follower / rack-aware replica selection path before making detailed read-routing claims.
- Keep Kafka-version caveats: this pass pins Kafka 3.9; trunk/4.x paths and ZooKeeper/KRaft status differ.
