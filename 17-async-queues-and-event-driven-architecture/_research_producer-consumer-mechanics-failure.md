# 17 · Cluster C — Producer/consumer mechanics + failure (research brief)

> **Phase 1 brief. NO course prose.** `[UNVERIFIED from fetched source]` = not confirmed against a
> fetched primary this session. Canon reused from line-verified sub-courses is **(reuse NN)**. Math
> recomputed in `_recompute.py`.

## 1. Key mechanisms

### 1.1 Consumer groups + rebalancing
- A **consumer group** splits a topic's partitions across its members so each partition is owned by
  *exactly one* member (within the group) — work-sharing with per-partition order preserved (**reuse
  09 §1.6 GroupCoordinator; reuse Cluster A §1.1/§1.5**).
- **Rebalance** = reassigning partitions when membership changes (member joins/leaves/dies) or topic
  metadata changes. Triggered by the **group coordinator** via heartbeats; a missed
  `session.timeout` evicts a member and reassigns its partitions.
- **Stop-the-world vs incremental/cooperative rebalancing:** eager rebalance revokes *all*
  assignments then re-divides (a full pause); cooperative/incremental rebalance only moves the
  partitions that must move (less disruption). **(reuse 09 rebalance states `ClassicGroupState`.)**
- **Rebalance storms**: too-short `session.timeout` + slow processing → spurious evictions →
  thrash. Long GC pauses or long `poll()` gaps look like death. The fix is decoupling liveness
  (heartbeat) from progress (`max.poll.interval`).
- **Parallelism ceiling (recomputed):** useful consumers per group ≤ partition count; extras idle.
  Required partitions = `ceil(target_tput / per_consumer_tput)` (e.g. 500K/s ÷ 20K/s ⇒ **25
  partitions**). **VERIFIED `_recompute.py` §5.** Partition count is simultaneously the parallelism
  unit and the ordering domain (Cluster A §1.5) → choose it for the *max* of throughput-need and
  ordering-need, then live with it (repartitioning is disruptive, **reuse 14 rebalancing**).

### 1.2 Commit / ack timing (where the semantics live)
- The **commit point relative to processing** *is* the delivery semantic (**reuse Cluster A §1.2**):
  - commit-before-process → at-most-once (loss on crash);
  - commit-after-process → at-least-once (dup on crash/redelivery);
  - atomic process+commit (transaction/idempotent) → effectively-once.
- **Auto-commit** (periodic, time-based) silently gives at-most-once *or* at-least-once depending on
  whether the timer fires before/after processing — a classic footgun; prefer **manual commit after
  processing**. **(reuse 09 §1.7 position vs committed; commit N+1 after processing N.)**
- **Batch commit vs per-message commit:** committing per message is safe but slow; committing per
  batch is fast but widens the redelivery window on crash (you reprocess the whole uncommitted
  batch). The redelivery window directly sizes the dedup store (**reuse Cluster A §1.4 / `_recompute`
  §2**).
- **Ack models in queues:** explicit ack (broker holds in-flight until ack, redelivers on timeout =
  **visibility timeout**), negative-ack/requeue, and ack-deadline extension for long work. Same
  semantics, different vocabulary.

### 1.3 Redelivery, retries, and backoff
- On nack/timeout/crash the message is **redelivered**. Naive immediate retry of a poison message =
  hot loop. Use **capped exponential backoff (+ jitter)** (**reuse 16 stampede jitter; reuse 03/13
  retry discipline**) — the same backoff that sizes the dedup window (`_recompute.py` §2).
- **Retry budget**: bound total retries; unbounded retry of a permanently-failing message blocks the
  partition (head-of-line blocking) and starves healthy messages behind it.
- **Retry topics / delay queues**: move a failing message to a separate retry topic with a delay so
  the main partition keeps flowing (sidesteps head-of-line blocking) at the cost of losing strict
  order for that message.

### 1.4 Dead-letter queues (DLQ) + poison messages
- A **poison message** can never be processed (malformed, references deleted state, triggers a bug);
  retrying it forever stalls the consumer. After the retry budget is exhausted, route it to a
  **dead-letter queue** for out-of-band inspection/repair/replay.
- DLQ design: carry the failure metadata (error, attempt count, original topic/offset/partition,
  timestamp) so it's debuggable and replayable. A DLQ with no alerting/draining is a silent data-loss
  sink — monitor depth (handoff → **19** SLOs on DLQ depth).
- **Replay/reprocessing:** because a log retains messages (**reuse 09**), reprocessing = reset the
  consumer-group offset backward and re-consume — but **only safe if consumers are idempotent**
  (replay = mass duplicates by construction; **reuse Cluster A §1.3 `E[dups]=N·p`**). For DLQ:
  fix the bug, then replay the DLQ back into the main flow through the same idempotent consumer.

### 1.5 Exactly-once-*effect* on the consumer
- Two mechanisms (**reuse Cluster A §1.2 + 09 EOS**):
  1. **Idempotent consumer**: at-least-once + dedup store keyed by message/idempotency id, sized to
     the redelivery window (`_recompute.py` §2). Works for *any* sink.
  2. **Transactional consume-transform-produce**: atomically commit output records + input offset in
     one broker transaction (Kafka EOS, `read_committed`/LSO). Works only when the sink is the *same*
     broker; external sinks fall back to idempotence. **(reuse 09 delivery-semantics-transactions.)**
- Teaching default: design natural idempotency (upsert/merge, **reuse 15 semilattice**) → dedup store
  → broker transaction last.

### 1.6 Failure modes catalogue (what actually breaks)
- **Slow consumer** → lag grows → buffer/retention pressure → eventually data loss if lag exceeds
  retention (**reuse 09 retention; Cluster D**). Handoff to **18** backpressure.
- **Stuck consumer** (long GC/processing) → missed heartbeat → rebalance → its in-flight work
  redelivered → duplicates.
- **Rebalance during processing** → uncommitted work reprocessed → duplicates (idempotency saves you).
- **Offset reset** (`auto.offset.reset=earliest/latest`) on a lost committed offset → mass replay or
  silent skip — pick deliberately.
- **Ordering break** under concurrent processing of one partition → only single-threaded-per-partition
  preserves order (Cluster A §1.5).

## 2. Foundational sources
- **VERIFIED by recomputation** (`_recompute.py`): parallelism ceiling / required partitions (§5);
  dedup/redelivery window (§2); duplicate certainty under replay (§1).
- **VERIFIED by reuse (line-checked earlier):** consumer groups / coordinator / rebalance states /
  position-vs-committed / EOS transactions / retention / compaction — **09**; backoff+jitter — **16**;
  retry discipline — **03/13**; idempotent merge — **15**; partition/rebalance cost — **14**.
- **`[UNVERIFIED from fetched source]` (HTTP 000):** Kafka KIP-429 (cooperative rebalancing), KIP-98/
  447 (EOS), exact `session.timeout.ms`/`max.poll.interval.ms`/`auto.offset.reset` doc wording
  (kafka.apache.org); SQS visibility-timeout/redrive-policy/DLQ + RabbitMQ dead-letter-exchange docs.
  Mechanisms reused from verified 09; vendor exact knob semantics unfetched.

## 3. "Why it's this way" — forcing functions
- **A consumer can stall or die mid-message, indistinguishably from being slow.** So liveness is
  inferred from heartbeats and progress from offset commits — and the *gap* between "did the work" and
  "recorded the work" is exactly where duplicates/loss live. Commit timing is therefore the load-
  bearing design decision, not an afterthought.
- **One bad message must not block the good ones.** Unbounded in-place retry causes head-of-line
  blocking; retry budgets + backoff + retry-topics + DLQ exist to *quarantine* failure so throughput
  survives.
- **Replay is a feature of the log, not a special tool.** Retention (09) means reprocessing is just
  an offset rewind — which makes idempotency non-optional, because replay is duplicate generation by
  design.
- **Partition count is a one-time-ish commitment.** It caps parallelism and defines ordering;
  changing it is disruptive (14), so it's sized up front for max(throughput, ordering) need.

## 4. Common misconceptions to preempt
- "Auto-commit is convenient and safe." It quietly picks a semantic by timer; manual commit after
  processing is the honest default.
- "Add more consumers to go faster." Only up to partition count; beyond that they idle (§1.1 verified).
- "Retry until it works." Poison messages need a budget + DLQ, else head-of-line blocking stalls the
  partition.
- "A DLQ fixes failures." It quarantines them; without alerting + drain + replay it's silent loss.
- "Replay is safe." Replay is mass duplication; only idempotent consumers survive it.
- "Rebalancing is rare/cheap." Misconfigured timeouts cause storms; long pauses look like death.
- "Exactly-once is a broker checkbox." It's consumer-side (idempotency) or broker-transactional with
  a same-broker-sink caveat.

## 5. Best build-your-own target(s)
- **Consumer-group coordinator toy:** assign partitions to members, heartbeat-evict on timeout,
  rebalance (eager then cooperative); show parallelism caps at partition count. (pairs §1.1, reuse 09)
- **Commit-timing matrix:** same workload under commit-before / commit-after / atomic; crash-inject;
  count loss vs dups vs exactly-once-effect (ties Cluster A harness). (pairs §1.2)
- **Retry + DLQ pipeline:** capped-exp-backoff + jitter, retry budget, DLQ with failure metadata;
  feed a poison message; show the partition keeps flowing; fix + replay the DLQ idempotently.
  (pairs §1.3–1.4)
- **Replay-safety demo:** rewind offsets and re-consume; show duplicate explosion without dedup,
  clean result with the idempotent consumer. (pairs §1.4–1.5, reuse Cluster A)

## 6. Open questions / gaps
- Fetch Kafka KIP-429/98/447 + SQS/RabbitMQ DLQ/visibility docs when reachable to pin exact knob
  semantics (HTTP 000). Mechanisms verified by reuse(09)+recomputation; *vendor exact wording*
  `[UNVERIFIED]`.
- Boundary: lag-driven backpressure/shedding → **18**; DLQ-depth/lag SLOs + tracing redeliveries →
  **19**; broker-side durability that bounds retention/loss → Cluster D.
