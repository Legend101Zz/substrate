# 18 — rate-limiting-backpressure-and-load-shedding (SEDA) — RECONCILED research (`_research.md`)

> **Phase 1 deliverable (NO course prose).** Synthesis of four factchecked clusters into the
> standard six sections (ADR-001: each cluster keeps its deep `_research_<cluster>.md`; this file
> reconciles overlaps, states the cross-cluster thesis, consolidates sources + gaps). Every
> `[UNVERIFIED]` / residual gap from the clusters is preserved here in intent.
>
> **Cluster files (read for full depth):**
> - A — `_research_rate-limiting-algorithms.md` (token/leaky bucket; fixed/sliding window log &
>   counter; distributed limiting; fairness/burst; where to enforce)
> - B — `_research_backpressure-and-seda.md` (bounded queues; block-vs-drop; credit/flow control;
>   end-to-end vs hop-by-hop; the SEDA stage/queue/controller model)
> - C — `_research_load-shedding-and-retry-storms.md` (admission control; criticality/tiered
>   shedding; brownout/degradation; FIFO/LIFO/CoDel; deadline-aware dropping; retry
>   amplification → storms → goodput collapse)
> - D — `_research_timeouts-breakers-bulkheads-hedging.md` (timeouts + deadline propagation;
>   bounded retries; circuit breakers; bulkheads; hedged/tied requests; adaptive concurrency)
> - Math — `_recompute.py` (9 load-bearing computations, pure stdlib, 0 failures)
> - Factcheck — `_factcheck_phase1.md` (recompute / reuse / primary; **0 blockers**)
>
> **Reconciliation verdict:** 18 is reconciled. Its load-bearing content is verified end-to-end:
> **9 math claims by recomputation** (token/leaky bucket sizing, fixed-window 2× boundary, sliding
> log vs counter accuracy/memory, distributed-counter slop, bounded-queue latency, retry
> amplification `1/(1−r)`, goodput collapse, adaptive-throttle reject probability), **every
> mechanism by reuse** of line-checked 03/11/13/14/15/16/17/10, and **three fetched primaries**
> (RFC 6585 §4 429/Retry-After; Google SRE *Handling Overload* + *Addressing Cascading
> Failures*). Remaining gaps are *vendor/paper attributions* (SEDA, CoDel, Hystrix, GCRA,
> Tail-at-Scale), carried forward `[UNVERIFIED]` — none load-bearing; none may harden into
> Phase-2 prose until fetched.

---

## The cross-cluster thesis (what this sub-course actually teaches)

18 is **deliberate overload control** — the sub-course where the queueing wall from 13 and the
consumer-lag/backpressure handoff named by 17 become an explicit engineering discipline. The
one truth underneath everything:

> **Demand can always exceed capacity. You will serve a subset of requests; the only question is
> whether you choose that subset deliberately — by rate-limiting the input, bounding the queues,
> shedding the least-valuable work, and bounding retries — or whether the system "chooses" it for
> you by melting down (unbounded latency, OOM, retry storm, cascading failure).**

13 proved the wall: `W = S/(1−ρ) → ∞` as `ρ→1`. 17 named the symptom: consumers fall behind, the
queue grows, it must be bounded. 18 supplies the four-layer answer, and the four clusters are
that answer in order — **input → buffer → drop → client**:

1. **A — bound the *input*: rate limiting (the proactive valve).** Token bucket (burst `B` +
   rate `r`), leaky bucket (smoothed output), fixed window (cheap, 2× boundary leak), sliding
   log (exact, O(limit)), sliding counter (O(1), bounded error) — one family across the
   *burst-tolerance × accuracy/memory* plane (all sized in `_recompute.py`). Distributed
   enforcement trades exactness for scale: a shared counter is a synchronous hot key (14/16/11),
   so cell-based local limiting over-admits by `(cells−1)·batch` (A5). Reject with **429 +
   Retry-After** (RFC 6585, VERIFIED). Enforce where it's cheapest to say no — edge/proxy/LB
   (16/10). But the limiter is **health-blind** (SRE, VERIFIED), so it is necessary, not
   sufficient.
2. **B — bound the *buffer*: backpressure + SEDA.** An unbounded queue is not safety — it
   converts overload into unbounded latency + OOM (the 13 wall). A bounded queue adds at most
   `Q/μ` latency (B1); SRE's rule — *queue ≤ 50% of the pool, reject early* — beats deep queues
   that hide overload. Once full, you **block** (propagate slow-down: TCP-window credit from 03,
   `request(n)` demand, pull-based logs from 17) or **drop** (hand off to C), the choice set by
   whether the producer is controllable. **SEDA** reframes a service as a graph of *explicit
   bounded queues with per-stage controllers* so overload is *visible* (queue length) and
   *actionable* (shed/adapt per stage).
3. **C — choose what to *drop*: load shedding (the reactive, health-aware valve).** Fail early
   and cheaply (503). Measure capacity in **resources (CPU), not QPS** (SRE, VERIFIED). Shed by
   **criticality** (4 tiers; reject a tier only when all lower tiers are already fully rejected)
   and **per-customer limits** (only misbehaving tenants eat errors). **Degrade** before you
   drop (partial corpus, stale cache — 16/15). Under overload prefer **LIFO/CoDel/deadline-drop**
   over FIFO (the oldest queued request is the most likely already-abandoned). And the killer:
   **retries amplify load `1/(1−r)`** (C1: .9→10×, .99→100×) into a **retry storm** and
   **goodput collapse** (C2: goodput plateaus at capacity without retries, *collapses below it*
   with naive retries + reject cost — congestion collapse). Fixes: per-request budget (3),
   per-client budget (10%), single-layer, backoff+jitter (16/17), Retry-After.
4. **D — bound the *client*: resilience patterns.** Timeouts (+ deadline propagation) bound the
   wait so a slow dependency can't starve threads; bounded retries (the C fixes as a client
   pattern, idempotent only — 17); **circuit breakers** stop calling the dead and let it recover;
   **bulkheads** isolate the blast radius (per-dependency pools); **hedged/tied requests** cut the
   tail (13/20) but add load so they stand down under shedding; **adaptive concurrency** (AIMD,
   reuse 03; Google **adaptive throttling** D1: `p = max(0,(req−K·acc)/(req+1))`) infers the
   right limit from latency instead of guessing a constant. All of it is parameterized by 20's
   capacity numbers — *18 defends the capacity 20 plans for* (SRE: capacity planning is necessary
   but not sufficient).

The through-line, identical to 13–17: **decide the expensive/failure case deliberately and make
saying "no" cheap.** Three primitives do double duty across clusters: the **bounded queue** (B
backpressure = C's shed point = D's bulkhead = A's leaky-bucket depth), **the budget/limit** (A's
token bucket = C's retry budgets = D's concurrency limit = the same "cap the multiplier" move),
and **the health/latency signal** (B queue length = C CPU/criticality = D adaptive limit = the
13 knee). Rate limiting is *proactive and health-blind*; shedding is *reactive and
health-aware*; backpressure *propagates*; resilience patterns *contain* — and you need all four
because each fails alone.

---

## 1. Key mechanisms (consolidated)

- **Token bucket:** burst `B` + sustained `r` as two knobs; long-run admit = min(arrival, r),
  instant burst ≤ B. **VERIFIED (A1).** *(A §1.1)*
- **Leaky bucket:** FIFO depth `D` leaked at `r`; output *smoothed* to `r`, overflow dropped.
  **VERIFIED (A2).** *(A §1.1)*
- **Fixed window:** O(1) but **2× limit boundary burst**. **Sliding log:** exact, O(limit).
  **Sliding counter:** `est = curr + prev·(1−frac)`, O(1), worst over-admit `prev·frac`.
  **VERIFIED (A3/A4).** *(A §1.1)*
- **Distributed limiting:** shared counter = synchronous hot key/SPOF (14/16/11); cell-based
  local limiting over-admits `(cells−1)·batch` — chatter vs slop dial. **VERIFIED (A5).** *(A §1.3)*
- **Fairness/burst + 429:** per-key/per-customer isolation; 429 + `Retry-After`, count
  per-resource/server/fleet (RFC 6585, **PRIMARY**). *(A §1.4)*
- **Enforcement ladder:** edge/proxy → LB → task; reject where cheapest; limiter is health-blind
  (SRE, **PRIMARY**). *(A §1.5; reuse 10/16)*
- **Bounded queue:** unbounded = OOM + unbounded latency (13 wall); bounded adds ≤ `Q/μ`; queue ≤
  50% pool, reject early (SRE). **VERIFIED (B1).** *(B §1.1)*
- **Block vs drop:** controllable producer → block (propagate); uncontrollable → drop (503/429).
  *(B §1.2)*
- **Credit/flow control:** TCP receiver window (03), `request(n)` demand, pull-based log
  consumer lag (17) = backpressure built in. *(B §1.3; reuse 03/17)*
- **End-to-end vs hop-by-hop:** hop = correct but slow to propagate; pair with edge admission.
  *(B §1.4)*
- **SEDA:** stage = bounded event queue + thread pool + controller; makes overload visible +
  per-stage actionable. *(B §1.5; SEDA paper `[UNVERIFIED]`)*
- **Admission control:** fail early/cheaply (503); measure capacity in CPU not QPS (SRE,
  **PRIMARY**). *(C §1.1)*
- **Criticality (4 tiers) + per-customer limits:** shed lowest-first, reject a tier only when all
  lower fully rejected; misbehaving tenants eat errors (SRE, **PRIMARY**). *(C §1.2)*
- **Brownout/degradation:** partial corpus / stale local copy (16/15) before errors (SRE,
  **PRIMARY**). *(C §1.3)*
- **Queue discipline:** FIFO→LIFO/CoDel + deadline-drop under overload (SRE, **PRIMARY**; CoDel
  paper `[UNVERIFIED]`). *(C §1.4)*
- **Retry amplification → storm → goodput collapse:** multiplier `1/(1−r)` (.9→10×, .99→100×);
  goodput collapses below capacity with naive retries (SRE 10K-QPS example, **PRIMARY**).
  **VERIFIED (C1/C2).** *(C §1.5)*
- **Retry bounds:** per-request budget 3, per-client budget 10%, single-layer, backoff+jitter
  (16/17), Retry-After, "overloaded; don't retry" (SRE, **PRIMARY**). **VERIFIED (C1).** *(C §1.6)*
- **Timeouts + deadline propagation:** bound the wait; pass remaining budget down. *(D §1.1)*
- **Circuit breaker:** closed→open→half-open; fail fast, let dependency recover. *(D §1.3;
  Hystrix `[UNVERIFIED]`)*
- **Bulkhead:** per-dependency bounded pool isolates blast radius. *(D §1.4)*
- **Hedged/tied requests:** cut tail (13/20), add load, stand down under shedding. *(D §1.5)*
- **Adaptive concurrency:** AIMD (03) / gradient infers limit from latency; Google adaptive
  throttling `p = max(0,(req−K·acc)/(req+1))`, K=2 default (SRE, **PRIMARY**). **VERIFIED (D1).**
  *(D §1.6)*
- **Handoff to 20:** every knob assumes known capacity; capacity planning necessary not
  sufficient (SRE, **PRIMARY**). *(D §1.7)*

## 2. Foundational sources (consolidated)

**VERIFIED BY RECOMPUTATION this session** (`_recompute.py`, pure stdlib, 9/9, 0 failures):
token/leaky bucket sizing (A1/A2); fixed-window 2× boundary + sliding-log exactness vs
sliding-counter `prev·frac` error & O(1)-vs-O(limit) memory (A3/A4); distributed over-admit
`(cells−1)·batch` (A5); bounded-queue latency `Q/μ` (B1); retry multiplier `1/(1−r)` + 3/10%
caps (C1); goodput plateau-vs-collapse (C2); adaptive-throttle reject `max(0,(req−K·acc)/(req+1))`
(D1).

**VERIFIED from FETCHED PRIMARIES this session** (`meta/fetched_primaries/`):
- **RFC 6585 §4** (Nottingham & Fielding, Apr 2012, `rfc6585.txt`): 429 = rate limiting,
  `Retry-After`, counting per-resource/server/fleet, user by credentials/cookie, 429 not cached.
- **Google SRE *Handling Overload*** (`sre_handling_overload.txt`): QPS pitfall / CPU-as-signal;
  per-customer limits; adaptive throttling (formula, K, "reject one per processed"); criticality
  (4 tiers + reject-lower-first); graceful degradation; retry budgets (3 / 10% / counter,
  "overloaded; don't retry").
- **Google SRE *Addressing Cascading Failures*** (`sre_cascading_failures.txt`): resource-
  exhaustion cascade + GC death spiral; queue/thread-pool model + "queue ≤ 50% pool, reject
  early"; fail-early-cheaply 503; FIFO→LIFO/CoDel [Nichols 2012]; enforcement layers + "rate
  limiting is health-blind"; the 10,000-QPS retry-storm; "capacity planning necessary not
  sufficient."

**Verified by REUSE (line-checked earlier — NOT re-fetched):**
- **13** Little's Law / M/M/1 `W=S/(1−ρ)` / `ρ→1` wall / tail / knee / USL.
- **03** TCP flow control (receiver window = credit) + AIMD congestion control + flow-vs-
  congestion distinction + connection limits.
- **17** queue-as-buffer + consumer lag = backpressure signal (pull-based), retry budgets +
  capped backoff+jitter + DLQ, idempotency.
- **16** jitter + coalescing + stale-serve degradation + hot key. **15** stale replica = degraded
  read. **14** hot shard/celebrity + sticky-routing rebalance cost. **11** no free global
  coordination. **10** reverse proxy as enforcement point.

**Blocked / not fetched — `[UNVERIFIED]`, carried forward (fetch when reachable):**
- *(A)* Envoy/Nginx `limit_req`/Cloudflare/Stripe/AWS-API-GW algorithms+defaults; GCRA; Redis
  cell-based limiter; Lyft global rate-limit service.
- *(B)* **SEDA** (Welsh/Culler/Brewer SOSP 2001) controller equations + overload graphs (Harvard
  + USENIX unreachable); Reactive Streams spec; Akka/Reactor/RxJava/Netty/gRPC-HTTP2 backpressure.
- *(C)* **CoDel** (Nichols & Jacobson, ACM Queue 2012) target/interval; AWS Builders' Library
  backoff-with-jitter (Brooker).
- *(D)* Netflix **Hystrix** + **concurrency-limits** (gradient/AIMD); resilience4j; Envoy
  circuit-breaking/outlier-detection; Nygard *Release It!*; Dean & Barroso "Tail at Scale" CACM
  2013 (hedged/tied — also carried by 13/20).

## 3. "Why it's this way" — forcing functions (consolidated)

- **Demand can exceed capacity and `ρ→1` ⇒ latency→∞** (13) ⇒ you must bound input (A), buffer
  (B), and drop deliberately (C); an unbounded queue just postpones the crash. *(A/B/C)*
- **Real traffic is bursty** ⇒ separate a burst budget from a sustained rate (token bucket). *(A)*
- **Exactness costs memory/coordination** ⇒ trade accuracy for scale (sliding counter; cell-based
  distributed slop `(cells−1)·batch`). *(A)*
- **A static limiter can't see health** (SRE) ⇒ pair it with reactive, resource-aware shedding. *(A/C)*
- **Producers differ in controllability** ⇒ block what you own, drop the Internet (B); you can
  only manage queues you can *see* (SEDA). *(B)*
- **Not all work is equal, and old queued work is often worthless** ⇒ criticality/per-customer
  shedding + LIFO/CoDel/deadline-drop. *(C)*
- **Retries multiply load exactly under overload** ⇒ `1/(1−r)` storm + goodput collapse ⇒ hard
  budgets + backoff/jitter + Retry-After. *(C/D)*
- **A slow dependency is worse than a dead one** ⇒ timeouts + breakers + bulkheads contain it. *(D)*
- **Fixed limits go stale as conditions change** ⇒ adaptive concurrency/throttling infers them
  from latency (the 03 window / 13 knee). *(D)*
- **Resilience needs capacity numbers** ⇒ 18 defends the capacity 20 plans; planning alone is
  insufficient. *(D)*

## 4. Common misconceptions to preempt (consolidated)

- "Rate limiting = load shedding." Static/health-blind (A) vs dynamic/health-aware (C). *(A/C)*
- "Fixed-window counters are accurate." 2× boundary burst (A3). "Sliding-log is always best."
  O(limit) memory; counter is O(1) (A4). "Shared Redis counter scales." Hot key/SPOF; cell-based
  over-admits (A5). "Token = leaky bucket." Permit-burst vs smooth-burst. *(A)*
- "A bigger queue is safer." It hides overload → unbounded latency + OOM; small queues reject
  early (B1). "Backpressure = dropping." Propagating slow-down vs dropping. "TCP handles my
  backpressure." Protects the socket, not the app/thread pool. "Async servers can't overload."
  Unbounded event queue OOMs the same. *(B)*
- "Serve everything under overload." Serves nothing (goodput collapse, C2); shed to hold goodput.
  "Retries improve reliability." Amplify `1/(1−r)` under overload (C1) → storm (C2). "Retry at
  every layer." Multipliers compound (27×). "FIFO is fair." Serves stalest/abandoned first;
  LIFO/CoDel better. "Measure load in QPS." Cost varies/drifts; use CPU. "503/breaker = giving
  up." Protects goodput + coordinates backoff. *(C)*
- "Generous timeouts are safe." Cause thread starvation; size to p99 + propagate deadlines.
  "Breakers are only for outages." Also for overload/latency. "Bulkheads waste resources." Cheap
  blast-radius insurance. "Hedging always helps." Adds load; backfires under overload. "A fixed
  concurrency cap is fine." Adaptive tracks the moving knee. "Capacity planning prevents
  cascades." Necessary, not sufficient. *(D)*

## 5. Best build-your-own target(s) (consolidated)

- **Four-algorithm limiter bench** (token/leaky/fixed/sliding-log/sliding-counter; replay a
  bursty trace; show the 2× boundary leak + `prev·frac` counter error) + **distributed limiter**
  (cell-based; sweep `sync_batch`, measure over-admit `(cells−1)·batch`; compare shared-counter
  latency). *(A; pairs 10 proxy → 429+Retry-After)*
- **Bounded-queue pipeline** (block-vs-drop on full; sweep depth, plot `Q/μ`; OOM the unbounded
  variant) + **credit-based stream** (`request(n)`; never overrun a slow consumer; compare TCP
  window from 03) + **mini-SEDA** (2 stages, bounded queue + pool + controller that sheds 503 &
  adapts; overload becomes visible queue growth). *(B; pairs 03/13/17)*
- **Goodput-vs-offered-load harness** (no-retry vs naive-3× vs budgeted+backoff; reproduce
  plateau vs collapse C2 + amplification C1) + **criticality shedder** (4 tiers + per-customer
  quotas; CRITICAL_PLUS survives) + **queue-discipline bench** (FIFO/LIFO/CoDel + deadline-drop;
  count *useful* completions). *(C; pairs 17/13)*
- **Circuit breaker + bulkhead** (trip/half-open + isolated pool; one slow dependency doesn't
  stall the rest) + **adaptive throttling client** (D1 formula; converge to "one reject per
  processed"; sweep K) + **AIMD concurrency limiter** (infer limit from latency; vs fixed cap) +
  **hedged-request tail cut** (2nd request past p95; measure p99 + extra load; backfire under
  overload). *(D; pairs 03/13/20)*

## 6. Open questions / gaps to close (consolidated — preserved verbatim in intent)

- **Vendor/paper attributions are `[UNVERIFIED]`** (none load-bearing; the method/math is verified
  by recomputation + reuse + the RFC 6585 / Google SRE primaries): Envoy/Nginx/Cloudflare/Stripe/
  AWS rate-limit algorithms + GCRA + Redis cell-based + Lyft RLS (A); **SEDA** SOSP 2001 +
  Reactive Streams + framework backpressure (B); **CoDel** ACM Queue 2012 + AWS backoff-jitter
  (C); **Hystrix**/concurrency-limits/resilience4j/Envoy + Nygard *Release It!* + Dean & Barroso
  "Tail at Scale" (D). Teach mechanisms now; do NOT harden specifics into Phase-2 prose until
  fetched.
- **Disagreements to resolve with sources:** default rate-limit algorithm to teach first (likely
  token bucket for burst + sliding-counter for distributed); whether to lead shedding with
  criticality (Google) or with adaptive concurrency (Netflix); how much of the breaker/bulkhead
  story is 18 vs an appendix.
- **Boundary discipline (cross-link, do NOT duplicate):**
  - queueing theory (`ρ`, Little's Law, M/M/1, the knee) → **13**; 18 *applies* it.
  - tail latency + hedged/tied requests *numbers* → **13/20**; 18 names the interaction.
  - TCP flow/congestion control internals → **03**; idempotency + bus retries + DLQ → **17**;
    edge/CDN placement + coalescing → **16/10**; stale replica = degraded read → **15**;
    hot key/shard → **14**; no-free-coordination → **11**.
  - capacity sizing / headroom / cascading-failure recovery → **20** (18 defends, 20 plans).
  - observing shed rate / retry ratio / breaker state / queue depth as SLO signals → **19**.
  - agentic budgets / tool-call rate limits / backpressure in the agent loop → **22/27/32**.
- **Next 18 work (optional, before Phase-2 prose):** fetch SEDA (USENIX/Harvard), CoDel (ACM
  Queue), Hystrix/concurrency-limits, and Tail-at-Scale when those hosts are reachable and
  upgrade the `[UNVERIFIED]` flags. Otherwise 18 is research-complete at the method/math level.
  **Next Phase-1 batch: 19-21** (Part II). **19 (observability-tracing-and-slos / Dapper)** is the
  natural next start — it owns the *signals* (shed rate, retry ratio, breaker state, queue depth,
  SLOs) that 18's controllers act on, and 20 (resilience/capacity/Tail-at-Scale) closes Part II.
