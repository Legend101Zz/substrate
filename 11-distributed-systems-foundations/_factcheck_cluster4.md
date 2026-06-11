# Factcheck — Sub-course 11, cluster 4 (CAP / partitions / PACELC + distributed commit)
## Checker: brain manual primary-source pass | Date: 2026-06-10
## Brief under check: `11-distributed-systems-foundations/_research_cap-partitions-distributed-commit.md`

Method: distributed-commit claims checked verbatim against the fetched/extracted primary text of Gray & Lamport,
"Consensus on Transaction Commit" (`/tmp/substrate-11-cap/txncommit.clean.txt`, from
`https://lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`), and against the cached Spanner OSDI
2012 text (`/tmp/substrate-11-sources/spanner.txt`) and Paxos Made Simple (`paxos-simple.txt`). CAP/PACELC claims could
NOT be checked against primaries this session — Gilbert/Lynch, Brewer, and Abadi were network-blocked (`HTTP 000`/403),
so those claims are reported as `[UNVERIFIED]` carry-forwards, not verified. `/Users/m0t0hu6/.code-puppy-venv` was not
modified.

Blockers found: **0.** Citation precision warnings: **2** (logged below, both already reflected as residual gaps in
the brief).

---

## Verified load-bearing claims (distributed commit) — with line receipts

1. **2PC blocks if the coordinator fails.** VERIFIED. Abstract: "The classic Two-Phase Commit protocol blocks if the
   coordinator fails." (`txncommit.clean.txt` line ~22.) §3.3: "the failure of the TM can cause the protocol to block
   until the TM is repaired ... if the TM fails right after every RM has sent a Prepared message, then the other RMs
   have no way of knowing whether the TM committed or aborted." (lines ~305–312.)

2. **Non-blocking commit definition.** VERIFIED. "A non-blocking commit protocol is one in which the failure of a
   single process does not prevent the other processes from deciding if the transaction is committed or aborted. They
   are often called Three-Phase Commit protocols." (lines ~301–306.)

3. **Classic 3PC can split-brain into inconsistency / no proven correctness condition.** VERIFIED (as the authors'
   stated claim). "we know of none that provides a complete algorithm proven to satisfy a clearly stated correctness
   condition ... [Bernstein, Hadzilacos, Goodman] fails to explain what a process should do if it receives messages
   from two different processes, both claiming to be the current TM." (lines ~308–315.) Note: this is Gray & Lamport's
   assessment of *classic* 3PC, faithfully attributed in the brief; not an absolute claim that all 3PC variants are
   broken.

4. **2PC normal-case cost = `3N − 1` messages, four message delays; `3N − 3` / three delays with TM co-location.**
   VERIFIED. "the RMs learn that the transaction has been committed after four message delays. A total of 3N − 1
   messages are sent. ... leaving 3N − 3 messages and three message delays." (lines ~279–282.)

5. **2PC stable-storage durability; failure+restart ≡ pausing.** VERIFIED. "Each process records its current state in
   stable storage before sending any message while in that state. ... Process failure and restart is equivalent to the
   process pausing, which is permitted by an asynchronous algorithm." (lines ~248–262.)

6. **`prepared` precondition for commit.** VERIFIED. The spec requires all RMs reach `prepared` before any commit; TM
   commits only "When it has received a Prepared message from all RMs." (lines ~136–141, ~218–220.)

7. **Paxos Commit uses `2F + 1` coordinators, makes progress with `F + 1` working.** VERIFIED. Abstract: "a
   transaction commit protocol that uses 2F + 1 coordinators and makes progress if at least F + 1 of them are working
   properly." (lines ~26–28.)

8. **Consensus lower bound: `2F + 1` acceptors needed to tolerate `F` failures without strict synchrony.** VERIFIED.
   "without strict synchrony assumptions, 2F + 1 acceptors are needed to achieve consensus despite the failure of any
   F of them." (lines ~331.)

9. **Paxos maintains safety under multiple leaders; multiple leaders cost only liveness.** VERIFIED. "Paxos maintains
   consistency, never allowing two different values to be chosen, even if multiple processes think they are the leader.
   ... A unique nonfaulty leader is needed only to ensure liveness." (lines ~340–345.)

10. **2PC = degenerate `F = 0` case of Paxos Commit (single acceptor).** VERIFIED. "The classic Two-Phase Commit
    algorithm is obtained as the special F = 0 case of the Paxos Commit algorithm." (line ~31.) §5: "The Two-Phase
    Commit protocol is thus the degenerate case of the Paxos Commit algorithm with a single acceptor." (lines ~678–680.)

11. **Spanner runs 2PC over Paxos groups.** VERIFIED. "Running two-phase commit over Paxos" (cached `spanner.txt`
    line ~334).

12. **Spanner read-write txns use two-phase locking.** VERIFIED. "Transactional reads and writes use two-phase
    locking." (`spanner.txt` line ~556.)

13. **Spanner read-only txns get snapshot-isolation performance, lock-free.** VERIFIED. "A read-only transaction ...
    has the performance benefits of snapshot isolation." (`spanner.txt` line ~512); reads "can proceed on any [replica
    sufficiently up-to-date]" (lines ~515–526).

14. **Commit wait makes it externally consistent.** VERIFIED (cluster-3 carry-forward, re-confirmed). "Commit Wait The
    coordinator leader ensures that ... TT.after(si) is true." (`spanner.txt` lines ~601–609.)

---

## `[UNVERIFIED]` claims — flagged, NOT verified this session (network-blocked)

- **CAP theorem statement + Gilbert/Lynch proof** (brief §1.1, §1.2): Gilbert/Lynch 2002 and Brewer PODC 2000 could
  not be fetched. The brief states the standard result and explicitly marks the exact model/availability
  definition/proof construction `[UNVERIFIED from fetched source]`. Acceptable for a Phase-1 brief; MUST be confirmed
  before Phase 2 prose.
- **Brewer "CAP Twelve Years Later"** (brief §1.3): partition-mode, recovery strategy, and latency-partition link are
  the standard summary but `[UNVERIFIED from fetched source]`.
- **Abadi PACELC** (brief §1.4): definition and PA/EL · PC/EC · PC/EL classifications are standard but `[UNVERIFIED
  from fetched source]`.
- **Skeen 1981 original 3PC pre-commit state machine** (brief §1.7, §6): not fetched; the brief relies on Gray &
  Lamport's critique rather than Skeen's primary.
- **Herlihy/Wing linearizability, Dynamo** (brief §1.2, §6): carried forward from clusters 2/3, still blocked.

All of the above are honestly flagged in the brief's §6 and §2 "Blocked/unverified" list. None hardened into
unattributed assertions.

---

## Citation-precision warnings (patched / acknowledged)

- **W1 — Gray & Lamport pagination.** Claims cite the 37-page tech-report PDF on lamport.azurewebsites.net, not the
  published ACM TODS 2006 (vol. 31, no. 1) pagination. Already logged in brief §6; re-pin before Phase 2 if exact
  ACM citations are required. No content change needed.
- **W2 — ANSI isolation formalism missing.** The isolation-level discussion (brief §1.8) is anchored only to Spanner's
  2PL/snapshot-isolation wording, not to the ANSI/Berenson "A Critique of ANSI SQL Isolation Levels" definitions.
  Already logged in brief §6 as a pre-Phase-2 source gap. No false claim present; the brief does not define dirty
  read / write skew / phantom from an unverified source.

---

## UPGRADE 2026-06-10 (Wave 9 — CAP primaries unblocked via sub-course 20 fetch)

During sub-course 20 work the network healed for two CAP primaries. Fetched + verified to
`meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_resilience.md`). Nothing below is erased;
these carry-forward `[UNVERIFIED]` flags are UPGRADED:
- **Brewer, "Towards Robust Distributed Systems," PODC 2000 keynote** (`brewer-podc-2000.{pdf,txt}`,
  HTTP 200). VERIFIED verbatim: "at most two of these properties" over {Consistency, Availability,
  Partitions}; the three explicit strategies "Forfeit Partitions / Forfeit Availability / Forfeit
  Consistency"; and BASE = "**B**asically **A**vailable, soft state, **E**ventual consistency" as
  the availability-first dual of ACID. This confirms brief §1.1 and §1.3 (the original conjecture +
  the partition-mode framing). The brief's §1.1 carry-forward `[UNVERIFIED from fetched source]` on
  Brewer PODC 2000 is now VERIFIED.
- **Kleppmann, "Please stop calling databases CP or AP" (2015)** (`kleppmann-cap-2015.{html,txt}`,
  HTTP 200). VERIFIED: CAP is a *narrow* formal result (Gilbert/Lynch linearizability + total
  availability + arbitrary partitions) and a poor general design taxonomy; a partition is a fault
  you do not get to choose. Confirms brief §1.2 ("C" = linearizability; weaker models dodge it) and
  the §1.3 "2-of-3 is the misconception" framing.
- **STILL blocked:** Gilbert & Lynch SIGACT News 2002 (the formal proof) and Abadi 2012 PACELC —
  remain `[UNVERIFIED]`, carried forward. The CAP *statement* and partition-mode framing are now
  primary-anchored via Brewer + Kleppmann; only the formal proof construction (Gilbert/Lynch) and
  the PACELC extension (Abadi) are still pending.

## UPGRADE 2026-06-10 (Wave 10) — Gilbert-Lynch formal CAP + Abadi PACELC UNBLOCKED

Both long-blocked primaries returned HTTP 200 this session and were fetched + text-extracted +
verified verbatim to `meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_cap-pacelc.md`).
Carry-forward `[UNVERIFIED]` -> VERIFIED; nothing above erased.
- **Gilbert & Lynch, "Perspectives on the CAP Theorem" (2012)** (`gilbert-lynch-2002.{pdf,txt}`,
  from groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf). VERIFIED: the CAP theorem is the
  formalized impossibility of guaranteeing both **safety (consistency)** and **liveness
  (availability)** in an unreliable (partitionable) asynchronous system; the service is modeled as
  an **atomic / linearizable** read/write register; the proof turns on a process being unable to
  distinguish a lost message from a slow one during a partition ("cannot determine whether to
  return"); and **CAP ⇒ you cannot achieve consensus in a system subject to partitions** (ties to
  FLP). This is the 2012 retrospective that restates & situates the 2002 SIGACT News formalization
  (its ref [16]); the load-bearing proof statement is now primary-anchored. (The original 2002
  SIGACT News PDF specifically remains separately unfetched — noted, non-blocking.)
- **Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design" / PACELC (2012)**
  (`abadi-pacelc-2012.{pdf,txt}`, from cs.umd.edu/~abadi/papers/abadi-pacelc.pdf). VERIFIED
  verbatim (L476-510): "rewriting CAP as PACELC (pronounced 'pass-elk'): if there is a **partition
  (P)**, how does the system trade off **availability and consistency (A and C)**; **else (E)**,
  when running normally in the absence of partitions, how does the system [trade off **latency (L)
  and consistency (C)**]." Worked classifications: Dynamo/Cassandra/Riak = **PA/EL**; ACID stores
  (VoltDB/H-Store, BigTable/HBase) = **PC/EC**; PNUTS = **PC/EL**. Brief §1.4 carry-forward
  `[UNVERIFIED]` is now VERIFIED.

---

## Verdict

Cluster 4 brief is **accepted as a Phase-1 research brief.** All distributed-commit load-bearing claims (2PC, its
blocking failure, 3PC critique, Paxos Commit, the `2F + 1`/`F + 1`/`F = 0` relationships, and the Spanner
commit×replication×isolation intersection) are verified against primary text with line receipts. CAP/PACELC claims are
correctly state-and-flag-as-unverified pending the blocked primaries. No blockers; two citation-precision warnings,
both already logged as residual gaps.
