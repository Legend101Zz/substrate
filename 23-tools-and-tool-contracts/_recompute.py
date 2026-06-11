#!/usr/bin/env python3
"""
Substrate 23 - tools-and-tool-contracts: independent recomputation of every quantitative claim in
the section brief. Pure stdlib. Run: python3 _recompute.py

23 refines the "parse decision" + "act" boxes of the 22 loop. Its load-bearing arithmetic is the
COST of advertising/validating/incorporating tools: a big toolbox is a fixed per-turn prompt tax
(feeds the 22 quadratic), tool results must be size-bounded, repair retries must be capped, and
selection error compounds over loop steps via the same 1-(1-q)^N fan-out identity as 13/20/21.
"""
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-4): return abs(a - b) <= tol * max(1.0, abs(b))

# =========================================================================
# 1. TOOLBOX PROMPT COST: K tools * S tokens/schema, paid EVERY turn
# =========================================================================
K = 40          # tools advertised
S = 150         # tokens per tool schema
toolbox = K * S
check("toolbox prompt cost per turn", toolbox == 6000, f"K*S = {K}*{S} = {toolbox} tokens/turn just to advertise tools")
# Share of a 128k window consumed by the toolbox alone.
W = 128000
share = toolbox / W
check("toolbox window share", approx(share, 0.046875), f"{toolbox}/{W} = {share:.4%} of the window is static tool schemas")
# Over a T-turn task the toolbox is re-sent every turn (part of the 22 prefix p).
T = 20
toolbox_total = toolbox * T
check("toolbox tokens billed over task", toolbox_total == 120000, f"K*S*T = {toolbox}*{T} = {toolbox_total} input tokens just for tool ads")

# =========================================================================
# 2. RETRIEVAL-OVER-TOOLS BREAK-EVEN (advertise k of K; handoff to 30)
# =========================================================================
# Retrieve top-k relevant tools instead of all K. Saving = (K-k)*S tokens/turn,
# minus a retrieval overhead r tokens/turn (the query/embedding bookkeeping).
k = 5
r_overhead = 50
saving = (K - k) * S - r_overhead
check("retrieval-over-tools net saving/turn", saving == 5200, f"(K-k)*S - r = ({K}-{k})*{S} - {r_overhead} = {saving} tokens/turn saved")
# Break-even K: retrieval wins once (K-k)*S > r  ->  K > k + r/S.
breakeven_K = k + r_overhead / S
check("retrieval break-even toolbox size", approx(breakeven_K, 5.3333),
      f"K > k + r/S = {k} + {r_overhead}/{S} = {breakeven_K:.4f} -> retrieval wins for any non-trivial toolbox")

# =========================================================================
# 3. TOOL-RESULT SIZE BUDGET (oversized result blows the window)
# =========================================================================
# At turn t the prompt is p + (t-1)*g (22 model). A tool result of R tokens this turn
# must keep p + (t-1)*g + R <= W. Max R at turn t:
p = 8000        # prefix incl. the K*S toolbox above (2000 base + 6000 toolbox)
g = 500
def max_result(t): return W - (p + (t - 1) * g)
check("max tool-result tokens at turn 1", max_result(1) == 120000, f"W-p = {W}-{p} = {max_result(1)} tokens headroom")
check("max tool-result tokens at turn 20", max_result(20) == 110500, f"W-(p+19g) = {W}-{p+19*500} = {max_result(20)}")
# A 1 MB JSON result ~ 250k tokens (4 chars/token) does NOT fit -> must truncate/summarize.
big_result_tokens = 1_000_000 // 4
check("1MB result overflows", big_result_tokens > max_result(1), f"~{big_result_tokens} tokens > headroom {max_result(1)} -> must bound/summarize (24/25)")
trunc_ratio = max_result(20) / big_result_tokens
check("required truncation ratio at turn 20", approx(trunc_ratio, 0.442),
      f"keep <= {trunc_ratio:.1%} of a 1MB result to fit at turn 20")

# =========================================================================
# 4. REPAIR-RETRY BOUND (validation failures capped under step budget; reuse 18/22)
# =========================================================================
# Each malformed call costs one extra model call. Cap repairs at R_max so a model that
# cannot satisfy the schema can't loop forever.
R_max = 3
extra_calls_worst = R_max
check("repair-retry bound", R_max == 3, f"at most {R_max} re-prompts on validation failure, then abort/escalate (reuse 18 + 22 step budget)")
# Worst-case calls for one logical step that needs 1 success after R_max failures:
calls_one_step = R_max + 1
check("worst-case model calls per step", calls_one_step == 4, f"{R_max} repairs + 1 success = {calls_one_step} model calls worst case")

# =========================================================================
# 5. SELECTION-ERROR COMPOUNDING over N steps = 1-(1-q)^N  (same fan-out identity as 13/20/21)
# =========================================================================
q = 0.02   # per-call mis-selection probability
for N, expect in [(5, 0.09608), (10, 0.18293), (50, 0.63583)]:
    p_any_wrong = 1 - (1 - q) ** N
    check(f"P(>=1 wrong tool) over N={N} steps", approx(p_any_wrong, expect, tol=1e-3),
          f"1-(1-{q})^{N} = {p_any_wrong:.5f} -> long tasks NEED validation/repair (reuse 13/20/21 identity)")

# =========================================================================
# 6. IDEMPOTENCY-KEY RETENTION for side-effecting tools (reuse 17/21)
# =========================================================================
retry_horizon_s = 86400   # keep keys >= 24h max retry horizon
check("idempotency key retention", retry_horizon_s == 86400, f"keep keys {retry_horizon_s}s -> exactly-once-EFFECT for write tools (17/21)")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 23 tool-contract economics verified by recomputation.")
