# Research Brief — Sub-course 11: Distributed Systems Foundations
## Source cluster: vector clocks, version vectors, causal histories, and model taxonomy
## Researcher: researcher-ce3aaf | Date: 2026-06-10

Status: **cluster 2 brief**. This is NOT a reconciled full-11 brief. It extends the starter cluster
`_research_time-clocks-ordering-failure.md` which covers Lamport scalar clocks, Chandy-Lamport
snapshots, FLP, Spanner TrueTime, and Chandra-Toueg failure detectors.

Source availability note: Fidge 1988, Mattern 1989, and DLS 1988 (JACM) could not be fetched
directly due to network domain restrictions (csail.mit.edu, ethz.ch, acm.org all timed out or
returned HTTP 000/403). Claims derived from those three papers are marked [UNVERIFIED from fetched
source]. The FLP paper (already fetched) explicitly cites DLS88 in its references (line 365) and in
its conclusion directly motivates the partial-synchrony research program, giving secondary
confirmation that DLS88's topic and framing are accurately described here. Paxos Made Simple was
fetched from lamport.azurewebsites.net and later extracted successfully with `pypdf` into
`/tmp/substrate-11-sources/paxos-simple.txt`; Paxos claims in this brief should cite that extracted
text directly. All other claims are anchored to fetched and extracted source text or explicitly
marked `[UNVERIFIED]`.

---

## 1. Key mechanisms

### 1.1 Why scalar Lamport clocks are insufficient: the converse failure

Intuitive model: Lamport timestamps are like receipt numbers at a deli. Higher number means you came
later — but only if you were at the same deli, and only in one direction. Two customers at different
deli branches can have any order of receipt numbers without any causal relationship.

Deep mechanism: Lamport 1978 explicitly proves the Clock Condition is necessarily asymmetric. He
writes (fetched text, lines 239-248):

  "Clock Condition. For any events a, b: if a --> b then C(a) < C(b). Note that we cannot expect
   the converse condition to hold as well, since that would imply that any two concurrent events must
   occur at the same time. In Figure 1, p2 and p3 are both concurrent with q3, so this would mean
   that they both must occur at the same time as q3, which would contradict the Clock Condition
   because p2 ---> p3."

The forcing constraint: if you demanded that C(a) < C(b) implies a → b, then concurrent events (by
definition: neither can causally affect the other) would be forced to carry identical timestamps,
contradicting the need for different events to be distinguishable. The system would collapse.

Practical consequence: given two events with Lamport timestamps 5 and 7, you cannot tell whether:
- the earlier event caused the later (causal),
- they are completely unrelated (concurrent), or
- they were ordered by the arbitrary tie-breaking rule.

You cannot detect or communicate concurrency with scalar clocks. This is the gap vector clocks fill.

Source: Lamport, "Time, Clocks, and the Ordering of Events in a Distributed System," CACM 1978.
`https://lamport.azurewebsites.net/pubs/time-clocks.pdf`, extracted lines 230-265.

### 1.2 Vector clocks: closing the converse gap

Intuitive model: instead of one counter per process, each process keeps a list of counters — one per
process in the system. Whenever a message arrives, the receiver updates its list to remember the
most advanced "view" it has seen from every sender. Two events can now be compared precisely because
each event carries a full picture of the sender's knowledge of the entire system at the moment of
sending.

Deep mechanism — the Fidge/Mattern algorithm [UNVERIFIED from fetched source; algorithm is standard
in distributed systems textbooks and mutually confirmed by both independent papers]:

Process Pi maintains a vector VC_i[0..N-1], initialized to all zeros. Three rules:

  Rule 1 (local step): Before each local event, increment VC_i[i].
  Rule 2 (send): When Pi sends a message, attach the current vector VC_i.
  Rule 3 (receive): When Pi receives a message carrying timestamp VC_m, set
    VC_i[k] = max(VC_i[k], VC_m[k]) for all k, then increment VC_i[i].

Comparison: define VC(a) <= VC(b) iff VC(a)[k] <= VC(b)[k] for ALL k.
Define VC(a) < VC(b) iff VC(a) <= VC(b) AND VC(a) != VC(b).
Define VC(a) || VC(b) iff neither VC(a) < VC(b) nor VC(b) < VC(a).

Strong Clock Condition in the vector-clock literature (following Fidge/Mattern, still
[UNVERIFIED from fetched source]; note Lamport 1978 uses the same phrase for a distinct physical-clock
property):
  a → b  iff  VC(a) < VC(b)
  a || b  iff  VC(a) || VC(b)

This is the key gain over Lamport clocks: the relationship is bidirectional. You can detect
concurrency directly from the timestamps.

Why it works: VC_i[j] counts the number of events at Pj that Pi knows about (transitively via
messages). If two processes have incomparable vectors, there exists at least one index where each
has a count the other has not yet seen — meaning each has done something the other is not aware of,
which is exactly the definition of concurrency.

Forcing constraint: the O(N) vector size is the fundamental cost. You cannot detect concurrency
with a scalar (O(1)) clock because a scalar cannot represent N independent "knowledge frontiers."
This is a known lower bound: detecting concurrency requires at least O(N) state [UNVERIFIED from
fetched source; see Charron-Bost 1991 which proved that N integers are necessary and sufficient].

Sources (primary papers not fetchable):
- Fidge, "Timestamps in Message-Passing Systems That Preserve the Partial Ordering,"
  11th Australian Computer Science Conference, 1988.
  [UNVERIFIED from fetched source] — standard citation:
  https://dl.acm.org/doi/10.5555/8514.8686
- Mattern, "Virtual Time and Global States of Distributed Systems," in Cosnard et al. (eds.),
  Parallel and Distributed Algorithms, 1989.
  [UNVERIFIED from fetched source] — canonical URL:
  https://vs.inf.ethz.ch/publ/papers/mattern89.pdf (blocked during this research pass)
- Secondary anchor: these papers are well-attested in every major distributed systems textbook
  and are cited as the primary discovery by Coulouris et al., Tanenbaum and Van Steen, and
  MIT 6.5840 reading lists.

### 1.3 Version vectors: the data-version variant of vector clocks

Intuitive model: vector clocks timestamp events; version vectors timestamp data objects. The
distinction matters because you are not asking "which event happened first" but "which version of
this data dominates, or are there two conflicting versions that need merging?"

Deep mechanism [UNVERIFIED from fetched source for Amazon Dynamo; mechanism is described in
the Dynamo paper SOSP 2007 which was inaccessible during this pass]:

Each data item carries a version vector VV = [(node_1, counter_1), (node_2, counter_2), ...].
When a node writes an object, it increments its own counter in VV.
To compare two versions VV_A and VV_B:
  - If VV_A[k] <= VV_B[k] for ALL k: VV_B "dominates" — it is the later version.
  - If VV_A[k] >= VV_B[k] for ALL k: VV_A dominates.
  - Otherwise (some k has A higher, some k has B higher): conflict — both are "siblings" and
    need application-level resolution.

Key distinction from vector clocks:
- Vector clocks attach to events (process-level counters); N = number of processes.
- Version vectors attach to data items (replica-level counters); N = number of replicas of that
  item. In a large system, only the nodes that have written a given item appear in its vector.

Practical use: Amazon Dynamo (SOSP 2007) uses version vectors to detect conflicts when multiple
replicas of an item diverge during a network partition. The application must resolve siblings.
Riak uses the same mechanism; it introduced "dotted version vectors" (or "dot notation") to avoid
a specific bug in naive version vectors where two concurrent writes from the same client could be
incorrectly discarded as dominated [UNVERIFIED from fetched source — see Preguica et al. 2010 and
the Riak documentation].

Source: DeCandia et al., "Dynamo: Amazon's Highly Available Key-Value Store," SOSP 2007.
[UNVERIFIED from fetched source] — canonical URL:
https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf (blocked during this pass)

### 1.4 Causal histories and causal broadcast

Intuitive model: instead of tracking vector clocks (which count events), track the actual set of
events that causally preceded a given event. This is the "causal history" approach — more general
but O(events) in size, so practical implementations compress it to vector clocks.

Deep mechanism: a causal history H(a) for event a is the set of all events b such that b → a.
Comparing two events by causal history gives the same answer as comparing vector clocks, but is
conceptually cleaner for reasoning: a happens-before b iff H(a) ⊂ H(b) strictly.

Birman, Schiper, and Stephenson (1991) applied vector clocks to achieve causal broadcast (CBCAST):
[UNVERIFIED from fetched source]
- Each process maintains a vector clock.
- Each message carries the sender's vector clock at time of send.
- A receiver delivers a message from process j with vector VV_m only when:
  (a) VV_m[j] = VC_local[j] + 1 (no missed messages from j), AND
  (b) VV_m[k] <= VC_local[k] for all k != j (all causal predecessors already delivered).
- Otherwise the message is held in a queue until both conditions are satisfied.

Why causal ordering matters: if a user posts a comment and then posts a reply, a replica that
delivers the reply before the original comment shows nonsense. Causal delivery guarantees that
if message A causally precedes message B, every process delivers A before B. This is strictly
weaker than total order (two causally unrelated messages may be delivered in any order) but
strictly stronger than FIFO (only same-sender ordering guaranteed).

Source: Birman, Schiper, Stephenson, "Lightweight Causal and Atomic Group Multicast," ACM TOCS
1991. [UNVERIFIED from fetched source] — DOI: 10.1145/128738.128742.

### 1.5 Synchronous model: failure detection is exact, consensus is achievable

Intuitive model: in a fully synchronous system, if you send a message and the reply doesn't arrive
within the known maximum round-trip time, you know the recipient is dead — not "maybe slow."
Timing assumptions turn guesses into proofs.

Deep mechanism: the synchronous model defines two known bounds:
- delta: maximum message delivery time
- phi: maximum time for one process step

Given these bounds, a process that sends a message and waits delta + phi time for a reply with no
response can conclude the remote process has failed. This makes failure detection exact and
deterministic: the detector makes no mistakes (strongly accurate AND strongly complete).

With exact failure detection, consensus becomes solvable:
- Simple rotating coordinator protocol: try coordinator 1, if silent for delta+phi, try coordinator 2, etc.
- Requires at most f+1 rounds where f is the number of crash failures, and N >= f+1 processes
  (at least one correct coordinator must survive). Note: quorum-based protocols that additionally
  require majority overlap for validity need N >= 2f+1, but the pure rotating-coordinator timeout
  scheme only requires N > f. [Source needed for the f+1-round crash-fault result — standard result;
  see Lynch 1996 *Distributed Algorithms* or equivalent before Phase 2 prose.]

The FLP paper confirms: "solutions are known for the synchronous case, the 'Byzantine Generals'
problem" (fetched text, line 16). The Byzantine Generals paper (Lamport, Shostak, Pease 1982)
works precisely because it assumes a synchronous model with known round bounds.

Forcing constraint: synchrony assumptions are strong. In a real network, message delays can be
unbounded (congestion, packet loss, retransmission). The synchronous model is appropriate for
tightly controlled networks, hardware synchronization, or systems where timing is explicitly
enforced (e.g., real-time systems with bounded network fabrics).

Source (synchronous model definition): [UNVERIFIED from fetched DLS88 primary source] — the
contrast is confirmed by FLP lines 16 and 326-328.

### 1.6 Asynchronous model: the FLP world — timing assumptions are zero

Intuitive model: in the fully asynchronous model, a message might arrive in 1 millisecond or in
1 year; you cannot tell the difference from the outside. Similarly, a process might respond in 1
microsecond or it may be dead — you cannot tell. This is not pessimism; it is the honest model for
the open internet.

Deep mechanism (VERIFIED from fetched FLP text):
FLP defines the asynchronous model with three explicit non-assumptions:
1. "We make no assumptions about the relative speeds of processes or about the delay time in
   delivering a message." (FLP lines 80-82)
2. "We also assume that processes do not have access to synchronized clocks, so algorithms based
   on time-outs, for example, cannot be used." (FLP lines 82-84)
3. "it is impossible for one process to tell whether another has died (stopped entirely) or is just
   running very slowly." (FLP lines 85-87)

The asynchronous model is deliberately strong (makes no assumptions) to maximize the generality of
the impossibility result. If consensus is impossible even under the weakest assumptions, it is
impossible under every stronger model that has the asynchronous model as a special case.

Result: FLP Theorem 1 says no consensus protocol can be "totally correct" in this model in spite of
one fault. Here "totally correct" means the protocol cannot guarantee both the required safety/validity
properties and liveness/termination under the fully asynchronous assumptions. (FLP Theorem 1, fetched
text.)

Source: Fischer, Lynch, Paterson, "Impossibility of Distributed Consensus with One Faulty
Process," JACM 1985. `https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf`.
(Fetched previously; text extracted in /tmp/substrate-11-sources/flp.txt.)

### 1.7 Partially synchronous model: the DLS bridge between FLP and reality

Intuitive model: real systems are usually fast and synchronized — messages arrive within seconds,
processes respond quickly — but occasionally they are not, due to network partitions, GC pauses,
or overload. Partial synchrony captures this: bounds exist but may not always hold (or may not be
known a priori).

Deep mechanism [UNVERIFIED from fetched source — DLS88 was inaccessible; the framing below is from
well-established secondary description of the paper plus FLP's own citation of it]:

Dwork, Lynch, Stockmeyer (JACM 1988, DOI: 10.1145/42282.42283) define two partial-synchrony
models:

Model 1 — Unknown bounds: Bounds delta and phi on message delay and processing time exist, but
their values are not known to the processes. The system will eventually satisfy these bounds, but
processes do not know when or what the bounds are. No process can compute a correct timeout for
failure detection, yet the system does eventually become "synchronous enough."

Model 2 — Global Stabilization Time (GST): Bounds delta and phi are known, but they only hold
after some unknown future time GST. Before GST, the system is asynchronous; after GST, it is
synchronous. Processes know the bounds but do not know when GST arrives.

DLS show that consensus is solvable in both models, despite being impossible in the fully
asynchronous model. [UNVERIFIED exact theorem from fetched source.]

Why these models are realistic:
- Internet behavior: during normal operation, most messages arrive within milliseconds (post-GST).
  During a partition or overload, there are no useful bounds (pre-GST or unknown bounds).
- The partial-synchrony model says: a correct protocol can be safe even in asynchronous phases
  (no wrong decisions ever) and live in synchronous phases (eventually makes progress once the
  network stabilizes).
- This is exactly the behavior of Paxos and Raft: they guarantee safety unconditionally; they
  guarantee liveness only when a stable leader can gather a quorum of responding replicas.

FLP confirms DLS motivation from its own conclusion (fetched text, lines 325-333):
  "These results do not show that such problems cannot be 'solved' in practice; rather, they point
   up the need for more refined models of distributed computing that better reflect realistic
   assumptions about processor and communication timings, and for less stringent requirements on
   the solution to such problems. [...] Subsequent to the original announcement of these results
   [12], progress has been made along both of these lines [1-4, 9, 10, 20, 25]."
Reference 10 in that list (FLP extracted lines 365-367) is explicitly:
  "DWORK, C., LYNCH, N., AND STOCKMEYER, L. Consensus in the presence of partial synchrony. In
   Proceedings of the 3rd Annual ACM Symposium on Principles of Distributed Computing (Vancouver,
   B.C., Canada, Aug. 27-29). ACM, New York, 1984, pp. 103-118."

Source (primary content): Dwork, Lynch, Stockmeyer, "Consensus in the Presence of Partial
Synchrony," JACM 35(2):288-323, April 1988. DOI: 10.1145/42282.42283.
[UNVERIFIED from fetched source — exact theorem statements not directly confirmed from text;
existence and framing confirmed via FLP reference at line 365.]

### 1.8 Eventually synchronous model and failure detectors

Intuitive model: instead of requiring that the system has explicit timing bounds, require only that
some "oracle" eventually makes correct guesses about who is dead. This is the failure detector
abstraction from Chandra-Toueg 1996.

Deep mechanism: the eventually synchronous model arises when failure detectors have "eventual
accuracy" — they may produce false suspicions initially, but eventually stop suspecting correct
processes. Combined with "strong completeness" (every crashed process is eventually suspected
permanently), this gives a practical system that:
- Cannot be confused forever by a live slow process, and
- Eventually terminates once the system stabilizes.

Relationship to partial synchrony: the eventually synchronous model and the DLS Model 2 (GST)
capture essentially the same intuition from different angles. DLS speaks directly about timing
bounds; Chandra-Toueg speak about what a failure detector with those bounds can compute. The two
are deeply connected: in a partially synchronous system (Model 2), a failure detector of class
◇S (eventually strong) can be implemented, and ◇S is sufficient to solve consensus.
[UNVERIFIED exact equivalence from fetched source — see CT96.]

The Chandra-Toueg failure detector taxonomy (from prior cluster 1 brief, with noisy PostScript
extraction warning preserved):
- Completeness: strong (every crashed process eventually suspected) vs. weak (at least one
  eventually suspected).
- Accuracy: strong (no correct process ever suspected) vs. eventual (eventually no correct process
  is suspected).
- ◇S (eventually strong): strong completeness + eventual accuracy. Sufficient for consensus.
- ◇W (eventually weak): weak completeness + eventual accuracy. Sufficient for consensus via
  reduction from ◇W to ◇S.

Source: Chandra and Toueg, "Unreliable Failure Detectors for Reliable Distributed Systems," JACM
1996. (CT96 text noisy from PostScript; exact theorem statements remain flagged from cluster 1.)

### 1.9 Why timing assumptions change what is solvable

The fundamental reason: in a distributed system, failure detection is the core capability that
enables consensus. Timing assumptions determine exactly what a failure detector can provide.

Synchronous: exact failure detection (wait delta+phi, no answer = dead). Consensus: easy.
Asynchronous: zero failure detection. Consensus: impossible (FLP). No amount of cleverness helps.
Partially synchronous: eventually-accurate failure detection. Consensus: solvable, but only
  eventually — the protocol must wait for the synchronous phase to arrive.
Eventually synchronous: same as partial synchrony from a solvability standpoint.

This is a solvability phase transition: adding even a small timing assumption (a bound that
eventually holds) crosses the threshold from "impossible" to "eventually possible." The price is
that liveness is conditional — you cannot guarantee termination in any bounded number of steps in
the worst case, only "eventually."

The intuition for WHY: FLP works by showing that for any proposed consensus protocol, there is
always some scheduling of messages and crashes that keeps the protocol in a "bivalent" (undecided)
state forever. The adversary can do this because it can delay messages arbitrarily. Once there is a
bound on message delay (even an eventually-holding one), the adversary can no longer delay
indefinitely after GST. After GST, the protocol's timeouts become meaningful and the adversary
loses the ability to maintain bivalence forever.

Sources:
- FLP (VERIFIED): defines the asynchronous model and proves the impossibility; lines 80-87 and
  conclusion lines 325-333.
- DLS88 (citation VERIFIED via FLP reference at line 365; content [UNVERIFIED from fetched source]).

---

## 2. Foundational sources

### Verified/fetched in this cluster

| Source | Status | Canonical URL |
|--------|--------|---------------|
| Lamport 1978 (CACM) | VERIFIED (prior cluster, re-used) | `https://lamport.azurewebsites.net/pubs/time-clocks.pdf` |
| FLP 1985 (JACM) | VERIFIED (prior cluster, re-used for model + DLS citation) | `https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf` |
| Paxos Made Simple (Lamport 2001) | VERIFIED (fetched + extracted via `pypdf` to `/tmp/substrate-11-sources/paxos-simple.txt`) | `https://lamport.azurewebsites.net/pubs/paxos-simple.pdf` |

### Primary sources not fetchable (blocked domains)

| Source | Status | Canonical URL / DOI |
|--------|--------|---------------------|
| Fidge 1988 (ACSC) | [UNVERIFIED from fetched source] | `https://dl.acm.org/doi/10.5555/8514.8686` |
| Mattern 1989 | [UNVERIFIED from fetched source] | `https://vs.inf.ethz.ch/publ/papers/mattern89.pdf` |
| DLS88 (JACM 1988) | [UNVERIFIED from fetched source; existence/framing confirmed via FLP ref] | DOI: 10.1145/42282.42283 |
| Dynamo SOSP 2007 | [UNVERIFIED from fetched source] | `https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf` |
| Birman/Schiper/Stephenson 1991 | [UNVERIFIED from fetched source] | DOI: 10.1145/128738.128742 |
| Chandra-Toueg CT96 (JACM) | FETCHED but noisy (PostScript, prior cluster) | `https://www.cs.cornell.edu/info/people/sam/FDpapers/CT96-JACM.ps` |

### Supporting confirmed claims in FLP (fetched text)

FLP line 16: "By way of contrast, solutions are known for the synchronous case, the 'Byzantine
Generals' problem." (Confirms: synchronous model has consensus solutions.)

FLP lines 80-87: Full asynchrony definition (no speed bounds, no synchronized clocks, no death
detection). (Confirms: asynchronous model.)

FLP lines 325-333: Conclusion explicitly motivates partial synchrony research and cites DLS88 as
reference [10]. (Confirms: DLS88 topic and motivation.)

FLP line 365: "DWORK, C., LYNCH, N., AND STOCKMEYER, L. Consensus in the presence of partial
synchrony. In Proceedings of the 3rd Annual ACM Symposium on Principles of Distributed Computing
(Vancouver, B.C., Canada, Aug. 27-29). ACM, New York, 1984, pp. 103-118."
(Confirms: DLS88 exists and the conference-version title and topic.)

---

## 3. Why it is this way — constraints that forced the design

1. **Scalar clocks are irreversible**: a scalar Lamport clock can only grow. Once two concurrent
   events get timestamps, their relationship is lost. There is no way to add more information to a
   scalar after the fact; the entire causal history must be encoded at send time. This forces a
   vector structure if you want bidirectional causal tracking.

2. **O(N) vector size is unavoidable**: to detect that process Pk has done something that process
   Pi has not yet heard about, Pi must maintain a counter for Pk. With N processes, N counters are
   needed. There is no compression of this into a smaller structure without losing information about
   which specific processes have had undelivered events (Charron-Bost 1991 proves N is a lower
   bound) [UNVERIFIED from fetched source].

3. **FLP's impossibility forces partial synchrony as the practical model**: in the real world,
   protocols must make progress. But pure asynchrony means a single slow process can block
   consensus forever. The only escape is to add timing assumptions. Partial synchrony is the
   weakest such assumption that still allows progress: after some stabilization point, the system
   behaves synchronously enough that failure detection becomes reliable.

4. **Liveness must be conditional**: no protocol can be unconditionally live in a model where the
   adversary controls message delivery order and timing. Paxos, Raft, and Zab all give up on
   unconditional liveness. What they preserve unconditionally is safety. Liveness is tied to
   "enough replicas are reachable and the leader is stable" — which is exactly the partial-synchrony
   stabilization condition.

5. **Version vectors decouple data versioning from event ordering**: the Dynamo model needs to
   track which replica last wrote an object, not which process step happened first. Version vectors
   reuse the vector comparison mechanism but attach it to data items, decoupling the question
   "which write is newer?" from the general event-ordering question. This is not an optimization;
   it is a different problem (data version lineage vs. event causality).

---

## 4. Common misconceptions to preempt

- **"Vector clocks solve ordering, so they solve consensus."** No. Vector clocks detect causality
  and concurrency, but detecting that two events are concurrent does not tell you how to resolve
  conflicting values. Consensus requires agreement on one value; vector clocks only tell you whether
  a conflict exists. Resolution is a separate problem.

- **"Vector clocks and version vectors are the same thing."** No. Vector clocks timestamp events in
  an execution (process-level); version vectors timestamp data objects (replica-level). The
  comparison algorithm is analogous, but the semantics differ: vector clock comparison asks "which
  event happened first?"; version vector comparison asks "which write is newer, or are they
  concurrent writes that need merging?"

- **"Partial synchrony means the system is usually slow."** No. Partial synchrony means timing
  bounds eventually hold — which for typical LAN or data-center networks means they hold almost all
  the time. The "partial" refers to the theoretical possibility of asynchronous phases (partitions,
  overload), not to the typical case.

- **"FLP proves that Paxos/Raft cannot work."** No. FLP proves impossibility in the FULLY
  ASYNCHRONOUS model, which excludes all timing assumptions. Paxos Made Simple describes Paxos using
  an asynchronous, non-Byzantine model, but notes that liveness requires "either randomness or real
  time — for example, by using timeouts" (Lamport 2001, extracted lines around 260–264). In practice,
  Paxos and Raft behave as if operating under partial synchrony: safe in all conditions, live when
  message delivery is timely enough for leader election to succeed.

- **"Logical (vector) clocks tell you real time."** No. A vector clock tells you the causal
  structure of the computation — which events are causally related and which are concurrent. It says
  nothing about wall-clock time, system time, or physical ordering. Events with vector clock
  timestamps 5 apart could be 1 nanosecond or 1 hour apart in physical time.

- **"A process with the same vector clock as another must be at the same point in the computation."**
  No. Two processes can have identical vector timestamps if they have both received the same set of
  messages (e.g., at initialization all zeros). Vector clock equality means "same causal knowledge,"
  not "same physical state." Processes can differ in internal state while having identical vector
  timestamps if all their state changes were concurrent with each other.

- **"GST (Global Stabilization Time) is something you can detect or measure."** No. GST in the
  DLS model is a theoretical construct — an unknown future time after which the synchrony bounds
  hold. A correct protocol must not require knowing when GST occurs. Protocols under partial
  synchrony must be safe before GST and live after it, without explicit GST detection.
  [UNVERIFIED — DLS exact definition not directly confirmed from fetched text.]

---

## 5. Best build-your-own targets

- **Vector clock visualizer**: N processes, user-driven sends/receives, real-time rendering of
  vector timestamps and the resulting happened-before/concurrent relationship graph. Let users
  corrupt one process and watch concurrency appear. Demonstrate that scalar Lamport clock cannot
  distinguish the same execution.

- **Causal delivery queue lab**: Implement CBCAST — processes send messages with vector timestamps;
  implement a delivery queue that holds messages until causal predecessors are delivered. Show the
  queue contents and delivery events. Compare to FIFO-only delivery (same sender order) and
  total-order delivery (more expensive).

- **Version vector conflict simulator**: simulate two replicas of a key-value store that diverge
  during a partition. Each replica writes independently. Show the version vectors growing, the
  moment when the vectors become incomparable (conflict), and how the application must resolve
  siblings. Add a third replica to show the fan-out of version vector size.

- **Partial synchrony workbench**: implement a simple consensus protocol (e.g., rotating
  coordinator with timeouts). Show it in three regimes:
  1. Synchronous: always terminates within known rounds.
  2. Fully asynchronous: adversarial scheduler blocks forever (FLP scenario).
  3. Partially synchronous: blocks until "GST" fires, then terminates.
  This concretizes the theoretical model taxonomy in executable code.

These are build-lab candidates only. Do not start /build during Phase 1.

---

## 6. Open questions / gaps

- **Fidge88 and Mattern89 exact text not fetched**: cannot verify the precise algorithm statements,
  the Strong Clock Condition theorem statement, or any paper-specific nuances. The algorithm
  described in section 1.2 is standard in textbooks and consistent across secondary sources, but
  exact wording from the original papers is not confirmed. Must fetch before Phase 2 prose.
  Recommended: try `https://dl.acm.org/doi/10.5555/8514.8686` after domain unblocking, or request
  the PDF from the author's institutional page.

- **DLS88 exact theorem statements not fetched**: the two partial-synchrony model definitions
  (Model 1 / Model 2 / GST) are well-established in the literature but the exact formal definitions
  and proof outlines are not confirmed from fetched source text. FLP confirms the paper exists and
  its topic. Must fetch before Phase 2 prose on partial synchrony. DOI: 10.1145/42282.42283.

- **Charron-Bost 1991 lower bound on vector size**: the claim that N counters are necessary
  (not just sufficient) is attributed to Charron-Bost's "Concerning the size of logical clocks in
  distributed systems" (1991). This was not fetched and is marked [UNVERIFIED from fetched source].

- **Dynamo version vector exact semantics**: the Dynamo paper (SOSP 2007) and the related dotted
  version vector correction (Preguica et al. 2010 or Riak documentation) were not fetchable. The
  distinction between plain version vectors and dotted version vectors (which prevents a
  false-dominance bug under concurrent sibling creation) needs primary-source confirmation.

- **Paxos Made Simple extraction now available**: `/tmp/substrate-11-sources/paxos-simple.txt` was
  extracted with `uv run --with pypdf` during this pass. Verified anchors: asynchronous non-Byzantine
  model (line ~47), progress/liveness via distinguished proposer and majority (lines ~252–265), and
  liveness requiring randomness or real time such as timeouts (lines ~260–264). Do not describe Paxos
  itself as "using DLS partial synchrony" unless that framing is sourced separately.

- **Birman/Schiper/Stephenson 1991 CBCAST exact delivery condition**: the causal delivery queue
  condition described in section 1.4 is standard, but the exact conditions and proof of correctness
  are not confirmed from fetched source text.

- **Eventually synchronous vs. partial synchrony equivalence**: the claim that DLS Model 2 and
  Chandra-Toueg's eventually-accurate failure detectors are "essentially equivalent" is a known
  result in distributed systems theory but was not directly confirmed from either the DLS88 or CT96
  fetched text (CT96 was noisy PostScript). This should be verified before Phase 2 prose.

- **Cluster 2 does not cover**: linearizability/sequential consistency/eventual consistency
  vocabulary, leader/follower and quorum mechanics, Raft/Paxos protocol internals, or CAP theorem.
  Those require a separate cluster before 11 is reconcilable.
