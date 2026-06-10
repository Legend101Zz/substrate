# Research Brief (RECONCILED) — Sub-course 11: Distributed Systems Foundations

## Reconciler: brain | Date: 2026-06-10 | Phase: 1 (research only — NO chapter prose)

This is the reconciled `_research.md` for sub-course 11, synthesizing four factchecked source clusters. It follows
ADR-001: each cluster keeps its own deep `_research_<cluster>.md` file; this file reconciles overlaps, states the
cross-cluster arc, and consolidates sources + gaps. For full depth and exact line receipts, read the cluster files.

### Cluster files and their factcheck reports
1. **Time / clocks / ordering / causality / global state / partial failure** —
   `_research_time-clocks-ordering-failure.md` · factcheck `_factcheck_phase1.md` (22 claims, 0 blockers).
2. **Vector clocks / version vectors / causal histories / model taxonomy** —
   `_research_vector-clocks-model-taxonomy.md` · factcheck `_factcheck_cluster2.md` (2 blockers patched).
3. **Consistency / replication / quorums / Paxos / Raft / Spanner bridge** —
   `_research_consistency-replication-quorums.md` · factcheck `_factcheck_cluster3.md` (13 claims, 0 blockers,
   2 line-drifts patched).
4. **CAP / partitions / PACELC and distributed commit (2PC / 3PC / Paxos Commit)** —
   `_research_cap-partitions-distributed-commit.md` · factcheck `_factcheck_cluster4.md` (14 claims verified,
   0 blockers, 2 citation-precision warnings).

### Coverage honesty statement
This corpus covers the foundational arc end-to-end: *what order even means* (time/causality) → *how to track causality*
(vector clocks) → *what timing assumptions make problems solvable* (model taxonomy, FLP/DLS) → *what contracts
replication can offer* (consistency models) → *how quorums/consensus enforce them* (Paxos/Raft) → *the partition and
latency trade-offs* (CAP/PACELC) → *how to commit atomically across shards* (2PC/3PC/Paxos Commit) → *a worked
end-to-end system* (Spanner). It is deep enough to draft 11 without further searching **except** for the residual
`[UNVERIFIED]` primaries listed in §6, which must be fetched before Phase 2 prose. We did not fake completeness on the
blocked CAP/PACELC/Herlihy-Wing/Dynamo primaries; they are flagged, not laundered.

---

## 1. Key mechanisms (cross-cluster synthesis)

The whole sub-course is one argument: **a distributed system has no free shared "now," so every guarantee you want must
be manufactured by a protocol, and every protocol pays in latency, availability, or message count.**

### 1.1 Order is information flow, not wall-clock time (cluster 1)
Lamport's happened-before (`→`) is the smallest relation with: program order within a process, send-before-receive
across processes, and transitivity. Events with no `→` path either way are *concurrent*. Logical clocks satisfy the
Clock Condition (`a → b ⇒ C(a) < C(b)`) and can be extended to an arbitrary total order — but that extra order is a
tiebreak convention, not a physical fact. Physical clocks only carry meaning with proven drift/sync bounds. Teach order
as causality before teaching wall clocks. *(Lamport 1978, verified.)*

### 1.2 Scalar clocks lose the converse; vector clocks recover it (clusters 1→2)
A Lamport scalar clock gives `a → b ⇒ C(a) < C(b)` but **not** the converse: `C(a) < C(b)` does not imply `a → b`.
Vector clocks close the gap — `VC(a) < VC(b) ⇔ a → b`, and incomparable vectors `⇔` concurrency. Version vectors are
the data-object variant used to detect conflicting replica versions. This is the machinery eventual-consistency systems
use to detect siblings. *(Lamport 1978 scalar limitation verified; Fidge 1988 / Mattern 1989 / Charron-Bost 1991 /
Dynamo version vectors / CBCAST remain `[UNVERIFIED from fetched source]` — blocked PDFs.)*

### 1.3 Timing assumptions decide what is solvable (cluster 2)
The model taxonomy is the hinge of the whole field:
- **Synchronous:** bounded message/processing delay → exact failure detection → consensus achievable.
- **Asynchronous (FLP):** no timing bounds at all → "dead" and "slow" are indistinguishable → **no deterministic
  protocol solves consensus if even one process may crash.** *(FLP/JACM 1985, verified.)*
- **Partially synchronous (DLS):** bounds exist but are unknown, or hold only eventually → the realistic middle ground
  where consensus is solvable with the right protocol. *(DLS/JACM 1988 model taxonomy `[UNVERIFIED from fetched
  source]`.)*
- **Failure detectors (Chandra-Toueg):** name the timing assumption explicitly (completeness + accuracy properties)
  instead of pretending it vanished; `◇S` is the weakest detector sufficient for consensus. *(Chandra-Toueg JACM 1996;
  exact definitions need a cleaner text — warning carried forward.)*

### 1.4 Consistency models are contracts over histories (cluster 3)
- **Sequential consistency** (Lamport, IEEE TC 1979, verified): some single global order exists that respects each
  client's program order — but **not** necessarily real-time order across clients.
- **Linearizability / external consistency:** adds real-time order — if A completes before B begins, the global order
  must put A before B. Spanner states the transaction-level form: T1 commits before T2 starts ⇒ smaller commit
  timestamp (verified). The object-level Herlihy/Wing definition is `[UNVERIFIED from fetched source]`.
- **Eventual consistency:** replicas may diverge now but converge if updates stop and links heal. Dynamo is the
  intended primary (sloppy quorums, hinted handoff, version vectors, app reconciliation) but remains `[UNVERIFIED from
  fetched source]`.

### 1.5 Quorums and consensus enforce a single order (cluster 3)
Quorums work because **any two majorities intersect**, so conflicting decisions can't be made by disjoint groups
(Paxos Made Simple, verified). Paxos *chooses values*; Multi-Paxos/Raft *turn choices into a replicated log*. Raft
decomposes into leader election (majority votes), log replication (AppendEntries), and safety (Log Matching, Leader
Completeness); an entry commits once replicated on a majority (verified). A leader is an *ordering device*, not just a
perf optimization — but it creates a liveness dependence on electing/reaching a quorum.

### 1.6 The partition trade-off and its always-on latency tax (cluster 4)
- **CAP:** under a partition you must choose linearizable Consistency *or* Availability — partition tolerance is not
  optional for a real network. The "2 of 3" framing is the misconception (Brewer's own retrospective corrects it). CAP's
  "C" is specifically linearizability, which is why weaker contracts dodge the theorem. *(Gilbert/Lynch 2002, Brewer
  2000/2012 — `[UNVERIFIED from fetched source]`, network-blocked.)*
- **PACELC:** CAP is silent about the healthy case; PACELC adds *Else, Latency-or-Consistency* — strong consistency
  costs round-trips even with no partition (the quorum/leader wait). Classifications: Dynamo PA/EL, Spanner PC/EC,
  PNUTS PC/EL. *(Abadi 2012 — `[UNVERIFIED from fetched source]`.)*

### 1.7 Atomic commit: 2PC, its blocking failure, and the consensus fix (cluster 4, verified primary)
- **2PC:** a transaction manager (TM) collects `Prepared` votes from all resource managers (RMs), then broadcasts one
  Commit/Abort. Cost: `3N − 1` messages / four message delays (`3N − 3` / three with co-location); durability via
  stable-storage logging before each message. *(Gray & Lamport, verified.)*
- **The blocking failure:** "The classic Two-Phase Commit protocol blocks if the coordinator fails." If the TM dies
  right after all `Prepared` messages, RMs hold locks and cannot learn the decision. 2PC is **safe** (never a split
  commit) but **not live** under coordinator failure. *(Verified.)*
- **3PC:** non-blocking commit attempts ("often called Three-Phase Commit") add a pre-commit round and elect a
  replacement TM — but classic ones can split-brain into actual *inconsistency*, and Gray & Lamport "know of none that
  provides a complete algorithm proven to satisfy a clearly stated correctness condition." *(Verified critique.)*
- **Paxos Commit:** runs Paxos on each participant's commit/abort decision using `2F + 1` coordinators, making progress
  if `F + 1` work; it never lets two leaders choose conflicting values (safety unconditional, liveness needs a stable
  leader). **2PC is exactly the `F = 0` degenerate case (single acceptor)** — which is precisely why one failure blocks
  it. General lower bound: `2F + 1` participants to tolerate `F` failures without synchrony. *(Verified.)*

### 1.8 The worked synthesis: Spanner (clusters 3+4, verified primary)
Spanner = per-shard **Paxos** replication + **two-phase commit over Paxos groups** (so the commit decision is itself
replicated, mitigating the blocking problem) + **two-phase locking** for read-write transactions + **snapshot-isolation
performance** for lock-free read-only transactions + **commit wait on TrueTime** to upgrade serializable → externally
consistent. The lesson: "distributed transactions" are a *stack* — concurrency control + atomic commit + replication +
(for external consistency) a real-time ordering device — and each layer is independently necessary.

---

## 2. Foundational sources (consolidated)

**Verified / fetched (with cluster-local line receipts):**
- Lamport, "Time, Clocks, and the Ordering of Events," CACM 1978 — `lamport.azurewebsites.net/pubs/time-clocks.pdf`.
- Lamport, "How to Make a Multiprocessor Computer..." (sequential consistency), IEEE TC 1979 —
  `lamport.azurewebsites.net/pubs/multi.pdf`.
- Chandy & Lamport, "Distributed Snapshots," ACM TOCS 1985.
- Fischer, Lynch & Paterson (FLP), "Impossibility of Distributed Consensus with One Faulty Process," JACM 1985.
- Lamport, "Paxos Made Simple," 2001 — `lamport.azurewebsites.net/pubs/paxos-simple.pdf`.
- Ongaro & Ousterhout, "In Search of an Understandable Consensus Algorithm (Raft)," USENIX ATC 2014.
- Corbett et al., "Spanner," OSDI 2012.
- **Gray & Lamport, "Consensus on Transaction Commit," ACM TODS 2006** (NEW this cluster; tech-report PDF from
  `lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`) — 2PC, blocking, 3PC critique, Paxos Commit,
  `2F+1`/`F+1`/`F=0`.

**Blocked / `[UNVERIFIED from fetched source]` (must fetch before Phase 2):**
- Gilbert & Lynch, "Brewer's Conjecture...," SIGACT News 2002 (CAP proof).
- Brewer, "Towards Robust Distributed Systems," PODC 2000; "CAP Twelve Years Later," IEEE Computer 2012.
- Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design," IEEE Computer 2012 (PACELC).
- Herlihy & Wing, "Linearizability," ACM TOPLAS 1990 (object-level definition).
- DeCandia et al., "Dynamo," SOSP 2007 (eventual consistency, sloppy quorum, hinted handoff, N/R/W).
- Fidge 1988, Mattern 1989, Charron-Bost 1991 (vector clocks + O(N) lower bound); Birman/Schiper/Stephenson 1991
  (CBCAST); Dwork/Lynch/Stockmeyer (DLS) JACM 1988 (partial synchrony).
- Skeen, "Nonblocking Commit Protocols," SIGMOD 1981 (original 3PC); Bernstein/Hadzilacos/Goodman 1987 (2PC/3PC text).
- Berenson et al., "A Critique of ANSI SQL Isolation Levels," SIGMOD 1995 (isolation formalism).
- Chandra & Toueg, "Unreliable Failure Detectors for Reliable Distributed Systems," JACM 1996 (have noisy PostScript;
  need cleaner text for exact definitions).

Full per-cluster source lists with exact line numbers live in the four `_research_*.md` files and their factchecks.

---

## 3. Why it is this way — the forcing functions (consolidated)

1. **No shared "now."** Independent machines + message passing ⇒ order must be derived from information flow, not
   assumed from clocks. (Cluster 1.)
2. **Scalar clocks under-determine causality.** Detecting concurrency vs. causation requires per-process vectors.
   (Cluster 2.)
3. **Timing assumptions are the lever.** FLP forbids deterministic asynchronous consensus under one crash; real systems
   buy progress with partial synchrony / failure detectors / randomness while keeping safety unconditional. (Cluster 2.)
4. **Replicas execute different orders unless a protocol chooses one.** Consensus manufactures a shared order; majority
   intersection preserves memory across failures. (Cluster 3.)
5. **Partitions are unavoidable, so C-vs-A is a real-time choice, not a menu.** And consistency costs latency even when
   healthy (PACELC). (Cluster 4.)
6. **Atomic commit needs one agreed decision; a lone decision-holder blocks or split-brains.** The principled fix is
   consensus over a quorum (`2F+1`), of which 2PC is the fragile `F=0` special case. (Cluster 4.)
7. **External consistency needs explicit clock-uncertainty accounting.** Spanner waits out TrueTime uncertainty.
   (Clusters 3+4.)

---

## 4. Common misconceptions to preempt (consolidated)

- "Timestamps order distributed events." No — only causally-related events have a real order; clocks need bounds.
- "Lamport clocks detect concurrency." No — they lose the converse; use vector clocks.
- "Asynchronous consensus is just hard." No — it's *impossible* deterministically under one crash (FLP); real systems
  change the model.
- "Replication means consistency." No — replication means copies; consistency needs ordering/quorum/commit rules.
- "Sequential consistency = linearizability." No — linearizability adds real-time order.
- "Eventual consistency is just bad consistency." No — it's a weaker contract chosen for latency/availability; the bug
  is pretending it's linearizable.
- "Paxos/Raft always make progress." No — safety is unconditional; liveness needs a reachable quorum + stable leader.
- "CAP means pick two of three." No — partition tolerance is mandatory; the choice is C-vs-A *during a partition*.
- "Strong consistency is free when the network is healthy." No — that's PACELC's point: it still costs latency.
- "2PC is unsafe." No — 2PC is safe; it *blocks* under coordinator failure (a liveness flaw).
- "3PC fixes 2PC for free." No — classic 3PC can split-brain into real inconsistency; Paxos Commit is the version with
  a proven fault model.
- "Spanner is linearizable because of atomic clocks." Incomplete — it's TrueTime uncertainty + Paxos + 2PC + 2PL +
  commit wait together.

---

## 5. Best build-your-own targets (consolidated)

- **Causality lab:** Lamport-clock vs. vector-clock event simulator; show the converse failure concretely.
- **Snapshot recorder:** implement Chandy-Lamport; visualize consistent vs. inconsistent cuts.
- **Model-taxonomy sandbox:** toggle synchronous/asynchronous/partially-synchronous delays; watch a toy consensus
  succeed/stall (FLP made tangible).
- **Mini Raft + single-decree Paxos playground:** election, AppendEntries, majority commit; livelock without a
  distinguished proposer.
- **Quorum / PACELC dial:** N replicas with tunable R/W and "ack after K"; plot latency vs. staleness; cut the network
  for the CAP C-vs-A demo.
- **2PC kill-switch visualizer → Paxos Commit upgrade:** kill the TM post-prepare to show blocking; replace with
  `2F+1` acceptors to show progress with `F+1` and no split commits.
- **Isolation-level harness:** 2PL vs. snapshot isolation over the commit protocol; reproduce a write-skew anomaly.

All build-lab candidates only. Do NOT start `/build` during Phase 1.

---

## 6. Open questions / gaps (consolidated — DO NOT erase on later edits)

**Network-blocked primaries to fetch before Phase 2 prose:**
- **CAP/PACELC:** Gilbert/Lynch 2002 (exact model, availability definition, proof construction; partial-synchrony
  variant), Brewer 2000/2012 (partition-mode + recovery + latency-partition link), Abadi 2012 (PACELC definition +
  classifications). All `[UNVERIFIED from fetched source]` this session.
- **Linearizability object-level:** Herlihy/Wing TOPLAS 1990 (locality, nonblocking properties). Carried from
  clusters 2/3.
- **Eventual consistency primary:** Dynamo SOSP 2007 (sloppy quorum, hinted handoff, N/R/W, version vectors). Carried
  from clusters 2/3.
- **Vector-clock primaries:** Fidge 1988, Mattern 1989, Charron-Bost 1991 (O(N) lower bound), CBCAST 1991. Carried
  from cluster 2.
- **Partial synchrony:** DLS/JACM 1988 model taxonomy. Carried from cluster 2.
- **3PC + isolation formalism:** Skeen 1981 (original 3PC pre-commit state machine), Berenson et al. 1995 (ANSI
  isolation levels: dirty read, write skew, phantom). New from cluster 4.

**Citation-precision / cleanup items:**
- Chandra-Toueg exact `◇S`/completeness/accuracy definitions need a cleaner text/PDF (noisy PostScript only).
- The `f+1` synchronous rotating-coordinator crash-fault claim (cluster 2) still needs a source pin.
- Gray & Lamport claims cite the 37-page tech-report PDF; re-pin to ACM TODS 2006 (vol. 31, no. 1) pagination if exact
  citations are required.

**Scope note:** consensus depth here is core leader/log/quorum + commit. Raft membership changes, snapshots, and
linearizable-read optimizations, and Byzantine fault tolerance, are intentionally out of scope for Phase 1 foundations
(candidate for appendix L). Not a gap — a deliberate boundary.
