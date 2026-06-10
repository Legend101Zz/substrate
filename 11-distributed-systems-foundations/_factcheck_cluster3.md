# Factcheck — Sub-course 11, cluster 3 (consistency, replication, quorums, Paxos/Raft bridge)
## Factchecker: brain manual primary-source pass | Date: 2026-06-10
## Target brief: `11-distributed-systems-foundations/_research_consistency-replication-quorums.md`

Method: load-bearing claims checked against text extracted from primary PDFs in `/tmp/substrate-11-sources`
(`pypdf` via throwaway `uv run`; `/Users/m0t0hu6/.code-puppy-venv` untouched). Line numbers refer to the extracted
`.txt` files. Blocked sources (Herlihy/Wing, Dynamo, MIT notes) were already marked `[UNVERIFIED from fetched source]`
in the brief and are not counted as blockers — they are honest gaps, not false claims.

Verdict: **CLEARED for cluster checkpoint. 0 blockers, 2 citation-precision warnings (patched).**

---

## Verified claims (primary text confirmed)

| # | Claim in brief | Source | Receipt |
|---|----------------|--------|---------|
| V1 | Sequential consistency = result as if all processors' ops ran in some sequential order, each processor's ops in program order | Lamport IEEE TC 1979 | `lamport-multiprocessor.txt` L78–82: "the result of any execution is the same as if the operations of all the processors were executed in some sequential order… called sequentially consistent" |
| V2 | External consistency ≡ linearizability; if T1 commits before T2 starts, T1's commit timestamp < T2's | Spanner OSDI 2012 | `spanner.txt` L98–101: "satisﬁes external consistency (or equivalently, linearizability): if a transaction T1 commits before another transaction T2 starts, then T1's commit timestamp is smaller than T2's" |
| V3 | Bigtable only supports eventually-consistent replication across datacenters (eventual-consistency contrast) | Spanner OSDI 2012 | `spanner.txt` L319: "supports eventually-consistent replication across datacenters" |
| V4 | Raft: majority votes → leader; AppendEntries replicates; entry committed once leader replicates on a majority; Log Matching; Leader Completeness | Raft ATC 2014 | `raft-usenix.txt` L420 (majority→leader), L525 (AppendEntries replicate), L637–638 ("committed once the leader that created the entry has replicated it on a majority"), L447–455 (Election Safety / Log Matching / Leader Completeness) |
| V5 | Quorum safety rests on majority intersection ("any two majorities have at least one acceptor in common") | Paxos Made Simple | `paxos-simple.txt` L80–81: "Because any two majorities have at least one acceptor in common" |
| V6 | Value chosen when accepted by a majority of acceptors | Paxos Made Simple | `paxos-simple.txt` L105–106: "A value is chosen when a single proposal with that value has been accepted by a majority of the acceptors" |
| V7 | Customary asynchronous, non-Byzantine model | Paxos Made Simple | `paxos-simple.txt` L59: "We use the customary asynchronous, non-Byzantine model" |
| V8 | Safety: only proposed values may be chosen; only one value chosen; learners never learn unless actually chosen | Paxos Made Simple | `paxos-simple.txt` L47–50 |
| V9 | Progress needs a distinguished proposer; ensuring progress needs randomness or real time (e.g. timeouts); cites FLP | Paxos Made Simple | `paxos-simple.txt` L282–293: "a distinguished proposer must be selected… The famous result of Fischer, Lynch, and Pat[terson]… either randomness or real time—for example, by using timeouts" |
| V10 | Spanner: single Paxos state machine per tablet; writes initiate Paxos at leader; reads from any replica sufficiently up-to-date; replicas form a Paxos group | Spanner OSDI 2012 | `spanner.txt` L186–209 |
| V11 | Spanner long-lived leaders with time-based leader leases defaulting to 10 seconds; lease via quorum of lease votes | Spanner OSDI 2012 | `spanner.txt` L193–194, L534–537 |
| V12 | Spanner runs two-phase commit over Paxos; commit wait holds visibility until `TT.after(s)`/`TT.after(si)` | Spanner OSDI 2012 | `spanner.txt` L334 (2PC over Paxos), L600–603 (Commit Wait ensures si < absolute commit time), L731 (obey commit-wait rule) |
| V13 | Raft is a replicated-state-machine protocol: leader accepts client log entries, replicates, tells servers when safe to apply | Raft ATC 2014 | `raft-usenix.txt` L315–331 |

---

## Warnings (patched, non-blocking)

- **W1 — citation line drift (Paxos progress).** Brief originally cited "252–265" for distinguished-proposer/progress;
  actual location is `paxos-simple.txt` L282–293. The L252–265 region is the learner-reliability discussion. The claim
  itself is correct; only the line pointer was wrong. **Patched** to 282–293.
- **W2 — citation line drift (Spanner commit wait + Paxos majority/chosen).** Brief cited "730–740 for commit wait" and
  rough Paxos line ranges. Tightened to the exact receipt lines (`spanner.txt` L603/L731; `paxos-simple.txt`
  L79–82, L104–107). Claims unchanged. **Patched.**

---

## Carry-forward gaps (honest; do not erase)

- **Herlihy/Wing linearizability (TOPLAS 1990) not fetched** — object-level definition, locality, nonblocking property
  remain `[UNVERIFIED from fetched source]`. Brief leans on Spanner's verified transaction-level external-consistency
  wording in the meantime. Fetch before Phase 2 prose.
- **Dynamo (SOSP 2007) not fetched** — eventual consistency, sloppy quorum, hinted handoff, N/R/W, version-vector
  reconciliation remain `[UNVERIFIED from fetched source]`. Same gap already logged in the vector-clocks cluster.
- **MIT 6.5840 linearizability notes not fetched** — supporting context only; not cited as primary.
- **Raft membership changes, log compaction/snapshots, and linearizable read-lease optimizations** not covered by this
  cluster (ATC paper core only).
- **CAP/PACELC and distributed commit (2PC/3PC blocking, isolation levels)** not yet a dedicated cluster — referenced
  but not covered. 11 should not be reconciled into `_research.md` until at least one of CAP/partitions or
  distributed-commit is its own clean cluster, unless the project explicitly accepts these as Phase 2 carry-forward.

Network note: this harness reset connections to ACM, Brown, CMU, Cornell, Princeton, UW, MIT pdos, and
allthingsdistributed. Lamport's site, USENIX, and Google research static hosting were reachable.
