# 26 · Phase-1 factcheck — state-persistence-and-resume

> Method (same discipline as 13-25): every load-bearing claim is either (a) RECOMPUTED in
> `_recompute.py` (12/12 pass), (b) VERIFIED verbatim against a primary fetched to
> `meta/fetched_primaries/`, (c) REUSED from a previously line-verified Part I/II sub-course, or
> (d) flagged `[UNVERIFIED]` and carried forward. 0 blockers.

## Bespoke structure note
Per the Part III plan: 26 makes the 25 persistent tier durable+replayable. Its brief is a
**durability/recovery walkthrough** (log → write-ahead → checkpoint → replay → idempotent resume →
replication), NOT abstract clusters and NOT the 13-20 four-cluster shape. Plan-sanctioned.

## Anchor source fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| PostgreSQL current docs — "Write-Ahead Logging (WAL)" | `postgres-wal-intro.txt` | §1/§2/§5: WAL = log-before-data; flush-on-commit guarantees durability; sequential append; roll-forward/REDO recovery |

Fetch: `curl https://www.postgresql.org/docs/current/wal-intro.html` (HTTP 200; network healed for
postgresql.org). Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_postgres-wal.md`. This ALSO
upgrades carried `[UNVERIFIED]` WAL attributions in **07** and **15** (see that receipt's APPLIES-TO).

### Verified claims (PostgreSQL WAL)
- "changes to data files ... must be written only after those changes have been logged, that is,
  after WAL records describing the changes have been flushed to permanent storage" — VERIFIED
  verbatim (extracted from raw HTML; the rendered view collapses the paragraph). Anchors: write-ahead
  rule (§1, §2).
- "only the WAL file needs to be flushed to disk to guarantee that a transaction is committed" —
  VERIFIED verbatim. Anchors: commit=flush; fsync/group-commit tradeoff (§5).
- "roll-forward recovery, also known as REDO" — VERIFIED verbatim. Anchors: replay-on-resume = REDO
  (§1, §3).
- "Write-Ahead Logging (WAL) is a standard method for ensuring data integrity" — VERIFIED verbatim.

## Recomputed claims (`_recompute.py`, 12/12)
- Write-ahead bounds crash loss to ≤1 step vs losing all 50 with persist-at-end. PASS.
- **Checkpoint knee I\* = √(2·N·c_ckpt)** (=63.25) verified to minimize total recovery+checkpoint
  cost. PASS.
- Idempotent replay: without keys, replaying 12 steps double-applies 3 side effects; with keys, 0
  (17/21 exactly-once-effect). PASS.
- RTO = I\*·t_replay = 3.16s vs 5.0s full replay (1.6× faster, widens with run length). PASS.
- fsync durability: 8ms/step (batch 1, lose ≤1) vs 1ms/step (batch 8, lose ≤8) — the 07/15
  group-commit tradeoff. PASS.
- Replication: majority W=⌊RF/2⌋+1=2; tolerates RF−W=1 node loss (15 reuse). PASS.

## Reused (line-verified Part I/II)
- 07 WAL + checkpoints + group commit → durability primitive + the knee + fsync tradeoff (§1,3,5).
- 09 the log + offsets + replay → transcript-as-WAL, cursor/offset, seek-and-continue (§1, §7).
- 15 replication + quorum + durability → surviving node loss (§6).
- 17/21 idempotency + exactly-once-effect + outbox → safe replay of side-effecting steps (§4, §7).
- 20 RTO/RPO + backups + redundancy → recovery-time framing, checkpoint corruption (§3, §8).
- 22 transcript-as-log; 24/25 compaction/consolidation = the checkpoint payload.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Durable-execution engines (Temporal, AWS Step Functions, DBOS) — vendor/idiom, not fetched.
- Agent-framework persistence (LangGraph checkpointer, etc.) — vendor, not primary.
- ARIES recovery algorithm (Mohan et al. 1992) — the formal WAL-recovery citation; not fetched
  (Postgres WAL doc covers the load-bearing rule; ARIES belongs in an appendix deep-dive).
- Event-sourcing/CQRS framing — reuse 17's carried Fowler `[UNVERIFIED]`.

## Verdict
26 is honest and recovery-appropriate: the durability rule (write-ahead, flush-on-commit,
roll-forward/REDO) is VERIFIED against the PostgreSQL WAL docs; the economics (write-ahead loss
bound, checkpoint knee, RTO, idempotent replay, fsync tradeoff, replication tolerance) are
RECOMPUTED; the mechanisms (WAL, the log, replication, idempotency/exactly-once-effect, RTO/RPO) are
REUSED from line-verified 07/09/15/17/20/22. Residual `[UNVERIFIED]` are vendor durable-execution
products + the ARIES deep citation, none load-bearing for the resume model. Reconcile into
`_research.md`.
