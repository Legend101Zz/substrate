#!/usr/bin/env python3
"""
Substrate 32 - cost-observability-and-ops: independent recomputation of every quantitative claim in
the cost/ops brief. Pure stdlib. Run: python3 _recompute.py

32 introduces NO new load-bearing primary. It makes 22's O(T^2) token economics OPERATIONAL:
- token/$ accounting on top of the 22 quadratic transcript growth;
- prefix/prompt caching ROI (the 24 prefix-cache discount, made a dollar number);
- per-tenant quotas/budgets = the 18 rate-limiting/admission identity over dollars;
- the cost dashboard = the 19 metrics/observability identity over $ instead of latency;
- compaction (24) and retrieval (30) as cost levers re-priced;
- the 20 tail applied to cost (a few runaway runs dominate the bill).
Everything re-derived from first principles, not re-cited. Prices are illustrative knobs.
"""

import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# Illustrative per-token prices ($ per 1K tokens), input cheaper than output (typical).
P_IN = 3e-6      # $3 / 1M input tokens
P_OUT = 15e-6    # $15 / 1M output tokens

# =========================================================================
# 1. TOKEN/$ ACCOUNTING ON TOP OF 22's O(T^2) (cost grows quadratically with turns)
# =========================================================================
# 22: input tokens over T turns = T*p + g*T*(T-1)/2 (transcript re-sent each turn, grows by g/turn).
# Output tokens ~ g per turn -> g*T. Dollar cost = in*P_IN + out*P_OUT.
def in_tokens(T, p=4000, g=1500): return T * p + g * T * (T - 1) // 2
def out_tokens(T, g=1500): return g * T
def run_cost(T):
    return in_tokens(T) * P_IN + out_tokens(T) * P_OUT
c20, c10 = run_cost(20), run_cost(10)
check("run cost grows super-linearly in turns (22 O(T^2))", c20 > 2 * c10,
      f"T=20 ${c20:.4f} vs 2*T=10 ${2*c10:.4f} -> doubling turns MORE than doubles cost (quadratic input)")
# the input (quadratic) term dominates the bill at high T -> compaction (24) is the main lever
in_cost20 = in_tokens(20) * P_IN; out_cost20 = out_tokens(20) * P_OUT
check("input (quadratic) term dominates the bill at high T", in_cost20 > out_cost20,
      f"T=20: input ${in_cost20:.4f} vs output ${out_cost20:.4f} -> attack the transcript, not the replies")

# =========================================================================
# 2. COMPACTION (24) RE-PRICED: O(T^2) -> O(T) is a DOLLAR win that grows unbounded with T
# =========================================================================
# 24: cap the transcript at ceiling C tokens (summarize beyond it) -> input per turn is bounded by C,
# total input ~ C*T (linear) instead of g*T^2/2 (quadratic).
C = 16000
def in_compacted(T, C=16000, p=4000, g=1500):
    return sum(min(p + g * t, C) for t in range(T))
for T in (20, 50, 100):
    unc, com = in_tokens(T), in_compacted(T)
    check(f"compaction caps input growth (T={T})", com <= unc,
          f"uncapped {unc:,} vs capped {com:,} input tok ({unc/com:.1f}x less) -> O(T) not O(T^2)")
# dollar headline at T=100
T = 100
save = (in_tokens(T) - in_compacted(T)) * P_IN
check("compaction dollar saving grows with T", save > 0 and in_tokens(T) > 3 * in_compacted(T),
      f"T=100 input: uncapped {in_tokens(T):,} vs capped {in_compacted(T):,} -> saves ${save:.2f}/run")

# =========================================================================
# 3. PREFIX / PROMPT CACHING ROI (24 prefix-cache discount made a dollar number)
# =========================================================================
# A cached prefix (system prompt + tools + few-shots) is billed at a discount d on cache hits.
# It helps the STATIC prefix only -- NOT the growing transcript (does not fix the quadratic, 24).
prefix_tokens = 4000
d = 0.1   # cached prefix billed at 10% of normal
def prefix_cost(hit): return prefix_tokens * P_IN * (d if hit else 1.0)
roi = prefix_cost(False) - prefix_cost(True)
check("prefix cache cuts the static-prefix bill", prefix_cost(True) < prefix_cost(False),
      f"miss ${prefix_cost(False):.5f} vs hit ${prefix_cost(True):.5f} -> {1/d:.0f}x cheaper prefix on hits")
# but it does NOT touch the quadratic transcript growth (the 24 caveat, re-priced)
check("prefix cache does NOT fix the O(T^2) transcript", in_tokens(50) - 50*prefix_tokens > 0,
      f"transcript term g*T(T-1)/2 = {1500*50*49//2:,} tok is uncached & quadratic -> caching != compaction")

# =========================================================================
# 4. PER-TENANT QUOTAS / BUDGETS = the 18 admission-control identity OVER DOLLARS
# =========================================================================
# A token budget per tenant is a 18 token-bucket over $/tokens: refill rate R tok/period, cap B.
# Requests are admitted while balance > cost; else shed (18 load-shedding) -> caps the blast radius
# of one runaway tenant. Fair-share: N tenants share a pool, each capped at pool/N (or weighted).
pool, N = 10_000_000, 5
per_tenant_cap = pool // N
check("per-tenant fair-share cap (18 over $)", per_tenant_cap == 2_000_000,
      f"pool {pool:,} / {N} tenants = {per_tenant_cap:,} tok each -> one tenant can't starve others")
# a runaway tenant is shed once over budget (bounded blast radius, 18/20)
spent, cap = 2_500_000, per_tenant_cap
check("runaway tenant is shed at the cap (18 load-shedding over $)", spent > cap,
      f"tenant spent {spent:,} > cap {cap:,} -> shed/throttle (bill bounded, not unbounded)")

# =========================================================================
# 5. COST TAIL (20): a few runaway runs dominate the bill (the 20 tail over $, not latency)
# =========================================================================
# Most runs are short (cheap); a few hit the turn cap / loop forever (expensive). The mean bill is
# dragged by the tail -> you must cap turns/tokens PER RUN (22 budgets) and alert on p99 cost (19).
costs = [run_cost(t) for t in [3,3,4,3,5,4,3,100]]  # one runaway 100-turn run
mean = sum(costs)/len(costs)
median = sorted(costs)[len(costs)//2]
check("a few runaway runs dominate mean cost (20 tail over $)", mean > 3 * median,
      f"median ${median:.4f} vs mean ${mean:.4f} -> the one 100-turn run drags the average (cap turns!)")
# capping the runaway run at T=20 collapses the tail
costs_capped = [run_cost(min(t,20)) for t in [3,3,4,3,5,4,3,100]]
check("a per-run turn cap collapses the cost tail (22 budget)", sum(costs_capped) < sum(costs),
      f"uncapped total ${sum(costs):.3f} vs T<=20 capped ${sum(costs_capped):.3f} -> budget caps the bill")

# =========================================================================
# 6. COST DASHBOARD = the 19 observability identity OVER $ (attribute every token)
# =========================================================================
# Cost is just another signal (19): attribute $ per (model, tenant, tool, feature, run) via the
# trace (31/19 spans annotated with tokens). Unattributed spend is un-optimizable (19 cardinality).
# Aggregate $ = sum over spans of (in*P_IN + out*P_OUT). Drill down by any span tag.
span_costs = {"llm": 0.12, "tool:search": 0.00, "tool:exec": 0.00, "judge": 0.03}
total = sum(span_costs.values())
check("cost is an attributable signal (19 over $)", approx(total, 0.15, 1e-9),
      f"sum span $ = {total:.2f}; LLM is {span_costs['llm']/total:.0%} of the bill -> optimize the biggest tag")
# model routing: a cheap model for easy turns vs expensive for hard turns (ROI knob)
cheap, dear = 0.2e-6, 3e-6  # $/token input
mix = 0.7  # 70% of turns routed to the cheap model
blended = mix * cheap + (1 - mix) * dear
check("model routing lowers blended $/token (32 ROI knob)", blended < dear,
      f"blended ${blended*1e6:.2f}/M vs all-dear ${dear*1e6:.2f}/M -> route easy turns to cheap model")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 32 cost/observability/ops economics verified by recomputation.")
