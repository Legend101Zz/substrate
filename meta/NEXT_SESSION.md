# NEXT_SESSION — resume here (harness: code-puppy)

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. (Detailed history → SESSION_LOG.md; scope/process
decisions → DECISIONS.md.)

Last updated: 2026-06-09 · Phase: 1 (deep research) · Harness: **code-puppy** (was Claude Code for Phase 0 + Wave 1)

> Note: Wave 1 stopped on a billing event in the *previous* harness — irrelevant now that we're on
> code-puppy. Treat this doc as a clean "done / left + how to run it here" handoff, not a blocker log.

---

## ✅ Things DONE
- **Phase 0** — scaffold + constitution files + subagent personas + living-state files; git
  initialized. (commits `ad7dfc8`, `05fd114`)
- **Phase 1 / Wave 1 — foundations 01, 02, 03 researched** (commit `5028386`). One brief per source
  cluster, all validated against RESEARCH_PROTOCOL (6 sections, primary-sources-first,
  `[UNVERIFIED]` flags), all accepted:
  - 01 computers-from-first-principles — `_research_nand2tetris-petzold.md` (13 srcs),
    `_research_eater-csapp.md` (10 srcs) → reconciled `_research.md`.
  - 02 terminal-shell-and-dev-environment — `_research_missing-semester-tlcl.md` (19 srcs),
    `_research_shell-internals-build.md` (11 srcs) → reconciled `_research.md`.
  - 03 networking-from-first-principles — `_research_cs144-sponge.md` (9), `_research_kurose-beej.md`
    (18), `_research_stevens-hpbn.md` (8) → reconciled `_research.md`.
- **RESEARCH_INDEX.md expanded** with Wave 1 finds (Minnow-vs-Sponge, RFC 9293/6298/8446/9000/9114,
  brennan.io, GNU libc job-control, SAP-1/Malvino, gaia.cs.umass free companion, hpbn.co free,
  End-to-End paper, CUBIC/BBR, XarkLabs VHDL).
- **DECISIONS.md** — ADR-001 (per-cluster files reconciled by brain to avoid write-clobber),
  ADR-002 (Wave 1 stop + factchecker deferred — historical, on the old harness).
- **PROGRESS.md** seeded with all ~50 sub-courses; 01–03 marked RESEARCHING (briefs done).

## ⏳ Things LEFT
- **Factcheck debt:** `factchecker` has NOT run on Wave 1. Briefs self-flag the shaky claims as
  `[UNVERIFIED]` — exact SAP-1 control-word bit map / T-state tables; Eater 6502 memory map;
  Scott/Petzold book figures; zsh no-word-split default; Bash *Environment* verbatim; CodeCrafters
  stage slugs; End-to-End paper page-quotes; Beej epoll depth; date-sensitive HTTP/3 numbers +
  per-OS congestion-control default. Resolve before they harden into chapters.
- **Phase 1 research remaining (~47 sub-courses):** foundations 04–12, System Design 13–21,
  Agentic 22–34, appendices A–O. All TODO in PROGRESS.md.
- **Open design question for Phase 2** (logged, not yet ADR): CS144 Minnow dropped the hand-authored
  `TCPConnection` state-machine lab — decide whether the own-tcp-ip lab models Sponge Lab 4.
- **Not started:** Phase 2 (per-sub-course `_structure.md`), any chapters. Do NOT begin until the
  Phase 1 corpus is signed off.

---

## 🐶 Running this project in code-puppy (read before resuming)

code-puppy (https://github.com/mpfaffenberger/code_puppy) differs from Claude Code in ways that
change HOW Phase 1 runs. Adapt the protocol's *intent*, not its Claude-specific mechanics.

- **Launch:** `uvx code-puppy -i` (interactive). `AGENTS.md` at repo root is auto-loaded as project
  rules (also `~/.code_puppy/AGENTS.md` for global). This repo ships an `AGENTS.md` pointing at the
  constitution — read it first.
- **NO parallel sub-agents.** code-puppy has agent *switching* (`/agent`, `/agent <name>`,
  `/agent agent-creator`), not parallel fan-out. So RESEARCH_PROTOCOL's "fan out researchers IN
  PARALLEL" becomes: **research each source cluster sequentially in one run**, writing
  `_research_<cluster>.md` per cluster, then reconcile into `_research.md`. For real parallelism,
  the human can run **multiple `code-puppy` terminals**, one per cluster. Use `/model` round-robin
  (`~/.code_puppy/extra_models.json`) to dodge rate limits.
- **NO built-in web search/fetch.** This is critical — researchers need primary sources. code-puppy's
  built-in tools are file/shell only (`read_file`, `create_file`, `replace_in_file`, `grep`,
  `list_files`, `delete_file`, `agent_run_shell_command`, `agent_share_your_reasoning`). **Configure
  a web fetch/search MCP server via `/mcp`** before any research (e.g. a fetch MCP + a search MCP),
  or research degrades to shell `curl`/`agent_run_shell_command`. Verify web access works before Wave 2.
- **Subagent personas → code-puppy agents.** `meta/subagents/{researcher,factchecker,critic,...}.md`
  were Claude-Code agents (they reference WebSearch/WebFetch). To reuse them here, create JSON agents
  in `~/.code_puppy/agents/` via `/agent agent-creator` (fields: name, system_prompt, tools,
  display_name), mapping their web steps onto the MCP web tools; or just paste the persona text as
  the run prompt and `/agent` into a research-tuned agent. Keep "briefs only, no prose" intact.
- **Tool-name map (Claude → code-puppy):** Read→`read_file`, Write→`create_file`, Edit→
  `replace_in_file`, Grep→`grep`, LS→`list_files`, Bash→`agent_run_shell_command`,
  WebSearch/WebFetch→(MCP web tools).
- **Custom commands** live in `.claude/commands/` (also `.github/prompts/`, `.agents/commands/`);
  filename = command name. Could wrap the resume prompt as a command later if useful.
- **Model:** pick a strong long-context coding model via `/model` (or `/add_model` from models.dev);
  set provider key env var (e.g. `CEREBRAS_API_KEY`, `GROQ_API_KEY`, `TOGETHER_API_KEY`, …).

---

## ▶️ PROMPT TO RUN NEXT (paste into `uvx code-puppy -i`)

```
You are the BRAIN agent for the Substrate course project (read AGENTS.md + meta/CONSTITUTION.md).
Rehydrate first: read START_HERE.md, meta/CONSTITUTION.md, RESEARCH_PROTOCOL.md, COURSE_MAP.md,
RESEARCH_INDEX.md, PROGRESS.md, SESSION_LOG.md, DECISIONS.md (ADR-001/002), and this
meta/NEXT_SESSION.md. Confirm in 3–4 lines: current state, that Wave 1 (01–03) briefs are committed,
and the exact plan you're about to run. Then proceed.

PRECHECK (code-puppy specifics): confirm a web fetch/search MCP is connected via /mcp (researchers
need primary sources). If not, set one up or fall back to curl via agent_run_shell_command — do NOT
research without web access. Remember: no parallel agents here, so do clusters sequentially (or tell
me to open extra terminals); use /model round-robin to avoid rate limits.

Continue Phase 1 deep research per RESEARCH_PROTOCOL.md (adapt mechanics to code-puppy):
- FIRST clear the factcheck debt: run the factchecker persona (meta/subagents/factchecker.md) over
  the most load-bearing / [UNVERIFIED]-flagged claims in 01–03's _research files. Record verdicts;
  fix or escalate any UNSUPPORTED/MISATTRIBUTED before they harden.
- THEN Wave 2 = sub-courses 04, 05, 06. For each, research one source cluster from RESEARCH_INDEX at
  a time (sequentially), writing _research_<cluster>.md; reconcile into each _research.md; validate
  before accepting (reject thin/uncited, redo); expand RESEARCH_INDEX with new finds.
- Each sub-course lives under <id>/ at repo root (create the dir first with list_files/shell).
- Keep PROGRESS.md current (RESEARCHING in-flight). Scope changes → DECISIONS.md as ADRs.
Then continue waves: 3 (07,08,09), 4 (10,11,12). STOP at the end of the foundations spine, commit,
append a SESSION_LOG entry, update this NEXT_SESSION.md (done/left + next prompt), and report gaps +
the proposed next batch (System Design 13–21). Do not start System-Design research or any Phase 2
work until I sign off. No chapters.
```
