# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.

Last updated: 2026-06-10 · Phase: 1 (deep research) · Harness: **code-puppy**

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
- **Phase 1 / Wave 3 / 07 database-internals — researched, factchecked, and reconciled.** Artifacts:
  - `07-database-internals/_research_storage-query-exec.md`
  - `07-database-internals/_research_transactions-recovery.md`
  - `07-database-internals/_research_optimizer-external-exec.md`
  - `07-database-internals/_factcheck_phase1.md`
  - `07-database-internals/_research.md`
- **Phase 1 / Wave 3 / 08 caches-and-storage-systems — researched, factchecked, and reconciled.** Artifacts:
  - `08-caches-and-storage-systems/_research_cache-eviction-consistency.md`
  - `08-caches-and-storage-systems/_research_memcached-internals.md`
  - `08-caches-and-storage-systems/_research_admission-dogpile-consistency.md`
  - `08-caches-and-storage-systems/_factcheck_phase1.md`
  - `08-caches-and-storage-systems/_research.md`
- **Phase 1 / Wave 3 / 09 message-queues-logs-and-kafka — researched, factchecked, and reconciled.** Artifacts:
  - `09-message-queues-logs-and-kafka/_research_log-abstraction-kafka-storage.md`
  - `09-message-queues-logs-and-kafka/_research_replication-availability.md`
  - `09-message-queues-logs-and-kafka/_research_consumer-groups-offsets.md`
  - `09-message-queues-logs-and-kafka/_research_delivery-semantics-transactions.md`
  - `09-message-queues-logs-and-kafka/_factcheck_phase1.md`
  - `09-message-queues-logs-and-kafka/_research.md`
- 09 factcheck blocker patched: Kafka 3.9 `LocalLog` source path is
  `core/src/main/scala/kafka/log/LocalLog.scala`, not trunk's later Java/storage path.
- **Phase 1 / Wave 4 / 10 nginx-proxies-and-load-balancing — started only.** One starter cluster exists:
  - `10-nginx-proxies-and-load-balancing/_research_event-driven-reverse-proxy.md`
- `meta/RESEARCH_INDEX.md` has Wave 3/4 additions for 09 Kafka and starter 10 NGINX sources.

---

## Things LEFT / current gaps

- **Do not start chapters. Do not start Phase 2.** Phase 1 research corpus is still incomplete.
- **09 residual gaps:** replace mirrored Kafka paper URL with canonical primary source if accessible; read
  KIP-101, KIP-497, KIP-500/KRaft, KIP-848, and KIP-360 directly before quoting rationale; trace KRaft
  eligible-leader-replica behavior, preferred-replica election, fetch-from-follower routing, coordinator runtime,
  offset expiration, sticky assignor/static membership, transaction marker retry, `__transaction_state` expiry, and
  long-open-transaction/log-cleaner interactions before Phase 2 prose.
- **10 current state:** starter only; not factchecked or reconciled. Sources are mostly NGINX `master`, so pin to a
  release tag/commit before final prose.
- **10 gaps for next session:** factcheck the starter, deepen with load-balancing/peer selection source cluster,
  deepen with proxy buffering/timeouts/retries/failure behavior source cluster, optionally TLS/HTTP2/HTTP3 only if
  time remains, then reconcile 10 if coverage is solid.
- **11 and 12 remain untouched.** Do not start them unless 10 is cleanly factchecked/reconciled and there is enough
  time for one careful starter cluster.

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
- that 07, 08, and 09 are reconciled/factchecked,
- that 10 has exactly one starter cluster and is not factchecked/reconciled,
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
  - 10 nginx-proxies-and-load-balancing has exactly one starter brief:
    `10-nginx-proxies-and-load-balancing/_research_event-driven-reverse-proxy.md`.
  - 10 is not factchecked or reconciled yet.
  - 11 and 12 are untouched.

Run this plan, but only do as much as can be completed well in one session. Do not rush or half-bake research just
to finish the whole list.

1. Check `git status --short`. If not clean, inspect exactly what changed before editing.
2. Factcheck 10 starter:
   - Spot-check NGINX event-driven architecture, master/worker, `ngx_process_events_and_timers`, epoll dispatch,
     accept mutex/backoff, HTTP request state, upstream reverse-proxy path, and upstream keepalive claims.
   - Patch blockers before adding more 10 material.
3. Deepen 10 with sequential source-cluster briefs:
   1. Load-balancing and peer selection: round-robin, weighted round-robin, least_conn, ip_hash/hash/consistent hash,
      upstream zones/shared state, health/failure accounting, `max_fails`, `fail_timeout`, slow_start if available.
   2. Proxy buffering, retries, timeouts, and backpressure: request/response buffering, temp files, `proxy_next_upstream`,
      connect/read/send timeouts, streaming vs buffering, client slow-read behavior.
   3. If time permits only: TLS termination and HTTP/2/HTTP/3 request multiplexing caveats.
4. Run/ask factchecker to spot-check the most load-bearing 10 claims. Patch blockers.
5. If enough time remains and 10 coverage is solid, reconcile all 10 cluster briefs into
   `10-nginx-proxies-and-load-balancing/_research.md` with the standard six sections:
   key mechanisms, foundational sources, why-it’s-this-way constraints, misconceptions, build-your-own targets,
   open questions/gaps.
6. Expand `meta/RESEARCH_INDEX.md` with genuinely new 10 sources discovered.
7. If, and only if, 10 is reconciled cleanly with no blockers and time remains, start 11 distributed-systems-foundations
   with one source-cluster brief. Otherwise stop after the best clean 10 checkpoint. Do not start 12 or Phase 2.
8. End cleanly: append `meta/SESSION_LOG.md`, update `meta/PROGRESS.md`, update `meta/NEXT_SESSION.md` with the exact
   next-session prompt, ensure files stay under 600 lines where reasonable, run `git status --short`, commit, and
   report remaining gaps + next batch.

No chapters. No Phase 2. No hand-waving. Cite the source or mark it `[UNVERIFIED]`.
```
