# 15 · Cluster B — Replication lag: anomalies & their guarantee fixes

> **Phase 1 brief (NO course prose).** Standard six sections. Cluster B of sub-course 15. This is
> the practical face of 11's consistency models: async read replicas (Cluster A §1.5) create a
> staleness window, and that window manifests as three *named anomalies* a user actually perceives —
> each cured by a specific routing/session guarantee. Reuses 11 (consistency-model taxonomy,
> happened-before/causality) and Cluster A (single-leader async read replicas). Unfetched primaries
> marked `[UNVERIFIED from fetched source]` (network: only `lamport.azurewebsites.net`, 7th session).

## 1. Key mechanisms

### 1.1 The lag window is the root cause
A follower applies the leader's log **asynchronously**, so at any instant it is some Δt behind. Δt
is normally milliseconds but spikes without bound under write bursts, network hiccups, follower GC,
or follower recovery (it must catch up the whole backlog). **Eventual consistency = "Δt → 0 if
writes stop and links heal" (11 §1.4)** — but *during* Δt a reader on a follower sees the past.
The three anomalies below are three different shapes of "reading the past," and the fixes are
**session guarantees** weaker than linearizability but strong enough that the *one user* never sees
a contradiction. *(Reuse 11 §1.4 eventual consistency; the session guarantees map onto Bayou's
Read-Your-Writes / Monotonic-Reads / Monotonic-Writes / Writes-Follow-Reads family — Terry et al.
1994 `[UNVERIFIED]`.)*

### 1.2 Anomaly 1 — read-your-writes (read-after-write) violation
User writes to the leader, then immediately reads from a lagging follower that hasn't applied the
write → the user's *own* update vanishes ("I posted a comment and it's gone"). This is the most
jarring because it breaks the user's mental causality.
**Fixes (cheap → strong):**
- **Read-from-leader for self-readable data** — anything the user themselves can edit (their own
  profile) is read from the leader; everyone else's reads go to followers. Simple, common.
- **Read-your-writes by timestamp** — client remembers the log position/timestamp of its last
  write; reads require a replica caught up to ≥ that position (or wait/redirect). This is a
  **causal token** — exactly a logical-clock cut (reuse 11 §1.1 happened-before).
- **Sticky routing** — pin the user's session to the leader (or one replica) for a short window
  after a write, so they read where they wrote.
Caveat: across devices/sessions the client-remembered position must be shared server-side, or the
same user on phone vs laptop sees the anomaly again.

### 1.3 Anomaly 2 — monotonic-reads violation (reading backwards in time)
A user makes two reads; the first hits a *fresher* replica, the second hits a *staler* one → time
appears to **run backwards** (a comment they saw disappears on refresh). Weaker than read-your-
writes (it's about repeated reads, not your own write) but still confusing.
**Fix — monotonic reads:** ensure each user always reads from replicas **at least as fresh as their
previous read** — typically by *pinning a user to one replica* (hash of user-id → replica), or by
tracking the max log position the user has observed and never serving older. Guarantees the user
never moves backward, even if they don't see the very latest.

### 1.4 Anomaly 3 — consistent-prefix violation (causality across keys/partitions)
With partitioning (14) different keys live on different partitions, each replicated independently
with its own lag. An observer can see effect-before-cause across partitions: sees the *answer* to a
question before the *question* (the classic Kleppmann example), because the two writes are causally
ordered but land on differently-lagging partitions.
**Fix — consistent prefix reads:** guarantee that if a sequence of writes is causally ordered, any
reader sees them in that order (never a gap that reveals a later write before an earlier cause).
Mechanisms: keep causally-related writes in the **same partition** (14 shard-key design feeds this),
or attach **causal metadata / version vectors** (reuse 11 §1.2) so readers enforce the prefix, or
use a global ordering device (Spanner TrueTime, 11 §1.8). This is the practical why behind 11's
causal-consistency model.

### 1.5 The ladder: these are exactly 11's models, applied
The three fixes are not ad-hoc — they're a **monotone ladder of session/consistency guarantees**:
> read-your-writes ⊂ monotonic-reads ⊂ consistent-prefix (causal) ⊂ linearizable
Each step costs more routing/coordination and removes more anomalies. The practitioner's move is to
buy the **weakest guarantee that removes the anomaly the user can actually perceive**, not jump to
linearizable (which forces leader reads / quorum round-trips, 11 §1.6 PACELC latency tax). This is
the consistency-tax bill that 14's denormalization and cross-partition ops handed here, now paid in
concrete session-guarantee currency.

## 2. Foundational sources

**Verified by reuse (line-checked earlier — NOT re-fetched):**
- Consistency-model taxonomy + eventual consistency definition + causal consistency — 11
  `_research.md` §1.4, `_research_vector-clocks-model-taxonomy.md`.
- Happened-before / logical-clock cut (the "causal token" used for read-your-writes by position) —
  11 `_research_time-clocks-ordering-failure.md` (Lamport 1978, verified there).
- Version vectors for cross-key causal metadata — 11 §1.2 (Dynamo version vectors `[UNVERIFIED]`).
- Spanner TrueTime as a global ordering device that erases consistent-prefix anomalies — 11 §1.8
  (Spanner OSDI 2012, verified there).
- Single-leader async read replicas = the lag source — 15 Cluster A §1.5.
- Partitions lag independently (why consistent-prefix breaks) — 14 `_research.md` §"span".

**Blocked primaries — `[UNVERIFIED from fetched source]`, carry forward:**
- Terry, Theimer, Petersen, Demers et al., **"Session Guarantees for Weakly Consistent Replicated
  Data"** (Bayou), PDIS 1994 — the original read-your-writes / monotonic-reads / monotonic-writes /
  writes-follow-reads framing.
- Kleppmann, *DDIA* ch.5 — the read-your-writes / monotonic-reads / consistent-prefix exposition
  and the lag-window discussion.
- PostgreSQL / MySQL docs — replica lag monitoring (`pg_stat_replication`, `Seconds_Behind_Master`)
  and any read-routing knobs.

## 3. Why it is this way — forcing functions
- **The anomalies exist because async replication trades freshness for latency/availability** (A
  §1.3) — they are the *user-visible shadow* of the lag window, not bugs to be eliminated for free.
- **Each anomaly is a different broken invariant**: read-your-writes = "see my own causal effect";
  monotonic-reads = "never move backward in time"; consistent-prefix = "never see effect before
  cause across keys." They need different fixes because they break different things.
- **The fixes are session guarantees, not global consistency** because the goal is "this *one user*
  perceives no contradiction," which is far cheaper than linearizability for everyone.
- **Routing/pinning is the cheapest lever** because it converts a global-ordering problem into a
  per-session locality problem (read where you wrote; stick to one replica).
- **Causal metadata is needed only when locality isn't enough** (cross-device, cross-partition) —
  that's when version vectors / global timestamps earn their cost.

## 4. Common misconceptions to preempt
- "Eventual consistency means data is sometimes just wrong." No — it converges; the issue is the
  *transient* lag window, and the anomalies are well-defined and individually fixable.
- "Read-your-writes needs strong/linearizable consistency." No — it's a *session* guarantee, far
  cheaper (read-from-leader for self-data, sticky routing, or a per-client causal token).
- "Monotonic reads = read-your-writes." Different: monotonic reads is about not going *backward*
  across repeated reads; read-your-writes is about seeing *your own* write.
- "Pinning a user to one replica gives strong consistency." No — it only gives monotonic reads;
  that replica can still be globally stale.
- "Consistent-prefix is automatic." No — independent per-partition lag actively breaks it; you need
  same-partition placement, causal metadata, or a global clock.
- "Just add replicas to reduce anomalies." More replicas = more lag surface; anomalies are cured by
  *guarantees/routing*, not copy count.
- "The latest write is always readable somewhere." Yes — but a given *follower* read may not see it;
  that's the whole point.

## 5. Best build-your-own target(s)
- **Lag-anomaly reproducer**: single leader + deliberately-lagged follower; script a write-then-read
  to *see* the missing comment; then add read-from-leader and watch it vanish. (Pairs with A.)
- **Session-guarantee toggles**: implement read-your-writes (by stored log position), monotonic
  reads (replica pinning), consistent-prefix (causal token across two partitions); measure the
  extra latency each adds — make the 11 ladder tangible.
- **Backward-time detector**: instrument repeated reads and flag any observed version regression
  (monotonic-reads violation) under random replica selection.

## 6. Open questions / gaps (do NOT erase)
- Terry/Bayou session-guarantees primary + DDIA ch.5 are `[UNVERIFIED]` (network HTTP 000). The
  *anomaly definitions + fix mechanisms* are verified by reuse of line-checked 11 (causality,
  consistency models, version vectors, Spanner); the *historical attribution* of the session-
  guarantee names and DDIA's exact examples must be pinned before Phase 2 prose.
- Disagreement to resolve: whether "consistent prefix" is best taught as a distinct guarantee or as
  the read-side of causal consistency — sources differ (DDIA lists it separately; the academic
  literature folds it into causal+). Flag, don't flatten.
- Boundary: the *causal-consistency theory* (vector clocks, CBCAST) ⇒ 11; the *shard-key choices*
  that keep causally-related writes co-located ⇒ 14; CDC/event ordering that also enforces prefixes
  ⇒ 17. Cross-link, don't duplicate.
