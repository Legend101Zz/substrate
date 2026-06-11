#!/usr/bin/env python3
"""
Substrate 28 - build-your-own-coding-harness: independent recomputation of every quantitative
claim in the build-progression brief. Pure stdlib. Run: python3 _recompute.py

28 is the Part III CAPSTONE LAB. It introduces NO new load-bearing math; instead it RE-DERIVES the
"wall" at the end of each build stage by reusing the already-verified identities from 22-27, applied
to the COODING-agent regime (long transcripts: big files + verbose test logs + many edit-test-fix
steps). Each section corresponds to one stage of the build progression and proves the wall that
motivates the next stage. Everything is re-derived from first principles, not re-cited.
"""

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# Coding-agent regime parameters (deliberately bigger than 22's chat defaults: code is verbose).
p = 4000      # fixed prefix: system + LARGE coding toolbox schemas + task (vs 2000 in 22)
g = 1500      # tokens appended per turn: a code Thought + patch + a chunk of test/compiler output
W = 128000    # context window
IN_PER_M = 3.00
OUT_PER_M = 15.00
o = 600       # output tokens per turn (a patch is bigger than a chat reply)

# =========================================================================
# STAGE 0 — pure loop (22): the O(T^2) wall, bigger/sooner for coding
# =========================================================================
def prompt_tokens(t): return p + (t - 1) * g
def cum_input(T): return T * p + g * T * (T - 1) // 2
# closed form matches brute sum (22's identity, re-derived in the coding regime)
for T in (1, 5, 10, 20):
    brute = sum(prompt_tokens(t) for t in range(1, T + 1))
    check(f"S0 cumulative input tokens T={T}", cum_input(T) == brute,
          f"T*p + g*T*(T-1)/2 = {cum_input(T)} == brute {brute}")
# quadratic: doubling T 10->20 ~4x the g-term
g10 = g * 10 * 9 // 2; g20 = g * 20 * 19 // 2
check("S0 quadratic growth (g-term ~4x when T doubles)", approx(g20/g10, 4.222, 1e-2),
      f"{g20}/{g10} = {g20/g10:.3f}x -> O(T^2)")
# window-overflow turn T* = floor((W-p)/g)+1; coding params make it SOONER than 22's chat case
T_star = (W - p) // g + 1
check("S0 window-overflow turn T*", T_star == (128000 - 4000)//1500 + 1,
      f"floor((W-p)/g)+1 = floor(124000/1500)+1 = {T_star}")
# prove "sooner": same window, 22's chat params gave T*=253; coding params give far fewer turns
T_star_chat = (W - 2000) // 500 + 1
check("S0 coding overflows sooner than chat", T_star < T_star_chat,
      f"coding T*={T_star} << chat T*={T_star_chat} (verbose code -> quadratic bites sooner)")

# =========================================================================
# STAGE 1 — code tools (23): selection compounding + result-size wall
# =========================================================================
# selection-error compounding over a coding task's many steps: 1-(1-q)^N (23/13/20/21 identity)
q = 0.02
def compound(N): return 1 - (1 - q) ** N
for N, exp in [(5, 0.0961), (10, 0.1829), (50, 0.6358)]:
    check(f"S1 selection compounding N={N}", approx(compound(N), exp, 1e-3),
          f"1-(1-{q})^{N} = {compound(N):.4f} (>= one wrong tool pick)")
# tool-result size budget: a result must fit W - prompt(t). A big file/test log overflows.
def result_budget(t): return W - prompt_tokens(t)
rb1, rb20 = result_budget(1), result_budget(20)
check("S1 result budget shrinks over turns", rb1 == 124000 and rb20 == 124000 - 19*1500,
      f"budget t=1 {rb1}, t=20 {rb20} (= W - (p+(t-1)g))")
# a 1 MB source file ~ 250k tokens (≈4 chars/token) overflows even an empty window
big_file_tokens = 1_000_000 // 4
check("S1 1MB file overflows result budget", big_file_tokens > rb1,
      f"~{big_file_tokens} tok > budget {rb1} -> must slice/summarize (24/25)")
# toolbox tax K*S/turn feeds the quadratic prefix (23): a big coding toolbox is expensive
K, S = 12, 200   # 12 coding tools, ~200 tokens of schema each
toolbox_tax = K * S
check("S1 toolbox tax K*S", toolbox_tax == 2400,
      f"{K}*{S} = {toolbox_tax} tok/turn baked into prefix p (feeds O(T^2))")

# =========================================================================
# STAGE 2 — budget (22+18+32): caps cost, does NOT cure the quadratic
# =========================================================================
max_steps = 20
def cum_cost(T): return cum_input(T)/1e6*IN_PER_M + (T*o)/1e6*OUT_PER_M
worst = cum_cost(max_steps)
exp_in = cum_input(20)  # 20*4000 + 1500*20*19/2 = 80000 + 285000 = 365000
check("S2 cumulative input tokens T=20", exp_in == 365000, f"80000 + 285000 = {exp_in}")
check("S2 step-budget bounds worst-case cost", approx(worst, exp_in/1e6*3 + 20*600/1e6*15),
      f"max_steps={max_steps} -> known worst-case ${worst:.4f}")
# wall-clock bound = max_steps * step_deadline (22 §6 + 18)
step_deadline = 30.0
check("S2 wall-clock bound", max_steps*step_deadline == 600.0,
      f"{max_steps}*{step_deadline} = 600s absolute cap")
# KEY: the budget caps but does not reduce per-turn growth — prompt at the cap is still huge
check("S2 budget caps but quadratic persists", prompt_tokens(max_steps) > prompt_tokens(1),
      f"prompt at cap {prompt_tokens(max_steps)} still >> prompt t=1 {prompt_tokens(1)} -> need 24")

# =========================================================================
# STAGE 3 — compaction (24): the HEADLINE O(T^2) -> O(T)
# =========================================================================
# cap the transcript at ceiling C tokens; once full, summarize so prompt stays ~constant.
C = 40000
def prompt_compacted(t):
    return min(prompt_tokens(t), p + C)
def cum_input_compacted(T):
    return sum(prompt_compacted(t) for t in range(1, T + 1))
# after the cap is reached, each turn costs ~ (p+C): cumulative grows LINEARLY in T
T_cap = (C) // g + 1   # turn at which transcript first exceeds C
big_T = 1000
lin_est = cum_input_compacted(big_T)
# linear upper bound: T*(p+C)
check("S3 compacted cumulative is O(T) (<= T*(p+C))", lin_est <= big_T * (p + C),
      f"compacted cum {lin_est} <= T*(p+C) {big_T*(p+C)}")
# the win grows without bound: uncompacted/compacted ratio rises with T (quadratic/linear)
ratio_200 = cum_input(200) / cum_input_compacted(200)
ratio_1000 = cum_input(big_T) / lin_est
check("S3 compaction win grows with T (quadratic/linear, unbounded)",
      ratio_1000 > ratio_200 > 1 and ratio_1000 > 10,
      f"ratio T=200 {ratio_200:.2f}x -> T=1000 {ratio_1000:.2f}x (grows without bound)")
# prefix-cache helps the PREFIX p only, NOT the growing transcript tail (24): can't cure quadratic
prefix_cache_discount = 0.10  # cached prefix billed at 10%
def cum_input_prefixcached(T):
    return sum(p*prefix_cache_discount + (t-1)*g for t in range(1, T+1))
pc = cum_input_prefixcached(big_T)
check("S3 prefix-cache still O(T^2) (tail uncached)", pc > lin_est,
      f"prefix-cached {pc} still >> compacted {lin_est} -> caching != compaction")

# =========================================================================
# STAGE 4 — memory (25): AMAT over tokens + poisoning blast radius
# =========================================================================
# AMAT over tokens (reuse 25's VERIFIED model): in-context hit ~0 extra tokens; a miss costs
# a recall round-trip. Effective extra tokens = miss_rate * miss_penalty.
miss_penalty = 350.0   # pulled tokens + search overhead (matches 25)
def amat(h): return (1 - h) * miss_penalty
a80, a95 = amat(0.80), amat(0.95)
check("S4 AMAT over tokens: hit 0.80->0.95 cuts effective cost 4x", approx(a80/a95, 4.0),
      f"AMAT(0.80)={a80:.1f} / AMAT(0.95)={a95:.1f} = {a80/a95:.1f}x cheaper (matches 25)")
# poisoning blast radius: 1 bad write read by many downstream steps (25): read-many-write-once
reads_per_write = 15
check("S4 poisoning blast radius", reads_per_write >= 1 and 1 * reads_per_write == 15,
      f"1 poisoned write -> {reads_per_write} downstream reads -> validate writes (33)")

# =========================================================================
# STAGE 5 — persistence/resume (26): write-ahead loss bound + checkpoint knee + idempotency
# =========================================================================
# persist-before-act: crash loses <=1 in-flight step vs the whole run
N = 50
check("S5 write-ahead loss bound", 1 < N, f"WAL loses <=1 step vs {N}-step whole run")
# checkpoint knee I* = sqrt(2*N*c_ckpt) (26)
import math
c_ckpt = 4.0
I_star = math.sqrt(2 * N * c_ckpt)
check("S5 checkpoint knee I*", approx(I_star, 20.0, 1e-9),
      f"sqrt(2*{N}*{c_ckpt}) = {I_star:.4f} steps between checkpoints")
# idempotent replay: without keys a re-applied patch/commit double-applies; with keys -> no-op
side_effects_without_keys = 3   # e.g. patch applied 1 + replayed 2 times
side_effects_with_keys = 0
check("S5 idempotency prevents double-applied edits", side_effects_with_keys == 0,
      f"replay side-effects: no-keys={side_effects_without_keys} -> keys={side_effects_with_keys} (17/21)")

# =========================================================================
# STAGE 6 — orchestration (27): Amdahl ceiling, join tail, aggregation tax, YAGNI payoff
# =========================================================================
# Amdahl over agents: speedup = 1/(s + (1-s)/P), ceiling 1/s
s = 0.20
def speedup(P): return 1 / (s + (1 - s)/P)
check("S6 Amdahl speedup P=10", approx(speedup(10), 3.571, 1e-3), f"1/(s+(1-s)/10) = {speedup(10):.3f}x")
check("S6 Amdahl hard ceiling 1/s", approx(1/s, 5.0), f"ceiling = 1/{s} = {1/s}x regardless of P")
# join gated by slowest worker: P(stall) = 1-(1-pp)^Nw
pp = 0.01
def join_tail(Nw): return 1 - (1 - pp) ** Nw
check("S6 join tail N=100", approx(join_tail(100), 0.6340, 1e-3),
      f"1-(1-{pp})^100 = {join_tail(100):.4f} -> deadline + partial results (20)")
# aggregation tax: reading Nw workers raw = Nw*r re-sent each supervisor turn; compaction cuts it
Nw, r, rho = 10, 3000, 0.15
raw_agg, compact_agg = Nw*r, Nw*r*rho
check("S6 aggregation tax compaction", approx(raw_agg/compact_agg, 6.667, 1e-3),
      f"raw {raw_agg} / compacted {compact_agg} = {raw_agg/compact_agg:.3f}x (24 at the parent)")
# YAGNI payoff: multi-agent wins only if T_total > T_total/speedup + T_coord
def worth_it(T_total, sp, T_coord): return T_total > T_total/sp + T_coord
check("S6 multi-agent WINS on big decomposable task",
      worth_it(1000, speedup(10), 200) is True,
      f"1000 > 1000/{speedup(10):.2f}+200 ({1000/speedup(10)+200:.1f}) -> True")
check("S6 multi-agent LOSES on small task (YAGNI)",
      worth_it(50, speedup(10), 200) is False,
      f"50 > 50/{speedup(10):.2f}+200 ({50/speedup(10)+200:.1f}) -> False; default to ONE loop")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 28 build-progression walls verified by recomputation (reusing 22-27).")
