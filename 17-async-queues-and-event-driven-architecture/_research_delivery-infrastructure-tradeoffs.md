# 17 · Cluster D — Delivery infrastructure + tradeoffs (research brief)

> **Phase 1 brief. NO course prose.** `[UNVERIFIED from fetched source]` = not confirmed against a
> fetched primary this session. Canon reused from line-verified sub-courses is **(reuse NN)**. Math
> recomputed in `_recompute.py`.

## 1. Key mechanisms

### 1.1 Broker durability + replication (reuse 09/15)
- A message is "safe" only once it's **durably replicated** to enough replicas. The broker is a
  replicated log: a partition has a **leader** + **in-sync replicas (ISR)**; a write is committed when
  the required replicas acknowledge (**reuse 09 §HW/ISR: HW ≤ LEO; `ReplicaFetcherThread`**).
- **acks / durability dial** is the *same durability-vs-latency dial as 15* (**reuse 15 Cluster A
  sync/async/semi-sync**): `acks=0` (fire-and-forget, can lose), `acks=1` (leader only — lose on
  leader failure before replication), `acks=all` + `min.insync.replicas` (quorum durability, higher
  latency). Choosing `acks` is choosing where on the loss-vs-latency curve you sit.
- **Quorum/overlap math is 15's** (**reuse 15 Cluster C/D**): with replication factor N and
  `min.insync.replicas = R`, you tolerate `N−R` replica failures while still committing; majority
  config tolerates `floor((N−1)/2)` (e.g. N=3 → 1). Do NOT re-derive — re-point 15's verified result.
- **Unclean leader election** = allowing an out-of-sync replica to become leader → availability over
  durability (can lose committed-looking data); the **CAP/PACELC choice (reuse 11/15)** at the broker.

### 1.2 Partitioning for throughput (reuse 14)
- Throughput scales by **adding partitions** (more parallel append points + more parallel consumers,
  Cluster C §1.1). Partition = the unit of parallelism, ordering (Cluster A §1.5), *and* placement.
- **Partition key = shard key** (**reuse 14 Cluster B**): hash-partition for even spread, range for
  scan locality; a skewed key → **hot partition / celebrity key** (**reuse 14 hot-shard**), the
  dominant real-world throughput limiter. The Zipf-head problem of 14/16 reappears as a hot partition.
- **Repartitioning is disruptive** (consistent-hashing/vnode minimizes movement, **reuse 06/14**);
  size partitions for the *future* max, since changing count reshuffles keys and breaks per-key order
  during the move.

### 1.3 Fan-out (one event, many destinations)
- **Read fan-out (consumer-side):** each consumer group is an independent full copy of the stream
  (Cluster A §1.1) → N subscribers = N× read load on the brokers, served cheaply from the page cache
  / sequential reads (**reuse 09 zero-copy/sequential IO**). This is *log fan-out* and is how one
  event feeds many materialized views/caches (reuse Cluster B §1.5).
- **Write fan-out (producer/topology-side):** one logical event must land in many partitions/topics
  (e.g. per-follower feed delivery) → write amplification; the **fan-out tail-latency math is 13's**
  (**reuse 13**: P(>=1 slow leg) = 1−(1−q)^N`, e.g. 100 fan-out legs at q=1% ⇒ ~63% slow). Fan-out
  multiplies tail risk → hedging/coalescing.
- **Fan-out-on-write vs fan-out-on-read** (feed problem, full treatment deferred to **21 case
  studies**): precompute per-consumer copies on write (fast reads, expensive hot producers/celebrities
  — the 14 celebrity problem again) vs compute on read (cheap writes, expensive reads). The async
  queue is the *transport* for fan-out-on-write. Cross-link to **21**, don't fully derive here.

### 1.4 Retention vs compaction (reuse 09; recomputed sizing)
- **Time/size retention**: keep messages for a window, then delete — for **event streams** (history
  matters for a while, then it's noise). Disk per partition = `rate · msg_bytes · retention`
  (recomputed: 1e6/s · 256B · 72h × RF3 ≈ **199 TB**; **`_recompute.py` §4**). Retention bounds how
  far back you can replay (Cluster C §1.4) and how long a slow consumer can lag before loss.
- **Compaction**: keep only the latest value per key — for **changelogs/CDC/state topics** (the
  current state, not the history). Floor = `unique_keys · bytes/key`, **independent of write history**
  (recomputed: 1e8 keys · 64B ⇒ **6.4 GB**; **`_recompute.py` §4**). (**reuse 09 LogCleaner**.)
- Rule to teach: **time-retention for events, compaction for state/CDC/materialized-view source.**
  An event-sourced log (Cluster B §1.4) often uses both: compacted current-state topic + retained
  event-history topic.

### 1.5 Latency vs throughput batching (recomputed)
- A per-batch fixed cost `c` (syscall/RTT/fsync) amortizes over batch size B: per-msg cost = `c/B +
  m`, throughput = `1/(c/B + m)`, asymptoting at `1/m` (**reuse 13 Little's Law / amortization**).
  Recomputed (c=1ms, m=5µs): B=1 → ~1K msg/s; B=100 → ~67K; B=10K → ~196K, asymptote `1/m=200K`.
  **VERIFIED `_recompute.py` §3.**
- The cost of batching is **linger latency** (wait-to-fill or a linger timer). So batching trades the
  *p50/tail latency* of an individual message for *system throughput* — the **same throughput-vs-
  latency tradeoff as 13's queueing** and 16's coalescing. `linger.ms`/`batch.size` (producer),
  fetch min-bytes/max-wait (consumer) are the knobs.
- **Compression** stacks on batching (compress the batch; better ratio on larger batches) — more
  throughput/byte, more CPU + latency. **(reuse 09 batch+compression; `[UNVERIFIED]` exact codec
  defaults.)**

### 1.6 Putting the dials together (the infra tradeoff space)
- Four coupled dials: **acks/ISR** (durability↔latency, §1.1/15), **partitions** (throughput/order/
  parallelism, §1.2/14/Cs), **retention/compaction** (replay-horizon↔disk, §1.4), **batch/linger/
  compression** (throughput↔latency, §1.5). Every "make it faster" turn costs durability, ordering,
  disk, or latency somewhere — conservation of pain, the same lesson as 13/14/15/16.

## 2. Foundational sources
- **VERIFIED by recomputation** (`_recompute.py`): batching throughput/latency (§3); retention &
  compaction sizing (§4); (fan-out tail reuses 13's verified `1−(1−q)^N`).
- **VERIFIED by reuse (line-checked earlier):** leader/ISR/HW/LEO, retention, compaction, zero-copy/
  sequential IO, batch+compression — **09**; durability dial + quorum/overlap + unclean-election CAP
  choice — **15 (+11)**; partition/shard key + hot partition + repartition cost + consistent hashing
  — **14 (+06)**; fan-out tail + Little's Law/amortization — **13**.
- **`[UNVERIFIED from fetched source]` (HTTP 000):** Kafka docs exact defaults (`acks`,
  `min.insync.replicas`, `linger.ms`, `batch.size`, `unclean.leader.election.enable`, compression
  codecs) and the Kafka paper / "Kafka: a Distributed Messaging System for Log Processing" (Kreps et
  al. NetDB 2011); Pulsar/BookKeeper, NATS JetStream, SQS/Kinesis durability docs. Mechanisms reused
  from verified 09/15/14/13; *vendor exact defaults* unfetched.

## 3. "Why it's this way" — forcing functions
- **Durability costs round-trips.** A message isn't safe until replicated; requiring more replicas to
  ack raises latency. `acks`/ISR is just 15's sync/async replication dial wearing broker clothes.
- **Throughput costs ordering and reshuffles.** Parallelism comes only from partitions, which cap
  ordering scope and are painful to change (14). So partition count is a durable architectural commit.
- **Replay horizon costs disk.** Retention buys replay + lag-tolerance linearly in traffic;
  compaction buys bounded state at the cost of losing history. The workload (events vs state) picks.
- **Throughput costs per-message latency.** Fixed per-batch costs only amortize if you wait to batch;
  that wait *is* latency. Speed-of-many and speed-of-one are different objectives (13).

## 4. Common misconceptions to preempt
- "`acks=all` is slow, use `acks=1`." `acks=1` can lose committed-looking data on leader failure;
  it's a durability *choice*, not a free speedup (15).
- "More partitions = strictly faster." More partitions = more files/rebalance overhead, smaller
  batches, more cross-partition disorder; size for need (14/Cs).
- "Retention forever is safest." It's unbounded disk; and it doesn't help if consumers are idempotent
  + checkpointed. Compaction is the bounded-state answer for changelogs.
- "Fan-out is free because the log is shared." Read fan-out is cheap (sequential reads); *write*
  fan-out amplifies and multiplies tail latency (13); celebrities make it pathological (14).
- "Bigger batches are always better." Throughput is concave (asymptotes at 1/m, §1.5) and linger
  latency grows; there's a knee, like 16's cache-size knee.
- "Compression is free throughput." It's CPU + latency for bytes-saved; depends on batch size + codec.

## 5. Best build-your-own target(s)
- **Replicated-log broker toy:** leader + ISR + HW; `acks` ∈ {0,1,all}; kill the leader mid-write and
  show data loss vs survival per `acks` (ties 15's failover lab). (pairs §1.1, reuse 09/15)
- **Partition-throughput bench:** vary partition count + producers; plot throughput; introduce a
  skewed key → hot partition; show the parallelism ceiling = partitions (ties Cluster C). (pairs
  §1.2, reuse 14)
- **Retention vs compaction lab:** same keyed stream under time-retention vs compaction; measure disk
  over time; confirm compaction floor = `keys·bytes` independent of history (`_recompute` §4).
  (pairs §1.4)
- **Batching knee finder:** sweep batch size/linger; plot throughput + p50/p99 latency; find the
  knee; add compression and re-measure (`_recompute` §3). (pairs §1.5, reuse 13)
- **Fan-out tail demo:** one event → N legs; measure P(slow) vs N against `1−(1−q)^N` (reuse 13);
  add coalescing/hedging. (pairs §1.3)

## 6. Open questions / gaps
- Fetch the Kafka paper (Kreps NetDB 2011) + Kafka/Pulsar/SQS/Kinesis durability+default docs when
  reachable to pin exact knob defaults + the original design rationale (HTTP 000). Mechanisms verified
  by reuse(09/15/14/13)+recomputation; *vendor exact defaults / original-paper attributions*
  `[UNVERIFIED]`.
- Boundary: feed fan-out-on-write/read full treatment → **21**; capacity/headroom for the broker
  fleet → **13/20**; broker SLOs (lag, ISR shrink, under-replicated partitions) → **19**; backpressure
  when consumers lag past retention → **18**.
