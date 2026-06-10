# 17 · Cluster B — Event-driven architecture + patterns (research brief)

> **Phase 1 brief. NO course prose.** `[UNVERIFIED from fetched source]` = not confirmed against a
> fetched primary this session. Canon reused from line-verified sub-courses is **(reuse NN)** and not
> re-derived. Math (where present) recomputed in `_recompute.py`.

## 1. Key mechanisms

### 1.1 Events vs commands (the orientation of intent)
- **Command**: an imperative *request* to do something, addressed to one handler, may be rejected
  (`PlaceOrder`). Expects an outcome. Coupling points *forward* (caller knows the callee).
- **Event**: an immutable *fact* that already happened, broadcast, not addressed (`OrderPlaced`).
  Cannot be rejected (it's history). Coupling points *backward* (subscribers know the event, the
  emitter doesn't know them). This inversion is the whole point of EDA: the producer is decoupled
  from an open set of consumers.
- **Event notification vs event-carried state transfer:** a thin event (`OrderPlaced{id}`) forces
  consumers to call back for data (chatty, coupled, but always fresh); a fat event
  (`OrderPlaced{id, items, total, customer}`) carries the state so consumers need no callback
  (autonomous, but the data can be stale and the schema couples). The fat form is a **denormalized
  read copy in flight** — the same denormalization tradeoff as **14 Cluster A** (**reuse 14**:
  read/write tax of denormalization) and a staleness source like **15/16**.

### 1.2 Choreography vs orchestration
- **Choreography**: no central brain; each service reacts to events and emits its own. Emergent flow.
  Maximally decoupled, maximally hard to *observe* (the business process exists only as a trace
  across services — handoff to **19** observability/tracing). Failure handling is distributed.
- **Orchestration**: a central coordinator (the orchestrator / process manager / saga executor)
  issues commands and awaits events, owning the workflow state machine. Easier to reason about,
  observe, and change; reintroduces a coupling hub and a thing that can fail (so the orchestrator
  itself needs persistence + resume — handoff to **26** in Part III, and durability here).
- The choice is **legibility vs decoupling**; most real systems mix (choreographed events with a few
  orchestrated critical flows).

### 1.3 Sagas + compensation (distributed "transactions" without 2PC)
- A **saga** is a sequence of local transactions, each in its own service/shard, where a failure
  triggers **compensating transactions** that semantically undo the prior steps — because a true
  atomic cross-service/cross-shard commit needs 2PC, which is blocking and unavailable under
  partition (**reuse 11** 2PC blocking; **reuse 14 Cluster C** cross-shard transactions handoff).
- This is **exactly the 14 Cluster C cross-partition-operations handoff** made concrete (**reuse
  14**): you can't hold one ACID transaction across shards/services, so you trade *atomicity* for
  *eventual consistency + compensation*. The saga is the async/event-driven realization of that
  trade.
- **Compensation ≠ rollback:** a compensating action is itself a new forward transaction
  (`RefundPayment` undoes `ChargePayment`); it can fail and must be retried → **compensations must be
  idempotent and retriable** (**reuse Cluster A §1.4 idempotency**). Some steps are *not* compensable
  (you can't un-send an email) → put non-compensable steps last (pivot transaction) or make them
  *retriable* instead.
- **Orchestration saga** (central executor drives steps + compensation) vs **choreography saga**
  (each step emits an event the next step listens for; compensation flows backward by events). Same
  Cluster B tradeoff applied to the saga.
- **Isolation is lost:** sagas are not isolated (other txns see intermediate states); countermeasures
  = semantic locks, commutative updates, reread-and-check (a known saga gotcha). `[UNVERIFIED from
  fetched source]` — Garcia-Molina & Salem "Sagas" SIGMOD 1987 still HTTP 000; mechanism reused via
  11/14.

### 1.4 Event sourcing + CQRS
- **Event sourcing**: the source of truth is the **append-only log of events**, not current state;
  current state is a *fold* (left-reduce) over the event history. This is the **09 log abstraction as
  the system of record** (**reuse 09**) and is *isomorphic to a database's WAL/replication log*
  (**reuse 07 WAL, 15 logical log**) — the log was always the truth; event sourcing just makes it the
  public API.
  - Wins: perfect audit, time-travel/replay, rebuild any projection, temporal queries.
  - Costs: queries need projections (you can't `SELECT` a fold cheaply), schema/versioning of old
    events forever, and **eventual consistency** between the log and its read models.
- **Snapshots**: replaying all history is O(events); periodic snapshots bound replay cost — the same
  **checkpoint idea as 09 offsets / 07 checkpoints** (**reuse**).
- **CQRS (Command Query Responsibility Segregation)**: separate the **write model** (validates
  commands, appends events) from one-or-many **read models** (denormalized projections optimized per
  query). Pairs naturally with event sourcing but is independent of it.
  - The read models are **materialized views maintained asynchronously off the event stream** — the
    *same* materialized-view maintenance as **14 (denormalized read copies)** and **16 (cache as a
    derived view)** (**reuse 14/16**), now fed by events. They are **eventually consistent** with the
    write side (lag = the 15 replication-lag window; **reuse 15 Cluster B** read-your-writes /
    monotonic-reads anomalies apply verbatim to "read your own command's effect").

### 1.5 Materialized-view maintenance off a stream
- A projection consumes the event log and upserts a query-shaped table/cache. Maintenance =
  at-least-once consume + **idempotent upsert keyed by event id/version** (**reuse Cluster A §1.4;
  reuse 15 conflict version**) so replays/duplicates don't double-apply.
- Rebuild = replay the log from offset 0 into a fresh projection (the **09 replay** capability).
  Compaction (**reuse 09 LogCleaner**) keeps a keyed changelog bounded to one record per key — the
  **changelog/CDC floor** (recomputed: floor = `unique_keys · bytes/key`, independent of write
  history; **`_recompute.py` §4**).
- Consistency contract to teach: a projection is a **deliberately-stale replica** bounded by consume
  lag — identical framing to 16's "a cache is a stale replica" (**reuse 16**).

### 1.6 Backpressure (handoff, not derived here)
- When consumers can't keep up, lag grows (buffer fills). Options: bound the buffer + shed/throttle
  producers, or scale consumers (≤ partitions, Cluster C/D). The **mechanisms of backpressure / load
  shedding / rate limiting are 18's job** — Cluster B only names the handoff: an event-driven system
  *converts* synchronous overload into a *growing queue*, which trades latency for survival and must
  be bounded. **(handoff → 18; reuse 13 queueing: unbounded queue + ρ→1 ⇒ unbounded latency.)**

## 2. Foundational sources
- **VERIFIED by reuse (line-checked earlier):** log-as-truth / replay / compaction / offsets — **09**;
  WAL as event log / checkpoints — **07**; logical replication log — **15 Cluster A**; denormalized
  read copies + cross-partition ops / sagas handoff — **14 Cluster A/C**; materialized view = stale
  replica + staleness ladder — **15 Cluster B / 16**; 2PC blocking / partial order — **11**;
  queueing latency wall — **13**.
- **VERIFIED from fetched primary this session:** the production EDA instance of CDC-driven async
  view (cache) invalidation — mcsqueal in Nishtala NSDI '13 (see Cluster A §1.6). `/tmp/nishtala.pdf`.
- **`[UNVERIFIED from fetched source]` (HTTP 000 this session):** Garcia-Molina & Salem "Sagas"
  SIGMOD 1987; Fowler "Event Sourcing"/"CQRS"/"What do you mean by Event-Driven?" (martinfowler.com);
  Young/Dahan CQRS write-ups; Vernon/Evans DDD aggregates-emit-events; Richardson microservices.io
  saga/outbox patterns. Mechanisms reused from verified 09/11/14/15/16; the *named-pattern attributions*
  are unfetched.

## 3. "Why it's this way" — forcing functions
- **You can't atomically commit across services/shards under partition (11/14).** So multi-step
  business processes become sagas: local atomicity + compensation + eventual consistency. EDA is the
  delivery vehicle for that trade.
- **The producer shouldn't have to know its consumers.** Events (facts, broadcast) invert the
  dependency so new consumers attach without touching the producer — the core decoupling win, paid
  for with eventual consistency and harder end-to-end observability (→19).
- **Current state is a lossy summary of history.** Event sourcing keeps the history as truth because
  the log is already how databases stay consistent internally (WAL/replication, 07/15); exposing it
  buys audit + replay + rebuildable views, paid for with projection lag + event-schema-forever.
- **Reads and writes want different shapes.** CQRS splits them so each is optimal; the read side is a
  materialized view = a derived, eventually-consistent replica (same as 14/16) maintained by
  idempotent consumers.

## 4. Common misconceptions to preempt
- "Events and commands are the same message." Different intent/coupling direction; conflating them
  recouples the system.
- "Choreography is always more scalable, so always use it." It's more decoupled but the business
  process becomes invisible — orchestration trades coupling for legibility/observability.
- "A saga is a distributed transaction." It is *not* atomic and *not* isolated; it's local txns +
  compensations + eventual consistency. Compensations are new forward txns and must be idempotent.
- "Event sourcing = event-driven." Orthogonal: event sourcing is a *storage/SoT* choice; EDA is a
  *communication* style. CQRS is a third orthogonal axis.
- "CQRS read models are consistent." They're materialized views with replication lag (15) — read-
  your-writes can break right after a command; design for it.
- "Just replay the log to rebuild." Fine, but O(events) without snapshots; and event-schema evolution
  must be handled forever.
- "EDA removes coupling." It moves coupling from *call graph* to *event schema* + introduces eventual
  consistency and distributed failure modes; it's a different coupling, not none.

## 5. Best build-your-own target(s)
- **Order saga (both styles):** implement `PlaceOrder` across payment/inventory/shipping as an
  orchestration saga *and* a choreography saga; inject a mid-saga failure; verify compensations
  (idempotent, retriable) restore a consistent end state. (pairs §1.2–1.3, reuse 14)
- **Event-sourced aggregate + projections:** append events as SoT; fold to current state; build 2
  CQRS read models (one row-store query view, one cache view, reuse 16); rebuild a projection by
  replay; add snapshots and measure replay cost before/after. (pairs §1.4–1.5, reuse 09/07)
- **Projection lag demo:** issue a command, immediately query the read model, observe stale/missing
  result (read-your-writes violation, reuse 15); fix with read-from-write-model-until-caught-up.
- **Notification vs state-transfer bake-off:** thin vs fat events; measure callback chattiness vs
  staleness/schema-coupling. (pairs §1.1, reuse 14)

## 6. Open questions / gaps
- Fetch Fowler/Richardson/Young + Garcia-Molina "Sagas" when reachable to pin pattern attributions
  (HTTP 000). Mechanisms verified by reuse; *named-pattern citations* `[UNVERIFIED]`.
- Decide depth split with Part III: agentic orchestration/process-managers + state-persistence/resume
  belong to **26/27**; Cluster B teaches the *data-plane* saga/EDA, cross-links forward.
- Boundary: backpressure/shedding internals → **18**; tracing a choreographed flow → **19**;
  exactly-once consumer/dedup mechanics → Cluster A; broker durability/partitioning → Cluster D.
