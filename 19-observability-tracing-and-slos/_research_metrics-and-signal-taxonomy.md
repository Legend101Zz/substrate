# 19 · Cluster A — Metrics & the signal taxonomy (what to measure)

> Phase-1 brief (NO course prose). One source cluster per ADR-001. Math claims are
> RECOMPUTED in `_recompute.py`. `[UNVERIFIED]` = not confirmed from a fetched primary
> this session; carried forward, must not harden into Phase-2 prose.

## Scope
Observability starts with **what signal to record and why**. This cluster covers the metric
primitives (counter/gauge/histogram), the three competing "what to measure" frameworks
(RED vs USE vs the Four Golden Signals), cardinality/aggregation cost, and percentile
discipline. It is the *measurement* layer that feeds the SLOs (Cluster D) and the controllers
of 18 (shed rate, retry ratio, breaker state, queue depth).

## 1. Key mechanisms

### 1.1 Metric primitives
- **Counter** — monotonically increasing total (requests, errors, bytes). You read its
  *rate* (`rate()` over a window), not its absolute value. Resets on process restart →
  rate functions must be counter-reset-aware.
- **Gauge** — an instantaneous value that can go up or down (queue depth, in-flight
  requests, memory, connections). This is the natural type for 18's **queue depth** and
  **in-flight/concurrency** signals and 13's **saturation**.
- **Histogram** — pre-bucketed distribution of observations (latency, payload size). Stores
  per-bucket counts so percentiles can be computed at query time WITHOUT keeping raw events.
  This is the metric-cheap way to get tail percentiles (reuses 13's percentile/HdrHistogram
  discipline). Aggregation across instances requires **bucket-additive** histograms (you can
  sum bucket counts; you canNOT average pre-computed percentiles — see §3.1).

### 1.2 The three "what to measure" frameworks (they are complementary, not rivals)
- **The Four Golden Signals** (Google SRE, Ch.6 — **VERIFIED** from
  `meta/fetched_primaries/sre_monitoring.txt`): **latency, traffic, errors, saturation**.
  "If you can only measure four metrics of your user-facing system, focus on these four."
  Latency: "distinguish between the latency of successful requests and the latency of failed
  requests" (a fast 500 must not flatter your latency SLI). Saturation = "how full your
  service is" + impending-saturation prediction.
- **RED** (Rate, Errors, Duration) — the request-centric view, per service/endpoint. Maps
  onto golden signals minus saturation. Best for *request-driven* services at the proxy
  (03/10 RED at the edge). [UNVERIFIED] attribution: Tom Wilkie / Weaveworks coined "RED".
- **USE** (Utilization, Saturation, Errors) — the **resource-centric** view, per resource
  (CPU, disk, NIC, lock). This is **reused verbatim from 13 Cluster B** (Gregg's USE method),
  where it was the bottleneck-finding lens. RED watches the *work*; USE watches the
  *machine*. [UNVERIFIED] attribution: Brendan Gregg "The USE Method" (carried from 13).
- Reconciliation: **RED/Golden = symptom-side (what users feel); USE = cause-side (why).**
  This is the same symptom-vs-cause split SRE Ch.6 draws for black-box vs white-box (§1.3).

### 1.3 Black-box vs white-box (SRE Ch.6 — VERIFIED)
- **Black-box** = symptom-oriented, probes from outside ("is it broken *now*?"). Good for
  paging: "forces discipline to only nag a human when a problem is both already ongoing and
  contributing to real symptoms."
- **White-box** = internals/telemetry ("*why* is it broken?"). Essential for debugging.
- "one person's symptom is another person's cause" (a slow DB is a symptom to the DB SRE, a
  cause to the frontend SRE) — the layering that 18's per-tier signals exploit.

### 1.4 Cardinality & aggregation (the cost model)
- A metric's **time-series count = product of its label cardinalities**. Adding a
  high-cardinality label (user_id, request_id, full URL) multiplies storage/CPU by that
  cardinality. RECOMPUTED (A8): `method(5)·status(4)·region(3) = 60` series; add `user_id`
  (1e6) → **60,000,000** series. This is the central reason metrics must stay **low-
  cardinality and aggregated**, while per-request identity belongs in **traces/logs**
  (Cluster B/C). The three pillars differ precisely on this cost axis.

## 2. Percentiles done right (reuse 13)
- "Most metrics are better thought of as distributions rather than averages" (SRE Ch.4 —
  VERIFIED from `sre_slo.txt`). A mean hides the tail; use p50/p99/p99.9.
- **Coordinated omission** (carried from 13/Tene): a load generator that stalls during a
  slow period UNDER-counts the slow requests, understating the tail by orders of magnitude
  (13 showed naive p99.9 = 1 ms vs CO-corrected ≈ 989 ms). Observability inherits the same
  trap: a histogram fed only by completed requests misses the requests that never completed.
- **You cannot average percentiles** across instances/time (§3.1). Aggregate the *buckets*,
  then compute the percentile — the reason histogram metrics store buckets, not quantiles.

## 3. Why it's this way (forcing functions)
### 3.1 Percentiles are not additive
Given two servers each reporting p99 = 100 ms, the fleet p99 is NOT 100 ms (could be far
higher if one server serves more traffic or has a fatter tail). Only the underlying
distribution (bucket counts) is additive. → metric systems standardized on histograms with
fixed/exponential buckets so quantiles are a query-time function of summed buckets.
### 3.2 Cardinality is the budget
Metric backends are cheap precisely because they aggregate away identity. Push identity in
and you reinvent a (more expensive) logging system. The pillar boundary is an economic one.
### 3.3 Counters over gauges for events
A gauge sampled every 10 s misses spikes between samples (13 saturation caveat); a counter
integrates every event, so its rate is exact regardless of scrape interval. Prefer counters
for anything you will rate().

## 4. Common misconceptions to preempt
- "Average latency is fine." No — averages hide the tail users actually feel (13/SRE Ch.4).
- "Just add user_id to the metric." That detonates cardinality (A8); use exemplars/traces.
- "p99 of p99s." Percentiles don't average; aggregate buckets first.
- "More signals = better." SRE Ch.4: "Have as few SLOs as possible"; too many indicators →
  noise and no one watches them.
- "Saturation = CPU%." Saturation is queueing/backlog beyond service rate (13/Little's Law);
  a box at 60% CPU with a growing run-queue is saturated.

## 5. Best build-your-own target(s)
- A tiny in-process **histogram with exponential buckets** + a `quantile(buckets, q)` query,
  demonstrating bucket-additivity across two simulated instances (ties to /build own-metrics
  or extends the 13 latency lab).

## 6. Open questions / where sources disagree
- RED vs Golden Signals naming/credit is informal; "RED" attribution to Wilkie is
  [UNVERIFIED] (Weaveworks blog blocked). USE attribution carried [UNVERIFIED] from 13.
- HdrHistogram exact bucketing / `recordValueWithExpectedInterval` CO-correction details are
  [UNVERIFIED] (carried from 13; brendangregg.com / hdrhistogram.org not fetched this session).
- Prometheus-specific histogram-vs-summary semantics [UNVERIFIED] (prometheus.io not fetched).
