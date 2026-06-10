# Research Brief — Sub-course 09: Kafka Delivery Semantics, Idempotence, and Transactions
## Source cluster: at-most/at-least/exactly-once caveats, idempotent producer, transactions, LSO
## Researcher: researcher + brain validation | Date: 2026-06-10

---

## 1. Key Mechanisms

### 1.1 Delivery semantics are failure contracts, not marketing labels

The Kafka 3.9 design doc distinguishes producer and consumer failure windows:
- If a producer retries after an ambiguous timeout, the original write may have succeeded, so retry can duplicate
  the batch unless the broker can detect the duplicate.
- If a consumer commits its position before processing, crash can drop work: at-most-once.
- If a consumer processes before committing, crash can repeat work: at-least-once.
- Kafka's exactly-once support is scoped to Kafka-controlled flows, especially consuming from Kafka and producing
  back to Kafka with transactional offset commits. External sinks still need idempotence or their own transaction
  coordination.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md`.

### 1.2 Idempotent producer = producer id + epoch + per-partition sequence

Kafka 3.9 enables idempotence by default (`enable.idempotence=true`) and producer `acks` defaults to `all`.
Validation in `ProducerConfig` requires idempotent producers to use non-zero retries, `acks=all`, and
`max.in.flight.requests.per.connection <= 5`; otherwise idempotence is disabled or config is rejected depending
on whether the user explicitly set the conflicting option. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java`.

Record batches carry producer metadata. `DefaultRecordBatch.java` defines fields and flags including:
- `PRODUCER_ID_OFFSET`
- `PRODUCER_EPOCH_OFFSET`
- `BASE_SEQUENCE_OFFSET`
- `TRANSACTIONAL_FLAG_MASK`
- `CONTROL_FLAG_MASK`
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/common/record/DefaultRecordBatch.java`.

Broker-side validation is in `ProducerAppendInfo.java`. It accepts the next sequence, treats lower/equal sequence
for the same epoch as duplicate, and throws `OutOfOrderSequenceException` for gaps. It also validates producer
epochs. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/ProducerAppendInfo.java`.

`ProducerStateManager.java` maintains per-partition producer state keyed by producer id and snapshots it for
recovery. The snapshot schema includes producer id, epoch, last sequence, last offset, offset delta, timestamp,
coordinator epoch, and current transaction first offset. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/ProducerStateManager.java`.

### 1.3 Producer epochs fence zombies

A producer id alone is not enough: an old producer process can continue running after a replacement starts. Epochs
let brokers reject stale producers. KIP-98 says `InitPidRequest` bumps the PID epoch so previous zombie instances
are fenced. Source:
`https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging`.

For transactional producers, `TransactionMetadata.isEpochExhausted(...)` returns true when the epoch reaches
`Short.MaxValue - 1`, forcing a new producer id rather than overflowing an `INT16` epoch. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/coordinator/transaction/TransactionMetadata.scala`.

### 1.4 Transaction coordinator and `__transaction_state`

Atomic writes across partitions require a coordinator. Kafka's transaction coordinator persists transactional-id
state in `__transaction_state`, a compacted internal topic. `TransactionLog.scala` enforces:
- cleanup policy = compact,
- compression = none,
- unclean leader election = disabled,
- required acks = `-1` for writes.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/coordinator/transaction/TransactionLog.scala`.

`TransactionMetadata.scala` defines transaction states:
- `Empty` (0)
- `Ongoing` (1)
- `PrepareCommit` (2)
- `PrepareAbort` (3)
- `CompleteCommit` (4)
- `CompleteAbort` (5)
- `Dead` (6)
- `PrepareEpochFence` (7)

Important flow:
1. `InitProducerId` obtains or refreshes producer id/epoch.
2. `AddPartitionsToTxn` enrolls topic partitions.
3. Data records are written with transactional and producer-sequence metadata.
4. Optional `sendOffsetsToTransaction(...)` enrolls the consumer offsets partition and writes offsets transactionally.
5. `EndTxn` transitions to `PrepareCommit` or `PrepareAbort` in `__transaction_state`.
6. The coordinator sends transaction markers to each affected partition leader.
7. After marker acknowledgements, the coordinator writes `CompleteCommit` or `CompleteAbort`.

`TransactionCoordinator.scala` responds to the client after the prepare-state log append succeeds and then queues
transaction markers; marker completion can continue asynchronously. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/coordinator/transaction/TransactionCoordinator.scala`.

### 1.5 Transaction markers are control batches, not segment rewrites

Kafka does not delete aborted records immediately. It appends control batches containing commit/abort markers.
`EndTransactionMarker.java` encodes marker type and coordinator epoch; coordinator epoch fences stale coordinator
marker writes. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/common/record/EndTransactionMarker.java`.

`TransactionIndex.java` stores aborted transactions per segment so `read_committed` consumers can skip aborted
ranges. `AbortedTxn.java` stores producer id, first offset, last offset, and last stable offset. Sources:
`https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/TransactionIndex.java`,
`https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/AbortedTxn.java`.

### 1.6 LSO and `read_committed`

`UnifiedLog.lastStableOffset` is:
- first unstable transaction offset if it is below high watermark,
- otherwise high watermark.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/UnifiedLog.scala`.

`FetchIsolation.java` maps fetch visibility:
- `LOG_END` for follower fetches,
- `HIGH_WATERMARK` for ordinary consumer fetches,
- `TXN_COMMITTED` for `read_committed` consumers.
Source: `https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/FetchIsolation.java`.

A long open transaction can hold LSO behind HWM, stalling `read_committed` consumers even though records exist in
the log.

### 1.7 Transactional offset commits close the consume-transform-produce hole

Exactly-once Kafka-to-Kafka processing requires output records and input offsets to commit atomically. The modern
producer API accepts `sendOffsetsToTransaction(Map<TopicPartition, OffsetAndMetadata>, ConsumerGroupMetadata)`;
the older string-only overload is deprecated since 3.0. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/KafkaProducer.java`.

The transaction manager client state includes:
`UNINITIALIZED`, `INITIALIZING`, `READY`, `IN_TRANSACTION`, `COMMITTING_TRANSACTION`, `ABORTING_TRANSACTION`,
`ABORTABLE_ERROR`, and `FATAL_ERROR`. Source:
`https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/internals/TransactionManager.java`.

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| Delivery semantics and exactly-once caveats | `https://raw.githubusercontent.com/apache/kafka/3.9/docs/design/design.md` | VERIFIED |
| KIP-98 design rationale | `https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging` | VERIFIED reachable; use sparingly with source cross-check |
| Producer config defaults/constraints | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java` | VERIFIED |
| Batch producer metadata flags | `https://raw.githubusercontent.com/apache/kafka/3.9/clients/src/main/java/org/apache/kafka/common/record/DefaultRecordBatch.java` | VERIFIED snippets |
| Broker sequence/epoch validation | `ProducerAppendInfo.java`, `ProducerStateManager.java` under Kafka 3.9 | VERIFIED snippets |
| Transaction coordinator and state log | `TransactionCoordinator.scala`, `TransactionLog.scala`, `TransactionMetadata.scala`, `TransactionStateManager.scala` | VERIFIED snippets |
| Transaction markers and aborted index | `EndTransactionMarker.java`, `TransactionIndex.java`, `AbortedTxn.java` | VERIFIED snippets |
| LSO/fetch isolation | `UnifiedLog.scala`, `FetchIsolation.java`, `FetchRequest.json`, `FetchResponse.json`, `CompletedFetch.java` | VERIFIED |
| Transactional offset API | `KafkaProducer.java`, `TransactionManager.java` | VERIFIED snippets |

---

## 3. Why It’s This Way — Forcing Constraints

- **Retries need broker-side duplicate detection.** A timeout cannot tell the client whether the broker committed
  the batch but lost the response.
- **Per-message IDs would be too expensive.** Kafka uses producer id + sequence ranges per partition instead.
- **Epochs fence zombies.** Logical producer identity can outlive a process; the old process must become stale.
- **Cross-partition atomicity needs a coordinator.** One partition leader cannot decide for all partitions.
- **Append-only logs prefer markers over rewrites.** Commit/abort markers preserve sequential append and recovery.
- **LSO is the read boundary for undecided transactions.** Physical presence in the log is not equivalent to
  committed visibility.
- **External systems are outside Kafka's transaction boundary.** Kafka can atomically combine Kafka outputs and
  Kafka offsets; databases/caches/services need additional idempotence or coordination.

---

## 4. Common Misconceptions to Preempt

1. **“Exactly-once means no duplicates anywhere.”** Kafka's guarantee is bounded by Kafka topics and transactional
   offset commits; external side effects are outside the boundary.
2. **“Idempotence solves consumer duplicates.”** It solves producer retry duplicates per producer/partition; consumer
   reprocessing is a different failure window.
3. **“Aborted records are removed from the log.”** They remain physically present; markers and indexes control visibility.
4. **“`read_committed` just filters aborted records.”** It also stops at LSO until earlier transactions are decided.
5. **“Transactions respond only after every marker is written.”** The coordinator can respond after durable prepare
   state and drive markers asynchronously.
6. **“`max.in.flight=1` is always required for idempotence.”** Kafka 3.9 allows up to 5 for idempotence.
7. **“Auto commit works with exactly-once processing.”** Transactional consume-transform-produce should disable
   auto-commit and send offsets through the producer transaction.

---

## 5. Build-Your-Own Targets

1. **Idempotent append toy:** broker tracks `(producerId, epoch, lastSeq)` and rejects duplicates/gaps.
2. **Producer snapshot recovery:** persist producer state and prove duplicates after broker restart are still rejected.
3. **Transaction coordinator state machine:** compacted `transactionalId → state` log plus prepare/complete transitions.
4. **Control marker simulation:** append data records and commit/abort markers; implement `read_uncommitted` vs
   `read_committed` reads.
5. **LSO calculator:** hold LSO at first open transaction and release it on commit/abort.
6. **Consume-transform-produce lab:** atomically commit output records plus consumed offsets in one toy transaction.

---

## 6. Open Questions / Gaps

- Trace `TransactionMarkerChannelManager.scala` retry loop before teaching marker failure recovery in detail.
- Trace `__transaction_state` expiration/tombstone timing end-to-end.
- Trace KIP-360 safe epoch bumping if explaining advanced transactional recovery.
- Kafka Streams EOS modes (`exactly_once`, `exactly_once_v2`) are not covered here; this cluster only covers base protocol.
- Interaction of long open transactions with log compaction needs direct `LogCleaner.scala` tracing before teaching.
