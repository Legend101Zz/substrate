# Research Brief (RECONCILED) — Sub-course 12: Research Papers for Engineers

## Reconciler: brain | Date: 2026-06-10 | Phase: 1 (research only — NO chapter prose)

This is the reconciled `_research.md` for sub-course 12, synthesizing two factchecked source clusters (ADR-001: each
cluster keeps its own deep `_research_<cluster>.md`; this file reconciles and consolidates). For exact line receipts,
read the cluster files and `_factcheck_phase1.md`.

### Cluster files and their factcheck
1. **How to read (and reason about) a research paper — the method** — `_research_how-to-read-a-paper.md`.
2. **The paper canon to walk through — catalog + verified anchors** — `_research_paper-canon-walkthroughs.md`.
   Both checked in `_factcheck_phase1.md` (Cluster A: 4 VERIFIED + 2 flagged; Cluster B: 9 VERIFIED + 2 flagged groups;
   **0 blockers**).

### Coverage honesty statement
12 has two jobs: teach the *reading method*, and *walk through the canon*. This corpus covers both honestly but
**unevenly by design**, because the network only allowed `lamport.azurewebsites.net`:
- The **method** is anchored by ONE freshly-verified primary — Lamport, "State the Problem Before Describing the
  Solution" — which is genuinely the engineer's reading rule. The popular Keshav three-pass framing on top of it is
  `[UNVERIFIED from fetched source]` (PDF blocked across 5 mirrors) and must be fetched before Phase 2 prose.
- The **canon** gained FOUR freshly-verified Lamport primaries this session (Byzantine Generals, Reaching Agreement,
  The Part-Time Parliament, plus the method note), and reuses the canon already line-verified in 06–11. The Google
  storage trilogy + ops classics (MapReduce/GFS/Bigtable/Dynamo/Dapper/Tail at Scale) remain `[UNVERIFIED]` —
  network-blocked, honestly flagged, NOT laundered.

This is enough to reconcile and to design 12's Phase-2 shape, with the blocked sources carried as gaps. We did not fake
completeness; raccoon-shaped documentation was actively avoided.

---

## 1. Key mechanisms (cross-cluster synthesis)

12's thesis: **reading a paper is an active, staged, adversarial skill — and the systems canon is the high-signal
training set on which to practice it.** Method and corpus are two halves of one loop.

### 1.1 The reader's rule comes from the writer's rule (VERIFIED — cluster A)
Lamport's expository rule — *state the precise correctness conditions independently of the solution, then give the
solution, then prove it meets them* — is the reader's interrogation checklist. The first question a reader must answer
is: *what problem does this paper actually solve, stated independently of its own mechanism?* If the paper only defines
correctness in terms of its own algorithm, the proof is near-vacuous and the reader must reconstruct the real spec
themselves. Lamport reports this reconstruction has caught "correct" algorithms that didn't do what he wanted —
i.e., comprehension ≠ correctness. *(All four sub-claims VERIFIED from `state-the-problem.txt`.)*

### 1.2 The three-pass triage operationalizes the rule (`[UNVERIFIED]` — cluster A)
Keshav's three-pass method (pass 1 quick scan + five Cs → pass 2 careful read + figure audit → pass 3 virtual
re-implementation), plus the citation-convergence literature survey, is the standard operational protocol layered on
top of §1.1. All timings, the five-Cs labels, and the survey steps are `[UNVERIFIED from fetched source]` (Keshav PDF
blocked). Reviewing-mindset guidance (Roscoe/Mitzenmacher/Smith) is likewise `[UNVERIFIED]`.

### 1.3 The agreement chain is the ideal teaching spine (mostly VERIFIED — cluster B)
The single best corpus for *teaching the reading skill* is the consensus/fault-tolerance lineage, because the **same
problem is told five ways with escalating clarity**, and four of the five are already primary-verified:
- **Reaching Agreement (1980, VERIFIED):** `n ≥ 3m+1` necessary and sufficient for interactive consistency under
  arbitrary faults; with omission-only faults, arbitrary `n ≥ m ≥ 0` (approximable with cryptography). Terse, formal.
- **Byzantine Generals (1982, VERIFIED):** the same `3m+1` result retold with the metaphor; oral messages need
  `> 2/3` loyal, signed messages tolerate any number; §2 proves impossibility *before* constructing `OM(m)`.
- **The Part-Time Parliament (1998, VERIFIED):** original Paxos; "a new way of implementing the state-machine
  approach"; progress needs a majority; the editor's-note allegory is the field's most famous *exposition failure*.
- **Paxos Made Simple (2001, VERIFIED in 11):** the rewrite that made Paxos teachable.
- **Raft (2014, VERIFIED in 11):** consensus designed *for* understandability — the thesis of Cluster A as a paper.
This chain literally demonstrates Cluster A: exposition is a gradeable property, and the same result spans
near-unreadable → crystal-clear.

### 1.4 The canon maps onto the headline course (cluster B)
Each canon paper feeds a Part II/III sub-course: Time/Clocks + FLP + Paxos/Raft + Spanner + Gray&Lamport → 11/15/L
(all VERIFIED in 11); GFS/Bigtable → 14, Dynamo/Spanner → 15, MapReduce → 17, Dapper → 19, Tail at Scale → 20 (storage/
ops set `[UNVERIFIED]`, fetch later). 12 is not trivia; it is the foundation the headline draws on.

### 1.5 The field's signature move: impossibility, then construction (VERIFIED — cluster B)
Byzantine §2 and FLP both prove what *cannot* be done before showing what can. Teaching readers to locate the
impossibility result first teaches them where the real constraint lives — the highest-leverage reading habit.

---

## 2. Foundational sources (consolidated)

**VERIFIED / fetched this session (`/tmp/substrate-12-sources/`):**
- Lamport, "State the Problem Before Describing the Solution," SRI/ACM SIGSOFT SEN — `…/pubs/state-the-problem.pdf`.
- Lamport, Shostak, Pease, "The Byzantine Generals Problem," ACM TOPLAS 4(3) 1982 — `…/pubs/byz.pdf`.
- Pease, Shostak, Lamport, "Reaching Agreement in the Presence of Faults," JACM 27(2) 1980 — `…/pubs/reaching.pdf`.
- Lamport, "The Part-Time Parliament" (original Paxos), ACM TOCS 16(2) 1998 (2000-corrected) — `…/pubs/lamport-paxos.pdf`.

**VERIFIED elsewhere in this repo (reuse the receipts):** Time/Clocks 1978, Chandy-Lamport 1985, FLP 1985, Paxos Made
Simple 2001, Raft 2014, Spanner 2012, Gray&Lamport 2006 (all in `11/_factcheck_*.md`); storage/cache/MQ production
internals in `06–09/_factcheck_phase1.md`.

**`[UNVERIFIED from fetched source]` — fetch before Phase 2 prose:**
- Keshav "How to Read a Paper" CCR 2007; Roscoe reviewing guide; Mitzenmacher; Smith "Task of the Referee."
- MapReduce (OSDI 2004), GFS (SOSP 2003), Bigtable (OSDI 2006), Dynamo (SOSP 2007), Dapper (2010), The Tail at Scale
  (CACM 2013), Chubby (OSDI 2006), ZooKeeper (ATC 2010), Herlihy/Wing "Linearizability" (TOPLAS 1990),
  Saltzer/Reed/Clark "End-to-End Arguments" (1984), Lampson "Hints for Computer System Design" (1983).

---

## 3. Why it is this way — the forcing functions (consolidated)

1. **Reading is a budget problem.** Dozens of papers/month → staged triage with an explicit escalate-to-pass-3 rule
   (build / review / teach). *(`[UNVERIFIED]` framing; structurally sound.)*
2. **Comprehension ≠ correctness** (VERIFIED via Lamport): if correctness is stated in terms of the solution, you must
   reconstruct the solution-independent spec to judge the paper at all.
3. **A reading course needs a fixed, convergent corpus.** Citation convergence surfaces the same ~15 papers; teach the
   method on them, not on noise.
4. **The agreement chain is pedagogically perfect** because exposition quality varies wildly across re-tellings of one
   result — the live proof of why reading method matters. *(VERIFIED across the four fetched Lamport papers.)*
5. **Reuse beats re-fetch.** 06–11 already verified much canon; 12 stands on those receipts and spends scarce network
   budget on the still-blocked storage trilogy.
6. **Impossibility-first is the field's method** (VERIFIED, Byzantine §2 + FLP).

---

## 4. Common misconceptions to preempt (consolidated)

- "Read top-to-bottom once, carefully." → conflates triage / comprehension / critique.
- "If I understand it, it's correct." → correctness needs pass 3 + a solution-independent restatement (Lamport).
- "A correctness proof means it's correct." → only if the *condition* is stated independently of the solution.
- "Paxos was always badly explained." → Part-Time Parliament was deliberately obscure; Paxos Made Simple/Raft fixed it.
- "BFT needs `2f+1`." → crash/omission can use `2f+1`; *Byzantine* needs `3m+1` (oral) — signatures relax it. (VERIFIED.)
- "Reaching Agreement and Byzantine Generals are different results." → same `3m+1`, different exposition. (VERIFIED.)
- "The canon is theory trivia." → it is the literal foundation of the headline System Design course.
- "You must read every paper end-to-end." → triage; go deep only on the canon you'll build/review/teach.

---

## 5. Best build-your-own targets (consolidated)

- **Structured three-pass reading log** (five Cs → summary + figure audit → criticism + solution-independent problem
  restatement). Operationalizes the method.
- **Canon three-pass workbook** using the existing `11/_factcheck_*` line receipts as the answer key.
- **Exposition diff lab:** Part-Time Parliament §3 vs Paxos Made Simple — record what changed in the *telling*.
- **`3m+1` simulator:** reproduce the impossible 3-general/1-traitor case and the working `OM(1)` 4-general case.
- **Citation-convergence explorer (stretch):** snowball survey as graph traversal; needs a reachable citation API.

All build-lab candidates only. Do NOT start `/build` during Phase 1.

---

## 6. Open questions / gaps (consolidated — DO NOT erase on later edits)

**Network-blocked sources to fetch before Phase 2 prose:**
- **Method (HIGH):** Keshav "How to Read a Paper" — three-pass timings, five-Cs labels, literature-survey steps all
  `[UNVERIFIED]`. Plus Roscoe / Mitzenmacher / Smith reviewing guidance.
- **Storage trilogy (HIGH):** MapReduce, GFS, Bigtable, Dynamo — `[UNVERIFIED]`; the most-requested walkthroughs.
- **Ops/coordination classics:** Dapper, The Tail at Scale, Chubby, ZooKeeper — `[UNVERIFIED]` (feed 19/20/L).
- **Method-canon cross-cuts:** Herlihy/Wing, End-to-End Arguments, Lampson "Hints" — `[UNVERIFIED]`.

**Citation-precision items (not blockers):**
- Re-confirm Byzantine (TOPLAS 4(3), pp.382–401) and Reaching Agreement (JACM 27(2), pp.228–234) pagination against the
  ACM record; cite the 2000-corrected Part-Time Parliament.

**Method-by-genre gap (not a blocker):** Keshav is systems-flavored; theory papers (check proof steps) and ML papers
(architecture + training + benchmark tables) need different pass-3 behavior; unsourced.

**Scope note (deliberate boundary, not a gap):** 12 = reading method + paper walkthroughs, NOT re-derivation of each
result (that depth lives in 11/L and the storage sub-courses).

**Carry-forward from 11 (attempted this session, still blocked):** the opportunistic step-5 fetch of the 11 CAP/PACELC
primaries (Gilbert/Lynch 2002, Brewer, Abadi), Herlihy/Wing, and Dynamo was retried this session and remained HTTP 000
on every academic/ACM host. The 11 `[UNVERIFIED]` flags stand unchanged; do not erase them.
