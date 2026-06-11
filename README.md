# Substrate — A First-Principles Course in System & Agentic System Design

> *Understand the layer everything else is built on.*
>
> Status: **Phase 1 (deep research) complete** for all 50 units; **Phase 2 (per-sub-course
> structure design) complete** for the 35 spine units (00–34). Chapter drafting (Phase 3) begins
> after structure sign-off. No course prose is published yet.

Substrate is a long-running effort to build the deepest first-principles course on system
design and agentic system design that exists — complete enough that a serious learner
needs no other resource.

It is two-tier by design:
- **Spine** (foundations `00–12` + System Design `13–21` + Agentic System Design `22–34`)
  teaches transferable concepts, each paired with a build-your-own-X lab where the material
  fits. The agentic track culminates in one capstone you grow across eleven units: a real,
  bounded, resumable, tool-using **coding agent harness**.
- **Appendices** (`A–O`) are reference-grade, info-only deep dives into one real system
  each (Postgres, Redis, Kafka, the JVM, V8, the Linux kernel, Docker, Kubernetes, …);
  spine chapters cross-link down into them. No exercises — pure reference.

Everything is grounded in primary sources — papers, source code, and official specs — and
every quantitative claim is recomputed and checked. See `meta/COURSE_MAP.md` for the full
curriculum and its dependency DAG.

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

**Currently at the Phase 2 → Phase 3 boundary:** the research corpus (50 units) and the
spine structure plans (35 `_structure.md` files) are done; chapter drafting starts once the
structures are signed off.

See `meta/COURSE_MAP.md` for the full planned curriculum and dependency DAG.
