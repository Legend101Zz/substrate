# 17 — async-queues-and-event-driven-architecture — RECONCILED research (`_research.md`)

> **Phase 1 deliverable (NO course prose).** Synthesis of four factchecked clusters into the standard
> six sections (ADR-001: each cluster keeps its deep `_research_<cluster>.md`; this file reconciles
> overlaps, states the cross-cluster thesis, consolidates sources + gaps). Every `[UNVERIFIED from
> fetched source]` / residual gap from the clusters is preserved here in intent.
>
> **Cluster files (read for full depth):**
> - A — `_research_messaging-models-delivery-semantics.md` (queue vs log vs pub/sub; at-most/at-least/
>   effectively-once; idempotency + dedup-window sizing; per-partition ordering; outbox + CDC)
> - B — `_research_event-driven-architecture-patterns.md` (events vs commands; choreography vs
>   orchestration; sagas + compensation; event sourcing + CQRS; materialized-view maintenance;
>   backpressure handoff to 18)
> - C — `_research_producer-consumer-mechanics-failure.md` (consumer groups/rebalancing; commit/ack
>   timing; redelivery/backoff; DLQ/poison; exactly-once-effect; replay/reprocessing)
> - D — `_research_delivery-infrastructure-tradeoffs.md` (broker durability/replication; partitioning
>   for throughput; fan-out; retention vs compaction; latency-vs-throughput batching)
> - Math — `_recompute.py` (6 load-bearing computations, pure stdlib, 0 errors)
> - Factcheck — `_factcheck_phase1.md` (recompute / reuse / primary; **0 blockers**)
>
> **Reconciliation verdict:** 17 is reconciled. Its load-bearing content is verified end-to-end:
> **6 math claims by recomputation** (duplicate certainty, dedup-window sizing, batching throughput,
> retention/compaction sizing, parallelism ceiling, dual-write window), **every mechanism by reuse**
> of line-checked 09 (log/offsets/consumer-groups/EOS), 11 (ordering/2PC/impossibility), 13 (queueing/
> amortization/fan-out tail), 14 (shard key/hot partition/saga handoff), 15 (logical log→CDC/
> durability dial/quorum), 16/08 (stale-replica framing/coalescing/dedup store), and a **fresh
> production primary** (Nishtala NSDI '13: leases 17K→1.3K herd cut + mcsqueal CDC delete-stream). The
> remaining gaps are *canonical/vendor attributions* (AMQP/JMS/SQS/RabbitMQ/Kafka-KIPs/Debezium/
> Sagas-1987/Fowler-CQRS/Kreps-2011), carried forward `[UNVERIFIED]`. None is load-bearing for the
> method; none may harden into Phase-2 prose until fetched.

---

## The cross-cluster thesis (what this sub-course actually teaches)

17 is **the async backbone every prior Part-II sub-course hands work to.** 14 ends with cross-shard
operations it cannot make atomic (Cluster C → sagas). 15 ends with a logical replication log it uses
for durability (Cluster A → CDC). 16 ends with a write-back flush and a cross-region cache
invalidation it must *transport* (Clusters A/C/D → the delete stream). Each of those is the same
move: **stop doing the expensive/coordinated thing synchronously, and instead emit a durable record
that something else consumes later.** So the whole sub-course is one question:

> **You want to decouple "it happened" from "everyone who cares has reacted." What do you write down,
> how exactly-once is the reaction, what happens when a consumer dies, and what does the durable
> middle cost you in latency, disk, and ordering?**

The four clusters answer that in order:

1. **A — the substrate is a log, and the only honest delivery guarantee is at-least-once.** Queue
   (delete-on-ack), log (delete-on-retention, replayable cursor), and pub/sub (everyone-gets-a-copy)
   are one family; a log + consumer groups gives queue semantics within a group and pub/sub across
   groups (reuse 09). Over an unreliable network, exactly-once *delivery* is impossible (reuse 11),
   so duplicates are a **certainty** (`E[dups]=N·p`, verified) and "effectively-once" is built by the
   *consumer* via idempotency/dedup — whose store has a real size and a window bounded by the
   redelivery horizon (verified). And the dual-write between a DB and a broker leaks at scale
   (verified), so the **outbox/CDC** pattern — write the event in the same DB txn, then tail the
   commit log — is the structural fix (the **15 logical log re-pointed at a bus**, verified in
   production as Facebook's **mcsqueal**).
2. **B — events invert coupling, and that buys decoupling at the price of eventual consistency.**
   Commands are addressed imperatives; events are broadcast facts the emitter doesn't address.
   Choreography (decoupled, illegible) vs orchestration (legible, recoupled) is the topology choice.
   Sagas are the **14-Cluster-C cross-shard "transaction" handoff made real**: local txns +
   idempotent compensations + eventual consistency, because 2PC is unavailable (reuse 11/14). Event
   sourcing makes the **09 log the system of record** (isomorphic to 07's WAL / 15's replication
   log), and CQRS read models are **materialized views = deliberately-stale replicas** maintained by
   idempotent consumers — the exact 14/16 denormalization-and-staleness tradeoff, now stream-fed.
3. **C — the failure semantics live at the commit point, and one bad message must not stall the good
   ones.** Consumer groups share partitions one-owner-each; rebalancing reassigns on
   membership/heartbeat changes; parallelism is capped at the partition count (verified). **When you
   commit relative to processing IS the delivery semantic** (reuse A) — auto-commit silently picks
   one, so commit-after-processing is the honest default. Redelivery + capped-backoff + retry budgets
   + DLQs quarantine poison messages so throughput survives, and replay (an offset rewind, free from
   the log) is mass duplication that only idempotent consumers survive.
4. **D — the durable middle is a set of coupled dials, and every "faster" turn costs something
   else.** Broker durability is **15's sync/async dial** (`acks`/ISR; quorum overlap, unclean
   election = a CAP choice). Throughput comes only from **14's partitions** (which cap ordering and
   resist change). Retention buys replay-horizon linearly in traffic; compaction buys bounded state
   (floor = `keys·bytes`, history-independent — verified). And batching trades **13's per-message
   latency for throughput** (concave, asymptotes at `1/m` — verified). Conservation of pain, again.

The through-line, identical to 13/14/15/16: **push the expensive case out of the synchronous path and
make the rare-but-inevitable failure cheap** — accept at-least-once and make consumers idempotent,
replace dual-writes with the outbox/CDC, quarantine poison into DLQs, and size partitions/retention/
batching to the knee, not the maximum. Three primitives do double duty across clusters:
**idempotency** (A dedup = C replay-safety = B compensation = projection upsert), **the log itself**
(09 substrate = B event-sourcing SoT = A CDC source = C replay buffer), and the **durability/latency
dial** (15 `acks` = D broker durability = A outbox-vs-fast-publish).

---

## 1. Key mechanisms (consolidated)

- **Three messaging shapes:** queue (delete-on-ack, work-share), log (retain, replayable offset
  cursor), pub/sub (copy-per-subscriber); log + consumer groups unifies all three. *(A §1.1; reuse 09)*
- **Delivery semantics = commit point vs processing:** at-most-once (commit first), at-least-once
  (commit after), effectively-once (idempotency/transaction). Exactly-once *delivery* impossible. *(A §1.2, C §1.2; reuse 11)*
- **Duplicates certain at scale:** `E[dups]=N·p`, `P(≥1)=1−(1−p)^N`. **VERIFIED.** *(A §1.3)*
- **Idempotency + dedup-window:** window ≥ redelivery horizon (`Σcapped-backoff+visibility`=213 s ex.);
  store=`rate·window·bytes`. **VERIFIED.** Prefer natural idempotency (upsert/merge, reuse 15). *(A §1.4)*
- **Per-partition ordering only:** partition key = ordering domain = shard key (reuse 14); total order
  needs single partition / consensus (reuse 11). *(A §1.5)*
- **Outbox + CDC:** dual-write leaks (`~38/1e9` at 100 ms, **VERIFIED**); outbox = event in the same
  DB txn + relay; CDC = relay tails the logical/commit log (reuse 15). Production: **mcsqueal**
  (Nishtala '13, **PRIMARY**). *(A §1.6)*
- **Events vs commands; notification vs state-transfer:** fat events = denormalized read copy in
  flight (reuse 14). *(B §1.1)*
- **Choreography vs orchestration:** decoupling vs legibility/observability (→19). *(B §1.2)*
- **Sagas + compensation:** local txns + idempotent/retriable compensations + eventual consistency;
  the 14-Cluster-C cross-shard handoff; non-compensable steps go last. *(B §1.3; reuse 11/14)*
- **Event sourcing + CQRS:** log as SoT (= 07 WAL / 15 log); state = fold + snapshots; read models =
  materialized views = stale replicas maintained by idempotent upsert (reuse 14/15/16). *(B §1.4–1.5)*
- **Consumer groups + rebalancing:** one owner per partition; heartbeat-eviction; eager vs
  cooperative; parallelism ≤ partitions, need=`ceil(target/per)`. **VERIFIED.** *(C §1.1; reuse 09/14)*
- **Commit/ack timing:** manual commit-after-processing default; batch commit widens redelivery
  window (sizes dedup store). *(C §1.2; reuse 09)*
- **Redelivery/backoff/retry budget/retry-topics:** capped-exp-backoff+jitter (reuse 16); avoid
  head-of-line blocking. *(C §1.3)*
- **DLQ + poison messages + replay:** quarantine after budget; replay = offset rewind = mass dups →
  idempotency required. *(C §1.4–1.5; reuse 09)*
- **Broker durability/replication:** leader+ISR+HW; `acks`/`min.insync.replicas` = 15's durability
  dial; quorum overlap + unclean-election CAP choice. *(D §1.1; reuse 09/15/11)*
- **Partitioning for throughput:** partition = parallelism+ordering+placement; hot partition =
  celebrity key (reuse 14); repartition disruptive. *(D §1.2; reuse 14/06)*
- **Fan-out:** read fan-out cheap (group = full copy, sequential reads); write fan-out amplifies +
  multiplies tail `1−(1−q)^N` (reuse 13); fan-out-on-write/read → 21. *(D §1.3)*
- **Retention vs compaction:** time-retention for events (`rate·bytes·ret·RF`), compaction for state
  (floor `keys·bytes`, history-independent). **VERIFIED.** *(D §1.4; reuse 09)*
- **Batching:** tput=`1/(c/B+m)` → `1/m`; cost = linger latency; +compression. **VERIFIED.** *(D §1.5; reuse 13)*

## 2. Foundational sources (consolidated)

**VERIFIED BY RECOMPUTATION this session** (`_recompute.py`, pure stdlib, 0 errors): duplicate prob
`N·p`/`1−(1−p)^N`; dedup window = redelivery horizon + store size; batching tput `1/(c/B+m)`→`1/m`;
retention `rate·bytes·ret·RF` + compaction floor `keys·bytes`; parallelism ceiling `ceil(target/per)`;
dual-write window `window·crash_rate`.

**Verified by REUSE (line-checked earlier — NOT re-fetched):**
- Log/partitions/offsets/consumer-groups/coordinator/retention/compaction/idempotent-producer/
  transactional-offset-commit/LSO/`read_committed`/HW≤LEO/zero-copy — **09** `_research.md` (Kafka
  source `LocalLog.scala`/`LogSegment.java`/`LogCleaner.scala`/`GroupCoordinatorService`/
  `__consumer_offsets`).
- Per-partition partial order, total-order-needs-consensus, exactly-once-delivery impossible (Two
  Generals), 2PC blocking — **11**.
- Shard/partition key (ordering+parallelism+placement), hot shard/celebrity, repartition cost, cross-
  shard txn → saga, denormalized read copies, consistent hashing — **14** (+**06**).
- Logical/row replication log = CDC source, durability dial, quorum overlap `W+R>N` + majority
  tolerance `floor((N−1)/2)`, semilattice/idempotent merge, materialized-view-as-stale-replica +
  staleness ladder — **15** (+**11**).
- Cache/projection = deliberately-stale replica, backoff+jitter, coalescing, Redis/TTL dedup store —
  **16/08**.
- Little's Law/amortization, queueing latency wall, fan-out tail `1−(1−q)^N`, retry discipline —
  **13/03**.

**Verified from a FETCHED PRIMARY this session (network partially healed):**
- Nishtala et al., *Scaling Memcache at Facebook*, **NSDI '13** (`/tmp/nishtala.pdf`→`.txt`):
  demand-filled look-aside cache (cache-aside default); leases (64-bit token, 10 s regulation);
  thundering-herd cut **17K/s → 1.3K/s**; **mcsqueal** CDC delete-stream off the DB commit log
  broadcasting cross-region; only **4%** of deletes actually invalidate. The concrete production EDA/
  CDC instance for A §1.6 + B §1.5. *(Also opportunistically upgrades 16/08 carry-forward — see those
  factcheck updates.)*
- RFC 9111/5861/7234/4786 fetched (rfc-editor.org HTTP 200) — applied to **16** carry-forward (see
  16 factcheck update); not load-bearing for 17.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when net heals):**
- *(A)* AMQP 0-9-1 / JMS ack semantics; SQS visibility-timeout/FIFO dedup; RabbitMQ confirms/acks;
  Debezium docs; Kafka EOS KIPs (98/129/447).
- *(B)* Garcia-Molina & Salem "Sagas" SIGMOD 1987; Fowler Event-Sourcing/CQRS/EDA; Young/Dahan CQRS;
  Richardson microservices.io saga/outbox; Vernon/Evans DDD.
- *(C)* Kafka KIP-429 cooperative rebalance; exact `session.timeout.ms`/`max.poll.interval.ms`/
  `auto.offset.reset` wording; SQS redrive/DLQ + RabbitMQ DLX docs.
- *(D)* Kreps et al. "Kafka…" NetDB 2011; Kafka exact defaults (`acks`/`min.insync.replicas`/
  `linger.ms`/`batch.size`/unclean-election/codecs); Pulsar/BookKeeper, NATS JetStream, Kinesis docs.

## 3. "Why it's this way" — the forcing functions (consolidated)

- **The network loses/dups/reorders and consumers crash mid-work** → at-most-once or at-least-once
  are the only cheap guarantees; exactly-once delivery is impossible (11), so the duplicate burden is
  *designed onto* the idempotent consumer. *(A/C)*
- **Atomicity doesn't cross systems for free** → dual-write leaks; the outbox makes the event part of
  the one already-atomic thing (the DB txn); CDC reuses the log databases already keep (15). *(A/B)*
- **Order and parallelism are in tension** → per-partition order is the *price* of horizontal
  throughput (same 14 trade); partition count is a durable commitment. *(A/C/D)*
- **You can't atomically commit across services/shards under partition** → sagas: local txns +
  compensation + eventual consistency (11/14). *(B)*
- **The producer shouldn't know its consumers** → events invert coupling; the cost is eventual
  consistency + harder end-to-end observability (→19). *(B)*
- **Current state is a lossy summary of history** → event sourcing keeps the log as truth (the WAL/
  replication insight, 07/15) for audit/replay/rebuildable views. *(B)*
- **One bad message must not block the good ones** → retry budgets + backoff + DLQ quarantine
  failure so throughput survives. *(C)*
- **Every "faster" turn costs durability, ordering, disk, or latency** → `acks`/partitions/retention/
  batching are coupled dials; conservation of pain (13/14/15/16). *(D)*

## 4. Common misconceptions to preempt (consolidated)

- "Use a queue for everything." Queues delete-on-ack (no replay); logs retain (replay/fan-out). *(A)*
- "Exactly-once delivery exists / Kafka gives it." At-least-once + idempotency/transaction =
  exactly-once *effect*; external sinks still need dedup. *(A/C)*
- "Duplicates are rare." `E[dups]=N·p` → certain at scale. *(A)*
- "Idempotency keys are free." Dedup store has size `rate·window·bytes` + a window bounded by the
  redelivery horizon; too short leaks. *(A)*
- "Publish after the DB write is fine." Dual-write leaks (`~38/1e9` at 100 ms); use outbox/CDC. *(A)*
- "CDC is separate from replication." CDC *is* the logical replication log on a bus (15). *(A)*
- "Events = commands." Different intent/coupling direction. "Choreography always wins." Decoupled but
  illegible. "A saga is a distributed transaction." Not atomic, not isolated; idempotent
  compensations. "Event sourcing = event-driven." Orthogonal. "CQRS read models are consistent."
  Stale replicas with lag (15). "Replay rebuilds for free." O(events) without snapshots. *(B)*
- "Auto-commit is safe." It picks a semantic by timer; commit-after-processing is honest. "Add more
  consumers to go faster." Caps at partition count. "Retry until it works." Poison needs budget+DLQ.
  "A DLQ fixes failures." It quarantines; needs alert+drain+replay. "Replay is safe." Mass dups;
  needs idempotency. "Rebalancing is rare/cheap." Misconfig → storms. *(C)*
- "`acks=all` is just slow." `acks=1` can lose committed-looking data (15). "More partitions = strictly
  faster." Overhead + disorder; size for need. "Retention forever is safest." Unbounded disk;
  compaction is the bounded-state answer. "Fan-out is free." Write fan-out amplifies + multiplies tail
  (13); celebrities pathological (14). "Bigger batches always better." Concave, linger latency, knee.
  "Compression is free throughput." CPU+latency for bytes. *(D)*

## 5. Best build-your-own target(s) (consolidated)

- **Delivery-semantics + idempotency harness** (3 commit modes; inject ack loss `p`; count loss vs
  dup vs exactly-once-effect; dedup store sized to redelivery horizon; show too-short window leaks).
  *(A/C; pairs 09)*
- **Outbox + relay → CDC** (event+state in one DB txn; tail the table, then the WAL; kill mid-publish
  → no loss, only dups caught by dedup). *(A; pairs 07/15)*
- **Order saga, both styles** (orchestration + choreography; mid-saga failure → idempotent
  compensations restore consistency; make a hot partition with a skewed key). *(B/A; pairs 14)*
- **Event-sourced aggregate + CQRS projections** (log as SoT; fold + snapshots; 2 read models incl. a
  cache view; rebuild by replay; show read-your-writes violation + fix). *(B; pairs 09/07/16)*
- **Retry+DLQ pipeline** (capped-backoff+jitter, retry budget, DLQ w/ metadata; poison message keeps
  partition flowing; fix + idempotent DLQ replay). *(C)*
- **Replicated-log broker toy** (leader+ISR+HW; `acks`∈{0,1,all}; kill leader → loss-vs-survival per
  `acks`). **Partition-throughput bench** (parallelism ceiling = partitions; hot key). **Retention vs
  compaction lab** (floor = `keys·bytes`). **Batching knee finder** (sweep B/linger; throughput +
  p50/p99; +compression). **Fan-out tail demo** (`1−(1−q)^N`; add coalescing). *(D; pairs 09/15/14/13)*

## 6. Open questions / gaps to close (consolidated — preserved verbatim in intent)

- **All canonical/vendor attributions are network-blocked** `[UNVERIFIED]` except the freshly-fetched
  Nishtala '13: AMQP/JMS/SQS/RabbitMQ/Debezium (A), Sagas-1987/Fowler-CQRS/Richardson/DDD (B),
  Kafka-KIP-429/98/447 + vendor knob wording (C), Kreps-2011/Kafka-defaults/Pulsar/NATS/Kinesis (D).
  The *method/math* is verified by recomputation + reuse + the Nishtala primary; the *citations / exact
  vendor knob semantics / original-paper rationale* need primaries when the network heals. Teach
  mechanisms now; do NOT harden specifics into Phase-2 prose until fetched.
- **Disagreements to resolve with sources:** dedup default to teach (natural idempotency/upsert first,
  dedup store second, broker "exactly once" last-with-caveats); orchestration vs choreography default
  (likely choreographed events + a few orchestrated critical sagas); event-sourcing depth before
  deferring projection-rebuild/versioning to a future appendix.
- **Boundary discipline (cross-link, do NOT duplicate):**
  - log/partitions/offsets/consumer-groups/EOS *internals* → **09** (+ appendix **H** Kafka). 17
    reuses; owns the *messaging-model + EDA-pattern* layer.
  - ordering/causality/consensus/2PC *theory* → **11**; cross-shard txn *mechanics* → **14**.
  - logical replication log / durability dial / quorum *theory* → **15**; the cache-as-stale-replica
    + invalidation transport it hands off → **16** (17 owns the async transport).
  - **backpressure / load shedding / rate limiting** when consumers lag → **18** (handoff named, not
    derived).
  - **tracing a choreographed flow / DLQ-depth + lag SLOs** → **19**.
  - **fan-out-on-write/read feed problem, capacity/headroom** → **21 / 13 / 20**.
  - agentic orchestration / process-managers / state-persistence-resume → **26/27** (Part III).
- **Next 17 work (optional, before Phase 2 prose):** fetch the blocked AMQP/SQS/Kafka-KIP/Sagas/Fowler/
  Kreps primaries when the network is healthier and upgrade the `[UNVERIFIED]` flags; otherwise 17 is
  research-complete at the *method/math* level. **Next Phase-1 batch: 18-21** (Part II). **18
  (rate-limiting-backpressure-and-load-shedding / SEDA)** is the natural next start — it absorbs the
  lag/backpressure handoff that 17 Clusters B/C/D name.
