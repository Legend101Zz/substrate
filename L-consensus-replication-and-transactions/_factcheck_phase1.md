# Appendix L · Phase-1 factcheck — consensus-replication-and-transactions

> Method (spine discipline): every load-bearing claim is (a) RECOMPUTED in `_recompute.py` (22/22) or
> (b) VERIFIED verbatim against a local primary. L is a **reference appendix** (no exercises). **0
> blockers.** NEW primaries fetched this session: Lamport Paxos + Byzantine Generals.

## Bespoke structure note
L is a **fault-model ladder** (crash → Byzantine → quorum → CAP/PACELC → atomic-commit → isolation),
NOT the 13-20 four-cluster shape and NOT a build progression. Appendix-appropriate (reference-grade).

## Primaries verified verbatim (receipt `meta/fetched_primaries/_VERIFIED_2026-06-11_consensus.md`)
- **Lamport, Byzantine Generals** (`lamport-byz.txt`): "more than two-thirds of the generals are
  loyal" (line 10); "no solution with fewer than 3m+1 generals" (156); "at least 3m+1 generals"
  (234–235). ⇒ BFT bound **n≥3f+1**. VERIFIED.
- **Lamport, Part-Time Parliament / Paxos** (`lamport-paxos.txt`): "If a majority of the legislators"
  (108); majority footnote (131); "every priest in the quorum voted … Bqrm A nonempty set of priests
  (the ballot's quorum)" (189–193); "State machines, … voting" (18). ⇒ Paxos = majority-quorum +
  state-machine approach. VERIFIED.
- **Spanner** (`spanner-osdi2012.txt`, local+prior): TrueTime exposes uncertainty ε ≈ "1 to 7 ms"
  (448), "<10ms" (105); "Commit Wait The coordinator leader ensures … commit wait ensures …"
  (580–588). VERIFIED (commit-wait 2ε is an illustrative model, flagged).
- **Dynamo / Gilbert-Lynch / Brewer / Kleppmann / Abadi-PACELC**: all local+VERIFIED in prior waves
  (R+W>N; CAP impossibility; PACELC Else L-vs-C). Reused.

## Recomputed claims (`_recompute.py`, 22/22)
- Crash consensus n≥2f+1 survives f (f=1/2/3 → n=3/5/7); majorities always intersect. PASS×4.
- Byzantine n≥3f+1, loyal>2/3 (f=1/2/3 → n=4/7/10); BFT 50% more nodes than CFT. PASS×4.
- Quorum W+R>N overlap (4 configs) + (3,2,1)=0 stale window. PASS×5.
- Write quorum tolerates N−W; stale-read prob 1−s^R. PASS×2.
- CAP minority drops C-or-A; PACELC Else L-vs-C costs RTT. PASS×2.
- 2PC ~4n messages + blocking window; consensus-commit removes it. PASS×2.
- Conflict pairs C(n,2)=28; hot-key throughput 1/hold=200 tps. PASS×2.
- Spanner commit-wait 2ε=14 ms. PASS.

## Reused (line-verified spine + local primaries)
07 (transactions/isolation/MVCC/2PL), 11 (consensus/CAP/distributed commit), 14 (partitioning/
consistent hashing), 15 (replication/quorum/staleness). Local primaries: Dynamo, Spanner, Bigtable,
GFS, Gilbert-Lynch, Brewer, Kleppmann, Abadi-PACELC, + new Lamport Paxos/Byz.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- **Raft** original paper (Ongaro-Ousterhout 2014) — raft.github.io HTTP 000, still blocked (retried
  this session). Claims about Raft stated as "same guarantees as Paxos, leader-based" only.
- **FLP impossibility** (Fischer, Lynch, Paterson 1985) — not fetched.
- **PBFT** (Castro & Liskov 1999) — not fetched (BFT protocol details beyond the 3f+1 bound).
- **Skeen 3PC**, ANSI/Adya isolation formalism (→ home in 07), exact TrueTime ε distribution +
  commit-wait formula (modeled as 2ε, not quoted). All logged, none load-bearing.

## Verdict
L is honest and appendix-appropriate: the consensus core (Paxos majority, Byzantine 3f+1) is now
VERIFIED against freshly-fetched Lamport primaries; replication/CAP/commit math is recomputed and
anchored to local Dynamo/Spanner/Gilbert-Lynch/Abadi. Reconcile into `_research.md`. **0 blockers.**
