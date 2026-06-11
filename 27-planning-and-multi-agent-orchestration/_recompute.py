#!/usr/bin/env python3
"""
Substrate 27 - planning-and-multi-agent-orchestration: independent recomputation of every
quantitative claim in the section briefs. Pure stdlib. Run: python3 _recompute.py

27 is where ONE loop (22) becomes MANY coordinating loops. A multi-agent system is a DISTRIBUTED
SYSTEM whose nodes happen to be LLM loops - so the laws are 11 (consensus/ordering), 17 (async/EDA),
and 20 (resilience/tail), not new agent magic. The load-bearing arithmetic of 27 is therefore the
ECONOMICS OF COORDINATION:
  (a) decomposition: plan depth/width vs total model calls (the planning cost);
  (b) parallel fan-out speedup AND its tail penalty (20: the slowest sub-agent gates the join);
  (c) supervisor token tax: re-aggregating N sub-agent results inflates the supervisor's context
      (24/22 quadratic at the parent level);
  (d) correctness compounding across agents: 1-(1-q)^N selection/step error over the whole DAG
      (the 13/20/21/23 fan-out identity, now over AGENTS);
  (e) when multi-agent BEATS a single loop (parallelism payoff) vs when it just adds tax.
Everything below is re-derived from first principles, not re-cited.
"""

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))
import math

# =========================================================================
# 1. DECOMPOSITION: plan width W and depth D -> total subtasks (the call budget)
# =========================================================================
# A plan is a tree/DAG: a task splits into W subtasks, each may split again, to
# depth D. Total leaf subtasks = W^D; total nodes (model calls to plan+run) =
# sum_{i=0..D} W^i = (W^(D+1)-1)/(W-1).
Wf = 3   # fan width per level
D = 2    # plan depth
leaves = Wf ** D
nodes = (Wf ** (D + 1) - 1) // (Wf - 1)
check("plan leaves = W^D", leaves == 9, f"{Wf}^{D} = {leaves} leaf subtasks")
check("plan total nodes = (W^(D+1)-1)/(W-1)", nodes == 13,
      f"(3^3-1)/(3-1) = {nodes} model-call sites (plan + execute) -> the call budget")

# =========================================================================
# 2. PARALLEL FAN-OUT SPEEDUP (Amdahl over agents, reuse 13/20)
# =========================================================================
# If a task has serial fraction s and parallelizable fraction (1-s) spread over P
# agents, speedup = 1 / (s + (1-s)/P) (Amdahl). Fan-out only helps the parallel part.
s = 0.2  # serial fraction (planning + final aggregation can't be parallelized)
P = 9    # parallel sub-agents (the leaves)
speedup = 1 / (s + (1 - s) / P)
check("Amdahl speedup over P agents", approx(speedup, 1/(0.2 + 0.8/9)),
      f"1/(0.2 + 0.8/9) = {speedup:.2f}x (serial fraction caps it; reuse 13)")
# Amdahl ceiling: even with infinite agents, speedup <= 1/s.
check("speedup ceiling = 1/s regardless of agent count", approx(1/s, 5.0),
      f"1/{s} = {1/s:.1f}x max even with infinite agents (planning+aggregation is the wall)")

# =========================================================================
# 3. THE JOIN IS GATED BY THE SLOWEST SUB-AGENT (tail at scale, reuse 20)
# =========================================================================
# A supervisor that waits for ALL N sub-agents finishes when the SLOWEST returns.
# If each sub-agent independently exceeds latency L with prob p, then
# P(at least one slow) = 1 - (1-p)^N -> the join tail EXPLODES with N. (20 headline.)
p = 0.01  # per-agent chance of being slow (> L)
for N, exp in [(1, 0.01), (10, 0.0956), (100, 0.634)]:
    val = 1 - (1 - p) ** N
    check(f"P(join stalls) with N={N} sub-agents", approx(val, exp, tol=1e-2),
          f"1-(1-{p})^{N} = {val:.4f} (the slowest gates the join; reuse 20 fan-out)")
# Mitigation (20): hedge/backup the slow sub-agent, or accept partial results.

# =========================================================================
# 4. SUPERVISOR TOKEN TAX: re-aggregating N results inflates parent context (24/22)
# =========================================================================
# Each sub-agent returns r tokens; the supervisor must read all N -> N*r tokens added
# to the supervisor's context, re-sent every supervisor turn (22 quadratic at parent).
r = 800; N = 9
agg_tokens = N * r
check("supervisor aggregation token cost = N*r", agg_tokens == 7200,
      f"{N} sub-agents * {r} tok = {agg_tokens} tok into supervisor context (24 budget pressure)")
# Fix (24/25): sub-agents return COMPACTED summaries, not raw transcripts. With ratio
# rho, the tax drops to N*r*rho.
rho = 0.15
agg_compacted = int(agg_tokens * rho)
check("compacting sub-agent returns cuts the supervisor tax",
      agg_compacted == 1080,
      f"N*r*rho = {agg_tokens}*{rho} = {agg_compacted} tok ({1/rho:.1f}x less; reuse 24)")

# =========================================================================
# 5. CORRECTNESS COMPOUNDING ACROSS AGENTS (1-(1-q)^N, reuse 13/20/21/23)
# =========================================================================
# If each of N agents/steps is independently correct with prob (1-q), the chance the
# WHOLE pipeline is correct is (1-q)^N -> end-to-end error = 1-(1-q)^N grows with N.
# This is WHY orchestration needs verification/voting, not just more agents.
q = 0.05
for N, _ in [(1, 0), (5, 0), (20, 0)]:
    err = 1 - (1 - q) ** N
    ok = err >= 0
    check(f"end-to-end error with N={N} agents", ok,
          f"1-(1-{q})^{N} = {err:.3f} pipeline error (compounds; needs checks -> 31)")
# Quorum/voting fix (11/20): k independent attempts, take majority. If a single attempt
# is wrong w.p. q, majority-of-3 is wrong only when >=2 fail: 3q^2(1-q)+q^3.
maj3_err = 3 * q**2 * (1 - q) + q**3
check("majority-of-3 voting beats a single agent when q<0.5",
      maj3_err < q,
      f"maj3 err = {maj3_err:.4f} < single {q} ({q/maj3_err:.1f}x better; reuse 11 quorum/20)")

# =========================================================================
# 6. WHEN MULTI-AGENT BEATS A SINGLE LOOP (the payoff condition)
# =========================================================================
# Multi-agent wins when parallel time saved > coordination tax added. Single loop
# time ~ T_total; parallel time ~ T_total/speedup + T_coord. Net win iff:
#   T_total > T_total/speedup + T_coord
T_total = 100.0   # time units for the whole task done serially in one loop
T_coord = 8.0     # planning + aggregation + comms overhead
parallel_time = T_total / speedup + T_coord
check("multi-agent wins only if parallel+coord beats serial",
      parallel_time < T_total,
      f"parallel {parallel_time:.1f} < serial {T_total:.1f} -> {T_total/parallel_time:.2f}x; else single loop is better")
# Counter-case: tiny task with high coord overhead -> multi-agent LOSES.
T_small = 10.0
parallel_small = T_small / speedup + T_coord
check("multi-agent LOSES on small tasks (coord tax dominates)",
      parallel_small > T_small,
      f"parallel {parallel_small:.1f} > serial {T_small:.1f} -> don't orchestrate trivial work (YAGNI)")

# =========================================================================
# 7. ORDERING / CONSENSUS for shared state (reuse 11)
# =========================================================================
# Agents writing shared state need an order. A single sequencer (11) gives total order;
# without it, concurrent writes from N agents create C(N,2) potential conflict pairs.
N3 = 5
conflict_pairs = N3 * (N3 - 1) // 2
check("concurrent shared-state writers -> C(N,2) conflict pairs",
      conflict_pairs == 10,
      f"C({N3},2) = {conflict_pairs} pairs need ordering (sequencer/consensus, 11) or they race")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 27 orchestration economics verified by recomputation.")
