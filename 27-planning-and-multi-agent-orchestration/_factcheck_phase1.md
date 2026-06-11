# 27 · Phase-1 factcheck — planning-and-multi-agent-orchestration

> Method (same discipline as 13-26): every load-bearing claim is either (a) RECOMPUTED in
> `_recompute.py` (16/16 pass), (b) VERIFIED verbatim against a primary fetched to
> `meta/fetched_primaries/`, (c) REUSED from a previously line-verified Part I/II sub-course, or
> (d) flagged `[UNVERIFIED]` and carried forward. 0 blockers.

## Bespoke structure note
Per the Part III plan: 27 is where one loop becomes many. Its brief is a **coordination
walkthrough** (planning → topologies → fan-out/join → aggregation → correctness → when-not-to), NOT
abstract source clusters and NOT the 13-20 four-cluster shape. Plan-sanctioned.

## Primary fetched THIS session
None. 27's load-bearing content is the APPLICATION of already-line-verified distributed-systems laws
(11/13/17/20) to agent loops, plus the per-agent loop already VERIFIED via ReAct (22). No single new
primary is load-bearing; planning-specific papers + multi-agent frameworks are flagged `[UNVERIFIED]`
(see below) and deferred — none are required for the coordination model, which is built from
recomputation + reuse. This mirrors 21's capstone discipline (apply the toolkit, fetch only the one
genuinely-new primary — and here there is none, because the laws already exist in Part I/II).

## Recomputed claims (`_recompute.py`, 16/16)
- Plan size: leaves=W^D, nodes=(W^(D+1)−1)/(W−1) (3,2 → 9 leaves, 13 call sites). PASS.
- **Amdahl over agents**: speedup 1/(s+(1−s)/P)=3.46×; ceiling 1/s=5× with infinite agents. PASS.
- **Join tail (20)**: P(join stalls)=1−(1−p)^N = 0.0100/0.0956/0.6340 at N=1/10/100. PASS.
- Aggregation tax: N·r=7200 tok; compacted N·r·ρ=1080 (6.7× less, reuse 24). PASS.
- **Correctness compounding**: 1−(1−q)^N = 0.05/0.226/0.642 at N=1/5/20; majority-of-3 err
  3q²(1−q)+q³=0.0073 < 0.05 single (6.9× better, reuse 11 quorum). PASS.
- Payoff condition: big task wins 2.71×; small task LOSES (11.5>10) → YAGNI. PASS.
- Shared-state writers: C(N,2)=10 conflict pairs need ordering (11). PASS.

## Reused (line-verified Part I/II) — the load-bearing content
- 09 the log + map-reduce shape → supervisor/worker dispatch + aggregation.
- 11 ordering/sequencer/consensus/quorum-voting/livelock → shared-state ordering + voting +
  deadlock (§5, §8).
- 13 Amdahl + scaling ceiling → parallel speedup wall (§3).
- 14 partition shared state → conflict avoidance (§8).
- 15 replication/quorum analogy → redundancy-needs-quorum framing (§5).
- 17 async/EDA + message passing + at-least-once + outbox → dispatch/hand-off reliability (§8).
- 18 backpressure + retry storms → cascading failure across agents (§9).
- 20 fan-out tail + hedging + deadlines + partial results + correlated failure → the join (§4) +
  error independence (§5).
- 22 per-agent loop + budgets + quadratic → each node is a 22 loop; aggregation tax (§6).
- 24 compaction → aggregation tax fix (§6); 25 shared memory/blackboard (§2, §8); 26 persist plan +
  resume orphans (§9).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Planning papers NOT fetched: Plan-and-Solve (arXiv 2305.04091), Least-to-Most (arXiv 2205.10625),
  Tree of Thoughts (arXiv 2305.10601), ReWOO, LLM-Compiler.
- Debate/"Society of Mind" (Du et al. 2023, arXiv 2305.14325) — not fetched.
- Multi-agent frameworks (AutoGen, CrewAI, LangGraph, MetaGPT, OpenAI Swarm/Agents SDK, Anthropic
  multi-agent research system) — vendor/idiom, not primary.
- "Multi-agent often underperforms a good single agent" — community finding; grounded here only by
  the recomputed payoff condition (§7), not a fetched study.

## Verdict
27 is honest and orchestration-appropriate: it makes the strong, defensible claim that a multi-agent
system is a distributed system, then proves the coordination economics by RECOMPUTATION (plan size,
Amdahl, join tail, aggregation tax, error compounding + voting, payoff condition, conflict pairs)
and REUSE of line-verified 09/11/13/14/15/17/18/20/22/24/25/26. No new primary is load-bearing; the
planning-paper + framework `[UNVERIFIED]` are enrichment, not foundation, and are carried forward for
Phase 2. Reconcile into `_research.md`.
