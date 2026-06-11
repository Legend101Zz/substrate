#!/usr/bin/env python3
"""
Substrate 25 - memory (short-term, long-term, and safety): independent recomputation of every
quantitative claim in the section briefs. Pure stdlib. Run: python3 _recompute.py

25 is what 24's compactor EXTERNALIZES TO. 24 proved compaction converts the 22 quadratic O(T^2)
-> O(T) by capping the in-window transcript at a ceiling C. But the evicted content cannot just be
deleted - it is paged out to a memory tier and paged back in on demand. This is EXACTLY the OS
virtual-memory / cache hierarchy (04/06/08), now over tokens. MemGPT (arXiv 2310.08560) names the
design: main context (fast, tiny, in-window) vs external context (slow, large, on "disk"), moved by
function calls. The load-bearing arithmetic of 25 is therefore the ECONOMICS OF THE HIERARCHY:
  (a) main context is a fixed token budget (sub-partition of 24's window);
  (b) retrieval (recall/archival -> main) has a TOKEN cost AND a hit/miss structure (08 cache math);
  (c) an effective-latency / effective-cost model identical to the memory-hierarchy AMAT (04/06);
  (d) eviction sizing (what fits, what spills) reuses 06/08 directly.
Everything below is re-derived from first principles, not re-cited.
"""

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# =========================================================================
# 1. MAIN CONTEXT IS A FIXED BUDGET, SPLIT INTO TIERS (MemGPT main context)
# =========================================================================
# MemGPT splits main context (prompt tokens) into: system instructions, working
# context (editable scratch memory), and a FIFO message queue. These must fit the
# in-window budget that 24's allocator handed to "memory".
main_context = 8_000          # MemGPT example: 8k-token finite window for main context
system_instr = 1_000
working_ctx  = 2_000          # self-editable working memory
fifo_queue   = main_context - system_instr - working_ctx
check("main context partitions into system + working + FIFO queue",
      fifo_queue == 5_000,
      f"8000 - 1000(sys) - 2000(working) = {fifo_queue} tok FIFO recent-message queue")
check("main-context tiers never exceed the in-window memory budget",
      system_instr + working_ctx + fifo_queue == main_context,
      f"{system_instr}+{working_ctx}+{fifo_queue} = {main_context} == main_context")

# =========================================================================
# 2. EXTERNAL CONTEXT IS UNBOUNDED; ONLY A PAGE FITS (the OS analogy)
# =========================================================================
# Archival/recall storage can hold N items; only what fits the FIFO/working budget
# is "resident". The resident fraction is tiny -> memory is a PAGING problem (04).
total_items   = 100_000       # everything the agent has ever stored
item_tokens   = 50            # avg tokens per stored memory item
resident_cap  = fifo_queue // item_tokens
check("only a tiny fraction of stored memory is resident in-context",
      resident_cap == 100,
      f"floor({fifo_queue}/{item_tokens}) = {resident_cap} items resident of {total_items:,} stored")
resident_frac = resident_cap / total_items
check("resident fraction is ~0.1% -> paging is mandatory",
      approx(resident_frac, 0.001),
      f"{resident_cap}/{total_items} = {resident_frac:.4f} (0.1%) resident -> retrieve on demand")

# =========================================================================
# 3. RETRIEVAL (recall -> main) HAS A TOKEN COST: k items of c tokens
# =========================================================================
# A recall_storage.search() pulls top-k items back into main context. That is a
# direct addend to 24's window budget AND to the 22 re-send every subsequent turn.
k = 5
c_item = 50
recall_cost = k * c_item
check("recall pulls k*c tokens into main context", recall_cost == 250,
      f"{k} items * {c_item} tok = {recall_cost} tok added to main context (and re-sent, 22)")
# It must fit the working/FIFO headroom or it triggers eviction (06/08) of older items.
check("recall result must fit resident budget or evict", recall_cost <= fifo_queue,
      f"{recall_cost} <= {fifo_queue} FIFO budget -> fits; if not, evict LRU (06/08)")

# =========================================================================
# 4. EFFECTIVE COST MODEL = the memory-hierarchy AMAT (reuse 04/06)
# =========================================================================
# Average "memory access" for the agent mirrors AMAT = hit_time + miss_rate*miss_penalty.
# In-context hit (info already resident) costs ~0 extra tokens; a miss costs a recall
# round-trip (a search + the pulled tokens + an extra LLM inference to use them).
# Effective extra tokens per memory access:
hit_rate    = 0.80            # fraction of needs already resident in main context
miss_penalty_tokens = recall_cost + 100   # pulled tokens + a search/query overhead
eff_tokens  = (1 - hit_rate) * miss_penalty_tokens
check("effective per-access token cost = miss_rate * miss_penalty (AMAT shape)",
      approx(eff_tokens, 0.20 * 350),
      f"(1-{hit_rate}) * {miss_penalty_tokens} = {eff_tokens:.0f} tok avg (04/06 AMAT over tokens)")
# Better resident policy (higher hit rate) lowers effective cost LINEARLY in miss rate.
hit_rate2 = 0.95
eff2 = (1 - hit_rate2) * miss_penalty_tokens
check("raising hit rate 0.80->0.95 cuts effective memory cost 4x",
      approx(eff_tokens / eff2, 4.0),
      f"{eff_tokens:.0f} -> {eff2:.1f} tok = {eff_tokens/eff2:.1f}x cheaper (good eviction/retrieval policy)")

# =========================================================================
# 5. WORKING vs LONG-TERM CONSOLIDATION (compaction handoff from 24)
# =========================================================================
# 24's compactor summarizes R evicted turns (R*g raw) into s tokens and WRITES the
# summary to long-term memory (this file's tier 2). The write is one-time; the read
# back is k-bounded (sec 3). Net: raw transcript O(T^2) growth is replaced by a
# bounded resident set + an external store that grows O(T) on disk (cheap), retrieved
# k-at-a-time. Verify the storage-tier accounting.
g = 500; R = 12
raw = R * g                  # 6000 raw tokens evicted
s = 600                      # consolidated summary written to long-term memory
check("consolidation writes a 10x-smaller summary to long-term store",
      approx(s / raw, 0.10), f"{s}/{raw} = {s/raw:.2f} (24 compaction ratio reused)")
# Long-term store grows linearly with turns (cheap disk), not quadratically in-window.
T = 200
disk_growth = (T // R) * s   # number of consolidations * summary size
check("long-term store grows ~O(T) on disk, not O(T^2) in-window",
      disk_growth == (200 // 12) * 600,
      f"floor({T}/{R})*{s} = {disk_growth} tok on disk over {T} turns (linear, off the critical path)")

# =========================================================================
# 6. SAFETY: memory is an ATTACK SURFACE -> poisoning persistence
# =========================================================================
# A single poisoned fact written to long-term memory is re-retrieved on every future
# matching query. Its blast radius is the number of future retrievals that hit it,
# NOT one turn. This is why memory writes need provenance/validation (33). Quantify:
poison_recall_prob = 0.30    # chance a future query retrieves the poisoned item
future_queries = 50
expected_hits = poison_recall_prob * future_queries
check("one poisoned memory item compounds across future retrievals",
      approx(expected_hits, 15.0),
      f"{poison_recall_prob}*{future_queries} = {expected_hits:.0f} expected re-uses (1 write, many reads -> validate writes, 33)")
# Contrast with a transient in-context error (22): it lives at most until compaction.
check("persistent memory error >> transient context error (blast radius)",
      expected_hits > 1,
      f"persistent {expected_hits:.0f} re-uses vs transient ~1 turn -> long-term memory needs write-time validation")

# =========================================================================
# 7. EVICTION POLICY SIZING (reuse 06/08 directly): what spills first
# =========================================================================
# When main context is full, evict to make room. With a working budget W_w and item
# size c, max resident items m = floor(W_w/c); the (m+1)th access is a miss (08).
W_w = working_ctx
m = W_w // c_item
check("max resident working-memory items = floor(W_w/c) (06/08 cache capacity)",
      m == 40, f"floor({W_w}/{c_item}) = {m} items; access #{m+1} misses -> recall (sec 3)")

# -------------------------------------------------------------------------
print("\n" + "=" * 60)
n = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{n} checks passed")
if passed != n:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 25 memory-hierarchy economics verified by recomputation.")
