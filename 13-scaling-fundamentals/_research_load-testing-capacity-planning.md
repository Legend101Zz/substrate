# 13 scaling-fundamentals — Cluster D: load testing & capacity planning method

> Phase 1 research brief (NO course prose). Standard six sections. Primary sources first;
> anything not fetched-and-verified this session is flagged `[UNVERIFIED from fetched source]`.
>
> **Network reality this session (5th consecutive):** only `lamport.azurewebsites.net` and
> Walmart artifactory resolve. Gil Tene's "How NOT to Measure Latency" talk/slides, the
> HdrHistogram pages, the wrk2 repo, and Schroeder/Harchol-Balter's "Open vs. Closed" paper
> all returned **HTTP 000** (verified by direct `curl`). Consequence: the **measurement
> logic** is presented from first principles and the **coordinated-omission arithmetic is
> verified by independent recomputation this session**; the **exact talk/paper attributions
> and tool specifics are flagged** and carried forward.
>
> **Scope of this cluster:** how to *measure* the wall Cluster A proved and Cluster B/C
> showed you how to find/move — load-test *models* (open vs. closed), the coordinated-omission
> measurement bug (Tene), percentile/histogram discipline, and the capacity-planning loop
> (headroom to a target utilization). This is the empirical complement to Cluster A's theory.

---

## 1. Key mechanisms (how the thing actually works, deeply)

### 1.1 The two load-generation models — open vs. closed

A load test is a *model of how requests arrive*, and the model changes the answer:

- **Closed model.** A fixed number of *virtual users* (concurrency `N`), each in a loop:
  send request → wait for response → think-time → repeat. The **next request cannot start
  until the previous one returns.** Offered load is therefore *self-limiting*: if the server
  slows, the clients slow with it. Parameter you control: **concurrency**.
- **Open model.** Requests arrive according to an *external arrival process* (e.g. a Poisson
  stream at rate `λ`) **independent of how fast the server responds.** New arrivals keep
  coming even if earlier ones are still in flight. Parameter you control: **arrival rate**.

**Why the distinction is load-bearing:** they exhibit *different* performance curves under
overload, and they model *different real systems*. A closed model with `N` users has a
built-in negative feedback loop (it can never offer more than `N` outstanding requests), so it
**hides overload** — it cannot reproduce the unbounded queue growth of Cluster A's `ρ→1`. An
open model has no such feedback: if `λ` exceeds capacity, the queue grows without bound,
exactly as M/M/1 predicts. **Most internet-facing services are open** (users/clients arrive
independently of your server's health), so testing them with a purely closed model
*systematically under-reports tail latency and overload behavior.* [Schroeder, Wierman,
Harchol-Balter, "Open Versus Closed: A Cautionary Tale" (NSDI 2006) is the primary;
`[UNVERIFIED from fetched source]` — host HTTP 000.]

- **Closed ⇒ Little's Law tie-in:** in a closed system, `N = X · R` (users = throughput ×
  response-time-incl-think), so as `R` rises, `X` falls — the feedback that caps offered load.
- **Practical:** use closed models for *capacity-of-a-fixed-client-pool* questions
  (e.g. a connection pool, a batch worker fleet); use open models for *internet traffic* and
  anything where arrivals are exogenous. Many tools default to closed, which is the trap.

### 1.2 Coordinated omission — the measurement bug that erases the tail

This is the headline of the cluster. **Coordinated omission** (Gil Tene's term) is a
systematic measurement error in *closed/loop-driven* load generators that **deletes exactly
the slow samples**, making latency reports optimistic by orders of magnitude at the tail.

**The mechanism.** A closed-loop client sends a request, *waits* for the response, then sends
the next. Suppose requests are *supposed* to go out every 1 ms (intended rate). Now the server
stalls for 100 ms (GC pause, lock, failover). During that stall:
- The one in-flight request is correctly measured as ~100 ms.
- But the **~100 requests that *should* have been sent during the stall were never sent** —
  the client was blocked waiting. Those omitted requests, had they been sent, would *also*
  have experienced large (decreasing) latencies (≈100 ms, 99 ms, 98 ms, …, 1 ms).
- The client "coordinates" its sending with the server's stall — it *omits* sending precisely
  when latency would have been high. The histogram therefore records **one** 100 ms sample
  instead of the **~100** high-latency samples reality would have produced.

**Consequence:** the percentiles are computed over a sample that is missing its worst members.
A reported "p99.9 = 2 ms" can hide true p99.9 of tens/hundreds of ms. The error grows with
the length and frequency of stalls — i.e. it is worst *exactly where you care most.*

**The fix (two equivalent framings):**
1. **Open-model / constant-arrival generation**: send on the *intended schedule* regardless
   of when responses return (e.g. `wrk2`'s constant-throughput mode), so stalls don't suppress
   issuance. Latency is then measured against *intended* send time.
2. **Correction in the recorder**: when a sample exceeds the expected inter-request interval,
   *synthesize the omitted samples* (back-fill the values that would have occurred), e.g.
   HdrHistogram's `recordValueWithExpectedInterval`. [Tene "How NOT to Measure Latency" +
   HdrHistogram/wrk2 are the primaries; `[UNVERIFIED from fetched source]` — hosts HTTP 000.
   The *arithmetic* below is verified this session.]

**Worked arithmetic (verified by recomputation this session).** A service responds in 1 ms
normally, but once per 10 000 requests it stalls for 1000 ms. Send rate intended 1 ms apart.
- *Naive closed measurement* (10 000 samples = 9 999 × 1 ms + 1 × 1000 ms): **p99 = 1.0 ms,
  p99.9 = 1.0 ms, p99.99 ≈ 1.1 ms, max = 1000 ms.** The report says "basically 1 ms" — the
  single slow sample doesn't even reach the p99.99.
- *Coordinated-omission-corrected:* the 1000 ms stall should have produced ~1000 requests
  with latencies 1000, 999, …, 1 ms (one per ms the client was blocked). Back-filling those
  gives ~10 999 samples whose tail is now dominated by the stall: **p99 ≈ 890 ms, p99.9 ≈
  989 ms, p99.99 ≈ 999 ms** (recomputed in pure Python this session). The naive method
  understated p99.9 by **~3 orders of magnitude** (1 ms → ~989 ms). The exact percentiles
  depend on the back-fill model (here one omitted sample per intended 1 ms interval), but the
  *direction and magnitude* — the tail you actually serve was almost entirely erased — is the
  load-bearing point.

### 1.3 Percentiles, histograms, and why you never average latencies

- **Never average percentiles, and never average latencies across servers.** The mean of
  per-second p99s is not the p99; percentiles are not linear. Aggregate by *merging the
  underlying distributions* (histograms), then computing the percentile once.
- **Use high-dynamic-range histograms.** Latency spans microseconds to seconds (Cluster A's
  ~9 orders of magnitude); fixed-bucket histograms either lose tail resolution or waste
  memory. HdrHistogram keeps constant *relative* error across the whole range — which is why
  it's the de-facto recorder for tail work. [HdrHistogram primary `[UNVERIFIED]`.]
- **Report the tail you serve at scale.** Cluster A §1.5: with fan-out `N`, the user's
  experience is dominated by p99/p99.9 of the *backends*, so capacity tests must report
  p99/p99.9(/p99.99 for high fan-out), not the mean. The required percentile rises with
  fan-out: if each user request touches 100 backends, the median user request sees ~the
  backend p99 (Cluster A fan-out math).

### 1.4 The capacity-planning loop — measuring and provisioning to a target

Capacity planning is the disciplined version of "how many machines?":

1. **Find the bottleneck resource** (Cluster B / USE) — the one whose `1/(1−ρ)` you'll climb.
2. **Measure the wall** with an *open-model, coordinated-omission-corrected* load test: ramp
   arrival rate `λ`, record throughput and the *tail* percentile, find the knee where the tail
   degrades (the empirical `ρ` at which `1/(1−ρ)` bites).
3. **Pick a target utilization with headroom** below the knee (often ρ ≈ 0.5–0.7 for
   latency-sensitive services) — buying latency headroom with idle capacity, per Cluster A.
4. **Provision via Little's Law:** required concurrency/instances = peak `λ` × per-request
   residence time at the target ρ, divided by per-instance capacity; size pools so
   `concurrency = throughput × latency` is satisfied with margin.
5. **Re-test after every change** — relieving one bottleneck moves it (Cluster B §1.6), so the
   loop repeats.

### 1.5 What a good load test must reproduce

- **Realistic arrival process** (open for internet traffic; correct burstiness/variance — the
  M/G/1 `C²ₛ` term, Cluster A §1.2). A perfectly smooth load test under-reports queueing vs.
  bursty real traffic.
- **Realistic mix and data** (cache hit ratios, key skew/hot keys, payload sizes) — a test
  that fits in cache or hits one hot shard measures the wrong wall.
- **Warmup + steady-state** (JIT/caches/connection pools must reach steady state before you
  trust numbers — ties to runtime internals, sub-course 05).
- **Coordinated-omission correction always on.** Without it, every other number is suspect.

---

## 2. Foundational sources

### Verified this session (by recomputation / reasoning — no fetch required)
- **Coordinated-omission magnitude** — the omitted-samples back-fill arithmetic in §1.2 was
  recomputed this session: a 1 in 10 000 × 1000 ms stall understates a true ~100 ms p99.9 as
  ~1 ms when the omitted ~1000 samples are dropped. Order-of-magnitude understatement verified.
- **Closed-model Little's-Law feedback** `N = X·R` ⇒ throughput falls as response time rises —
  same conservation identity verified in Cluster A (`_factcheck_clusterA.md` #1–#2).
- **Percentiles are non-linear / must merge distributions** — elementary statistics; the
  fan-out percentile requirement ties to Cluster A §1.5 (verified, claim #7).

### Reused verified canon (already line-checked in earlier sub-courses — do NOT re-fetch)
- **Tail/fan-out arithmetic** `1−(1−q)^N` driving which percentile to report — Cluster A
  (`_factcheck_clusterA.md` #7, verified by recomputation).
- **The utilization wall `1/(1−ρ)`** that the load test empirically locates — Cluster A
  (`_factcheck_clusterA.md` #4).
- **Cache hit-ratio / hot-key skew realism** — `08-caches-and-storage-systems/_research.md`
  (cache stampede / stale-while-revalidate), verified there; matters for test fidelity.

### Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals)
- **Gil Tene, "How NOT to Measure Latency"** (talk + slides; Strange Loop / QCon) — the
  canonical coordinated-omission exposition.
- **HdrHistogram** (`hdrhistogram.org` / GitHub `HdrHistogram/HdrHistogram`) —
  `recordValueWithExpectedInterval` correction; HDR bucketing.
- **`wrk2`** (GitHub `giltene/wrk2`) — constant-throughput, coordinated-omission-corrected
  load generator.
- **Schroeder, Wierman, Harchol-Balter, "Open Versus Closed: A Cautionary Tale"** (NSDI 2006)
  — the formal open-vs-closed model comparison.
- **Harchol-Balter, _Performance Modeling and Design of Computer Systems_** — open/closed
  queueing models, the textbook backing for Cluster A + D. `[UNVERIFIED]`.

---

## 3. "Why it's this way" — the forcing functions

- **The load model is part of the experiment, not a detail.** Closed models have a negative
  feedback loop (`N = X·R`) that *cannot* express unbounded overload; open models can. Testing
  an open (internet) system with a closed generator is measuring a different system — the
  arrival process is a first-class input, dictated by what you're modeling.
- **Coordinated omission exists because a blocked client stops sampling exactly when latency
  is worst.** The bug is *structural* to loop-driven generators: the measurement apparatus
  participates in the stall. Only constant-rate issuance (or back-fill correction) breaks the
  coordination. This is why "our p99 is great" is so often a lie.
- **You report the tail because users live in it and fan-out compounds it.** Cluster A's
  `1−(1−q)^N` forces the reported percentile upward with fan-out; the mean is operationally
  meaningless at scale.
- **You plan to a target ρ with headroom because the wall is hyperbolic.** Cluster A's
  `1/(1−ρ)` means the last few percent of utilization cost order-of-magnitude latency; the
  capacity loop buys headroom with idle capacity on purpose.
- **Realism (burstiness, skew, warmup) matters because variance and locality move the wall.**
  The M/G/1 `C²ₛ` term and cache hit-ratios change the effective capacity; an unrealistic test
  measures a wall that doesn't exist in production.

---

## 4. Common misconceptions to preempt

- **"Concurrency and arrival rate are the same knob."** False — §1.1: closed models control
  concurrency (self-limiting); open models control arrival rate (can overload). They give
  different curves; pick the one that matches your real arrival process.
- **"Our load test shows great p99."** Suspect by default — §1.2: if it's a closed/loop
  generator without coordinated-omission correction, the tail samples were *deleted*. Turn on
  constant-rate issuance / HdrHistogram correction before believing any percentile.
- **"Average the per-host p99s to get the fleet p99."** False — §1.3: percentiles aren't
  linear; merge the histograms, then take the percentile once.
- **"Run the test at 100% to find max throughput."** Misleading — max throughput at the cliff
  comes with catastrophic latency (Cluster A); the *useful* capacity is the knee under your
  tail-latency SLO, not the saturation point.
- **"A smooth, cache-friendly test is fine."** False — §1.5: real traffic is bursty and skewed
  (M/G/1 variance + hot keys); an unrealistic test measures the wrong wall.
- **"Closed-model testing is wrong, always use open."** Too strong — closed models correctly
  model *fixed client pools* (connection pools, batch fleets). Use the model that matches the
  system; the error is using closed for *open* (internet) traffic.

## 5. Best build-your-own target(s)

- **A coordinated-omission demo harness.** Build a tiny closed-loop generator and an
  open/constant-rate one against a server that periodically stalls; show the closed one reports
  ~1 ms p99.9 while the corrected/open one reports ~100 ms. The single most convincing lab in
  the sub-course — makes §1.2 undeniable.
- **An open-vs-closed curve plotter.** Drive the Cluster-A M/M/1 sim with (a) `N` fixed users
  and (b) Poisson arrivals at rate `λ`; overlay response-time-vs-load. The student *sees* the
  closed feedback loop hide the wall the open model exposes.
- **A capacity-planning notebook.** Given a measured throughput/tail curve, locate the knee,
  pick a target ρ, and size instances/pools via Little's Law with headroom — the full §1.4
  loop. Direct feeder into 21-design-case-studies.
- (Pairs with appendix **N-math-for-systems** for open/closed queueing derivations.)

## 6. Open questions / where sources disagree / gaps to close

- **Tene + HdrHistogram + wrk2 + Open-vs-Closed (NSDI 2006) are all blocked.** The *mechanism
  and arithmetic* of coordinated omission are verified by recomputation this session, but the
  canonical talk/paper/tool attributions stay `[UNVERIFIED from fetched source]` until the
  hosts are reachable. Do NOT harden exact quotes/figures or the NSDI citation into prose yet.
- **Exact HdrHistogram correction algorithm** (`recordValueWithExpectedInterval` back-fill
  rule) needs the primary before we describe it precisely; §1.2 fix #2 is the *intent*, not the
  verified algorithm.
- **Boundary with 19 (observability/SLOs):** percentile/histogram discipline is introduced
  here as *load-test* method; production *SLO/SLI* definitions and tracing live in 19. Keep the
  line clean.
- **Boundary with 20 (resilience/capacity planning):** the capacity *loop* and headroom
  *method* are here; *failure-mode* capacity (provisioning for node loss, tail-tolerant
  patterns, hedged requests) is 20.
- **Disagreement to resolve with sources:** the precise scope of "coordinated omission" (Tene
  frames it broadly; some define it narrowly as the back-fill correction). Pin against the talk
  before asserting a single definition.
