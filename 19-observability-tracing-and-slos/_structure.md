# 19 — Observability, Tracing, and SLOs (Dapper) · _structure.md

**Identity:** the sensing half of the production control loop. When a number moves, how do you know
WHERE and WHY — and how do you set a target worth defending? Observability is a layered control
loop, not a pile of tools.

**Bespoke shape — "measure → explain → detail → target & alert (one control loop)."** NOT three
disconnected "pillars." The sub-course is a single layered loop where each layer answers the
question the previous one raises: **A — MEASURE (pick the right signal primitive + framework) → B —
EXPLAIN (a trace localizes WHERE the time/error went) → C — DETAIL (a log/event gives the full
local fact; exemplars stitch metric→trace→log) → D — TARGET & ALERT (SLI→SLO→error budget→burn-rate
alerting).** The closing move: the signals A/B/C/D produce ARE the inputs 18's controllers act on —
19 is the sensing half, 18 the actuating half, the error-budget policy the governor. Two cross-
cutting disciplines run throughout: percentiles (never average them) and cardinality (the master
economic constraint). Math heavily recomputed (28/28); Dapper + SRE chapters are VERIFIED primaries.

## Dependency position
- **Depends on:** 13 (percentiles/tail/coordinated-omission/USE/Little's Law — reused, not
  re-derived), 11 (happens-before/no-global-clock = trace ordering without synced clocks), 09 (the
  log abstraction), 16 (retention/TTL), 17 (consumer-lag/DLQ as signals, async flow tracing,
  retention math), 03/10 (RED at the proxy), 18 (the controllers the signals feed; error-budget
  policy as governor).
- **Feeds into:** 18 (closes the loop — sensing feeds actuating), 20 (golden signals + burn rate =
  capacity signals; tracing the straggler), 21 (every case has observability obligations), Part III
  (agent traces/eval loops).
- **Appendix links DOWN:** N-math (sampling statistics, RSE), O-cloud (managed telemetry). 19 owns
  the signal taxonomy + SLO discipline.

## Chapter specs (3–5 lines each)
### A — measure
1. **Signal primitives & cardinality** — counter / gauge / histogram; keep metrics LOW-cardinality
   (60 labels → 60M series, RECOMPUTED) — cardinality is the master economic constraint that divides
   the three pillars (identity lives in logs/traces, NOT metrics). Percentiles, not means; histograms
   are bucket-additive (you can't average quantiles).
2. **The signal frameworks** — Four Golden Signals (latency/traffic/errors/saturation) for user-
   facing SYMPTOMS; USE (13) for resource CAUSES; RED at the proxy for request rate/errors/duration.
   Black-box (symptom) vs white-box (cause); page on symptoms. Successful-vs-failed latency measured
   separately.

### B — explain (distributed tracing / Dapper)
3. **The trace as a causal span-tree** — a trace = tree of nested RPCs; span (name/id/parent-id) +
   64-bit trace id; root = no parent; context propagated thread-local + async + client→server. When a
   metric moves, the trace localizes WHERE in the call tree the time/error went. (Dapper, VERIFIED.)
4. **Causality without clocks, and sampling** — span ordering uses parent/child ids + send-before-
   receive happens-before bounds, NOT wall clocks (11's no-global-clock applied to spans). Sampling
   is necessary: uniform 1/1024 + adaptive-by-rate + a collection-time second pass; overhead is tiny
   (Table 2: 204/176/9/40 ns, 426 B/span, <0.01% net). Tail sampling noted as a modern pattern
   (UNVERIFIED).

### C — detail (logs/events + the three pillars)
5. **Logs, events & stitching the pillars** — a log/event gives the full LOCAL fact at one node;
   exemplars + shared trace ids stitch metric→trace→log into one drill-down. The three pillars are
   three points on ONE cost/detail curve, divided by the cardinality budget. Error-biased sampling +
   retention = 16 TTL + 17 `rate·bytes·window`. (Honeycomb "wide events" critique noted, UNVERIFIED.)

### D — target & alert (SLIs/SLOs/error budgets)
6. **SLIs, SLOs & the error budget** — SLI ≤ target; 100% is the wrong target (set an SLO + a budget);
   few SLOs. **Error budget = (1−SLO)·window** (43.2 min/30d @99.9%, RECOMPUTED). SLA = external
   contract ≠ SLO = internal target. Distributions, not averages (inherits 13's tail/CO discipline).
7. **Burn-rate alerting** — alert on budget BURN, not raw threshold: burn_rate = `P·period/window`
   (rate 1 = exhaust at window end); the naive-tiny-window precision trap; multiwindow multi-burn-
   rate config (e.g. 2%/1h/14.4, 5%/6h/6, 10%/3d/1 + 1/12 short windows) trading precision/detection/
   reset. The error-budget policy is the governor that decides freeze/shed/degrade — closing the loop
   into 18.

## Paired build labs (/build — instrument-it-yourself)
Bucket-additive histogram + query-time quantile (prove you can't average percentiles) → minimal
tracer (trace/span/parent ids; context propagated through a 2-tier RPC + an async hop; render as a
waterfall; clock-skew bounding WITHOUT synced clocks) → structured logger auto-injecting trace/span
id + a metric→trace→log exemplar drill-down → burn-rate alert simulator (feed an error timeline; run
iterations 1→6 + the recommended multiwindow multi-burn-rate config; visualize precision/detection/
reset; couple the error-budget policy to a mock 18 controller to close the loop).

## Diagrams needed
- The measure→explain→detail→target loop as spine motif, with 18 as the actuating half.
- Counter/gauge/histogram; cardinality explosion (60→60M series).
- Four Golden Signals vs USE vs RED (symptom vs cause; where each lives).
- Trace span-tree (root + nested RPC spans, parent/child ids) → waterfall rendering.
- Clock-skew bounding via send-before-receive (no synced clocks); sampling funnel (1/1024).
- Metric→trace→log stitching via exemplars + shared ids; three-pillars cost/detail curve.
- Error budget = (1−SLO)·window (downtime ladder); burn-rate exhaustion timeline.
- Multiwindow multi-burn-rate alert config (precision/detection/reset tradeoff).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED PRIMARIES this session (`meta/fetched_primaries/`):** Dapper (span-tree, 64-bit ids,
  context propagation, clock-skew bounds, uniform 1/1024 + adaptive sampling, overhead Table 2,
  out-of-band 3-stage collection median <15s); SRE Ch.4 (SLI/SLO/SLA, percentiles>means, 100% wrong,
  few SLOs); SRE Ch.6 (Four Golden Signals, black/white-box, page on symptoms); SRE Workbook Ch.5
  (error budget, burn-rate table, threshold = burn·(1−SLO), 1/12 short windows, multiwindow config);
  SEDA (bonus, confirms 18B).
- **RECOMPUTED (28/28):** error budget (1−SLO)·window + downtime ladder; burn_rate = P·period/window
  (36/14.4/6/1); threshold = burn·(1−SLO); naive-window precision trap; 1/12 short windows;
  time-to-exhaust 20.57h; sampled/s = QPS/1024; adaptive p=min(1,R/QPS); sampling RSE = 1/√obs +
  102,400 true-events-for-100-samples; cardinality 60→60M.
- **`[UNVERIFIED]` — spec/vendor attributions, non-load-bearing:** W3C Trace Context (traceparent/
  tracestate), OpenTelemetry span/log model, B3/Zipkin/Jaeger; OpenMetrics/Prometheus exemplars +
  histogram-vs-summary; "RED" credit (Wilkie/Weaveworks); HdrHistogram CO specifics (from 13);
  Honeycomb wide-events critique; Loki/Elastic/ClickHouse tradeoffs; tail sampling as a named pattern;
  Dapper's relatives (Magpie/X-Trace/Pinpoint); error-budget-policy templates (deep factcheck deferred
  to Phase 2; multi-burn-rate numbers are SRE-stated "starting points," service-dependent, NOT
  constants). Teach mechanisms now; do NOT harden specifics until fetched.
- **Still network-blocked (retried, STILL down):** CoDel (queue.acm.org 403), CAP/PACELC primaries
  (later VERIFIED in 20/21), Herlihy-Wing, Bayou, CRDTs, Keshav, Kafka paper/KIPs, AWS builders',
  arxiv, raft.github.io, postgresql.org, kafka.apache.org. NEWLY unblocked: SEDA (in 18), Kleppmann
  CAP blog (deferred).
- **Boundary discipline:** percentile/CO/USE/Little's-Law math → 13; happens-before theory → 11;
  log abstraction → 09; retention/TTL → 16/17; controllers that consume the signals → 18; capacity
  signals + straggler tracing → 20; sampling statistics → appendix N.
