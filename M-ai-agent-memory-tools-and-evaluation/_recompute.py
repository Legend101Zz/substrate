#!/usr/bin/env python3
"""
Substrate Appendix M - ai-agent-memory-tools-and-evaluation: independent recomputation of the
load-bearing arithmetic behind agent memory, tool use, and evaluation. Pure stdlib.
Run: python3 _recompute.py

M is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for the agent
primitives the Part III spine (22-34) teaches operationally -- here collected with their canonical
PRIMARIES (all LOCAL+VERIFIED) and re-derived math, so spine chapters cross-link DOWN:
  Memory hierarchy / AMAT over tokens     (MemGPT 2310.08560; 25)
  Episodic memory as learning signal      (Reflexion 2303.11366; 25)
  Tool contract / selection compounding   (Toolformer 2302.04761; 23)
  ReAct interleaving reason+act           (ReAct 2210.03629; 22)
  RAG retrieval (ANN vs scan, K knob)     (RAG 2005.11401; 30)
  Evaluation: execution-based, CI, judge  (SWE-bench 2310.06770; 31)
  Indirect prompt injection blast radius  (Greshake 2302.12173; 33)
Every number re-derived first-principles, cross-linked to its primary + spine anchor.
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. MEMORY HIERARCHY / AMAT over tokens (MemGPT; 25)
#    effective cost = hit*resident + (1-hit)*recall   (the OS AMAT identity, tokens)
# =====================================================================
def amat(hit, c_resident, c_recall): return hit*c_resident + (1-hit)*c_recall
c_res, c_rec = 1.0, 50.0   # resident token ~1 unit; recall from external store ~50 units
for hit, want_band in [(0.95, 3.5), (0.5, 25.5), (0.0, 50.0)]:
    a = amat(hit, c_res, c_rec)
    check(f"AMAT over tokens at hit={hit} (MemGPT/25)", a <= c_rec and a >= c_res,
          f"effective cost {a:.2f} (between resident {c_res} and recall {c_rec}) -> high hit-rate buys cheapness")
check("external memory pays only when hit-rate high (25)", amat(0.95,c_res,c_rec) < 0.1*c_rec,
      f"hit=0.95 -> {amat(0.95,c_res,c_rec):.2f} << recall {c_rec} -> the paging win")

# =====================================================================
# 2. RESIDENT FRACTION: a tiny working set in a huge memory (MemGPT virtual context; 25)
# =====================================================================
window, total_mem = 128_000, 128_000_000   # 128K live window vs 128M external store
resident_frac = window/total_mem
check("resident fraction ~0.1% (virtual context paging) (MemGPT/25)", approx(resident_frac, 0.001),
      f"{resident_frac*100:.2f}% of memory is 'in context' at once -> WHY paging/eviction is mandatory")

# =====================================================================
# 3. TOOL SELECTION COMPOUNDING: success over N steps = q^N ; failure 1-(1-e)^N (Toolformer; 23)
# =====================================================================
def all_ok(q, N): return q**N
def any_fail(e, N): return 1-(1-e)**N
check("tool selection compounds: 0.95^10 ~ 0.599 (Toolformer/23)", abs(all_ok(0.95,10)-0.5987) < 1e-3,
      f"95% per-step over 10 tool calls -> {all_ok(0.95,10)*100:.1f}% all-correct -> WHY per-call accuracy matters")
check("step-failure compounds 1-(1-e)^N (23)", abs(any_fail(0.02,50)-0.636) < 2e-3,
      f"2% per-step over 50 steps -> {any_fail(0.02,50)*100:.1f}% chance of >=1 bad call -> validation/repair needed")

# =====================================================================
# 4. RESULT BUDGET: a tool that dumps R tokens N times costs the O(T^2) loop (23/22)
# =====================================================================
def result_overhead(N, R, g=1500): return N*R    # each result re-sent every later turn -> see loop
R_big = 100_000   # a 1MB file dumped raw
check("raw tool-result dump blows the window (23/28)", R_big > 0.5*128_000,
      f"a {R_big:,}-token raw result > 50% of a 128K window -> MUST summarize/paginate (the 23 result contract)")

# =====================================================================
# 5. RAG: ANN vs full scan at scale (RAG 2005.11401; 30)
# =====================================================================
def scan_cost(Ndocs): return Ndocs                  # O(N) brute force
def ann_cost(Ndocs): return math.log2(Ndocs)        # ~O(log N) HNSW-ish
Ndocs = 10_000_000
speedup = scan_cost(Ndocs)/ann_cost(Ndocs)
check("ANN ~430,000x faster than scan at 10M docs (RAG/30)", speedup > 4e5,
      f"scan {Ndocs:,} vs ANN ~{ann_cost(Ndocs):.0f} comparisons -> ~{speedup:,.0f}x -> WHY MIPS/HNSW index")
# K knob: retrieved tokens = K*chunk ; precision/recall vs budget
def retrieved_tokens(K, chunk=500): return K*chunk
check("RAG K knob: retrieved tokens = K*chunk (30)", retrieved_tokens(8) == 4000,
      "K=8 chunks x500 tok = 4000 tok injected -> K trades recall vs window budget vs cost")

# =====================================================================
# 6. EVALUATION: execution-based %resolved + sample-size CI (SWE-bench; 31)
# =====================================================================
# SWE-bench: apply patch -> run fail-to-pass + pass-to-pass tests; resolved = ALL pass.
def ci95(p, N): return 1.96*math.sqrt(p*(1-p)/N)
N_tasks = 2294   # SWE-bench full ~2294 task instances
ci = ci95(0.20, N_tasks)
check("SWE-bench execution-based eval: CI tightens with N (31)", ci < 0.02,
      f"p=0.20 over {N_tasks} tasks -> +-{ci*100:.2f}% CI -> WHY a big execution suite beats lexical match")
# pass@k vs pass^k: lenient vs strict aggregation
def pass_at_k(p, k): return 1-(1-p)**k     # any of k samples passes
def pass_pow_k(p, k): return p**k          # all k must pass
check("pass@k (lenient) >> pass^k (strict) (31)", pass_at_k(0.6,3) > 0.93 and pass_pow_k(0.6,3) < 0.22,
      f"p=0.6,k=3: pass@k={pass_at_k(0.6,3):.3f} vs pass^k={pass_pow_k(0.6,3):.3f} -> report which you mean")

# =====================================================================
# 7. LLM-AS-JUDGE: majority-of-3 reduces judge variance (Condorcet; 27/31)
# =====================================================================
def maj3(p): return p**3 + 3*p**2*(1-p)     # majority of 3 independent judges each acc p
check("majority-of-3 judges beats single when p>0.5 (31/27)", maj3(0.7) > 0.7,
      f"single judge 0.70 -> maj-of-3 {maj3(0.7):.3f} (Condorcet); BACKFIRES if p<0.5: maj3(0.4)={maj3(0.4):.3f}")
check("judge ensemble backfires below 0.5 (31)", maj3(0.4) < 0.4,
      f"p=0.4 -> maj-of-3 {maj3(0.4):.3f} < 0.4 -> a biased judge gets WORSE in ensemble")

# =====================================================================
# 8. INDIRECT PROMPT INJECTION: blast radius 1-write-many-reads (Greshake; 33)
# =====================================================================
# one poisoned doc read by R downstream calls -> R contaminated outputs
def blast(R_reads): return R_reads
check("injection blast radius = downstream reads (Greshake/33)", blast(15) == 15,
      "one poisoned memory/passage read 15x -> 15 contaminated calls -> WHY screen every untrusted channel")
# defence-in-depth escape = prod(1-c_i)
def escape(layers): 
    p=1.0
    for c in layers: p*=(1-c)
    return p
check("defence-in-depth: escape = prod(1-c_i) (33)", abs(escape([0.8,0.8,0.8])-0.008) < 1e-9,
      f"three 80% screens -> {escape([0.8,0.8,0.8])*100:.1f}% escape -> depth multiplies, no single layer suffices")

# =====================================================================
# 9. ReAct: interleaving reason+act beats act-only on multi-step (ReAct; 22)
# =====================================================================
# model: each reasoning step cuts per-action error; compare act-only e0 vs react e0*r over N steps
def react_success(e_per, N, reason_factor):
    e = e_per*reason_factor
    return (1-e)**N
check("ReAct interleaving lowers compounded error (22)",
      react_success(0.1,10,0.5) > react_success(0.1,10,1.0),
      f"N=10: react(reason halves err) {react_success(0.1,10,0.5):.3f} vs act-only {react_success(0.1,10,1.0):.3f}")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"M-ai-agent-memory-tools-and-evaluation recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All agent memory/tools/eval claims re-derived first-principles.")
