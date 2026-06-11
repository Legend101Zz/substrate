# 19 · Phase-1 factcheck — observability-tracing-and-slos

> Method: every load-bearing claim is either (a) RECOMPUTED in `_recompute.py` (28/28 pass),
> (b) VERIFIED verbatim against a primary fetched this session to `meta/fetched_primaries/`,
> or (c) REUSED from a previously line-verified sub-course (11/13/16/17/09/03/10), or
> (d) flagged `[UNVERIFIED]` and carried forward (must not harden into Phase-2 prose).
> 0 blockers. No raccoon-shaped completeness.

## Primaries fetched + verified this session (network heal)
| source | file | what it anchors |
|--------|------|-----------------|
| Dapper (Google TR dapper-2010-1, 2010) | `dapper-2010.pdf` + `.txt` | Cluster B entire span/trace/context/sampling/overhead model |
| Google SRE Book Ch.4 "Service Level Objectives" | `sre_slo.txt` | Cluster D SLI/SLO/SLA defs; percentiles>means; error-budget rationale; "few SLOs" |
| Google SRE Book Ch.6 "Monitoring Distributed Systems" | `sre_monitoring.txt` | Cluster A Four Golden Signals; black-box vs white-box; symptoms-for-paging |
| Google SRE Workbook Ch.5 "Alerting on SLOs" | `sre_workbook_alerting.txt` | Cluster D burn-rate + multiwindow multi-burn-rate canon |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_observability.md`.

## Cluster A — metrics & signal taxonomy
- VERIFIED: Four Golden Signals = latency/traffic/errors/saturation; "distinguish latency of
  successful vs failed requests"; black-box=symptom / white-box=cause (sre_monitoring.txt).
- VERIFIED: "metrics better thought of as distributions rather than averages" → percentiles
  (sre_slo.txt).
- RECOMPUTED (A8): cardinality blow-up 60 → 60,000,000 series on adding user_id.
- REUSED: USE method + coordinated omission + HdrHistogram discipline from 13 (line-verified
  there); RED at the proxy from 03/10.
- `[UNVERIFIED]`: "RED" attribution to Wilkie/Weaveworks; HdrHistogram CO-correction specifics
  (carried from 13); Prometheus histogram-vs-summary semantics. None load-bearing.

## Cluster B — distributed tracing (Dapper)
- VERIFIED verbatim (dapper-2010.txt): trace=tree of nested RPCs; span = unit of work with
  span name/span id/parent id; root span = no parent id; shared 64-bit trace id; two-host RPC
  spans; thread-local trace context + async callback propagation + client→server id transmit;
  clock-skew handled by send-before-receive happens-before bounds; sampling necessary; uniform
  1/1024; adaptive sampling by target rate; overhead 204/176/9/40 ns, 426 B/span, <0.01% net,
  <0.3% core; Table 2 latency/throughput vs sampling; collection out-of-band 3-stage to
  Bigtable, median <15 s.
- RECOMPUTED (A6/A7): uniform sampled/s = QPS/1024; adaptive p = min(1,R/QPS) holds rate.
- REUSED: 11 happens-before/no-global-clock (spans); 13 fan-out tail (1-0.99^100); 17
  async/choreographed flow linkage.
- `[UNVERIFIED]`: W3C traceparent/OpenTelemetry/B3/Zipkin/Jaeger propagation; tail-sampling as
  named pattern; Magpie/X-Trace/Pinpoint own claims. None load-bearing (Dapper is the primary).

## Cluster C — logs, events & three pillars
- RECOMPUTED (A8): three-pillars cost boundary = the cardinality budget (60 vs 60M).
- VERIFIED: Dapper §4.6 collection-time second sampling + >=2 week retention (dapper-2010.txt).
- REUSED: 09 log abstraction (append-only ordered replayable); 16 retention/TTL (cost = rate x
  bytes x window); 17 consumer-lag/DLQ-depth as signals + retention math (history-independent).
- `[UNVERIFIED]`: exemplars exact spec (OpenMetrics/Prometheus); Honeycomb "wide events"
  critique of three-pillars; Loki/Elastic/ClickHouse storage tradeoffs. None load-bearing.

## Cluster D — SLI/SLO/error budgets & burn-rate alerting
- VERIFIED verbatim (sre_slo.txt / sre_workbook_alerting.txt): SLI/SLO/SLA definitions; SLI<=
  target structure; "Have as few SLOs as possible"; 100% wrong target; burn rate definition
  (rate 1 = exhaust at end of window); "5% over 1h = burn rate 36"; recommended table 2%/1h/
  14.4, 5%/6h/6, 10%/3d/1; multiwindow short=1/12 long; PromQL forms; "0.1% for 10 min
  consumes only 0.02% of budget"; "35x burn exhausts in 20.5h".
- RECOMPUTED (all in _recompute.py, 28/28): error budget = (1-SLO)*window (43.2 min/30d at
  99.9%); downtime ladder 432/43.2/4.32/0.432; burn_rate = P*period/window (36, 14.4, 6, 1);
  threshold error rate = burn*(1-SLO) (1.44%, 0.6%); naive-window 0.023% budget; 1/12 short
  windows (5m/30m/6h); time-to-exhaust 720/35 = 20.57h.
- REUSED: 13 percentiles/tail discipline; 18 error-budget-policy as the controller that
  decides freeze/shed/degrade.
- `[UNVERIFIED]`: error-budget-policy templates (Workbook App.B, deferred to Phase 2);
  latency-SLO accounting conventions. SRE itself flags the table as service-dependent
  "starting numbers," not constants. None load-bearing.

## Carry-forward still-blocked primaries (retried this session — STILL blocked)
SEDA SOSP'01 (eecs.harvard.edu), CoDel ACM Queue'12 (queue.acm.org 403), CAP/PACELC,
Herlihy-Wing, Bayou, CRDTs, Keshav, Codd, Kafka paper/KIPs, AWS builders' library, arxiv,
raft.github.io, postgresql.org, kafka.apache.org, martin.kleppmann. Unchanged from 18.

## Verdict
19 coverage is honest and primary-anchored on its load-bearing core (Dapper + 3 SRE
chapters fetched + 28/28 math recomputed). Reconcile into `_research.md`. Residual
`[UNVERIFIED]` items are non-load-bearing vendor/spec attributions, carried forward.
