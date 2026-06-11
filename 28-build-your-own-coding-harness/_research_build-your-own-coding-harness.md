# 28 · build-your-own-coding-harness — research brief (Phase 1, briefs only)

> Bespoke structure: a **BUILD PROGRESSION**, NOT abstract source clusters and NOT the 13-20
> four-cluster shape. The sub-course is the Part III CAPSTONE LAB: it grows a single program — the
> "40-line agent" — stage by stage, **breaking it on purpose at the end of each stage** so the next
> primitive (22→23→24→25→26→27→32) is *motivated by a failure the learner just watched happen*,
> not asserted. No new load-bearing primary: 28 APPLIES the line-verified Part I/II + 22-27 canon
> (the same discipline as 21, the Part II capstone). Math: `_recompute.py`. Factcheck:
> `_factcheck_phase1.md`.

---

## 0. What this sub-course IS (and is not)

- **IS:** the assembly course. Every prior agentic primitive was taught in isolation; 28 is where
  they become **one running coding harness** — the kind of thing Code Puppy / Claude Code / Aider /
  OpenAI Codex CLI actually are. The deliverable a learner walks away with is a working,
  budget-bounded, resumable, tool-using coding agent they built themselves.
- **IS a lab, so its spine is a BUILD ORDER, not a taxonomy.** Each stage = {build it → run it →
  watch it break at a specific, predictable wall → the break IS the spec for the next stage}.
- **IS NOT** a new-concept course. It introduces no new load-bearing claim; it re-derives nothing
  from scratch. Every mechanism is a CROSS-LINK back to where it was proven (22-27 + Part I/II).
- **IS NOT** Phase 2 (no `_structure.md`) and **IS NOT** chapters — Phase-1 brief only.

The pedagogical contract: **a primitive you were forced to invent because your toy broke is a
primitive you understand.** This is the "broken on purpose" method. It mirrors how the real arc was
discovered historically — people built loops, hit the quadratic, invented compaction; built tools,
hit poisoning, invented validation; etc.

---

## 1. The headline idea

**A coding harness is the agent loop (22) with code-aware tools (23), under a context budget (24),
backed by memory (25), made durable (26), optionally parallelized (27), and bounded by an explicit
cost/step/time budget (32).** Nothing more. Every "magic" feature of a real coding agent
decomposes into exactly one of those seven primitives. 28 proves this by construction: you can reach
a genuinely useful coding agent in a few hundred lines if and only if you add the primitives in
dependency order, each one paying for itself by fixing the wall the previous stage hit.

The forcing function that drives the whole progression is **22's O(T²) input-token cost**
(`T*p + g*T*(T-1)/2`): a coding task has *long* transcripts (big files, long tool outputs, many
steps), so the quadratic bites *sooner and harder* here than anywhere else. That single economic
fact is why a coding harness needs compaction (24), memory (25), and a budget (32) far more
urgently than a chat agent does.

---

## 2. The build progression (the bespoke spine)

Each stage below is `{ stage : what you add : the cross-link it reuses : the wall it hits :
the next stage that wall demands }`. Quantitative claims are RECOMPUTED in `_recompute.py`.

### Stage 0 — The 40-line agent (pure loop) — reuses **22**
- **Build:** the minimal control loop: `assemble(prompt) → call(model) → parse → if tool: act,
  observe, append → else: stop`. A `max_steps` cap. That's the whole thing.
- **Run:** it can already answer one-shot questions and call one trivial tool (e.g. `read_file`).
- **Wall it hits:** with no tools that change the world, it can *describe* a fix but not *make* one;
  and with the transcript re-sent every turn, you watch input tokens climb linearly per turn →
  **O(T²) cumulative** (22's headline; recomputed). On a real repo it blows the context window at
  turn `T* = floor((W-p)/g)+1` (22 §5).
- **→ demands Stage 1** (real code tools) and foreshadows Stage 3 (compaction).

### Stage 1 — Code-aware tools + the contract (make it edit code) — reuses **23**
- **Build:** the coding toolset as **contracts between a stochastic caller and deterministic code**
  (23): `read_file`, `write_file`/`apply_patch`, `list_dir`, `grep`, **`run_shell`/`run_tests`**.
  Each gets a JSON-schema'd signature, argument validation, and a structured result. The
  test-runner tool is the one that makes it a *coding* agent: it closes a **ReAct loop** (22) where
  the *observation is a compiler/test result* — acting grounds reasoning, exactly Toolformer's
  "incorporate the result into future prediction" (23, verified).
- **Run:** it can now read, patch, and run tests — a real edit-test-fix cycle.
- **Walls it hits:** (a) **selection error compounds** over a coding task's many steps:
  `1-(1-q)^N` (23/13/20/21 identity — recomputed; e.g. 63.6% chance of ≥1 wrong tool pick at
  N=50, q=0.02). (b) **tool results are huge** — a 1 MB file or a verbose test log overflows the
  result budget `W-(p+(t-1)g)` (23 recompute). (c) **`run_shell` is an arbitrary-code-execution
  hole** (23 security) → must sandbox + allowlist. (d) The toolbox itself costs `K·S` tokens/turn
  (23) feeding the quadratic.
- **→ demands Stage 2** (a budget to stop runaway/cost), Stage 3 (compaction for huge results),
  and a security boundary now.

### Stage 2 — The budget (stop it from runaway cost/loops) — reuses **22 + 18 + 32**
- **Build:** three hard budgets — **steps** (`max_steps`, 22), **dollars** (token-priced cost cap,
  22/32), **wall-clock** (`max_steps · step_deadline`, 22 §6 + 18 timeouts). Plus per-step
  retry/backoff (18) and a circuit breaker on a flapping tool (18). This is the cheapest possible
  safety net and it comes *before* the fancy stuff on purpose.
- **Run:** the agent can no longer bankrupt you or spin forever; worst-case cost is now a known
  number (22 step-budget bound, recomputed).
- **Wall it hits:** the budget *caps* the quadratic but doesn't *cure* it — a long coding task
  still hits the cap mid-fix because each turn re-sends the whole growing transcript. The budget
  buys safety, not reach.
- **→ demands Stage 3** (actually shrink the per-turn context).

### Stage 3 — Context engineering + compaction (extend its reach) — reuses **24**
- **Build:** treat context as a **fixed budget to engineer** (24). Allocate: system + tools +
  *relevant* file slices (not whole files) + recent transcript. **Compaction**: when the transcript
  exceeds ceiling `C`, summarize the old middle and keep head+tail. This is 24's HEADLINE:
  **compaction converts 22's O(T²) → O(T)** (recomputed) — the single most important upgrade in the
  whole harness for coding, because coding transcripts are long.
- **Run:** the agent now sustains long multi-file refactors without window overflow; cost grows
  ~linearly. Placement matters (put the task + most-relevant code at the *edges*, "lost-in-the-
  middle" band — 24, `[UNVERIFIED]` carry).
- **Wall it hits:** compaction is **lossy** — summarizing throws away detail the agent later needs
  ("what was that function signature again?"), and the summary lives only in the live window, so a
  restart loses it. You need a place to *durably externalize* facts, not just compress them.
- **→ demands Stage 4** (memory).

### Stage 4 — Memory: scratchpad + retrievable store (let it remember) — reuses **25**
- **Build:** memory as an **OS storage hierarchy over tokens** (25, MemGPT-verified "virtual context
  management = paging"). Resident window (fast/small) ↔ external store (slow/large), with explicit
  pager tools (`memory_write`, `memory_read`/search). Short-term scratchpad (plan, current file
  set) + long-term store (project facts, conventions, prior decisions). **AMAT over tokens** (25
  recompute): raising hit rate 0.80→0.95 cuts effective per-fact cost ~4×.
- **Run:** the agent recalls project conventions across compactions and even across sessions; the
  scratchpad survives summarization because it's externalized, not in the transcript.
- **Wall it hits:** memory is **read many, written once** → **poisoning blast radius** (25
  recompute: 1 bad write → ~15 downstream reads). And it's still in RAM: kill the process mid-fix
  and the whole run — scratchpad, partial patch state, budget consumed — evaporates.
- **→ demands Stage 5** (durability) + write-validation (33 carry).

### Stage 5 — Persistence + resume (survive a crash) — reuses **26**
- **Build:** the **transcript is a Write-Ahead Log** (26, Postgres-WAL-verified). Append each step
  to a WAL *before* acting (persist-before-act); checkpoint compacted state every `I* = √(2N·c_ckpt)`
  steps (26 recompute); on startup, **REDO** replay from the last checkpoint with **idempotency
  keys** gating side effects so a re-run patch/commit doesn't double-apply (26/17/21 recompute).
- **Run:** kill it mid-refactor → restart → it resumes exactly where it was, no double-applied
  edits, no lost budget. Agent resume **IS database crash recovery** (26 headline).
- **Wall it hits:** one durable loop is still *one* loop — a big task (refactor 30 files, each
  independent) runs strictly serially; latency = sum of parts.
- **→ demands Stage 6** (parallelism) — *only if the task is genuinely decomposable* (YAGNI gate).

### Stage 6 — Sub-agents / orchestration (scale it — carefully) — reuses **27**
- **Build:** a **supervisor** spawns worker loops (each a Stage-5 durable agent) for independent
  sub-tasks (e.g. one worker per file/module), joins with a **deadline + partial results** (27/20),
  aggregates **compacted** returns (27/24), optionally **votes** (majority-of-3, 27/11). A
  multi-agent harness **IS a distributed system** (27 headline).
- **Run:** independent work parallelizes; the refactor finishes faster — *sometimes*.
- **Wall it hits (the YAGNI lesson, recomputed):** speedup is **Amdahl over agents** (ceiling
  `1/s`, 27); the join is gated by the **slowest worker** `1-(1-p)^N = 63.4%@N=100` (27/20 tail);
  the **aggregation tax** `N·r` re-sends every worker's output to the supervisor (the quadratic at
  the parent, 27/24); and the **coordination tax makes multi-agent LOSE on small tasks** (27 payoff
  condition, recomputed). The lesson the learner *watches*: orchestration is a scaling tool for big
  decomposable tasks, **not** a free capability upgrade — default to one loop.
- **→ the harness is complete.** Everything past here is the rest of Part III (29 MCP connectors,
  30 RAG grounding, 31 eval/guardrails, 32 cost/ops, 33 safety) bolted onto this skeleton.

---

## 3. The "broken on purpose" table (the spine in one view)

| Stage | Add | Reuses | The wall (recomputed) | Demands |
|------|-----|--------|------------------------|---------|
| 0 | 40-line loop | 22 | O(T²) tokens; window overflow at T* | tools, compaction |
| 1 | code tools + test-runner | 23 | selection compounding 1-(1-q)^N; huge results; ACE hole | budget, compaction, sandbox |
| 2 | step/$/time budget | 22·18·32 | caps cost but doesn't cure quadratic | compaction |
| 3 | context + compaction | 24 | O(T²)→O(T) **but lossy + volatile** | memory |
| 4 | scratchpad + store | 25 | poisoning blast radius; volatile on crash | persistence |
| 5 | WAL + resume | 26 | durable but strictly serial | orchestration (if decomposable) |
| 6 | supervisor + workers | 27 | Amdahl ceiling, join tail, aggregation tax, YAGNI | (done) |

The diagonal is the whole point: **each row's "wall" is the next row's reason to exist.**

---

## 4. The minimal durable set the harness must persist (reuse 26 §4)

Transcript/WAL (source of truth) · compacted context + memory pointers (24/25) · cursor/offset
(09 LSN / step index) · idempotency keys + commit status for every world-changing tool call (17) ·
pending tool calls / outbox (17) · budgets consumed: steps, $, wall-clock (22/32) · the working set
(open files, current plan). **Not** persisted: anything re-derivable by replaying the WAL.

## 5. The security boundary (introduced at Stage 1, hardened throughout)

A coding harness runs **arbitrary code** (`run_shell`, `run_tests`) and **edits the filesystem** —
it is the single most dangerous agent class. Boundary (reuse 23 security + forward to 33):
allowlist commands, sandbox/container the execution (workspace jail, no network unless granted),
require confirmation or dry-run for destructive ops, never let tool *output* (file contents, test
logs, web text) be trusted as instructions (**prompt-injection-via-tool-result** → 33), cap
resource use (CPU/mem/time per tool call, reuse 18 + 20 bulkhead). The harness's blast radius is
the union of its tools' blast radii.

## 6. Build-your-own target (the capstone deliverable)

**Grow ONE program through the 7 stages above.** Acceptance per stage = *demonstrate the wall*, then
*demonstrate the fix*: e.g. Stage 0→3, show the window overflow on a big file, then show compaction
sustaining the same task; Stage 4→5, kill the process mid-patch, show clean resume with no
double-applied edit; Stage 6, show a 10-file refactor where multi-agent wins, then a 1-file fix
where it *loses* to a single loop. The final artifact is a real, bounded, resumable coding agent —
and, more importantly, a learner who can name exactly which primitive each feature is and why it's
there. This is the `/build` capstone: **own-coding-agent-harness**.

## 7. Why no new primary source (and what's `[UNVERIFIED]`)

28 is a **capstone application** (like 21 for Part II): it introduces no new load-bearing claim, so
it needs no new fetched primary. Every mechanism cross-links to an already-VERIFIED anchor —
ReAct (22), Toolformer (23), CoT (24), MemGPT/Reflexion (25), Postgres-WAL (26), and the
recomputed coordination math (27). All quantitative claims are RECOMPUTED in `_recompute.py` by
reusing the verified identities from 22-27.

Carry-forward `[UNVERIFIED]` (none load-bearing for the build progression; all inherited from the
sub-courses 28 assembles):
- Real coding-agent implementations as design references (Claude Code, Aider, OpenAI Codex CLI,
  SWE-agent, Cursor, Code Puppy itself) — design folklore, not fetched primaries; useful as Phase-2
  case material, not as load-bearing claims.
- **SWE-bench** (Jimenez et al., arXiv 2310.06770) as the canonical coding-agent benchmark — noted
  for Stage-1 "what does 'useful' mean" and for 31; NOT fetched this session.
- Sandboxing/ACE-mitigation specifics (containers/cgroups/seccomp → Appendix I) — reuse, deferred.
- prompt-injection-via-tool-result (→33) and memory-poisoning mitigations (→25/33) — carry-forward.
- All prior 22-27 + 01-21 carried `[UNVERIFIED]` remain logged and untouched.
