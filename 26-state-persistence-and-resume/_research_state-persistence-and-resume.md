# 26 · state-persistence-and-resume — research brief (full depth)

> Phase-1 research brief (NO course prose; briefs only). 26 makes the persistent tier of 25
> **durable and replayable**. The load-bearing realization (carried from 22): **the agent
> transcript is an append-only log** — which is exactly a Write-Ahead Log (07/15 WAL) and exactly
> Kafka's log (09). So **agent resume IS database crash recovery.** Bespoke structure: a
> **durability/recovery walkthrough** (the log → write-ahead → checkpoint → replay → idempotent
> resume → replication), NOT abstract clusters. Math: `_recompute.py` (12/12). Anchor source:
> PostgreSQL WAL docs (FETCHED+VERIFIED this session) + reuse of line-verified 09/15/17. Factcheck:
> `_factcheck_phase1.md`.

---

## 0. Scope and the one-sentence thesis
**An agent run is a long-lived transaction; resuming it is crash recovery.** A multi-step agent
loop can run for minutes-to-hours, spend real money (22 economics), and cause real side effects (23
tools). If the process dies — OOM, deploy, timeout, rate-limit, this very session's CWD gremlin —
you must not lose the whole run or, worse, re-do its side effects. 26 is the discipline that makes
the loop **crash-safe and resumable**, built entirely from primitives Part I/II already proved:
the log (09), WAL durability (07/15), checkpoints (07/15), and idempotency/exactly-once-effect
(17/21).

Two layers:
- **Intuitive:** keep a running journal of everything the agent decides and does; if it crashes,
  re-read the journal and pick up where it left off — without re-doing anything already done.
- **Mechanism:** persist each step **before** acting (write-ahead); snapshot compacted state
  periodically (checkpoint); on restart, **replay** the log forward from the last checkpoint (REDO),
  skipping any side effect whose idempotency key shows it already committed.

---

## 1. The transcript is a WAL (the unifying insight)
22 established the loop transcript as an append-only log. 26 names what kind of log it must be: a
**Write-Ahead Log.** PostgreSQL's WAL chapter (VERIFIED this session) states the rule precisely:
"changes to data files ... **must be written only after those changes have been logged**, that is,
after WAL records describing the changes have been flushed to permanent storage" and "Using WAL
results in a significantly reduced number of disk writes, because **only the WAL file needs to be
flushed to disk to guarantee that a transaction is committed**." Mapped to the agent:
- **data file** = the agent's externalized state (memory 25, side effects in the world via 23);
- **WAL record** = a persisted loop step (the chosen action + args + observation);
- **the rule** = persist the step record *before* executing its side effect;
- **commit = flush** = the step isn't durable until its record hits permanent storage.
"roll-forward recovery, also known as **REDO**" (VERIFIED) = exactly agent replay-on-resume.
This is also Kafka's log (09): an offset-addressed, append-only, replayable sequence; resume =
seek to the last committed offset and continue.

---

## 2. Write-ahead: persist before acting (RECOMPUTED §1)
Order matters. If you persist *after* acting, a crash in the gap loses the record of a side effect
that already happened → on resume you don't know it ran → you re-run it (double-apply) or skip
needed follow-up. Write-ahead (persist *intent* before act, *result* after) bounds crash loss to
**≤ 1 in-flight step** (recompute §1), versus losing the **entire run** if you only persist at the
end (50 steps gone). This is the WAL invariant applied to the loop.

---

## 3. Checkpointing: the recovery/overhead knee (RECOMPUTED §2, §4)
Replaying from turn 1 every time is wasteful; never checkpointing makes recovery unbounded. A
**checkpoint** snapshots compacted state (reuse 25 consolidation) so replay starts from the last
snapshot. The tradeoff is the classic WAL knee: small interval = many cheap recoveries but high
checkpoint overhead; large interval = cheap steady state but expensive replay. Recomputed: total
cost = (N/I)·c_ckpt + (I/2)·replay → minimized at **I\* = √(2·N·c_ckpt)** (= 63 steps for the
example), verified to be a true minimum. Recovery time (RTO) = I\*·t_replay = 3.16s vs 5.0s full
replay (1.6× faster, and the gap widens with run length). Same math as DB checkpoint tuning and
backup RPO/RTO planning (07/15/20).

---

## 4. Idempotent replay: don't double-apply side effects (RECOMPUTED §3 — reuse 17/21)
The dangerous part of resume: replaying a step that already **committed a side effect** (charged a
card, sent an email, wrote a file). Recomputed: replaying 12 steps where 30% are side-effecting
double-applies **3 effects** without protection; with a **per-step idempotency key** (17/21
exactly-once-effect), re-execution of a committed step is a **no-op** → 0 double-applies. This is
why 23 insisted side-effecting tools carry idempotency keys and 17/21 built exactly-once-effect:
26 is where that investment pays off. Replay must be **deterministic for reads** and
**idempotent for writes**.

---

## 5. Durability vs latency: the fsync/group-commit tradeoff (RECOMPUTED §5 — reuse 07/15)
WAL durability comes from flushing the log to permanent storage on commit (Postgres: "only the WAL
file needs to be flushed ... to guarantee that a transaction is committed"). Per-step fsync costs
latency (8ms/step) but bounds loss to ≤1 step; batching (group commit) amortizes it (1ms/step at
batch=8) but **widens the loss window** to the batch size. This is the exact 07/15 group-commit
tradeoff, now choosing the agent's durability/latency point. Agents with cheap, replayable steps
can batch; agents with irreversible side effects should fsync the step record before the effect.

---

## 6. Replication: survive node loss, not just process loss (RECOMPUTED §6 — reuse 15)
Process crash → local WAL replay. **Node** loss → the log must already be on another node. Reuse 15
verbatim: replication factor RF with a majority quorum W = ⌊RF/2⌋+1 tolerates RF−W node losses
(RF=3 → tolerate 1). For most agents, persisting state to a replicated store (managed DB / object
store) inherits this for free; the lesson is to put the WAL somewhere already durable, not on the
agent's local disk.

---

## 7. What state must persist (structure-bearing checklist)
- **The transcript/WAL** — the ordered step log (the source of truth; everything else is derivable).
- **Compacted context + memory pointers** (24/25) — so resume rebuilds the working set cheaply.
- **Cursor/offset** — which step we're on (Kafka offset / WAL LSN, 09).
- **Idempotency keys + their commit status** (17) — to make replay safe.
- **Pending tool calls / outbox** (17) — in-flight side effects to reconcile on resume.
- **Budgets consumed so far** (22/32) — so resume doesn't reset the step/cost/time budget.
NOT persisted: anything re-derivable from the log (keep the durable set minimal — the WAL philosophy).

---

## 8. Failure modes (tie-back)
Lost run (no incremental persist → §2) · double side effect on resume (no idempotency → §4, 17) ·
torn write / partial step (persist step atomically — single append, 09) · checkpoint corruption
(verify + keep N checkpoints, 20) · replay divergence (non-determinism in reads → pin/record tool
outputs in the log so replay is faithful) · node loss (→ replication, §6, 15) · poisoned state
restored (resume a poisoned memory → 25/33). **All are recovery-system failures, not model
failures.**

---

## 9. Build-your-own (toward the 28 capstone)
Make the 24/25 loop durable: append each step to a WAL (file or DB), persist-before-act, checkpoint
compacted state every I\* steps, and on startup replay from the last checkpoint with idempotency
keys gating side effects. Break it: kill the process mid-run → it resumes without losing/re-doing
work; remove idempotency keys → watch a payment double-apply on resume. Fifth harness upgrade (loop
→ tools → context → memory → **persistence/resume** → subagents → budgets).

---

## 10. Sources & provenance
- **VERIFIED anchor (fetched this session):** PostgreSQL WAL docs —
  `meta/fetched_primaries/postgres-wal-intro.txt`, receipt `_VERIFIED_2026-06-10_postgres-wal.md`
  (WAL rule: log-before-data; flush-on-commit; sequential append; roll-forward/REDO recovery).
- **RECOMPUTED:** `_recompute.py` (12/12) — write-ahead loss bound, checkpoint knee I\*=√(2N·c),
  RTO, idempotent replay, fsync/group-commit, replication quorum.
- **REUSED (line-verified Part I/II):** 07 (WAL, checkpoints, group commit), 09 (the log, offsets,
  replay), 15 (replication, quorum, durability), 17/21 (idempotency, exactly-once-effect, outbox),
  20 (RTO/RPO, backups, redundancy), 22 (transcript-as-log), 24/25 (compaction/consolidation as the
  checkpoint payload).
- **`[UNVERIFIED]` carry-forward (do NOT harden into prose):**
  - Durable-execution engines (Temporal, AWS Step Functions, DBOS) — vendor/idiom, not fetched.
  - LangGraph checkpointer / agent-framework persistence APIs — vendor, not primary.
  - ARIES recovery algorithm (Mohan et al. 1992) as the formal WAL recovery basis — not fetched
    (Postgres WAL doc covers the load-bearing rule; ARIES is the deeper citation for an appendix).
  - Event-sourcing/CQRS as the architectural framing — reuse 17's `[UNVERIFIED]` (Fowler), carried.
