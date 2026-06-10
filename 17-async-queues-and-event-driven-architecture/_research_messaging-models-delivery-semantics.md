# 17 · Cluster A — Messaging models + delivery semantics (research brief)

> **Phase 1 brief. NO course prose.** Mechanisms, sources, forcing functions, misconceptions,
> build targets, open questions. `[UNVERIFIED from fetched source]` = claim not confirmed against a
> fetched primary this session. Math claims are recomputed in `_recompute.py` (run, 0 errors).
> Canon reused from line-verified earlier sub-courses is cited as **(reuse NN)** and NOT re-derived.

## 1. Key mechanisms

### 1.1 Three messaging shapes: queue vs log vs pub/sub
- **Work queue** (competing consumers): one logical destination, many workers; each message is
  delivered to *one* worker; the broker tracks per-message state (in-flight → acked/nacked) and
  *deletes* on ack. Optimizes for **load distribution**; message is gone once consumed. Classic AMQP/
  JMS/SQS shape. Ordering is best-effort and breaks under redelivery + concurrency.
- **Log** (shared cursor): an append-only, offset-addressed sequence; consumers track their own
  **offset** and re-read at will; the broker does *not* delete on consume, it deletes on
  **retention** (time/size) or **compaction**. Optimizes for **replay, fan-out, and ordered
  per-partition reads**. This is the 09 abstraction — *reuse it wholesale*. **(reuse 09 §1.1–1.7:
  partition = ordered append-only log addressed by offsets; `__consumer_offsets`; position ≠
  committed offset; HW ≠ LEO.)**
- **Pub/sub** (topic broadcast): each subscriber gets its *own* copy of every message; decouples N
  producers from M consumers by *topic*, not by work-sharing. A log with one consumer-group per
  subscriber *is* durable pub/sub; a queue with fan-out exchanges *is* transient pub/sub. So pub/sub
  is a delivery *policy* (everyone gets a copy) layered on either substrate.
- **The unification:** queue = "delete on ack, one consumer wins"; log = "delete on retention, every
  group has its own cursor". A Kafka-style log with **consumer groups** gives you queue semantics
  *within* a group (partitions split across members, one member per partition) AND pub/sub *across*
  groups (each group a full independent copy). **(reuse 09 §1.6 consumer groups / coordinator.)**

### 1.2 Delivery semantics: the three guarantees and what they cost
- **At-most-once**: ack/commit the offset *before* processing. A crash after commit, before work →
  message lost, never redelivered. Zero duplicates, possible loss. Cheapest. Fine for metrics/best-
  effort telemetry.
- **At-least-once**: process *then* ack. A crash (or lost ack) after work, before the commit lands →
  redelivery → **duplicate**. No loss, guaranteed duplicates at scale. This is the default and only
  honest broker guarantee for most systems. **(reuse 09 §1.7: commit N+1 only after processing N.)**
- **Effectively-once / exactly-once-*processing***: at-least-once delivery + **idempotent consumer**
  (dedup) OR an atomic "consume→produce→commit-offset" transaction. There is **no exactly-once
  *delivery*** over an unreliable network (the Two Generals impossibility, **reuse 11**); what
  systems sell as "exactly once" is *exactly-once effect* via dedup or transactions. Kafka EOS bounds
  this to Kafka topics + transactional offset commits; **external sinks still need idempotence.**
  **(reuse 09 §1.x delivery-semantics-transactions: idempotent producer = PID+epoch+seq; transactional
  offset commit; `read_committed`/LSO.)**

### 1.3 Duplicates are a certainty, not a risk (recomputed)
- Under at-least-once, expected duplicates over a stream = `N · p_ack_loss`; P(≥1 dup) = `1−(1−p)^N`.
  At `p=1e-4`, `N=1e6` → **~100 expected duplicates**, P(≥1)=1.0. **VERIFIED `_recompute.py` §1.**
- Consequence: **the consumer must be idempotent or dedup** — you cannot wish duplicates away at the
  broker. "Exactly once" is a consumer-side property.

### 1.4 Idempotency + dedup keys
- **Idempotency key**: a producer-assigned stable id per logical operation (`order_id`,
  `request_id`, hash of payload). Consumer keeps a **seen-set**; a repeat is a no-op. Turns
  at-least-once into effectively-once *for that effect*.
- **Natural idempotency** is cheaper than a dedup store: `SET balance=100` is idempotent; `balance +=
  10` is not. Prefer designing operations to be replay-safe (upserts, CRDT-style merges — **reuse 15
  Cluster C semilattice merge**) over bolting on dedup.
- **Dedup-window sizing (recomputed):** a dedup store only needs to remember a key for the **maximum
  redelivery horizon** = `Σ capped-exp-backoff(retries) + visibility/in-flight timeout`. With
  retries=8, base=1s, cap=60s, vis=30s → window ≥ **213 s** (~3.5 min). Store size = `key_rate ·
  window · bytes/key` (e.g. 50K keys/s · 213s · 64B ≈ **682 MB**). **VERIFIED `_recompute.py` §2.**
  Too-short a window → a late duplicate slips past dedup silently.
- Dedup substrate options: in-memory LRU/TTL set (fast, lossy on restart), Redis SET with TTL =
  window (**reuse 08**), or a compacted changelog keyed by idempotency key (**reuse 09 compaction**).

### 1.5 Ordering: per-partition only
- A log guarantees order **only within a partition**; across partitions there is no global order.
  **(reuse 09 §1.1; reuse 11 partial order / happens-before.)** Total order requires a single
  partition (no parallelism) or a consensus log (**reuse 11**) — expensive.
- **Ordering key** = partition key: messages that must be ordered relative to each other (e.g. all
  events for one `account_id`) must hash to the *same* partition. This is the **same shard-key
  decision as 14** (**reuse 14 Cluster B**): the partition key chooses both parallelism and the
  ordering domain, and a skewed key makes a hot partition (**reuse 14 hot-shard / celebrity key**).
- Redelivery breaks ordering even within a partition if you commit out of order or process
  concurrently; strict order ⇒ single-threaded per partition (the 09/Kafka model).

### 1.6 The outbox pattern + CDC (the dual-write killer)
- **Dual write** = write the DB *and* publish to the broker as two non-atomic steps. A crash between
  them yields a DB change with no event (or vice versa). **Failure window (recomputed):** P(bad/op) ≈
  `window · crash_rate`; at a 100 ms window and 30-day MTBF, **~38 bad events per 1e9 ops** —
  nonzero, so it leaks at scale. **VERIFIED `_recompute.py` §6.**
- **Transactional outbox**: write the event row into an `outbox` table **in the same DB transaction**
  as the state change. Atomicity is the DB's (ACID). A separate **relay** tails the outbox and
  publishes → at-least-once, **zero dual-write gap**. Cost shifts from *lost/phantom events* to
  *duplicate events* — handled by §1.4 dedup.
- **CDC (Change Data Capture)** = the relay reads the DB's **logical replication log** instead of an
  outbox table, turning every committed row change into an event. This is precisely **15 Cluster A's
  logical/row-based replication log re-pointed at a message bus** (**reuse 15**: statement vs
  WAL-physical vs logical-row; logical decoding / `pgoutput`). The log is already durable, ordered,
  and post-commit — ideal event source. **Debezium-style CDC = "the replication stream IS the event
  stream."**
- **Verified industrial instance (primary, fetched this session):** Facebook's **mcsqueal** daemon
  "examines the SQL statements that a database commits, extracts any deletes, and broadcasts these
  deletes to the memcache deployment in every cluster/region" — i.e. **CDC off the DB commit log
  driving cross-region cache invalidation**. Notably **"only 4% of all deletes issued result in the
  actual invalidation of cached data."** This is the **16 Cluster C/D cross-region invalidation
  transport handed off to 17's async log.** SOURCE: Nishtala et al., *Scaling Memcache at Facebook*,
  NSDI '13, §4.1 Regional Invalidations + Fig. 6 (mcsqueal). **VERIFIED from fetched PDF
  (`/tmp/nishtala.pdf`, USENIX).**

## 2. Foundational sources
- **VERIFIED by recomputation** (`_recompute.py`): duplicate prob `N·p` / `1−(1−p)^N` (§1); dedup
  window = redelivery horizon + store size (§2); dual-write failure window (§6).
- **VERIFIED by reuse (line-checked earlier):** the log / partitions / offsets / consumer groups /
  delivery / idempotent producer / transactional offset commit / compaction — **09** `_research.md`
  (Kafka source: `LocalLog.scala`, `LogSegment.java`, `LogCleaner.scala`, `GroupCoordinatorService`,
  `__consumer_offsets`, PID+epoch+seq, LSO/`read_committed`). Ordering / happens-before / Two
  Generals / total-order-needs-consensus — **11**. Shard/partition key + hot-shard skew — **14**.
  Logical/row replication log = CDC source; semilattice merge for idempotent merges — **15**.
  Redis/TTL set as dedup store — **08**.
- **VERIFIED from fetched primary this session:** Nishtala et al., NSDI '13 — demand-filled
  look-aside cache (cache-aside default), leases (64-bit token, 10 s regulation, **17K/s → 1.3K/s**
  herd cut), mcsqueal CDC delete-stream, 4% effective-invalidation. SOURCE: `/tmp/nishtala.pdf` →
  `/tmp/nishtala.txt`.
- **`[UNVERIFIED from fetched source]` (still HTTP 000 this session):** AMQP 0-9-1 / JMS spec exact
  ack semantics; SQS visibility-timeout / FIFO dedup-window (Amazon docs); Kafka KIPs for EOS
  (KIP-98/129/447) — reused via 09's source-verified summary but the KIP text itself unfetched;
  RabbitMQ docs (publisher confirms, consumer acks); Debezium docs; the "Two Generals" / "exactly
  once is impossible" framed against a fetched primary (reused from 11's verified treatment).

## 3. "Why it's this way" — forcing functions
- **The network can lose/duplicate/reorder, and a consumer can crash mid-work.** Therefore the only
  guarantees a broker can *cheaply* give are at-most-once (ack first) or at-least-once (ack last);
  exactly-once *delivery* is impossible (**11**), so the duplicate-handling burden is *designed* onto
  the consumer. The whole taxonomy is "who eats the inevitable failure: the lost message, or the
  duplicate?"
- **Order and parallelism are in tension.** A single sequence is totally ordered but serial; to go
  parallel you must partition, and partitioning destroys global order. So "per-partition order" is
  not a limitation, it's the *price* of horizontal throughput (**same 14 tradeoff**).
- **Atomicity doesn't cross systems for free.** A DB and a broker are two systems; a single op can't
  be atomic across both without 2PC (**11**, expensive/blocking). The outbox sidesteps this by making
  the event part of the *one* thing that is already atomic — the DB transaction — and accepting
  at-least-once downstream.

## 4. Common misconceptions to preempt
- "Use a queue for everything." Queues delete on ack (no replay); logs retain (replay/fan-out). The
  choice is *replay + multi-consumer* vs *work-sharing + auto-cleanup*.
- "Exactly-once delivery exists / Kafka gives exactly once." No — at-least-once + idempotency/
  transactions = exactly-once *effect*; external sinks still need dedup. (**reuse 09.**)
- "Duplicates are rare edge cases." `E[dups]=N·p` → certain at scale (**§1.3 verified**).
- "Idempotency keys are free." A dedup store has a size = `rate·window·bytes` and a window bounded by
  the redelivery horizon (**§1.4 verified**); too-short window leaks dups.
- "Publishing after the DB write is fine." Dual write leaks (`~38/1e9` at 100 ms; **§1.6 verified**);
  use the outbox/CDC.
- "CDC is a different thing from replication." CDC *is* the logical replication log pointed at a bus
  (**reuse 15**).
- "More partitions = always faster." Partition count caps parallelism (Cluster C) and *is* the
  ordering domain (§1.5); too many = tiny batches + rebalance churn + more files.

## 5. Best build-your-own target(s)
- **Delivery-semantics harness:** one in-memory broker, three modes (ack-first / ack-last / ack-last
  + dedup); inject ack loss at rate `p`; count lost vs duplicate vs exactly-once-effect; confirm
  `E[dups]=N·p`. (pairs §1.2–1.4)
- **Idempotent consumer + dedup store:** Redis/TTL seen-set sized to the redelivery horizon; prove a
  too-short window leaks a late dup. (pairs §1.4)
- **Outbox + relay:** write state+event in one DB txn, tail the outbox, publish; kill the relay
  mid-publish and show no lost events, only dups (caught by the dedup store). Upgrade to **CDC** by
  tailing the WAL/logical stream instead of a table. (pairs §1.6, reuse 07/15)
- **Ordering-key lab:** route by partition key; show per-partition order preserved, cross-partition
  not; make a hot partition with a skewed key (reuse 14). (pairs §1.5)

## 6. Open questions / gaps
- Fetch AMQP/JMS/SQS/RabbitMQ/Debezium primaries when reachable to pin exact ack/visibility/FIFO-
  dedup wording (still HTTP 000). The *mechanisms* are verified by reuse(09)+recomputation; the
  *vendor exact semantics* are `[UNVERIFIED]`.
- Decide teaching default for dedup: natural idempotency (upsert) first, dedup store second, broker
  "exactly once" last-and-with-caveats.
- Boundary: broker durability/replication internals → Cluster D + reuse 09/15; backpressure when
  consumers fall behind → **18** (handoff, do not derive here).
