# 34 · Phase-1 factcheck — design-your-own-agentic-system

> Method (same discipline as 13-33): every load-bearing claim is (a) RECOMPUTED in `_recompute.py`
> (13/13 pass) or (b) REUSED from a line-verified 22-33 anchor. **NO new primary** — 34 is the Part
> III CAPSTONE DESIGN CANVAS, the agentic counterpart of 21 (which applied 13-20). **0 blockers.**

## Bespoke structure note
34 is a **DESIGN CANVAS / FORCED-MOVES DECISION-TREE** (Define the task → arithmetic → forced
primitives → budget every cross-cut → failure modes), NOT four clusters and NOT the 13-20
four-cluster shape. Plan-sanctioned ("the Part III CAPSTONE DESIGN CANVAS — applies all of 22-33 the
way 21 applied 13-20; NO new primary"). It is to Part III exactly what 21 is to Part II.

## No new primary (why) — the capstone identity
Like 21, 34 introduces NO new primitive; it teaches the *method* of composing the ones already
proven. Every cross-cutting budget reduces to an already-FETCHED+VERIFIED-or-recomputed anchor:
- **22** loop O(T²) — ReAct-anchored, recomputed in 22/28/32.
- **24** compaction O(T²)→O(T) — CoT-anchored (format/context), recomputed in 24.
- **25** memory AMAT over tokens — MemGPT+Reflexion-anchored, recomputed in 25.
- **26** checkpoint knee I*=√(2N·c) — Postgres-WAL-anchored, recomputed in 26.
- **27** Amdahl ceiling + join tail 1-(1-p)^N + YAGNI — distributed-systems toolkit, recomputed in 27.
- **31** eval CI = 1.96√(p(1-p)/N) — SWE-bench-anchored, recomputed in 31.
- **32** cost = the 22 quadratic priced — recomputed in 32.
- **33** defence-in-depth escape = ∏(1-c_i) — Greshake-anchored, recomputed in 33.

## Recomputed claims (`_recompute.py`, 13/13)
- Loop cost O(T²) is the master constraint (22). PASS.
- Compaction FORCED only past the per-call window; restores per-call headroom (24). PASS×2.
  *(Note: the WINDOW is the per-call linear constraint p+g(T-1); the quadratic in_tokens is the
  cumulative COST — kept distinct, see steps 1/7.)*
- External memory pays when hit-rate high (25 AMAT). PASS.
- Checkpoint knee I*=√(2N·c); short task → skip (26/YAGNI). PASS×2.
- Amdahl ceiling 1/s; join tail 63.4%@N=100; multi-agent loses on small tasks (27). PASS×3.
- Eval set size from target CI ≈1068 tasks (31). PASS.
- Pricing the design shows compaction's $ win (32 over 24). PASS.
- Each untrusted channel needs a screen; depth bounds escape (33). PASS.
- **Capstone thesis:** small task forces {22}; big task forces {22,24,33,26,27,31,32} — a design is
  a SEQUENCE OF FORCED MOVES picked by task shape + arithmetic (the 21 thesis, agentic). PASS.

## Reused (line-verified 22-33)
22 (loop/O(T²)), 23 (tool contract/validation), 24 (context/compaction), 25 (memory/AMAT),
26 (persistence/resume/checkpoint knee), 27 (planning/orchestration/Amdahl/tail/YAGNI), 28 (the
harness all this builds), 29 (connectors/MCP), 30 (RAG/grounding), 31 (eval/trace/guardrails),
32 (cost/ops), 33 (safety/self-evolution). Plus the Part I/II canon those rest on.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- No NEW gaps introduced (capstone reuses only verified anchors). The canvas inherits each home
  sub-course's residual `[UNVERIFIED]` (e.g. provider specs 22/24/32, planning papers 27,
  LLM-judge primary 31, dual-LLM/alignment 33) — all already logged, none load-bearing for the
  design METHOD, which is the recomputed forced-moves logic.

## Verdict
34 is honest and capstone-appropriate: NO new load-bearing claim — it composes the 22-33 toolkit
into a forced-moves design method, every cross-cutting budget RECOMPUTED first-principles (13/13)
and cross-linked to a line-verified anchor, exactly as 21 did for 13-20. Reconcile into
`_research.md`. **Finishing 34 COMPLETES Part III (22-34).** **0 blockers.**
