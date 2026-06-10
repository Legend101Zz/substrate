# Research Brief — Sub-course 11: Distributed Systems Foundations
## Source cluster: consistency, replication, quorums, and the Paxos/Raft bridge
## Researcher: brain manual primary-source pass | Date: 2026-06-10

Status: **cluster 3 brief**. This is not a reconciled full-11 brief. It extends the existing time/clocks/failure and
vector-clocks/model-taxonomy clusters. Sources were fetched/extracted into `/tmp/substrate-11-sources` with throwaway
`uv run --with pypdf`; `/Users/m0t0hu6/.code-puppy-venv` was not modified.

Source availability note: Raft, Paxos Made Simple, Spanner, and Lamport's sequential-consistency paper were fetched
and text-extracted. Herlihy/Wing linearizability, Dynamo, and MIT 6.5840 linearizability notes were blocked by network
resets in this harness; exact primary-paper claims from those sources are marked `[UNVERIFIED from fetched source]`.

---

## 1. Key mechanisms

### 1.1 Consistency models are contracts over histories, not implementation recipes

Intuitive model: a consistency model says what stories a client is allowed to believe after observing reads and writes.
Replication is how the system tries to make those stories true despite multiple machines.

Deep mechanism: Lamport's sequential consistency definition for shared memory says the result of any execution must be
as if operations of all processors were executed in some sequential order, while operations of each individual processor
appear in that sequence in program order. This definition does **not** require the global sequence to respect real-time
order between operations on different processors; it requires one legal interleaving that preserves each processor's
program order.

Source: Lamport, "How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs," IEEE TC 1979,
`https://lamport.azurewebsites.net/pubs/multi.pdf`, extracted lines around the abstract and first page.

Course consequence: teach consistency vocabulary before protocol vocabulary. A protocol is a machine for enforcing a
contract. If the contract is fuzzy, the protocol discussion becomes folklore soup. Nobody wants soup with race bugs.

### 1.2 Linearizability / external consistency adds real-time order

Intuitive model: sequential consistency says "there exists a single order that explains what everyone saw." Linearizability
adds: if operation A finishes before operation B begins, the single order must put A before B. Real-time non-overlap now
matters.

Deep mechanism: the general Herlihy/Wing object-level definition could not be fetched in this environment, so keep the
exact object-level theorem language `[UNVERIFIED from fetched source]`. Spanner gives a verified transaction-level
statement of the same real-time-order constraint: it says its serialization order satisfies external consistency, or
equivalently linearizability, such that if transaction `T1` commits before transaction `T2` starts, then `T1`'s commit
timestamp is smaller than `T2`'s.

Sources:
- Herlihy and Wing, "Linearizability: A Correctness Condition for Concurrent Objects," ACM TOPLAS 1990,
  DOI `10.1145/78969.78972` — `[UNVERIFIED from fetched source]`, Brown/CMU/ACM URLs reset in this harness.
- Corbett et al., "Spanner: Google's Globally-Distributed Database," OSDI 2012,
  `https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf`, extracted lines
  around 95–103.

Why it matters: sequential consistency can allow a stale read after a completed write if some global order can explain
it while preserving each client's program order. Linearizability forbids that for non-overlapping operations because the
completed write must appear before the later read.

### 1.3 Eventual consistency gives up immediate single-copy illusion for availability/latency

Intuitive model: eventual consistency says replicas may disagree now, but if updates stop and communication eventually
works, they should converge. It is the "we'll clean it up later" model. Useful? yes. A free lunch? absolutely not.

Deep mechanism: the Dynamo paper is the intended primary source for this cluster because it combines always-writable
replication, sloppy quorums, hinted handoff, vector clocks/version vectors, and application conflict resolution. Dynamo
was blocked through all attempted canonical/mirror URLs, so the details below remain `[UNVERIFIED from fetched source]`:
- writes can be accepted by multiple replicas during failures/partitions;
- reads may see divergent versions;
- version vectors detect sibling versions;
- application-specific reconciliation resolves conflicts;
- quorum parameters `N`, `R`, and `W` tune latency/availability vs. consistency.

Verified supporting anchor: Spanner explicitly contrasts itself with systems that use asynchronous/eventually consistent
cross-datacenter replication, stating Bigtable only supports eventually-consistent replication across datacenters, while
Spanner supports externally consistent distributed transactions.

Sources:
- DeCandia et al., "Dynamo: Amazon's Highly Available Key-Value Store," SOSP 2007,
  canonical URL `https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf` — blocked; mark exact claims
  `[UNVERIFIED from fetched source]` until fetched.
- Spanner OSDI 2012, extracted lines around 313–319 for the Bigtable/eventual-consistency contrast.

### 1.4 Leader/follower replication makes one replica the sequencer

Intuitive model: if every replica accepts writes independently, they can disagree on order. A leader fixes this by making
one replica the front desk: writes go to the leader, the leader appends them to a log, followers copy the log, and all
replicas apply entries in the same order.

Deep mechanism in Raft: Raft decomposes consensus into leader election, log replication, and safety. A server receiving
votes from a majority becomes leader for a term. Leaders initiate AppendEntries RPCs to replicate log entries. An entry
is committed once the leader that created it has replicated it on a majority of servers; then that entry and prior
entries are safe to apply to the replicated state machine. The Log Matching Property says if two logs contain an entry
with the same index and term, they store the same command and all preceding entries are identical. The Leader
Completeness Property says if a log entry is committed in a term, it will be present in leaders of all higher-numbered
terms.

Sources:
- Ongaro and Ousterhout, "In Search of an Understandable Consensus Algorithm (Raft)," USENIX ATC 2014,
  `https://www.usenix.org/system/files/conference/atc14/atc14-paper-ongaro.pdf`, extracted lines around 331–454,
  503–557, 602–652, 659–680, and 763–793.

Forcing constraint: the leader is not just a performance optimization. It is an ordering device. The system needs a
single sequence of commands for the replicated state machine; the leader proposes that sequence, and the majority/quorum
rules make sure future leaders cannot safely forget committed entries.

### 1.5 Quorums work because majorities intersect

Intuitive model: a quorum is a receipt threshold. If every decision must be signed by a majority, then two conflicting
decisions cannot be made by disjoint groups; at least one participant would have to be in both groups and carry memory
of the earlier decision.

Deep mechanism in Paxos: Paxos Made Simple explicitly motivates replacing a single acceptor with multiple acceptors. A
value is chosen when a majority of acceptors accept it. Lamport states the reason: any two majorities have at least one
acceptor in common. Paxos safety then forces higher-numbered proposals to carry forward the value of any previously
chosen proposal, via the prepare/promise phase that asks a majority for the highest-numbered accepted proposal they know.

Sources:
- Lamport, "Paxos Made Simple," 2001, `https://lamport.azurewebsites.net/pubs/paxos-simple.pdf`, extracted lines
  around 79–82 (majority intersection), 104–107 (chosen by majority), and 136–172 (P2c/prepare-promise).

Mechanism consequence: quorum intersection is the bridge from replication to agreement. Replication copies data;
quorum intersection makes it impossible for the system to make independent, mutually ignorant decisions if the protocol
preserves the right acceptor state.

### 1.6 Paxos chooses values; Multi-Paxos/Raft turn choices into a log

Intuitive model: single-decree Paxos chooses one value. A database needs a long sequence: command 1, command 2, command
3, and so on. Multi-Paxos and Raft run the agreement idea repeatedly over log slots, usually with a stable leader to
avoid paying the full election/prepare cost every time.

Deep mechanism:
- Paxos Made Simple describes proposers, acceptors, and learners; safety requires only proposed values can be chosen,
  only one value is chosen, and learners never learn a value was chosen unless it was actually chosen.
- Paxos progress is not unconditional: Lamport says progress requires selecting a distinguished proposer, and ensuring
  progress requires either randomness or real time such as timeouts.
- Raft packages the replicated-log case directly: leaders append client commands to their logs, replicate them to
  followers, and apply committed entries to replicated state machines in log order.

Sources:
- Paxos Made Simple, extracted lines around 43–53 for safety properties, 282–293 for distinguished proposer/progress.
- Raft ATC 2014, extracted lines around 315–331 for the replicated-state-machine/log framing and 602–652 for commit.

Course consequence: do not teach Paxos/Raft as "replication" alone. They are replicated-state-machine protocols: their
job is to make independent machines execute the same commands in the same order, despite failures.

### 1.7 Spanner shows the bridge from quorum replication to externally consistent transactions

Intuitive model: consensus gives each shard a reliable ordered log. Transactions across shards still need a single
commit decision and a timestamp that respects real time. Spanner combines Paxos groups, two-phase commit across group
leaders, and TrueTime commit wait.

Deep mechanism: each Spanner spanserver implements a Paxos state machine on top of each tablet. Writes must initiate
Paxos at the leader; reads can access any replica that is sufficiently up-to-date. For multi-group read-write
transactions, participant leaders prepare via Paxos, the coordinator leader chooses the transaction timestamp after
hearing participant prepare timestamps, logs the commit record through Paxos, then waits until `TT.after(s)` before
allowing coordinator replicas to apply the commit. Spanner says this commit-wait rule helps ensure external consistency.

Sources:
- Spanner OSDI 2012, extracted lines around 186–210 for Paxos groups/leaders/reads, 700–735 for two-phase commit and
  commit timestamps, and 603 / 731 for the commit-wait rule (`TT.after(si)` / `TT.after(s)`).

Course consequence: "linearizable distributed transactions" are not magic timestamps. Spanner buys them with explicit
clock uncertainty, Paxos replication, leader leases, two-phase commit, and waiting out uncertainty.

---

## 2. Foundational sources

Verified/fetched sources:

- Lamport, "How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs," IEEE TC 1979.
  `https://lamport.azurewebsites.net/pubs/multi.pdf`
  - Anchor: sequential consistency definition.
- Lamport, "Paxos Made Simple," 2001.
  `https://lamport.azurewebsites.net/pubs/paxos-simple.pdf`
  - Anchors: asynchronous non-Byzantine model; majority intersection; chosen values; prepare/promise; progress needs a
    distinguished proposer and timing/randomness.
- Ongaro and Ousterhout, "In Search of an Understandable Consensus Algorithm (Raft)," USENIX ATC 2014.
  `https://www.usenix.org/system/files/conference/atc14/atc14-paper-ongaro.pdf`
  - Anchors: leader election by majority, log replication, commit by majority replication, Log Matching, Leader
    Completeness.
- Corbett et al., "Spanner: Google's Globally-Distributed Database," OSDI 2012.
  `https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf`
  - Anchors: external consistency/linearizability condition, Paxos groups and leaders, sufficiently up-to-date replica
    reads, leader leases, 2PC over Paxos groups, commit wait with TrueTime.

Blocked/unverified primary sources:

- Herlihy and Wing, "Linearizability: A Correctness Condition for Concurrent Objects," ACM TOPLAS 1990,
  DOI `10.1145/78969.78972`. Brown/CMU/ACM URLs reset in this environment. Use Spanner for verified transaction-level
  external-consistency wording until fetched.
- DeCandia et al., "Dynamo: Amazon's Highly Available Key-Value Store," SOSP 2007. allthingsdistributed, ACM, Cornell,
  Princeton, UW, and Amazon Science URLs were blocked/reset. Keep exact Dynamo claims `[UNVERIFIED from fetched source]`.
- MIT 6.5840 linearizability notes. `pdos.csail.mit.edu` reset in this harness. Supporting context only; not primary.

---

## 3. Why it is this way — constraints that forced the design

1. **Replicas can execute different orders unless a protocol chooses one.** If two leaders accept writes independently,
   clients can observe histories no single-copy system could produce. Consensus protocols manufacture a shared order.
2. **Real-time order is externally visible.** If client B starts after client A's write completed, B can carry knowledge
   of A's write outside the storage system. Linearizability/external consistency preserve that external information flow.
3. **Majority quorums preserve memory across failures.** Since any two majorities intersect, a later leader/proposer that
   consults a majority can learn enough about prior accepted/committed work to avoid contradicting it.
4. **Leaders reduce coordination cost but create liveness dependence.** Stable leaders avoid constant prepare/election
   work, but progress depends on electing/reaching a leader and a quorum.
5. **Eventual consistency chooses availability/latency over immediate global order.** Accepting writes during partitions
   means conflicts can exist and must be detected/merged later; version vectors and application reconciliation are the
   standard Dynamo-style answer `[UNVERIFIED from fetched Dynamo source]`.
6. **Clock-backed external consistency needs uncertainty accounting.** Spanner can use commit timestamps for real-time
   ordering because TrueTime exposes uncertainty and Spanner waits until the chosen timestamp is definitely in the past.

---

## 4. Common misconceptions to preempt

- **"Replication means consistency."** No. Replication means copies exist. Consistency requires rules for ordering writes,
  choosing visible versions, detecting conflicts, and handling failures.
- **"Majority quorum means the latest value is always on the node I read."** No. A single replica can be stale. Quorum
  protocols rely on intersection plus protocol metadata; plain majority replication without the right metadata can still
  serve stale or conflicting data.
- **"A leader makes consensus easy."** A leader simplifies the common path, but safety still depends on election and log
  rules that prevent an incomplete leader from overwriting committed history.
- **"Sequential consistency and linearizability are synonyms."** No. Sequential consistency preserves per-client/program
  order in some global order. Linearizability also respects real-time order between non-overlapping operations.
- **"Eventual consistency is bad consistency."** Not automatically. It is a weaker contract chosen for specific latency
  and availability goals. The bug is pretending it gives linearizable behavior.
- **"Paxos and Raft guarantee progress no matter what."** No. They preserve safety under broad failure/timing conditions,
  but liveness needs a reachable quorum and leader/proposer stability; Paxos Made Simple explicitly points to randomness
  or real time/timeouts for progress.
- **"Spanner is linearizable because it uses atomic clocks."** Incomplete. It is because TrueTime exposes uncertainty,
  Paxos orders writes, 2PC coordinates cross-group commits, and commit wait ensures the timestamp is in the past before
  commit becomes visible.

---

## 5. Best build-your-own targets

- **Consistency history checker:** feed operation histories into checkers for sequential consistency vs. a simplified
  linearizability/external-consistency rule. Show histories accepted by one and rejected by the other.
- **Majority quorum simulator:** N replicas, W/R thresholds, failures, and stale reads. Demonstrate why intersection is
  necessary but not sufficient without metadata/commit rules.
- **Mini Raft log visualizer:** leader election, AppendEntries, majority commit, follower repair, and committed-entry
  survival across leader changes.
- **Single-decree Paxos playground:** prepare/promise/accept/learn with majority intersection, then show how two
  proposers can livelock without a distinguished proposer or timing assumption.
- **Spanner timestamp sketch:** model TrueTime intervals and commit wait; show why returning before `TT.after(s)` could
  violate external consistency.

These are build-lab candidates only. Do not start `/build` during Phase 1.

---

## 6. Open questions / gaps

- **Herlihy/Wing not fetched:** must fetch before Phase 2 prose for exact object-level linearizability definition,
  locality, and nonblocking properties. Current brief uses Spanner's verified transaction-level equivalence/external
  consistency wording and marks Herlihy/Wing claims unverified.
- **Dynamo not fetched:** cannot harden eventual-consistency, sloppy-quorum, hinted-handoff, `N/R/W`, or version-vector
  details until Dynamo SOSP 2007 is fetched. Existing vector-clock cluster already carries Dynamo gaps; preserve them.
- **MIT 6.5840 notes not fetched:** supporting context only; do not cite as primary.
- **Raft extended dissertation/book details not fetched:** USENIX ATC paper is sufficient for core leader/log/quorum
  mechanisms, but membership changes, snapshots, and linearizable read optimizations are not covered in this cluster.
- **CAP/partitions and distributed commit remain separate clusters:** this brief references partitions and Spanner 2PC,
  but does not fully cover CAP theorem, PACELC, 2PC/3PC/blocking, or transaction isolation. 11 should not be reconciled
  until at least CAP/partitions or distributed commit is covered, unless the project explicitly accepts those as Phase 2
  carry-forward gaps.
