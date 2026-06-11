# 19 · Cluster D — SLIs, SLOs, error budgets & burn-rate alerting

> Phase-1 brief (NO course prose). Per ADR-001. ALL math RECOMPUTED in `_recompute.py`
> (28/28 pass). Primaries **VERIFIED** from `meta/fetched_primaries/sre_slo.txt`,
> `sre_monitoring.txt`, `sre_workbook_alerting.txt` (receipt
> `_VERIFIED_2026-06-10_observability.md`). `[UNVERIFIED]` carried forward.

## Scope
The signals (A/B/C) only matter if they tie to a **target** and an **alert that fires when
the target is threatened**. This cluster is the SRE control loop: define an SLI, set an SLO,
derive the error budget, and alert on **burn rate** with multiwindow multi-burn-rate rules.
This is the layer that closes the loop with 18 (the error budget is the policy that decides
when to slow releases / shed / degrade).

## 1. Key mechanisms

### 1.1 SLI / SLO / SLA (SRE Ch.4 — VERIFIED)
- **SLI** = "a carefully defined quantitative measure of some aspect of the level of service"
  (e.g. fraction of successful well-formed requests = availability/yield; request latency
  p99). Prefer **good-events / total-events** ratios (Workbook).
- **SLO** = "a target value or range of values for a service level that is measured by an
  SLI"; natural structure `SLI ≤ target` or `lower ≤ SLI ≤ upper` (e.g. "99.9% of Get RPCs
  complete < 100 ms"). Use **percentiles, not means** — "Most metrics are better thought of
  as distributions rather than averages" (reuse 13).
- **SLA** = "a contract with your users that includes consequences of meeting (or missing)
  the SLOs." SRE sets SLOs; business sets SLAs. SLO is usually **stricter** than the SLA
  (alert before you owe a refund).
- Guidance (VERIFIED): "Have as few SLOs as possible"; 100% is the wrong target — "it is
  better to allow an error budget." Chubby planned-outage example: deliberately spend budget
  so dependents don't over-rely on an SLO you don't promise.

### 1.2 Error budget (Workbook Ch.5 — VERIFIED; math RECOMPUTED)
- **Error budget = (1 − SLO) over the SLO window.** RECOMPUTED:
  - 99.9% SLO ⇒ allowed error fraction 0.1%; over 30 days = `0.001 × 43,200 min = 43.2
    min/30d`. Sanity ladder: 99%→432 min, 99.9%→43.2 min, 99.99%→4.32 min, 99.999%→0.432 min.
- The budget is a **currency**: feature velocity spends it; reliability work refills it. The
  **error-budget policy** decides what happens at exhaustion (freeze releases, divert to
  reliability) — this is the formal handoff to 18 (shed/degrade) and to release management.

### 1.3 Burn rate (Workbook Ch.5 — VERIFIED; math RECOMPUTED)
- **Burn rate** = "how fast, relative to the SLO, the service consumes the error budget."
  Burn rate **1** ⇒ budget exactly exhausted at the end of the SLO period.
- Budget consumed when an alert over `window` fires = `burn_rate × window / SLO_period`.
  Invert for "spend fraction P over `window`": `burn_rate = P × SLO_period / window`.
- RECOMPUTED, matching SRE's stated numbers:
  - "5% of a 30-day budget over 1 h requires **burn rate 36**" → `0.05 × 720 / 1 = 36`. 
  - Recommended page/ticket table (Table 5-6/5-8, 99.9% SLO):
    - **2% budget / 1 h window → burn rate 14.4** (Page)
    - **5% budget / 6 h window → burn rate 6** (Page)
    - **10% budget / 3 d window → burn rate 1** (Ticket)
  - "35× burn rate exhausts the 30-day budget in **20.5 h**" → `720 / 35 = 20.57 h`. 
- **Alert threshold error rate = burn_rate × (1 − SLO)** (the PromQL form
  `ratio_rate1h > 14.4 × 0.001`): RECOMPUTED 14.4×0.001 = **1.44%** error rate over 1 h;
  6×0.001 = **0.6%** over 6 h.

### 1.4 The alerting evolution (Workbook Iterations 1→6 — VERIFIED)
1. **Tiny fixed window** (10 min > SLO): fast but low precision — "0.1% error rate for 10
   minutes would alert, while consuming only 0.02% of the monthly budget." RECOMPUTED:
   `(0.001 × 10) / 43.2 ≈ 0.023%` of budget. → pages on non-events.
2. **Bigger window** (36 h for 5% spend): better precision, **terrible reset time** (fires
   for 36 h after a 100% outage).
3. **Duration parameter**: poor recall/detection — severity doesn't scale with the window.
4. **Burn-rate alert**: short window + burn-rate threshold = good precision + detection, but a
   single rate has a recall hole (a 35× burn never trips a 36× rule yet drains budget in 20 h).
5. **Multiple burn rates** (14.4 / 6 / 1) at (1 h / 6 h / 3 d): fast page for severe, ticket
   for slow-sustained. Needs alert suppression (a severe spike trips all three).
6. **Multiwindow, multi-burn-rate** (RECOMMENDED): AND a **short window = 1/12 of the long**
   so the alert only fires while *still burning*, and **stops ~short-window later** (better
   reset time). RECOMPUTED short windows: 1 h→5 min, 6 h→30 min, 3 d→6 h. Final
   recommended config for a 99.9% SLO (Table 5-8):
   - Page: long 1 h / short 5 m / burn 14.4 / 2% budget
   - Page: long 6 h / short 30 m / burn 6 / 5% budget
   - Ticket: long 3 d / short 6 h / burn 1 / 10% budget

## 2. Why it's this way (forcing functions)
- **100% is unaffordable & undesirable** (SRE Ch.4): the marginal nine costs exponentially
  (downtime ladder above) and slows innovation. The budget turns reliability into an explicit
  tradeoff, not an absolute.
- **Precision vs detection-time is the core tension** (Workbook §"dimensions": precision,
  recall, detection time, reset time). Tiny windows detect fast but page on noise; big windows
  are precise but slow to detect and slow to reset. Burn rate + dual windows is the Pareto fix.
- **Alert on symptoms (budget burn), not causes** (SRE Ch.6, reuse Cluster A black-box): the
  error budget is a user-facing symptom signal, which is why it makes a good paging trigger.

## 3. Common misconceptions to preempt
- "Aim for 100% uptime." Wrong target; set an SLO < 100% and budget the rest (SRE Ch.4).
- "Alert when error rate > SLO over a small window." Precision trap — pages on 0.02%-budget
  blips (RECOMPUTED).
- "One burn-rate threshold is enough." Recall hole: a sub-threshold-but-sustained burn drains
  the budget silently (35× vs 36× example). Use multiple rates.
- "Longer window = strictly better." Reset time degrades; a 36 h window fires for 36 h after a
  brief total outage. Add a short confirmation window (1/12 rule).
- "SLA = SLO." SLA is the external contract with consequences; SLO is the internal (stricter)
  target you alert on.

## 4. Best build-your-own target(s)
- A burn-rate alert simulator: feed a synthetic error-rate timeline, compute `ratio_rateXh`,
  and fire the multiwindow multi-burn-rate rules (14.4/6/1 with 1/12 short windows); show
  detection time vs reset time vs precision for each iteration 1→6.

## 5. Open questions / where sources disagree
- Exact error-budget *policy* templates (freeze criteria, exemptions) are org-specific; SRE
  Workbook Appendix B example [present in fetched text but not deeply factchecked] —
  defer detail to Phase 2.
- Latency-SLO error-budget accounting (counting slow-but-successful requests as "bad") has
  several conventions; SRE uses good/total ratio, but threshold choice is service-specific.
- Multi-burn-rate parameters are "reasonable starting numbers" (SRE explicitly says they
  "depend on the service") — not universal constants; present as defaults, not laws.
