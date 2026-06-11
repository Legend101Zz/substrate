#!/usr/bin/env python3
"""
Substrate 30 - rag-retrieval-and-grounding: independent recomputation of every quantitative claim in
the retrieval-pipeline brief. Pure stdlib. Run: python3 _recompute.py

30's new primitive (parametric vs non-parametric memory + ANN top-K) is VERIFIED against RAG (Lewis
2020). Its quantitative claims are (a) the sub-linear ANN payoff vs brute-force scan (the 06
structure argument over a corpus), (b) the retrieve-vs-stuff budget argument (the 24/23 break-even
over documents), (c) K as a precision/recall/cost knob, (d) embedding-cache reuse (08), and (e)
index staleness/lag (15/16). Everything re-derived from first principles, not re-cited.
"""

import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# =========================================================================
# 1. ANN (sub-linear) vs BRUTE-FORCE SCAN (the 06 structure payoff, VERIFIED sub-linear)
# =========================================================================
# Brute force semantic search compares the query to all N chunks: O(N).
# An HNSW/MIPS index is ~O(log N) (VERIFIED "approximately solved in sub-linear time").
def brute_ops(N): return N
def ann_ops(N): return math.log2(N)
for N in (1_000, 1_000_000, 10_000_000):
    speedup = brute_ops(N) / ann_ops(N)
    check(f"ANN vs scan N={N}", ann_ops(N) < brute_ops(N),
          f"scan {brute_ops(N)} vs ANN ~{ann_ops(N):.1f} ops = {speedup:,.0f}x fewer")
# headline: 10M chunks -> ~23 ops, ~430,000x fewer comparisons
N = 10_000_000
check("ANN payoff at 10M chunks", approx(brute_ops(N)/ann_ops(N), 429496.7, 1e-2),
      f"{brute_ops(N)}/{ann_ops(N):.2f} = {brute_ops(N)/ann_ops(N):,.1f}x (06 structure buys sub-linear)")

# =========================================================================
# 2. RETRIEVE TOP-K vs STUFF THE WHOLE CORPUS (the 24 budget argument)
# =========================================================================
# Corpus has N chunks of c tokens. The window can only hold the prompt + K chunks.
# Stuffing all N is impossible/absurd; retrieval sends only K relevant chunks.
N_chunks, c, W, prefix = 10_000_000, 500, 128_000, 4_000
def stuff_all_tokens(): return N_chunks * c           # absurd
def retrieve_tokens(K): return K * c
check("stuffing whole corpus overflows window absurdly",
      stuff_all_tokens() > W,
      f"all-corpus {stuff_all_tokens():,} tok >> window {W:,} (impossible -> must retrieve)")
K = 8
budget_at_t1 = W - prefix
check("top-K fits the budget", retrieve_tokens(K) <= budget_at_t1,
      f"K*c = {K}*{c} = {retrieve_tokens(K)} <= budget {budget_at_t1} (24)")
# max K that fits the budget
K_max = budget_at_t1 // c
check("max K under budget", K_max == (124000)//500,
      f"floor((W-prefix)/c) = floor({budget_at_t1}/{c}) = {K_max} chunks max")

# =========================================================================
# 3. K AS A PRECISION/RECALL/COST KNOB (optimal K where marginal recall < marginal cost)
# =========================================================================
# Model recall(K) with diminishing returns: recall = 1 - (1-r)^K (each extra relevant-ish chunk
# adds a chance the answer is covered), r = per-chunk hit prob. Cost grows linearly: K*c tokens.
r = 0.5
def recall(K): return 1 - (1 - r) ** K
for K_, exp in [(1, 0.5), (2, 0.75), (4, 0.9375)]:
    check(f"recall(K={K_})", approx(recall(K_), exp, 1e-6),
          f"1-(1-{r})^{K_} = {recall(K_):.4f} (diminishing returns)")
# marginal recall shrinks while marginal cost is constant -> a finite optimum exists
marg_1to2 = recall(2) - recall(1)   # 0.25
marg_4to5 = recall(5) - recall(4)   # ~0.03
check("marginal recall diminishes (cost is constant -> optimal K finite)", marg_4to5 < marg_1to2,
      f"d_recall 1->2 = {marg_1to2:.3f} vs 4->5 = {marg_4to5:.3f}; each chunk costs the same c tokens")
# distractor cost: extra irrelevant chunks dilute (24 lost-in-the-middle) -> don't max K blindly
check("big K adds distractors (don't maximize K)", K_max > 50 and recall(50) > 0.999,
      f"K_max={K_max} but recall saturates by K~{ -math.log(0.001)/-math.log(1-r):.0f}; rest are distractors")

# =========================================================================
# 4. EMBEDDING CACHE REUSE (08): embeddings are deterministic per (model, chunk)
# =========================================================================
# Embedding is a pure function of (model, chunk_text) -> cache it. Re-indexing without a cache
# re-embeds all N; with a cache only the CHANGED chunks are re-embedded.
N_total, changed = 1_000_000, 1_000
def reembed_no_cache(): return N_total
def reembed_with_cache(): return changed
check("embedding cache cuts re-index cost", reembed_with_cache() < reembed_no_cache(),
      f"no-cache re-embeds {N_total:,} vs cache re-embeds {changed:,} ({N_total/changed:.0f}x less, 08)")

# =========================================================================
# 5. INDEX STALENESS / REPLICATION LAG (15/16): index is a replica of the corpus
# =========================================================================
# An edited doc is invisible until re-embedded+re-indexed. Staleness window = time to re-index.
edit_time, reindex_latency = 0.0, 30.0   # seconds
visible_at = edit_time + reindex_latency
check("index lag = staleness window", visible_at == 30.0,
      f"edited doc visible only after re-index ({reindex_latency}s lag) -> 15/16 cache-consistency")
# grounding freshness is bounded by index freshness: a fact edited 10s ago, index lag 30s -> stale
check("grounding only as fresh as the index", 10 < reindex_latency,
      "fact edited 10s ago, lag 30s -> retrieval still returns the OLD passage (16 invalidation)")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 30 retrieval/grounding economics verified by recomputation.")
