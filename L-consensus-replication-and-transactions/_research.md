# Appendix L · consensus-replication-and-transactions — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). L is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for the "how do independent
> machines agree, stay in sync, and commit atomically" theory the spine leans on (07/11/14/15) and
> the canon papers instantiate. Bespoke structure: a **fault-model ladder** (crash → Byzantine →
> quorum → CAP/PACELC → atomic-commit → isolation), NOT four clusters and NOT a build progression.
> Math: `_recompute.py` (22/22). Factcheck: `_factcheck_phase1.md` (0 blockers).
> **NEW primaries fetched+verified this session**: Lamport Paxos + Byzantine Generals (receipt
> `meta/fetched_primaries/_VERIFIED_2026-06-11_consensus.md`).

## 1. Thesis
Consensus, replication, and transactions are **three faces of one problem**: getting independent,
unreliable machines to behave like one reliable machine. The fault model you assume (crash vs lying
vs partition) and the consistency you demand set an unavoidable PRICE — in nodes, rounds, latency, or
availability. This appendix derives each price first-principles.

## 2. The fault-model ladder (the bespoke spine)

### Tier 1 — Crash-fault consensus: `n ≥ 2f+1` (Paxos / Raft)
- To tolerate `f` crash failures and still decide, you need a **majority quorum** of `n = 2f+1`. Two
  majorities of `n` always intersect (`2·⌈(n+1)/2⌉ − n ≥ 1`) ⇒ **no split-brain** — the safety core.
- **Paxos** (Lamport, "The Part-Time Parliament," `lamport-paxos.txt`): a ballot succeeds iff every
  member of its **quorum** votes; progress needs a **majority** (verbatim, lines 108/131/189–193).
  Implements the **state-machine approach** — all replicas apply the same command log → same state
  (line 18, "State machines, … voting"). Raft is the same guarantees with an understandable
  leader-based exposition (raft.github.io still blocked → `[UNVERIFIED]`, carried).
- RECOMPUTED: f=1/2/3 ⇒ n=3/5/7; alive `n−f` ≥ majority every time. (`_recompute.py`)

### Tier 2 — Byzantine-fault consensus: `n ≥ 3f+1` (the price of lying)
- If nodes can lie/equivocate (not just crash), you need **more than two-thirds loyal**: `n = 3f+1`.
- **Byzantine Generals** (Lamport, Shostak, Pease, `lamport-byz.txt`): "solvable iff more than
  two-thirds of the generals are loyal" (line 10); "no solution with fewer than 3m+1 generals"
  (line 156); "to cope with m traitors there must be at least 3m+1 generals" (lines 234–235) — all
  verbatim.
- RECOMPUTED: f=1/2/3 ⇒ n=4/7/10, loyal fraction 0.75/0.714/0.700 (all > 2/3). BFT costs **~50% more
  nodes** than crash-fault for the same f (7 vs 5 at f=2) — why most systems assume crash-only.

### Tier 3 — Quorum replication: `W+R>N` (Dynamo; 15)
- Sloppy/Dynamo-style replication makes quorums **tunable**. `W+R>N` ⇒ the read set intersects the
  write set ⇒ a read sees the latest write (strong-ish). `W>N/2` ⇒ no two writes diverge.
- RECOMPUTED: (N,W,R)=(3,2,2)/(5,3,3)/(3,3,1)/(3,1,3) all give overlap ≥1; **(3,2,1) gives overlap 0
  → can read stale** (the eventual-consistency window). Write quorum tolerates `N−W` failures (tune W
  down for availability). More read replicas cut stale-read prob `1−s^R` (read-repair logic).
- Anchored to Dynamo (`dynamo-sosp2007`, local+VERIFIED): `R+W>N` verbatim, sloppy quorum, hinted
  handoff, Merkle anti-entropy, vector clocks — reuse 15/14/11/06.

### Tier 4 — CAP / PACELC: partition forces the choice
- **CAP** (Gilbert & Lynch 2002, `gilbert-lynch-2002` local+VERIFIED; Brewer PODC 2000): during a
  partition, the minority side **must forfeit C or A** — it cannot both answer and stay consistent.
  RECOMPUTED as a quorum-reachability decision: majority side keeps C&A, minority drops one.
- **PACELC** (Abadi 2012, `abadi-pacelc-2012` local+VERIFIED): **Else** (no partition) you still
  trade **Latency vs Consistency** — synchronous cross-region commit pays ≥1 RTT. Consistency is
  never free, partition or not.

### Tier 5 — Atomic commit: 2PC blocks; consensus-commit doesn't
- **2PC** over n participants ≈ `4n` messages (prepare/vote/commit/ack). Fatal flaw: if the
  coordinator dies between prepare and commit, participants **block** holding locks.
- Fix: replicate the commit decision through consensus (Paxos/Raft). **Spanner** (`spanner-osdi2012`
  local+VERIFIED) makes each participant a Paxos group and the coordinator's decision fault-tolerant.
- **Spanner TrueTime**: exposes clock uncertainty ε (paper: ε ≈ **1 to 7 ms**, generally <10 ms,
  line 448/105). **Commit-wait** (lines 580–588) waits out the uncertainty (~2ε model, illustrative)
  so timestamp intervals don't overlap ⇒ **external consistency** (linearizable commits) across the
  globe. RECOMPUTED: ε=7 ⇒ wait ~14 ms.

### Tier 6 — Isolation & serializability (07)
- Serializable execution = some serial order. Concurrent txns on a hot key create `C(n,2)` conflict
  pairs (8 txns ⇒ 28) → lock/abort cost. Under 2PL, throughput on ONE contended key ≈ `1/hold_time`
  (5 ms hold ⇒ **200 txn/s max** — the contention wall). Snapshot isolation, MVCC, and the anomaly
  ladder (dirty/non-repeatable/phantom/write-skew) live deep in 07; L cross-links DOWN to them.

## 3. The "one problem, three faces" reconciliation (appendix payload)
| face | mechanism | quorum/price | anchor |
|---|---|---|---|
| **Agree** (consensus) | Paxos/Raft majority log | n≥2f+1 (3f+1 Byzantine) | Lamport Paxos/Byz |
| **Stay in sync** (replication) | leader/quorum replication | W+R>N for fresh reads | Dynamo/15 |
| **Commit atomically** (transactions) | 2PC over a consensus log | 4n msgs; commit-wait 2ε | Spanner/07 |
All three reduce to **"a majority decides, and intersection guarantees safety."** Quorum
intersection is the load-bearing idea the whole appendix turns on.

## 4. Common misconceptions to preempt
- "CAP means pick 2 of 3 always" — no; partitions are rare, so it's really **C-vs-A only during P**,
  and **L-vs-C otherwise** (PACELC). (Kleppmann `kleppmann-cap-2015` local+VERIFIED.)
- "Quorum reads are always fresh" — only if `W+R>N`; `W>N/2` alone allows stale reads.
- "2PC gives you distributed transactions safely" — it gives atomicity but **blocks** on coordinator
  failure; you need consensus underneath (Spanner).
- "Byzantine tolerance is just more replicas" — it's a different bound (3f+1) and different protocol.

## 5. Provenance summary
- **NEW primaries fetched+verified:** Lamport Paxos (`lamport-paxos.txt`) + Byzantine Generals
  (`lamport-byz.txt`) — receipt `_VERIFIED_2026-06-11_consensus.md`. **Upgrades 12's carried
  Byzantine/Paxos `[UNVERIFIED]` → LOCAL+VERIFIED.**
- **REUSED (local+VERIFIED):** Dynamo, Spanner, Bigtable, GFS, Gilbert-Lynch, Brewer, Kleppmann,
  Abadi-PACELC; spine 07/11/14/15.
- **RECOMPUTED:** `_recompute.py` (22/22).
- **`[UNVERIFIED]` carry-forward (not load-bearing):** Raft paper (raft.github.io 000, still
  blocked); FLP impossibility (Fischer-Lynch-Paterson 1985) not fetched; PBFT (Castro-Liskov 1999)
  not fetched; ANSI/Adya isolation formalism (→07); Skeen 3PC; ε exact distribution + commit-wait
  exact formula (modeled, not quoted verbatim). All logged, none hardened.

---
**Appendix L reconciled.** Reference-grade, exercise-free, 22/22 recomputed, two new Lamport
primaries verified. No chapters yet.
