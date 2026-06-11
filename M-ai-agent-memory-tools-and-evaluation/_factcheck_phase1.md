# Appendix M · Phase-1 factcheck — ai-agent-memory-tools-and-evaluation

> Method (spine discipline): every load-bearing claim is (a) RECOMPUTED in `_recompute.py` (17/17) or
> (b) VERIFIED against a LOCAL primary. M is a **reference appendix** (no exercises). **0 blockers.**
> **NO new primary needed — all seven primaries already local+VERIFIED from Part III.**

## Bespoke structure note
M is a **primitive-by-primary catalogue** (memory → tools → reasoning → retrieval → evaluation →
safety), NOT the 13-20 four-cluster shape and NOT a build progression. It is the reference-grade
companion to the Part III spine (22-34): the spine teaches these primitives operationally; M is the
deep paper-anchored shelf they cross-link DOWN to.

## Primaries reused (all LOCAL+VERIFIED in prior waves; receipts in fetched_primaries/)
- **MemGPT** `memgpt-2310.08560` — virtual context = paging; main vs external context. (25)
- **Reflexion** `reflexion-2303.11366` — episodic memory as learning signal. (25/33)
- **Toolformer** `toolformer-2302.04761` — four tool decisions (which/when/args/incorporate). (23)
- **ReAct** `react-2210.03629` — interleave reasoning + acting. (22)
- **RAG** `rag-2005.11401` (Lewis et al. 2020) — parametric vs non-parametric; DPR; MIPS; FAISS/HNSW. (30)
- **SWE-bench** `swe-bench-2310.06770` (ICLR 2024) — execution-based %resolved; tests-as-oracle;
  lexical≠correct. (31)
- **Greshake** `greshake-injection-2302.12173` (AISec '23) — data/instruction blur; injection
  taxonomy; persistence-via-memory. (33)

## Recomputed claims (`_recompute.py`, 17/17)
- AMAT over tokens at hit=0.95/0.5/0.0 between resident and recall; external memory pays only at high
  hit-rate. PASS×4.
- Resident fraction ~0.1% (virtual context). PASS.
- Tool selection compounds 0.95^10≈59.9%; failure 1−(1−0.02)^50≈63.6%. PASS×2.
- Raw 100K result > 50% window → must paginate. PASS.
- ANN ~430,043× faster than scan at 10M; K knob = K·chunk. PASS×2.
- SWE-bench CI ±1.64% at N=2294; pass@k 0.936 vs pass^k 0.216. PASS×2.
- Majority-of-3 judges 0.70→0.784 (Condorcet); backfires 0.40→0.352. PASS×2.
- Injection blast radius = 15 downstream reads; defence-in-depth escape ∏(1−c)=0.8%. PASS×2.
- ReAct interleaving lifts compounded success 0.349→0.599. PASS.

## Reused (line-verified spine)
22 (loop/ReAct), 23 (tool contract/Toolformer), 25 (memory/MemGPT+Reflexion/AMAT), 27 (voting),
30 (RAG/retrieval), 31 (eval/SWE-bench/judge), 33 (safety/Greshake). Shared math from 06/N
(hashing, probability, AMAT, sub-linear index, sampling CI).

## `[UNVERIFIED]` — carry-forward (inherited from home sub-courses; do NOT harden into prose)
- DPR (arXiv 2004.04906), FAISS/HNSW (Malkov-Yashunin 2016) primaries (→30).
- LLM-judge primary MT-Bench (arXiv 2306.05685) + bias taxonomy (→31); HumanEval; SWE-agent (2405.15793).
- dual-LLM/CaMeL, Constitutional-AI (2212.08073), RLHF (2203.02155) (→33).
- provider function-calling / prompt-caching specs (→22/23/24/32).
All already logged in their home sub-courses; M is a reference shelf and introduces no NEW gap.

## Verdict
M is honest and appendix-appropriate: no new load-bearing claim, every agent primitive pinned to a
LOCAL+VERIFIED primary and a recomputed number (17/17), with a cross-cutting map showing the agent
stack is the same systems math re-aimed at tokens. Reconcile into `_research.md`. **0 blockers.**
