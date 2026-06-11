# 26 · state-persistence-and-resume — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 26 makes the 25 persistent tier **durable
> and replayable**. Load-bearing insight (from 22): **the agent transcript is a Write-Ahead Log**
> (07/15) and Kafka's log (09) — so **agent resume IS database crash recovery.** Bespoke structure:
> a durability/recovery walkthrough. Full depth: `_research_state-persistence-and-resume.md`. Math:
> `_recompute.py` (12/12). Anchor: PostgreSQL WAL docs (FETCHED+VERIFIED). Factcheck:
> `_factcheck_phase1.md` (0 blockers).

## 1. The one idea
**An agent run is a long-lived transaction; resuming it is crash recovery.** Long runs spend money
(22) and cause side effects (23); a crash must not lose the run or re-do its effects. 26 builds
crash-safety entirely from proven primitives: the log (09), WAL durability/checkpoints (07/15), and
idempotency/exactly-once-effect (17/21).

## 2. The transcript is a WAL (unifying insight, VERIFIED)
PostgreSQL's WAL rule, VERIFIED: changes "must be written only after those changes have been
logged ... flushed to permanent storage"; "only the WAL file needs to be flushed to disk to
guarantee that a transaction is committed"; recovery is "roll-forward ... REDO." Mapped to the
agent: data file = externalized state (25) + world side effects (23); WAL record = a persisted loop
step; commit = flush the record before the side effect; resume = REDO (replay) from the last
checkpoint. Same as Kafka's offset-addressed replayable log (09): seek to last committed offset and
continue.

## 3. The mechanism, walked (RECOMPUTED)
- **Write-ahead (§1):** persist intent before acting → crash loses ≤1 in-flight step, vs the whole
  run if you persist only at the end (1 vs 50).
- **Checkpoint knee (§2,4):** snapshot compacted state (25 consolidation) so replay starts recent;
  total cost = (N/I)·c_ckpt + (I/2)·replay minimized at **I\*=√(2·N·c_ckpt)** (=63); RTO =
  I\*·t_replay = 3.16s vs 5.0s full replay. Same as DB checkpoint + backup RPO/RTO tuning (07/15/20).
- **Idempotent replay (§3 — reuse 17/21):** replaying side-effecting steps without keys
  double-applies (3 effects); with per-step idempotency keys, re-execution is a no-op (0). Replay
  = deterministic reads + idempotent writes.
- **Durability/latency (§5 — reuse 07/15):** fsync-per-step (8ms, lose ≤1) vs group-commit batching
  (1ms, lose ≤batch) — pick the point by how irreversible the side effects are.
- **Replication (§6 — reuse 15):** process crash → local replay; node loss → log must already live
  elsewhere; majority quorum W=⌊RF/2⌋+1 tolerates RF−W losses. Put the WAL on a replicated store.

## 4. What must persist (minimal durable set)
Transcript/WAL (source of truth) · compacted context + memory pointers (24/25) · cursor/offset
(09 LSN) · idempotency keys + commit status (17) · pending tool calls/outbox (17) · budgets
consumed (22/32). **Not** persisted: anything re-derivable from the log (the WAL minimality
philosophy).

## 5. Failure modes
Lost run (no incremental persist) · double side effect on resume (no idempotency → 17) · torn/partial
step (atomic single append, 09) · checkpoint corruption (verify + keep N, 20) · replay divergence
(record tool outputs in the log so replay is faithful) · node loss (→15) · poisoned state restored
(→25/33). **All recovery-system failures, not model failures.**

## 6. Build-your-own
Make the 24/25 loop durable: append each step to a WAL, persist-before-act, checkpoint every I\*
steps, replay-from-checkpoint on startup with idempotency keys gating side effects. Break it: kill
mid-run → clean resume; remove keys → payment double-applies on resume. Fifth harness upgrade (loop
→ tools → context → memory → **persistence/resume** → subagents → budgets).

## 7. Provenance summary
- **VERIFIED anchor:** PostgreSQL WAL docs — `meta/fetched_primaries/postgres-wal-intro.txt`,
  receipt `_VERIFIED_2026-06-10_postgres-wal.md` (also upgrades 07/15 carried WAL `[UNVERIFIED]`).
- **RECOMPUTED:** `_recompute.py` (12/12) — write-ahead bound, checkpoint knee, RTO, idempotent
  replay, fsync/group-commit, replication tolerance.
- **REUSED:** 07, 09, 15, 17/21, 20, 22, 24, 25.
- **`[UNVERIFIED]` carry-forward:** durable-execution engines (Temporal/Step Functions/DBOS);
  agent-framework checkpointers; ARIES (Mohan 1992) formal recovery; event-sourcing/CQRS (17's
  Fowler). None load-bearing for the resume model.

---
**26 reconciled.** Next in dependency order: **27-planning-and-multi-agent-orchestration** (multiple
loops coordinating; ↔ 11 consensus/ordering + 17 async/EDA + 20 resilience/tail). After 27 this
session should close at a clean checkpoint.
