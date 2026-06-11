# 00 — How to Use This Course · _plan.md (Phase 3 PLAN — outline only, NOT a draft)

> **Status:** PLAN for annotation. No prose written. Per START_HERE Phase 3, this outline STOPS for
> your notes before `writer` drafts anything. Derived verbatim-in-spirit from `00/_structure.md`
> (orientation pamphlet, NOT a teaching arc) + the finalized `meta/COURSE_MAP.md` DAG.
> **Sequencing caveat (honored):** 00's structure says "write LAST-ish / revise after the DAG is
> final." The DAG is now final (`2e23b60`), so the map is safe to render — but if any spine reshapes
> in Phase 3, §2/§5/D1 get a revision pass before 00 is marked DONE.

## Target shape & length
- Orientation pamphlet: 6 short, scannable sections, each ~½–1 screen. A reader passes through ONCE
  then refers back. Airport-terminal map, not a lecture. Total target: well under any teaching unit.
- Voice per STYLE: senior engineer, plain, unpadded. No marketing tone (extra-important here — this
  is the front door and the temptation to sell is highest).

## Section-by-section outline (what each will contain — to be drafted after sign-off)
1. **What this is & who it's for**
   - Mission line: one resource, zero hand-waving, first-principles (from CONSTITUTION).
   - Persona: capable junior → senior; define the bar honestly ("you can read code; you're willing
     to build, not just read").
   - "What you need first": minimal — can read a little code, a terminal, curiosity. NOT a CS degree.
   - Anti-promise: this is long and deep on purpose; it is not a cheat sheet.
2. **The two-tier map: spine vs appendices**
   - Spine 00–34 = transferable CONCEPTS + build labs; Appendices A–O = ONE real system, infinitely
     deep, reference-only (no exercises — CONSTITUTION #5).
   - Part 0 / I / II / III shape; the two headlines (System Design 13–21, Agentic 22–34) called out.
   - Renders **D1** (the course map) right here.
3. **How to read a chapter**
   - The default arc: intuitive model THEN deep mechanism (and that the second is never skipped).
   - Why every non-obvious claim is cited (primary sources); what `[UNVERIFIED]` means to a reader.
   - What a `<!-- IMAGE PROMPT -->` is and why it's there instead of a fabricated image.
   - How cross-links DOWN into appendices work; how a spine chapter pairs with its /build lab.
   - Renders **D2** (anatomy of a chapter).
4. **The agent-paired learning method** (the distinctive bit)
   - The pitch: you have a coding agent; use it as a tutor/lab-partner, not an answer key.
   - 3–4 concrete, reusable copy-paste prompt templates:
     (a) **Quiz me** on chapter N at the senior bar; (b) **Extend the build lab** with one new
     feature + tests; (c) **Explain this diagram** / re-derive it from scratch; (d) **Check my
     mental model** — I'll explain X back, you find the hand-wave.
   - One worked example of (a) so the reader sees the shape.
5. **Three reading paths**
   - (a) cover-to-cover (the number line — a verified topological sort);
   - (b) "I just need System Design": 00 → skim 01/03/04/06 → 11 → 13–21;
   - (c) "I just need Agentic": 00 → (assume 04/09/13/17/18/19/20 fluency) → 22–34, dip into App M.
   - Tiny path table; renders **D3** (three reading paths swimlane).
   - Cross-reference the same orders in COURSE_MAP so they never drift (single source = COURSE_MAP).
6. **Conventions & contributing**
   - Citation style (primary-source-first; cite books by chapter title due to edition drift);
     `[UNVERIFIED]` flag meaning; the `/build` directory; image-prompt manifest location.
   - Public + contribution-friendly: how to file an issue, the quality bar contributions are held to.

## Diagrams (to author in IMPLEMENT, with the diagrammer)
- **D1 — course map** (Mermaid): reuse/condense the finalized DAG from COURSE_MAP; highlight the two
  headline nodes + the appendix shelf. The single most important visual in the repo.
- **D2 — anatomy of a chapter** (annotated callout): intuitive layer / deep mechanism / diagram /
  citation / appendix cross-link / lab link.
- **D3 — three reading paths** (swimlane/path diagram).
- No `<!-- IMAGE PROMPT -->` expected here (all three are structural diagrams, Mermaid-able).

## Build lab
- None. 00 POINTS at the /build index; builds nothing.

## Sources / gaps to honor (carried — erase nothing)
- No new research; pure synthesis of CONSTITUTION + STYLE + the final COURSE_MAP DAG.
- The three reading paths MUST match COURSE_MAP exactly (treat COURSE_MAP as the source of truth;
  if they diverge, COURSE_MAP wins and 00 is corrected).
- Revisit §2/§5/D1 if the DAG changes during Phase 3 before marking 00 DONE.

## Open questions for your annotation
- Q1: How many agent-paired prompt templates do you want in §4 — keep to 3–4, or expand into a
  fuller "prompt library" appendix later?
- Q2: Should D1 be a condensed map (Parts + headlines only) or the full 34-node DAG inline? (Lean:
  condensed in 00, full DAG stays in COURSE_MAP with a link.)
- Q3: Contributing section — link out to a future `CONTRIBUTING.md`, or inline the essentials in §6?
