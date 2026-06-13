# AGENTS.md — Substrate project rules (auto-loaded by code-puppy)

You are working on **Substrate**: the deepest first-principles course on system design + agentic
system design. This file is the entry point; the binding rules live in `meta/`.

## Read these first (every session)
1. `meta/NEXT_SESSION.md` — where we are, what's done/left, and the exact prompt to run next.
2. `meta/CONSTITUTION.md` — mission + non-negotiables + the orchestration/memory model.
3. `meta/PROGRESS.md` — the resume anchor (per-sub-course state).
4. `START_HERE.md`, `meta/RESEARCH_PROTOCOL.md`, `meta/COURSE_MAP.md`, `meta/RESEARCH_INDEX.md`,
   `meta/SESSION_LOG.md`, `meta/DECISIONS.md` as the task requires.
5. `meta/CHAPTER_WORKFLOW.md` — **REQUIRED in Phase 3.** The binding collaborative chapter loop
   (owner-in-the-loop, one chapter at a time, surface every diagram/image need). See ADR-005.

## Hard rules (from the constitution)
- First principles, zero hand-waving. Explain WHY before HOW, grounded in a paper/source/constraint,
  and cite it. Two layers per concept: intuitive model THEN deep mechanism.
- Phases are gated. Phase 1 = research briefs only (NO chapters). Phase 2 = per-sub-course
  `_structure.md` (STOP for sign-off). Phase 3+ = one chapter at a time. Never skip a gate.
- Never mark a chapter DONE without a passing `critic` review against `meta/QUALITY_BAR.md`.
- Never start a session by guessing — rehydrate from PROGRESS.md + SESSION_LOG.md + NEXT_SESSION.md.
- Validate every researcher/factchecker output before accepting it; reject thin or uncited work.
- Any scope/ordering/cut change goes in `meta/DECISIONS.md` as an ADR — never silently.
- End every session: append to SESSION_LOG.md (shipped / decisions / stopped-at), update PROGRESS.md
  and NEXT_SESSION.md, commit.

## code-puppy specifics (this harness)
- Create the project agents FIRST: materialize `researcher`/`factchecker` (later critic/writer/
  diagrammer) from `meta/subagents/*.md` as code-puppy JSON agents via `/agent agent-creator`, then
  `/agent <name>` to use them. Keep "briefs only, no prose" in the researcher's system_prompt.
- No parallel sub-agents — research source clusters **sequentially** (switch agents), or run multiple
  terminals. Use `/model` round-robin to avoid rate limits.
- Web research works via `agent_run_shell_command` (`curl`, etc.) and/or a web **MCP** (`/mcp`) —
  primary sources are mandatory; pull them by whichever path is available.
- Tool map: read_file / create_file / replace_in_file / grep / list_files / agent_run_shell_command.
