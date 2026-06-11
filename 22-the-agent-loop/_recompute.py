#!/usr/bin/env python3
"""
Substrate 22 - the-agent-loop: independent recomputation of every quantitative claim in the
section brief. Pure stdlib. Run: python3 _recompute.py

22 introduces the agent control loop. Its load-bearing arithmetic is the ECONOMICS of the loop:
because the full context is re-sent every turn AND the transcript grows every turn, input-token
cost is QUADRATIC in the number of turns. That single fact motivates 24 (context engineering),
25 (memory), and 32 (cost). Everything here is re-derived from first principles, not re-cited.
"""

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# =========================================================================
# 1. PER-TURN INPUT TOKEN GROWTH (linear per turn)
# =========================================================================
# Fixed prefix p = system + tool schemas + task. Each turn appends g tokens
# (Thought + Action + Observation). Prompt tokens at turn t = p + (t-1)*g.
p = 2000      # fixed prefix tokens
g = 500       # tokens appended per turn
def prompt_tokens(t): return p + (t - 1) * g
check("turn 1 prompt tokens", prompt_tokens(1) == 2000, f"p + 0*g = {prompt_tokens(1)}")
check("turn 5 prompt tokens", prompt_tokens(5) == 4000, f"p + 4*g = 2000 + 4*500 = {prompt_tokens(5)}")
check("turn 10 prompt tokens", prompt_tokens(10) == 6500, f"p + 9*g = 2000 + 9*500 = {prompt_tokens(10)}")

# =========================================================================
# 2. CUMULATIVE INPUT TOKENS OVER T TURNS = QUADRATIC (the headline)
# =========================================================================
# sum_{t=1..T}[p + (t-1)*g] = T*p + g*T*(T-1)/2
def cum_input(T): return T * p + g * T * (T - 1) // 2
def cum_input_formula(T): return T * p + g * (T * (T - 1)) // 2
for T in (1, 5, 10, 20):
    brute = sum(prompt_tokens(t) for t in range(1, T + 1))
    check(f"cumulative input tokens T={T}", cum_input(T) == brute,
          f"closed-form {cum_input(T)} == brute-sum {brute}")
# Show it's quadratic: doubling T from 10->20 should ~4x the g-term, not 2x.
g_term_10 = g * 10 * 9 // 2          # 22500
g_term_20 = g * 20 * 19 // 2         # 95000
check("quadratic growth (g-term ~4x when T doubles 10->20)",
      approx(g_term_20 / g_term_10, 4.222, tol=1e-2),
      f"{g_term_20}/{g_term_10} = {g_term_20/g_term_10:.3f}x (super-linear -> O(T^2))")

# =========================================================================
# 3. COST-PER-CALL AND CUMULATIVE $ (example provider pricing)
# =========================================================================
# Example: $3 / 1M input tokens, $15 / 1M output tokens. Output ~ o tokens/turn.
IN_PER_M = 3.00
OUT_PER_M = 15.00
o = 300  # output tokens per turn
def turn_cost(t):
    return prompt_tokens(t) / 1e6 * IN_PER_M + o / 1e6 * OUT_PER_M
c1 = turn_cost(1)
check("turn 1 cost", approx(c1, 2000/1e6*3 + 300/1e6*15),
      f"{2000}/1M*$3 + {300}/1M*$15 = ${c1:.6f}")
# Cumulative $ over T=20 turns.
def cum_cost(T):
    return cum_input(T) / 1e6 * IN_PER_M + (T * o) / 1e6 * OUT_PER_M
cc20 = cum_cost(20)
exp_in = cum_input(20)            # 20*2000 + 500*20*19/2 = 40000 + 95000 = 135000
exp_cost = 135000/1e6*3 + (20*300)/1e6*15
check("cumulative input tokens T=20 (=135000)", exp_in == 135000, f"40000 + 95000 = {exp_in}")
check("cumulative cost T=20", approx(cc20, exp_cost),
      f"135000/1M*$3 + 6000/1M*$15 = ${cc20:.4f}")
# Naive (wrong) linear estimate would undercount: linear would assume flat prompt = p every turn.
naive_in = 20 * p
check("naive flat-prompt undercount", naive_in < exp_in,
      f"naive {naive_in} << actual {exp_in} (ignoring transcript growth underestimates {exp_in/naive_in:.2f}x)")

# =========================================================================
# 4. STEP BUDGET -> WORST-CASE COST (the bound that tames the quadratic)
# =========================================================================
# A hard max_steps cap turns unbounded O(T^2) into a known worst case.
max_steps = 20
worst_cost = cum_cost(max_steps)
check("step-budget bounds worst-case cost", approx(worst_cost, exp_cost),
      f"max_steps={max_steps} -> worst-case ${worst_cost:.4f}; without it cost is unbounded")

# =========================================================================
# 5. CONTEXT-WINDOW EXHAUSTION TURN  T* = floor((W - p)/g) + 1
# =========================================================================
# The prompt at turn t must fit the window W. Largest feasible turn:
# p + (T*-1)*g <= W  ->  T* = floor((W - p)/g) + 1.
W = 128000
T_star = (W - p) // g + 1
check("context-window exhaustion turn", T_star == (128000 - 2000)//500 + 1,
      f"floor((W-p)/g)+1 = floor(126000/500)+1 = {T_star} turns before overflow")
# Verify boundary: prompt at T* fits, prompt at T*+1 does not.
check("T* prompt fits window", prompt_tokens(T_star) <= W,
      f"prompt({T_star}) = {prompt_tokens(T_star)} <= {W}")
check("T*+1 prompt overflows window", prompt_tokens(T_star + 1) > W,
      f"prompt({T_star+1}) = {prompt_tokens(T_star+1)} > {W} -> need compaction (24)")

# =========================================================================
# 6. PER-STEP RETRY / DEADLINE BUDGET (reuse 18 applied to one model/tool call)
# =========================================================================
# One step has a per-attempt timeout and a step deadline. Effective attempts =
# floor(step_deadline / per_attempt_timeout). (Backoff ignored for the floor bound.)
per_attempt = 10.0     # seconds
step_deadline = 30.0   # seconds
attempts = int(step_deadline // per_attempt)
check("per-step retry attempts under deadline", attempts == 3,
      f"floor({step_deadline}/{per_attempt}) = {attempts} attempts before the step deadline (reuse 18)")
# Loop-level wall clock: max_steps * step_deadline is the absolute worst-case latency bound.
loop_deadline = max_steps * step_deadline
check("loop worst-case wall-clock bound", loop_deadline == 600.0,
      f"max_steps*step_deadline = {max_steps}*{step_deadline} = {loop_deadline}s absolute cap")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 22 agent-loop economics verified by recomputation.")
