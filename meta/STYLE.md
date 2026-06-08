
# Style & format rules

## The default teaching arc (adapt per sub-course, do not template blindly)
theory → intuition → diagram(s) → implementation/walkthrough → tradeoffs → real-world case study
Each sub-course's _structure.md may reshape this to fit its material.

## Diagrams
- A diagram for every non-trivial mechanism. Prefer Mermaid; ASCII where Mermaid can't.
- Simple to look at, technically precise. Label the parts that matter.

## Images (not diagrams)
- Never fabricate an image. Where a real visual beats prose, leave:
  <!-- IMAGE PROMPT: <detailed generation prompt> -->
  with a one-line caption of what it should show. Log every one in
  assets/diagrams/image-prompts.md (path | prompt | caption).

## Sources & links
- Every non-obvious claim gets a link, preferring primary sources: papers, source code,
  vendor/official docs — over blogs. One canonical link per claim.

## Cross-linking
- When the spine uses a concept, link down to the appendix that goes deep
  ("we shard here — see appendices/F-postgres-internals for MVCC + WAL").

## Voice
- Senior engineer mentoring a capable junior. Precise, plain, unpadded. Define jargon on
  first use. No filler, no marketing tone.
