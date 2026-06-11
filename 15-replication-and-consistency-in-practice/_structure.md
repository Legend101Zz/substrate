# 15 — Replication and Consistency in Practice · _structure.md

**Identity:** 11's consistency theory cashed out into operations — and the place where 14's bills
come due. Once the same fact lives in more than one place, who may write it, how stale may a
reader be, what happens when copies disagree, and what happens when the writer dies?

**Bespoke shape — "the four questions of any replicated fact."** NOT a vendor feature tour. The
moment state has more than one copy (deliberate replication, or 14's denormalization + cross-
partition spread), four questions follow IN ORDER, and the sub-course is those four questions:
**A — topology decides whether conflicts can exist (who may write) → B — async staleness becomes
user-visible anomalies (how stale) → C — when writers disagree, detect & converge (copies
disagree) → D — the single-leader convenience has one bill: the leader dies (writer dies).** The
recurring primitive is the pigeonhole (majority intersection, 11): it makes quorum reads fresh,
elects one leader, AND makes the minority unable to corrupt. Practice-focused; theory lives in 11/L.

## Dependency position
- **Depends on:** 11 (consensus internals, vector clocks, CAP/PACELC proofs, Spanner — 15 is the
  PRACTICE of these), 14 (absorbs denormalization's write-tax + cross-partition read consistency;
  replicate-each-partition-R-ways), 07 (WAL/physical log = crash-recovery log), 06 (Merkle trees,
  hashing), 13 (X-axis read-scale, lag tail), 09 (logs/ISR preview).
- **Feeds into:** 16 (a cache IS a deliberately-stale replica — staleness ladder re-pointed), 17
  (logical log → CDC on a bus; materialized-view maintenance), 19/20 (failover capacity + SLOs),
  Part III (CRDT agent-memory merge).
- **Appendix links DOWN:** L-consensus (Paxos/Raft/BFT/isolation formalism in full), F-postgres
  (streaming/logical replication guts). 15 owns the operational practice.

## Chapter specs (3–5 lines each)
### A — topology (who may write)
1. **Why replicate, and the three reasons** — availability (one node is a SPOF + a `1/(1−ρ)` wall,
   13), read-scale, locality; orthogonal to partitioning (14 — replicate EACH partition R-ways).
   Sets up that replication = deliberately making copies that can disagree.
2. **Topology decides whether conflicts can exist** — single-leader (one writer ⇒ total order ⇒ NO
   conflicts, but a failover liability) vs multi-leader/leaderless (many writers ⇒ write-
   availability + locality, but conflicts are structural). Where writes land is the root choice.
3. **The durability/latency dial & the replication log** — sync/async/semi-sync (semi-sync = the
   practical knee); async has a lost-write window on leader failure. A replica is correct iff replay
   reproduces leader state ⇒ DETERMINISM is the whole game: statement (compact, nondeterministic →
   diverges) vs WAL/physical (exact, version-coupled) vs logical/row (decoupled, feeds CDC → 17).
   Read replicas scale READS not writes; staleness is the cost → Part B.

### B — staleness (how stale)
4. **The lag window & three anomalies** — async apply delay; eventual consistency = "lag→0 if
   writes stop + links heal." Three named, user-visible anomalies: read-your-writes ("my post
   vanished"), monotonic-reads ("time ran backwards"), consistent-prefix ("effect before cause").
5. **Session guarantees: buy the cheapest rung** — each anomaly cured by the WEAKEST guarantee that
   removes it: read-from-leader / sticky routing (read-your-writes), replica pinning (monotonic),
   same-partition placement / causal token (consistent-prefix). These ARE 11's consistency models
   on a monotone ladder ending in linearizable — you buy what the user can perceive, not lin.

### C — conflicts (copies disagree)
6. **Detecting concurrency** — a conflict = concurrent writes (no happened-before); detected by
   version vectors, NOT wall clocks (clock skew misorders causally-later writes, 11). Dotted
   version vectors as the sibling-explosion fix.
7. **Resolution & quorum tuning** — ladder: LWW (free, lossy) → version vectors + app merge
   (lossless, app work) → CRDTs (lossless + automatic via semilattice merge: commutative/
   associative/idempotent). Quorum freshness: **W+R>N guarantees overlap** (pigeonhole, VERIFIED) —
   but NOT linearizability; W=R=majority tolerates ⌊(N−1)/2⌋ failures. Sloppy quorum ≠ quorum.
8. **Background convergence** — read-repair (hot keys) + Merkle anti-entropy (cold keys, O(log n)
   diff, 06) + hinted handoff (sloppy quorum keeps writes available during failure).

### D — the writer dies
9. **Failover & split-brain** — failover = detect (a GUESS, by FLP) → elect (quorum vote) →
   reconfigure; the catastrophic failure is split-brain (two leaders → corruption). Electing FASTER
   increases false-positive split-brain — speed is not the fix.
10. **Fencing & real systems** — fencing makes the wrong bet harmless: quorum-gated commits
    (minority can't commit) + monotonic fencing tokens (resource rejects stale epochs) + STONITH.
    Real systems instantiate differently: Postgres/MySQL bolt failover on; Raft-based (etcd/
    CockroachDB) bake it in; Dynamo-style have NO failover. CAP/PACELC becomes the concrete
    choosing framework (partition → CP/AP; healthy → latency-vs-consistency).

## Paired build labs (/build — replicator + reproducers)
Single-leader replicator + three-log bake-off (statement vs row vs WAL; inject `NOW()`/`RAND()` to
diverge statement-based; measure follower lag) → sync/async/semi-sync dial (write latency vs
durability window; kill leader mid-flight) → lag-anomaly reproducer + session-guarantee toggles
(see the missing comment; add each fix; measure latency cost) → quorum dial simulator (confirm
P(stale)=0 iff W+R>N; reproduce 2/3 and 0.8 stale rates) → conflict bake-off + CRDT mini-lib (LWW
vs VV+merge vs CRDT; count lost updates; fuzz a G-Counter/OR-Set to prove convergence) →
anti-entropy with Merkle trees + hinted handoff → failover harness + split-brain reproducer →
fencing fix (induce false-positive failover; partition the leader; add quorum-gated commits +
fencing tokens; reject zombie writes) → CAP/PACELC dashboard.

## Diagrams needed
- The four-questions arc (topology→staleness→conflicts→writer-dies) as spine motif.
- Single-leader (total order, no conflicts) vs multi-leader/leaderless (structural conflicts).
- Durability/latency dial (sync/semi-sync/async) + lost-write window at failover.
- The three lag anomalies as timelines + the session guarantee that cures each.
- Version-vector concurrency detection (incomparable = conflict) vs wall-clock misorder.
- Resolution ladder (LWW → VV+merge → CRDT semilattice); W+R>N pigeonhole overlap.
- Merkle anti-entropy O(log n) diff; hinted handoff during a node outage.
- Failover steps (detect/elect/reconfigure) + split-brain + fencing token rejection.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED BY RECOMPUTATION:** `W+R>N ⟺ guaranteed overlap` (exhaustive; `W+R=N` insufficient —
  strict `>`); stale-read prob 0 iff W+R>N (N=3,W=R=1 → 2/3 stale; N=5 → 0.8); majority quorum
  tolerates ⌊(N−1)/2⌋ failures (N∈{3,5,7}→{1,2,3}).
- **`[UNVERIFIED]` — all canonical/vendor attributions network-blocked:** DDIA ch.5/8/9, Dynamo
  2007, Bayou session guarantees (Terry 1994), CRDT papers (Shapiro 2011), CAP/PACELC (Gilbert-
  Lynch/Brewer/Abadi — later VERIFIED in 20/21, reconcile at draft), and Postgres/MySQL/MongoDB/
  Cassandra/Riak/etcd/CockroachDB/ZooKeeper/Patroni/Pacemaker docs (e.g. `synchronous_commit`
  levels, semi-sync ack timing, GTID, oplog idempotence, `zxid`, STONITH). Teach mechanisms now;
  do NOT harden vendor specifics until fetched.
- **Disagreements to resolve:** exact meaning of "synchronous" across vendors (commit vs flush vs
  apply; Postgres `remote_write|on|remote_apply`); whether "consistent prefix" is distinct or the
  read-side of causal; plain vs dotted version vectors as teaching default; failover via Raft
  (clean) vs Postgres/MySQL+external-tooling reality (likely both).
- **Boundary discipline:** consensus internals + vector-clock theory + CAP/PACELC proofs + Spanner
  → 11 (+ appendix L); WAL/B-tree/Merkle physics → 06/07; shard-key co-location + denormalization
  tax → 14; X-axis read-scale → 13; CDC/saga/materialized-view transport → 17; hot-key caching →
  16/08; tail-tolerant hedging → 20; SLOs/capacity headroom for failover → 19/13/20.
