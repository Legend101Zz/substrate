# Substrate — A First-Principles Course in System & Agentic System Design

> *Understand the layer everything else is built on.*
>
> Status: **Phase 0 (scaffold) complete.** No course content yet. Research begins in Phase 1.

Substrate is a long-running effort to build the deepest first-principles course on system
design and agentic system design that exists — complete enough that a serious learner
needs no other resource.

It is two-tier by design:
- **Spine** (foundations `00–12` + System Design + Agentic System Design) teaches
  transferable concepts, each paired with a build-your-own-X lab where the material fits.
- **Appendices** (`A–O`) are reference-grade, info-only deep dives into one real system
  each; spine chapters cross-link down into them.

## Repository layout

- `meta/` — the project's constitution and living state:
  - `CONSTITUTION.md`, `PERSONA.md`, `STYLE.md`, `QUALITY_BAR.md`, `RESEARCH_PROTOCOL.md`
  - `COURSE_MAP.md` — the course outline (becomes a full dependency DAG in Phase 2)
  - `RESEARCH_INDEX.md` — the source corpus index
  - `PROGRESS.md`, `SESSION_LOG.md`, `DECISIONS.md` — resume anchor, history, ADR log
  - `subagents/` — role definitions (researcher, factchecker, writer, diagrammer, critic)
- `assets/diagrams/image-prompts.md` — manifest of every image placeholder
- `START_HERE.md` — the bootstrap document that defines the whole project

## How it's built

A BRAIN agent (Opus) plans, sequences, and reviews; specialized subagents research,
draft, diagram, fact-check, and critique. Work proceeds in phases:
0 bootstrap → 1 deep research → 2 per-sub-course structure design → 3+ one chapter at a
time (Research → Plan → Implement → Verify), with a critic gate against `QUALITY_BAR.md`
before anything is marked DONE.

See `meta/COURSE_MAP.md` for the full planned curriculum.
