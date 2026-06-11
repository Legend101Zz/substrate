# 34 · design-your-own-agentic-system — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 34 is the **CAPSTONE of Part III**: it
> introduces NO new primitive — it APPLIES the entire 22-33 toolkit to a design method, exactly as
> **21** applied 13-20 to six system designs. Bespoke structure: a **design canvas / forced-moves
> decision-tree** (NOT four clusters). Math: `_recompute.py` (13/13). Factcheck: `_factcheck_phase1.md`
> (0 blockers). NO new primary (capstone application).

## 1. The thesis (RECOMPUTED — the agentic 21)
**An agentic design is a SEQUENCE OF FORCED MOVES: the task's shape + the arithmetic pick the
primitives.** RECOMPUTED: a *small* task (short, single-shot, no untrusted data) forces only
`{22 loop}`; a *big* task (long, multi-source, multi-agent, evaluated) forces the whole stack
`{22, 24, 33, 26, 27, 31, 32}`. The engineer's job is to see the forcing function and price the
tradeoff — the same capstone identity as 21, now over the agentic toolkit.

## 2. The design canvas (the bespoke spine — the teachable method)
A repeatable loop, the agentic mirror of 21's 6-step method:
1. **Define the task** — functional + **non-functional** (latency/turn budget, correctness bar,
   safety surface, $/run, autonomy level). The non-functionals decide everything (the 21 lesson).
2. **The arithmetic** — RECOMPUTE the budgets that the task forces (the §3 budget ledger): expected
   turns T → loop cost (22); per-call input vs window → compaction (24); knowledge needs → memory
   (25)/retrieval (30); duration/value → checkpointing (26); parallelism → orchestration (27);
   correctness bar → eval set size (31); all of it → $/run (32); untrusted channels → safety (33).
3. **Pick the agentic primitives** — apply the minimal set the bottleneck forces; cross-link each to
   its home sub-course; price it.
4. **Compose into the harness (28)** — loop → tools → context → memory → persistence →
   orchestration → connectors → grounding → trust → cost → safety, the 28 build progression.
5. **Budget every cross-cut** (§3) — leave no quadratic unbounded, no untrusted channel unscreened,
   no long task without resume, no claim of "it works" without an eval CI.
6. **Failure modes + tradeoffs** — what breaks (33 attack surface, 27 join tail, 20 partial
   failure) and the explicit cost of every choice (compact vs cache, single vs multi-agent,
   gate-all vs risk-based, autonomy vs oversight).

## 3. The cross-cutting budget ledger (RECOMPUTED — headlines, `_recompute.py` 13/13)
| budget | rule | anchor |
|---|---|---|
| **Loop** | input cost is O(T²) — the master constraint to bound | 22 |
| **Context** | per-call window p+g(T-1) overflows → compaction FORCED (O(T²)→O(T)) | 24 |
| **Memory** | AMAT over tokens; external memory pays when hit-rate high (~2.5× at 0.95) | 25 |
| **Persistence** | checkpoint every I*N·c); short task → skip (YAGNI) | 26 |
| **Orchestration** | Amdahl ceiling 1/s; join tail 1-(1-p)^N=63.4%@N=100; multi-agent LOSES on small tasks | 27 |
| **Eval** | set size from target CI: ±3% ≈ 1068 golden tasks | 31 |
| **Cost** | price the whole design; compaction saves ~$18.8/run@T=100 | 32 |
| **Safety** | each untrusted channel (23/25/30) needs a screen; depth bounds escape; one open channel = 100% | 33 |

Reading the ledger top-to-bottom for a given task = a complete, costed design. This ledger IS the
capstone payload (the agentic counterpart of 21's toolkit-usage matrix).

## 4. The decision tree (forced moves by task shape)
- **Short single-shot Q&A (no tools, no untrusted data):** just `22`. (Resist over-engineering —
  the 27 YAGNI lesson generalized to the whole stack.)
- **+ external actions:** add `23` tools (+ arg-schema validation) and, if any tool output is
  attacker-influenceable, `33` safety on that channel.
- **+ long horizon (per-call window overflow):** add `24` compaction; if duration/value high, `26`
  persistence/resume.
- **+ large/changing knowledge:** add `25` memory and/or `30` RAG grounding (and `33` on the
  retrieved-passage channel).
- **+ parallelizable big task (benefit > coordination + tail):** add `27` orchestration (else stay
  single-agent).
- **+ external tool ecosystem:** add `29` MCP/connectors.
- **Always, before deploy:** `31` eval (with a budgeted CI) + tracing; `32` cost accounting/caps;
  `33` defence-in-depth on every untrusted channel + oversight on high-capability actions.

## 5. Cross-cutting reconciliations (the recurring patterns of Part III)
- **The O(T²) loop is the gravity well.** 24 (compaction), 25 (offload), 30 (retrieve-not-stuff),
  32 ($ of it), and 28's budget stage are all responses to the SAME quadratic from 22. Bounding it
  is the first forced move of every long-running design.
- **Selection/compounding error `1-(1-q)^N` recurs** as tool-selection error (23), join-tail (27),
  and multi-step failure (28) — one identity, three costumes (the 13/20/21 identity, agentic).
- **"Exactly-once-effect" recurs** as idempotent tool retry (23), idempotent replay on resume (26),
  and dedup in orchestration (27) — the 17/21 pattern over agent steps.
- **Defence-in-depth / blast-radius recurs** as 18 guardrails (31), 20 cells → sandboxing (33),
  and the eval/over-refusal tradeoff (31/33) — the 18/20 toolkit re-aimed at a stochastic actuator
  and an adversary.
- **Trust triad 31/32/33:** is it correct? / what does it cost? / can it be attacked & safely
  improve? Every deployable design budgets all three.

## 6. Build-your-own (the capstone deliverable)
- **The agentic design canvas**: the §2 method as a fill-in template (task → arithmetic → forced
  primitives w/ cross-links → cross-cut budget ledger → failure modes + tradeoffs).
- **A budget calculator**: input T/parallelism/untrusted-channels/correctness-bar → loop $/turn,
  compaction trigger, checkpoint interval I*, Amdahl ceiling, eval set size, $/run, safety-layer
  count (wraps `_recompute.py`'s formulas).
- **The capstone harness (28)** assembled end-to-end with every cross-cut budgeted and every
  untrusted channel screened (33), evaluated with a CI (31), and cost-capped (32).

## 7. Provenance summary
- **NO new primary** (capstone application, like 21). Every budget cross-links to a line-verified
  anchor: 22 (loop, ReAct), 24 (compaction, CoT), 25 (AMAT, MemGPT+Reflexion), 26 (checkpoint knee,
  Postgres-WAL), 27 (Amdahl/tail/YAGNI), 31 (eval CI, SWE-bench), 32 ($), 33 (defence-in-depth,
  Greshake).
- **RECOMPUTED:** `_recompute.py` (13/13).
- **REUSED:** 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 (+ the Part I/II canon beneath them).
- **`[UNVERIFIED]` carry-forward:** NONE new — 34 inherits each home sub-course's already-logged
  residual gaps (none load-bearing for the design method, which is the recomputed forced-moves logic).

---
**34 reconciled.** **PART III (Agentic System Design, 22-34) is COMPLETE** — all twelve primitive
sub-courses (22-33) plus this capstone design course (34) are reconciled + factchecked, math
recomputed, primaries anchored. With Part I (01-12) and Part II (13-21) already complete, **the
entire Phase-1 research corpus for the spine (01-34) is now done.** Next batch: **Phase 1 batch 4 —
the Appendices (A-O)**, OR proceed to Phase 2 (per-sub-course `_structure.md`, which STOPS for
sign-off). No chapters yet.
