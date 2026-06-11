# 22 — The Agent Loop · _structure.md

**Identity:** the OPENING of Part III — Agentic System Design. It establishes the one primitive the
entire part refines: **an agent is a control loop wrapped around an LLM.** The model is a component;
the loop is the system. Every later sub-course (23–34) owns exactly one box of THIS loop.

**Bespoke shape — "one loop, walked box by box, then broken on purpose."** NOT abstract clusters
and NOT a survey. A single control-loop walkthrough: introduce the loop (sense→decide→act, the same
shape as an OS scheduler tick / epoll / Kafka poll() — reuse 04/10/17, with a stochastic next-token
predictor in the decide box), walk one iteration box by box (each box names its downstream owner =
the dependency map for all of Part III), establish that termination is external + bounded, derive
the O(T²) economics that motivate half of Part III, then catalogue the failure modes (all are
SYSTEMS failures, not model failures) and build the 40-line agent. ReAct is the load-bearing primary
(VERIFIED). Math recomputed (18/18). This is the pivot from classical systems to agentic systems.

## Dependency position
- **Depends on:** ALL of Part I/II — 04 (control loop / scheduler tick), 09 (transcript = append-only
  log), 10 (epoll loop), 11 (livelock/no-progress), 13 (the O(T²) is a capacity problem), 17 (poll()/
  exactly-once-effect), 18 (timeout/retry/deadline-propagation bounds), 20 (hedge the model-call tail).
- **Feeds into:** EVERY Part III sub-course — each refines one box: assemble→24/25/30, model-call→
  32/18/20, parse→23, act→23/17/33, observe→18, append+decide→26; eval/tracing→31. The 40-line agent
  is the seed of the 28 capstone.
- **Appendix links DOWN:** M-agentic-papers (ReAct/CoT/Reflexion lineage), I-sandboxing (the act box's
  blast radius). 22 owns the loop primitive itself.

## Chapter specs (3–5 lines each)
1. **The one idea: the model is a component, the loop is the system** — an agent repeatedly assembles
   context → calls a model → parses an action → executes → observes → appends → decides. Classic
   sense→decide→act with a stochastic decide box. Reliability/cost/safety/capability are properties of
   the LOOP and its plumbing — which is why all of Part I/II is prerequisite.
2. **The canonical loop: ReAct** — interleave Thought (reason) + Action (act) + Observation (sense).
   VERIFIED: reasoning lets the agent "induce, track, update plans and handle exceptions"; acting
   "overcomes hallucination and error propagation" by grounding in real observations; beats imitation/
   RL by 34%/10% with one or two in-context examples — capability lives in the loop STRUCTURE. Mental
   model: agent loop = Chain-of-Thought + a feedback edge (CoT is open-loop and can drift).
3. **Anatomy of one iteration → the Part III dependency map** — walk each box of one turn and name its
   downstream owner (assemble→24/25/30, model-call→32/18/20, parse→23, act→23/17/33, observe→18,
   append+decide→26). The growing transcript is an APPEND-ONLY LOG (09): durability + replay (26) +
   tracing/eval (31) come for free if you treat loop history as a log. This table is the spine of Part III.
4. **Termination is external, layered, and bounded** — an LLM loop never halts itself. Impose
   termination in layers: success (terminal action) · step budget (the #1 reliability guardrail) ·
   token/cost budget · wall-clock deadline (18) · no-progress/loop detection (livelock, 04/11). Theory:
   general termination is undecidable (halting problem) → we don't predict, we BOUND (same discipline
   as 18 bound-queues, 20 bound-blast-radius).
5. **The economics: the O(T²) quadratic** — context is RE-SENT every turn and GROWS every turn. Prompt
   at turn t = `p+(t−1)g`; cumulative input over T turns = `T·p + g·T(T−1)/2` = **O(T²)** (VERIFIED:
   T=20→135k tokens; flat estimate undercounts 3.38×; window exhausts at `T*=⌊(W−p)/g⌋+1`=253 for
   W=128k). THIS quadratic is the entire reason 24 (compaction), 25 (memory), and 32 (cost) exist.
6. **Failure modes = systems failures** — runaway loop (→budgets/18) · context overflow (→24/25) ·
   malformed action (→23 schema+repair) · tool error/timeout (→18 + observe-and-adapt) · hallucinated
   tool/args (→23 allow-list + 33) · error propagation (→ReAct grounding + 31 + 25 hygiene) · cost
   blowup (→32 + compaction) · side-effect double-apply (→17 idempotency). None are MODEL failures.

## Paired build lab (/build → the seed of own-coding-agent-harness, 28)
The "40-line agent": minimal loop + one tool + a step budget + a transcript log. Then break it on
purpose to motivate every later chapter — drop the step budget → runaway loop; oversize the task →
context overflow at the recomputed exhaustion turn. This is Stage 0 of the 28 build progression.

## Diagrams needed
- The sense→decide→act loop with the stochastic decide box (and its OS-scheduler/epoll/Kafka-poll twins).
- One-iteration anatomy with each box labeled by its downstream Part III owner (the dependency map).
- The transcript as an append-only log (durability/replay/tracing for free).
- Termination layers (success/step/cost/deadline/no-progress) stacked as bounds.
- The O(T²) growth curve (per-turn prompt + cumulative) with the window-exhaustion turn marked.
- Failure-mode map: each failure → the downstream sub-course that fixes it.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED primary:** ReAct (arXiv 2210.03629; `meta/fetched_primaries/react-2210.03629.*`, receipt
  `_VERIFIED_2026-06-10_agentic.md`) — Thought/Action/Observation, the 34%/10% gains, grounding-beats-
  hallucination, capability-in-loop-structure.
- **RECOMPUTED (18/18):** token growth, cost, budgets, window exhaustion, retry counts.
- **`[UNVERIFIED]` carry-forward (none load-bearing for the loop primitive):** CoT (Wei 2022,
  2201.11903 — later VERIFIED as 24's primary, reconcile at draft); control-loop/BDI lineage; Reflexion
  (2303.11366 — later VERIFIED in 25, reconcile); provider tool-use docs. Teach the loop now; do NOT
  harden lineage attributions until reconciled.
- **Boundary discipline:** each box's depth lives in its owner sub-course (23–34); ReAct/CoT/Reflexion
  paper depth → appendix M; the act box's sandbox → appendix I. 22 owns ONLY the loop primitive + the
  economics + the dependency map.
