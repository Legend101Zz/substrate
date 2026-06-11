# 22 · the-agent-loop — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 22 OPENS **Part III — Agentic System
> Design**. It establishes the foundational primitive of the entire part: **an agent is a control
> loop wrapped around an LLM.** Every later Part III sub-course (23-34) refines exactly one box of
> THIS loop. Bespoke structure: a single control-loop walkthrough (not abstract clusters). Full
> depth: `_research_the-agent-loop.md`. Math: `_recompute.py` (18/18). Primary: ReAct (Yao et al.,
> ICLR 2023). Factcheck: `_factcheck_phase1.md` (0 blockers).

## 1. The one idea
**The model is a component; the loop is the system.** An agent repeatedly assembles context →
calls a model → parses an action → executes it → observes the result → appends → decides to
continue. This is the classic **sense → decide → act** control loop (same shape as an OS scheduler
tick / `epoll` loop / Kafka consumer `poll()` — reuse 04/10/17) with a stochastic next-token
predictor in the "decide" box. Reliability, cost, safety, capability are properties of the **loop
and its plumbing**, not of the weights — which is why all of Part I/II is prerequisite.

## 2. The canonical loop (primary: ReAct)
ReAct is the load-bearing primary: interleave **Thought** (reason) with **Action** (act) and feed
**Observation** (sense) back in. VERIFIED verbatim that this (a) lets reasoning "induce, track,
update plans and handle exceptions," (b) "overcomes ... hallucination and error propagation ... by
interacting with a simple Wikipedia API" (acting grounds reasoning), and (c) beats imitation/RL by
"34% and 10%" with "only one or two in-context examples" (capability lives in the loop structure).
Mental model: **agent loop = Chain-of-Thought + a feedback edge.** CoT is open-loop (can drift);
ReAct closes the loop with observations.

## 3. Anatomy of one iteration → the Part III dependency map
Each box of one turn is owned by a downstream sub-course — this is the spine of Part III:

| box | what happens | owned by |
|---|---|---|
| assemble context | prompt + tools + transcript + memory | **24** context, **25** memory, **30** RAG |
| model call | context → LLM → tokens; cost+latency here | **32** cost, **18** timeout/retry, **20** hedge tail |
| parse decision | extract tool + args (contract parse) | **23** tool contracts/schemas |
| act | run tool / emit answer (side-effecting) | **23** tools, **17** exactly-once-effect, **33** safety |
| observe | capture result/error | **18** errors/timeouts |
| append + decide | grow transcript (a **log**, reuse 09); check termination | **26** persistence/resume |

The growing transcript is an **append-only log** (09): durability + replay (26) + tracing/eval (31)
come for free if you treat loop history as a log.

## 4. Termination is external, layered, and bounded
An LLM loop never halts itself. Termination must be imposed from outside, in layers: success
(terminal action) · **step budget** (the #1 reliability guardrail) · token/cost budget (cost rises
per turn, §5) · wall-clock deadline (reuse 18 deadline-propagation) · no-progress/loop detection
(livelock, reuse 04/11). Theory note: deciding termination in general is undecidable (halting
problem) → we don't predict, we **bound** — the same "bound everything" discipline as 18 (bound
queues) and 20 (bound blast radius).

## 5. The economics (RECOMPUTED — the headline math)
The context is **re-sent every turn and grows every turn**. With prefix `p` and `g` tokens added
per turn, prompt tokens at turn `t` = `p+(t-1)*g` (linear), and cumulative **input** tokens over
`T` turns = `T*p + g*T*(T-1)/2` = **O(T²)**. Verified: T=20 → 135,000 input tokens; g-term grows
4.22x when T doubles 10→20; a naive flat-prompt estimate undercounts 3.38x; window exhaustion at
`T*=floor((W-p)/g)+1`=253 turns for W=128k. **This quadratic is the entire reason 24 (context
engineering/compaction), 25 (memory), and 32 (cost) exist.** Bounds that tame it: step budget →
known worst-case $; per-step retry = floor(deadline/timeout) (reuse 18); loop wall-clock =
max_steps·step_deadline.

## 6. Failure modes (motivate 23-34)
Runaway loop (→ budgets/18) · context overflow (→ 24/25) · malformed action (→ 23 schema+repair) ·
tool error/timeout (→ 18 + observe-and-adapt) · hallucinated tool/args (→ 23 allow-list + 33) ·
error propagation (→ ReAct grounding + 31 + 25 hygiene) · cost blowup (→ 32 + compaction) ·
side-effect double-apply (→ 17 idempotency). **All are systems failures, not model failures.**

## 7. Build-your-own
The capstone harness (28) starts here: the minimal loop + one tool + a step budget + a transcript
log ("the 40-line agent"), then broken on purpose (drop the budget → runaway; oversize the task →
overflow) to motivate every later chapter.

## 8. Provenance summary
- **VERIFIED primary**: ReAct (arXiv 2210.03629) — `meta/fetched_primaries/react-2210.03629.{pdf,txt}`,
  receipt `_VERIFIED_2026-06-10_agentic.md`.
- **RECOMPUTED**: `_recompute.py` (18/18) — token growth, cost, budgets, window exhaustion, retry.
- **REUSED**: 04, 09, 10, 11, 13, 17, 18, 20.
- **`[UNVERIFIED]` carry-forward**: CoT (Wei 2022, arXiv 2201.11903); control-loop/BDI lineage;
  Reflexion (arXiv 2303.11366); provider tool-use docs. None load-bearing for the loop primitive.

---
**22 reconciled.** Part III is now open. Next in dependency order: **23-tools-and-tool-contracts**
(refines the "parse decision" + "act" boxes; primary anchor Toolformer, already fetched).
