# 34 — Design Your Own Agentic System · _structure.md

**Identity:** the **GRAND CAPSTONE of Part III** — the agentic mirror of 21. It introduces NO new
primitive; it APPLIES the entire 22–33 toolkit to a repeatable design METHOD, exactly as 21 applied
13–20 to six system designs. Where 28 proved "a harness = seven primitives" by *construction*, 34
proves "any agentic system = a sequence of forced moves" by *design method*. This is the last spine
chapter; the reader leaves able to size, cost, secure, and assemble an agentic system from a blank
page.

**Bespoke shape — "a design canvas + a forced-moves decision tree, driven by a cross-cutting budget
ledger."** NOT four clusters, NOT a build progression (that's 28). The thesis (RECOMPUTED): **an
agentic design is a SEQUENCE OF FORCED MOVES — the task's shape + the arithmetic pick the
primitives.** A *small* task (short, single-shot, no untrusted data) forces only `{22 loop}`; a *big*
task (long, multi-source, multi-agent, evaluated) forces the whole stack `{22, 24, 25/30, 26, 27, 31,
32, 33}`. The engineer's job is to see the forcing function and price the tradeoff. NO new primary
(capstone application, like 21). Math recomputed (13/13). The `/build` deliverable: the agentic design
canvas + a budget calculator + the 28 capstone harness assembled end-to-end with every cross-cut
budgeted.

## Dependency position
- **Depends on:** ALL of 22–33 (each is one column of the design ledger / one branch of the decision
  tree) + the Part I/II canon beneath them (13/17/18/19/20/21 patterns recur as agentic identities).
  This is the synthesis chapter — it introduces nothing new.
- **Feeds into:** nothing in the spine (it is the terminal spine chapter) — it feeds the LEARNER, who
  takes the canvas to real systems. The README points new readers here as "the destination."
- **Appendix links DOWN:** M-agentic-papers (every anchor the ledger cross-links to) · N-math (the
  budget arithmetic the calculator wraps) · I/J/L/O (the infra the design runs on). 34 owns the design
  method itself; every primitive's depth lives in its home chapter 22–33.

## Section specs (3–5 lines each)
1. **The thesis: design = a sequence of forced moves (the agentic 21)** — RECOMPUTED: the task's shape
   + the arithmetic pick the primitives, not taste. A small task forces `{22}`; a big task forces the
   whole stack. The chapter's job is to make the forcing functions visible and the tradeoffs priced —
   the same capstone identity as 21, now over the agentic toolkit. Resisting over-engineering (27
   YAGNI, generalized) is half the skill.
2. **The design canvas (the bespoke spine — the agentic mirror of 21's 6-step method)** — a repeatable
   loop: (1) **Define the task** (functional + non-functional: latency/turn budget, correctness bar,
   safety surface, $/run, autonomy level — the non-functionals decide everything); (2) **The
   arithmetic** (RECOMPUTE the budgets the task forces — the §3 ledger); (3) **Pick the primitives**
   (apply the minimal set the bottleneck forces; cross-link + price each); (4) **Compose into the
   harness 28** (loop → tools → context → memory → persistence → orchestration → connectors →
   grounding → trust → cost → safety); (5) **Budget every cross-cut** (no unbounded quadratic, no
   unscreened untrusted channel, no long task without resume, no "it works" without an eval CI); (6)
   **Failure modes + tradeoffs** (what breaks + the explicit cost of every choice).
3. **The cross-cutting budget ledger (RECOMPUTED, `_recompute.py` 13/13 — the capstone payload)** —
   read top-to-bottom for a task = a complete, costed design (the agentic counterpart of 21's
   toolkit-usage matrix):

   | budget | rule | anchor |
   |---|---|---|
   | **Loop** | input cost is O(T²) — the master constraint to bound | 22 |
   | **Context** | per-call window p+g(T−1) overflows → compaction FORCED (O(T²)→O(T)) | 24 |
   | **Memory** | AMAT over tokens; external memory pays when hit-rate high (~2.5× at 0.95) | 25 |
   | **Grounding** | retrieve relevant K, don't stuff the corpus; index = a replica (staleness) | 30 |
   | **Persistence** | checkpoint every I*≈√(2N·c); short task → skip (YAGNI) | 26 |
   | **Orchestration** | Amdahl ceiling 1/s; join tail 1−(1−p)^N=63.4%@N=100; multi-agent LOSES small | 27 |
   | **Eval** | set size from target CI: ±3% ≈ 1067 golden tasks | 31 |
   | **Cost** | price the whole design; compaction saves ~$18.8/run@T=100 | 32 |
   | **Safety** | each untrusted channel (23/25/30) needs a screen; one open channel = 100% | 33 |

4. **The decision tree (forced moves by task shape)** — short single-shot Q&A → just `{22}` (resist
   over-engineering); + external actions → `23` tools (+ arg-schema) and `33` on any attacker-
   influenceable output; + long horizon (window overflow) → `24` compaction, then `26` if duration/
   value high; + large/changing knowledge → `25` and/or `30` (+ `33` on the passage channel); +
   parallelizable big task (benefit > coordination + tail) → `27`; + external tool ecosystem → `29`;
   always before deploy → `31` eval + tracing, `32` cost accounting/caps, `33` defence-in-depth +
   oversight.
5. **The recurring patterns of Part III (cross-cutting reconciliations)** — the **O(T²) loop is the
   gravity well** (24/25/30/32/28's budget stage are all responses to the same 22 quadratic);
   **selection/compounding `1−(1−q)^N`** recurs as tool-selection (23), join-tail (27), multi-step
   failure (28) — one identity, three costumes; **"exactly-once-effect"** recurs as idempotent tool
   retry (23), idempotent replay on resume (26), dedup in orchestration (27); **defence-in-depth /
   blast-radius** recurs as 18 guardrails (31), 20 cells → sandboxing (33); the **trust triad 31/32/33**
   = correct? / cost? / attackable & safely-improving? Every deployable design budgets all three.
6. **Failure modes + tradeoffs (design-level)** — the catalog of what breaks (33 attack surface, 27
   join tail, 20 partial failure) and the explicit cost of every choice (compact vs cache, single vs
   multi-agent, gate-all vs risk-based, autonomy vs oversight). The capstone lesson: a good agentic
   design is the *cheapest* one that meets the non-functionals — no more primitives than the
   arithmetic forces.

## Paired build lab (/build → the capstone deliverable, three artifacts)
- **The agentic design canvas** — the §2 method as a fill-in template (task → arithmetic → forced
  primitives w/ cross-links → cross-cut budget ledger → failure modes + tradeoffs).
- **A budget calculator** — input T / parallelism / untrusted-channels / correctness-bar → loop
  $/turn, compaction trigger, checkpoint interval I*, Amdahl ceiling, eval set size, $/run, safety-
  layer count (wraps `_recompute.py`'s formulas).
- **The capstone harness (28)** assembled end-to-end with every cross-cut budgeted, every untrusted
  channel screened (33), evaluated with a CI (31), and cost-capped (32). Acceptance: the learner can,
  for a NEW task, name every forced move and justify every primitive (and every omission) by the
  arithmetic.

## Diagrams needed
- The design canvas loop (6 steps — the agentic mirror of 21's method).
- The cross-cut budget ledger as a single readable table → "read it top-to-bottom = a costed design."
- The forced-moves decision tree (task shape → which primitives switch on).
- The O(T²) gravity well: 24/25/30/32/28 all pulling on the same quadratic.
- One identity, three costumes: `1−(1−q)^N` as tool-selection / join-tail / multi-step failure.
- The trust triad 31/32/33 as the three mandatory pre-deploy gates.
- A worked example: one big task threaded through the canvas to a complete costed design.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **NO new primary** (capstone application, like 21). Every budget cross-links to a line-verified
  anchor: 22 (loop, ReAct), 24 (compaction, CoT), 25 (AMAT, MemGPT+Reflexion), 26 (checkpoint knee,
  Postgres-WAL), 27 (Amdahl/tail/YAGNI), 30 (retrieve-vs-stuff, RAG), 31 (eval CI, SWE-bench), 32 ($),
  33 (defence-in-depth, Greshake).
- **RECOMPUTED:** `_recompute.py` (13/13) — the forced-moves logic + the full budget ledger.
- **REUSED:** 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 (+ the Part I/II canon beneath them).
- **`[UNVERIFIED]` carry-forward:** NONE new — 34 inherits each home chapter's already-logged residual
  gaps (none load-bearing for the design method, which is the recomputed forced-moves logic). The
  opportunistic owed fetches that touch Part III (DPR → 30) remain blocked and carried in their home
  chapter, not here.
- **Boundary discipline:** every primitive's depth stays in its home chapter 22–33; 34 owns ONLY the
  design method (canvas + ledger + decision tree) and the cross-cutting pattern reconciliations. It is
  a method, not new material.
