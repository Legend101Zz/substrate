# Research Brief — Sub-course 09: Log Abstraction and Kafka Storage
## Source cluster: Kafka paper/design, partitions, offsets, retention, compaction, broker log storage
## Researcher: brain-manual starter | Date: 2026-06-10

---

## 1. Key Mechanisms

### 1.1 The log abstraction: append first, read by position

Kafka’s central move is to treat a message stream as an append-only log. Producers append records; consumers
read records by monotonically increasing position. This replaces per-message broker delivery state with a
shared ordered file abstraction.

The original Kafka paper states that a topic is split into sub-streams/partitions and that each partition is
a logical log. A message is addressed by its logical offset in the log rather than by an explicit message id.
The paper argues this avoids auxiliary seek-heavy indexes and allows sequential IO and OS page cache behavior.
Source: Kreps, Narkhede, Rao, “Kafka: a Distributed Messaging System for Log Processing,”
`https://notes.stephenholiday.com/Kafka.pdf` (PDF extracted with `/tmp` pypdf).

### 1.2 Topics, partitions, offsets

A topic is divided into partitions so the stream can scale across brokers and consumers. A partition is the
unit of ordering: offsets are meaningful within one partition, not globally across all partitions in a topic.
The paper’s architecture section shows producers writing to topic partitions on brokers and consumers reading
partition streams.

**Important teaching point:** Kafka gives ordered replay inside a partition; it does not give one total order
for a multi-partition topic unless the application imposes one.

### 1.3 Broker storage: partition log as segment files

Kafka’s storage layout is deliberately simple: each topic partition maps to a log; physically a log is split
into segment files. Current Kafka source preserves this model:

- `LocalLog.java` comment: “An append-only log for storing messages locally. The log is a sequence of
  LogSegments, each with a base offset.” New segments are created according to size/time policy.
  Source: `https://raw.githubusercontent.com/apache/kafka/trunk/storage/src/main/java/org/apache/kafka/storage/internals/log/LocalLog.java`.
- `LogSegment.java` is the per-segment storage unit. It carries a base offset and associated index/time-index
  structures. Source: `https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java`.
- `LogConfig.java` exposes segment and retention knobs such as `segmentSize`, `segmentMs`, `retentionSize`,
  `retentionMs`, and compaction lag settings. Source:
  `https://raw.githubusercontent.com/apache/kafka/trunk/storage/src/main/java/org/apache/kafka/storage/internals/log/LogConfig.java`.

### 1.4 Efficiency: sequential IO, batching, zero-copy/page cache direction

The Kafka paper’s efficiency section emphasizes:

- **Simple storage:** append to files and keep sparse in-memory indexes instead of random per-message state.
- **Batching:** producer can send sets of messages in one request, reducing round trips.
- **OS caching:** because producer appends and consumers often read sequentially with small lag, write-through
  caching and read-ahead help.
- **Transfer efficiency:** the paper discusses careful transfer in/out of Kafka; exact modern zero-copy/sendfile
  source tracing is not yet done in this starter brief, so keep detailed claims `[UNVERIFIED]` until fetched.

### 1.5 Retention: delete by time/size, not by consumer acknowledgement

Unlike classic queues that delete a message when consumed, Kafka retains log data according to retention policy.
That lets multiple consumer groups replay at their own pace. This brief has verified retention fields in
`LogConfig.java` and segment deletion mechanics in `LocalLog.java`, but has not yet traced the full
`LogManager` cleanup path. Treat exact deletion scheduling as `[UNVERIFIED]` pending follow-up.

### 1.6 Compaction: keep latest value per key

Kafka log compaction is a retention mode for keyed streams: older records for a key can be removed after a newer
record for that key exists, leaving a compacted latest-state history rather than pure time/size deletion.

Verified from Kafka 3.9 `LogCleaner.scala`:
- The cleaner removes obsolete records from logs with the `compact` retention strategy.
- A record with key K at offset O is obsolete if there is another record with key K at offset O′ where O < O′.
- Logs are split into clean and dirty sections; the active segment is uncleanable.
- Cleaner threads choose dirty compacted logs, build a key→last_offset map for the dirty section, then recopy
  segments while omitting records superseded by higher offsets.
- Null payloads are delete markers/tombstones and receive special retention treatment.

Source: `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LogCleaner.scala`.

### 1.7 Replication and high watermark — queued for deeper cluster

This starter only lightly touches replication. `Partition.scala` shows leader/follower state, ISR, high watermark,
leader epoch, and min ISR checks. Source:
`https://raw.githubusercontent.com/apache/kafka/trunk/core/src/main/scala/kafka/cluster/Partition.scala`.

Do not teach exact replication semantics from this starter alone. A later 09 cluster should cover leader election,
ISR, high watermark, acknowledgements, producer idempotence, transactions, and controller/KRaft.

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| Original Kafka design/paper | `https://notes.stephenholiday.com/Kafka.pdf` | VERIFIED via PDF extraction; mirror URL, should replace with canonical ACM/LinkedIn if accessible |
| Local append-only log and segments | `https://raw.githubusercontent.com/apache/kafka/trunk/storage/src/main/java/org/apache/kafka/storage/internals/log/LocalLog.java` | VERIFIED snippets |
| Segment implementation | `https://raw.githubusercontent.com/apache/kafka/3.9/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java` | VERIFIED snippets |
| Log config: retention, segment, compaction knobs | `https://raw.githubusercontent.com/apache/kafka/trunk/storage/src/main/java/org/apache/kafka/storage/internals/log/LogConfig.java` | VERIFIED snippets |
| Compaction cleaner | `https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/log/LogCleaner.scala` | VERIFIED |
| Partition leader/ISR/high watermark source | `https://raw.githubusercontent.com/apache/kafka/trunk/core/src/main/scala/kafka/cluster/Partition.scala` | VERIFIED snippets; deeper pass needed |
| Apache Kafka HTML docs | `https://kafka.apache.org/40/documentation.html` | PARTIAL/REDIRECT issues in this pass; do not rely on docs text yet |
| Kreps “The Log” essay | LinkedIn engineering URL | Fetch unreliable in this pass; queued |

---

## 3. Why It’s This Way — Forcing Constraints

- **Sequential IO beats random per-message bookkeeping.** Kafka’s log layout turns message storage into append
  and sequential scan, which maps well to disks, SSDs, and OS page cache.
- **Offsets replace broker-owned delivery state.** Consumers can track their own position; the broker does not
  need to delete a message just because one consumer saw it.
- **Partitions scale throughput and storage.** One total order is a bottleneck; partitioned logs trade global
  order for parallelism.
- **Retention decouples consumption from deletion.** Multiple consumer groups can independently replay the same
  log; deletion becomes a storage policy.
- **Compaction exists because some streams represent latest state.** For keyed updates, keeping every old value
  forever is wasteful; keeping the latest value per key supports rebuildable materialized state.

---

## 4. Common Misconceptions to Preempt

1. **“Kafka is just a queue.”** It is a retained partitioned log; queue behavior is one consumption pattern.
2. **“A topic has one total order.”** Ordering is per partition.
3. **“Offsets are message IDs.”** They are positions in a partition log; they are not globally meaningful IDs.
4. **“Consumed means deleted.”** Kafka retention is policy-based, not per-consumer acknowledgement deletion.
5. **“Compaction deletes old records immediately.”** Cleaning is background, segment-based, and constrained by active
   segment, compaction lag, tombstones, and transaction boundaries.
6. **“Replication semantics are obvious from segments.”** Replication/high watermark/ISR need their own deep source pass.

---

## 5. Build-Your-Own Targets

1. **Append-only partition log:** segment files named by base offset; append records; read from offset.
2. **Sparse index:** map every N bytes/records to file position; binary search segment by offset.
3. **Retention cleaner:** delete old closed segments by time/size policy.
4. **Compaction cleaner:** build key→latest-offset map and recopy segments omitting obsolete keyed records.
5. **Consumer group toy:** store committed offsets externally and allow replay from earlier offsets.
6. **Mini broker:** producers append to partitions; consumers fetch batches from offsets.

---

## 6. Open Questions / Gaps

- Replace mirrored Kafka paper URL with canonical primary source if accessible; preserve extracted-paper claims meanwhile.
- Fetch reliable Apache Kafka design docs text; initial documentation fetch hit redirect/HTML issues.
- Trace modern Kafka append/fetch path, FileRecords, indexes, zero-copy/sendfile, and page-cache behavior.
- Deepen replication: leader/follower, ISR, high watermark, acks, leader epochs, unclean leader election, KRaft controller.
- Deepen consumer groups and committed offsets (`__consumer_offsets`) from current coordinator source.
- Deepen delivery semantics: at-most-once/at-least-once/effectively-once, idempotent producers, transactions.
- Factcheck this 09 starter before reconciliation; 09 is only started, not complete.
