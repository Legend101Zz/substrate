# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 · Phase: 1 (deep research) · Harness: **code-puppy**

---

## Code Puppy recovery note (still relevant)

The earlier crash was **not** a research/content failure. Code Puppy callback code failed while
rebuilding the prompt because `os.getcwd()` / `Path.cwd()` raised:

```text
PermissionError: [Errno 1] Operation not permitted
```

Launch from the shorter Desktop path first:

```bash
cd /Users/m0t0hu6/Desktop/substrate
pwd
uvx code-puppy -i
```

This session confirmed:

- shell `pwd` = `/Users/m0t0hu6/Desktop/substrate`
- physical `pwd -P` / git top-level resolve through OneDrive:
  `/Users/m0t0hu6/Library/CloudStorage/OneDrive-WalmartInc/Desktop/substrate`
- no `cwd` PermissionError occurred.

If the callback permission error recurs, do **not** edit or reinstall anything under
`/Users/m0t0hu6/.code-puppy-venv`. Instead: grant the terminal/Code Puppy process Desktop/OneDrive
access in macOS Privacy settings, or copy the repo to a non-OneDrive workspace and continue there.

This session also hit a separate subagent `httpx.ReadError` while trying to start 08. That was a
network/stream error, not a cwd crash. No Code Puppy venv changes were made.

---

## Things DONE

- **Phase 0** — scaffold + constitution files + subagent personas + living-state files; git initialized.
- **Phase 1 / Wave 1 — 01, 02, 03 researched and reconciled.** Factcheck report
  `meta/factcheck_wave1_01-03.md` exists; fixes were applied in milestone commit `4a1cc71`.
  Residual gaps remain logged and must not be erased.
- **Phase 1 / Wave 2 — 04, 05, 06 researched, reconciled, and factchecked.** Factcheck report
  `meta/factcheck_wave2_04-06.md` exists; blockers were patched in milestone commit `4a1cc71`.
- **Phase 1 / Wave 3 / 07 database-internals — researched, factchecked, and reconciled.**
  Current artifacts:
  - `07-database-internals/_research_storage-query-exec.md`
  - `07-database-internals/_research_transactions-recovery.md`
  - `07-database-internals/_research_optimizer-external-exec.md`
  - `07-database-internals/_factcheck_phase1.md`
  - `07-database-internals/_research.md`
- 07 factcheck blockers were patched:
  - BusTub `READ_COMMITTED`/`REPEATABLE_READ` lock-manager behavior is Project 3 spec-comment material,
    not current Project 4 `IsolationLevel` enum behavior.
  - `DISABLE_LOCK_MANAGER` is now called out.
  - Deadlock victim rule is `[NEEDS-SOURCE]` until `lock_manager.cpp` or CMU Project 3 spec is fetched.
  - BusTub WAL `HEADER_SIZE=20` is source-defined header/serialized-size contract, with `txn_id_t=int64_t`
    caveat preserved.
- **Phase 1 / Wave 3 / 08 caches-and-storage-systems — researched, factchecked, and reconciled.**
  Current artifacts:
  - `08-caches-and-storage-systems/_research_cache-eviction-consistency.md`
  - `08-caches-and-storage-systems/_research_memcached-internals.md`
  - `08-caches-and-storage-systems/_research_admission-dogpile-consistency.md`
  - `08-caches-and-storage-systems/_factcheck_phase1.md`
  - `08-caches-and-storage-systems/_research.md`
- 08 factcheck was manual fallback after `factchecker` subagent `httpx.ReadTimeout`; blockers were patched.
- **Phase 1 / Wave 3 / 09 message-queues-logs-and-kafka — started only.** One starter cluster exists:
  `09-message-queues-logs-and-kafka/_research_log-abstraction-kafka-storage.md`.
- `meta/RESEARCH_INDEX.md` has Wave 3 additions for 07, 08, and starter 09 Kafka storage/log sources.

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **07 remaining gaps:** Graefe 1994, Graefe 1993, Selinger 1979, Mohan ARIES 1992, Crotty mmap 2022,
  MonetDB/X100, HyPer/Neumann, and PAX exact text/page claims remain `[UNVERIFIED]` or
  `[UNVERIFIED from text]` unless directly fetched/extracted. PostgreSQL SSI/deadlock/VACUUM freeze and
  InnoDB purge internals also need deeper source tracing if used.
- **08 remaining gaps:** pin Redis/Memcached source citations to release tags or commit SHAs before Phase 2;
  source-level Redis RDB/AOF implementation tracing is deferred to Redis appendix G unless needed; write-through
  and write-back taxonomy need stronger primary/official anchors; ARC exact pseudo-code/patent status and
  Count-Min Sketch formal math need deeper sources; XFetch/probabilistic early expiration remains unverified.
- **09 is not reconciled and not factchecked.** Current starter brief is intentionally conservative. Next source
  clusters should include:
  1. Replication/availability: Kafka replication design docs/source, leader/follower, ISR, high watermark,
     leader epochs, min ISR, acks, unclean leader election, KRaft/controller.
  2. Consumer groups/offsets: group coordinator, `__consumer_offsets`, rebalance protocols, fetch path,
     committed offsets, lag, replay.
  3. Delivery semantics: at-most/at-least/effectively-once, idempotent producer, transactions, producer state,
     exactly-once caveats.
  4. Factcheck 09 starter + new clusters, then reconcile 09 into `_research.md` and expand index.
- **Wave 4 remains untouched:** 10 nginx/proxies/LB, 11 distributed foundations, 12 research papers.

---

## Running this project in code-puppy

- Start from `/Users/m0t0hu6/Desktop/substrate`.
- Rehydrate first from `AGENTS.md`, `meta/CONSTITUTION.md`, `meta/PROGRESS.md`, `meta/SESSION_LOG.md`,
  and this file. Do not guess.
- Use tools, not vibes. Read files before modifying them. Keep diffs small.
- No parallel sub-agents in this harness. Switch agents sequentially or use multiple terminals.
- Phase 1 = research briefs only. No chapter prose.
- Validate source claims before accepting them. Primary sources first. `[UNVERIFIED]` is allowed in
  briefs but must not harden into course prose.
- End every session: append `SESSION_LOG.md`, update `PROGRESS.md` and `NEXT_SESSION.md`, run status,
  and commit.

---

## PROMPT TO RUN NEXT

```text
You are the BRAIN agent for the Substrate course project. Start safely from
`/Users/m0t0hu6/Desktop/substrate`. Read AGENTS.md, START_HERE.md, meta/CONSTITUTION.md,
meta/RESEARCH_PROTOCOL.md, meta/COURSE_MAP.md, meta/RESEARCH_INDEX.md, meta/PROGRESS.md,
meta/SESSION_LOG.md, meta/DECISIONS.md, and meta/NEXT_SESSION.md. Confirm in 3–4 lines:
current Phase 1 state, Wave 2 milestone `4a1cc71`, current checkpoint commit, that 07 and 08 are
reconciled/factchecked, that 09 has exactly one starter cluster, and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError
recurs, stop and tell the user to grant Desktop/OneDrive access or move the repo to a non-OneDrive
workspace. Do not reinstall Code Puppy.

Current state to preserve:
- Wave 1 (01–03): research + reconciled briefs done; factcheck report `meta/factcheck_wave1_01-03.md`
  exists and fixes were applied in commit `4a1cc71`. Residual gaps are logged; do not erase them.
- Wave 2 (04–06): research + reconciled briefs + factcheck report `meta/factcheck_wave2_04-06.md`
  done in commit `4a1cc71`. Residual gaps are logged.
- Wave 3: 07 database-internals has three cluster briefs, `07-database-internals/_factcheck_phase1.md`,
  and reconciled `07-database-internals/_research.md`. 08 caches-and-storage-systems has three cluster
  briefs, `08-caches-and-storage-systems/_factcheck_phase1.md`, and reconciled
  `08-caches-and-storage-systems/_research.md`. 09 has one starter brief:
  `09-message-queues-logs-and-kafka/_research_log-abstraction-kafka-storage.md`.

Run this plan:
1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. Factcheck and deepen 09:
   - Spot-check the existing starter brief claims on Kafka log abstraction, partitions, offsets, retention,
     compaction, and source links.
   - Add sequential source-cluster briefs for replication/ISR/high watermark and consumer groups/offsets.
   - If time permits, add delivery semantics/idempotent producer/transactions as a third 09 cluster.
3. Reconcile all 09 cluster briefs into `09-message-queues-logs-and-kafka/_research.md` with the standard six
   sections: key mechanisms, foundational sources, why-it's-this-way constraints, misconceptions,
   build-your-own targets, open questions/gaps.
4. Expand `meta/RESEARCH_INDEX.md` with genuinely new 09 sources.
5. If time remains after 09 reconciliation, start 10 nginx-proxies-and-load-balancing with one source-cluster
   brief. Otherwise stop after 09 reconciliation. Do not start 11–12 or Phase 2.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md` and `meta/NEXT_SESSION.md`, ensure
   files stay under 600 lines where reasonable, run `git status --short`, commit, and report remaining gaps
   + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
