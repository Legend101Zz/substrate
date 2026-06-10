# Research Brief — Sub-course 11: Distributed Systems Foundations
## Source cluster: time, clocks, ordering, causality, global state, and partial failure
## Researcher: brain manual primary-source pass | Date: 2026-06-10

Status: **starter cluster**. Sources were fetched and text-extracted into `/tmp/substrate-11-sources` on
2026-06-10 using a throwaway `uv run --with pypdf` environment; `/Users/m0t0hu6/.code-puppy-venv` was not modified.
This brief is factchecked in `11-distributed-systems-foundations/_factcheck_phase1.md`.

---

## 1. Key mechanisms

### 1.1 The first trap: distributed systems do not have one obvious “now”

Intuitive model: in one process, events naturally line up because the process executes them in program order. In a
distributed system, every machine has its own local timeline and communicates by messages. If two events happen on
different machines and no message chain connects them, there may be no fact inside the system that says which one
“really happened first.”

Deep mechanism: Lamport defines the happened-before relation as the smallest relation satisfying three rules:
1. if two events are in the same process and `a` comes before `b`, then `a -> b`;
2. if `a` sends a message and `b` receives that same message, then `a -> b`;
3. transitivity: if `a -> b` and `b -> c`, then `a -> c`.
Two distinct events are concurrent when neither happened-before relation holds. Lamport states this relation is an
irreflexive partial ordering over system events.

Source: Lamport, “Time, Clocks, and the Ordering of Events in a Distributed System,” CACM 1978,
`https://lamport.azurewebsites.net/pubs/time-clocks.pdf`, extracted lines around 90–170.

Course consequence: teach order as an information-flow relation before teaching wall clocks. If the system did not
carry information from `a` to `b`, treating `a < b` as a semantic fact is usually smuggling in an external observer.

### 1.2 Logical clocks preserve causality, not real time

Intuitive model: a logical clock is a receipt counter. It does not tell the time of day; it tells whether this process
has heard enough history to place one event after another.

Deep mechanism: Lamport’s Clock Condition says that for any events `a` and `b`, if `a -> b`, then `C(a) < C(b)`.
Lamport also gives implementation rules:
- `IR1`: each process increments its local clock between successive events;
- `IR2`: a sent message carries timestamp `Tm = Ci(a)`, and a receiver advances its clock to be greater than both its
  current value and `Tm` before recording the receive event.
Those rules imply the Clock Condition.

Important non-converse: `C(a) < C(b)` does **not** imply `a -> b`. Different concurrent events can be assigned an
arbitrary order by clock values and tie-breakers. The clock preserves known causality; it does not discover hidden
causality.

Source: Lamport 1978, `time-clocks.pdf`, extracted lines around 230–320.

### 1.3 Total order is useful, but its extra ordering is arbitrary

Intuitive model: sometimes a protocol needs every participant to process requests in the same sequence. Logical clocks
can help manufacture such a sequence, but the manufactured sequence contains policy choices, not newly discovered
physics.

Deep mechanism: Lamport shows how to extend the partial order to a total order by sorting events by logical timestamp
and breaking ties with an arbitrary total ordering of processes. The result extends happened-before: if `a -> b`, then
`a` comes before `b` in the total order. But Lamport explicitly notes that this total order is not unique; different
clock choices can yield different total orders, and only the partial ordering is uniquely determined by the events.

Source: Lamport 1978, `time-clocks.pdf`, extracted lines around 318–360.

Course consequence: when later teaching logs, replicated state machines, linearizability, and consensus, separate:
- causal order: forced by computation and messages;
- chosen total order: agreed by protocol;
- wall-clock order: external physical-time order, only usable when the clock assumptions are explicit.

### 1.4 Physical clocks require bounds; “close enough” is a theorem obligation

Intuitive model: wall clocks are not magic; they are sensors with error bars. Distributed algorithms that depend on
wall time need those error bars in the design.

Deep mechanism: Lamport’s physical-clock section introduces conditions on clock drift and synchronization. The paper
states that a physical clock must run at approximately the correct rate, with a bounded rate error, and synchronized
clocks must remain within a small bound of each other. It also distinguishes a stronger physical-time ordering condition
from ordinary logical clocks.

Spanner makes this modern and operational: TrueTime returns an interval `[earliest, latest]`, not a single timestamp,
and guarantees that the absolute invocation time lies inside that interval. Spanner’s paper says that if uncertainty is
large, Spanner slows down to wait out that uncertainty; it “reifies” clock uncertainty in the API.

Sources:
- Lamport 1978, `time-clocks.pdf`, extracted lines around 543–610.
- Corbett et al., “Spanner: Google’s Globally-Distributed Database,” OSDI 2012,
  `https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf`, extracted lines
  around 392–418, 441–460, and 1255–1261.

Course consequence: never say “use timestamps” without saying which clock model backs them: unsynchronized local
clock, NTP-ish best effort, bounded uncertainty interval, lease clock with drift assumptions, or consensus-derived
logical order. Those are different animals; pretending otherwise is how systems get spicy at 3 a.m.

### 1.5 A global snapshot is a consistent cut, not a synchronized photograph

Intuitive model: if photographers take separate pictures of a moving flock, the stitched panorama might show one bird
twice or miss it entirely. Distributed snapshots have the same problem with in-flight messages.

Deep mechanism: Chandy and Lamport define a global state as the set of process states plus channel states. Their paper
emphasizes that processes cannot all record local state at precisely the same instant unless they share a common clock,
and assumes no shared clocks or memory. A naive composite can be inconsistent: in their token example, recording a
sender before it sends and a channel after the send can show two tokens; recording channel before send and receiver
afterward can show no token. The snapshot algorithm records a state that may not be identical to any physical global
state that occurred, but the paper proves it is meaningful via reachability: the recorded state is reachable from the
initiation state and can reach the termination state.

Source: Chandy and Lamport, “Distributed Snapshots: Determining Global States of Distributed Systems,” ACM TOCS 1985,
`https://lamport.azurewebsites.net/pubs/chandy.pdf`, extracted lines around 29–65, 159–168, 263–292, and 383–410.

Course consequence: later observability/debugging sections should teach traces, checkpoints, and metrics as partial
cuts through a computation, not omniscient truth. A dashboard is a sampled cut, not the voice of destiny.

### 1.6 Partial failure: without time assumptions, “dead” and “slow” are indistinguishable

Intuitive model: if another process stops responding, you cannot tell whether it crashed, the network delayed your
messages, your reply was lost, or the remote process is merely slow. Humans call it “down” after waiting too long;
that phrase already smuggles in a timeout and a service expectation.

Deep mechanism: Lamport observes that failure is only meaningful in the context of physical time; without physical
time, there is no way to distinguish a failed process from one pausing between events. FLP makes the point formal for
consensus: in a completely asynchronous model with reliable message delivery, no assumptions about process speeds or
message delay, no synchronized clocks, and no death detector, no consensus protocol can tolerate even one unannounced
process death. The paper explicitly says algorithms based on timeouts cannot be used in that model and that a process
cannot tell whether another has died or is just running very slowly.

Sources:
- Lamport 1978, `time-clocks.pdf`, extracted lines around 490–510.
- Fischer, Lynch, and Paterson, “Impossibility of Distributed Consensus with One Faulty Process,” JACM 1985,
  `https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf`, extracted lines around 64–89, 112–120, and 326–328.

Course consequence: teach timeouts as engineering guesses layered on top of an asynchronous reality. They are useful
and necessary in production, but they are not proof that a remote process crashed.

### 1.7 Failure detectors name the assumption instead of pretending it vanished

Intuitive model: a failure detector is the system’s gossip column about who might be dead. It can be wrong. Useful
protocols specify how wrong it may be and whether those mistakes eventually stop.

Deep mechanism: Chandra and Toueg introduce unreliable failure detectors for asynchronous systems with crash failures,
classifying them with completeness and accuracy properties. A detector can suspect a process even if that process is
only very slow; practical detectors often increase timeouts to reduce false suspicions. This source was fetched as
PostScript from Cornell (`CT96-JACM.ps`); text extraction via `strings` is noisy, so exact theorem statements should be
rechecked before Phase 2 prose.

Source: Chandra and Toueg, “Unreliable Failure Detectors for Reliable Distributed Systems,” JACM 1996,
`https://www.cs.cornell.edu/info/people/sam/FDpapers/CT96-JACM.ps`, extracted/noisy string lines around 6608–7041 and
7317–7454. Mark exact definitions `[UNVERIFIED from clean text]` until a cleaner source is fetched.

Course consequence: when a production system says “member failed,” the mechanism is usually “member was suspected by
a detector configured with timeout/heartbeat rules.” The honest teaching move is to expose the detector’s assumptions.

---

## 2. Foundational sources

Primary sources fetched in this pass:

- Lamport, “Time, Clocks, and the Ordering of Events in a Distributed System,” CACM 1978.
  `https://lamport.azurewebsites.net/pubs/time-clocks.pdf`
  - Anchors: happened-before definition; Clock Condition; implementation rules IR1/IR2; arbitrary total-order
    extension; physical clock drift/synchronization assumptions; failure requires physical-time context.
- Chandy and Lamport, “Distributed Snapshots: Determining Global States of Distributed Systems,” ACM TOCS 1985.
  `https://lamport.azurewebsites.net/pubs/chandy.pdf`
  - Anchors: global state = process states + channel states; no shared clocks/memory; inconsistent naive cuts;
    meaningful recorded global state via reachability.
- Fischer, Lynch, and Paterson, “Impossibility of Distributed Consensus with One Faulty Process,” JACM 1985.
  `https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf`
  - Anchors: completely asynchronous model; no process-speed/message-delay assumptions; no synchronized clocks;
    no death detector; one crash can prevent deterministic consensus termination.
- Corbett et al., “Spanner: Google’s Globally-Distributed Database,” OSDI 2012.
  `https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf`
  - Anchors: TrueTime interval API; bounded uncertainty; waiting out uncertainty; stronger time semantics from
    explicit uncertainty.
- Chandra and Toueg, “Unreliable Failure Detectors for Reliable Distributed Systems,” JACM 1996.
  `https://www.cs.cornell.edu/info/people/sam/FDpapers/CT96-JACM.ps`
  - Anchors: completeness/accuracy framing for failure detectors; exact definitions need clean-text verification.

Secondary/course anchors discovered but not deeply used yet:
- MIT 6.5840/6.824 current schedule (`https://pdos.csail.mit.edu/6.824/schedule.html`) confirms course placement of
  fault tolerance/Raft and linearizability material, but this cluster did not rely on it for mechanisms.

---

## 3. “Why it is this way” constraints

1. **No shared memory:** processes can directly record only their local state and messages they send/receive. Global
   reasoning must be reconstructed from communication.
2. **Finite message speed and variable delay:** a receive can be causally after a send, but absence of a receive at time
   `t` does not prove absence forever.
3. **Independent clocks drift:** physical clocks need rate and synchronization bounds; without bounds, timestamps are
   observations, not ordering guarantees.
4. **Asynchrony erases failure certainty:** if there are no bounds on process speed or message delay, “slow” and
   “dead” cannot be distinguished by observation alone.
5. **Protocols create order:** total order in replicated systems is not discovered floating in the ether; it is chosen by
   a protocol under stated assumptions.

---

## 4. Common misconceptions to preempt

- “Distributed systems are just concurrent systems over the network.” Not quite. Concurrency gives interleavings;
  distribution adds independent clocks, message delay, partial failure, and no single memory/observer.
- “Timestamps solve ordering.” Only if the timestamp source has the needed guarantees. Lamport timestamps preserve
  happened-before but do not identify all real-time ordering; physical timestamps need bounded drift/synchronization.
- “If my timeout fired, the other node is dead.” No: it is suspected. The node, network, scheduler, GC, kernel, or client
  could be slow. Cute little timeout, huge ego.
- “A global snapshot is exactly what happened at one instant.” Chandy-Lamport snapshots can be meaningful without
  matching an actual physical instant; consistency is about cuts and reachability.
- “FLP means consensus is impossible in practice.” FLP says deterministic consensus cannot guarantee termination in the
  fully asynchronous model with even one crash. Practical systems add assumptions: timing, randomness, failure detectors,
  leases, quorum availability, operator intervention, or eventually synchronous behavior.

---

## 5. Best build-your-own targets

- **Visual Lamport-clock simulator:** N processes, message sends/receives, logical clock updates, and a display showing
  happened-before vs arbitrary total order.
- **Consistent-cut lab:** simulate in-flight token/message movement and show why naive snapshots duplicate/drop tokens;
  then implement marker-based Chandy-Lamport snapshot for FIFO channels.
- **Failure-detector playground:** heartbeat + timeout detector where users tune delay distributions and watch false
  suspicions, detection latency, and “eventual” stabilization.

These are build-lab candidates only. Do not start `/build` during Phase 1.

---

## 6. Open questions / gaps

- Fetch a cleaner text/PDF source for Chandra-Toueg before exact Phase 2 prose; current PostScript extraction is noisy.
- Add vector clocks/version vectors in the next 11 cluster or a dedicated causality subcluster; this starter only covers
  Lamport scalar clocks.
- Add linearizability and consistency vocabulary in the next 11 cluster, using Herlihy/Wing and MIT 6.5840 notes.
- Add replication/quorum sources after the time/failure foundation is accepted: Raft extended paper, Paxos Made Simple,
  Dynamo, Spanner sections beyond TrueTime, and DDIA only where directly accessible.
- Clarify model boundaries: asynchronous vs synchronous vs partially synchronous vs eventually synchronous. This brief
  names the asynchronous edge but does not yet build the full taxonomy.
