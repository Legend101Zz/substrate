# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-09 · Phase: 1 (deep research) · Harness: **code-puppy**

---

## Code Puppy recovery note (read first)

The previous session crashed immediately after this shell command:

```bash
curl -s --max-time 15 https://raw.githubusercontent.com/sqlite/sqlite/master/src/pager.c 2>&1 | sed -n 1,120p
```

The error was **not** a research/content failure. Code Puppy callback code failed while rebuilding the
prompt because `os.getcwd()` / `Path.cwd()` raised:

```text
PermissionError: [Errno 1] Operation not permitted
```

Likely trigger: macOS/OneDrive/Desktop permission weirdness around the repo path. The repo is visible
through both:

- `/Users/m0t0hu6/Desktop/substrate`
- `/Users/m0t0hu6/Library/CloudStorage/OneDrive-WalmartInc/Desktop/substrate`

Both resolve to the same directory. For the next session, launch from the shorter Desktop path first:

```bash
cd /Users/m0t0hu6/Desktop/substrate
pwd
uvx code-puppy -i
```

If the callback permission error recurs, do **not** edit or reinstall anything under
`/Users/m0t0hu6/.code-puppy-venv`. Instead: grant the terminal/Code Puppy process Desktop/OneDrive
access in macOS Privacy settings, or copy the repo to a non-OneDrive workspace and continue there.

---

## Things DONE

- **Phase 0** — scaffold + constitution files + subagent personas + living-state files; git
  initialized. Earlier commits include scaffold/history before code-puppy retargeting.
- **Phase 1 / Wave 1 — sub-courses 01, 02, 03 researched and reconciled.** One brief per source
  cluster plus `_research.md` per sub-course. Factcheck debt from ADR-002 has now been addressed via
  `meta/factcheck_wave1_01-03.md` and fixes in commit `4a1cc71`.
  - 01 residual gaps: exact Ben Eater control-word bit order, 6502 memory map, Scott/Petzold
    book-only figure/chapter detail remain source-limited / JS-rendered / book-only.
  - 02 key fixes: glibc `posix_spawn` is not simply fork+exec on Linux; it uses clone/vfork-style
    fast paths. Bash/zsh/CodeCrafters/POSIX claims verified.
  - 03 key fixes: Beej covers `poll()` and `select()`, not epoll/kqueue. E2E paper verified.
    QUIC CPU/adoption stats and Sponge Lab 4 remain cite-needed.
- **Phase 1 / Wave 2 — sub-courses 04, 05, 06 researched, reconciled, and factchecked.** Wave 2
  committed milestone: `4a1cc71` (`Phase 1 Wave 2 research and factcheck fixes`). The current HEAD is
  a recovery checkpoint that adds the 07 cluster brief and refreshed handoff state.
  - 04 operating systems: xv6/OSTEP/CS162/Linux/man-pages/Gregg clusters + reconciled `_research.md`.
  - 05 language runtimes: Crafting Interpreters/Ball-style builds + CPython/V8/libuv/HotSpot clusters
    + reconciled `_research.md`.
  - 06 data structures: B+tree/LSM/Bloom + skiplist/ring/consistent-hashing/HLL clusters + reconciled
    `_research.md`.
  - Factcheck report: `meta/factcheck_wave2_04-06.md`; blockers patched, residual gaps logged.
- **RESEARCH_INDEX.md expanded** with Wave 1 and Wave 2 sources.
- **Phase 1 / Wave 3 started — sub-course 07 database-internals, cluster 1 drafted.** Current artifact:
  `07-database-internals/_research_storage-query-exec.md` (463 lines). It covers storage pages,
  tuple layout, buffer pool/ARC, disk scheduler, WAL, B+ tree pages, Volcano/batched executors,
  scans/joins/sort/aggregation/TopN, BusTub optimizer rules, and BusTub MVCC.
- **Current living state updated:** `meta/PROGRESS.md`, `meta/SESSION_LOG.md`, and this file now reflect
  that 07 is in progress while 08/09 are queued, not started.
- **Ignored local Copilot instruction file:** `.gitignore` now ignores
  `.github/instructions/wmt-copilot.instructions.md` so local editor/Walmart tooling noise does not
  pollute commits.

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **Validate 07 cluster 1 before building on it.** Especially:
  - Graefe 1994 Volcano, Graefe 1993 survey, Selinger 1979 System R, Crotty mmap paper are currently
    identity-confirmed but not fully directly fetched; keep exact page/quote claims `[UNVERIFIED]`.
  - BusTub/Postgres numeric claims in 07 are mostly source-verified; spot-check any that become
    teaching anchors.
  - BusTub currently uses ARC replacer even though legacy constants mention LRU-K; keep that nuance.
  - BusTub `AbstractExecutor::Next()` is batch-at-a-time (`BUSTUB_BATCH_SIZE=20`), not pure
    one-tuple-at-a-time Volcano.
- **Finish sub-course 07 database-internals.** Remaining likely clusters:
  1. transactions/concurrency/recovery: ARIES, WAL/redo/undo, isolation, MVCC, 2PL/OCC, deadlocks;
     use PostgreSQL/InnoDB/BusTub/CMU sources where possible.
  2. query planning/statistics/storage-model extensions: Selinger, cardinality estimation, external
     sort, hash join variants, columnar/vectorized/compiled execution as needed.
  3. reconcile all 07 clusters into `07-database-internals/_research.md`.
- **Then continue Wave 3:**
  - 08 caches-and-storage-systems — Memcached at Facebook, Redis source/design, eviction/admission,
    cache consistency, persistence/write paths, storage media constraints.
  - 09 message-queues-logs-and-kafka — Kreps "The Log," Kafka paper/design docs/source concepts,
    partitions, offsets, replication, ISR, compaction, delivery semantics.
- **Wave 4 remains untouched:** 10 nginx/proxies/LB, 11 distributed foundations, 12 research papers.
- **Open design question for later Phase 2:** CS144 Minnow dropped the hand-authored Sponge
  `TCPConnection` state-machine lab. Decide whether Substrate's own TCP/IP lab models Sponge Lab 4.
  Logged as an open question, not yet an ADR.

---

## Running this project in code-puppy

- Start from `/Users/m0t0hu6/Desktop/substrate` to dodge the last `os.getcwd()` permission crash.
- Rehydrate first from `AGENTS.md`, `meta/CONSTITUTION.md`, `meta/PROGRESS.md`,
  `meta/SESSION_LOG.md`, and this file. Do not guess.
- Use tools, not vibes. Read files before modifying them. Keep diffs small.
- No parallel sub-agents in this harness. Switch agents sequentially or open multiple terminals.
- If using project agents, create/switch to researcher/factchecker agents from `meta/subagents/*.md`.
- Research briefs only in Phase 1. No chapter prose.
- Validate source claims before accepting them. Primary sources first. `[UNVERIFIED]` is allowed in
  briefs but must not harden into course prose.
- End every session: append `SESSION_LOG.md`, update `PROGRESS.md` and `NEXT_SESSION.md`, run status,
  and commit.

---

## PROMPT TO RUN NEXT (paste into `uvx code-puppy -i`)

```text
You are the BRAIN agent for the Substrate course project. First, recover safely from the previous
Code Puppy callback crash: make sure you launched from `/Users/m0t0hu6/Desktop/substrate`, then read
AGENTS.md, START_HERE.md, meta/CONSTITUTION.md, meta/RESEARCH_PROTOCOL.md, meta/COURSE_MAP.md,
meta/RESEARCH_INDEX.md, meta/PROGRESS.md, meta/SESSION_LOG.md, meta/DECISIONS.md, and
meta/NEXT_SESSION.md. Confirm in 3–4 lines: current Phase 1 state, Wave 2 milestone `4a1cc71`,
that current HEAD is a recovery checkpoint with one drafted 07 cluster, and the exact plan you will
run. Then proceed.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError
recurs, stop and tell the user to grant Desktop/OneDrive access or move the repo to a non-OneDrive
workspace. Do not reinstall Code Puppy.

Current state to preserve:
- Wave 1 (01–03): research + reconciled briefs done; factcheck report `meta/factcheck_wave1_01-03.md`
  exists and fixes were applied in commit `4a1cc71`. Residual gaps are logged; do not erase them.
- Wave 2 (04–06): research + reconciled briefs + factcheck report `meta/factcheck_wave2_04-06.md`
  done in commit `4a1cc71`. Residual gaps are logged.
- Wave 3: 07 database-internals started. `07-database-internals/_research_storage-query-exec.md`
  exists but is not yet reconciled into `07-database-internals/_research.md`. 08 and 09 are queued,
  not started.

Run this plan:
1. Check `git status --short` and inspect the 07 brief. If working tree is not clean, identify exactly
   what changed before editing.
2. Validate/factcheck the most load-bearing claims in `07-database-internals/_research_storage-query-exec.md`:
   BusTub page size/config constants, TablePage/TupleInfo/TupleMeta sizes, Postgres PageHeaderData and
   ItemIdData bit fields, HeapTupleHeaderData size, WAL header size, AbstractExecutor batching, ARC vs
   legacy LRU-K constants. Keep Graefe/Selinger/Crotty exact page/quote claims `[UNVERIFIED]` unless you
   directly fetch primary sources.
3. Finish sub-course 07 with additional cluster briefs, sequentially, per RESEARCH_PROTOCOL:
   - `07-database-internals/_research_transactions-recovery.md` for ARIES/WAL/redo/undo, MVCC,
     isolation, locking/deadlocks, 2PL/OCC, PostgreSQL/BusTub/InnoDB anchors.
   - `07-database-internals/_research_optimizer-external-exec.md` for Selinger/costing/cardinality,
     external sort, hash join variants, vectorized/compiled execution, and storage-model tradeoffs if
     needed.
   Use primary sources first; cite exact links per claim; keep briefs only.
4. Reconcile all 07 cluster briefs into `07-database-internals/_research.md` with the standard 6
   sections: key mechanisms, foundational sources, why-it's-this-way constraints, misconceptions,
   build-your-own targets, open questions/gaps.
5. Expand `meta/RESEARCH_INDEX.md` with genuinely new sources discovered for 07.
6. If time remains, start 08 caches-and-storage-systems with one source-cluster brief. Otherwise stop
   after 07 reconciliation. Do not start 10–12 or Phase 2.
7. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md` and `meta/NEXT_SESSION.md`,
   ensure files stay under 600 lines where reasonable, run `git status --short`, commit, and report
   remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
