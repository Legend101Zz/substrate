# 12 — Research Papers for Engineers · _structure.md

**Identity:** the meta-skill chapter — how to read a systems paper actively and
adversarially, practiced on the canon that the rest of the course is built from. Closes
Part I by teaching the reader to keep learning past this course.

**Bespoke shape — "method, then guided walkthroughs (the canon IS the exercise set)."**
NOT a teaching arc and NOT a paper-by-paper survey. Two halves of one loop. **Part A — the
method:** a short, sharp protocol for reading (the writer's rule → the reader's rule →
staged triage → impossibility-first). **Part B — walkthroughs:** apply the method to a
fixed, high-signal corpus, leading with the agreement chain (the SAME result told five ways
with escalating clarity — the live proof that exposition is gradeable), then mapping the
rest of the canon onto the headline course. Distinctive: 12 reuses the line-verified
receipts in 06–11 as the answer key, so walkthroughs are grounded, not summaries.

## Dependency position
- **Depends on:** 11 (the agreement/consensus canon is verified there — 12 reuses it),
  06–10 (storage/cache/MQ/proxy internals already line-verified — the answer keys), 03
  (End-to-End Arguments).
- **Feeds into:** all of Part II/III (each canon paper feeds a sub-course: GFS/Bigtable→14,
  Dynamo/Spanner→15, MapReduce→17, Dapper→19, Tail→20). 12 is the foundation the headline
  draws on — not trivia.
- **Appendix links DOWN:** L (consensus papers in depth), M (agent papers). 12 teaches HOW
  to read; the appendices + spine teach the results.

## Chapter specs (3–5 lines each)
### Part A — the reading method
1. **The reader's rule comes from the writer's rule** — Lamport: state the correctness
   condition independently of the solution, THEN the solution, THEN the proof. The reader's
   first job: *what problem does this solve, stated independently of its mechanism?* If
   correctness is defined in terms of the algorithm, the proof is near-vacuous —
   comprehension ≠ correctness. (VERIFIED from `state-the-problem`.)
2. **Staged triage: read in passes, not top-to-bottom** — Keshav three-pass (scan + five Cs
   → careful read + figure audit → virtual re-implementation) + citation-convergence survey.
   Reading is a budget problem: escalate to pass 3 only for papers you'll build/review/teach.
   (Framing `[UNVERIFIED]` — Keshav PDF blocked; fetch before prose.)
3. **The field's signature move: impossibility, then construction** — Byzantine §2 and FLP
   both prove what CAN'T be done before showing what can. Teaching readers to locate the
   impossibility result first shows where the real constraint lives — the highest-leverage
   habit. (VERIFIED.)

### Part B — guided walkthroughs (the canon)
4. **The agreement chain — one result, five tellings** — the perfect teaching corpus:
   Reaching Agreement (1980: n≥3m+1) → Byzantine Generals (1982: same result + metaphor;
   impossibility before OM(m)) → The Part-Time Parliament (1998: original Paxos, famously
   obscure) → Paxos Made Simple (2001) → Raft (2014, designed FOR understandability). Proves
   Part A: exposition is a gradeable property. (Four Lamport primaries VERIFIED.)
5. **The storage & data canon** — guided walkthroughs: GFS (append-optimized, single master)
   → Bigtable (SSTable/tablets) → Dynamo (eventual consistency, sloppy quorum, version
   vectors) → MapReduce (the programming model). Each mapped to its spine home (14/15/17) and
   read with the Part-A method, using 06–09 receipts where they overlap.
6. **The ops & coordination canon** — Dapper (distributed tracing → 19), The Tail at Scale
   (latency variability → 20), Chubby/ZooKeeper (coordination → 11/L), End-to-End Arguments
   (→ 03), Lampson "Hints" (design wisdom). How to read a measurement/experience paper
   differently from a theory paper.

## Paired build labs (/build — reading artifacts, not systems)
Structured three-pass reading log (five Cs → summary + figure audit → criticism + solution-
independent problem restatement) → canon three-pass workbook (using 11's line receipts as the
answer key) → exposition diff lab (Part-Time Parliament §3 vs Paxos Made Simple — what changed
in the TELLING) → 3m+1 simulator (the impossible 3-general/1-traitor case + working OM(1)
4-general case) → citation-convergence explorer (stretch; needs a citation API).

## Diagrams needed
- The reading loop: writer's rule → reader's rule → three passes → escalate-or-stop.
- The agreement chain as an exposition-quality gradient (obscure → crystal-clear).
- Impossibility-first pattern (locate the theorem → then the construction).
- Canon → spine map (which paper feeds 14/15/17/19/20/11).
- 3m+1: the 3-general impossibility vs the 4-general OM(1) success.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- VERIFIED this session: Lamport "State the Problem," Byzantine Generals 1982, Reaching
  Agreement 1980, Part-Time Parliament 1998 (+ reuse 11's Time/Clocks, FLP, Paxos Made
  Simple, Raft, Spanner, Gray&Lamport receipts).
- `[UNVERIFIED]` — fetch before prose: Keshav "How to Read a Paper" (three-pass timings,
  five-Cs labels, survey steps) + Roscoe/Mitzenmacher/Smith reviewing guidance (Part A
  method); MapReduce, GFS, Bigtable, Dynamo, Dapper, Tail at Scale, Chubby, ZooKeeper,
  Herlihy/Wing, End-to-End Arguments, Lampson "Hints" (Part B walkthroughs). NOTE: several
  (Tail, Dynamo, MapReduce/GFS/Bigtable/Spanner, Dapper, End-to-End) were UPGRADED→VERIFIED
  in Waves 7/8/9 — reconcile receipts at draft time; erase nothing.
- Citation-precision (not blockers): re-confirm Byzantine (TOPLAS 4(3) 382–401) + Reaching
  Agreement (JACM 27(2) 228–234) pagination; cite the 2000-corrected Part-Time Parliament.
- Deliberate boundary: 12 = reading method + walkthroughs, NOT re-derivation (depth lives in
  11/L + storage sub-courses). Method-by-genre (theory vs ML papers need different pass-3) is
  noted, unsourced — light touch only.
