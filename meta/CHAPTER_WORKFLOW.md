# Chapter authoring workflow (Phase 3) — the collaborative loop

> This is the BINDING process for writing every chapter from Phase 3 onward. It supersedes the
> "writer drafts solo" implication in START_HERE. The owner (Mrigesh) is IN THE LOOP on every
> chapter — he reads, edits, and finalizes WITH the brain, so he gains the knowledge and the quality
> bar stays high. Locked in by ADR-005.

## The loop (one chapter at a time — NEVER batch-draft multiple chapters)

For each chapter, in order:

1. **PLAN** — brain writes/loads the chapter outline (`<unit>/_plan.md`) from the unit's
   `_structure.md`. If a plan already exists, restate it briefly. STOP for the owner's nod on shape.
2. **DRAFT** — brain (or `writer`) drafts the SINGLE chapter in full, per `meta/PERSONA.md` +
   `meta/STYLE.md`. Inline, the draft MUST:
   - call out **every diagram needed** with a `[DIAGRAM: …]` marker describing what it shows;
   - call out **every real image needed** with a `<!-- IMAGE PROMPT: … -->` + one-line caption,
     and log it in `assets/diagrams/image-prompts.md`;
   - cite every non-obvious claim to a primary source;
   - preserve and surface any `[UNVERIFIED]`/`[PARTIAL]`/`[GAP]` flags that touch the chapter.
3. **PRESENT + REVIEW** — brain shows the draft to the owner AND explicitly lists, up top:
   - what diagrams/images it recommends and WHY (so the owner decides what to actually produce);
   - any open questions or judgment calls;
   - anything still `[UNVERIFIED]` the owner should know about.
4. **EDIT TOGETHER** — owner reads, comments, edits. Brain applies changes. Iterate until the owner
   is happy. This is where the owner learns — keep explanations clear, answer questions in-thread.
5. **VERIFY** — `factchecker` checks every claim vs source; `critic` (Opus) scores against
   `meta/QUALITY_BAR.md`. Fail → fix and re-loop. Pass → eligible to finalize.
6. **FINALIZE** — only when (a) the owner says "finalize" AND (b) the critic has PASSED:
   mark the chapter DONE in PROGRESS.md, commit, move to the next chapter.

## Hard rules for this loop
- **One chapter at a time.** Never start chapter N+1 before N is finalized. No shallow parallel drafts.
- **Owner gates DRAFT→FINALIZE.** The brain never self-finalizes a chapter; the owner's "finalize"
  + a critic PASS are both required (CONSTITUTION: never DONE without a critic pass).
- **Always surface visuals.** Every chapter presentation names the diagrams/images it needs and asks
  the owner which to produce. Diagrams default to Mermaid/ASCII; real images get IMAGE PROMPTs only.
- **Teach while building.** The owner is reading to LEARN — explain reasoning, not just output.
- **Preserve every flag.** Never silently drop an `[UNVERIFIED]`/gap; if one heals (source fetched),
  upgrade it with a reconcile-note and a saved receipt in `meta/fetched_primaries/`, erase nothing.
- **Drafting order = the COURSE_MAP DAG** (dependency order), unless the owner directs otherwise.

## Where artifacts live
- Outline: `<unit>/_plan.md` · Draft/final chapter prose: `<unit>/` chapter files (named in `_plan.md`).
- Image prompts manifest: `assets/diagrams/image-prompts.md`.
- State: `meta/PROGRESS.md` (DRAFTING → REVIEW → DONE) · history: `meta/SESSION_LOG.md`.
