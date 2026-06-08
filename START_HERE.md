# START_HERE.md — Substrate: A First-Principles Course in System & Agentic System Design

You are the BRAIN agent for a long-running (1–2 month, many-session) project: building
the deepest first-principles course on system design and agentic system design in
existence — so complete a reader never needs another resource.

This document is self-installing. Everything below the line `=== SCAFFOLD BELOW ===`
is a set of files delimited by `=== FILE: <path> ===` / `=== END FILE ===` markers.

────────────────────────────────────────────────────────
PHASE 0 — BOOTSTRAP (this session only; no research, no chapters)
────────────────────────────────────────────────────────
1. Read this entire document top to bottom.
2. For each `=== FILE: <path> ===` block below, write its contents VERBATIM to <path>.
   Do not edit, summarize, or "improve" them. These are the project's constitution.
3. Create the living-state files (empty, with the headers shown in CONSTITUTION.md):
   meta/PROGRESS.md, meta/SESSION_LOG.md, meta/DECISIONS.md.
4. Initialize git. Commit as "scaffold".
5. Print the resulting file tree and STOP. Wait for my "go" before Phase 1.

Do NOT begin research or write any course content in Phase 0.

────────────────────────────────────────────────────────
PHASE 1 — DEEP RESEARCH (only after I say "go")
────────────────────────────────────────────────────────
Follow meta/RESEARCH_PROTOCOL.md. For each sub-course in meta/COURSE_MAP.md, fan out
`researcher` subagents IN PARALLEL (one per source cluster in meta/RESEARCH_INDEX.md).
Each returns a structured brief into <subcourse>/_research.md. Then EXPAND
meta/RESEARCH_INDEX.md with everything new. Build a corpus deep enough that drafting
needs no further searching. Write NO course chapters yet. STOP when the corpus is done
and report coverage gaps.

────────────────────────────────────────────────────────
PHASE 2 — DESIGN EACH SUB-COURSE'S OWN SHAPE (then STOP for sign-off)
────────────────────────────────────────────────────────
Sub-courses must NOT share one template. For each, write <subcourse>/_structure.md
proposing a bespoke structure that fits its material (e.g. computer-architecture builds
up from a NAND gate; networking goes layer by layer; research-papers is paper-walkthroughs;
db-internals is component-by-component). The default teaching arc in STYLE.md is a
starting point to adapt, not a cage. Finalize meta/COURSE_MAP.md (dependency DAG +
per-chapter 3–5 line specs + paired build lab + diagrams needed), populate PROGRESS.md,
draft the public README.md, and present it all. STOP. I will annotate before any drafting.

────────────────────────────────────────────────────────
PHASE 3+ — BUILD ONE CHAPTER AT A TIME (subsequent sessions)
────────────────────────────────────────────────────────
EVERY session starts by reading PROGRESS.md + SESSION_LOG.md and telling me the state
and proposed batch. Per chapter run Research → Plan → Implement → Verify:
  PLAN     write outline, STOP for my annotation, then proceed.
  IMPLEMENT `writer` drafts per persona + style; `diagrammer` adds diagrams + IMAGE PROMPTs.
  VERIFY    `factchecker` checks every claim vs source; `critic` (Opus) scores vs QUALITY_BAR.
            Fail → loop. Pass → mark DONE.
End each session: append to SESSION_LOG.md (shipped / decisions / exact stop point),
update PROGRESS.md, commit. Small batches. Finish chapters; do not start three shallow ones.

GUARDRAILS: never mark DONE without a critic pass; never start a session by guessing —
rehydrate from PROGRESS.md; validate every subagent output before accepting; scope growth
goes in DECISIONS.md as an ADR, never silent expansion.

Begin Phase 0 now. Stop after printing the file tree.
=== SCAFFOLD BELOW ===

The scaffold file blocks from this document have been materialized into the repository
(see `meta/` and `meta/subagents/`). They are the project's constitution — refer to the
files on disk as the source of truth from here on.
