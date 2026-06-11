# 19 · Cluster C — Logs, events & the three pillars

> Phase-1 brief (NO course prose). Per ADR-001. `[UNVERIFIED]` carried forward.
> Reuses 09 (the log abstraction), 16 (retention), 17 (consumer-lag/DLQ as signals).

## Scope
The third pillar. Metrics (Cluster A) tell you *that* something is wrong cheaply; traces
(Cluster B) tell you *where* in the call tree; **logs/events** tell you *exactly what
happened* at one point with full local detail. This cluster covers structured logging, the
three-pillars cost/cardinality tradeoff, exemplars that stitch metrics→traces→logs, and
sampling/retention.

## 1. Key mechanisms

### 1.1 The three pillars and their cost axis
- **Metrics** = aggregated numbers over time; cheap, low-cardinality, great for alerting and
  dashboards; lose per-event identity (Cluster A §1.4).
- **Traces** = per-request causal trees; medium cost, sampled (Cluster B); show cross-service
  causality.
- **Logs/events** = per-event records with arbitrary fields; highest cost per unit insight at
  scale (cardinality is unbounded — every field is effectively a label), richest local detail.
- The boundary is **economic**, the same cardinality budget from Cluster A (§3.2): identity
  and high-cardinality context belong in logs/traces; counts/rates belong in metrics. Pushing
  identity into metrics detonates series count (A8: 60 → 60,000,000).

### 1.2 Structured logging
- A log line should be a **structured record** (key/value, e.g. JSON), not a free-text
  string, so it is queryable/aggregatable without regex archaeology. Carry the **trace id +
  span id** (Cluster B) in every log line so logs join to the trace that produced them — the
  glue that makes the three pillars one system, not three silos.
- Levels (DEBUG/INFO/WARN/ERROR) are a sampling/volume knob, not just severity decoration.

### 1.3 Exemplars (metric → trace linkage)
- An **exemplar** attaches a sample trace id (and its value) to a metric bucket — e.g. the
  histogram bucket that holds your p99.9 latency carries the trace id of one request that
  landed there. This is the designed bridge from "p99.9 is high" (metric) to "here is one
  slow request's full trace" (trace) to "here are its logs" — without paying per-request
  metric cardinality. [UNVERIFIED] exact spec: OpenMetrics/Prometheus exemplars
  (openmetrics.io / prometheus.io not fetched).

### 1.4 Events vs logs vs the log abstraction (reuse 09/17)
- An **event** is a structured, business-meaningful fact ("order.placed"); a **log** is an
  operational record. Both are append-only streams — the **log abstraction from 09** (totally
  ordered, replayable). 17's broker IS an event log; observability often reuses the same
  transport (ship logs/spans through Kafka-like pipelines).
- **17 signals that live as events/metrics**: consumer **lag** (gauge), **DLQ depth** (gauge),
  redelivery/retry ratio — these are exactly the inputs 18's controllers act on, surfaced via
  this pillar.

### 1.5 Sampling & retention (reuse 16 retention, 09 log)
- Logs/traces are **sampled** (Cluster B 1/1024 head-sampling) and **retained** for a bounded
  window (Dapper: ≥ 2 weeks; collection-time second sampling caps repository write throughput
  — Dapper §4.6, VERIFIED). Retention is the **16 TTL/eviction** problem applied to telemetry:
  hot-recent kept verbatim, older down-sampled/rolled-up/expired. Cost = rate × bytes ×
  retention (the 17 retention math, history-independent vs compaction).
- **Error/slow-biased sampling**: keep 100% of error traces/logs, sample the happy path —
  the analog of tail sampling (Cluster B), maximizing signal per stored byte.

## 2. Why it's this way (forcing functions)
- **Cardinality economics** (A §3.2) is the master constraint: you cannot afford per-request
  identity in metrics, so it migrates to logs/traces, which in turn must be sampled/retained
  to stay affordable. The three pillars are three points on a cost/detail curve, not a
  fashion choice.
- **Joinability requires shared ids.** Without trace id + span id in logs and exemplars in
  metrics, the three pillars are disconnected and an investigation degrades to manual
  correlation by timestamp (SRE Ch.6 warns against fragile timestamp-correlation).
- **Volume forces sampling.** Same Dapper forcing function as tracing: always-on + full
  fidelity is unaffordable; sample + bias toward errors.

## 3. Common misconceptions to preempt
- "Logs are enough; skip metrics/traces." Logs don't aggregate cheaply (no fast p99 across a
  fleet) and don't show cross-service causality. Each pillar answers a different question.
- "Structured logging is just JSON formatting." Its point is queryability + id-joins, not
  syntax.
- "Keep everything forever." Retention cost = rate × bytes × window (17); unbounded retention
  is unbounded spend. Down-sample/roll-up old data (16).
- "Trace and log are redundant." Trace = causal skeleton across services; log = full local
  detail at one node. Exemplars connect them; neither subsumes the other.

## 4. Best build-your-own target(s)
- A structured logger that auto-injects the current trace/span id (from Cluster B's context),
  + a tiny "exemplar" that tags a latency-histogram bucket with one sample trace id; show a
  metric→trace→log drill-down on a simulated slow request.

## 5. Open questions / where sources disagree
- "Three pillars" framing is industry-canonical but its sharpest critiques (Majors/Honeycomb:
  "observability ≠ three pillars, it's high-cardinality wide events") are [UNVERIFIED]
  (honeycomb.io not fetched). Worth presenting as a genuine debate in Phase 2.
- OpenTelemetry logs/exemplars spec, OpenMetrics exemplars [UNVERIFIED] (not fetched).
- Elastic/Loki/ClickHouse log-storage tradeoffs [UNVERIFIED] (vendor docs not fetched).
