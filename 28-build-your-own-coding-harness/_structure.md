# 28 — Build Your Own Coding Harness · _structure.md

**Identity:** the Part III CAPSTONE LAB. It assembles the entire agentic arc into ONE running coding
harness and proves BY CONSTRUCTION that a coding agent = the agent loop (22) + code-aware tools (23),
under a context budget (24), backed by memory (25), made durable (26), optionally parallelized (27),
bounded by a cost/step/time budget (32). Nothing more.

**Bespoke shape — "a build progression where the diagonal IS the point: each stage's WALL is the next
stage's reason to exist."** NOT a feature checklist. Grow the "40-line agent" stage by stage, BREAKING
IT ON PURPOSE at each stage so the next primitive is motivated by an OBSERVED failure (22→23→24→25→26
→27→32). The forcing function is 22's O(T²) — and coding has LONG transcripts (big files, verbose
test/compiler logs, many edit-test-fix steps), so the quadratic bites sooner and harder here (overflow
at T*=83 for coding vs 253 for chat). That single economic fact is why a coding harness needs
compaction/memory/budget more urgently than any other agent class. NO new primary (applies verified
22–27, like 21). Math recomputed (31/31). The `/build` capstone: **own-coding-agent-harness.**

## Dependency position
- **Depends on:** ALL of 22–27 (each stage IS one of them) + 09/17/18/20/21 (the systems primitives they
  reuse) + appendix I (sandbox, deferred). This is the synthesis course — it introduces nothing new.
- **Feeds into:** 29 (MCP as the tool transport for a real harness), 31 (SWE-bench = the "useful"
  benchmark), 32 (the explicit budget stage), 33 (the security boundary — most dangerous agent class),
  34 (design-your-own — generalize the progression beyond coding).
- **Appendix links DOWN:** I-sandboxing (the ACE/arbitrary-code boundary), M-agentic-papers (the anchors
  each stage cross-links to), F-postgres (WAL for the resume stage). 28 owns the build progression itself.

## Section specs (3–5 lines each)
1. **The one idea: a coding harness is seven primitives, nothing more** — every "magic" feature of a real
   coding agent (Code Puppy / Claude Code / Aider / Codex CLI) decomposes into exactly one of: loop (22),
   tools (23), context budget (24), memory (25), durability (26), orchestration (27), cost/step/time
   budget (32). 28 proves this by reaching a genuinely useful coding agent in a few hundred lines iff you
   add the primitives in dependency order, each paying for itself by fixing the previous stage's wall.
2. **Why coding hits the quadratic hardest** — 22's O(T²) (`T·p + g·T(T−1)/2`) with LONG coding
   transcripts (big files, verbose logs, many edit-test-fix steps) → overflow at T*=83 (coding) vs 253
   (chat). This is the economic reason a coding harness needs compaction (24), memory (25), and an
   explicit budget (32) more urgently than any other agent class.
3. **The build progression (the bespoke spine — the diagonal IS the point)** — each row's WALL is the
   next row's reason to exist (all walls RECOMPUTED in the coding regime):
   - **Stage 0** — 40-line loop (22): wall = O(T²), overflow at T*=83 → demands tools + compaction.
   - **Stage 1** — code tools + test-runner (23): wall = selection compounding 1−(1−q)^N + 1MB file
     overflows budget + `run_shell` = ACE hole + toolbox tax K·S → demands budget + compaction + sandbox.
     The test-runner is what makes it a CODING agent: it closes a ReAct loop where the observation is a
     compiler/test result (acting grounds reasoning — Toolformer "incorporate the result").
   - **Stage 2** — step/$/time budget (22·18·32): caps cost ($1.275 worst-case) but DOESN'T cure the
     quadratic → demands compaction.
   - **Stage 3** — context + compaction (24): O(T²)→O(T) (win grows unbounded) BUT lossy + volatile →
     demands memory.
   - **Stage 4** — scratchpad + store (25): AMAT (hit 0.80→0.95 = 4× cheaper) + poisoning blast radius
     (1 write→15 reads) + volatile on crash → demands persistence.
   - **Stage 5** — WAL + resume (26): I*=√(2N·c)=20 + idempotent replay (no double-applied edit) BUT
     strictly serial → demands orchestration (if decomposable).
   - **Stage 6** — supervisor + workers (27): Amdahl ceiling 5× + join tail 63.4%@N=100 + aggregation
     tax + multi-agent LOSES on small tasks (YAGNI, watched not asserted: 10-file refactor wins, 1-file
     fix loses).
4. **The minimal durable set (reuse 26 §4)** — transcript/WAL (source of truth) · compacted context +
   memory pointers (24/25) · cursor/step index (09 LSN) · idempotency keys + commit status per
   world-changing tool call (17) · pending tool calls/outbox (17) · budgets consumed: steps/$/wall-clock
   (22/32) · working set (open files, plan). NOT persisted: anything re-derivable by replaying the WAL.
5. **The security boundary (Stage 1 onward — the most dangerous agent class)** — a coding harness runs
   ARBITRARY CODE and EDITS THE FILESYSTEM. Boundary (23 security → 33): command allowlist; sandbox/
   container the workspace (jail, no network unless granted); confirm/dry-run destructive ops; NEVER
   trust tool output as instructions (injection-via-tool-result → 33); cap per-call CPU/mem/time
   (18 + 20 bulkhead). The harness's blast radius = the union of its tools' blast radii.
6. **Failure modes (every one decomposes to a prior primitive)** — window overflow (24) · runaway cost/
   loop (22/32) · wrong-tool compounding (23/31) · huge result overflow (23/24/25) · ACE/injection
   (23/33) · lossy compaction (25) · poisoned memory (25/33) · crash mid-fix (26) · double-applied edit
   on resume (17/26) · join stall (20/27) · aggregation overflow (24/27) · over-orchestration (27 YAGNI).
   Every harness bug is a known systems bug wearing a coding-agent costume.

## Paired build lab (/build → own-coding-agent-harness — THE Part III deliverable)
Grow ONE program through the 7 stages. Acceptance per stage = DEMONSTRATE THE WALL, THEN THE FIX
(overflow→compaction; kill-mid-patch→clean resume; 10-file refactor wins→1-file fix loses). Final
artifact: a real bounded, resumable, tool-using coding agent — plus a learner who can NAME which
primitive each feature is and WHY it's there.

## Diagrams needed
- The 7-stage build progression as a diagonal: each stage's wall → next stage's primitive.
- The "everything decomposes to 7 primitives" map (real-agent feature → which primitive).
- Coding vs chat quadratic (overflow at T*=83 vs 253) — why coding bites hardest.
- Stage 1 test-runner closing a ReAct loop (observation = compiler/test result).
- The minimal durable set (persist vs re-derivable).
- The security boundary (arbitrary code + FS edits; allowlist/sandbox/confirm/cap; blast-radius union).
- Failure-mode map: each harness bug → the prior primitive that fixes it.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **NO new primary** (capstone application, like 21). Every mechanism CROSS-LINKS to a VERIFIED anchor:
  ReAct (22), Toolformer (23), CoT (24), MemGPT/Reflexion (25), Postgres-WAL (26), recomputed
  coordination math (27).
- **RECOMPUTED (31/31):** all 7 stage walls re-derived in the coding regime (overflow T*=83, selection
  compounding, $1.275 worst-case, O(T²)→O(T), AMAT 4×, poisoning 1→15, I*=20, Amdahl 5×, join 63.4%).
- **`[UNVERIFIED]` carry-forward (none load-bearing for the build progression):** coding-agent
  implementations (Claude Code/Aider/Codex CLI/SWE-agent/Cursor/Code Puppy) as design references;
  SWE-bench (arXiv 2310.06770) as the "useful" benchmark (→31); sandbox/ACE specifics (→appendix I);
  injection-via-tool-result + memory-poisoning mitigations (→33). Teach the progression now; do NOT
  harden implementation/benchmark specifics until fetched.
- **Boundary discipline:** each stage's depth lives in its home sub-course (22–27, 32); sandbox → appendix
  I; benchmark → 31; safety mitigations → 33. 28 owns ONLY the build progression + the "it's all seven
  primitives" proof-by-construction.
