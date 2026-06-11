# 18 · Cluster D — Timeouts, circuit breakers, bulkheads, hedging, adaptive concurrency

> Phase-1 brief (NO course prose). ADR-001 cluster file. Math reuses `_recompute.py` C1/C2
> (retry/goodput) and D1 (adaptive throttling). Primary: Google SRE (**VERIFIED**).
> `[UNVERIFIED]` = not fetched this session.

## Scope
The client-side and isolation patterns that keep one slow/overloaded dependency from taking down
its callers: **timeouts, retries (bounded), circuit breakers, bulkheads, hedged requests, and
adaptive concurrency limiting**. These are the resilience primitives that *use* A/B/C correctly
and hand off to capacity planning (20). The unifying idea: **bound the blast radius of a slow
dependency in time (timeouts), in attempts (retry budgets), in scope (bulkheads), and in
concurrency (adaptive limits) — and stop calling a dead dependency (circuit breaker).**

## 1. Key mechanisms

### 1.1 Timeouts (bound the wait)
- Every remote call MUST have a deadline; an unbounded wait turns a slow dependency into
  exhausted threads/connections upstream (SRE thread-starvation, **VERIFIED**: "as a server
  becomes overloaded its responses arrive later, exceeding deadlines; the work is then wasted
  and clients may retry → more overload").
- **Deadline propagation:** pass the *remaining* budget down the call chain so a deep call
  doesn't spend time on work whose top-level deadline has already expired (deadline-aware
  dropping, 18C). A timeout without propagation lets each hop spend the full budget → totals
  blow up.
- Timeout sizing: too short = false failures + retries (amplification, 18C); too long = thread
  starvation. Tie to the latency distribution (p99 + margin), not a round number — reuse 13 tail.

### 1.2 Retries (bounded — the 18C fixes, restated as a client pattern)
- Retries belong *only* on idempotent operations (reuse 17 idempotency) and *only* with: a
  per-request attempt cap (3), a per-client budget (10%), single-layer placement, capped
  exponential backoff **+ jitter** (reuse 16/17), and respect for `Retry-After` (RFC 6585,
  **VERIFIED**). Math: `1/(1−r)` amplification, caps bound it (C1). Without these, retries cause
  the storm/collapse of 18C (C2).

### 1.3 Circuit breakers (stop calling the dead)
- A circuit breaker watches the error/latency rate to a dependency. **Closed** = calls pass;
  on sustained failure it **opens** = calls fail fast locally (no network, no thread held);
  after a cooldown it goes **half-open** = lets a trial trickle through; success → closed,
  failure → open again.
- Why: when a dependency is down/overloaded, *continuing to call it* (a) wastes the caller's
  threads/timeouts and (b) adds load that keeps the dependency down (18C). Failing fast frees
  the caller and lets the dependency recover. This is the client-side dual of the server's
  "overloaded; don't retry" signal (SRE, **VERIFIED**).
- Tradeoff: thresholds too sensitive ⇒ flapping; too lax ⇒ slow to trip. Half-open trial count
  bounds the recovery probe load.

### 1.4 Bulkheads (isolate the blast radius)
- Named after ship compartments: give each dependency (or tenant, or request class) its **own
  bounded resource pool** (thread pool, connection pool, semaphore) so one slow dependency can
  only exhaust *its* pool, not the whole server. Without bulkheads, one slow downstream consumes
  *all* shared threads and the entire service stalls (SRE thread-starvation cascade,
  **VERIFIED**).
- Relation to 18B: a bulkhead is a bounded queue + concurrency limit *scoped per dependency*;
  to 18C criticality: bulkheads can be sized per tier so critical traffic keeps its pool.

### 1.5 Hedged / tied requests (cut the tail — the 13/20 handoff)
- **Hedged request:** send the request, and if no response by (say) p95, send a *second* copy
  to another replica and take whichever returns first. Cuts tail latency at the cost of a small
  extra load (~5% if hedging past p95).
- **Tied request:** send to two replicas but tell each about the other so the loser cancels —
  less duplicated work. (Both are from the tail-at-scale playbook owned by **13/20**; named here
  because they interact with concurrency limits — hedging *adds* load, so it must respect
  budgets/breakers.)
- Caveat: hedging an *overloaded* system makes it worse (more load when you can least afford it,
  18C); gate hedging behind a small budget and disable under shedding.

### 1.6 Adaptive concurrency limiting (the self-tuning valve)
- Instead of a fixed concurrency cap, *infer* the right in-flight limit from observed latency,
  the same way TCP infers the right window. **AIMD** (additive-increase/multiplicative-decrease,
  reuse 03 congestion control): grow the limit while latency is healthy, cut it hard when
  latency/queueing rises. Gradient/Little's-Law-based limiters (e.g. Netflix concurrency-limits)
  estimate the concurrency at which latency starts climbing (the 13 knee) and hold just below it.
- **Google adaptive throttling** (SRE, **VERIFIED**, D1) is the client-side instance: each
  client tracks `requests` and `accepts` over 2 min and rejects locally with probability
  `max(0, (requests − K·accepts)/(requests + 1))`, `K=2` default.
  - VERIFIED (D1): healthy (`requests=accepts`) ⇒ p=0; backend accepting half (`200 vs 100`,
    K=2) ⇒ p=0 (the 2× multiplier *tolerates* 2× rejection to propagate state fast); accepting a
    third (`300 vs 100`) ⇒ p≈0.332; lowering `K` to 1.1 throttles much earlier (use when
    rejecting still costs ~as much as serving). This makes the client self-regulate so the
    backend "ends up rejecting one request for each request it actually processes" even under
    large overload (SRE — VERIFIED).

### 1.7 Interaction with capacity planning (handoff to 20)
- Every knob here assumes a *known* capacity: timeouts vs p99, concurrency limits vs the knee,
  retry budgets vs headroom. Capacity planning (20) supplies those numbers; SRE
  (cascading-failures, **VERIFIED**): "capacity planning reduces the probability of a cascading
  failure but is not sufficient" — you still need A/B/C/D because lost infrastructure can erase
  any headroom. 18 protects the capacity 20 plans for.

## 2. Foundational sources
- **VERIFIED (recomputation):** C1 retry multiplier + caps; C2 goodput; **D1 adaptive throttling
  reject probability `max(0,(req−K·acc)/(req+1))`** with K=2 vs K=1.1 behavior.
- **VERIFIED (fetched primary):** Google SRE *Handling Overload* — adaptive throttling formula +
  K multiplier rationale, "reject one per processed under overload," sporadic-client caveat;
  *Addressing Cascading Failures* — thread/FD/memory starvation cascade, GC death spiral,
  capacity-planning-is-necessary-not-sufficient (`sre_*.txt`).
- **Reuse (line-verified):** 03 (AIMD congestion control, window inference), 13 (tail latency,
  the knee, hedged/tied requests origin), 17 (idempotency for safe retries, backoff+jitter,
  budgets), 16 (jitter, coalescing), 11 (no free coordination).
- **`[UNVERIFIED]`:** Netflix Hystrix (circuit breaker + bulkhead) docs; Netflix
  concurrency-limits (gradient/Little's-Law adaptive limiter); resilience4j; Envoy circuit
  breaking + outlier detection knobs; Nygard *Release It!* (circuit breaker / bulkhead origin
  pattern names). **Dean & Barroso "The Tail at Scale" CACM 2013 — FETCHED + VERIFIED this
  session** (`meta/fetched_primaries/tail-at-scale-cacm2013.{pdf,txt}`): backup requests (hedged)
  + backup requests w/ cancellation (tied) confirmed verbatim; Backup Requests Effects table
  (no-backups 99.9%ile 994 ms → backup-after-10 ms 50 ms). Fetch remaining when reachable.

## 3. "Why it's this way" — forcing functions
- **A slow dependency is worse than a dead one** ⇒ timeouts bound the wait, circuit breakers
  stop calling it, bulkheads contain it — otherwise it silently consumes all threads/conns
  (SRE cascade — VERIFIED).
- **Shared resource pools couple unrelated failures** ⇒ bulkheads isolate so one bad dependency
  can't sink the ship.
- **Fixed limits are wrong as conditions change** ⇒ adaptive concurrency/throttling infers the
  limit from latency (the 13 knee, the 03 window) instead of a guessed constant.
- **Tail latency dominates fan-out** (13) ⇒ hedging cuts it — but hedging adds load, so it must
  respect budgets and stand down under shedding (18C).
- **Resilience patterns need capacity numbers** ⇒ they're parameterized by 20's capacity model;
  18 defends that capacity, 20 sizes it.

## 4. Common misconceptions to preempt
- "Set a generous timeout to be safe." Long timeouts cause thread starvation and cascading
  stalls; size to p99 + margin and propagate deadlines (SRE — VERIFIED).
- "Circuit breakers are only for outages." They also protect against *overload* and *latency*
  spikes by failing fast and letting the dependency recover (the don't-retry-the-overloaded
  rule).
- "Bulkheads waste resources." They trade a little utilization for blast-radius isolation —
  cheap insurance against total stalls.
- "Hedging always reduces latency." It adds load; on an *overloaded* system it makes things
  worse — gate it behind a budget and disable under shedding.
- "A fixed concurrency limit is fine." The right limit changes with downstream health; adaptive
  (AIMD / gradient / adaptive-throttling D1) tracks it; a fixed cap is either too low (wasted
  capacity) or too high (overload).
- "Capacity planning alone prevents cascading failures." SRE: necessary but not sufficient —
  you still need A/B/C/D (VERIFIED).

## 5. Best build-your-own target(s)
- **Circuit breaker + bulkhead:** wrap a flaky dependency; trip open on error-rate threshold,
  half-open probe, and give it an isolated pool; inject a slow dependency and show the rest of
  the service stays responsive (vs a shared-pool baseline that stalls).
- **Adaptive throttling client:** implement the D1 formula over a 2-min window; drive a backend
  to reject a fraction and verify the client converges to "one reject per processed"; sweep K
  (2 vs 1.1) and show aggressiveness.
- **AIMD concurrency limiter:** infer the in-flight limit from latency (additive-increase /
  multiplicative-decrease, reuse 03); compare goodput vs a fixed cap as downstream capacity
  changes.
- **Hedged-request tail cut:** send a second request past p95 to a replica; measure p99
  improvement and the extra load; show it backfires under simulated overload.

## 6. Open questions / gaps
- **`[UNVERIFIED]`:** Hystrix/resilience4j/Envoy circuit-breaker + bulkhead defaults; Netflix
  concurrency-limits algorithm; Nygard *Release It!* pattern definitions; Dean & Barroso "Tail
  at Scale" hedged/tied request numbers (carried by 13/20). Fetch when reachable.
- **Boundary discipline:** tail latency + hedging *theory/numbers* are owned by **13/20** (18D
  names the interaction); congestion-control AIMD internals = **03**; idempotency for retries =
  **17**; capacity sizing/headroom = **20**; observing breaker state / shed rate / retry ratio as
  SLO signals = **19**; static rate limit = **18A**; bounded queues/SEDA = **18B**; shedding +
  criticality = **18C**.
