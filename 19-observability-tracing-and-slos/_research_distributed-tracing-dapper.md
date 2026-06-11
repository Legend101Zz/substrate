# 19 · Cluster B — Distributed tracing (the Dapper model)

> Phase-1 brief (NO course prose). Per ADR-001. Math RECOMPUTED in `_recompute.py`.
> Dapper claims **VERIFIED** from `meta/fetched_primaries/dapper-2010.txt` (+ receipt
> `_VERIFIED_2026-06-10_observability.md`). `[UNVERIFIED]` carried forward.

## Scope
A single user request fans out across many services (13 fan-out, 17 choreographed flows).
A metric tells you *that* p99 rose; a **trace** tells you *where* the time went, by
reconstructing the causal tree of one request across process boundaries. This cluster is
the Dapper model: spans, trace context propagation, sampling, overhead, and how a trace
makes a 17 async flow and a 13 fan-out tail legible.

## 1. Key mechanisms

### 1.1 The trace tree & spans (Dapper §2.1 — VERIFIED)
- "We tend to think of a Dapper trace as a tree of nested RPCs." Tree nodes = **spans**
  (basic units of work); edges = a **causal relationship between a span and its parent span**.
- A span is "a simple log of timestamped records" encoding start/end time, RPC timing, and
  zero-or-more annotations. Each span carries a human-readable **span name**, a **span id**,
  and a **parent id**. Spans with no parent id are **root spans**. All spans in one trace
  share a common **trace id**. "All of these ids are probabilistically unique 64-bit
  integers." Each RPC ≈ one span; each infra tier adds a level of depth.
- **Two-host spans** are the most common: "every RPC span contains annotations from both the
  client and server processes." This is what lets a trace show client-observed vs
  server-observed timing for the *same* call (network + queueing delay falls out as the gap).

### 1.2 Trace context propagation (Dapper §2.2 — VERIFIED)
- Near-zero app intervention by instrumenting a few common libraries:
  - A **trace context** (trace id + span ids, small & copyable) is stored in **thread-local
    storage** while a thread handles a traced path.
  - Across **async** work, the common control-flow library copies the creator's trace context
    into callbacks so ids "follow asynchronous control paths transparently" — this is exactly
    how a **17 choreographed/async flow** stays linked into one trace.
  - The RPC framework **transmits span + trace ids client→server** for traced RPCs ("an
    essential instrumentation point"). Modern equivalent: W3C `traceparent` header
    [UNVERIFIED — w3.org not fetched].
- Language-independent (C++ & Java in one trace).

### 1.3 Causality & clock skew (Dapper §2.1 — VERIFIED; reuse 11)
- Client and server timestamps come from different machines → **clock skew**. Dapper does NOT
  assume synchronized clocks; it uses the **happens-before invariant**: "an RPC client always
  sends a request before a server receives it, and vice versa for the server response,"
  giving a lower/upper bound on server-side span timestamps. This is **11's happens-before /
  no-global-clock** applied to spans — the same reason vector logic, not wall clocks, orders
  distributed events.

### 1.4 Sampling (Dapper §2.4/§4.4 — VERIFIED)
- "sampling [is] necessary for low overhead, especially in highly optimized Web services."
- "a sample of just one out of thousands of requests provides sufficient information for many
  common uses." First production version: **uniform 1/1024** ("one sampled trace for every
  1024 candidates").
- **Adaptive sampling**: parameterize by a *desired rate of sampled traces per unit time*,
  not a fixed probability — low-traffic services raise their rate, high-traffic lower it, so
  overhead stays bounded. RECOMPUTED (A6/A7): uniform `p=1/1024` → sampled/s = QPS/1024
  (10/1000/100k QPS → 0.0098 / 0.977 / 97.7 per s); adaptive `p = min(1, R/QPS)` for target
  `R=10`/s holds sampled/s ≈ 10 across 100→100k QPS.
- **Head sampling** (decide at trace start, propagate the bit) vs **tail sampling** (buffer
  the whole trace, keep it if it's slow/errored). Head = cheap, simple, but may miss rare
  slow traces; tail = keeps the interesting tail but needs buffering. Dapper's described
  scheme is head-style + a **second collection-time sampling** pass (hash trace id to z∈[0,1],
  keep if z < threshold) to cap repository write throughput (§4.6). [tail-sampling as a named
  modern pattern is post-Dapper; UNVERIFIED here].

### 1.5 Overhead & collection (Dapper §4 — VERIFIED)
- Root span create/destroy **204 ns**, non-root **176 ns** (the delta = allocating a unique
  root trace id). Unsampled annotation = thread-local lookup **~9 ns**; sampled string
  annotation **40 ns** (2.2 GHz x86). Span ≈ **426 bytes** avg. Trace collection < **0.01%**
  of production network traffic; daemon < **0.3%** of one core.
- Sampling-vs-overhead table (Table 2): 1/1 → 16.3% latency / −1.48% throughput; 1/16 →
  2.12% / −0.08%; 1/1024 → −0.20% / −0.06% (penalties below 1/16 are within experimental
  error 2.5%/0.15%). → low sampling is what makes always-on tracing affordable.
- Collection = **out-of-band, asynchronous**, 3-stage: local log → daemon pull → regional
  Bigtable cell (one trace = one Bigtable row, each span a column; sparse). Median collection
  latency **< 15 s**. Tracing must never be on the request's critical path.

## 2. How tracing reconstructs higher-level structure
- **A 13 fan-out tail**: the trace tree shows the front-end span with N child RPC spans; the
  slowest child is the straggler driving the tail (13/Tail-at-Scale 1−0.99^100 ≈ 63%). The
  trace localizes *which* leaf, not just *that* p99 rose.
- **A 17 choreographed flow**: async context propagation links producer→broker→consumer spans
  into one tree, so an event-driven path (otherwise invisible across queue hops) becomes a
  legible causal chain. Consumer lag / DLQ depth (17) are the *metric* signals; the trace is
  the *causal* explanation.

## 3. Why it's this way (forcing functions)
- **Transparency forces library-level instrumentation.** App-developer-driven annotation is
  "extremely fragile" (Dapper §1) → instrument the shared RPC/threading/control-flow libs.
- **Scale forces sampling.** Always-on + ubiquitous + low-overhead are contradictory without
  sampling; 1/1024 reconciles them (and rare patterns "surface thousands of times" anyway).
- **No global clock forces causal ids, not timestamps.** (11.) Ordering comes from
  parent/child ids + the send-before-receive invariant, not synchronized wall clocks.

## 4. Common misconceptions to preempt
- "Tracing needs synchronized clocks." No — it uses causal ids + happens-before bounds (11).
- "Sample everything for accuracy." Overhead + storage make that infeasible; 1/1024 suffices
  for common analyses (Dapper). Errors/slow traces can be tail-sampled to keep the rare ones.
- "A span = a service." A span = a unit of work (usually one RPC, client+server); a service
  can emit many spans per request.
- "Tracing replaces metrics/logs." Dapper §1: it "focuses a performance investigation so
  that other tools can be applied locally" — complementary, not a replacement (three pillars).

## 5. Best build-your-own target(s)
- A minimal tracer: `trace_id`/`span_id`/`parent_id`, a context object propagated through a
  simulated 2-tier RPC + one async hop (17), emitting a span tree you can render as a waterfall.
  Demonstrates context propagation + clock-skew bounding without synchronized clocks.

## 6. Open questions / where sources disagree
- W3C Trace Context (`traceparent`/`tracestate`), OpenTelemetry span model, B3/Zipkin/Jaeger
  propagation specifics — all [UNVERIFIED] (w3.org / opentelemetry.io / zipkin.io not fetched).
- Tail-sampling as a formal pattern (and its buffering cost) is post-Dapper; [UNVERIFIED].
- Magpie [3] / X-Trace [12] / Pinpoint [9] (Dapper's cited relatives) not fetched; mentioned
  by Dapper but their own claims [UNVERIFIED].
