#!/usr/bin/env python3
"""
Substrate 31 - evaluation-tracing-and-guardrails: independent recomputation of every quantitative
claim in the eval/tracing/guardrails brief. Pure stdlib. Run: python3 _recompute.py

31 introduces NO new load-bearing primary mechanism of its own beyond what is already VERIFIED:
- execution-based evaluation + "% resolved" is VERIFIED against SWE-bench (Jimenez/Yang 2024,
  arXiv 2310.06770) -> receipt meta/fetched_primaries/_VERIFIED_2026-06-10_swe-bench.md;
- distributed tracing (spans/trace-tree/sampling) is VERIFIED against Dapper (2010) in 19;
- LLM-as-judge voting reuses the 27 Condorcet/majority-of-3 identity;
- guardrails reuse the 18 validation + defence-in-depth identity.
So 31's quantitative claims are: (a) how many golden tasks you need to TRUST a pass rate
(binomial CI), (b) nondeterminism: pass@k vs pass^k, (c) judge ensemble beats single judge
(27 reused over judges), (d) tracing spans/run + Dapper sampling RSE (19 reused over loop steps),
(e) defence-in-depth guardrail escape 1-(1-c)^L (18 reused), (f) lexical-similarity is NOT
correctness (SWE-bench), (g) eval is expensive because each task is a full O(T^2) loop (22).
Everything re-derived from first principles, not re-cited.
"""

import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# =========================================================================
# 1. HOW MANY GOLDEN TASKS TO TRUST A PASS RATE (binomial confidence)
# =========================================================================
# A measured pass rate p_hat over N independent golden tasks has standard error
# SE = sqrt(p(1-p)/N). The 95% CI half-width ~ 1.96*SE. Small N -> wide, untrustworthy interval.
def se(p, N): return math.sqrt(p * (1 - p) / N)
def ci95(p, N): return 1.96 * se(p, N)
for N, exp in [(10, 0.3098), (100, 0.0980), (1000, 0.0310)]:
    w = ci95(0.5, N)
    check(f"95% CI half-width at N={N} (p=0.5)", approx(w, exp, 2e-3),
          f"+-{w:.4f} -> N=10 is +-31% (useless), N=1000 is +-3% (trustworthy)")
# To pin a pass rate to +-3% at p=0.5 you need ~1067 tasks (the 19 'measurement precision' lesson).
N_needed = (1.96**2 * 0.25) / (0.03**2)
check("tasks needed for +-3% precision at p=0.5", 1000 < N_needed < 1100,
      f"N = 1.96^2*0.25/0.03^2 = {N_needed:.0f} golden tasks (precision costs sample size)")

# =========================================================================
# 2. NONDETERMINISM: pass@k (lenient) vs pass^k (strict) -- a STOCHASTIC agent is not binary
# =========================================================================
# A flaky agent passes a task with prob p each run. Over k independent attempts:
#   pass@k  = P(at least one success) = 1 - (1-p)^k      (lenient: best-of-k)
#   pass^k  = P(all k succeed)        = p^k              (strict: reliability under repetition)
p = 0.6
def pass_at_k(p, k): return 1 - (1 - p) ** k
def pass_pow_k(p, k): return p ** k
check("pass@k rises with retries (lenient)", approx(pass_at_k(p, 3), 0.936, 1e-3),
      f"1-(1-0.6)^3 = {pass_at_k(p,3):.3f} (best-of-3 looks great)")
check("pass^k falls with retries (strict)", approx(pass_pow_k(p, 3), 0.216, 1e-3),
      f"0.6^3 = {pass_pow_k(p,3):.3f} (reliability under repetition is BRUTAL)")
check("a single run of a stochastic agent is an unreliable verdict", pass_at_k(p,3) - pass_pow_k(p,3) > 0.7,
      f"same agent: best-of-3={pass_at_k(p,3):.3f} vs all-3={pass_pow_k(p,3):.3f} -> must repeat + report which metric")

# =========================================================================
# 3. LLM-AS-JUDGE: a VOTING ENSEMBLE beats a single judge (the 27 Condorcet identity, reused over JUDGES)
# =========================================================================
# A single judge is correct with prob a (a>0.5). Majority-of-3 independent judges is correct with
# a^3 + 3*a^2*(1-a). This is exactly 27's majority-of-3 voting, now applied to GRADERS not workers.
def maj3(a): return a**3 + 3 * a**2 * (1 - a)
for a in (0.7, 0.8, 0.9):
    m = maj3(a)
    check(f"majority-of-3 judges beats single judge (a={a})", m > a,
          f"single {a} -> maj3 {m:.4f} (judge error {1-a:.2f} -> {1-m:.4f}, {(1-a)/(1-m):.1f}x fewer)")
# headline: a=0.8 judge error 0.20 -> majority-of-3 error 0.104 (1.9x fewer); below 0.5 it BACKFIRES
check("voting backfires for a worse-than-coin judge (a<0.5)", maj3(0.4) < 0.4,
      f"a=0.4 -> maj3 {maj3(0.4):.3f} < 0.4 (Condorcet: only helps if each judge > 0.5)")

# =========================================================================
# 4. TRACING = Dapper SPANS over agent steps/tool calls (19 reused over the 22 loop)
# =========================================================================
# One agent run of T turns, each making m tool calls, emits a trace tree: 1 root + T step spans +
# T*m tool spans. The trace tree is the agent loop made observable (Dapper span/trace model, 19).
T, m = 12, 3
spans_per_run = 1 + T + T * m
check("spans per agent run (root + steps + tool calls)", spans_per_run == 1 + 12 + 36,
      f"1 + T + T*m = 1 + {T} + {T*m} = {spans_per_run} spans (the loop becomes a Dapper trace tree)")
# Dapper sampling: at sample rate s, the relative standard error of a measured rate over n_events is
# RSE ~ sqrt((1-s)/(s*n_events)) (19's sampling-precision lesson). Low traffic -> sample MORE.
def rse(s, n): return math.sqrt((1 - s) / (s * n))
check("trace sampling RSE shrinks with volume (19)", rse(0.001, 1_000_000) < rse(0.001, 1000),
      f"s=0.1%: RSE@1e6={rse(0.001,1e6):.3f} vs @1e3={rse(0.001,1e3):.3f} (rare bugs need higher s)")

# =========================================================================
# 5. GUARDRAILS = DEFENCE-IN-DEPTH validation (the 18 identity, reused over guardrail layers)
# =========================================================================
# Each independent guardrail layer (schema validation 23, policy filter 18, output checker, safety
# filter 33) catches a bad output with prob c. L layers in series let through (1-c)^L. Adding layers
# cuts ESCAPE multiplicatively -- but each adds false-positive (over-refusal) cost.
c, L = 0.8, 3
def escape(c, L): return (1 - c) ** L
check("defence-in-depth escape falls multiplicatively (18)", approx(escape(c, L), 0.008, 1e-9),
      f"(1-0.8)^3 = {escape(c,L):.3f} -> 3 layers @80% leave 0.8% escape (vs 20% for one)")
# false-positive tax: each layer with FP rate f rejects a GOOD output with prob 1-(1-f)^L
f = 0.02
fp_total = 1 - (1 - f) ** L
check("guardrail false-positive (over-refusal) tax compounds too", approx(fp_total, 0.058808, 1e-6),
      f"1-(1-0.02)^3 = {fp_total:.4f} -> stacking guardrails over-refuses ~5.9% of good outputs")

# =========================================================================
# 6. LEXICAL SIMILARITY IS NOT CORRECTNESS (SWE-bench: execution decides, % resolved)
# =========================================================================
# A patch can share most tokens with the golden patch yet FAIL the tests (wrong line), while a
# textually different patch PASSES. Correctness is binary under execution (tests go red->green),
# not a similarity score. VERIFIED SWE-bench: "all of these tests pass -> resolved".
token_overlap_A, tests_pass_A = 0.95, False   # looks right, broken
token_overlap_B, tests_pass_B = 0.40, True    # looks different, correct
resolved_A = 1.0 if tests_pass_A else 0.0
resolved_B = 1.0 if tests_pass_B else 0.0
check("high lexical overlap can still be WRONG", token_overlap_A > token_overlap_B and resolved_A < resolved_B,
      f"A: overlap {token_overlap_A} resolved {resolved_A}; B: overlap {token_overlap_B} resolved {resolved_B} (execution, not BLEU)")
# the benchmark metric is a mean of binary resolutions, not a mean of similarity
resolutions = [1, 0, 0, 1, 0]
pct_resolved = sum(resolutions) / len(resolutions)
check("metric = % resolved (binary aggregate), SWE-bench", approx(pct_resolved, 0.4, 1e-9),
      f"mean([1,0,0,1,0]) = {pct_resolved:.2f} resolved (Claude-2 baseline on full set was 1.96%)")

# =========================================================================
# 7. EVAL IS EXPENSIVE: each golden task is a full O(T^2) loop (22) -> subset/sample, don't run all
# =========================================================================
# Running a suite of S tasks, each a T-turn loop, costs sum of the 22 quadratic token total per task.
# This is why eval is gated/sampled in CI (you can't run 2,294 full agent loops per commit cheaply).
def loop_tokens(T, prefix=4000, g=1500): return T * prefix + g * T * (T - 1) // 2
S = 2294
per_task = loop_tokens(20)
suite = S * per_task
check("full suite cost = S * per-task O(T^2) (22)", suite == 2294 * loop_tokens(20),
      f"{S} tasks * {per_task:,} tok/task = {suite:,} tok -> eval is a budget line item (->32), gate/sample it")
check("per-task token cost is quadratic in turns (22 carried)", loop_tokens(40) > 3 * loop_tokens(20),
      f"T=40 costs {loop_tokens(40):,} vs T=20 {loop_tokens(20):,} (>3x for 2x turns -> cap eval turns)")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 31 eval/tracing/guardrails math verified by recomputation.")
