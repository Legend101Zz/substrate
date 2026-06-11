# Appendix M · ai-agent-memory-tools-and-evaluation — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). M is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the deep, primary-anchored companion to Part III
> (22-34): where the spine teaches each agent primitive *operationally and in dependency order*, M is
> the single reference that collects the **canonical papers** (all LOCAL+VERIFIED) with their precise
> mechanisms + re-derived math, so any spine chapter can cross-link DOWN. Bespoke structure: a
> **primitive-by-primary catalogue** (memory → tools → reasoning → retrieval → evaluation → safety),
> NOT four clusters and NOT a build progression. Math: `_recompute.py` (17/17). Factcheck:
> `_factcheck_phase1.md` (0 blockers). **NO new primary needed — every primary is already local.**

## 1. Thesis
An "AI agent" is a small set of primitives, each with a real research primary and a piece of
load-bearing arithmetic. This appendix is the reference shelf: one entry per primitive, each pinned
to its FETCHED+VERIFIED paper and its recomputed number, with the spine sub-course that operationalizes
it.

## 2. The catalogue (the bespoke spine)

### Memory — MemGPT (`memgpt-2310.08560`, local+VERIFIED) + Reflexion (`reflexion-2303.11366`)
- **Virtual context management = OS paging over tokens.** Main context (in-window) vs external
  context (paged store); the agent issues function calls to page data in/out. RECOMPUTED: resident
  fraction ~**0.1%** (128K window over 128M store) ⇒ eviction/paging is mandatory.
- **AMAT over tokens**: effective per-token cost = `hit·resident + (1−hit)·recall`. At hit=0.95 ⇒
  3.45 vs recall 50 ⇒ external memory pays **only when hit-rate is high** (the paging win).
- **Reflexion**: episodic memory of past failures becomes a *learning signal* — verbal
  self-reflection stored and replayed improves later attempts. Anchors the self-improvement loop (33)
  and the "memory as learning, not just storage" distinction. Spine home: **25**.

### Tools — Toolformer (`toolformer-2302.04761`, local+VERIFIED)
- **A tool is a contract** between a stochastic caller and deterministic code: four decisions —
  which tool, when, what args, how to incorporate the result. RECOMPUTED: **selection compounds** —
  0.95^10 ≈ 59.9% all-correct over 10 calls; 1−(1−0.02)^50 ≈ 63.6% chance of ≥1 bad call over 50 ⇒
  per-call accuracy + validation/repair matter.
- **Result budget**: a raw tool result of R tokens re-sent every later turn feeds the O(T²) loop; a
  100K-token raw dump (>50% of a 128K window) MUST be summarized/paginated — the result-contract
  half of the tool. Spine homes: **23** (contract), **29** (MCP wire protocol), **28** (in the lab).

### Reasoning loop — ReAct (`react-2210.03629`, local+VERIFIED)
- **Interleave reasoning + acting**: a thought step before each action lowers per-action error and
  lets the agent re-plan on observations. RECOMPUTED illustration: halving per-step error over 10
  steps lifts success 0.349 → 0.599. The control loop (call→observe→decide→repeat) is the agent's
  fetch-decode-execute. Spine home: **22**.

### Retrieval — RAG (`rag-2005.11401`, Lewis et al. 2020, local+VERIFIED)
- **Parametric vs non-parametric memory**: the model's weights vs an external, *updatable*,
  *attributable* corpus. Pipeline: corpus → chunk → embed → index → retrieve (MIPS top-K) → ground.
  RECOMPUTED: **ANN ≈ 430,000× faster** than full scan at 10M docs (~23 vs 10M comparisons) ⇒ why
  FAISS/HNSW exists; **K knob** = retrieved tokens K·chunk trades recall vs window vs cost. Cures
  hallucination + gives provenance + lets knowledge update without retraining. Spine home: **30**
  (retrieval mechanism for 25's non-parametric tier).

### Evaluation — SWE-bench (`swe-bench-2310.06770`, Jimenez/Yang et al. ICLR 2024, local+VERIFIED)
- **Execution-based "is it useful"**: apply the patch → run fail-to-pass + pass-to-pass tests →
  resolved iff ALL pass. Metric = **%resolved**. Tests are the oracle; **lexical similarity ≠
  correctness**. RECOMPUTED: full suite (~2294 tasks) gives a tight CI (±1.64% at p=0.20) ⇒ big
  execution suites beat string-match eval; **pass@k (lenient) ≫ pass^k (strict)** (0.936 vs 0.216 at
  p=0.6,k=3) — always say which you report.
- **LLM-as-judge** for un-gradeable outputs: **majority-of-3** independent judges beats a single one
  *iff* per-judge accuracy > 0.5 (Condorcet; 0.70 → 0.784), and **backfires below 0.5** (0.40 →
  0.352) — a biased judge gets worse in ensemble. Reuses 27's voting. Spine home: **31**.

### Safety — Greshake Indirect Prompt Injection (`greshake-injection-2302.12173`, AISec '23, local+VERIFIED)
- **Root cause**: LLMs blur the line between *data* and *instructions* ⇒ retrieved/tool/memory
  content can carry commands. RECOMPUTED: **blast radius = downstream reads** (1 poisoned
  doc/memory read 15× → 15 contaminated calls — 1-write-many-reads); **defence-in-depth escape =
  ∏(1−c_i)** (three 80% screens → 0.8% escape) ⇒ no single layer suffices, screen *every* untrusted
  channel (tool-result 23, memory 25, retrieved-passage 30). Spine home: **33**.

## 3. The cross-cutting reconciliation (appendix payload)
| recurring identity | appearance in agent primitives |
|---|---|
| O(T²) loop cost | re-sent transcript (22), raw tool results (23), uncompacted memory (25) |
| `1−(1−p)^N` | tool-step failure (23), judge/voting (31), join tail (27), injection blast complement (33) |
| AMAT (`hit·res+(1−hit)·rec`) | token memory hierarchy (25), retrieval-vs-stuff (30) |
| sub-linear index (~log N) | ANN/MIPS retrieval (30), any large lookup (06/N) |
| sampling CI `1.96√(p(1−p)/N)` | eval set size (31), judge agreement (31) |
This is the appendix's reason to exist: it lets the reader see the agent stack is the SAME systems
math (queueing, hashing, probability, AMAT) re-aimed at tokens and a stochastic actuator.

## 4. Common misconceptions to preempt
- "More memory = better agent" — only if hit-rate is high (AMAT); else recall cost dominates.
- "Tools just work once defined" — selection + result handling compound; validate and budget results.
- "RAG eliminates hallucination" — it *reduces* it and adds provenance, but a poisoned passage is a
  new attack surface (33).
- "A good LLM judge is enough" — only above 0.5 accuracy, and ensembles amplify bias below it.
- "%resolved on a benchmark = production-ready" — execution-based eval is necessary, not sufficient;
  pair with tracing (19/31) + safety (33).

## 5. Provenance summary
- **NO new primary fetched** — all seven primaries already LOCAL+VERIFIED (MemGPT, Reflexion,
  Toolformer, ReAct, RAG, SWE-bench, Greshake). Receipts in `meta/fetched_primaries/`.
- **RECOMPUTED:** `_recompute.py` (17/17).
- **REUSED (line-verified):** spine 22/23/25/27/30/31/33 (and 06/N for the shared math).
- **`[UNVERIFIED]` carry-forward (inherited, not load-bearing):** DPR (arXiv 2004.04906) + FAISS/HNSW
  (Malkov-Yashunin 2016) primaries (→30); LLM-judge primary MT-Bench (2306.05685) + bias taxonomy
  (→31); HumanEval, SWE-agent (2405.15793); dual-LLM/CaMeL, Constitutional-AI (2212.08073), RLHF
  (2203.02155) (→33); provider function-calling/prompt-cache specs (→22/23/24/32). All already logged
  in their home sub-courses; M does not harden any into prose.

---
**Appendix M reconciled.** Reference-grade, exercise-free, 17/17 recomputed, every primitive pinned
to a LOCAL+VERIFIED primary. No chapters yet.
