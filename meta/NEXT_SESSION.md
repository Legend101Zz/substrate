# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-09 · Phase: 1 (deep research) · Harness: **code-puppy**

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
- **Phase 1 / Wave 3 / 08 caches-and-storage-systems — started only.** One starter cluster exists:
  `08-caches-and-storage-systems/_research_cache-eviction-consistency.md`.
- `meta/RESEARCH_INDEX.md` has Wave 3 additions for 07 and started-08 sources.

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **07 remaining gaps:** Graefe 1994, Graefe 1993, Selinger 1979, Mohan ARIES 1992, Crotty mmap 2022,
  MonetDB/X100, HyPer/Neumann, and PAX exact text/page claims remain `[UNVERIFIED]` or
  `[UNVERIFIED from text]` unless directly fetched/extracted. PostgreSQL SSI/deadlock/VACUUM freeze and
  InnoDB purge internals also need deeper source tracing if used.
- **08 is not reconciled and not factchecked.** Current starter brief is intentionally conservative.
  Next source clusters should include:
  1. Redis deeper pass: `evict.c` full sampled eviction/LRU/LFU/LRM mechanics, official eviction docs,
     persistence docs (RDB/AOF/rewrite/fsync), event loop/source if needed.
  2. Memcached deeper pass: extract/read NSDI 2013 Facebook Memcached paper; trace `items.c`, LRU
     maintainer/crawler, slab automove, extstore, threading, and protocol CAS/stale flags.
  3. Admission/anti-dogpile cluster: TinyLFU/W-TinyLFU/ARC/admission policies, leases/singleflight,
     thundering herd/dogpile prevention, cache consistency primary anchors.
  4. Reconcile 08 into `08-caches-and-storage-systems/_research.md` and expand index.
- **09 message-queues-logs-and-kafka** remains queued, not started.
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
current Phase 1 state, Wave 2 milestone `4a1cc71`, that 07 is now reconciled/factchecked, that 08
has exactly one starter cluster, and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError
recurs, stop and tell the user to grant Desktop/OneDrive access or move the repo to a non-OneDrive
workspace. Do not reinstall Code Puppy.

Current state to preserve:
- Wave 1 (01–03): research + reconciled briefs done; factcheck report `meta/factcheck_wave1_01-03.md`
  exists and fixes were applied in commit `4a1cc71`. Residual gaps are logged; do not erase them.
- Wave 2 (04–06): research + reconciled briefs + factcheck report `meta/factcheck_wave2_04-06.md`
  done in commit `4a1cc71`. Residual gaps are logged.
- Wave 3: 07 database-internals has three cluster briefs, `07-database-internals/_factcheck_phase1.md`,
  and reconciled `07-database-internals/_research.md`. 08 caches-and-storage-systems has one starter
  brief: `08-caches-and-storage-systems/_research_cache-eviction-consistency.md`. 09 is queued, not started.

Run this plan:
1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. Factcheck and deepen 08:
   - Verify/expand Redis eviction/TTL/persistence claims from Redis source/docs (`evict.c`, `expire.c`,
     `server.h`, official eviction/persistence docs).
   - Extract/read the Facebook Memcached NSDI 2013 paper if possible; otherwise keep leases/gutter/regional
     pool claims `[UNVERIFIED from text]`.
   - Add one or two additional 08 cluster briefs for Memcached internals and admission/dogpile/cache
     consistency, primary sources first.
3. Reconcile all 08 cluster briefs into `08-caches-and-storage-systems/_research.md` with the standard six
   sections: key mechanisms, foundational sources, why-it's-this-way constraints, misconceptions,
   build-your-own targets, open questions/gaps.
4. Expand `meta/RESEARCH_INDEX.md` with genuinely new 08 sources.
5. If time remains after 08 reconciliation, start 09 message-queues-logs-and-kafka with one source-cluster
   brief. Otherwise stop after 08 reconciliation. Do not start 10–12 or Phase 2.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md` and `meta/NEXT_SESSION.md`, ensure
   files stay under 600 lines where reasonable, run `git status --short`, commit, and report remaining gaps
   + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
