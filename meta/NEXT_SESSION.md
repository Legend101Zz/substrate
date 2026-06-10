# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 (12 reconciled — ALL foundations 01-12 done) · Phase: 1 (deep research) · Harness: **code-puppy**

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
- **Phase 1 / Wave 4 / 11 distributed-systems-foundations — FOUR clusters drafted/factchecked AND reconciled.**
  Artifacts:
  - `11-distributed-systems-foundations/_research_time-clocks-ordering-failure.md` + `_factcheck_phase1.md`
  - `11-distributed-systems-foundations/_research_vector-clocks-model-taxonomy.md` + `_factcheck_cluster2.md`
  - `11-distributed-systems-foundations/_research_consistency-replication-quorums.md` + `_factcheck_cluster3.md`
  - `11-distributed-systems-foundations/_research_cap-partitions-distributed-commit.md` + `_factcheck_cluster4.md`
  - `11-distributed-systems-foundations/_research.md` (RECONCILED, six sections)
- 11 cluster 4 fetched a NEW primary (Gray & Lamport "Consensus on Transaction Commit", TODS 2006) from
  `lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf` and verified 14 load-bearing 2PC/3PC/Paxos-
  Commit/Spanner claims with line receipts (0 blockers). CAP/PACELC primaries (Gilbert/Lynch, Brewer, Abadi) were
  network-blocked and stay `[UNVERIFIED from fetched source]`; Herlihy/Wing + Dynamo also still blocked.
- **Phase 1 / Wave 4 / 12 research-papers-for-engineers — TWO clusters drafted/factchecked AND reconciled.**
  Artifacts:
  - `12-research-papers-for-engineers/_research_how-to-read-a-paper.md` (reading method; verified Lamport "State the
    Problem" backbone; Keshav three-pass `[UNVERIFIED]`)
  - `12-research-papers-for-engineers/_research_paper-canon-walkthroughs.md` (canon catalog; 4 fresh-verified Lamport
    primaries + reuse of 06-11 receipts + blocked storage/ops canon flagged)
  - `12-research-papers-for-engineers/_factcheck_phase1.md` (Cluster A 4 VERIFIED + 2 flagged; Cluster B 9 VERIFIED +
    2 flagged; 0 blockers)
  - `12-research-papers-for-engineers/_research.md` (RECONCILED, six sections)
- 12 fetched FOUR new primaries from `lamport.azurewebsites.net/pubs/`: "State the Problem Before Describing the
  Solution", "The Byzantine Generals Problem" (TOPLAS 1982), "Reaching Agreement in the Presence of Faults" (JACM 1980),
  and "The Part-Time Parliament" (original Paxos, TOCS 1998). Verified `3m+1`/`>2/3`-loyal, conditions A/B,
  impossibility-then-`OM(m)`, interactive consistency, the state-machine approach, and the editor's-note exposition
  exemplar. Keshav + the Google storage trilogy (MapReduce/GFS/Bigtable/Dynamo) + Dapper/Tail-at-Scale stay
  `[UNVERIFIED from fetched source]` (network-blocked). **ALL foundations 01-12 now reconciled/factchecked.**

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **10 residual gaps:** reverify exact nginx.org wording before Phase 2 prose; trace `reuseport`/`EPOLLEXCLUSIVE`
  operational interaction, `ngx_thread_pool.c`, full HTTP phase engine, `X-Accel-Buffering`, cache-specific proxy paths,
  TLS termination/OpenSSL, HTTP/2 stream multiplexing/flow control, HTTP/3/QUIC, and commercial/open-source boundaries
  for `slow_start`, active health checks, sticky, queue, random, least_time, and dynamic membership.
- **11 distributed-systems-foundations is reconciled.** Four clusters factchecked and synthesized into `_research.md`.
  Remaining 11 carry-forward gaps (do NOT erase; fetch before Phase 2 prose): CAP/PACELC primaries (Gilbert/Lynch 2002,
  Brewer 2000/2012, Abadi 2012), Herlihy/Wing TOPLAS 1990 object-level linearizability, Dynamo SOSP 2007,
  Fidge/Mattern/Charron-Bost/CBCAST + DLS/JACM 1988, Skeen 1981 original 3PC, Berenson 1995 ANSI isolation levels,
  cleaner Chandra-Toueg text, source pin for the `f+1` synchronous rotating-coordinator claim, and re-pin Gray &
  Lamport to ACM TODS 2006 pagination.
- **12 research-papers-for-engineers is reconciled.** Two clusters (reading-method + canon-walkthroughs) factchecked
  and synthesized into `_research.md`. Carry-forward 12 gaps (do NOT erase; fetch before Phase 2 prose): Keshav "How to
  Read a Paper" CCR 2007 + Roscoe/Mitzenmacher/Smith reviewing guidance; the storage trilogy MapReduce/GFS/Bigtable/
  Dynamo; ops classics Dapper/Tail-at-Scale/Chubby/ZooKeeper; method cross-cuts Herlihy/Wing, Saltzer/Reed/Clark
  End-to-End, Lampson "Hints"; and re-pin Byzantine/Reaching-Agreement pagination to the ACM record.
- **ALL foundations 01-12 are now research-complete** (reconciled `_research.md` + factcheck artifacts each), subject to
  the logged `[UNVERIFIED]` gaps. The next Phase-1 batch is Part II System Design (13-21).

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
meta/SESSION_LOG.md, meta/DECISIONS.md, and meta/NEXT_SESSION.md. Confirm in 3-4 lines:
- current Phase 1 state,
- Wave 2 milestone `4a1cc71`,
- current checkpoint commit from `git rev-parse --short HEAD`,
- that ALL foundations 01-12 are reconciled/factchecked (Part I research-complete),
- that 12 has TWO factchecked clusters and a reconciled `_research.md`,
- that Part II System Design (13-21) is the next batch and is untouched,
- and the exact plan you will run.

Do not touch `/Users/m0t0hu6/.code-puppy-venv`. If `os.getcwd()` / `Path.cwd()` PermissionError recurs,
stop and tell me to grant Desktop/OneDrive access or move the repo to a non-OneDrive workspace. Do not reinstall
Code Puppy.

Current state to preserve (do NOT erase logged `[UNVERIFIED]`/residual gaps):
- Foundations 01-12 each have reconciled `_research.md` + factcheck artifacts. 12 has
  `_research_how-to-read-a-paper.md` + `_research_paper-canon-walkthroughs.md` + `_factcheck_phase1.md` + reconciled
  `_research.md`. Four Lamport primaries were verified for 12 (State-the-Problem, Byzantine Generals, Reaching
  Agreement, Part-Time Parliament).
- Network reality (3 sessions running): only `lamport.azurewebsites.net` resolves; academic/ACM/arXiv/raw.github =
  HTTP 000. Carried-forward blocked primaries to fetch when the network is healthier:
  - 12: Keshav "How to Read a Paper" CCR 2007 (+ Roscoe/Mitzenmacher/Smith); MapReduce/GFS/Bigtable/Dynamo;
    Dapper/Tail-at-Scale/Chubby/ZooKeeper; Herlihy/Wing, Saltzer/Reed/Clark End-to-End, Lampson "Hints".
  - 11: CAP/PACELC (Gilbert/Lynch 2002, Brewer 2000/2012, Abadi 2012), Herlihy/Wing TOPLAS 1990, Dynamo SOSP 2007,
    Fidge/Mattern/Charron-Bost/CBCAST/DLS, Skeen 1981 3PC, Berenson 1995 ANSI isolation, cleaner Chandra-Toueg.
  - 10: nginx.org wording recheck, reuseport/EPOLLEXCLUSIVE, thread pools, HTTP phase engine, TLS/HTTP2/HTTP3.

Run this plan, but only as much as can be completed well in one session. Prefer one clean factchecked checkpoint over
multiple shallow briefs.

1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. Start Part II System Design (Phase 1 research briefs ONLY - no chapters, no Phase 2), beginning with
   13-scaling-fundamentals. Begin with ONE tightly-scoped source cluster, e.g.:
   - Cluster A - back-of-envelope + latency: Dean "Latency Numbers Every Programmer Should Know", Little's Law /
     queueing basics, Drepper "What Every Programmer Should Know About Memory". Reuse the canon already verified in
     06-12 where it overlaps. Prefer primary sources; fetch via `curl`; mark anything unfetched `[UNVERIFIED]`.
3. Factcheck the new cluster's load-bearing claims against primary sources. Patch blockers.
4. If coverage is honest, reconcile into `13-scaling-fundamentals/_research.md` (standard six sections), preserving
   every logged `[UNVERIFIED]`/residual gap. If coverage is thin or a blocker can't clear, stop at a clean cluster
   checkpoint; do not fake completeness (raccoon-shaped docs are forbidden).
5. Opportunistic: if the network is healthier, fetch the carried-forward blocked 11 + 12 primaries above and upgrade
   the corresponding `[UNVERIFIED]` flags to verified, updating the relevant cluster + factcheck files.
6. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md`, update `meta/NEXT_SESSION.md` with the exact
   next-session prompt, keep files under 600 lines where reasonable, run `git status --short`, commit, and report
   remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
