# 15 · Cluster D — Failover, split-brain/fencing & real systems

> **Phase 1 brief (NO course prose).** Standard six sections. Cluster D of sub-course 15. Single-
> leader replication (A §1.2) is conflict-free but inherits one hard problem: **the leader can
> die**, and recovering from that — leader election, split-brain, fencing — is where most real
> outages live. This cluster grounds 11's consensus/CAP theory in operational practice and pins
> the topologies of real systems (Postgres/MySQL/Raft-based/Dynamo-style). Reuses 11 (leader
> election, quorum, FLP/partial synchrony, CAP/PACELC, Spanner) + Clusters A/C. Unfetched primaries
> `[UNVERIFIED from fetched source]` (network: only `lamport.azurewebsites.net`, 7th session).

## 1. Key mechanisms

### 1.1 Failover = detect → elect → reconfigure (and each step can go wrong)
When the leader fails, a single-leader system must:
1. **Detect** the failure — usually a timeout (no heartbeat for Δ). But **FLP (11 §1.3): "dead" and
   "slow" are indistinguishable** in an async network, so detection is a *guess*; too-short Δ →
   false positives (needless failovers), too-long Δ → long unavailability. There is no perfect
   timeout — this is the partial-synchrony reality (11 §1.3).
2. **Elect** a new leader — pick a follower (ideally the most up-to-date, i.e. furthest in the log)
   and promote it. Done safely via a **consensus vote over a quorum** (Raft leader election, 11
   §1.5: majority votes, so two leaders can't both win) or an external coordinator (ZooKeeper/etcd
   lease). *(Raft verified in 11; ZooKeeper/etcd `[UNVERIFIED]`.)*
3. **Reconfigure** — redirect clients + remaining followers to the new leader; the old leader, if it
   returns, must **step down** (become a follower) and not keep accepting writes.

### 1.2 Split-brain — the failure mode that corrupts data
If detection is wrong (the old leader is alive but unreachable, e.g. a network partition) and a new
leader is elected anyway, **two nodes both believe they are leader** and both accept writes →
divergent, conflicting histories on what was supposed to be a conflict-free single-leader system.
This is the worst case: silent data corruption / lost updates. It is **CAP made concrete (11 §1.6)**:
during a partition you cannot have both a always-available writable leader on each side *and*
consistency — choosing availability on both sides gives split-brain.

### 1.3 Fencing — making the old leader harmless
The fix isn't "elect faster," it's **fencing**: ensure a deposed/zombie leader's writes are
*rejected* even if it doesn't know it was deposed.
- **Quorum/majority requirement** — a leader may only commit a write if it can reach a majority
  (11 §1.5); a partitioned-off old leader on the minority side *cannot* reach a quorum, so it can't
  commit → it fences itself. This is why Raft-based systems are split-brain-safe by construction:
  the minority side simply can't make progress.
- **Fencing tokens** — every leadership grant carries a monotonically increasing token (epoch/term/
  lease number); the storage/resource rejects any write carrying an *older* token than it has seen.
  So even if a zombie leader sends a write, the resource fences it. (Raft `term`, ZooKeeper `zxid`/
  epoch, generic lock-service fencing token — the classic Kleppmann "fencing tokens" example.)
  *(`[UNVERIFIED]`; Raft term verified in 11.)*
- **STONITH** ("shoot the other node in the head") — power-fence the old node externally. Heavy-
  handed, used in HA clusters (Pacemaker). *(`[UNVERIFIED]`.)*

The unifying rule: **never trust a leader's self-belief; gate writes on a quorum or a token.** This
is the operational payoff of 11's "majority intersection" — it's not just for choosing a value, it's
for *preventing two leaders*.

### 1.4 The lost-write window during failover
If replication was **async** (A §1.3) and the leader fails, writes it acked but didn't replicate are
**lost** when a behind follower is promoted — and if the old leader rejoins, those writes may need to
be *discarded* (MySQL's classic "errant transactions" / the "GTID" reconciliation problem
`[UNVERIFIED]`). Synchronous/semi-sync narrows this window at a latency cost (A §1.3). Failover and
the durability dial are the same trade-off seen from the recovery side.

### 1.5 Replication in real systems — the topologies pinned
- **PostgreSQL** — single-leader; physical WAL streaming (A §1.4); sync via
  `synchronous_standby_names` + `synchronous_commit` levels; failover is *not* built-in to core →
  external tooling (Patroni on etcd/ZooKeeper/Consul, repmgr) does detection/election/fencing.
  Logical decoding enables CDC/cross-version. *(`[UNVERIFIED]` — pin to Postgres docs.)*
- **MySQL** — single-leader; binlog (statement/row/mixed, A §1.4); semi-sync plugin; failover via
  orchestrator/MHA/Group Replication; GTIDs to reconcile errant transactions. MySQL **Group
  Replication** = Paxos-like (consensus) multi-primary option. *(`[UNVERIFIED]`.)*
- **Raft-based systems** (etcd, CockroachDB, TiKV, Consul, RethinkDB) — consensus *is* the
  replication: a per-range Raft group elects a leader and replicates the log; failover + fencing are
  built in (minority can't commit). Linearizable within a range. (Reuse 11 §1.5 Raft, verified.)
- **Dynamo-style** (Dynamo, Cassandra, Riak) — leaderless (A §1.2, C): **no failover step at all**
  because there's no leader — any node serves any request; availability via sloppy quorum + hinted
  handoff (C §1.4). The trade is the lack of linearizability. *(`[UNVERIFIED]`.)*
- **Spanner** — per-shard Paxos groups (leader per group) + 2PC over Paxos + TrueTime; failover is a
  Paxos re-election within the group; externally consistent (11 §1.8, verified). The "have it all" by
  paying with TrueTime commit-wait + hardware clocks.

### 1.6 CAP/PACELC made concrete (the choosing framework)
This sub-course turns 11's CAP/PACELC theory into an operational checklist:
- **During a partition (CAP):** a single-leader system on the minority side must choose — refuse
  writes (**CP**, consistent but unavailable there) or accept them and risk split-brain (**AP**).
  Quorum/fencing makes the principled choice CP for the minority. Dynamo-style chooses AP (stay
  available, reconcile later via C's machinery).
- **When healthy (PACELC's ELC):** strong consistency *still* costs latency — sync replication /
  quorum / leader round-trips (11 §1.6). Async read replicas trade that latency for the lag
  anomalies of Cluster B.
- The practitioner's decision = (a) how bad is a lost/stale write for this data, vs (b) how bad is
  unavailability, vs (c) the steady-state latency budget. 14's denormalized/duplicated data raises
  the cost of (a) — which is why this whole sub-course exists. *(CAP/PACELC primaries Gilbert-Lynch/
  Brewer/Abadi `[UNVERIFIED]`, carried from 11.)*

## 2. Foundational sources

**Verified by reuse (line-checked earlier — NOT re-fetched):**
- FLP: dead vs slow indistinguishable → detection is a guess; partial synchrony — 11 §1.3.
- Raft leader election by majority vote (two leaders can't win) + `term` as a fencing epoch — 11
  §1.5 (Raft, verified).
- Quorum = majority intersection → minority can't commit (split-brain safety) — 11 §1.5.
- CAP (C-vs-A during partition) + PACELC (latency tax when healthy) — 11 §1.6.
- Spanner (Paxos per shard + 2PC over Paxos + TrueTime) — 11 §1.8 (verified).
- Sloppy quorum + hinted handoff (why leaderless has no failover) — 15 Cluster C §1.4.
- Async durability window — 15 Cluster A §1.3.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carry forward:**
- Kleppmann, *DDIA* ch.5 (failover, split-brain) + ch.8 (fencing tokens, "The Truth Is Defined by
  the Majority") + ch.9.
- DeCandia et al., **Dynamo**, SOSP 2007 (leaderless, no-failover model).
- PostgreSQL docs (streaming replication, `synchronous_commit`, logical decoding) + Patroni docs.
- MySQL docs (binlog, semi-sync, GTID, Group Replication).
- etcd / CockroachDB / Consul / TiKV docs (Raft groups, ranges, leader leases).
- ZooKeeper (Zab, `zxid`, ephemeral nodes/leases) / Chubby (lock service, leases) — carried from 11/12.
- Pacemaker/Corosync STONITH docs.

## 3. Why it is this way — forcing functions
- **Failover is hard because failure detection is impossible to do perfectly** (FLP, 11 §1.3) — every
  timeout is a bet, so every failover risks a false positive (split-brain) or slow recovery.
- **Split-brain corrupts data because single-leader's correctness assumed exactly one writer** —
  break that assumption and you've turned a conflict-free design into an unresolved-conflict one.
- **Fencing exists because you can't make a node *know* it was deposed** — so you make its writes
  *ineffective* via quorum (it can't reach majority) or tokens (resource rejects stale epoch).
- **Quorum is the unifying primitive** — the same majority-intersection that chooses a value (11)
  also prevents two leaders, because the minority simply can't commit.
- **The async lost-write window reappears at failover** because un-replicated acked writes have
  nowhere to come from when a behind follower is promoted — durability vs latency, again.
- **CAP/PACELC are the choosing framework** because a partition forces C-vs-A and even health costs
  latency-for-consistency; the data's cost-of-staleness (raised by 14's duplication) sets the choice.

## 4. Common misconceptions to preempt
- "Failover is automatic and safe." It's three fallible steps (detect/elect/reconfigure); the unsafe
  middle is split-brain.
- "Just elect a new leader faster." Speed *increases* false-positive split-brain risk; safety comes
  from fencing, not speed.
- "A network partition just makes things slow." It can elect a second leader → split-brain → silent
  corruption if you don't fence.
- "Synchronous replication means no data loss on failover." It narrows but doesn't fully erase the
  window, and it stalls writes if the sync follower is down.
- "Raft/etcd can split-brain." No — the minority can't reach a quorum, so it can't commit; that's the
  built-in fencing.
- "Leaderless systems need failover." They don't — no leader to fail; they trade that simplicity for
  no linearizability (C).
- "Fencing tokens are optional if you have leader election." No — a zombie leader can still issue
  writes; the resource must reject stale tokens.
- "CAP lets you pick two of three." No (11) — partition tolerance is mandatory; the real choice is
  C-vs-A *during* a partition, and latency-vs-consistency when healthy (PACELC).

## 5. Best build-your-own target(s)
- **Failover harness**: single leader + followers + a heartbeat timeout; kill the leader, promote the
  furthest-ahead follower; tune Δ to induce false-positive failovers (FLP made tangible).
- **Split-brain reproducer → fencing fix**: partition the leader from a quorum but keep a client
  attached; show divergence; then add quorum-gated commits + fencing tokens and watch the zombie
  leader's writes get rejected.
- **Lost-write window measurer**: async-replicate, kill the leader mid-flight, promote a behind
  follower, count lost acked writes; flip to semi-sync and re-measure. (Pairs with A.)
- **CAP/PACELC dashboard**: one knob for "during partition: CP or AP" and one for "healthy: latency
  vs consistency"; observe availability, staleness, and latency move together. (Pairs with 11/13.)

## 6. Open questions / gaps (do NOT erase)
- DDIA ch.5/8/9, Dynamo, and all DB-vendor docs above are `[UNVERIFIED]` (network HTTP 000). The
  *mechanisms* (detection-is-a-guess, quorum/token fencing, minority-can't-commit, CAP/PACELC
  choice) are verified by reuse of line-checked 11 (FLP, Raft, quorum, CAP/PACELC, Spanner); the
  *vendor specifics* (Patroni/orchestrator behavior, GTID errant-transaction handling, `zxid`,
  STONITH, exact `synchronous_commit` semantics) and DDIA's exact wording must be pinned before
  Phase 2 prose.
- Disagreement to resolve: whether to teach failover primarily through Raft (consensus-native, clean)
  or through the messier Postgres/MySQL + external-tooling reality (what most engineers operate) —
  likely both, framed as "consensus does it for you vs you bolt it on." Flag.
- Boundary: consensus *internals* (Paxos/Raft election + log matching) ⇒ 11 (+ appendix L); lock-
  service internals (ZooKeeper Zab/Chubby) ⇒ 12/appendix; SLO/alerting on failover ⇒ 19;
  capacity/headroom for failover ⇒ 13/20. Cross-link, don't duplicate.
