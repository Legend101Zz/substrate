# 15 — Factcheck (Phase 1) — clusters A/B/C/D

> Factchecker pass over the load-bearing claims of sub-course 15
> (replication-and-consistency-in-practice). Method: **recompute all math independently** (pure
> Python, no deps); **verify mechanisms by reuse** of earlier line-checked sub-courses (06/07/11/
> 13/14) with per-claim pointers; **flag every unfetched primary** `[UNVERIFIED from fetched
> source]`. Network reality (7th consecutive session): only `lamport.azurewebsites.net` resolves
> (HTTP 200); `arxiv.org`, `raw.githubusercontent.com`, `allthingsdistributed.com`,
> `research.google`, `postgresql.org`, `raft.github.io` all HTTP 000. No new primary fetchable.
> **Result: 0 blockers.** All load-bearing math recomputed clean; all mechanisms trace to verified
> canon; the only open items are canonical/vendor *attributions*, all uniformly network-blocked and
> carried forward (not laundered).

---

## A. Math verified by recomputation (this session)

Script: exhaustive enumeration of all (W-set, R-set) quorum pairs over N nodes + a stale-read
probability model + majority-quorum failure tolerance. Receipts:

### A1. Quorum overlap: `W+R>N ⇔ guaranteed overlap` (exhaustive)
| N | W | R | W+R vs N | min overlap over ALL pairs | guaranteed overlap |
|---|---|---|----------|----------------------------|--------------------|
| 3 | 2 | 2 | 4 > 3 | 1 | **True** |
| 3 | 3 | 1 | 4 > 3 | 1 | **True** |
| 5 | 3 | 3 | 6 > 5 | 1 | **True** |
| 5 | 1 | 5 | 6 > 5 | 1 | **True** |
| 3 | 1 | 1 | 2 ≤ 3 | 0 | False |
| 3 | 2 | 1 | 3 ≤ 3 | 0 | False |
| 5 | 2 | 3 | 5 ≤ 5 | 0 | False |
**Verdict:** overlap is guaranteed **iff** `W+R>N`. Note `W+R=N` (e.g. 3,2,1 and 5,2,3) is NOT
sufficient — strict `>` is required. Used in Cluster C §1.5 (correct) and Cluster A §1.3/§1.4 (W as
ack threshold). 

### A2. Stale-read probability (illustrative model)
P(a uniform R-read misses the W freshest replicas), immediately after a write reached exactly W:
| N | W | R | P(read sees latest) | P(stale) |
|---|---|---|---------------------|----------|
| 3 | 1 | 1 | 1/3 ≈ 0.333 | 0.667 |
| 3 | 2 | 1 | 2/3 ≈ 0.667 | 0.333 |
| 3 | 1 | 2 | 2/3 ≈ 0.667 | 0.333 |
| 3 | 2 | 2 | 1 | 0.000 |
| 5 | 1 | 1 | 1/5 = 0.200 | 0.800 |
| 5 | 3 | 3 | 1 | 0.000 |
**Verdict:** P(stale)=0 **iff** W+R>N; the 2/3 and 0.8 figures cited in Cluster C §1.5 table are
correct. 

### A3. Majority-quorum failure tolerance
W=R=⌊N/2⌋+1 ⇒ tolerates `N − (⌊N/2⌋+1) = ⌊(N−1)/2⌋` failures while still W+R>N:
| N | majority q | W+R | tolerated failures |
|---|------------|-----|--------------------|
| 3 | 2 | 4 > 3 | 1 |
| 4 | 3 | 6 > 4 | 1 |
| 5 | 3 | 6 > 5 | 2 |
| 6 | 4 | 8 > 6 | 2 |
| 7 | 4 | 8 > 7 | 3 |
**Verdict:** matches Cluster C §1.5 (N∈{3,5,7}→{1,2,3}); odd N is more failure-efficient (even N
buys no extra tolerance over N−1). Same majority-intersection object as 11 §1.5 consensus quorum. 

### A4. Async durability window (structural, no number claimed)
Cluster A §1.3 / D §1.4 claim only that acked-but-unreplicated writes are lost on leader failure.
This is structural (a consequence of acking before replicating), not a numeric claim. No false
precision introduced. 

---

## B. Mechanisms verified by reuse (per-claim pointers; NOT re-fetched)

| # | Claim (cluster) | Verified via | Status |
|---|-----------------|--------------|--------|
| B1 | Leader = ordering device ⇒ single-leader has no write conflicts (A §1.2, C §1.1) | 11 §1.5 (Paxos Made Simple, line-verified) |  reuse |
| B2 | Quorum = majority intersection / pigeonhole (C §1.5, D §1.3) | 11 §1.5 (verified) |  reuse |
| B3 | Version vectors detect concurrency: incomparable ⇔ concurrent (B §1.4, C §1.2) | 11 §1.2 (Lamport scalar limitation verified; VV primary `[UNVERIFIED]`) |  mechanism /  attribution |
| B4 | Wall clocks can't order distributed events without bounds (C §1.2) | 11 §1.1 (Lamport 1978, verified) |  reuse |
| B5 | Eventual consistency converges if writes stop + links heal (B §1.1, C §1.1) | 11 §1.4 (verified framing) |  reuse |
| B6 | FLP: dead vs slow indistinguishable ⇒ detection is a guess (D §1.1) | 11 §1.3 (FLP/JACM 1985, verified) |  reuse |
| B7 | Raft majority-vote election ⇒ two leaders can't win; `term` as epoch (D §1.1, §1.3) | 11 §1.5 (Raft, verified) |  reuse |
| B8 | Minority side can't reach quorum ⇒ split-brain-safe (D §1.3) | 11 §1.5 (verified) |  reuse |
| B9 | CAP = C-vs-A during partition; PACELC = latency tax when healthy (D §1.6) | 11 §1.6 (Gilbert-Lynch/Brewer/Abadi `[UNVERIFIED]`) |  attribution |
| B10 | Spanner = Paxos/shard + 2PC-over-Paxos + TrueTime ⇒ external consistency (D §1.5) | 11 §1.8 (Spanner OSDI 2012, verified) |  reuse |
| B11 | Physical log ships the WAL the engine already writes (A §1.4) | 07 storage/WAL + 06 B-tree pages (verified there) |  reuse |
| B12 | Merkle tree diffs replicas in O(log n) hashes (C §1.4) | 06 hashing/tree intuition (verified) |  reuse |
| B13 | Replication ≠ partitioning; denormalization owes a write-side consistency tax landing here (A §1.1, D §1.6) | 14 `_research.md` (verified by recomputation/reuse) |  reuse |
| B14 | Fan-out / lag-window framing (B §1.1) consistent with tail math | 13 `_factcheck_clusterA.md` (verified) |  reuse |

---

## C. Attribution flags — `[UNVERIFIED from fetched source]` (carry forward, do NOT erase)

All are *citations/exact-wording/vendor-specifics*, none load-bearing for the verified method/math:
- **DDIA ch.5 (replication), ch.8 (fencing), ch.9** — Kleppmann; the taxonomy + anomaly exposition
  + fencing-token example.
- **Dynamo, SOSP 2007** — leaderless quorum N/R/W, sloppy quorum, hinted handoff, Merkle anti-
  entropy, read-repair, version-vector siblings (master primary for Clusters C & the leaderless
  parts of A/D). Also carried in 11/14.
- **Terry et al., "Session Guarantees..." (Bayou), PDIS 1994** — read-your-writes / monotonic-reads
  / monotonic-writes / writes-follow-reads naming (Cluster B).
- **Shapiro et al., CRDTs, INRIA RR-7506 / SSS 2011** — CvRDT/CmRDT, semilattice convergence
  (Cluster C).
- **CAP/PACELC primaries** — Gilbert/Lynch 2002, Brewer 2000/2012, Abadi 2012 (carried from 11).
- **Vendor docs** — PostgreSQL (streaming/physical repl, `synchronous_commit` levels, logical
  decoding/`pgoutput`), MySQL (binlog STATEMENT/ROW/MIXED, semi-sync, GTID, Group Replication),
  MongoDB (replica sets, oplog, write concern), Cassandra (LWW default, tunable consistency, hinted
  handoff, read repair), Riak (siblings, dotted version vectors, CRDT types), etcd/CockroachDB/
  Consul/TiKV (Raft groups/ranges/leases), ZooKeeper/Chubby (Zab/`zxid`/leases), Patroni,
  Pacemaker/STONITH.

**Patches applied this session:** none required — no first-draft numeric error survived
recomputation (the W+R=N-is-insufficient subtlety was caught and stated explicitly in A1, and the
Cluster C table uses strict `>` correctly). The async durability claim was kept structural to avoid
false precision.

**Verdict: 0 blockers.** 15's load-bearing content — the *method + mathematics* of replicating data,
paying the lag/consistency tax, resolving conflicts, tuning quorums, and surviving leader failure —
is verified end-to-end by recomputation + reuse. Remaining items are network-blocked attributions
carried forward; none may harden into Phase-2 prose until fetched.

---

## UPGRADE 2026-06-10 (network heal — Dynamo + Spanner FETCHED + VERIFIED)

The 18-session network heal made `allthingsdistributed.com` + `research.google` mirrors
reachable. Fetched + extracted to `meta/fetched_primaries/` (see `_VERIFIED_2026-06-10_canon.md`):

- **Dynamo (DeCandia et al., SOSP 2007)** — `dynamo-sosp2007.{pdf,txt}`. **VERIFIED verbatim:**
  "Setting R and W such that **R + W > N** yields a quorum-like system… latency dictated by the
  slowest of the R (or W) replicas." Confirms the quorum-overlap claim previously verified only
  by recomputation. Terms present + verified: consistent hashing, virtual nodes, vector clocks,
  **sloppy quorum, hinted handoff, Merkle anti-entropy, read repair**, gossip. → Clears the
  carried-forward 15 `[UNVERIFIED]` for Dynamo (leaderless quorum, sloppy quorum, hinted handoff,
  Merkle, read repair, sibling version vectors).
- **Spanner (Corbett et al., OSDI 2012)** — `spanner-osdi2012.{pdf,txt}`. **VERIFIED (terms):**
  TrueTime, commit wait, Paxos, external consistency, uncertainty interval, `TT.now()`. → Clears
  the carried-forward 15/14/11 `[UNVERIFIED]` for the Spanner externally-consistent topology.

**Still `[UNVERIFIED]` (carried forward):** Kleppmann DDIA ch.5/8/9; Terry et al. Bayou session
guarantees PDIS 1994; Shapiro et al. CRDTs; CAP/PACELC primaries (Gilbert-Lynch/Brewer/Abadi);
all vendor docs (Postgres/MySQL/Mongo/Cassandra/Riak/etcd/CockroachDB/ZooKeeper).

## UPGRADE 2026-06-10 (Wave 9 — CAP primaries unblocked via sub-course 20 fetch)

Network healed for two CAP primaries during 20 work; fetched + verified to
`meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_resilience.md`). Nothing erased:
- **Brewer PODC 2000 keynote** (`brewer-podc-2000.{pdf,txt}`): VERIFIED "at most two" of
  {C,A,P}; Forfeit C/A/P; BASE = Basically Available, Soft state, Eventual consistency. Confirms
  15 Cluster D's CAP-made-concrete framing (failover forfeits A via fencing to keep C).
- **Kleppmann "Please stop calling databases CP or AP" (2015)** (`kleppmann-cap-2015.{html,txt}`):
  VERIFIED — CAP is a narrow theorem, a poor general taxonomy; a partition is an unchosen fault.
- The CAP `[UNVERIFIED]` in 15 is now **partially upgraded** (statement + partition-mode framing
  primary-anchored via Brewer + Kleppmann); **Gilbert-Lynch 2002 formal proof and Abadi 2012
  PACELC remain blocked / carried forward.** PACELC itself is unchanged-pending.

## UPGRADE 2026-06-10 (Wave 10) — Gilbert-Lynch formal CAP + Abadi PACELC UNBLOCKED

Both returned HTTP 200 this session; fetched + verified verbatim to `meta/fetched_primaries/`
(receipt `_VERIFIED_2026-06-10_cap-pacelc.md`). Carry-forward `[UNVERIFIED]` -> VERIFIED; nothing
above erased.
- **Gilbert & Lynch "Perspectives on the CAP Theorem" (2012)** (`gilbert-lynch-2002.{pdf,txt}`):
  VERIFIED — formal CAP = cannot guarantee both safety(C) + liveness(A) in a partitionable async
  system, modeled as an atomic/linearizable register; CAP ⇒ no consensus under partition. Anchors
  15 Cluster D's "failover forfeits A to keep C under partition" (claim B9).
- **Abadi PACELC (2012)** (`abadi-pacelc-2012.{pdf,txt}`): VERIFIED verbatim — "if Partition (P):
  trade A vs C; **else (E)**: trade **Latency (L) vs Consistency (C)**." PA/EL (Dynamo/Cassandra/
  Riak) vs PC/EC (ACID) vs PC/EL (PNUTS). Anchors claim B9's "PACELC = latency tax when healthy";
  the carry-forward PACELC `[UNVERIFIED]` in 15 is now VERIFIED. (Synchronous-quorum replication is
  the PC/EC latency tax; tunable async quorums are the PA/EL choice — 15 Cluster C/D made concrete.)
