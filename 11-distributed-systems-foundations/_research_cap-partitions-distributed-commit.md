# Research Brief — Sub-course 11: Distributed Systems Foundations
## Source cluster: CAP / partitions / PACELC and distributed commit (2PC / 3PC / Paxos Commit)
## Researcher: brain manual primary-source pass | Date: 2026-06-10

Status: **cluster 4 brief**. This is not a reconciled full-11 brief. It extends the time/clocks/failure,
vector-clocks/model-taxonomy, and consistency/replication/quorums clusters. The new primary source fetched and
text-extracted this session is Gray & Lamport, "Consensus on Transaction Commit" (the 37-page tech-report version),
pulled from `https://lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf` and extracted with a
throwaway `uv run --with pypdf` (Walmart index) into `/tmp/substrate-11-cap`; `/Users/m0t0hu6/.code-puppy-venv` was
not modified.

Source availability note for this cluster: in this harness only `lamport.azurewebsites.net` (and `example.com`)
resolved. Academic hosts (MIT/CMU/Cornell/UMD/UCSB/UW/Brown), ACM (`dl.acm.org` returned Cloudflare/403), arXiv, and
`raw.githubusercontent.com` all timed out (`HTTP 000`). Therefore:
- **Distributed commit (2PC/3PC/Paxos Commit) is anchored to fetched primary text** (Gray & Lamport) plus the cached
  Spanner OSDI 2012 text for the replication×transaction intersection.
- **CAP, PACELC, and Gilbert/Lynch's formal proof could not be fetched.** Their exact theorem/proof wording is marked
  `[UNVERIFIED from fetched source]` and must be confirmed against primaries before any Phase 2 prose. The mechanisms
  below state the standard results but flag every claim whose exact wording needs a primary.

---

## 1. Key mechanisms

### 1.1 CAP: under a network partition you must choose between consistency and availability

Intuitive model: imagine a service replicated across two sides of a network that has just been cut in half. A client
talks to one side. Two honest options exist: (a) refuse to answer until the partition heals, so you never serve stale
or divergent data (choose consistency, sacrifice availability), or (b) answer from the reachable side even though it
cannot see the other side's writes (choose availability, sacrifice consistency). You cannot have both *for that
request* while the partition lasts — there is no third option that is simultaneously linearizable and available to
both sides.

Deep mechanism (standard statement): CAP says a distributed shared-data system cannot simultaneously provide all three
of Consistency (here meaning linearizability/atomic single-copy semantics), Availability (every request to a
non-failed node returns a non-error response), and Partition tolerance (the system keeps operating despite arbitrary
message loss between nodes). Gilbert & Lynch formalized Brewer's conjecture and proved that in an asynchronous network
model where messages can be lost, no algorithm can guarantee both atomic/linearizable consistency and availability when
partitions are possible. The proof intuition is a partition/indistinguishability argument: partition the nodes into
two groups that cannot communicate; a write commits on one side; an available read on the other side must return a
response without having seen that write, so the response is either non-linearizable (violates C) or the node had to
refuse (violates A).

Sources:
- Gilbert and Lynch, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web
  Services," ACM SIGACT News 2002, DOI `10.1145/564585.564601`. **`[UNVERIFIED from fetched source]`** — MIT/NUS/CMU
  mirrors and the ACM DOI all blocked in this harness; confirm the exact model (asynchronous vs. partially-synchronous
  variants), the precise availability definition, and the proof construction before Phase 2.
- Brewer, "Towards Robust Distributed Systems," PODC 2000 keynote (the original CAP conjecture). **`[UNVERIFIED from
  fetched source]`**.

Course consequence: CAP is *not* "pick two of three at all times." Partition tolerance is not optional for a real
networked system — partitions happen whether you plan for them or not. So the real, ongoing choice CAP forces is
**C vs. A *during a partition*.** Teach it as a conditional, not as a static "two-out-of-three" menu, because the
two-out-of-three framing is exactly the misconception Brewer himself later walked back (see 1.3).

### 1.2 The CAP "C" is linearizability — weaker models dodge the theorem

Intuitive model: CAP only bites if you demand the strongest single-copy illusion. If your contract is weaker (eventual
consistency, causal consistency, read-your-writes), you can stay available under a partition without violating *that
weaker contract*, because the contract never promised both sides agree immediately.

Deep mechanism: CAP's "C" is the same real-time single-copy property as linearizability / external consistency from
cluster 3 (Spanner's "if T1 commits before T2 starts, T1's timestamp is smaller"). A system that only promises eventual
convergence (cluster 3, §1.3; Dynamo-style) can accept writes on both sides of a partition and reconcile later — it
sacrifices linearizable C by design, which is precisely why it can remain available (AP). This is why the consistency
*vocabulary* (cluster 3) must precede the CAP discussion: "CA," "CP," "AP" are meaningless until you pin down which
consistency contract "C" names.

Sources: Spanner OSDI 2012 external-consistency wording (cached `spanner.txt`, lines ~95–103, ~313–319) for the
linearizable-C anchor; Herlihy/Wing object-level linearizability remains **`[UNVERIFIED from fetched source]`** (still
network-blocked, carried forward from clusters 2 and 3).

### 1.3 Brewer's retrospective: partitions are rare, so the choice is dynamic and per-operation

Intuitive model: most of the time the network works. When it works, you do not have to choose — you can be both
consistent and available. CAP's trade-off only activates *during* a partition. So a good system detects partition
mode, degrades deliberately (e.g., limits which operations are allowed, queues writes, serves bounded-stale reads),
and then *recovers* by reconciling once the partition heals.

Deep mechanism (standard statement): Brewer's "CAP Twelve Years Later" argues that (1) the "2 of 3" formulation is
misleading because C, A, and P are not symmetric — you only forfeit one of C/A and only while partitioned; (2) the
real design space is a partition-recovery strategy: detect partitions, enter an explicit partition mode that may limit
some operations, and run a recovery/merge protocol (compensations, commutative merges, version reconciliation) when
connectivity returns; and (3) latency and partitions are deeply related — a partition is, operationally, a timeout.

Source: Brewer, "CAP Twelve Years Later: How the 'Rules' Have Changed," IEEE Computer 2012. **`[UNVERIFIED from
fetched source]`** — all attempted mirrors (UCSB/UMich/UW course copies, ResearchGate, papers-we-love GitHub) returned
`HTTP 000`/blocked. Confirm exact phrasing of "partition mode," the recovery examples, and the latency-partition
linkage before Phase 2.

### 1.4 PACELC: even with no partition, you still trade latency vs. consistency

Intuitive model: CAP only describes the partition case. But replicas have to talk to each other to stay consistent,
and talking takes time. So even when the network is perfectly healthy, a system still chooses: wait for replicas to
agree (more latency, more consistency) or answer immediately from one replica (less latency, weaker consistency).
PACELC names both halves: *if Partition, then C-or-A; Else, L-or-C.*

Deep mechanism (standard statement): Abadi's PACELC extends CAP by pointing out CAP is silent about the common
no-partition case. The forcing function is the same quorum/replication cost from cluster 3: a linearizable write must
reach enough replicas (a quorum or the leader + followers) before acknowledging, which adds round-trip latency; a
low-latency design acknowledges early and propagates asynchronously, weakening consistency. Classic classifications:
Dynamo-style systems are **PA/EL** (give up C in both partition and normal operation for availability/latency);
fully-consistent systems like Spanner/VoltDB are **PC/EC** (pay latency/availability to keep consistency); some systems
(e.g., PNUTS) are **PC/EL**.

Source: Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design," IEEE Computer 2012. **`[UNVERIFIED
from fetched source]`** — `cs.umd.edu` and course mirrors blocked. Confirm Abadi's exact PACELC definition and his
example classifications before Phase 2.

Course consequence: PACELC fixes CAP's biggest teaching gap — CAP makes consistency look "free when healthy," which
hides the everyday latency tax of strong consistency. The Spanner numbers (cluster 3 commit-wait + 2PC over Paxos) are
the concrete proof that strong consistency costs latency even with no partition.

### 1.5 Two-Phase Commit (2PC): one coordinator drives an all-or-nothing decision

Intuitive model: a transaction touches several resource managers (RMs) on different nodes. They must *all* commit or
*all* abort — no partial commits. 2PC uses a transaction manager (TM) as the front desk: phase 1 asks "can you
commit?" and collects votes; phase 2 broadcasts the single decision.

Deep mechanism (verified primary text): Each RM has a `prepared` state; the protocol's correctness conditions require
that an RM can only enter `committed` if all RMs first reached `prepared`. In Gray & Lamport's description:
- An RM spontaneously enters `prepared` and sends a `Prepared` message to the TM (the TM's `Prepare` message is "an
  optional suggestion that now would be a good time to do so").
- When the TM has received `Prepared` from **all** RMs, it enters `committed` and sends `Commit` to everyone; RMs
  commit on receipt.
- The TM (or a working RM) can spontaneously `abort` (in practice triggered by a timeout) before the TM commits.
- **Durability via stable storage:** "Each process records its current state in stable storage before sending any
  message while in that state," so failure+restart is equivalent to the process pausing — safe in an asynchronous model.
- **Cost (normal commit case):** with `N` RMs, 2PC sends `3N − 1` messages and the RMs learn the outcome after four
  message delays; co-locating the TM with the initiating RM reduces this to `3N − 3` messages and three message delays.
  Stable-storage write delays: three (the first RM's prepare write, the other RMs' prepare writes, the TM's decision
  write), reducible to two if all RMs prepare concurrently.

Source: Gray & Lamport, "Consensus on Transaction Commit," ACM TODS 2006 (tech-report version),
`https://lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`, extracted `/tmp/substrate-11-cap/
txncommit.clean.txt` lines ~136–204 (specification + prepared state), ~206–253 (2PC protocol), ~265–305 (cost).

### 1.6 The blocking failure mode of 2PC: TM dies after everyone is prepared

Intuitive model: 2PC's fatal flaw is that the decision lives in one place — the TM. If the TM crashes at exactly the
wrong moment (after every RM has voted `Prepared` but before the `Commit`/`Abort` reaches them), the RMs are stuck:
they have promised to be able to commit, they are holding locks, and they have no way to learn what the TM decided.
They must wait — block — until the TM is repaired.

Deep mechanism (verified primary text, quoting the structure): "the failure of the TM can cause the protocol to block
until the TM is repaired. In particular, if the TM fails right after every RM has sent a `Prepared` message, then the
other RMs have no way of knowing whether the TM committed or aborted the transaction." A *non-blocking* commit protocol
is then defined as "one in which the failure of a single process does not prevent the other processes from deciding."

Source: Gray & Lamport, §3.3 "The Problem with Two-Phase Commit," `txncommit.clean.txt` lines ~305–320.

Course consequence: 2PC is *safe* (it never produces a split commit) but not *live* under coordinator failure. This is
the cleanest concrete instance of the safety-vs-liveness split from earlier clusters: 2PC keeps atomicity (safety) by
sacrificing progress (liveness) when the single decision-holder is unreachable. FLP (cluster 1) is the deeper reason a
*perfectly* non-blocking, deterministic, asynchronous commit is impossible.

### 1.7 Three-Phase Commit (3PC) and Paxos Commit: making the decision survive a single failure

Intuitive model: 2PC blocks because one node (the TM) is the single source of truth for the decision. Two families fix
this: 3PC inserts an extra "pre-commit" round so survivors can finish the decision if the coordinator dies; Paxos
Commit replaces the single TM's stable storage with a *replicated* decision via consensus.

Deep mechanism (verified primary text):
- **3PC framing:** Gray & Lamport describe non-blocking commit protocols as "often called Three-Phase Commit
  protocols," noting several were proposed/implemented but warning that the classic ones "have usually attempted to fix
  the Two-Phase Commit protocol by choosing another TM if the first TM fails," and that the authors "know of none that
  provides a complete algorithm proven to satisfy a clearly stated correctness condition" — the specific hazard is two
  processes both believing they are the current TM (a split-brain coordinator), which can drive classic 3PC into
  *inconsistency* (a real split commit), not just blocking.
- **Paxos Commit:** runs a separate instance of the Paxos consensus algorithm to choose each RM's `Prepared`/`Aborted`
  outcome, using a set of `2F + 1` acceptors; it "makes progress if at least `F + 1` of them are working properly."
  Crucially, "Paxos maintains consistency, never allowing two different values to be chosen, even if multiple processes
  think they are the leader" — so multiple competing coordinators cost liveness but never safety, unlike classic 3PC.
- **The unifying result:** "The classic Two-Phase Commit algorithm is obtained as the special `F = 0` case of the Paxos
  Commit algorithm" — i.e., 2PC is the degenerate Paxos Commit with a single acceptor, where the TM *is* that one
  acceptor (hence one failure blocks it). The general fault model is grounded in the consensus lower bound: "without
  strict synchrony assumptions, `2F + 1` acceptors are needed to achieve consensus despite the failure of any `F` of
  them."

Sources: Gray & Lamport, abstract (`txncommit.clean.txt` lines ~21–31), §3.3 (3PC critique, lines ~310–320), §4.1
(Paxos, `2F + 1` acceptors, lines ~325–345), §5 "Paxos versus Two-Phase Commit" (lines ~623–680: 2PC blocks if TM
fails; 2PC is the degenerate `F = 0` case with a single acceptor; isomorphism table).

Course consequence: the line from 2PC → 3PC → Paxos Commit is the same arc as cluster 3's quorum story. The fix for "a
single decision-holder can block or split" is always the same: replicate the decision across a quorum so any majority
of survivors can finish it, and never let two leaders choose conflicting values.

### 1.8 Where commit meets replication and isolation: Spanner is the worked example

Intuitive model: real systems do not pick "replication" or "transactions" — they layer 2PC *on top of* per-shard
consensus, and bolt isolation levels onto that. Spanner is the canonical demonstration.

Deep mechanism (verified primary text): Spanner runs **two-phase commit over Paxos groups** — each participant shard
is itself a Paxos-replicated state machine, so the 2PC participants are fault-tolerant and the blocking problem of a
single-node TM is mitigated (the coordinator's decision is Paxos-logged). Concretely:
- "Running two-phase commit over Paxos" mitigates the availability problems of plain 2PC (cached `spanner.txt`
  line ~334).
- **Read-write transactions use two-phase locking** ("Transactional reads and writes use two-phase locking,"
  line ~556) and are assigned the timestamp Paxos gives the commit write.
- **Read-only transactions get snapshot-isolation performance** ("A read-only transaction ... has the performance
  benefits of snapshot isolation," line ~512) and are lock-free, executing at a chosen timestamp on any
  sufficiently-up-to-date replica.
- **Commit wait** (cluster 3) is what upgrades this from "serializable" to "externally consistent": the coordinator
  leader waits until `TT.after(s)` before committing so the commit timestamp is guaranteed to be in the past.

Source: Spanner OSDI 2012, cached `spanner.txt` lines ~328–334 (2PC over Paxos), ~474/505–526 (read-only/snapshot
isolation), ~556 (two-phase locking), ~601–609 (commit wait).

Course consequence: the intersection to teach is "isolation level × replication × commit." Serializable distributed
transactions = a concurrency-control mechanism (2PL or SI/MVCC) + an atomic-commit protocol (2PC/Paxos Commit) + a
replication protocol (Paxos/Raft) + (for *external* consistency) a real-time ordering device (commit wait / TrueTime).
Each layer is independently necessary; conflating them is how "we have transactions" turns into a stale-read incident.

---

## 2. Foundational sources

Verified/fetched this session:

- Gray and Lamport, "Consensus on Transaction Commit," ACM TODS 2006 (tech-report PDF, 37 pp.).
  `https://lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`
  - Anchors: transaction-commit spec + `prepared` state; 2PC protocol, cost (`3N−1` / four message delays, `3N−3` /
    three with co-location), stable-storage durability; the blocking problem (TM fails after all `Prepared`);
    definition of non-blocking commit; 3PC critique (split-brain TM → inconsistency); Paxos Commit with `2F + 1`
    acceptors, progress with `F + 1`; consensus lower bound `2F + 1` to tolerate `F`; 2PC = degenerate `F = 0` Paxos
    Commit with a single acceptor.

Cached from prior sessions (verified):

- Corbett et al., "Spanner," OSDI 2012. `spanner.txt` — 2PC over Paxos, two-phase locking, read-only/snapshot
  isolation, commit wait, external consistency.
- Lamport, "Paxos Made Simple," 2001. `paxos-simple.txt` — majority intersection / consensus safety (cluster 3 anchor;
  reused for the Paxos-Commit consensus backbone).

Blocked/unverified primary sources (network reset this session — keep `[UNVERIFIED from fetched source]`):

- Gilbert and Lynch, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web
  Services," ACM SIGACT News 2002, DOI `10.1145/564585.564601`. CAP formal proof + exact model and availability
  definition.
- Brewer, "Towards Robust Distributed Systems," PODC 2000 (original conjecture); and Brewer, "CAP Twelve Years Later,"
  IEEE Computer 2012 (partition-mode/recovery, latency-partition link, the "2-of-3 is misleading" correction).
- Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design," IEEE Computer 2012 (PACELC definition,
  PA/EL · PC/EC · PC/EL classifications).
- Skeen, "Nonblocking Commit Protocols," SIGMOD 1981 (original 3PC); Bernstein, Hadzilacos, Goodman, *Concurrency
  Control and Recovery in Database Systems*, 1987 (2PC/3PC textbook treatment, cited by Gray & Lamport as ref [3]).
- Herlihy and Wing, "Linearizability," ACM TOPLAS 1990 (carried forward from clusters 2/3 — still blocked).
- DeCandia et al., "Dynamo," SOSP 2007 (carried forward — still blocked; needed to harden the AP/PA-EL example).

---

## 3. Why it is this way — constraints that forced the design

1. **Networks partition, so C-vs-A is unavoidable, not a design taste.** A partition is indistinguishable from slow
   nodes/lost messages; an available node must answer without the other side's state, so it cannot also be linearizable.
2. **Consistency costs round-trips even when healthy (PACELC's "ELSE").** Keeping replicas in agreement means waiting
   for a quorum/leader; the only way to skip the wait is to weaken the contract. CAP hides this; PACELC names it.
3. **Atomic commit needs a single agreed decision.** Partial commits violate the all-or-nothing contract, so some
   process(es) must hold the canonical decision and survivors must be able to learn it.
4. **A single decision-holder is a single point of blocking (and, if duplicated naively, of inconsistency).** 2PC
   blocks when the lone TM dies post-prepare; classic 3PC tries to elect a replacement TM but can split-brain into an
   actual inconsistency. The principled fix is consensus over a quorum.
5. **Consensus needs `2F + 1` participants to tolerate `F` failures without synchrony.** Majority intersection
   (cluster 3) is the reason; Paxos Commit applies it to the commit decision so `F + 1` survivors can still decide.
6. **FLP sets the ceiling.** No deterministic asynchronous protocol is *both* always-safe and always-live under a
   single crash, so every real commit protocol either blocks (2PC) or leans on timing/leader assumptions for liveness
   while keeping safety unconditional (Paxos Commit).

---

## 4. Common misconceptions to preempt

- **"CAP means pick two of three."** No. Partition tolerance is mandatory for a networked system; the real choice is
  C vs. A *during a partition*. Brewer's own retrospective corrects the 2-of-3 framing.
- **"CAP's C is just 'consistency' generally."** No. It is linearizability/atomic single-copy. Weaker contracts
  (eventual, causal) sidestep the theorem because they never promised both sides agree immediately.
- **"If there's no partition, strong consistency is free."** No — that's exactly the gap PACELC fills: strong
  consistency still pays latency (quorum/leader round-trips) in normal operation.
- **"CA systems exist."** A single-node or non-distributed store can be "CA" trivially, but for a real distributed
  system "CA" means "we ignore partitions," which just means undefined behavior when one happens.
- **"2PC is unsafe."** Wrong direction. 2PC is *safe* (never a split commit); its flaw is *liveness* — it blocks when
  the coordinator dies after everyone prepared.
- **"3PC fixes 2PC for free."** Classic 3PC removes blocking under benign timing assumptions but can produce real
  inconsistency under split-brain coordinators/partitions; Gray & Lamport explicitly note none of the classic ones has
  a proven correctness condition. Paxos Commit is the version with a precise fault model.
- **"Paxos Commit is unrelated to 2PC."** It generalizes it: 2PC is exactly Paxos Commit with `F = 0` (a single
  acceptor). That's why one failure blocks 2PC.
- **"Distributed transactions = strong consistency."** Only with the full stack: concurrency control (2PL or SI/MVCC)
  + atomic commit (2PC/Paxos Commit) + replication (Paxos/Raft) + a real-time ordering device for *external*
  consistency (Spanner's commit wait/TrueTime).

---

## 5. Best build-your-own targets

- **Partition simulator:** two replica groups, a toggleable network cut, and a client that issues reads/writes to each
  side. Let the learner choose CP (refuse on the minority side) vs. AP (answer + diverge) and watch the resulting
  histories, then run a reconciliation pass on heal (Brewer's partition-recovery mode).
- **2PC visualizer with a kill switch:** TM + N RMs with stable-storage logs; kill the TM right after all `Prepared`
  messages and show the RMs blocked holding locks — the textbook blocking failure made tangible.
- **2PC → Paxos Commit upgrade:** replace the single TM with `2F + 1` acceptors; kill `F` of them and show the
  decision still completes (progress with `F + 1`), and that two "leaders" never produce conflicting commits.
- **PACELC dial:** a replicated KV store with a tunable "ack after K replicas" knob; plot write latency vs. staleness
  to make the EL-vs-EC trade-off measurable, then cut the network to show the PA-vs-PC trade-off.
- **Isolation-level harness:** layer 2PL vs. snapshot isolation over the commit protocol; demonstrate a write-skew
  anomaly under SI that serializable 2PL forbids.

These are build-lab candidates only. Do not start `/build` during Phase 1.

---

## 6. Open questions / gaps

- **CAP/PACELC primaries unfetched this session.** Gilbert/Lynch 2002, Brewer 2000/2012, and Abadi 2012 were all
  network-blocked; every CAP/PACELC claim above that quotes or paraphrases those papers is `[UNVERIFIED from fetched
  source]` and must be confirmed before Phase 2 prose. In particular: Gilbert/Lynch's exact network model and
  availability definition; whether their partial-synchrony variant changes the result; Brewer's exact "partition mode"
  and recovery wording; Abadi's exact PACELC definition and his per-system classifications.
- **3PC original (Skeen 1981) unfetched.** Gray & Lamport critique classic 3PC but cite Skeen; the precise 3PC
  pre-commit state machine and its exact failure assumptions need Skeen 1981 (or Bernstein/Hadzilacos/Goodman 1987)
  before Phase 2.
- **Isolation-level formalism is shallow here.** This brief uses Spanner's verified 2PL / snapshot-isolation wording
  but does not yet anchor the ANSI/Berenson "A Critique of ANSI SQL Isolation Levels" definitions (dirty read, write
  skew, phantom). Add that source before Phase 2 isolation prose.
- **Herlihy/Wing and Dynamo still blocked.** Carried forward from clusters 2 and 3 — needed to fully harden the
  linearizable-C anchor and the AP/PA-EL example. Do not erase these gaps on reconciliation.
- **Gray & Lamport TODS-vs-tech-report pagination.** Claims above cite the 37-page tech-report PDF on lamport's site;
  re-pin to the published ACM TODS 2006 version (vol. 31, no. 1) page/section numbers before Phase 2 if exact citations
  are needed.
