#!/usr/bin/env python3
"""
Substrate 19 — observability-tracing-and-slos: independent recomputation of every
load-bearing quantitative claim. Pure stdlib. Run: python3 _recompute.py

Each check asserts the claim AND prints the worked number so a skeptical reader can
follow the arithmetic. Sources are cited inline; primary receipts in
meta/fetched_primaries/_VERIFIED_2026-06-10_observability.md and
.../sre_workbook_alerting.txt + dapper-2010.txt.
"""

EPS = 1e-9
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# -------------------------------------------------------------------------
# 1. Error budget = (1 - SLO) * window.  (SRE Workbook Ch.5; SRE Book Ch.4)
#    For a 99.9% SLO over 30 days, the *allowed* error fraction is 0.1%, and
#    the absolute budget is 0.001 * (minutes in 30 days).
# -------------------------------------------------------------------------
SLO = 0.999
err_ratio = 1 - SLO                                  # 0.001
period_min = 30 * 24 * 60                            # 43,200 min
budget_min = err_ratio * period_min                  # minutes of "allowed badness"
check("error-budget fraction", approx(err_ratio, 0.001),
      f"1-SLO = {err_ratio} (0.1%)")
check("error-budget absolute (30d, 99.9%)", approx(budget_min, 43.2),
      f"0.001 * {period_min} min = {budget_min} min/30d (~43.2 min)")

# Three-nines / four-nines / five-nines downtime per 30-day month (sanity table).
for nines, expect in [(0.99, 432.0), (0.999, 43.2), (0.9999, 4.32), (0.99999, 0.432)]:
    dt = (1 - nines) * period_min
    check(f"downtime budget at SLO={nines}", approx(dt, expect),
          f"{dt:.3f} min/30d")


# -------------------------------------------------------------------------
# 2. Burn rate.  (SRE Workbook Ch.5, "Alert on Burn Rate")
#    Burn rate = how fast, relative to the SLO, you consume the budget.
#    Burn rate 1 => budget exactly exhausted at the end of the SLO period.
#    Budget consumed when an alert over `window` fires =
#        burn_rate * window / SLO_period
#    => to spend a target fraction P of the budget over `window`:
#        burn_rate = P * SLO_period / window
# -------------------------------------------------------------------------
def burn_rate_for(P, window_h, period_h=30*24):
    return P * period_h / window_h

# "Five percent of a 30-day error budget spend over one hour requires a burn rate of 36."
br = burn_rate_for(0.05, 1)
check("burn rate: 5% budget / 1h", approx(br, 36.0),
      f"0.05 * 720h / 1h = {br} (SRE: 'burn rate of 36')")

# Recommended multi-burn-rate table (Table 5-6 / 5-8, 99.9% SLO):
#   2% / 1h  -> 14.4 ; 5% / 6h -> 6 ; 10% / 3d -> 1
br_2_1h  = burn_rate_for(0.02, 1)
br_5_6h  = burn_rate_for(0.05, 6)
br_10_3d = burn_rate_for(0.10, 72)
check("burn rate: 2% / 1h  (Page)",  approx(br_2_1h, 14.4),  f"0.02*720/1   = {br_2_1h}")
check("burn rate: 5% / 6h  (Page)",  approx(br_5_6h, 6.0),   f"0.05*720/6   = {br_5_6h}")
check("burn rate: 10% / 3d (Ticket)",approx(br_10_3d, 1.0),  f"0.10*720/72  = {br_10_3d}")

# Inverse: time to *exhaust the whole budget* at a given burn rate = period / burn_rate.
# Workbook: "a 35x burn rate ... consumes all of the 30-day budget in 20.5 hours."
t_exhaust_35 = (30*24) / 35.0
check("time to exhaust budget at 35x", approx(t_exhaust_35, 20.571, tol=2e-3),
      f"720h / 35 = {t_exhaust_35:.3f} h (~20.5 h)")


# -------------------------------------------------------------------------
# 3. The error rate an alert must observe to constitute a given burn rate.
#    Threshold error rate = burn_rate * (1 - SLO).
#    Workbook PromQL: ratio_rate1h > 14.4 * 0.001  => alert when 1h error
#    rate exceeds 1.44%.
# -------------------------------------------------------------------------
thr_14_4 = br_2_1h * err_ratio
check("alert threshold error rate @14.4x", approx(thr_14_4, 0.0144),
      f"14.4 * 0.001 = {thr_14_4} (1.44% error rate over 1h)")
thr_6 = br_5_6h * err_ratio
check("alert threshold error rate @6x", approx(thr_6, 0.006),
      f"6 * 0.001 = {thr_6} (0.6% over 6h)")


# -------------------------------------------------------------------------
# 4. The "tiny-window naive alert" precision trap. (Workbook Iteration 1)
#    "A 0.1% error rate for 10 minutes would alert, while consuming only
#    0.02% of the monthly error budget."
#    Budget consumed fraction = (observed_error_rate * window) / total_budget
#      total_budget (in error-minutes) = (1-SLO) * period
#      error-minutes spent ~ observed_error_rate * window
# -------------------------------------------------------------------------
window_min = 10
obs_err = 0.001                                   # 0.1%
err_minutes_spent = obs_err * window_min          # 0.01 error-min
frac_budget = err_minutes_spent / budget_min      # fraction of 43.2 min budget
check("naive 10m/0.1% consumes ~0.02% budget", approx(frac_budget, 0.0002314, tol=5e-3),
      f"(0.001*10)/{budget_min} = {frac_budget*100:.4f}% (~0.02%)")


# -------------------------------------------------------------------------
# 5. Multiwindow short-window guideline: short = 1/12 of long. (Workbook Iter 6)
# -------------------------------------------------------------------------
for long_h, short_expect_min in [(1, 5), (6, 30), (72, 360)]:
    short_min = long_h * 60 / 12
    check(f"short window = 1/12 long ({long_h}h)", approx(short_min, short_expect_min),
          f"{long_h}h/12 = {short_min:.0f} min")


# -------------------------------------------------------------------------
# 6. Dapper sampling overhead model. (Dapper §2.4/§4.4)
#    Overhead attributed to a process is proportional to traces sampled per
#    unit time. Uniform p=1/1024 keeps cost ~constant per request; expected
#    sampled traces = p * QPS.  Adaptive sampling targets a *rate* R: it
#    picks p = min(1, R/QPS) so sampled-traces/sec ~ R regardless of QPS.
# -------------------------------------------------------------------------
p_uniform = 1/1024
for qps in (10, 1000, 100000):
    sampled_per_s = p_uniform * qps
    check(f"uniform 1/1024 sampled/s @ {qps} QPS", sampled_per_s == qps/1024,
          f"{qps}/1024 = {sampled_per_s:.4f} traces/s")

# Adaptive: target R=10 traces/s. Low-traffic raises p; high-traffic lowers it.
R = 10
for qps, expect_p in [(5, 1.0), (100, 0.1), (100000, 0.0001)]:
    p = min(1.0, R / qps)
    check(f"adaptive p for target {R}/s @ {qps} QPS", approx(p, expect_p),
          f"min(1, {R}/{qps}) = {p:g}; sampled/s = {min(R, qps)}")


# -------------------------------------------------------------------------
# 7. Sampling estimator error (statistics of the 1/N sample).
#    A counted event observed k times in a sample at rate p estimates the
#    true count k/p. The relative standard error of a Poisson/Binomial count
#    estimate ~ 1/sqrt(k_observed). Dapper: "If a notable pattern surfaces
#    once ... it will surface thousands of times" -> at p=1/1024 a pattern
#    occurring T times in truth is seen ~T/1024; you need T >> 1024 to see it.
# -------------------------------------------------------------------------
import math
# Relative standard error of a scaled count with `obs` observed samples.
for obs in (1, 100, 10000):
    rse = 1 / math.sqrt(obs)
    check(f"sampling RSE at {obs} observed", approx(rse, {1:1.0,100:0.1,10000:0.01}[obs]),
          f"1/sqrt({obs}) = {rse:.4f} ({rse*100:.1f}% relative error)")
# To observe ~100 samples of a pattern at p=1/1024, it must truly occur ~102,400x.
need_true = 100 / p_uniform
check("true events needed for 100 samples @1/1024", approx(need_true, 102400),
      f"100 / (1/1024) = {need_true:.0f} true occurrences")


# -------------------------------------------------------------------------
# 8. Three-pillars cost intuition (cardinality blow-up).
#    A metric's series count = product of label cardinalities. Adding a
#    high-cardinality label (e.g. user_id) multiplies storage by that count.
#    This is WHY traces/logs (per-event) cost more than aggregated metrics.
# -------------------------------------------------------------------------
base_series = 5 * 4 * 3            # method x status x region = 60 series
with_userid = base_series * 1_000_000
check("cardinality explosion w/ user_id label",
      with_userid == 60_000_000,
      f"60 * 1e6 = {with_userid:,} series (vs {base_series} aggregated)")


# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _,ok,_ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    bad = [nm for nm,ok,_ in results if not ok]
    print("FAILED:", bad); raise SystemExit(1)
print("All load-bearing 19 math claims verified by recomputation.")
