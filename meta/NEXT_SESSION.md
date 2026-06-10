# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 (cluster 3 added) · Phase: 1 (deep research) · Harness: **code-puppy**

---

## Code Puppy recovery note (still relevant)

Start from the shorter Desktop path first:

```bash
cd /Users/m0t0hu6/Desktop/substrate
pwd
uvx code-puppy -i
```

Physical path may resolve through OneDrive:
`/Users/m0t0hu6/Library/CloudStorage/OneDrive-WalmartInc/Desktop/substrate`.

If `os.getcwd()` / `Path.cwd()` raises:

```text
PermissionError: [Errno 1] Operation not permitted
```

then **do not** edit or reinstall anything under `/Users/m0t0hu6/.code-puppy-venv`. Stop and tell the
user to grant the terminal/Code Puppy process Desktop/OneDrive access in macOS Privacy settings, or copy the repo
to a non-OneDrive workspace and continue there.

---

## Things DONE

- **Phase 0** — scaffold + constitution files + subagent personas + living-state files; git initialized.
- **Phase 1 / Wave 1 — 01, 02, 03 researched and reconciled.** Factcheck report
  `meta/factcheck_wave1_01-03.md` exists; fixes were applied in milestone commit `4a1cc71`. Residual gaps remain
  logged and must not be erased.
- **Phase 1 / Wave 2 — 04, 05, 06 researched, reconciled, and factchecked.** Factcheck report
  `meta/factcheck_wave2_04-06.md` exists; blockers were patched in milestone commit `4a1cc71`. Residual gaps remain
  logged.
- **Phase 1 / Wave 3 — 07, 08, and 09 researched, factchecked, and reconciled.** Artifacts include each sub-course's
  cluster briefs, `_factcheck_phase1.md`, and `_research.md`.
- **Phase 1 / Wave 4 / 10 nginx-proxies-and-load-balancing — core coverage researched, factchecked, and reconciled.**
  Artifacts:
  - `10-nginx-proxies-and-load-balancing/_research_event-driven-reverse-proxy.md`
  - `10-nginx-proxies-and-load-balancing/_research_load-balancing-peer-selection.md`
  - `10-nginx-proxies-and-load-balancing/_research_proxy-buffering-retries-timeouts.md`
  - `10-nginx-proxies-and-load-balancing/_factcheck_phase1.md`
  - `10-nginx-proxies-and-load-balancing/_research.md`
- 10 factcheck checked 43 load-bearing claims against NGINX `release-1.31.1` source. No unsupported claims remain.
  BRAIN patches applied after factcheck: release-pinned remaining URLs, added `ngx_posted_next_events` event-loop step,
  and annotated nginx.org doc-wording caveats.
- `meta/RESEARCH_INDEX.md` now includes verified 10 NGINX source anchors and residual 10 gaps.
- **Phase 1 / Wave 4 / 11 distributed-systems-foundations — three clusters drafted/factchecked, not reconciled.**
  Artifacts:
  - `11-distributed-systems-foundations/_research_time-clocks-ordering-failure.md`
  - `11-distributed-systems-foundations/_factcheck_phase1.md`
  - `11-distributed-systems-foundations/_research_vector-clocks-model-taxonomy.md`
  - `11-distributed-systems-foundations/_factcheck_cluster2.md`
  - `11-distributed-systems-foundations/_research_consistency-replication-quorums.md`
  - `11-distributed-systems-foundations/_factcheck_cluster3.md`
- 11 starter factcheck checked 22 load-bearing claims against Lamport 1978, Chandy-Lamport 1985, FLP/JACM 1985,
  Spanner OSDI 2012, and Chandra-Toueg JACM 1996 PostScript. Cluster 2 factcheck checked vector-clock/model-taxonomy
  claims; two blockers were patched. Cluster 3 factcheck verified 13 load-bearing claims against Lamport sequential
  consistency (IEEE TC 1979), Paxos Made Simple, Raft USENIX ATC 2014, and Spanner OSDI 2012 with exact line receipts;
  0 blockers, 2 citation line-drifts patched. Carry-forward warnings: Herlihy/Wing, Dynamo, and MIT 6.5840 notes were
  network-blocked and stay `[UNVERIFIED from fetched source]`; the f+1 synchronous rotating-coordinator claim still
  needs a source pin; Chandra-Toueg exact definitions need cleaner text.

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **10 residual gaps:** reverify exact nginx.org wording before Phase 2 prose; trace `reuseport`/`EPOLLEXCLUSIVE`
  operational interaction, `ngx_thread_pool.c`, full HTTP phase engine, `X-Accel-Buffering`, cache-specific proxy paths,
  TLS termination/OpenSSL, HTTP/2 stream multiplexing/flow control, HTTP/3/QUIC, and commercial/open-source boundaries
  for `slow_start`, active health checks, sticky, queue, random, least_time, and dynamic membership.
- **11 distributed-systems-foundations is started but not reconciled.** Three clusters are factchecked: time/clocks/
  global state/partial failure, vector clocks/model taxonomy, and consistency/replication/quorums/Paxos-Raft.
  Remaining 11 gaps before reconciliation: CAP/partitions (PACELC), distributed commit/transactions (2PC/3PC
  blocking, isolation levels), cleaner Chandra-Toueg text, and direct blocked primary text for Herlihy/Wing, Dynamo,
  Fidge/Mattern/DLS/CBCAST.
- **12 research-papers-for-engineers is untouched.** Do not start 12 until 11 has a clean reconciled checkpoint.

---

## Running this project in code-puppy

- Start from `/Users/m0t0hu6/Desktop/substrate`.
- Rehydrate first from `AGENTS.md`, `START_HERE.md`, `meta/CONSTITUTION.md`, `meta/RESEARCH_PROTOCOL.md`,
  `meta/COURSE_MAP.md`, `meta/RESEARCH_INDEX.md`, `meta/PROGRESS.md`, `meta/SESSION_LOG.md`,
  `meta/DECISIONS.md`, and this file. Do not guess.
- Use tools, not vibes. Read files before modifying them. Keep diffs small.
- No parallel sub-agents in this harness. Switch agents sequentially or use multiple terminals.
- Phase 1 = research briefs only. No chapter prose.
- Validate source claims before accepting them. Primary sources first. `[UNVERIFIED]` is allowed in briefs but must
  not harden into course prose.
- End every session: append `SESSION_LOG.md`, update `PROGRESS.md` and `NEXT_SESSION.md`, run status, and commit.

---

## PROMPT TO RUN NEXT

```text
You are the BRAIN agent for the Substrate course project. Start safely from
`/Users/m0t0hu6/Desktop/substrate`. Read AGENTS.md, START_HERE.md, meta/CONSTITUTION.md,
meta/RESEARCH_PROTOCOL.md, meta/COURSE_MAP.md, meta/RESEARCH_INDEX.md, meta/PROGRESS.md,
meta/SESSION_LOG.md, meta/DECISIONS.md, and meta/NEXT_SESSION.md. Confirm in 3–4 lines:
- current Phase 1 state,
- Wave 2 milestone `4a1cc71`,
- current checkpoint commit from `git rev-parse --short HEAD`,
- that 07, 08, 09, and 10 are reconciled/factchecked,
- that 11 has three factchecked clusters but is not reconciled,
- that 12 is untouched,
- and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError recurs,
stop and tell me to grant Desktop/OneDrive access or move the repo to a non-OneDrive workspace. Do not reinstall
Code Puppy.

Current state to preserve:
- Wave 1 (01–03): research + reconciled briefs done; factcheck report `meta/factcheck_wave1_01-03.md` exists and
  fixes were applied in commit `4a1cc71`. Residual gaps are logged; do not erase them.
- Wave 2 (04–06): research + reconciled briefs + factcheck report `meta/factcheck_wave2_04-06.md` done in commit
  `4a1cc71`. Residual gaps are logged.
- Wave 3:
  - 07 database-internals has three cluster briefs, `07-database-internals/_factcheck_phase1.md`, and reconciled
    `07-database-internals/_research.md`.
  - 08 caches-and-storage-systems has three cluster briefs, `08-caches-and-storage-systems/_factcheck_phase1.md`,
    and reconciled `08-caches-and-storage-systems/_research.md`.
  - 09 message-queues-logs-and-kafka has four cluster briefs, `09-message-queues-logs-and-kafka/_factcheck_phase1.md`,
    and reconciled `09-message-queues-logs-and-kafka/_research.md`.
- Wave 4:
  - 10 nginx-proxies-and-load-balancing has three core cluster briefs, `_factcheck_phase1.md`, and reconciled
    `_research.md`. Residual TLS/HTTP2/HTTP3/reuseport/docs wording gaps are logged; do not erase them.
  - 11 distributed-systems-foundations has three factchecked clusters:
    `11-distributed-systems-foundations/_research_time-clocks-ordering-failure.md` + `_factcheck_phase1.md`,
    `11-distributed-systems-foundations/_research_vector-clocks-model-taxonomy.md` + `_factcheck_cluster2.md`, and
    `11-distributed-systems-foundations/_research_consistency-replication-quorums.md` + `_factcheck_cluster3.md`.
    It is not reconciled into `_research.md`. Residual gaps are logged; do not erase them.
  - 12 research-papers-for-engineers is untouched.

Run this plan, but only do as much as can be completed well in one session. Prefer one clean, factchecked checkpoint
over multiple shallow briefs.

1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. Continue 11 distributed-systems-foundations with the next source cluster.
   - **Preferred: CAP/partitions + distributed commit/transactions.** Cover the CAP theorem and its partition
     trade-off, PACELC, two-phase commit and its blocking failure mode, three-phase commit, and transaction isolation
     levels where they intersect with replication/consistency. Primary sources to prioritize: Gilbert/Lynch CAP proof,
     Brewer's CAP retrospective, Abadi PACELC, Gray/Lamport or Bernstein/Hadzilacos/Goodman for 2PC/3PC, and
     Spanner/Dynamo sections already partly fetched. Try again to fetch Herlihy/Wing and Dynamo primaries to close the
     `[UNVERIFIED]` gaps from clusters 2 and 3.
3. Factcheck the new 11 cluster's load-bearing claims against primary sources. Patch blockers.
4. After CAP/distributed-commit is clean, 11 should have enough coverage: reconcile all cluster briefs into
   `11-distributed-systems-foundations/_research.md` with the standard six sections, preserving every logged
   `[UNVERIFIED]`/residual gap. If coverage still feels thin or a blocker cannot be cleared, stop at another clean
   cluster checkpoint; do not fake completeness. Sneaky fake completeness is how documentation gets raccoon-shaped.
5. Only after 11 is reconciled cleanly and there is meaningful time left, you may begin 12 research-papers-for-engineers
   (Phase 1 briefs only). Do not start Phase 2.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md`, update `meta/NEXT_SESSION.md` with the exact
   next-session prompt, ensure files stay under 600 lines where reasonable, run `git status --short`, commit, and
   report remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
