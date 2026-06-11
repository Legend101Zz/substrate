# 27 — Planning and Multi-Agent Orchestration · _structure.md

**Identity:** where ONE loop (22) becomes MANY coordinating loops. The load-bearing claim: **a
multi-agent system is a distributed system whose nodes happen to be LLM loops** — its laws are 11
(ordering/consensus), 17 (async/EDA), 20 (resilience/tail), 13 (Amdahl). The moment there's more than
one loop, every Part I/II problem returns.

**Bespoke shape — "a coordination walkthrough that earns each topology, and insists on when NOT to."**
NOT a multi-agent-framework tour. 27 applies the Part I/II toolkit to loops (like 21 applied it to
systems), and its distinctive spine is YAGNI: multi-agent is a SCALING tool, not a capability upgrade —
it wins only when `T_total > T_total/speedup + T_coord`. The arc: planning + topologies → the
coordination economics (Amdahl ceiling, join tail, error compounding, aggregation tax, the
payoff/anti-payoff condition) → shared state needs ordering (11) + async hand-off (17) → failure modes.
No new load-bearing primary (applies the verified toolkit). Math recomputed (16/16). Sixth harness
upgrade.

## Dependency position
- **Depends on:** 22 (the loop being multiplied; the call budget), 11 (ordering/consensus/quorum voting),
  13 (Amdahl over agents), 17 (async hand-off = message passing), 20 (join tail; uncorrelated redundancy),
  14 (partition shared state), 15 (CRDT-merge/quorum), 09 (supervisor/worker = map-reduce log), 18
  (cross-agent retry storm), 24 (aggregation tax = the quadratic at the parent), 25/26 (shared state,
  orphan resume), 31 (verifier/critic preview).
- **Feeds into:** 28 (the supervisor + workers stage), 31 (voting/critic as eval), 34 (design-your-own
  agentic system), 33 (cross-agent isolation).
- **Appendix links DOWN:** M-agentic-papers (planning + debate lineage), L-consensus (voting = quorum),
  N-math (Amdahl/tail). 27 owns the coordination model + YAGNI discipline.

## Chapter specs (3–5 lines each)
1. **The one idea: orchestration is distributed systems with stochastic nodes** — more than one loop ⇒
   every Part I/II problem returns: decomposition, parallel speedup + tail (13/20), aggregation (17),
   shared-write ordering (11), partial failure (20), correctness compounding (13/20/21/23). 27 applies
   those laws to loops — and insists on when NOT to.
2. **Planning + topologies** — a plan is a tree/DAG (leaves=W^D, call-sites=(W^(D+1)−1)/(W−1) = the call
   budget, 22). Styles: decompose-then-execute, interleaved plan-act (ReAct, 22), plan-and-solve
   (UNVERIFIED). Topologies: single loop (default), supervisor/worker (= map-reduce 09/17, the project's
   own constitution topology), pipeline, fan-out, blackboard/shared-state (25+11), debate/vote (11 quorum
   + 31). Topology follows the task's dependency structure (like data-flow shapes in 17/21).
3. **Coordination economics, part 1: speedup & tail** — parallel speedup is Amdahl over agents (13):
   1/(s+(1−s)/P)=3.46×, hard ceiling 1/s=5× (the planner+aggregator is the serial wall). The join is
   gated by the slowest worker (20): P(stall)=1−(1−p)^N = 63.4% at N=100 (the fan-out-tail identity over
   agents). Fix: hedge/backup, join deadline + partial results, cap fan-out.
4. **Coordination economics, part 2: correctness & aggregation** — correctness COMPOUNDS (13/20/21/23):
   end-to-end error 1−(1−q)^N = 64.2% at N=20 (more agents = more chances to be wrong). Fix: majority-of-3
   voting err 0.7% vs 5% (6.9× better, 11 quorum) + a verifier/critic (31) — redundancy buys correctness
   ONLY with independence + a decision rule (like 15 quorum / 20 uncorrelated failure). Aggregation tax
   (24/22): reading N workers = N·r tokens re-sent every supervisor turn (the quadratic at the parent) →
   workers must return COMPACTED summaries (ρ=0.15 → 6.7× less).
5. **When NOT to orchestrate (YAGNI — the headline)** — multi-agent wins only if `T_total > T_total/
   speedup + T_coord`: a big task wins 2.71×, a small task LOSES (coord tax dominates). Default to a
   single loop; orchestrate only for genuinely decomposable, large tasks. Multi-agent is a scaling tool,
   not a capability upgrade.
6. **Shared state needs ordering (11) + async hand-off (17)** — N concurrent writers create C(N,2)
   conflict pairs → use a sequencer/consensus (11), partition the state (14), or CRDT-merge (11/15).
   Hand-offs are message passing (17): at-least-once + idempotency (17/26) + outbox for exactly-once-effect.
7. **Failure modes** — runaway sub-agent (22 budget) · join stall (20 hedge/deadline) · error compounding
   (31 verifier) · aggregation overflow (24 compaction) · shared-state race (11) · cross-agent retry
   storm (18) · orphaned sub-agent on supervisor crash (26 resume) · deadlock (04/11). All
   distributed-systems failures, not model failures.

## Paired build lab (/build → supervisor stage of own-coding-agent-harness, 28)
Add a supervisor to the durable loop (24/25/26): decompose → dispatch worker loops (22/23) → join with
deadline + partial results (20) → aggregate compacted returns (24) → optional vote/critic (31) →
persist plan + sub-results to the WAL (26). Break it: unbounded fan-out → tail explodes; raw returns →
overflow; no voting → compounded error; orchestrate trivial work → slower than one loop. Sixth harness
upgrade (loop → tools → context → memory → persistence → orchestration → …).

## Diagrams needed
- "Orchestration = distributed systems with stochastic nodes" — Part I/II laws returning over loops.
- Plan tree/DAG (leaves W^D, call-sites budget); the topology zoo (single/supervisor/pipeline/fan-out/
  blackboard/debate) keyed to task dependency structure.
- Amdahl over agents (speedup curve + hard ceiling 1/s); join tail 1−(1−p)^N over workers.
- Error compounding 1−(1−q)^N vs majority-of-3 voting (6.9× better); aggregation tax at the parent.
- The YAGNI condition: big task wins vs small task loses (coord tax dominates).
- Shared state: C(N,2) conflict pairs → sequencer/partition/CRDT; hand-off = idempotent message passing.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **REUSED (load-bearing):** 09, 11, 13, 14, 15, 17, 18, 20, 22, 24, 25, 26.
- **RECOMPUTED (16/16):** plan size, Amdahl + ceiling, join tail, aggregation tax, error compounding +
  majority voting, payoff/anti-payoff condition, conflict pairs.
- **`[UNVERIFIED]` carry-forward (none load-bearing for the coordination model):** planning papers
  (Plan-and-Solve 2305.04091, Least-to-Most 2205.10625, Tree-of-Thoughts 2305.10601, ReWOO,
  LLM-Compiler); debate (2305.14325); multi-agent frameworks (AutoGen/CrewAI/LangGraph/MetaGPT/Swarm/
  Anthropic multi-agent); the "single agent often beats multi-agent" community finding. Teach the
  coordination model now; do NOT harden planning-paper or framework specifics until fetched (→ appendix M).
- **Boundary discipline:** ordering/consensus/quorum-voting theory → 11 (+ appendix L); Amdahl/tail math
  → 13/20 (+ appendix N); async hand-off → 17; orphan resume → 26; verifier/critic → 31; planning/debate
  papers → appendix M. 27 owns the coordination model + YAGNI.
