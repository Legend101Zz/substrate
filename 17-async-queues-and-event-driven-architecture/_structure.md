# 17 — Async Queues and Event-Driven Architecture · _structure.md

**Identity:** the async backbone every prior Part-II sub-course hands work to. The move is always
the same: stop doing the expensive/coordinated thing synchronously, and instead emit a durable
record that something else consumes later. Decouple "it happened" from "everyone who cares has
reacted."

**Bespoke shape — "write it down → react exactly-once → survive the consumer dying → price the
durable middle."** NOT a broker feature tour. 14 hands off cross-shard ops it can't make atomic
(→sagas), 15 hands off a logical log (→CDC), 16 hands off invalidation it must transport (→delete
stream) — each is the same move. The sub-course is four clusters answering one question in order:
**A — the substrate is a log + at-least-once is the only honest guarantee → B — events invert
coupling, buying decoupling at the price of eventual consistency → C — the failure semantics live
at the commit point, one bad message must not stall the good → D — the durable middle is coupled
dials, every "faster" turn costs something.** Three primitives recur: idempotency, the log itself,
the durability/latency dial. Math verified by recomputation; a real production primary anchors it.

## Dependency position
- **Depends on:** 09 (the log/partitions/offsets/consumer-groups/EOS substrate — 17 reuses, owns
  the messaging-model + EDA-pattern layer), 11 (ordering/causality/2PC/exactly-once-delivery
  impossible), 14 (shard key = ordering domain, hot partition, cross-shard txn → saga), 15 (logical
  log → CDC, durability dial, quorum, materialized-view = stale replica), 16/08 (cache-as-stale-
  replica, coalescing, dedup store), 13/03 (queueing/amortization/fan-out tail, retry discipline).
- **Feeds into:** 18 (backpressure/load-shedding when consumers lag — named, not derived), 19
  (tracing choreographed flows; lag/DLQ-depth SLOs), 20 (fan-out tail capacity), 21 (feed/chat/
  payments), 26/27 (agentic orchestration/process-managers/resume).
- **Appendix links DOWN:** H-kafka (the broker internals), F-postgres (outbox/CDC source).

## Chapter specs (3–5 lines each)
### A — write it down (substrate + delivery)
1. **Three messaging shapes are one family** — queue (delete-on-ack, work-share), log (retain,
   replayable offset cursor), pub/sub (copy-per-subscriber); a log + consumer groups unifies all
   three (queue within a group, pub/sub across groups). Reuse 09.
2. **At-least-once is the only honest guarantee** — exactly-once DELIVERY is impossible over an
   unreliable network (11); duplicates are a CERTAINTY (`E[dups]=N·p`, VERIFIED). "Effectively-
   once" is built by the CONSUMER via idempotency/dedup — whose store has size `rate·window·bytes`
   and a window bounded by the redelivery horizon (VERIFIED; too short leaks). Per-partition
   ordering ONLY (partition key = ordering domain = shard key, 14).
3. **Outbox + CDC: the dual-write fix** — writing to a DB AND a broker leaks at scale
   (`~38/1e9` at 100ms, VERIFIED). Outbox = emit the event in the SAME DB txn; CDC = a relay tails
   the commit/logical log (15's log re-pointed at a bus). Production instance: Facebook's
   **mcsqueal** (Nishtala NSDI'13, VERIFIED primary).

### B — react (events + patterns)
4. **Events vs commands; the coupling inversion** — commands are addressed imperatives; events are
   broadcast facts the emitter doesn't address. Choreography (decoupled, illegible) vs orchestration
   (legible, recoupled) is the topology choice. Fat events = a denormalized read copy in flight (14).
5. **Sagas: cross-shard "transactions" made real** — the 14-Cluster-C handoff: local txns +
   idempotent/retriable compensations + eventual consistency, because 2PC is unavailable (11/14).
   Non-compensable steps go last. NOT atomic, NOT isolated.
6. **Event sourcing & CQRS** — the log becomes the system of record (isomorphic to 07's WAL / 15's
   replication log); state = fold + snapshots. CQRS read models = materialized views = deliberately-
   stale replicas maintained by idempotent upsert (14/15/16 tradeoff, stream-fed). Replay rebuilds
   views (O(events) without snapshots).

### C — survive failure (the commit point)
7. **Consumer groups, commit timing & redelivery** — groups share partitions one-owner-each;
   rebalancing reassigns on membership/heartbeat changes; parallelism ≤ partition count (VERIFIED).
   WHEN you commit relative to processing IS the delivery semantic (auto-commit silently picks one;
   commit-after-processing is the honest default). Redelivery + capped-backoff + jitter + retry
   budgets avoid head-of-line blocking.
8. **DLQ, poison messages & replay** — quarantine poison after the budget so throughput survives; a
   DLQ needs alert + drain + replay, it doesn't "fix" anything. Replay = an offset rewind (free from
   the log) = mass duplication that only idempotent consumers survive.

### D — price the middle (coupled dials)
9. **Durability & partitioning dials** — broker durability = 15's sync/async dial (`acks`/ISR/
   `min.insync.replicas`; quorum overlap + unclean-election = a CAP choice). Throughput comes ONLY
   from 14's partitions (which cap ordering and resist change). Hot partition = celebrity key (14).
10. **Retention, compaction & batching** — retention buys replay-horizon linearly in traffic
    (`rate·bytes·ret·RF`); compaction buys bounded state (floor `keys·bytes`, history-independent,
    VERIFIED). Batching trades 13's per-message latency for throughput (`1/(c/B+m)`→`1/m`, concave,
    VERIFIED) + compression (CPU for bytes). Conservation of pain, again.

## Paired build labs (/build — harnesses)
Delivery-semantics + idempotency harness (3 commit modes; inject ack loss `p`; count loss vs dup
vs exactly-once-effect; dedup store sized to redelivery horizon; show too-short window leaks) →
outbox + relay → CDC (event+state in one DB txn; tail the table then the WAL; kill mid-publish →
no loss, only dups caught by dedup) → order saga both styles (orchestration + choreography; mid-
saga failure → idempotent compensations; skewed key → hot partition) → event-sourced aggregate +
CQRS projections (log as SoT; fold + snapshots; 2 read models incl. a cache view; rebuild by
replay; read-your-writes violation + fix) → retry+DLQ pipeline (capped-backoff+jitter, budget, DLQ
metadata; poison keeps the partition flowing; idempotent DLQ replay) → replicated-log broker toy
(leader+ISR+HW; `acks`∈{0,1,all}; kill leader → loss-vs-survival) → partition-throughput bench
(ceiling = partitions; hot key) → retention vs compaction lab (floor `keys·bytes`) → batching knee
finder (sweep B/linger; throughput + p50/p99; +compression) → fan-out tail demo.

## Diagrams needed
- The four-cluster arc (write-down → react → survive → price) as spine motif.
- Queue/log/pub-sub unified by log + consumer groups.
- Dual-write leak vs outbox (event in the DB txn) vs CDC (relay tails the log).
- Events-vs-commands coupling direction; choreography vs orchestration topology.
- Saga: local txns + compensations (vs 2PC's prepare/commit blocking).
- Event sourcing: log as SoT → fold + snapshots → CQRS read models (stale replicas).
- Commit-point timeline (before/after processing = the delivery semantic); redelivery + DLQ.
- `acks`/ISR durability dial; batching knee (`1/(c/B+m)`); retention vs compaction floor.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED BY RECOMPUTATION:** duplicate prob `N·p`/`1−(1−p)^N`; dedup window = redelivery horizon
  + store size; batching `1/(c/B+m)→1/m`; retention `rate·bytes·ret·RF` + compaction floor
  `keys·bytes`; parallelism ceiling `ceil(target/per)`; dual-write window `window·crash_rate`.
- **VERIFIED PRIMARY this session:** Nishtala NSDI'13 (cache-aside default; leases 17K→1.3K herd;
  **mcsqueal** CDC delete-stream; only 4% of deletes invalidate). Also RFC 9111/5861/7234/4786
  fetched (applied to 16 carry-forward).
- **`[UNVERIFIED]` — network-blocked, fetch before hardening:** AMQP/JMS/SQS/RabbitMQ/Debezium (A),
  Sagas-1987/Fowler-CQRS/Richardson/DDD (B), Kafka KIP-429/98/447 + vendor knob wording (C), Kreps-
  2011/Kafka-defaults/Pulsar/NATS/Kinesis (D). Teach mechanisms now; do NOT harden vendor knob
  semantics or original-paper rationale until fetched.
- **Disagreements to resolve:** dedup default (natural idempotency/upsert first, dedup store second,
  broker "exactly once" last-with-caveats); orchestration vs choreography default (likely
  choreographed events + a few orchestrated critical sagas); event-sourcing depth before deferring
  projection-rebuild/versioning to an appendix.
- **Boundary discipline:** log/partitions/offsets/consumer-groups/EOS internals → 09 (+ appendix H);
  ordering/consensus/2PC theory → 11; cross-shard txn mechanics → 14; durability/quorum theory + the
  cache-as-stale-replica → 15/16 (17 owns the async transport); backpressure/shedding/rate-limiting
  → 18; tracing/lag SLOs → 19; fan-out feed problem + capacity → 21/13/20; agentic orchestration →
  26/27.
