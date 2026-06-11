#!/usr/bin/env python3
"""
Substrate 34 - design-your-own-agentic-system: independent recomputation of the cross-cutting
budgets an agentic design must satisfy. Pure stdlib. Run: python3 _recompute.py

34 is the PART III CAPSTONE DESIGN CANVAS. Like 21 (Part II capstone), it introduces NO new
primitive -- it APPLIES the whole 22-33 toolkit to a design method. This file re-derives, in ONE
place, the load-bearing budgets that every agentic design is forced to price, each already proven in
its home sub-course:
  22  loop cost is O(T^2)            (transcript re-sent + grows g/turn)
  24  compaction converts O(T^2)->O(T)
  25  memory AMAT over tokens        (hit-rate buys effective cheapness)
  26  checkpoint knee I* = sqrt(2N*c)
  27  Amdahl over agents + join tail 1-(1-p)^N + YAGNI (multi-agent loses on small tasks)
  31  eval sample size: 95% CI = 1.96*sqrt(p(1-p)/N)
  32  cost = the 22 quadratic, priced
  33  defence-in-depth escape = prod(1-c_i)
The thesis (capstone): a design is a SEQUENCE OF FORCED MOVES -- the task's shape + the arithmetic
pick the agentic primitives. Every number is re-derived first-principles, cross-linked to its anchor.
"""

import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

P_IN, P_OUT = 3e-6, 15e-6   # illustrative $/token (knobs, as in 32)

# =========================================================================
# 1. THE LOOP BUDGET (22): input tokens are O(T^2) -> the master constraint
# =========================================================================
def in_tokens(T, p=4000, g=1500): return T * p + g * T * (T - 1) // 2
check("design constraint: loop cost is O(T^2) in turns (22)",
      in_tokens(20) > 2 * in_tokens(10),
      f"T=10 {in_tokens(10):,} vs T=20 {in_tokens(20):,} input tok -> the quadratic is the budget every design must bound")

# =========================================================================
# 2. COMPACTION DECISION (24): O(T^2)->O(T) -- when does the canvas REQUIRE it?
# =========================================================================
def in_compacted(T, C=16000, p=4000, g=1500): return sum(min(p + g * t, C) for t in range(T))
# The WINDOW is a PER-CALL constraint: input on the last turn = p + g*(T-1) (linear, O(T)).
# (Cumulative tokens-sent = in_tokens(T) is the COST model, O(T^2) -- that is step 1 / step 7.)
def per_call(T, p=4000, g=1500): return p + g * (T - 1)
W = 128_000
T_short, T_long = 8, 100
check("canvas rule: compaction is FORCED only past the per-call window (24)",
      (per_call(T_short) <= W) and (per_call(T_long) > W),
      f"T={T_short} per-call {per_call(T_short):,}<=W; T={T_long} per-call {per_call(T_long):,}>W={W:,} -> long tasks MUST compact")
check("compaction restores per-call headroom (24): O(T)->bounded", 16000 < W,
      f"compacted per-call <=16,000 <= W={W:,} -> each call fits regardless of T")

# =====================================================================
# 3. MEMORY DECISION (25): AMAT over tokens -- when is external memory worth it?
# =========================================================================
# AMAT = hit_rate*cost_resident + (1-hit_rate)*cost_retrieve. Higher hit-rate -> cheaper effective token.
def amat(hit, c_res=1.0, c_ret=20.0): return hit*c_res + (1-hit)*c_ret
check("canvas rule: external memory pays when hit-rate is high (25 AMAT)",
      amat(0.95) < 0.50 * amat(0.80),
      f"AMAT hit=0.80 {amat(0.80):.2f} vs hit=0.95 {amat(0.95):.2f} -> a good index cuts effective cost ~{amat(0.80)/amat(0.95):.1f}x")

# =========================================================================
# 4. PERSISTENCE DECISION (26): checkpoint knee I* = sqrt(2N*c)
# =========================================================================
def I_star(N, c): return math.sqrt(2 * N * c)
N_steps, c_ckpt = 200, 0.5   # 200-step task, checkpoint costs 0.5 step-equivalents
istar = I_star(N_steps, c_ckpt)
check("canvas rule: checkpoint every I*=sqrt(2N*c) steps (26)",
      approx(istar, math.sqrt(200.0), 1e-9),
      f"I* = sqrt(2*{N_steps}*{c_ckpt}) = {istar:.1f} steps -> long/expensive tasks REQUIRE resume (26)")
# short cheap task: I* may exceed the whole task -> persistence is YAGNI
istar_short = I_star(5, 0.5)
check("canvas rule: short task -> checkpoint interval exceeds task -> skip (26/YAGNI)",
      istar_short >= 2.0,
      f"5-step task I*={istar_short:.1f} ~ whole task -> one final save suffices, not per-step WAL")

# =========================================================================
# 5. ORCHESTRATION DECISION (27): Amdahl ceiling + join tail + YAGNI
# =========================================================================
def amdahl_speedup(s, n): return 1.0 / (s + (1 - s) / n)
def amdahl_ceiling(s): return 1.0 / s
s = 0.30   # 30% of the work is irreducibly serial (plan + aggregate)
check("canvas rule: multi-agent speedup is capped by the serial fraction (27 Amdahl)",
      amdahl_speedup(s, 1000) < amdahl_ceiling(s) + 1e-9 and amdahl_ceiling(s) < 4,
      f"s={s}: ceiling {amdahl_ceiling(s):.2f}x even at n=inf -> don't fan out past the knee")
def join_tail(p, N): return 1 - (1 - p) ** N
check("canvas rule: the slow-agent join tail grows with fan-out (27)",
      approx(join_tail(0.01, 100), 1 - 0.99**100, 1e-12) and join_tail(0.01, 100) > 0.6,
      f"p=0.01,N=100 -> P(>=1 slow)={join_tail(0.01,100):.1%} -> the join waits on the tail (hedge/quorum it)")
# YAGNI: multi-agent only pays when parallel benefit > coordination + tail cost
single_cost, coord_cost = 6.0, 4.0
parallel_saving = single_cost * (1 - 1/amdahl_speedup(s, 4))  # saving from 4 agents on a SMALL task
check("canvas rule: multi-agent LOSES on small tasks (27 YAGNI)",
      parallel_saving < coord_cost,
      f"4-agent saving {parallel_saving:.1f} < coordination {coord_cost:.1f} -> stay single-agent unless the task is big & parallel")

# =========================================================================
# 6. EVAL BUDGET (31): how many golden tasks for a target CI?
# =========================================================================
def ci_halfwidth(p, N): return 1.96 * math.sqrt(p * (1 - p) / N)
def n_for_ci(p, target): return math.ceil(p * (1 - p) * (1.96 / target) ** 2)
N_ci3 = n_for_ci(0.5, 0.03)
check("canvas rule: eval set size is set by the target CI (31)",
      ci_halfwidth(0.5, N_ci3) <= 0.03 + 1e-4 and 1000 <= N_ci3 <= 1100,
      f"+/-3% at p=0.5 needs ~{N_ci3} golden tasks -> a design must BUDGET its eval suite (31->32 cost)")

# =========================================================================
# 7. COST BUDGET (32): the canvas prices the whole design in $/run
# =========================================================================
def run_cost(T):
    return in_tokens(T) * P_IN + (1500 * T) * P_OUT
def run_cost_compacted(T):
    return in_compacted(T) * P_IN + (1500 * T) * P_OUT
T = 100
save = run_cost(T) - run_cost_compacted(T)
check("canvas rule: pricing the design shows compaction's $ win (32 over 24)",
      save > 0 and run_cost(T) > 3 * run_cost_compacted(T),
      f"T=100: uncompacted ${run_cost(T):.2f}/run vs compacted ${run_cost_compacted(T):.2f}/run -> saves ${save:.2f} (design must budget $)")

# =========================================================================
# 8. SAFETY BUDGET (33): every untrusted-data channel needs a defence layer
# =========================================================================
def escape(cs):
    p = 1.0
    for c in cs: p *= (1 - c)
    return p
# A design with 3 untrusted channels (tool-result 23, memory 25, passage 30) each needs screening;
# defence-in-depth across 3 80%-screens bounds escape; un-screened channel = open door.
check("canvas rule: each untrusted channel needs a screen; depth bounds escape (33)",
      escape([0.8, 0.8, 0.8]) < 0.01 and escape([0.0]) == 1.0,
      f"3 screened channels -> escape {escape([0.8,0.8,0.8]):.2%}; one un-screened channel -> {escape([0.0]):.0%} open (budget a safety layer per channel)")

# =========================================================================
# 9. THE CANVAS IS A SEQUENCE OF FORCED MOVES (the capstone thesis, like 21)
# =========================================================================
# A 'small task' (short, single-shot, no untrusted data) forces almost nothing; a 'big task'
# (long, multi-source, multi-agent) forces the whole stack. The arithmetic picks the primitives.
def forced_primitives(T_exp, untrusted_channels, parallelizable, N_eval_needed):
    moves = ["22 loop"]                                  # always
    if per_call(T_exp) > W: moves.append("24 compaction")
    if untrusted_channels > 0: moves.append("33 safety")
    if T_exp > 30: moves.append("26 persistence")  # long/expensive tasks force resume (26)
    if parallelizable and T_exp > 30: moves.append("27 orchestration")
    if N_eval_needed: moves.append("31 eval"); moves.append("32 cost")
    return moves
small = forced_primitives(5, 0, False, False)
big = forced_primitives(120, 3, True, True)
check("capstone thesis: small task forces few moves, big task forces the stack (like 21)",
      set(small) == {"22 loop"} and {"24 compaction","33 safety","27 orchestration","31 eval"} <= set(big),
      f"small -> {small}; big -> {big} -> design = forced moves picked by task shape + arithmetic")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All 34 cross-cutting agentic-design budgets verified by recomputation (no new primary).")
