# 28 · build-your-own-coding-harness — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 28 is the **Part III CAPSTONE LAB**: it
> assembles the entire agentic arc into ONE running coding harness. Load-bearing method: a **BUILD
> PROGRESSION** — grow the "40-line agent" stage by stage, **breaking it on purpose** at each stage
> so the next primitive is motivated by an observed failure (22→23→24→25→26→27→32). NO new
> load-bearing primary (applies the line-verified 22-27 + Part I/II toolkit, like 21). Full depth:
> `_research_build-your-own-coding-harness.md`. Math: `_recompute.py` (31/31). Factcheck:
> `_factcheck_phase1.md` (0 blockers).

## 1. The one idea
**A coding harness = the agent loop (22) + code-aware tools (23), under a context budget (24),
backed by memory (25), made durable (26), optionally parallelized (27), bounded by a cost/step/time
budget (32).** Nothing more. Every "magic" feature of a real coding agent (Code Puppy / Claude Code
/ Aider / Codex CLI) decomposes into exactly one of those seven primitives. 28 proves this **by
construction**: you reach a genuinely useful coding agent in a few hundred lines iff you add the
primitives in dependency order, each paying for itself by fixing the wall the previous stage hit.

The forcing function is **22's O(T²) input-token cost** (`T*p + g*T*(T-1)/2`). Coding has *long*
transcripts (big files, verbose test/compiler logs, many edit-test-fix steps), so the quadratic
bites **sooner and harder** here than in chat (recomputed: window overflow at T*=83 for coding vs
253 for chat). That single economic fact is why a coding harness needs compaction (24), memory (25),
and an explicit budget (32) more urgently than any other agent class.

## 2. The build progression (the bespoke spine — the diagonal IS the point)
Each row's **wall** is the next row's reason to exist (all walls RECOMPUTED in the coding regime):

| Stage | Add | Reuses | Wall it hits (recomputed) | Demands |
|------|-----|--------|----------------------------|---------|
| 0 | 40-line loop | 22 | O(T²); window overflow at T*=83 | tools, compaction |
| 1 | code tools + test-runner | 23 | selection compounding 1-(1-q)^N; 1MB file overflows budget; `run_shell` = ACE hole; toolbox tax K·S | budget, compaction, sandbox |
| 2 | step/$/time budget | 22·18·32 | caps cost ($1.275 worst-case) but **doesn't cure** the quadratic | compaction |
| 3 | context + compaction | 24 | **O(T²)→O(T)** (win grows unbounded) **but lossy + volatile** | memory |
| 4 | scratchpad + store | 25 | AMAT (hit 0.80→0.95 = 4× cheaper); poisoning blast radius (1 write→15 reads); volatile on crash | persistence |
| 5 | WAL + resume | 26 | I*=√(2N·c)=20; idempotent replay (no double-applied edit); **but strictly serial** | orchestration (if decomposable) |
| 6 | supervisor + workers | 27 | Amdahl ceiling 5×; join tail 63.4%@N=100; aggregation tax; **multi-agent LOSES on small tasks (YAGNI)** | (done) |

Stage 1's **test-runner** is what makes it a *coding* agent: it closes a ReAct loop (22) where the
*observation is a compiler/test result* — acting grounds reasoning (Toolformer "incorporate the
result", 23-verified). Stage 6's YAGNI lesson is *watched, not asserted*: show a 10-file refactor
where multi-agent wins, then a 1-file fix where a single loop beats it.

## 3. The minimal durable set (reuse 26 §4)
Transcript/WAL (source of truth) · compacted context + memory pointers (24/25) · cursor/step index
(09 LSN) · idempotency keys + commit status per world-changing tool call (17) · pending tool calls/
outbox (17) · budgets consumed: steps/$/wall-clock (22/32) · working set (open files, plan).
**Not** persisted: anything re-derivable by replaying the WAL.

## 4. The security boundary (Stage 1 onward — the most dangerous agent class)
A coding harness runs **arbitrary code** and **edits the filesystem**. Boundary (23 security → 33):
command allowlist; sandbox/container the workspace (jail, no network unless granted); confirm/
dry-run destructive ops; **never trust tool output as instructions** (prompt-injection-via-tool-
result → 33); cap per-call CPU/mem/time (18 + 20 bulkhead). The harness's blast radius = the union
of its tools' blast radii.

## 5. Failure modes (all decompose to a prior primitive)
Window overflow (24 compaction) · runaway cost/loop (22/32 budget) · wrong tool pick compounding
(23/31 verifier) · huge result overflow (23/24/25) · ACE/injection (23/33 sandbox) · lossy
compaction (25 externalize) · poisoned memory (25/33 validate writes) · crash mid-fix (26 WAL+
idempotency) · double-applied edit on resume (17/26 keys) · join stall (20/27 deadline+partial) ·
aggregation overflow (24/27 compact returns) · over-orchestration (27 YAGNI). **Every harness bug
is a known systems bug wearing a coding-agent costume.**

## 6. Build-your-own (the capstone deliverable)
Grow ONE program through the 7 stages. Acceptance per stage = **demonstrate the wall, then the fix**
(overflow→compaction; kill-mid-patch→clean resume; 10-file refactor wins→1-file fix loses). Final
artifact: a real bounded, resumable, tool-using coding agent — the `/build` capstone
**own-coding-agent-harness** — plus a learner who can name which primitive each feature is and why.

## 7. Provenance summary
- **NO new primary** (capstone application, like 21). Every mechanism CROSS-LINKS to a VERIFIED
  anchor: ReAct (22), Toolformer (23), CoT (24), MemGPT/Reflexion (25), Postgres-WAL (26),
  recomputed coordination math (27).
- **RECOMPUTED:** `_recompute.py` (31/31) — all 7 stage walls re-derived in the coding regime.
- **REUSED:** 09, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27 (+ Appendix I sandbox, deferred).
- **`[UNVERIFIED]` carry-forward:** coding-agent implementations (Claude Code/Aider/Codex CLI/
  SWE-agent/Cursor/Code Puppy) as design references; **SWE-bench (arXiv 2310.06770)** as the
  "useful" benchmark (→31); sandbox/ACE specifics (→Appendix I); injection-via-tool-result +
  memory-poisoning mitigations (→33). None load-bearing for the build progression.

---
**28 reconciled.** Part III "Phase 1 batch 3" now stands at **22-28 reconciled** (7 of 13 agentic
sub-courses). Next in dependency order: **29-mcp-skills-and-connectors** (FETCH the MCP spec from
modelcontextprotocol.io; ↔ 23 tool contracts + 03 transport), then 30 RAG (fetch Lewis 2020,
arXiv 2005.11401), 31 eval, as far as one clean checkpoint allows.
