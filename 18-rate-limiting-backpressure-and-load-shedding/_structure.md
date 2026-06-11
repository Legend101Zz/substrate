# 18 — Rate Limiting, Backpressure, and Load Shedding (SEDA) · _structure.md

**Identity:** deliberate overload control — the discipline where 13's queueing wall and 17's
consumer-lag handoff become explicit engineering. The one truth: demand can always exceed capacity;
you WILL serve a subset of requests — the only question is whether you choose that subset
deliberately, or the system "chooses" it for you by melting down.

**Bespoke shape — "four valves along the path: input → buffer → drop → client."** NOT a pattern
catalogue. 13 proved the wall (`W=S/(1−ρ)→∞`); 17 named the symptom (consumers fall behind, the
queue grows). 18 is the four-layer answer, taught as the request's journey through your system:
**A — bound the INPUT (rate limiting, proactive + health-blind) → B — bound the BUFFER
(backpressure + SEDA) → C — choose what to DROP (load shedding, reactive + health-aware) → D —
bound the CLIENT (timeouts/breakers/bulkheads/hedging/adaptive concurrency).** You need all four
because each fails alone. Three primitives do double duty: the bounded queue, the budget/limit, and
the health/latency signal. Math heavily verified by recomputation; three production primaries
(RFC 6585 + two Google SRE chapters) anchor it.

## Dependency position
- **Depends on:** 13 (Little's Law, M/M/1 wall, the knee — 18 APPLIES it), 03 (TCP flow control =
  credit; AIMD; flow-vs-congestion), 17 (queue-as-buffer, consumer lag = backpressure signal, retry
  budgets, backoff+jitter, DLQ, idempotency), 16 (jitter, coalescing, stale-serve degradation), 15
  (stale replica = degraded read), 14 (hot shard/celebrity, sticky-routing cost), 11 (no free global
  coordination), 10 (reverse proxy = enforcement point).
- **Feeds into:** 19 (shed rate/retry ratio/breaker state/queue depth = the SIGNALS the controllers
  act on — 18 actuates, 19 senses), 20 (18 DEFENDS the capacity 20 PLANS; cascading-failure
  recovery), 21 (the rate-limiter case study is direct 18), 22/27/32 (agent budgets/tool-call
  limits/loop backpressure).
- **Appendix links DOWN:** N-math (queueing), B-linux (thread pools, /proc). 18 owns the control
  discipline.

## Chapter specs (3–5 lines each)
### A — bound the input (rate limiting)
1. **The rate-limiting algorithm family** — token bucket (burst `B` + rate `r`, two knobs), leaky
   bucket (smoothed output), fixed window (O(1), 2× boundary leak), sliding log (exact, O(limit)),
   sliding counter (O(1), bounded error `prev·frac`) — one family across the burst-tolerance ×
   accuracy/memory plane (all VERIFIED).
2. **Distributed limiting & enforcement** — a shared counter is a synchronous hot key/SPOF (14/16/
   11); cell-based local limiting over-admits `(cells−1)·batch` (chatter vs slop dial, VERIFIED).
   Reject with **429 + Retry-After** (RFC 6585, VERIFIED). Enforce where it's cheapest to say no —
   edge/proxy/LB (10/16). But the limiter is HEALTH-BLIND (SRE, VERIFIED) — necessary, not sufficient.

### B — bound the buffer (backpressure + SEDA)
3. **Bounded queues & block-vs-drop** — an unbounded queue is NOT safety — it converts overload into
   unbounded latency + OOM (the 13 wall). A bounded queue adds ≤ `Q/μ` latency (VERIFIED); SRE's
   rule: queue ≤ 50% of the pool, reject early. Full → block (propagate slow-down: TCP-window credit
   from 03, `request(n)` demand, pull-based logs from 17) or drop (→ C), set by producer
   controllability.
4. **SEDA: making overload visible** — reframe a service as a graph of explicit bounded queues with
   per-stage controllers, so overload is VISIBLE (queue length) and ACTIONABLE (shed/adapt per
   stage). End-to-end vs hop-by-hop backpressure (hop = correct but slow to propagate; pair with edge
   admission).

### C — choose what to drop (load shedding)
5. **Admission control & criticality** — fail early and cheaply (503). Measure capacity in RESOURCES
   (CPU), not QPS (SRE, VERIFIED). Shed by criticality (4 tiers; reject a tier only when all lower
   tiers are fully rejected) + per-customer limits (only misbehaving tenants eat errors). Degrade
   before you drop (partial corpus, stale cache — 16/15). Under overload prefer LIFO/CoDel/deadline-
   drop over FIFO (the oldest queued request is most likely already abandoned).
6. **Retry storms & goodput collapse** — the killer: retries amplify load `1/(1−r)` (.9→10×,
   .99→100×, VERIFIED) into a storm; goodput PLATEAUS at capacity without retries but COLLAPSES below
   it with naive retries + reject cost (congestion collapse, VERIFIED). Fixes: per-request budget
   (3), per-client budget (10%), single-layer, backoff+jitter (16/17), Retry-After.

### D — bound the client (resilience patterns)
7. **Timeouts, breakers, bulkheads** — timeouts (+ deadline propagation) bound the wait so a slow
   dependency can't starve threads (size to p99); circuit breakers (closed→open→half-open) stop
   calling the dead and let it recover; bulkheads isolate the blast radius (per-dependency pools). A
   slow node is worse than a dead one.
8. **Hedging & adaptive concurrency** — hedged/tied requests cut the tail (13/20) but ADD load, so
   they stand down under shedding. Adaptive concurrency (AIMD, 03; Google adaptive throttling
   `p=max(0,(req−K·acc)/(req+1))`, K=2, VERIFIED) infers the right limit from latency instead of
   guessing a constant — fixed limits go stale. Everything here is parameterized by 20's capacity
   numbers: 18 DEFENDS the capacity 20 plans.

## Paired build labs (/build — overload harnesses)
Four-algorithm limiter bench (token/leaky/fixed/sliding-log/sliding-counter; bursty trace; show 2×
boundary leak + `prev·frac` error) + distributed limiter (cell-based; sweep `sync_batch`, measure
over-admit; compare shared-counter latency) → bounded-queue pipeline (block-vs-drop on full; sweep
depth, plot `Q/μ`; OOM the unbounded variant) + credit-based stream (`request(n)`; compare TCP
window from 03) + mini-SEDA (2 stages, bounded queue + pool + shed/adapt controller; overload =
visible queue growth) → goodput-vs-offered-load harness (no-retry vs naive-3× vs budgeted+backoff;
reproduce plateau vs collapse + amplification) + criticality shedder (4 tiers + per-customer quotas)
+ queue-discipline bench (FIFO/LIFO/CoDel + deadline-drop; count USEFUL completions) → circuit
breaker + bulkhead (trip/half-open + isolated pool) + adaptive throttling client (D1 formula;
converge to "one reject per processed"; sweep K) + AIMD concurrency limiter (infer from latency vs
fixed cap) + hedged-request tail cut (2nd request past p95; measure p99 + extra load; backfire under
overload).

## Diagrams needed
- The four-valves-along-the-path motif (input→buffer→drop→client).
- Rate-limit family on the burst-tolerance × accuracy/memory plane; fixed-window 2× boundary leak.
- Cell-based distributed limiter over-admit `(cells−1)·batch`; 429 + Retry-After flow.
- Bounded vs unbounded queue (latency `Q/μ` vs OOM); SEDA stage (queue + pool + controller).
- Criticality tiers (shed lowest-first); FIFO vs LIFO/CoDel under overload.
- Goodput-vs-offered-load: plateau (no retries) vs collapse (naive retries); `1/(1−r)`.
- Circuit-breaker state machine; bulkhead pool isolation.
- Adaptive throttling convergence; hedged-request tail cut (and backfire under overload).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED BY RECOMPUTATION (9/9):** token/leaky bucket sizing; fixed-window 2× + sliding-log
  exactness vs sliding-counter `prev·frac` error & O(1)-vs-O(limit); distributed over-admit
  `(cells−1)·batch`; bounded-queue `Q/μ`; retry `1/(1−r)` + 3/10% caps; goodput plateau-vs-collapse;
  adaptive-throttle reject `max(0,(req−K·acc)/(req+1))`.
- **VERIFIED PRIMARIES this session (`meta/fetched_primaries/`):** RFC 6585 §4 (429/Retry-After);
  Google SRE *Handling Overload* (QPS-vs-CPU, per-customer limits, adaptive throttling, criticality,
  retry budgets); Google SRE *Addressing Cascading Failures* (queue ≤ 50% pool, fail-early 503,
  FIFO→LIFO/CoDel, health-blind limiting, 10K-QPS retry storm, "capacity planning necessary not
  sufficient").
- **`[UNVERIFIED]` — fetch when reachable (none load-bearing):** Envoy/Nginx/Cloudflare/Stripe/AWS
  limiter algos + GCRA + Redis cell-based + Lyft RLS (A); **SEDA** SOSP 2001 controller equations +
  Reactive Streams + framework backpressure (B — NOTE: SEDA later unblocked/VERIFIED in 19/20,
  reconcile); **CoDel** ACM Queue 2012 (queue.acm.org STILL 403 — retry) + AWS backoff-jitter (C);
  **Hystrix**/concurrency-limits/resilience4j/Envoy + Nygard *Release It!* + Tail-at-Scale (D — later
  VERIFIED in 20). Teach mechanisms now; do NOT harden vendor specifics until fetched.
- **Disagreements to resolve:** default rate-limit algo to teach first (likely token bucket for burst
  + sliding-counter for distributed); lead shedding with criticality (Google) or adaptive concurrency
  (Netflix); breaker/bulkhead depth here vs an appendix.
- **Boundary discipline:** queueing theory → 13 (+ appendix N); tail/hedged numbers → 13/20; TCP
  flow/congestion → 03; idempotency/bus-retries/DLQ → 17; edge/CDN coalescing → 16/10; stale replica
  → 15; hot key/shard → 14; no-free-coordination → 11; capacity sizing/cascade recovery → 20;
  shed-rate/retry-ratio/breaker SLO signals → 19; agent budgets/tool-call limits → 22/27/32.
