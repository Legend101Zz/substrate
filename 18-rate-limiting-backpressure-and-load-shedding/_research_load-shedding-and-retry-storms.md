# 18 · Cluster C — Load shedding, retry amplification, and goodput collapse

> Phase-1 brief (NO course prose). ADR-001 cluster file. Math RECOMPUTED in `_recompute.py`
> (blocks C1, C2; B1 reused). Primary: Google SRE *Handling Overload* + *Addressing Cascading
> Failures* (both **VERIFIED** from `meta/fetched_primaries/`). `[UNVERIFIED]` = not fetched.

## Scope
Load shedding = **deliberately dropping work under measured overload to keep the rest healthy.**
Where Cluster A's rate limit is a static, health-blind cap, shedding is dynamic and
health-aware. This cluster covers admission control, priority/tiered shedding (criticality),
brownout/graceful degradation, FIFO-vs-LIFO/CoDel under overload, deadline-aware dropping, and
the killer failure mode: **retry amplification → retry storms → goodput collapse** (congestion
collapse). All primary-grounded in Google SRE.

## 1. Key mechanisms

### 1.1 Admission control: fail early and cheaply
- Google SRE (cascading-failures, **VERIFIED**): "Servers should protect themselves from
  becoming overloaded and crashing. When overloaded at either the frontend or backend layers,
  **fail early and cheaply**." Reject when in-flight requests exceed a threshold (e.g. HTTP
  **503**).
- This is the reactive complement to 18A: the limiter caps the *input rate*; admission control
  rejects when *this server's own health* (queue depth, in-flight count, CPU) says it's past
  capacity. SRE warns the static limiter alone "may not stop a failure already begun" and
  "leaves capacity unused" — so health-aware shedding is required (**VERIFIED**).
- **Measure capacity in resources, not QPS** (SRE *Handling Overload*, **VERIFIED**): "The
  Pitfalls of Queries per Second" — different queries cost vastly different resources, and the
  ratio drifts over time, so QPS is "a poor metric." Google provisions and sheds against
  **CPU consumption** directly (memory pressure shows up as CPU under GC; other resources are
  over-provisioned relative to CPU). Shed against the *real* bottleneck signal.

### 1.2 Per-customer limits + criticality (tiered shedding)
- **Per-customer limits** (SRE, **VERIFIED**): under *global* overload, "the service only
  delivers error responses to misbehaving customers, while other customers remain unaffected."
  Provision per the negotiated quota; the over-quota customer eats the errors. (The fairness
  point from 18A, applied reactively.)
- **Criticality** (SRE, **VERIFIED**) — a first-class tag on every RPC, four values:
  `CRITICAL_PLUS` (most critical, serious user-visible impact if dropped) > `CRITICAL` (default
  for prod jobs, provision for these) > `SHEDDABLE_PLUS` (partial unavailability expected,
  default for batch) > `SHEDDABLE` (frequent partial / occasional full unavailability OK). Rule:
  "a backend will only reject requests of a given criticality if it's already rejecting **all**
  requests of all lower criticalities," and "when a task is itself overloaded it rejects lower
  criticalities sooner." Adaptive throttling keeps **separate stats per criticality**. This is
  **priority/tiered shedding**: shed the cheap/deferrable work first, protect the critical work.

### 1.3 Brownout / graceful degradation
- SRE *Handling Overload* (**VERIFIED**): serve **degraded responses** that are "less accurate
  or contain less data but easier to compute" — e.g. search only a small percentage of the
  candidate set, or rely on a possibly-stale local copy (reuse 16 cache / 15 stale replica).
  "Graceful degradation takes load shedding one step further by reducing the amount of work."
  Under *extreme* overload the service may have "no immediate option but to serve errors."
- Caveat SRE gives: test degraded modes (they run rarely, so they rot), and don't make
  degradation logic so complex it becomes its own failure source.

### 1.4 Queue discipline under overload: FIFO vs LIFO vs CoDel
- SRE (cascading-failures, **VERIFIED**): under overload, changing the queue from **FIFO to
  LIFO**, or using the **CoDel (controlled delay) algorithm [Nichols 2012]**, "can reduce load
  by removing requests that are unlikely to be worth processing." The intuition: under
  overload, the *oldest* queued request (FIFO head) is the most likely to have already blown its
  client's deadline — serving it is wasted work — so **LIFO serves the freshest** (most likely
  still wanted) request, and CoDel drops requests that have sat too long. **Deadline-aware
  dropping:** if a request's deadline has passed before a thread picks it up, drop it unserved —
  the work would be wasted (SRE: a server that responds after the client's deadline does work
  that's "then wasted, and clients may retry, leading to even more overload").

### 1.5 Retry amplification → retry storms (the failure mode)
- SRE (cascading-failures, **VERIFIED**) worked example: backend cap 10,000 QPS; frontend offers
  10,100 QPS; the 100 rejected QPS are retried, becoming 200, then 300 QPS of *added* load —
  "the volume of retries grows... fewer and fewer requests succeed on first attempt... less
  useful work is performed." Naive retries **destabilize** the system and can keep it down even
  after offered load drops back below capacity, because (a) rejections still cost resources and
  (b) the backend may not be stable.
- VERIFIED (C1): if a fraction `r` of requests are retried (and retries can be retried), the
  request multiplier is the geometric series `1/(1−r)`: `r=0.5 → 2×`, `r=0.9 → 10×`,
  `r=0.99 → 100×`. **That is the retry storm.**
- VERIFIED (C2, goodput collapse): below saturation, goodput = offered. At saturation with no
  retries / cheap rejection, goodput **plateaus at capacity**. But with naive retries *and* a
  non-trivial cost to reject, goodput **collapses below capacity** and gets *worse* as overload
  grows — the classic **congestion-collapse** curve. (In the model: 3× retry + 0.5 reject cost
  drove goodput from 1000 to ~0.)

### 1.6 Bounding retries (the fixes — all SRE, **VERIFIED**)
- **Per-request retry budget:** cap attempts (Google uses **3**); after 3 failures, let it
  bubble up. (C1: a 3-attempt cap bounds the worst-case multiplier to ~3× even if everything
  fails, vs ∞ uncapped.)
- **Per-client retry budget:** only retry while retries are **< 10%** of requests; if a large
  fraction of tasks are overloaded there's little point retrying. (C1: a 10% budget caps
  steady-state amplification at `1/(1−0.1) ≈ 1.11×`.)
- **Don't retry at every level:** if every layer retries 3×, the multiplier *compounds* across
  layers (3×3×3 = 27×). Retry at **one** level, or pass a "don't retry" signal down.
- **Backoff + jitter** (reuse 16/17): capped exponential backoff with jitter spreads retries so
  they don't synchronize into a thundering herd. SRE also propagates an "overloaded; don't
  retry" response when histograms show many retries already in flight (server-side circuit).
- **Retry-After** (RFC 6585, **VERIFIED**): the server *tells* the client how long to wait,
  turning blind client retries into coordinated backoff.

## 2. Foundational sources
- **VERIFIED (recomputation, C1/C2, B1 reuse):** retry multiplier `1/(1−r)` (2×/10×/100×) and
  3-attempt / 10%-budget caps; goodput plateau-vs-collapse curve; bounded-queue latency.
- **VERIFIED (fetched primary):** Google SRE *Handling Overload* — QPS pitfall, CPU-as-signal,
  per-customer limits, criticality (4 tiers + the "reject lower criticalities first" rule),
  adaptive throttling per-criticality, graceful degradation, retry budgets (3 / 10% / counter),
  "overloaded; don't retry" (`sre_handling_overload.txt`); *Addressing Cascading Failures* —
  fail-early-and-cheaply 503, FIFO/LIFO/CoDel [Nichols 2012], deadline-wasted-work, the
  10,000-QPS retry-storm worked example, GC death spiral (`sre_cascading_failures.txt`).
- **VERIFIED (fetched primary):** RFC 6585 §4 — 429 + `Retry-After` (`rfc6585.txt`).
- **Reuse (line-verified):** 17 (retry budgets, capped backoff+jitter, DLQ for poison, the queue
  as buffer), 16 (coalescing + jitter, stale-serve degradation), 13 (queueing wall, tail
  latency, `ρ→1`), 15 (stale replica = degraded read), 11 (no free coordination).
- **`[UNVERIFIED]`:** Nichols & Jacobson, "Controlling Queue Delay" (CoDel), CACM/ACM Queue 2012
  — named by SRE but not fetched; AWS Builders' Library "Timeouts, retries and backoff with
  jitter" (Brooker) — blocked this session; Netflix Hystrix/concurrency-limits (AIMD adaptive
  limiter) docs; Envoy outlier detection / circuit-breaker config.

## 3. "Why it's this way" — forcing functions
- **Overload is inevitable past provisioned capacity** (SRE) ⇒ you must shed *something*; the
  only choice is whether you choose what to drop (criticality/deadline) or the system chooses
  for you (crash). Fail early and cheaply.
- **Not all requests are equal** ⇒ criticality + per-customer limits let you protect the
  valuable/critical work and shed batch/deferrable work first.
- **Under overload, old queued work is often already worthless** ⇒ LIFO/CoDel/deadline-dropping
  beat FIFO because they stop spending capacity on requests whose clients have given up.
- **Retries multiply load exactly when you can least afford it** ⇒ `1/(1−r)` amplification (C1)
  turns a small overload into a storm and causes goodput collapse (C2); hence hard retry budgets
  (3 / 10% / one-level-only) + backoff/jitter + `Retry-After`.
- **QPS hides cost variance** ⇒ shed against the real resource bottleneck (CPU), not request
  count.

## 4. Common misconceptions to preempt
- "Shedding load loses business; better to try to serve everything." Trying to serve everything
  under overload serves *nothing* (goodput collapse, C2); shedding keeps goodput at capacity.
- "Retries make the system more reliable." Naive retries make it *less* reliable under overload
  — they amplify load `1/(1−r)` (C1) and cause retry storms / congestion collapse (C2, SRE
  worked example — VERIFIED). Retries help only with *isolated* failures, bounded by budgets.
- "Retry at every layer for robustness." Multipliers *compound* across layers (3×3×3=27×); retry
  at one layer only.
- "FIFO is the fair queue discipline." Under overload FIFO serves the *stalest* (most likely
  abandoned) requests first — LIFO/CoDel/deadline-aware dropping is better (SRE — VERIFIED).
- "Measure load in QPS." QPS is a poor capacity metric; cost per query varies and drifts — shed
  against CPU/resources (SRE — VERIFIED).
- "A circuit breaker / 503 is giving up." It's *protecting goodput*; a fast cheap 503 frees
  capacity for the requests that can succeed, and (with `Retry-After`) coordinates client backoff.

## 5. Best build-your-own target(s)
- **Goodput-vs-offered-load harness:** drive a fixed-capacity server past saturation with (a)
  no retries, (b) naive 3× retries, (c) retries + 10% budget + backoff; plot goodput and
  reproduce the plateau vs collapse (C2) and the `1/(1−r)` amplification (C1).
- **Criticality shedder:** tag traffic into 4 tiers; under rising load, shed lowest-first and
  verify CRITICAL_PLUS survives while SHEDDABLE is dropped; add per-customer quotas and show one
  abusive tenant eats the errors.
- **Queue-discipline bench:** same overload through FIFO vs LIFO vs CoDel + deadline-drop;
  measure *useful* completions (requests answered before their deadline) per discipline.
- (Pairs with 17 retry+DLQ lab and 13 queueing lab.)

## 6. Open questions / gaps
- **`[UNVERIFIED]`:** CoDel paper (Nichols/Jacobson 2012) exact target/interval; AWS
  backoff-with-jitter article; Hystrix / Netflix concurrency-limits (AIMD) algorithm; Envoy
  circuit-breaker/outlier-detection knobs. Fetch when reachable.
- **Boundary discipline:** static admission valve / algorithms = **18A**; bounded queues +
  credit/SEDA = **18B**; circuit breakers / bulkheads / hedged requests / adaptive concurrency =
  **18D**; queueing theory = **13**; tail latency = **13/20**; capacity headroom = **20**;
  retry-on-the-message-bus + DLQ = **17**; SLO-driven shedding thresholds + observing shed rate =
  **19**.
