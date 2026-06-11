# 26 — State Persistence and Resume · _structure.md

**Identity:** makes the 25 persistent tier DURABLE and REPLAYABLE. The load-bearing insight (from 22):
**the agent transcript is a Write-Ahead Log** (07/15) and Kafka's log (09) — so **agent resume IS
database crash recovery.** An agent run is a long-lived transaction; resuming it is roll-forward REDO.

**Bespoke shape — "a durability/recovery walkthrough" built entirely from proven primitives.** NOT a
checkpointing-library tour. Long runs spend money (22) and cause side effects (23); a crash must not
lose the run OR re-do its effects. 26 builds crash-safety from the log (09), WAL durability/checkpoints
(07/15), and idempotency/exactly-once-effect (17/21) — nothing new. The unifying move: map every WAL
concept onto the agent (data file = externalized state + world side effects; WAL record = a persisted
loop step; commit = flush-before-side-effect; resume = REDO from last checkpoint). PostgreSQL WAL docs
are the VERIFIED anchor (also upgrades 07/15's carried WAL [UNVERIFIED]). Math recomputed (12/12).
Fifth harness upgrade.

## Dependency position
- **Depends on:** 22 (transcript-as-log; the run is a long-lived transaction), 09 (the append-only
  offset-addressed replayable log), 07 (WAL/checkpoints/recovery — the direct model), 15 (durability
  dial, replication, quorum tolerance), 17/21 (idempotency → exactly-once-effect on replay), 25 (the
  persistent tier this makes durable), 20 (checkpoint verification, RPO/RTO).
- **Feeds into:** 27 (orphaned sub-agent on supervisor crash → resume), 28 (the WAL+resume stage), 33
  (poisoned state restored on resume), 31 (replay faithfulness for eval/debugging).
- **Appendix links DOWN:** F-postgres (WAL/ARIES guts), L-consensus (replicated-log durability), N-math
  (checkpoint-knee optimization). 26 owns the resume model.

## Chapter specs (3–5 lines each)
1. **The one idea: an agent run is a long-lived transaction** — long runs spend money (22) and cause
   side effects (23); a crash must not lose the run or re-do its effects. 26 builds crash-safety entirely
   from proven primitives: the log (09), WAL durability/checkpoints (07/15), idempotency (17/21).
2. **The transcript is a WAL (the unifying insight)** — PostgreSQL's WAL rule, VERIFIED: changes "must
   be written only after those changes have been logged ... flushed to permanent storage"; "only the WAL
   file needs to be flushed ... to guarantee a transaction is committed"; recovery is "roll-forward ...
   REDO." Mapped: data file = externalized state (25) + world side effects (23); WAL record = a persisted
   loop step; commit = flush the record before the side effect; resume = REDO from the last checkpoint.
   Same as Kafka's offset seek-and-continue (09).
3. **Write-ahead: persist intent before acting** — crash loses ≤1 in-flight step (vs the whole run if you
   persist only at the end: 1 vs 50). The single rule that makes resume possible.
4. **The checkpoint knee** — snapshot compacted state (25 consolidation) so replay starts recent; total
   cost = `(N/I)·c_ckpt + (I/2)·replay`, minimized at `I*=√(2·N·c_ckpt)`=63; RTO = I*·t_replay = 3.16s
   vs 5.0s full replay. Same as DB checkpoint + backup RPO/RTO tuning (07/15/20).
5. **Idempotent replay** — replaying side-effecting steps without keys double-applies (3 effects); with
   per-step idempotency keys, re-execution is a no-op (0). Replay = deterministic reads + idempotent
   writes (reuse 17/21). Record tool OUTPUTS in the log so replay is faithful.
6. **Durability/latency & replication** — fsync-per-step (8ms, lose ≤1) vs group-commit batching (1ms,
   lose ≤batch) — pick the point by how irreversible the side effects are (07/15). Process crash → local
   replay; node loss → the log must already live elsewhere (majority quorum W=⌊RF/2⌋+1 tolerates RF−W
   losses, 15). Put the WAL on a replicated store.
7. **The minimal durable set & failure modes** — persist: transcript/WAL (source of truth), compacted
   context + memory pointers (24/25), cursor/offset (09 LSN), idempotency keys + commit status (17),
   pending tool calls/outbox (17), budgets consumed (22/32). NOT persisted: anything re-derivable from
   the log (WAL minimality). Failures: lost run, double side-effect, torn step, checkpoint corruption,
   replay divergence, node loss, poisoned state restored — all recovery-system failures, not model.

## Paired build lab (/build → WAL+resume stage of own-coding-agent-harness, 28)
Make the 24/25 loop durable: append each step to a WAL, persist-before-act, checkpoint every I* steps,
replay-from-checkpoint on startup with idempotency keys gating side effects. Break it: kill mid-run →
clean resume; remove keys → a payment/edit double-applies on resume. Fifth harness upgrade
(loop → tools → context → memory → persistence/resume → …).

## Diagrams needed
- The WAL→agent mapping table (data file/WAL record/commit/recovery → agent equivalents).
- Write-ahead: persist-before-act vs persist-at-end (lose ≤1 step vs lose the run).
- Checkpoint knee curve (checkpoint cost vs replay cost; minimum at I*).
- Idempotent replay: same step re-executed → no-op with keys vs double-applied without.
- Durability dial (fsync-per-step vs group-commit) + replicated WAL (quorum tolerance).
- The minimal durable set (what persists vs what's re-derivable from the log).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED anchor:** PostgreSQL WAL docs (`meta/fetched_primaries/postgres-wal-intro.txt`, receipt
  `_VERIFIED_2026-06-10_postgres-wal.md`) — log-before-data, flush-to-commit, roll-forward REDO. This
  also UPGRADES 07/15's carried WAL [UNVERIFIED] → reconcile receipts at draft time, erase nothing.
- **RECOMPUTED (12/12):** write-ahead bound, checkpoint knee I*, RTO, idempotent replay, fsync/
  group-commit, replication tolerance.
- **`[UNVERIFIED]` carry-forward (none load-bearing for the resume model):** durable-execution engines
  (Temporal/Step Functions/DBOS); agent-framework checkpointers; ARIES (Mohan 1992) formal recovery;
  event-sourcing/CQRS (17's Fowler). Teach the resume model now; do NOT harden engine specifics or ARIES
  field-level claims until fetched (ARIES → appendix F).
- **Boundary discipline:** WAL/ARIES internals → 07 (+ appendix F); replicated-log durability → 15
  (+ appendix L); idempotency/outbox → 17; checkpoint-knee math → appendix N; resume + safety (poisoned
  state) → 33. 26 owns the agent-resume model.
