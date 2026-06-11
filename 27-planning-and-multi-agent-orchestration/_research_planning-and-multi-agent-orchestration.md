# 27 · planning-and-multi-agent-orchestration — research brief (full depth)

> Phase-1 research brief (NO course prose; briefs only). 27 is where **one loop (22) becomes many
> coordinating loops**. Load-bearing insight: **a multi-agent system is a distributed system whose
> nodes happen to be LLM loops** — so its laws are 11 (consensus/ordering), 17 (async/EDA), and 20
> (resilience/tail), not new agent magic. Bespoke structure: a **coordination walkthrough**
> (planning → topologies → fan-out/join → aggregation → correctness → when-not-to), NOT abstract
> clusters. Math: `_recompute.py` (16/16). Anchors: reuse of line-verified 11/13/17/20 + ReAct (22)
> for the per-agent loop. Factcheck: `_factcheck_phase1.md`.

---

## 0. Scope and the one-sentence thesis
**Orchestration is distributed systems with stochastic nodes.** Once you have more than one agent
loop, every hard problem you already solved in Part I/II comes back: decomposition (the plan),
parallel speedup and its tail (13/20), aggregation/joins (17), ordering of shared writes (11),
partial failure (20), and end-to-end correctness compounding (13/20/21/23). 27's job is to apply
those laws to loops — and, crucially, to know **when not to** orchestrate (YAGNI: most tasks are a
single loop).

Two layers:
- **Intuitive:** a manager breaks a job into pieces, hands them to workers, and combines the
  results. The manager and workers are all agent loops (22).
- **Mechanism:** a supervisor loop decomposes a task into a plan (tree/DAG), dispatches sub-tasks to
  worker loops (sync or async, 17), waits on a join gated by the slowest worker (20), aggregates
  compacted results (24), and resolves ordering/conflicts on shared state (11).

---

## 1. Planning = decomposition (RECOMPUTED §1)
A plan is a tree/DAG of sub-tasks. With fan width `W` per level and depth `D`: leaves = `W^D`, total
nodes (plan + execute call sites) = `(W^(D+1)−1)/(W−1)` (recomputed: W=3,D=2 → 9 leaves, 13 nodes).
That node count IS the model-call budget — planning isn't free; deeper/wider plans cost more calls
(22 economics) before any work happens. Planning styles (structure-bearing):
- **Decompose-then-execute** (plan upfront, then run) — cheap to reason about, brittle to surprises.
- **Interleaved plan-act** (ReAct, 22) — re-plan as observations arrive; robust, more calls.
- **Plan-and-solve / least-to-most** — explicit subgoal ordering `[UNVERIFIED]` (community methods).
The plan is itself context the supervisor must hold in its window (24 budget) and persist (26 WAL).

## 2. Topologies (structure-bearing)
- **Single loop** — the default; orchestrate nothing until you must (§6).
- **Supervisor / worker (one level)** — the project's own constitution topology: a supervisor
  decomposes + dispatches + aggregates; workers are stateless-ish loops. Matches map-reduce (09/17).
- **Pipeline / chain** — output of one agent feeds the next; correctness compounds (§5).
- **Fan-out / parallel** — N workers on independent sub-tasks; speedup + tail (§3, §4).
- **Blackboard / shared state** — agents read/write shared memory (25); needs ordering (§7, 11).
- **Debate / vote** — k agents answer, majority/critic decides (§5, reuse 11 quorum + 31).
Topology is a design choice driven by the dependency structure of the task, exactly like choosing a
data-flow shape in 17/21.

## 3. Parallel speedup is Amdahl over agents (RECOMPUTED §2 — reuse 13)
Fan-out only speeds the parallelizable fraction. With serial fraction `s` (planning + final
aggregation can't parallelize) over `P` workers: speedup = `1/(s+(1−s)/P)` (recomputed 3.46× at
s=0.2,P=9), with a hard **ceiling 1/s = 5×** even with infinite agents. So adding workers has sharp
diminishing returns; the planner+aggregator is the serial wall (same lesson as 13 scaling).

## 4. The join is gated by the slowest worker (RECOMPUTED §3 — reuse 20)
A supervisor waiting for **all** N workers finishes when the **slowest** returns. If each worker
independently exceeds latency `L` with prob `p`, then P(join stalls) = `1−(1−p)^N` — the 20
fan-out-tail identity, now over agents: p=0.01 → 9.6% at N=10, **63.4% at N=100**. This is why
large fan-outs feel slow even when each worker is usually fast. Mitigations are 20 verbatim: **hedge/
backup** the slow worker, set a **join deadline** and accept **partial results**, or cap fan-out.

## 5. Correctness compounds across agents (RECOMPUTED §5 — reuse 13/20/21/23)
If each of N agents/steps is independently correct w.p. `(1−q)`, the whole pipeline is correct w.p.
`(1−q)^N` → end-to-end error `1−(1−q)^N` grows with N (q=0.05 → 22.6% at N=5, **64.2% at N=20**).
This is the same identity as 23's selection compounding and 20's fan-out, now over the orchestration
DAG — **more agents is more chances to be wrong, not automatically more right.** Fix (reuse 11/20/
31): **voting/quorum** — majority-of-3 is wrong only at `3q²(1−q)+q³` = 0.7% vs 5% single (**6.9×
better**); plus a verifier/critic agent (handoff to 31). Redundancy buys correctness only with
independence + a decision rule, exactly like replication needs quorum (15) and resilience needs
uncorrelated failures (20).

## 6. The aggregation tax (RECOMPUTED §4 — reuse 24/22)
The supervisor must read every worker's result: N·r tokens into the supervisor's context, re-sent
every supervisor turn (the 22 quadratic, now at the parent). Recomputed: 9 workers × 800 = 7200 tok;
**compacting** each worker's return (24, ratio ρ=0.15) cuts it to 1080 tok (6.7× less). Design rule:
**workers return compacted summaries, not raw transcripts** — orchestration without compaction
re-creates the context-overflow problem one level up.

## 7. When NOT to orchestrate (RECOMPUTED §6 — YAGNI)
Multi-agent wins **only if** parallel time saved > coordination tax: `T_total >
T_total/speedup + T_coord`. Recomputed: a big task (T=100) wins 2.71×; a small task (T=10) **loses**
(11.5 > 10) because planning+aggregation+comms overhead dominates. The discipline: **default to a
single loop (22); orchestrate only when the task is genuinely decomposable and large enough to repay
the tax.** Multi-agent is a scaling tool, not a capability upgrade.

## 8. Shared state needs ordering (RECOMPUTED §7 — reuse 11)
Agents writing shared state (blackboard/memory 25) race: N concurrent writers create `C(N,2)`
conflict pairs (N=5 → 10). Fixes are 11 verbatim: a **single sequencer** for total order, or
consensus, or partition the state so each agent owns a shard (14), or use CRDT-style merges (11/15).
Async hand-offs between agents are message passing (17): at-least-once + idempotency (17/26) for
reliable dispatch, an outbox for exactly-once-effect.

## 9. Failure modes (tie-back)
Runaway sub-agent (per-agent budget, 22) · join stall (slow worker → §4, 20 hedge/deadline) · error
compounding (→§5, 31 verifier) · aggregation overflow (→§6, 24 compaction) · shared-state race
(→§8, 11) · cascading failure (one agent's retries storm a shared tool → 18 backpressure) ·
orphaned sub-agent on supervisor crash (→26 resume + reconciliation) · deadlock (agents waiting on
each other → 04/11 livelock detection). **All are distributed-systems failures, not model failures.**

## 10. Build-your-own (toward the 28 capstone)
Add a **supervisor** to the durable loop (24/25/26): decompose → dispatch worker loops (each a 22/23
loop) → join with a deadline + partial results (20) → aggregate compacted returns (24) → optional
vote/critic (31) → persist the plan + sub-results to the WAL (26). Break it: unbounded fan-out →
join tail explodes; raw returns → supervisor overflow; no voting → compounded error; orchestrate a
trivial task → slower than one loop. Sixth harness upgrade (loop → tools → context → memory →
persistence → **subagents/orchestration** → budgets).

## 11. Sources & provenance
- **REUSED (line-verified Part I/II) — the load-bearing content:** 09 (the log, map-reduce shape),
  11 (ordering, sequencer, consensus, quorum/voting, livelock), 13 (Amdahl, scaling ceiling), 14
  (partition shared state), 15 (replication/quorum analogy), 17 (async/EDA, message passing,
  at-least-once, outbox), 18 (backpressure, retry storms), 20 (fan-out tail, hedging, deadlines,
  partial results, correlated failure), 22 (the per-agent loop, budgets, quadratic), 24
  (compaction/aggregation tax), 25 (shared memory/blackboard), 26 (persist plan + resume).
- **RECOMPUTED:** `_recompute.py` (16/16) — plan size, Amdahl speedup+ceiling, join tail, aggregation
  tax, error compounding + majority voting, payoff/anti-payoff condition, conflict pairs.
- **`[UNVERIFIED]` carry-forward (do NOT harden into prose):**
  - ReAct/Reflexion already VERIFIED (22/25); planning-specific papers NOT fetched: Plan-and-Solve
    (arXiv 2305.04091), Least-to-Most (arXiv 2205.10625), Tree of Thoughts (arXiv 2305.10601),
    ReWOO, LLM-Compiler.
  - Multi-agent frameworks (AutoGen, CrewAI, LangGraph, MetaGPT, OpenAI Swarm/Agents SDK,
    Anthropic multi-agent research system) — vendor/idiom, not primary.
  - "Society of Mind" / debate (Du et al. 2023, arXiv 2305.14325) — not fetched.
  - Empirical "multi-agent often underperforms a good single agent" claims — community finding,
    grounded here only by the recomputed payoff condition (§7), not a fetched study.
