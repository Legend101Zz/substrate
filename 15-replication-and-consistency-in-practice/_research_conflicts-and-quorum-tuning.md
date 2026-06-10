# 15 · Cluster C — Conflict handling & quorum tuning (W+R>N)

> **Phase 1 brief (NO course prose).** Standard six sections. Cluster C of sub-course 15. When more
> than one node accepts writes (multi-leader / leaderless, Cluster A §1.2), two writes can be
> *concurrent* (no happened-before either way, 11 §1.1) → a **conflict** that must be detected and
> resolved. This cluster covers detection (version vectors), resolution policies (LWW / VV / CRDT),
> the background repair machinery (read-repair / anti-entropy / hinted handoff), and the quorum dial
> (W+R>N) that tunes the freshness/availability trade. All load-bearing **math is verified by
> recomputation this session** (`_factcheck_phase1.md`). Reuses 11 (quorum = majority intersection,
> version vectors, eventual consistency) + 14 (denormalization conflict surface). Unfetched
> primaries `[UNVERIFIED from fetched source]` (network: only `lamport.azurewebsites.net`, 7th).

## 1. Key mechanisms

### 1.1 What a conflict *is*
A conflict is two writes to the same key that are **concurrent** — neither happened-before the other
(11 §1.1). Single-leader has none (the leader totally orders writes, A §1.2). Multi-leader and
leaderless have them structurally, so they need (a) **detection** and (b) a **resolution policy**
that is *deterministic across replicas* (every replica must converge to the same winner, or you get
permanent divergence). Convergence-to-the-same-value is the correctness bar (the "C" in CRDT, and
the goal of read-repair/anti-entropy in §1.4).

### 1.2 Detection — version vectors beat wall clocks
- **Wall-clock timestamps can't detect concurrency** — clock skew makes a *causally later* write
  look earlier (11 §1.1: only causally-related events have a real order; clocks need bounds).
- **Version vectors / vector clocks** (reuse 11 §1.2: `VC(a)<VC(b) ⇔ a→b`, incomparable ⇔
  concurrent) detect exactly which writes are concurrent → the system can surface **siblings**
  (multiple concurrent values) instead of silently dropping one. Dynamo/Riak return siblings to the
  app; the app or a CRDT merges them. *(Dynamo version vectors `[UNVERIFIED]`; the VC math verified
  in 11.)*

### 1.3 Resolution policies (the trade: simplicity vs correctness)
- **Last-Write-Wins (LWW).** Pick the write with the highest timestamp; discard the rest. Trivially
  convergent and stateless, but **silently loses data** under concurrency + clock skew (the loser's
  write is gone forever). Cassandra's default; correct *only* if writes to a key are never truly
  concurrent or loss is acceptable. *(Cassandra LWW `[UNVERIFIED]`.)*
- **Version vectors + app merge.** Keep all siblings, hand them to the app to merge with domain
  logic (e.g. union two shopping carts → never lose an added item; Dynamo's canonical example).
  No data loss, but the app must write merge code. *(Dynamo `[UNVERIFIED]`.)*
- **CRDTs (Conflict-free Replicated Data Types).** Data types whose merge is **commutative,
  associative, and idempotent**, so concurrent replicas *always* converge with no coordination and
  no lost updates, *by construction*. Two families: **state-based (CvRDT)** ship merged state via a
  join over a semilattice; **op-based (CmRDT)** ship commutative ops. Examples: G-Counter/PN-Counter,
  OR-Set, LWW-Register, RGA/sequence (collaborative text). The merge being a semilattice join is why
  order/duplication/retries don't matter — exactly the property anti-entropy needs. *(Shapiro,
  Preguiça, Baquero, Zawirski, "A Comprehensive Study of CRDTs," INRIA RR-7506, 2011 `[UNVERIFIED]`.)*

The ladder: **LWW (lossy, free) → version vectors + merge (lossless, app work) → CRDT (lossless,
automatic, but you must model your data as a CRDT).**

### 1.4 Background convergence — repair the divergence you allowed
Leaderless systems don't block writes on all replicas, so replicas *will* diverge; three mechanisms
drag them back together:
- **Read-repair** — on a read across R replicas, if one returns a stale value, the coordinator
  writes the fresh value back to it. Cheap, repairs hot/read keys, but cold keys never get read →
  needs anti-entropy too. *(Dynamo `[UNVERIFIED]`.)*
- **Anti-entropy** — a background process compares replicas (efficiently, via **Merkle trees** so
  you diff O(log n) hashes instead of all data — reuse 06 hashing/tree intuition) and copies missing
  updates. Repairs cold keys; the steady-state convergence engine. *(Dynamo Merkle anti-entropy
  `[UNVERIFIED]`.)*
- **Hinted handoff** — if a target replica is down at write time, a *different* node accepts the
  write and holds a "hint"; when the target returns, the hint is delivered. Keeps writes available
  during failures (a **sloppy quorum**: the write goes to N healthy nodes, not necessarily the N
  "home" nodes — which means W+R>N no longer guarantees overlap during the failure). *(Dynamo
  sloppy quorum + hinted handoff `[UNVERIFIED]`.)*

### 1.5 Quorum tuning W+R>N — **verified by recomputation**
Leaderless freshness is a dial, not a leader. Write to W replicas, read from R of N. **The
correctness condition is W+R>N**, and the reason is pigeonhole: any W-set and any R-set must share
at least one node, so a read always touches a node that saw the latest write.

Exhaustive recomputation this session (all quorum pairs over N nodes):
| N | W | R | W+R vs N | guaranteed overlap | P(stale read)\* |
|---|---|---|----------|--------------------|------------------|
| 3 | 2 | 2 | 4 > 3 | **yes** | 0.000 |
| 3 | 3 | 1 | 4 > 3 | **yes** | 0.000 |
| 3 | 1 | 1 | 2 ≤ 3 | no | 0.667 |
| 3 | 2 | 1 | 3 ≤ 3 | no | 0.333 |
| 5 | 3 | 3 | 6 > 5 | **yes** | 0.000 |
| 5 | 2 | 3 | 5 ≤ 5 | no | >0 |
| 5 | 1 | 1 | 2 ≤ 5 | no | 0.800 |

\*P(stale read) = probability a uniformly-random R-read misses the W freshest replicas, immediately
after a write reaches exactly W replicas (illustrative model). It is exactly 0 **iff** W+R>N.

Tuning within W+R>N trades *which operation pays*:
- **W=N, R=1** — fast reads, slow/fragile writes (any replica down blocks the write).
- **W=1, R=N** — fast writes, slow reads; write survives if ≥1 replica up.
- **W=R=⌊N/2⌋+1 (majority)** — balanced; and majority quorums **tolerate ⌊(N−1)/2⌋ node failures**
  while still satisfying W+R>N (verified by recomputation): N=3→1, N=5→2, N=7→3 failures. This is
  the same majority-intersection object as 11's consensus quorum (11 §1.5) — leaderless quorums and
  consensus quorums are the *same pigeonhole*, used for different guarantees (freshness vs a single
  chosen order).

Limits: even with W+R>N, leaderless quorums are **not linearizable** in general (concurrent writes,
read-repair races, sloppy quorums during failures all break it) — W+R>N buys "a read sees *a* recent
write," not "a single global order." For linearizable, you need a leader/consensus (11). *(Dynamo
N/R/W `[UNVERIFIED]`; the intersection + failure-tolerance math verified here.)*

## 2. Foundational sources

**Verified by recomputation this session** (`_factcheck_phase1.md`, pure-Python, no deps):
- `W+R>N ⇔ guaranteed read/write overlap` — exhaustive over all (W-set, R-set) pairs; W+R≤N always
  admits a disjoint pair (min overlap 0).
- Stale-read probability is exactly 0 iff W+R>N; e.g. N=3,W=R=1 → 2/3 stale; N=5,W=R=1 → 0.8 stale.
- Majority quorum W=R=⌊N/2⌋+1 tolerates ⌊(N−1)/2⌋ failures: N∈{3,5,7}→{1,2,3}.

**Verified by reuse (line-checked earlier — NOT re-fetched):**
- Quorum = majority intersection (the same pigeonhole) — 11 §1.5 (Paxos Made Simple, verified).
- Version vectors detect concurrency (`VC` incomparable ⇔ concurrent) — 11 §1.2.
- Eventual consistency converges if writes stop + links heal — 11 §1.4.
- Merkle-tree / hashing intuition for efficient diff — 06 `_research_indexes-lsm-bloom.md` /
  probabilistic structures.
- Concurrent writes only exist with multi-writer topologies — 15 Cluster A §1.2.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carry forward:**
- DeCandia et al., **Dynamo**, SOSP 2007 — N/R/W quorum, sloppy quorum, hinted handoff, Merkle
  anti-entropy, read-repair, version-vector siblings (the master primary for this entire cluster).
- Shapiro et al., **"A Comprehensive Study of CRDTs,"** INRIA RR-7506 (2011) + "Conflict-free
  Replicated Data Types," SSS 2011 — CvRDT/CmRDT, semilattice convergence.
- Cassandra docs — LWW conflict resolution, tunable consistency (`ONE`/`QUORUM`/`ALL`), hinted
  handoff, read repair, Merkle-tree repair.
- Riak docs — siblings, dotted version vectors, CRDT data types ("Riak DataTypes").
- DDIA ch.5 — leaderless replication, quorum math, LWW pitfalls.

## 3. Why it is this way — forcing functions
- **Multi-writer topologies create concurrency by construction** (no single ordering leader) → a
  conflict is the *normal* outcome of two regions writing the same key, not an error.
- **You must resolve deterministically** because replicas that pick different winners diverge
  permanently — convergence is the correctness bar, hence semilattice merges / VV / agreed LWW.
- **LWW exists because it's free and stateless** — and it loses data precisely because it throws
  away everything but the max timestamp under skew.
- **CRDTs exist to make merge associative/commutative/idempotent** so that the messy realities of
  anti-entropy (reorder, duplicate, retry) can't corrupt state — the merge *is* the safety net.
- **W+R>N exists because of pigeonhole** — overlap is the only way a read without a leader can be
  sure it touched the latest write; the dial picks which side pays latency/availability.
- **Read-repair + anti-entropy + hinted handoff exist because leaderless writes don't wait for all
  replicas** — you allow divergence for availability, then repair it in the background.

## 4. Common misconceptions to preempt
- "W+R>N means linearizable." No — it means a read intersects a recent write; concurrent writes,
  read-repair races, and sloppy quorums still break a global order. Linearizable needs consensus (11).
- "Last-write-wins is a safe default." No — it silently *loses* concurrent writes under clock skew;
  safe only if concurrency truly can't happen or loss is acceptable.
- "Timestamps resolve conflicts correctly." Clock skew makes a later write look earlier; only causal
  metadata (version vectors) detects concurrency.
- "CRDTs eliminate all conflicts." They eliminate *merge* conflicts for data modeled as a CRDT; they
  don't remove application-level semantic conflicts and constrain how you model data.
- "Quorum reads always return the newest value." Only with W+R>N *and* no concurrent writes / sloppy
  quorum in play.
- "Sloppy quorum is just a quorum." It writes to N *healthy* nodes (hinted handoff), so during
  failures it does **not** guarantee W+R>N overlap — availability bought with a freshness risk.
- "Bigger N is always safer." It changes the tolerated-failure and latency math; correctness is
  W+R>N, not N alone.

## 5. Best build-your-own target(s)
- **Quorum dial simulator**: N replicas, tunable W/R; inject a write, then random R-reads; confirm
  P(stale)=0 iff W+R>N and reproduce the 2/3 and 0.8 stale rates from the table. (Pairs with 13.)
- **Conflict-resolution bake-off**: same concurrent-write workload under LWW vs version-vectors+merge
  vs a CRDT counter/set; count lost updates (LWW loses, the others don't).
- **CRDT mini-lib**: G-Counter + OR-Set with `merge()`; fuzz with reordered/duplicated deliveries to
  prove convergence (semilattice property).
- **Anti-entropy with Merkle trees**: diff two diverged replicas in O(log n) hashes; add read-repair
  and hinted handoff; kill/restore a node to watch a hint deliver. (Pairs with 06.)

## 6. Open questions / gaps (do NOT erase)
- Dynamo + CRDT + Cassandra/Riak docs are `[UNVERIFIED]` (network HTTP 000). The **quorum math is
  verified by recomputation**; the conflict-detection mechanism (version vectors) and convergence
  (eventual consistency) are verified by reuse of line-checked 11; but the *attribution* of
  sloppy-quorum / hinted-handoff / Merkle anti-entropy to Dynamo, of LWW-default to Cassandra, and
  the *exact CRDT semilattice proofs* must be pinned to primaries before Phase 2 prose.
- Disagreement to resolve: whether version vectors or **dotted version vectors** (Riak) are the
  right teaching default (plain VVs have a sibling-explosion problem under many clients) — flag.
- Boundary: vector-clock *theory* + `O(N)` lower bound ⇒ 11; *consensus-based* linearizable
  alternatives ⇒ 11 + Cluster D; CRDT use in *agent memory merge* ⇒ Part III. Cross-link, don't
  duplicate.
