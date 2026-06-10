# 15 — replication-and-consistency-in-practice — RECONCILED research (`_research.md`)

> **Phase 1 deliverable (NO course prose).** Synthesis of four factchecked clusters into the
> standard six sections (ADR-001: each cluster keeps its deep `_research_<cluster>.md`; this file
> reconciles overlaps, states the cross-cluster thesis, consolidates sources + gaps). Every
> `[UNVERIFIED from fetched source]` / residual gap from the clusters is preserved here in intent.
>
> **Cluster files (read for full depth):**
> - A — `_research_replication-topologies-and-log.md` (why replicate; single/multi/leaderless;
>   sync/async/semi-sync; the replication log statement/WAL/logical/trigger; read replicas)
> - B — `_research_replication-lag-anomalies-and-fixes.md` (lag window; read-your-writes,
>   monotonic-reads, consistent-prefix anomalies + their session-guarantee fixes)
> - C — `_research_conflicts-and-quorum-tuning.md` (conflict detection via version vectors; LWW vs
>   VV vs CRDT; read-repair/anti-entropy/hinted-handoff; quorum tuning W+R>N)
> - D — `_research_failover-split-brain-real-systems.md` (failover detect/elect/reconfigure;
>   split-brain + fencing; Postgres/MySQL/Raft-based/Dynamo-style; CAP/PACELC made concrete)
> - Factcheck — `_factcheck_phase1.md` (math verified by recomputation; mechanisms verified by reuse
>   of 06/07/11/13/14; attributions flagged `[UNVERIFIED]`; **0 blockers**)
>
> **Reconciliation verdict:** 15 is reconciled on the basis that its load-bearing content — the
> *method + mathematics* of replicating data, paying the lag/consistency tax, resolving write
> conflicts, tuning quorums, and surviving leader failure — is verified end-to-end (recomputation
> for the quorum/staleness/failure-tolerance math; reuse of line-checked 06/07/11/13/14 for every
> mechanism), **0 factcheck blockers across A-D**. The remaining gaps are *canonical/vendor/
> historical attributions* (DDIA ch.5/8/9, Dynamo, Bayou session guarantees, CRDT papers, CAP/PACELC
> primaries, and the Postgres/MySQL/Mongo/Cassandra/Riak/etcd/CockroachDB/ZooKeeper docs), all
> uniformly network-blocked (7th session, HTTP 000 on every non-Lamport host) and carried forward
> `[UNVERIFIED]`. None is load-bearing for the *method*; none may harden into Phase-2 prose until
> fetched.

---

## The cross-cluster thesis (what this sub-course actually teaches)

15 is **11's consistency theory cashed out into operations, and the place where 14's bills come
due.** 14 ends by handing off two debts: denormalization (Cluster A there) duplicates a fact across
rows, and cross-partition operations (Cluster C there) span nodes — both create *multiple copies of
state that can disagree*. Replication does the same thing deliberately (copies for HA/read-scale/
locality). So the whole sub-course is one question:

> **Once the same fact lives in more than one place, who may write it, how stale may a reader be,
> what happens when copies disagree, and what happens when the writer dies?**

The four clusters are that question answered in order:

1. **A - topology decides whether conflicts can exist.** Where writes land is the root choice:
   single-leader (one writer ⇒ total order ⇒ *no* conflicts, but a failover liability), multi-leader
   / leaderless (many writers ⇒ write-availability + locality, but conflicts are now structural).
   Sync/async is the durability-vs-latency dial; the replication log (statement/WAL/logical) must be
   *deterministic* or replicas diverge. Read replicas scale reads (13 X-axis) but not writes, and
   buy that scale with staleness.
2. **B - async replication's staleness becomes user-visible anomalies.** The lag window manifests as
   three named anomalies - read-your-writes ("my own post vanished"), monotonic-reads ("time ran
   backwards"), consistent-prefix ("effect before cause across keys") - each cured by the *weakest*
   session guarantee that removes it (read-from-leader / sticky routing / replica pinning / causal
   token). These are exactly 11's consistency models on a monotone ladder; you buy the cheapest rung
   that hides the anomaly the user can perceive, not linearizability.
3. **C - when multiple writers disagree, you detect and converge.** Concurrency is detected with
   version vectors (wall clocks can't, 11). Resolution climbs a ladder: LWW (free, lossy) -> version
   vectors + app merge (lossless, app work) -> CRDTs (lossless + automatic via semilattice merge).
   Divergence allowed for availability is repaired in the background by read-repair + Merkle
   anti-entropy + hinted handoff. Freshness is dialed by quorum: **W+R>N guarantees a read sees a
   recent write** (pigeonhole) - but *not* linearizability.
4. **D - the single-leader convenience has one bill: the leader dies.** Failover = detect (a guess,
   by FLP) -> elect (consensus vote over a quorum) -> reconfigure. The catastrophic failure is
   split-brain (two leaders -> corruption), and the fix is *fencing*: gate every write on a quorum
   (minority can't commit) or a monotonic token (resource rejects stale epochs). Real systems
   instantiate this differently - Postgres/MySQL bolt failover on; Raft-based bake it in; Dynamo-
   style have *no* failover (no leader). CAP/PACELC becomes the concrete choosing framework.

The through-line, identical in spirit to 13 and 14: **push the hard work up the stack so the
expensive case stays rare.** Choose single-leader if you can tolerate the failover bill and avoid
conflicts entirely; reach for multi-writer only when write-availability/locality forces it, and then
pay with conflict resolution. Buy the weakest consistency guarantee that hides the anomaly. Tune the
quorum to put latency where you can afford it. And never trust a leader's self-belief - gate on a
quorum or a token. The same pigeonhole (majority intersection, 11 §1.5) does triple duty here: it
makes quorum reads fresh (C), it makes consensus elect one leader (D), and it makes the minority
side unable to corrupt data (D).

---

## 1. Key mechanisms (consolidated)

- **Three reasons to replicate** - availability, read-scale, locality - orthogonal to partitioning
  (14): replicate each partition R-ways. *(A §1.1)*
- **Topology = who may write:** single-leader (total order, no conflicts, failover liability) /
  multi-leader (per-region writers, conflicts) / leaderless (quorum, no leader, no failover).
  *(A §1.2)*
- **Sync/async/semi-sync** = durability-vs-latency dial; async has a lost-write window on leader
  failure; semi-sync (one sync follower) is the practical knee. *(A §1.3, D §1.4)*
- **Replication log formats:** statement (compact, nondeterministic -> diverges), WAL/physical
  (exact, version-coupled), logical/row (decoupled, feeds CDC -> 14/17), trigger (last resort).
  Determinism is the whole game. *(A §1.4)*
- **Read replicas** scale reads not writes; staleness is the cost -> Cluster B anomalies. *(A §1.5)*
- **Lag window** = async apply delay; eventual consistency = "lag -> 0 if writes stop + links heal."
  *(B §1.1; reuse 11 §1.4)*
- **Three lag anomalies + fixes:** read-your-writes (read-from-leader / sticky / causal token),
  monotonic-reads (replica pinning), consistent-prefix (same-partition placement / causal metadata /
  global clock). A monotone guarantee ladder ending in linearizable. *(B §1.2-1.5; reuse 11
  consistency models)*
- **Conflict = concurrent writes** (no happened-before); detected by version vectors (not wall
  clocks). *(C §1.1-1.2; reuse 11 §1.1-1.2)*
- **Resolution ladder:** LWW (lossy) -> version vectors + merge (lossless, app) -> CRDT (lossless,
  automatic, semilattice merge: commutative/associative/idempotent). *(C §1.3)*
- **Background convergence:** read-repair (hot keys) + Merkle anti-entropy (cold keys, O(log n)
  diff, reuse 06) + hinted handoff (sloppy quorum keeps writes available during failure). *(C §1.4)*
- **Quorum tuning W+R>N** - guaranteed overlap by pigeonhole (verified by recomputation);
  W=R=majority tolerates ⌊(N-1)/2⌋ failures; W+R>N != linearizable. *(C §1.5)*
- **Failover** = detect (FLP: a guess) -> elect (quorum vote) -> reconfigure; old leader must step
  down. *(D §1.1; reuse 11 §1.3/§1.5)*
- **Split-brain** (two leaders -> corruption) fixed by **fencing**: quorum-gated commits (minority
  can't commit) + monotonic fencing tokens (reject stale epoch) + STONITH. *(D §1.2-1.3)*
- **Real systems:** Postgres/MySQL single-leader + external failover; Raft-based (etcd/CockroachDB)
  consensus-native; Dynamo-style leaderless no-failover; Spanner Paxos+2PC+TrueTime. *(D §1.5; reuse
  11 §1.8)*
- **CAP/PACELC concrete:** partition -> CP (minority refuses) or AP (stay up, reconcile later);
  healthy -> consistency still costs latency. *(D §1.6; reuse 11 §1.6)*

## 2. Foundational sources (consolidated)

**Verified by recomputation this session** (`_factcheck_phase1.md`, pure-Python, no deps):
`W+R>N <=> guaranteed overlap` (exhaustive over all quorum pairs; `W+R=N` insufficient - strict `>`
required); stale-read prob = 0 iff W+R>N (e.g. N=3,W=R=1 -> 2/3 stale; N=5,W=R=1 -> 0.8 stale);
majority quorum W=R=⌊N/2⌋+1 tolerates ⌊(N-1)/2⌋ failures (N in {3,5,7} -> {1,2,3}); async durability
window kept structural (no false precision).

**Verified by reuse (line-checked earlier - NOT re-fetched):**
- Leader = ordering device; quorum = majority intersection; Paxos/Raft replicated log; Raft
  election + `term` epoch; FLP dead-vs-slow; CAP/PACELC framing; Spanner stack - 11 `_research.md`
  §§1.1-1.8 + cluster files (Lamport/FLP/Paxos/Raft/Spanner line-verified; Gray-Lamport TODS 2006
  verified).
- Version vectors detect concurrency; wall clocks can't order without bounds; eventual consistency
  convergence - 11 §1.1-1.2/§1.4.
- WAL/physical-log = the engine's crash-recovery log; B-tree pages - 07 + 06.
- Merkle-tree O(log n) diff; hashing - 06.
- X-axis read-scale vs Z-axis shard; fan-out/lag tail framing - 13.
- Replication != partitioning; denormalization's write-side consistency tax landing here - 14.

**Blocked primaries - `[UNVERIFIED from fetched source]`, carried forward (fetch when net heals):**
- *(A)* Kleppmann DDIA ch.5; Dynamo SOSP 2007 (leaderless); Postgres docs (streaming/physical repl,
  `synchronous_standby_names`, `synchronous_commit` levels, logical decoding/`pgoutput`); MySQL docs
  (binlog STATEMENT/ROW/MIXED, semi-sync); MongoDB docs (replica sets, oplog, write concern).
- *(B)* Terry et al. "Session Guarantees..." (Bayou) PDIS 1994; DDIA ch.5; replica-lag monitoring
  (`pg_stat_replication`, `Seconds_Behind_Master`).
- *(C)* Dynamo SOSP 2007 (N/R/W, sloppy quorum, hinted handoff, Merkle anti-entropy, read-repair,
  sibling version vectors); Shapiro et al. CRDTs INRIA RR-7506 / SSS 2011; Cassandra docs (LWW,
  tunable consistency, hinted handoff, read repair, Merkle repair); Riak docs (siblings, dotted
  version vectors, CRDT types); DDIA ch.5.
- *(D)* DDIA ch.5/8/9 (failover, fencing tokens, "truth defined by the majority"); Dynamo;
  Postgres+Patroni; MySQL (GTID, Group Replication, orchestrator); etcd/CockroachDB/Consul/TiKV
  (Raft ranges/leases); ZooKeeper (Zab/`zxid`)/Chubby (carried from 11/12); Pacemaker/STONITH;
  CAP/PACELC primaries Gilbert-Lynch 2002 / Brewer 2000-2012 / Abadi 2012 (carried from 11).

## 3. "Why it's this way" - the forcing functions (consolidated)

- **You replicate because one node is a SPOF and a `1/(1-rho)` wall (13)** - HA + read-scale +
  locality are three independent pressures. *(A)*
- **Where writes land is the root choice** because it decides whether conflicts can exist at all -
  one leader buys a total order; many writers create conflicts you must resolve. *(A->C)*
- **Durability and latency are conserved** - no instant ack with a guaranteed second copy; semi-sync
  picks the knee; the same window reappears at failover. *(A, D)*
- **A replica is correct iff replay reproduces leader state** -> determinism kills statement-based,
  forces physical/logical logs. *(A)*
- **Async staleness is real and user-visible** -> session guarantees, the cheapest lever being
  routing/pinning, causal metadata only when locality fails. *(B)*
- **Multi-writer concurrency is structural** -> detect (version vectors, not clocks) + converge
  deterministically (semilattice merges) or diverge forever. *(C)*
- **Pigeonhole is the one primitive** - W+R>N freshness, consensus single-leader, minority-can't-
  corrupt - all the same majority intersection. *(C, D; reuse 11 §1.5)*
- **Failure detection is impossible to perfect (FLP)** -> failover is a bet; split-brain is the
  cost of betting wrong; fencing makes the wrong bet harmless. *(D)*
- **CAP/PACELC are the choosing framework** because a partition forces C-vs-A and health still costs
  latency-for-consistency; 14's duplication raises the cost-of-staleness that sets the choice. *(D)*

## 4. Common misconceptions to preempt (consolidated)

- "Replication gives consistency." It gives copies; consistency is the ordering/quorum/lag rules on
  top. *(A)*
- "Replication = sharding." Orthogonal; replicate a partition for HA/read-scale, shard for
  write-scale. *(A; reuse 14)*
- "Async is just faster sync." It has a real data-loss window on leader failure. *(A, D)*
- "Statement-based replication is the efficient default." Nondeterminism diverges replicas. *(A)*
- "Read replicas scale the database." Reads only; writes still serialize at the leader; more
  replicas = more lag surface. *(A, B)*
- "Eventual consistency = sometimes wrong." It converges; the issue is the transient lag window with
  well-defined, individually fixable anomalies. *(B)*
- "Read-your-writes needs linearizability." It's a cheap session guarantee. *(B)*
- "Monotonic reads = read-your-writes." Different invariants (no backward time vs see-your-own). *(B)*
- "LWW is a safe default." It silently loses concurrent writes under clock skew. *(C)*
- "Timestamps resolve conflicts." Skew misorders causally-later writes; use version vectors. *(C)*
- "CRDTs remove all conflicts." Only merge conflicts for CRDT-modeled data; semantic conflicts
  remain. *(C)*
- "W+R>N means linearizable / quorum reads are always newest." No - concurrent writes, read-repair
  races, and sloppy quorums break a global order; W+R>N buys "a recent write," not one order. *(C)*
- "Sloppy quorum is a quorum." During failures it writes to N *healthy* nodes -> no W+R>N overlap
  guarantee. *(C)*
- "Failover is automatic and safe." Three fallible steps; the unsafe middle is split-brain. *(D)*
- "Elect faster to fix failover." Speed increases false-positive split-brain; fencing is the fix. *(D)*
- "A partition just makes things slow." It can elect a second leader -> corruption without fencing. *(D)*
- "Raft/etcd can split-brain." Minority can't reach a quorum, so it can't commit. *(D)*
- "Fencing tokens are optional with leader election." A zombie leader still issues writes; resources
  must reject stale tokens. *(D)*
- "CAP = pick two of three." Partition tolerance is mandatory; choose C-vs-A during a partition,
  latency-vs-consistency when healthy. *(D; reuse 11)*

## 5. Best build-your-own target(s) (consolidated)

- **Single-leader replicator + three-log bake-off** (statement vs row vs WAL; inject `NOW()`/`RAND()`
  to diverge statement-based; measure follower lag). *(A; pairs 07/09)*
- **Sync/async/semi-sync dial** (write latency vs durability window; kill leader mid-flight). *(A, D)*
- **Lag-anomaly reproducer + session-guarantee toggles** (see the missing comment; add read-your-
  writes / monotonic-reads / consistent-prefix; measure each fix's latency). *(B; makes 11's ladder
  tangible)*
- **Quorum dial simulator** (confirm P(stale)=0 iff W+R>N; reproduce 2/3 and 0.8 stale rates). *(C;
  pairs 13)*
- **Conflict bake-off + CRDT mini-lib** (LWW vs VV+merge vs CRDT; count lost updates; fuzz a
  G-Counter/OR-Set to prove convergence). *(C)*
- **Anti-entropy with Merkle trees + hinted handoff** (O(log n) diff; kill/restore a node to watch a
  hint deliver). *(C; pairs 06)*
- **Failover harness + split-brain reproducer -> fencing fix** (induce false-positive failover;
  partition the leader; add quorum-gated commits + fencing tokens; reject zombie writes). *(D)*
- **CAP/PACELC dashboard** (knobs: partition CP-vs-AP, healthy latency-vs-consistency; watch
  availability/staleness/latency move together). *(D; pairs 11/13)*

## 6. Open questions / gaps to close (consolidated - preserved verbatim in intent)

- **All canonical/vendor/historical attributions are network-blocked** `[UNVERIFIED]` (7th session,
  HTTP 000 on every academic/vendor host; only `lamport.azurewebsites.net` resolves): DDIA ch.5/8/9,
  Dynamo SOSP 2007, Bayou session guarantees (Terry 1994), CRDT papers (Shapiro 2011), CAP/PACELC
  (Gilbert-Lynch/Brewer/Abadi), and the Postgres/MySQL/MongoDB/Cassandra/Riak/etcd/CockroachDB/
  Consul/TiKV/ZooKeeper/Patroni/Pacemaker docs. The *math/method* is verified by recomputation +
  reuse; the *citations / exact wording / vendor specifics* (e.g. Postgres `synchronous_commit`
  levels, MySQL semi-sync ack timing + GTID errant-transaction handling, MongoDB oplog idempotence,
  Cassandra LWW + tunable consistency names, Riak dotted version vectors, `zxid`, STONITH) need
  primaries when the network heals. Teach mechanisms now; do NOT harden specifics into Phase-2 prose
  until fetched.
- **Disagreements to resolve with sources:** exact meaning of "synchronous" across vendors (commit
  vs flush vs apply on the follower; Postgres `remote_write|on|remote_apply` differ materially) (A);
  whether "consistent prefix" is a distinct guarantee or the read-side of causal consistency - DDIA
  lists it separately, the academic literature folds it in (B); plain version vectors vs **dotted**
  version vectors as the teaching default given sibling explosion (C); whether to teach failover via
  Raft (clean) or via the Postgres/MySQL+external-tooling reality most engineers operate (likely
  both) (D).
- **Boundary discipline (cross-link, do NOT duplicate downstream mechanics):**
  - consensus *internals* (Paxos/Raft election + log matching + safety) + vector-clock *theory* +
    CAP/PACELC *proofs* + Spanner stack => **11** (+ appendix L). This sub-course is the *practice*.
  - storage-engine/WAL physics + B-tree pages + Merkle/hashing => **06/07**.
  - shard-key choices that keep causally-related writes co-located + denormalization's write tax =>
    **14**; the AKF X-axis read-scale framing => **13**.
  - CDC/event-ordering fan-out of the logical log + saga orchestration => **17**; materialized-view
    maintenance => **14/17**.
  - hot-key *caching/CDN* mitigation => **16/08**; tail-tolerant hedged/tied requests => **20**;
    SLO/alerting + capacity headroom for failover => **19/13/20**.
  - lock-service internals (ZooKeeper Zab / Chubby) => **12 / appendix**; CRDT use in agent memory
    merge => **Part III**.
- **Next 15 work (optional, before Phase 2 prose):** fetch the blocked A/B/C/D primaries when a
  healthier network exists and upgrade the `[UNVERIFIED]` flags; otherwise 15 is research-complete at
  the *method/math* level. Next Phase-1 batch: **16-21** (Part II); 16 (caching-and-cdn-strategies)
  is the natural next start - it absorbs the hot-key + read-scale + staleness pressures that 14 (hot
  shards) and 15 (read replicas, lag) both hand off.
