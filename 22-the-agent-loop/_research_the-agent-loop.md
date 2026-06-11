# 22 · the-agent-loop — section brief (control-loop walkthrough)

> Phase-1 brief (NO course prose). 22 opens **Part III — Agentic System Design**. It is the
> FOUNDATIONAL primitive of the whole part: an agent is a **control loop** wrapped around an LLM.
> Bespoke structure: a single-loop walkthrough (anatomy → one iteration → termination → failure),
> NOT abstract source clusters and NOT the 13-20 four-cluster shape. Everything downstream
> (23 tools, 24 context, 25 memory, 26 resume, 27 orchestration) is a refinement of one box in
> THIS loop. Primary anchor: ReAct (Yao et al., ICLR 2023). Math: `_recompute.py`.

Cross-link map (this loop is built out of Part I/II primitives):
- the loop itself ↔ **04** OS scheduler loop / event loop (10 nginx), **17** consumer poll loop
- "observe" = I/O ↔ **03** networking (tool calls are RPCs), **18** timeouts/retries on each call
- step/cost budget ↔ **13** capacity + **18** rate-limiting/budgets; tail of a step ↔ **20**
- determinism/replay of the trace ↔ **09** the log (the transcript IS an append-only log)

---

## 1. The primitive — what an agent actually is
An **agent** is not a model. It is a **control loop** that repeatedly: (1) assembles a context,
(2) calls a model to get the next action, (3) executes that action against the world, (4) observes
the result, (5) appends it to the context, and (6) decides whether to continue. Strip away the
branding and it is the classic **sense → decide → act** control loop (same shape as an OS
scheduler tick, an `epoll` event loop in 10, or a Kafka consumer `poll()` loop in 17) — except the
"decide" box is a stochastic next-token predictor instead of deterministic code.

The thesis of Part III: **the model is a component; the LOOP is the system.** Reliability,
cost, safety, and capability are properties of the loop and its surrounding plumbing — not of the
weights. This is why "system design" applies: the agent is a distributed, stateful, failure-prone
system whose central worker happens to be an LLM.

## 2. The canonical loop — ReAct (primary: Yao et al., ICLR 2023, arXiv 2210.03629)
ReAct is the load-bearing primary for this sub-course. Its contribution is exactly the loop:
**interleave reasoning traces (Thought) with task-specific Actions, and feed the Observation back
in.** Verbatim (abstract, VERIFIED in `meta/fetched_primaries/react-2210.03629.txt`):

> "we explore the use of LLMs to generate both reasoning traces and task-specific actions in an
> interleaved manner ... reasoning traces help the model induce, track, and update action plans
> as well as handle exceptions, while actions allow it to interface with and gather additional
> information from external sources such as knowledge bases or environments."

The trajectory is the now-ubiquitous cycle:

```
Thought:      reason about the current state / what's needed next   (the "decide")
Action:       emit a structured call to a tool/environment          (the "act")
Observation:  the tool/environment returns a result                 (the "sense")
... repeat ...
Answer:       terminal action that ends the loop
```

Two empirical results worth teaching (VERIFIED, abstract):
- ReAct **"overcomes prevalent issues of hallucination and error propagation in chain-of-thought
  reasoning by interacting with a simple Wikipedia API"** — i.e. *acting* grounds *reasoning*.
  This is the WHY of tools (handed to 23): reasoning alone drifts; an observation pins it to reality.
- ReAct beats imitation/RL by **"an absolute success rate of 34% and 10%"** (ALFWorld, WebShop)
  **"with only one or two in-context examples"** — the loop + a couple of exemplars > task-specific
  training. The capability is in the *loop structure*, not in fine-tuning.

Contrast to set up later chapters: **Chain-of-Thought** reasons but never observes (open loop, can
hallucinate); **ReAct** closes the loop with observations (grounded). The agent loop = CoT + a
feedback edge.

## 3. Anatomy of one iteration (the box diagram every later chapter refines)
One turn of the loop, with the downstream owner of each box in brackets:
1. **Assemble context** — system prompt + task + tool schemas + running transcript + retrieved
   memory. [24 context engineering; 25 memory; 30 RAG]
2. **Model call** — send context → LLM → token stream out. Cost + latency live here. [32 cost; 18
   timeout/retry on the call; 20 hedging the tail]
3. **Parse the decision** — extract the next action (tool name + arguments) from the output. This
   is a *contract-parsing* step and a major failure surface. [23 tool contracts/schemas]
4. **Act** — execute the chosen tool / emit the final answer. Side-effecting; needs idempotency +
   permissions. [23 tools; 17 exactly-once-effect for side-effecting tools; 33 safety]
5. **Observe** — capture the tool result (or error) as the next Observation. [18 errors/timeouts]
6. **Append + decide-to-continue** — append (Thought, Action, Observation) to the transcript;
   check the termination condition; loop or halt. [26 state/persistence of the transcript]

The transcript that grows across iterations is an **append-only log** (reuse 09): ordered,
immutable per entry, replayable. That single observation is the seed of 26 (persistence/resume)
and 31 (tracing/eval) — you get durability and observability for free if you treat the loop's
history as a log.

## 4. Termination — the part everyone gets wrong
An LLM control loop does **not** halt on its own; it will happily emit "Thought:" forever. The
loop needs **explicit, layered termination**:
- **Success**: the model emits the terminal action (final answer / `done`).
- **Step budget**: hard cap on iterations (`max_steps`). The single most important reliability
  guardrail — without it, one bad trajectory burns unbounded tokens/dollars.
- **Token / cost budget**: cumulative context grows every turn (§6), so cost per turn *rises*;
  cap total tokens or total $ (handoff to 32; budget enforcement is 18's job applied to spend).
- **Wall-clock / deadline**: propagate a deadline through the loop (reuse 18 deadline-propagation).
- **No-progress / loop detection**: detect repeated identical (Action, Observation) pairs or
  oscillation; abort or escalate. This is the agent analogue of livelock (reuse 04/11 intuition).

Connection to theory: deciding *in general* whether the loop will terminate is undecidable (the
halting problem) — so we do NOT try; we impose **external bounds** (steps, tokens, time). This is
the same move as 18 (you can't predict overload, so you bound queues) and 20 (you can't prevent
all failure, so you bound blast radius). **Bounded everything** is the recurring discipline.

## 5. Failure modes (what breaks in a raw loop — the motivation for 23-34)
| failure | mechanism | where it's fixed |
|---|---|---|
| **Infinite / runaway loop** | no terminal action ever emitted | step + cost + time budgets (§4); 18 |
| **Context overflow** | transcript grows past the context window (§6) | 24 context engineering, compaction; 25 memory |
| **Malformed action** | model output doesn't match the tool contract | 23 schemas + validation + repair |
| **Tool error / timeout** | the world fails (network, 5xx, slow) | 18 timeout/retry/breaker; observe-the-error + let the loop adapt (ReAct's "handle exceptions") |
| **Hallucinated tool/args** | model invents a tool or argument | 23 strict schema + allow-list; 33 safety |
| **Error propagation** | one bad observation poisons all later turns | ReAct grounding; 31 eval/guardrails; 25 memory hygiene |
| **Cost blowup** | quadratic token growth (§6) unbounded | 32 cost-obs; 24 compaction; budgets |
| **Side-effect double-apply** | a retried side-effecting tool runs twice | 17 idempotency / exactly-once-effect keys |

Every one of these is a *systems* failure, not a *model* failure — which is the whole reason Part I/II
exists before Part III.

## 6. The quantitative core (all RECOMPUTED in `_recompute.py`)
The loop's economics are dominated by one fact: **the context is re-sent every turn, and it grows
every turn.** Let the transcript add `g` tokens per turn (Thought+Action+Observation). With a fixed
prefix `p` (system+tools+task), the prompt tokens at turn `t` are `p + (t-1)*g`. Over `T` turns the
total *input* tokens billed are:

```
sum_{t=1..T} [ p + (t-1)*g ]  =  T*p + g*T*(T-1)/2     →  O(T^2) in the transcript term.
```

That quadratic is THE reason context engineering (24), compaction, and memory (25) exist. Things
recomputed:
- per-turn and cumulative **input-token growth** (linear per turn, quadratic cumulative);
- **cost-per-call** and **cumulative $** under example input/output token prices;
- **step-budget → worst-case cost** (the cap that bounds the quadratic);
- **context-window exhaustion turn** `T* = floor((W - p)/g) + 1` for a window `W`;
- **deadline / retry budget** of a single step (reuse 18: effective attempts under a per-step
  timeout and a step deadline).

These are the numbers a designer needs to size an agent the way 13 sizes a service.

## 7. Build-your-own target
The capstone harness (28) starts HERE: implement the minimal loop —
`while not done and steps < budget: ctx = assemble(); action = parse(call(ctx)); obs = run(action);
transcript.append(...)`. Everything in 23-27 is then a drop-in upgrade to one box. A good lab is
"the 40-line agent": raw loop + one tool + a step budget + a transcript log, then break it on
purpose (remove the budget → runaway; oversize the task → context overflow) to motivate the rest.

## 8. Sources & provenance
- **PRIMARY (fetched + verified this session)**: ReAct, Yao et al., ICLR 2023, arXiv 2210.03629 —
  `meta/fetched_primaries/react-2210.03629.{pdf,txt}`; receipt
  `meta/fetched_primaries/_VERIFIED_2026-06-10_agentic.md`. Anchors §2 (the loop, grounding,
  34%/10%), §3, §5 (handle-exceptions).
- **REUSED (line-verified Part I/II)**: 04 (scheduler/event loop), 09 (the log = transcript),
  10 (event loop), 13 (capacity/sizing), 17 (consumer loop, idempotency/exactly-once-effect),
  18 (timeout/retry/deadline/budgets), 20 (tail/blast radius), 11 (livelock/halting intuition).
- **RECOMPUTED**: `_recompute.py` (token growth, cost, budgets, window exhaustion, step retry).
- **`[UNVERIFIED]` (carry-forward — do NOT harden into prose):**
  - Chain-of-Thought (Wei et al., NeurIPS 2022, arXiv 2201.11903) — referenced as the open-loop
    contrast; not fetched this session.
  - "Agent" framing as control loop is the author's synthesis grounded in 04/17 + ReAct; the
    specific "sense-decide-act" lineage (classic control theory / Brooks subsumption / BDI agents)
    is not separately primary-sourced.
  - Reflexion (Shinn et al., 2023, arXiv 2303.11366) and self-reflection loops — deferred to 25/31.
  - Provider "agent loop" / tool-use docs (OpenAI, Anthropic) — deferred to 23/29.
