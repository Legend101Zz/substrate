# 19 · observability-tracing-and-slos — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). Synthesizes the four cluster files
> per ADR-001. Full depth lives in the cluster files; this file is the cross-cluster spine,
> consolidated sources, and the gap ledger. Math: `_recompute.py` (28/28 pass). Primaries
> fetched this session: Dapper + 3 SRE chapters (+ SEDA bonus) in `meta/fetched_primaries/`.

Cluster files:
- `_research_metrics-and-signal-taxonomy.md` (A)
- `_research_distributed-tracing-dapper.md` (B)
- `_research_logs-events-three-pillars.md` (C)
- `_research_sli-slo-error-budgets.md` (D)
Factcheck: `_factcheck_phase1.md`. Recompute: `_recompute.py`.

---

## 1. The spine (how the clusters compose)
Observability is a **layered control loop**, not a pile of tools:

1. **Measure** (A) — pick the right signal primitive (counter/gauge/histogram) and the right
   framework (Four Golden Signals for user-facing symptoms; USE for resource causes; RED at
   the proxy). Keep metrics low-cardinality; percentiles, not means.
2. **Explain** (B) — when a metric moves, a **trace** localizes *where* in the call tree the
   time/error went, reconstructing one request's causal span-tree across services (Dapper).
3. **Detail** (C) — a **log/event** gives the full local fact at one node; exemplars + shared
   trace ids stitch metric -> trace -> log. The three pillars are three points on one
   cost/detail curve, divided by the **cardinality budget** (A 3.2).
4. **Target & alert** (D) — tie an SLI to an SLO, derive the **error budget = (1-SLO)*window**,
   and alert on **burn rate** with multiwindow multi-burn-rate rules.

**The closed loop with 18:** the signals D/A/B/C produce (shed rate, retry ratio, breaker
state, queue depth, latency percentiles, error-budget burn) ARE the inputs 18's controllers
act on. 19 is the sensing half; 18 is the actuating half. The **error-budget policy** is the
governor that decides when to freeze releases / shed / degrade.

## 2. Cross-cluster reconciliations (where clusters meet)
- **Percentiles are one discipline, used twice**: A (metric histograms, bucket-additivity, no
  averaging quantiles) and D (latency SLOs at p99/p99.9) both inherit 13's tail + coordinated-
  omission discipline. Verified once (sre_slo.txt "distributions not averages"), applied in
  both.
- **Causality without clocks**: B's clock-skew handling (send-before-receive happens-before
  bounds) is 11's no-global-clock theorem applied to spans. The same reason trace ordering
  uses parent/child ids, not wall clocks.
- **Cardinality is the master economic constraint**: A (60 -> 60M series), C (why identity
  lives in logs/traces not metrics), B (why traces are sampled at 1/1024). One forcing
  function, three consequences. RECOMPUTED (A8) + Dapper-VERIFIED (1/1024).
- **Sampling reappears at every pillar**: B (head 1/1024 + adaptive-by-rate + collection-time
  second pass), C (error-biased log/trace sampling + retention = 16 TTL + 17 rate*bytes*window).
- **Symptom vs cause** runs through everything: SRE black-box(symptom)/white-box(cause) (A) =
  RED/Golden(symptom)/USE(cause) (A) = alert-on-budget-burn(symptom)/traces(cause) (D).
- **17 async flows become legible**: B's async context propagation links producer->broker->
  consumer spans; 17's consumer-lag/DLQ-depth are the metric signals (C), the trace is the
  causal explanation, 18 acts on them.

## 3. Load-bearing facts, by provenance
**VERIFIED from primaries fetched this session** (`meta/fetched_primaries/`):
- Dapper: trace=tree of nested RPCs; span(name/id/parent id) + 64-bit trace id; root=no
  parent; two-host RPC spans; thread-local + async + client->server context propagation;
  clock-skew via send-before-receive bounds; sampling necessary; uniform 1/1024; adaptive
  sampling by target rate; overhead 204/176/9/40 ns, 426 B/span, <0.01% net, <0.3% core,
  Table 2; out-of-band 3-stage collection to Bigtable, median <15 s.
- SRE Ch.4: SLI/SLO/SLA defs; SLI<=target; percentiles>means; 100% wrong target; "few SLOs".
- SRE Ch.6: Four Golden Signals (latency/traffic/errors/saturation); successful-vs-failed
  latency; black-box(symptom)/white-box(cause); symptoms-for-paging.
- SRE Workbook Ch.5: error budget; burn-rate (rate 1 = exhaust at window end); 5%/1h=36;
  table 2%/1h/14.4, 5%/6h/6, 10%/3d/1; threshold = burn*(1-SLO); 1/12 short window;
  multiwindow multi-burn-rate config; iterations 1->6 with the precision/reset tradeoffs.
- SEDA (bonus, also confirms 18B): stage/queue/thread-pool/controller; well-conditioned =
  graceful degradation; dynamic resource controllers; explicit bounded queues.

**RECOMPUTED** (`_recompute.py`, 28/28): error budget (1-SLO)*window (43.2 min/30d @99.9%) +
downtime ladder; burn_rate = P*period/window (36, 14.4, 6, 1); threshold = burn*(1-SLO)
(1.44%, 0.6%); naive-window precision trap (0.023% budget); 1/12 short windows (5m/30m/6h);
time-to-exhaust 720/35=20.57h; uniform sampled/s=QPS/1024; adaptive p=min(1,R/QPS);
sampling RSE = 1/sqrt(obs) + 102,400 true-events-for-100-samples; cardinality 60->60M.

**REUSED from line-verified prior sub-courses**: 13 (percentiles/tail/coordinated-omission/
USE/Little's Law), 11 (happens-before/no-global-clock), 09 (log abstraction), 16 (retention/
TTL), 17 (consumer-lag/DLQ/retention math/async flows), 03/10 (RED at the proxy), 18 (the
controllers the signals feed; error-budget policy).

## 4. Common misconceptions (consolidated)
- Average latency is fine (no — tails); p99 of p99s (can't average percentiles); add user_id
  to a metric (cardinality bomb); aim for 100% uptime (set an SLO + budget); alert on a tiny
  window over SLO (precision trap); one burn-rate threshold (recall hole); longer window is
  strictly better (reset-time penalty); tracing needs synchronized clocks (no — causal ids);
  a span = a service (a span = a unit of work); tracing/logs/metrics are redundant (three
  questions, three pillars); SLA = SLO (external contract vs internal target).

## 5. Build-your-own targets
- Bucket-additive histogram + query-time quantile (A).
- Minimal tracer: trace/span/parent ids, context propagated through 2-tier RPC + async hop,
  rendered as a waterfall; clock-skew bounding without synced clocks (B).
- Structured logger auto-injecting trace/span id + a metric->trace->log exemplar drill-down (C).
- Burn-rate alert simulator: feed an error timeline, run iterations 1->6 + the recommended
  multiwindow multi-burn-rate config; visualize precision/detection/reset (D).

## 6. Open questions / gaps (carry-forward `[UNVERIFIED]` — do NOT harden into prose)
- **Spec/vendor attributions (non-load-bearing):** W3C Trace Context (traceparent/tracestate),
  OpenTelemetry span/log model, B3/Zipkin/Jaeger propagation; OpenMetrics/Prometheus exemplars
  + histogram-vs-summary; "RED" credit (Wilkie/Weaveworks); HdrHistogram CO-correction
  specifics (carried from 13); Honeycomb "wide events" critique of the three-pillars framing;
  Loki/Elastic/ClickHouse storage tradeoffs. (All target hosts not fetched this session.)
- **Tail sampling** as a named modern pattern (+ buffering cost): post-Dapper, [UNVERIFIED].
- **Dapper's cited relatives** Magpie/X-Trace/Pinpoint: mentioned by Dapper, own claims
  [UNVERIFIED].
- **Error-budget policy templates** (SRE Workbook App.B): present in fetched text, deep
  factcheck deferred to Phase 2; multi-burn-rate numbers are SRE-stated "starting points,"
  service-dependent, not constants.
- **Still network-blocked carry-forwards (retried this session, STILL down):** CoDel ACM
  Queue'12 (queue.acm.org 403), CAP/PACELC primaries, Herlihy-Wing, Bayou, CRDTs, Keshav,
  Codd, Kafka paper/KIPs, AWS builders' library, arxiv, raft.github.io, postgresql.org,
  kafka.apache.org. **NEWLY UNBLOCKED this session: SEDA (upgraded in 18) + Kleppmann CAP
  blog (HTTP 200 — fetch+verify deferred; not load-bearing for 19).**
