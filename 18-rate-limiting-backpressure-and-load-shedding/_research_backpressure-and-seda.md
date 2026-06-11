# 18 · Cluster B — Backpressure (bounded queues, flow control, the SEDA model)

> Phase-1 brief (NO course prose). ADR-001 cluster file. Math RECOMPUTED in `_recompute.py`
> (block B1). `[UNVERIFIED]` = not confirmed from a fetched primary this session.

## Scope
Backpressure = **propagating "I am full, slow down" upstream** so a fast producer cannot
overwhelm a slow consumer. It is the structural answer to 17's named handoff (consumers fall
behind → queue grows → must be bounded) and to 13's queueing wall (`ρ→1` ⇒ unbounded latency).
The core insight: **an unbounded queue is not a safety mechanism, it is a way to convert an
overload into an out-of-memory crash plus unbounded latency.** This cluster covers bounded
queues, blocking-vs-dropping, credit/flow control, end-to-end vs hop-by-hop, and the SEDA
stage/queue/controller model.

## 1. Key mechanisms

### 1.1 Why bound the queue at all (the 13 handoff made concrete)
- From 13 (line-verified): in an M/M/1 queue, waiting time `W = S/(1−ρ)` → ∞ as utilization
  `ρ→1`. An **unbounded** buffer in front of a saturated server therefore grows without limit:
  latency explodes and memory is exhausted (the 17 consumer-lag scenario).
- VERIFIED (B1, reuse of 13's Little's Law): a bounded queue of capacity `Q` drained at rate
  `μ` adds **at most `Q/μ`** waiting time. Google SRE (cascading-failures, **VERIFIED**) gives
  the concrete case: a queue 10× the thread-pool size with 100 ms service time means a request
  that lands on a full queue waits **~1.0 s** ("most of which is spent on the queue"); a queue
  sized at **50% of the pool** bounds added latency to **~0.05 s** and makes the server
  **reject early** instead of building a deep, latent backlog. So: *small queues reject early
  and keep latency low; deep queues hide overload and convert it to latency + OOM.*

### 1.2 Bounded queue → blocking vs dropping (the fork)
Once the queue is full, you must do exactly one of:
- **Block the producer** (apply pressure) — correct when the producer *can* slow down and you
  want lossless flow (in-process pipelines, TCP-backed streams). Propagates the pressure
  upstream hop by hop.
- **Drop / reject** (shed) — correct when the producer *cannot* be slowed (the open Internet,
  fire-and-forget) or when stale work is worthless; return 429/503 and let the client decide
  (handoff to Cluster C). Google SRE: "fail early and cheaply" with HTTP 503 when in-flight
  exceeds a threshold (**VERIFIED**).
The choice is governed by whether the producer is *controllable*. You cannot "block" the
Internet; you can block your own thread pool's upstream stage.

### 1.3 Credit / flow control (the explicit mechanism)
- **TCP flow control (reuse 03, line-verified):** the receiver advertises a *window* = how many
  bytes it has buffer for; the sender may not exceed it. This is backpressure as a **credit
  scheme** — the canonical, decades-proven design. (Distinct from congestion control, which
  reacts to *network* loss, not receiver buffer.)
- **Reactive-Streams-style credit:** the consumer `request(n)` items; the producer may emit at
  most `n` before receiving more demand. Demand flows *backward*, data flows *forward*. Same
  shape as TCP windows applied to in-process/streaming pipelines.
- **17 consumer lag (reuse):** in a log, the broker doesn't push — the consumer *pulls* at its
  own pace, so the log itself is the bounded buffer (bounded by retention), and "lag" (offset
  distance) is the backpressure signal. Pull = built-in backpressure; push needs explicit
  credit.

### 1.4 End-to-end vs hop-by-hop
- **Hop-by-hop:** each stage blocks its immediate upstream when full. Pressure propagates
  backward one link at a time (TCP per-hop, SEDA stage-to-stage). Simple, local, but pressure
  takes time to reach the true source and intermediate buffers still fill.
- **End-to-end:** the original producer is told to slow (or is rate-limited at the edge, 18A)
  based on a signal from deep in the system. Faster relief, needs a signal path. In practice
  systems combine both: hop-by-hop for correctness, end-to-end (admission control / rate limit)
  to stop the flood at the source.

### 1.5 The SEDA model (Staged Event-Driven Architecture)
- SEDA decomposes a service into **stages**, each = an **event queue + a thread pool +
  a controller**. Stages are connected by explicit queues; each stage's controller observes its
  queue and **adjusts its own concurrency (thread count) and admission** in response to load.
- The point relevant to 18: **the queues are explicit and bounded, and they are the natural
  place to apply backpressure and load shedding.** Because every stage has a visible queue with
  a length, the system can (a) see overload as queue growth, (b) shed at a queue when it
  exceeds a threshold, and (c) adapt concurrency per stage rather than globally. SEDA reframes
  "a server" as "a graph of bounded queues with controllers" — which is exactly the mental
  model 18 needs.
- Lineage: the thread-per-request + bounded-queue + thread-pool design Google SRE describes
  (**VERIFIED**) is the same stage primitive; SEDA generalizes it to a pipeline of such stages.
- `[UNVERIFIED]`: Welsh, Culler & Brewer, "SEDA: An Architecture for Well-Conditioned,
  Scalable Internet Services," **SOSP 2001** — could not fetch a primary this session (Harvard
  mirror + USENIX both unreachable). Mechanism described from reuse + general knowledge; the
  paper's exact controller equations / overload graphs are carried forward `[UNVERIFIED]`.

## 2. Foundational sources
- **VERIFIED (recomputation, B1):** bounded-queue added latency = `Q/drain`; SRE's 10×-pool
  (~1.0 s) and 0.5×-pool (~0.05 s) cases reproduced.
- **VERIFIED (fetched primary):** Google SRE *Addressing Cascading Failures* — queue-in-front-
  of-thread-pool model, "queue ≤ 50% of pool, reject early," HTTP 503 when in-flight exceeds a
  threshold, FIFO vs LIFO vs CoDel under overload (`sre_cascading_failures.txt`).
- **Reuse (line-verified):** 13 (Little's Law, M/M/1 `W=S/(1−ρ)`, `ρ→1` wall), 03 (TCP flow
  control = receiver window = credit scheme; congestion vs flow control distinction), 17 (pull
  = built-in backpressure, consumer lag as the signal, the log as a bounded buffer), 10
  (proxy connection/queue limits), 16 (coalescing to reduce upstream load).
- **`[UNVERIFIED]`:** SEDA paper (Welsh SOSP 2001) exact stage-controller design + overload
  graphs; Reactive Streams spec (`request(n)`/demand semantics, JDK `Flow`); Akka/Project
  Reactor/RxJava backpressure strategies; gRPC/HTTP-2 flow-control window defaults; Netty
  `WRITE_BUFFER_WATER_MARK`. Fetch when reachable.

## 3. "Why it's this way" — forcing functions
- **A producer faster than a consumer must be stopped somewhere** ⇒ either an unbounded buffer
  (OOM + unbounded latency, the 13 wall) or backpressure. There is no third option; "just add a
  bigger queue" only delays the crash.
- **`ρ→1` ⇒ latency → ∞** (13) ⇒ the queue must be *bounded*, and the bound directly sets the
  worst-case added latency (`Q/μ`, B1). Sizing the queue *is* choosing a latency budget.
- **Controllable vs uncontrollable producers** ⇒ block the ones you own (lossless), drop the
  ones you don't (the Internet) — hence blocking-vs-dropping is a property of the producer, not
  a preference.
- **Pressure must reach the source** ⇒ hop-by-hop is correct but slow to propagate; pair it with
  end-to-end admission/rate-limiting (18A) at the edge.
- **You can only manage what you can see** ⇒ SEDA makes queues explicit so overload is
  observable (queue length) and actionable (shed/adapt per stage). Hidden buffers (socket
  backlogs, library queues, GC) cause invisible overload.

## 4. Common misconceptions to preempt
- "A bigger queue makes the system more robust." The opposite: a deep queue converts overload
  into unbounded latency + OOM and *hides* the problem; small queues reject early and stay fast
  (B1, SRE — VERIFIED).
- "Backpressure means dropping requests." Backpressure is *propagating slow-down upstream*;
  dropping (shedding) is what you do when you *can't* propagate it. Different mechanisms.
- "TCP already handles backpressure, so I don't need any." TCP flow control protects the
  *socket buffer*, not your *application* thread pool / downstream service; application-level
  backpressure is separate (and TCP congestion control ≠ flow control).
- "Async/event-driven servers can't be overloaded." They just move the queue from threads to an
  event queue; an unbounded event queue OOMs exactly the same. SEDA's point is to *bound and
  observe* those queues.
- "Push is simpler than pull." Push needs an explicit credit scheme to avoid overrunning the
  consumer; pull (17 log) has backpressure built in because the consumer sets the pace.

## 5. Best build-your-own target(s)
- **Bounded-queue pipeline:** producer → bounded queue → slow consumer; toggle block-vs-drop on
  full; sweep queue depth and plot added latency = `Q/μ` (B1) and OOM/drop behavior of an
  unbounded variant.
- **Credit-based stream:** implement `request(n)` demand signaling (Reactive-Streams-lite); show
  a fast producer never overruns a slow consumer; compare to TCP-window behavior from the 03 lab.
- **Mini-SEDA:** two stages each with a bounded queue + thread pool + a controller that sheds
  (503) past a queue threshold and adapts pool size; drive it past saturation and watch overload
  become *visible* as queue growth instead of a silent meltdown.

## 6. Open questions / gaps
- **`[UNVERIFIED]`:** SEDA paper controller equations + overload graphs; Reactive Streams spec;
  framework backpressure (Akka/Reactor/RxJava/Netty/gRPC-HTTP2 flow control) defaults.
- **Boundary discipline:** queueing theory (`ρ`, Little's Law, M/M/1) is owned by **13** — 18B
  *applies* it. The drop side (what/how to shed, criticality, LIFO/CoDel) is **18C**. The
  admission valve / rate limit at the source is **18A**. Pull-based logs + consumer lag are
  **17**. TCP flow control internals are **03**. Capacity sizing / headroom is **20**.
