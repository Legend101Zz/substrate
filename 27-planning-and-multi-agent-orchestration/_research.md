# 27 · planning-and-multi-agent-orchestration — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 27 is where **one loop (22) becomes many
> coordinating loops**. Load-bearing claim: **a multi-agent system is a distributed system whose
> nodes happen to be LLM loops** — its laws are 11 (ordering/consensus), 17 (async/EDA), 20
> (resilience/tail), 13 (Amdahl). Bespoke structure: a coordination walkthrough. Full depth:
> `_research_planning-and-multi-agent-orchestration.md`. Math: `_recompute.py` (16/16). No new
> load-bearing primary (applies the Part I/II toolkit, like 21). Factcheck: `_factcheck_phase1.md`
> (0 blockers).

## 1. The one idea
**Orchestration is distributed systems with stochastic nodes.** The moment there's more than one
loop, every Part I/II problem returns — decomposition, parallel speedup + tail (13/20), aggregation
(17), shared-write ordering (11), partial failure (20), correctness compounding (13/20/21/23). 27
applies those laws to loops, and insists on **when not to** orchestrate (YAGNI).

## 2. Planning + topologies
A plan is a tree/DAG: leaves=W^D, call-sites=(W^(D+1)−1)/(W−1) (the call budget, 22). Styles:
decompose-then-execute, interleaved plan-act (ReAct, 22), plan-and-solve `[UNVERIFIED]`. Topologies:
single loop (default), supervisor/worker (the project's own constitution topology = map-reduce 09/17),
pipeline, fan-out, blackboard/shared-state (25 + 11), debate/vote (11 quorum + 31). Topology follows
the task's dependency structure, like data-flow shapes in 17/21.

## 3. The coordination economics (RECOMPUTED — the headlines)
- **Parallel speedup is Amdahl over agents (13):** 1/(s+(1−s)/P)=3.46×, hard ceiling 1/s=5×; the
  planner+aggregator is the serial wall.
- **The join is gated by the slowest worker (20):** P(stall)=1−(1−p)^N = **63.4% at N=100** — the
  fan-out-tail identity over agents. Fix: hedge/backup, join deadline + partial results, cap fan-out.
- **Correctness compounds (13/20/21/23):** end-to-end error 1−(1−q)^N = **64.2% at N=20** — more
  agents = more chances to be wrong. Fix: majority-of-3 voting err 0.7% vs 5% (**6.9× better**, 11
  quorum) + a verifier/critic (31). Redundancy buys correctness only with independence + a decision
  rule (like 15 quorum / 20 uncorrelated failure).
- **Aggregation tax (24/22):** reading N workers = N·r tokens re-sent every supervisor turn (the
  quadratic at the parent); workers must return **compacted** summaries (ρ=0.15 → 6.7× less).
- **When NOT to orchestrate (YAGNI):** multi-agent wins only if `T_total > T_total/speedup +
  T_coord` — a big task wins 2.71×, a small task LOSES (coord tax dominates). Default to a single
  loop; orchestrate only for genuinely decomposable, large tasks. Multi-agent is a scaling tool, not
  a capability upgrade.

## 4. Shared state needs ordering (11) + async hand-off (17)
N concurrent writers create C(N,2) conflict pairs → use a sequencer/consensus (11), partition the
state (14), or CRDT-merge (11/15). Hand-offs are message passing (17): at-least-once + idempotency
(17/26) + outbox for exactly-once-effect.

## 5. Failure modes
Runaway sub-agent (22 budget) · join stall (20 hedge/deadline) · error compounding (31 verifier) ·
aggregation overflow (24 compaction) · shared-state race (11) · cross-agent retry storm (18) ·
orphaned sub-agent on supervisor crash (26 resume) · deadlock (04/11). **All distributed-systems
failures, not model failures.**

## 6. Build-your-own
Add a **supervisor** to the durable loop (24/25/26): decompose → dispatch worker loops (22/23) →
join with deadline + partial results (20) → aggregate compacted returns (24) → optional vote/critic
(31) → persist plan + sub-results to the WAL (26). Break it: unbounded fan-out → tail explodes; raw
returns → overflow; no voting → compounded error; orchestrate trivial work → slower than one loop.
Sixth harness upgrade (loop → tools → context → memory → persistence → **orchestration** → budgets).

## 7. Provenance summary
- **REUSED (load-bearing):** 09, 11, 13, 14, 15, 17, 18, 20, 22, 24, 25, 26.
- **RECOMPUTED:** `_recompute.py` (16/16) — plan size, Amdahl + ceiling, join tail, aggregation tax,
  error compounding + majority voting, payoff/anti-payoff condition, conflict pairs.
- **`[UNVERIFIED]` carry-forward:** planning papers (Plan-and-Solve 2305.04091, Least-to-Most
  2205.10625, Tree-of-Thoughts 2305.10601, ReWOO, LLM-Compiler); debate (2305.14325); multi-agent
  frameworks (AutoGen/CrewAI/LangGraph/MetaGPT/Swarm/Anthropic multi-agent); "single agent often
  beats multi-agent" community finding. None load-bearing for the coordination model.

---
**27 reconciled.** Part III "Phase 1 batch 3" now stands at **24, 25, 26, 27 reconciled** (6 of 13
agentic sub-courses done: 22-27). Next in dependency order: **28-build-your-own-coding-harness** (the
capstone lab that assembles loop→tools→context→memory→persistence→orchestration→budgets/compaction),
then 29 MCP, 30 RAG, 31 eval, 32 cost, 33 safety, 34 design-your-own.
