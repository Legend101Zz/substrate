# 11 — Distributed Systems Foundations · _structure.md

**Identity:** the theory floor for everything distributed. One argument, proven step by step:
a distributed system has no free shared "now," so every guarantee must be manufactured by a
protocol — and every protocol pays in latency, availability, or messages. The conceptual
keystone of Part II.

**Bespoke shape — "one argument, proven in a chain."** NOT a topic list and NOT
component-by-component. It is a single logical argument where each chapter is a link the next
one needs: *what order means* (causality) → *how to track it* (vector clocks) → *what timing
makes problems solvable* (models, FLP) → *what contracts replication offers* (consistency
models) → *how quorums/consensus enforce them* (Paxos/Raft) → *the partition tradeoff*
(CAP/PACELC) → *atomic commit across shards* (2PC→Paxos Commit) → *a worked stack* (Spanner).
Each chapter pairs the intuition with the load-bearing theorem and its forcing function.
Theorem-driven, with small simulators as labs.

## Dependency position
- **Depends on:** 03 (the network — messages, partitions, latency), 09 (logs/ISR preview
  replication), 07 (isolation previews distributed commit), light 06 (consistent hashing).
- **Feeds into:** 14/15 (partitioning + replication in practice), 12 (the canon walkthroughs),
  20 (failure/tail), 26 (resume = recovery), 27 (multi-agent IS a distributed system).
- **Appendix links DOWN:** L-consensus-replication-and-transactions (the fault-model ladder
  in full: Byzantine, PBFT, FLP detail, isolation formalism), 12 (paper walkthroughs). 11
  teaches the foundations; L is the deep reference.

## Chapter specs (3–5 lines each)
1. **Order is information flow, not wall-clock** — Lamport happened-before (`→`): program
   order + send-before-receive + transitivity; no `→` path either way = concurrent. Logical
   clocks satisfy `a→b ⇒ C(a)<C(b)`; total order is a tiebreak convention, not physics.
   Physical clocks mean nothing without proven drift bounds. (Lamport 1978, VERIFIED.)
2. **Tracking causality: vector clocks** — scalar clocks lose the converse (`C(a)<C(b)` does
   NOT imply `a→b`); vector clocks recover it (`VC(a)<VC(b) ⇔ a→b`; incomparable ⇔
   concurrent). Version vectors detect conflicting replica versions (siblings) — the
   eventual-consistency machinery.
3. **What timing makes solvable: models & FLP** — the hinge. Synchronous (bounded delay →
   exact failure detection → consensus). Asynchronous: FLP — no deterministic protocol
   solves consensus if even one process may crash ("dead" vs "slow" indistinguishable).
   Partially synchronous (DLS) = realistic middle; failure detectors (◇S) name the
   assumption instead of hiding it. (FLP VERIFIED.)
4. **Consistency models as contracts over histories** — sequential (some global order
   respecting per-client program order, NOT real-time) vs linearizability (adds real-time:
   A-before-B ⇒ ordered) vs eventual (diverge now, converge if updates stop + links heal).
   Spanner external-consistency form VERIFIED; weaker contracts dodge CAP's "C."
5. **Quorums & consensus enforce one order** — majorities intersect ⇒ disjoint groups can't
   make conflicting decisions. Paxos chooses a value; Multi-Paxos/Raft turn choices into a
   replicated log (election + AppendEntries + safety: Log Matching, Leader Completeness;
   commit on majority). A leader is an ordering device — but creates a liveness dependence.
   (Paxos Made Simple + Raft VERIFIED.)
6. **The partition tradeoff: CAP & PACELC** — under a partition, choose linearizable C or A
   (P is not optional on a real network); "2 of 3" is the misconception. CAP's C is
   specifically linearizability. PACELC adds the healthy case: Else, Latency-or-Consistency —
   strong consistency costs round-trips even with no partition. Dynamo PA/EL, Spanner PC/EC.
7. **Atomic commit across shards** — 2PC: TM collects Prepared votes then broadcasts
   Commit/Abort (3N−1 msgs); SAFE but BLOCKS if coordinator dies post-prepare (RMs hold
   locks). 3PC attempts non-blocking but classic versions split-brain. Paxos Commit runs
   Paxos per participant decision (2F+1 coordinators, progress with F+1); **2PC is exactly
   the F=0 case** — which is why one failure blocks it. (Gray & Lamport VERIFIED.)
8. **The worked synthesis: Spanner** — distributed transactions are a STACK: per-shard Paxos
   replication + 2PC over Paxos groups (commit decision itself replicated) + 2PL for
   read-write + snapshot reads + commit-wait on TrueTime to upgrade serializable → externally
   consistent. Each layer independently necessary. (Spanner VERIFIED.)

## Paired build labs (/build — simulators, theorem-made-tangible)
Causality lab (Lamport vs vector clock; show the converse failure) → Chandy-Lamport snapshot
recorder (consistent vs inconsistent cuts) → model-taxonomy sandbox (toggle sync/async/
partial delays; watch toy consensus stall = FLP tangible) → mini-Raft + single-decree Paxos
(election, AppendEntries, majority commit; livelock without distinguished proposer) → quorum/
PACELC dial (N replicas, tunable R/W, ack-after-K; latency vs staleness; cut network for CAP
C-vs-A) → 2PC kill-switch → Paxos Commit upgrade (kill TM post-prepare to show blocking;
2F+1 to show progress) → isolation harness (2PL vs SI; reproduce write skew).

## Diagrams needed
- happened-before space-time diagram (concurrent vs causally-ordered events).
- Scalar-clock converse failure vs vector-clock comparability lattice.
- Model taxonomy table (sync/async/partial) → solvable? + FLP impossibility illustration.
- Consistency-model hierarchy (eventual ⊂ sequential ⊂ linearizable + real-time arrow).
- Quorum intersection (two majorities overlap); Raft log replication + commit-on-majority.
- CAP decision under partition; PACELC 2×2 (partition? → C/A; else → L/C).
- 2PC message flow + coordinator-failure blocking; Paxos Commit 2F+1 acceptors.
- Spanner stack layers (Paxos + 2PC + 2PL + commit-wait/TrueTime).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- VERIFIED primaries: Lamport Time/Clocks 1978, Sequential Consistency 1979, Chandy-Lamport
  1985, FLP 1985, Paxos Made Simple 2001, Raft 2014, Spanner 2012, Gray & Lamport 2006.
- `[UNVERIFIED from fetched source]` — fetch before prose: Gilbert/Lynch 2002 (CAP proof),
  Brewer 2000/2012, Abadi 2012 (PACELC), Herlihy/Wing 1990 (object-level linearizability),
  Dynamo 2007, Fidge/Mattern/Charron-Bost (vector clocks + O(N) bound), DLS 1988, Skeen 1981
  (3PC), Berenson 1995 (ANSI isolation), Chandra-Toueg 1996 (need cleaner text for ◇S).
  NOTE: Brewer/Kleppmann CAP + Dynamo + several were later UPGRADED→VERIFIED in Waves 7/9 and
  appendix L — reconcile receipts at draft time; erase nothing.
- Deliberate boundary (NOT a gap): Raft membership/snapshots/read optimizations + BFT live in
  appendix L, not 11.
