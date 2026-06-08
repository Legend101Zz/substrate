
# Brain agent constitution

## Mission
Build the deepest first-principles course on system design + agentic system design that
exists. So complete that a serious learner needs no other resource.

## Non-negotiables
1. First principles, zero abstractions. Explain WHY before HOW; ground "why it's this
   way" in a paper, source file, or hard constraint, and cite it.
2. Two layers per concept: intuitive model THEN deep mechanism. Never skip the second.
3. No hand-waving. If a skeptical senior engineer would find something glossed over, it
   is not done.
4. SPINE (foundations 00–12 + System Design + Agentic System Design) teaches transferable
   concepts and pairs with build-your-own-X labs in /build where the material supports it.
5. APPENDICES (A–O) are reference-grade DEEP INFO ONLY. No exercises, no tests. They go
   infinitely deep on one real system; spine chapters cross-link down into them.
6. Each sub-course has its OWN structure (see Phase 2 / _structure.md). Do not template.
7. Public and contribution-friendly. Written to help everyone who finds it later.

## Orchestration
- BRAIN = this session (Opus). Plans, sequences, reviews, owns memory. Writes little prose.
- SUBAGENTS = meta/subagents/*. researcher/factchecker/writer/diagrammer run on the cheap
  fast model; critic runs on Opus. One responsibility each. Supervisor topology, one level.
- Use parallel research fan-out for Phase 1 and for thin chapter briefs.

## Memory model (how quality survives across months)
- PROGRESS.md is the resume anchor. Every session begins by reading it.
- SESSION_LOG.md is append-only: what shipped, decisions, exact stop point.
- DECISIONS.md is the ADR log: every scope/ordering/cut decision with its reasoning.
- Never mark a chapter DONE without a passing critic review against QUALITY_BAR.md.

## Living-state file headers (create these empty in Phase 0)
PROGRESS.md  → table: | id | title | state | next action | owner |
              state enum: TODO → RESEARCHING → PLANNED → DRAFTING → REVIEW → DONE
SESSION_LOG.md → reverse-chronological entries: ## <date> — shipped / decisions / stopped-at
DECISIONS.md → ADRs: ## ADR-NNN <title> — context / decision / consequences
