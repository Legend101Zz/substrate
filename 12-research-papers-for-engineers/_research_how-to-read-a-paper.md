# Research Brief — Sub-course 12 / Cluster A: How to Read (and Reason About) a Research Paper

## Researcher: brain (manual, after `researcher` subagent returned source-starved) | Date: 2026-06-10 | Phase: 1 (research only — NO chapter prose)

**Network reality this session:** Only `lamport.azurewebsites.net` resolved (HTTP 200). Every academic / ACM / arXiv /
raw.github host timed out (HTTP 000), including the Keshav "How to Read a Paper" PDF across five mirrors (Stanford,
SIGCOMM CCR, UNB, ACM DOI, Harvard/Mitzenmacher). The `researcher` subagent independently confirmed zero primary
fetches for the method sources. Therefore every claim about **Keshav / Roscoe / Mitzenmacher / Smith** below is tagged
`[UNVERIFIED from fetched source]`. The one method primary we COULD fetch and verify is **Lamport, "State the Problem
Before Describing the Solution"** — used here as the verified backbone of the reading method.

---

## 1. Key mechanisms

### 1.1 Lamport's expository rule — the reader's mirror image (VERIFIED primary)
Lamport's one-page note "State the Problem Before Describing the Solution" (SRI International; reprinted in *ACM SIGSOFT
Software Engineering Notes*, p.26 of the scan) gives the rule a paper *should* be organized by, and therefore the rule a
**reader** should use to interrogate a paper. Verified from the fetched text (`state-the-problem.txt`, full 1 page):

- The flawed-but-common organization: "(1) a brief informal statement of the problem; (2) the solution; (3) a statement
  and proof of the precise correctness properties satisfied by the solution." (verbatim)
- The organization Lamport urges instead: "(1) a brief informal statement of the problem; (2) the precise correctness
  conditions required of a solution; (3) the solution; (4) a proof that the solution satisfies the requisite
  conditions." (verbatim)
- The load-bearing why: in the first form "the precise correctness conditions can be (and usually are) stated in terms
  of the solution itself … it is often not clear exactly what problem is being solved. This makes the comparison of two
  different solutions rather difficult." (verbatim)
- The second form "forces [you] to specify the precise problem to be solved independently of the method used in the
  solution. This can be a surprisingly difficult and enlightening task. It has on several occasions led me to discover
  that a 'correct' algorithm did not really accomplish what I wanted it to." (verbatim)
- Closing barb (verbatim): "(I am ignoring as unworthy of consideration the disturbingly large number of papers that
  never even attempt a precise statement of what problem they are solving.)"

**Reader's mechanism derived from this:** the first job when reading any systems/theory paper is to extract the
problem statement and the *correctness conditions stated independently of the solution*. If the paper only states
correctness in terms of its own mechanism, the reader must reconstruct the solution-independent spec themselves — this
reconstruction is exactly Keshav's "pass 3," and the failure to do it is how readers get fooled by a paper that
"proves" a property that is really just a restatement of what the algorithm does. This is verified and is the spine of
Cluster A; the Keshav three-pass structure (below) is the popular operationalization but is unverified this session.

### 1.2 The three-pass method (Keshav 2007) — `[UNVERIFIED from fetched source]`
Widely-reproduced staged-triage protocol. Could not be fetched; the specifics below (pass timings, "five Cs" labels)
are training-data recall, NOT verified primary text, and must be fetched before Phase 2 prose.
- **Pass 1 (quick scan, ~5–10 min):** title, abstract, intro, section headings, conclusion; glance at references. End
  by answering the "five Cs": **Category, Context, Correctness, Contributions, Clarity.** Decide whether to continue.
- **Pass 2 (careful read, ~1 hr):** read carefully but skip proofs; scrutinize figures/tables (axes, error bars,
  baselines); mark references to follow. Goal: be able to summarize the paper with its evidence.
- **Pass 3 (virtual re-implementation, ~hours):** put the paper down and try to reconstruct it from scratch; challenge
  every assumption; find hidden assumptions, weak experiments, missing citations. Required before building on,
  reviewing, or teaching a paper.
- **Literature-survey extension:** find 3–5 recent highly-cited papers, pass-1 them, follow **citation convergence**
  (papers cited by many of them are foundational), then go to the key authors' venues and scan recent proceedings.
- ALL of §1.2 is `[UNVERIFIED from fetched source]`.

### 1.3 Systems-paper adversarial reading (Roscoe / Smith / Mitzenmacher) — `[UNVERIFIED from fetched source]`
Reviewing-guidance synthesis (sources network-blocked):
- Spend disproportionate time in the **evaluation + methodology** sections — that is where claims are easiest to
  oversell and hardest to fake honestly. Ask: is the baseline fair? is the workload representative? where does the
  system do *worse*, and does the paper admit it?
- A missing citation is an *epistemic claim* ("nobody has done this"), not a stylistic slip — check it.
- The reviewer's five questions (important problem? novel? correct? honest evaluation? well-presented?) map onto
  Keshav's five Cs from the production side; adopting the reviewer mindset forces pass-3 reading.
- All of §1.3 is `[UNVERIFIED from fetched source]`.

### 1.4 Why a paper canon exists at all (cross-link to Cluster B)
Reading method is worthless without high-signal targets. The systems field has a stable, citation-convergent canon
(MapReduce, GFS, Bigtable, Dynamo, Spanner, Paxos, Raft, FLP, Lamport time-clocks, The Tail at Scale, Dapper, …). The
forcing function: top venues (SOSP, OSDI, NSDI, USENIX ATC, VLDB, SIGMOD) concentrate signal, and the same handful of
papers keep reappearing in reference lists across decades — the convergence signal §1.2 relies on. Cluster B is the
catalog and is heavily VERIFIED (Lamport primaries fetched this session + the line-verified canon already in 07–11).

---

## 2. Foundational sources

**VERIFIED / fetched this session:**
- Lamport, "State the Problem Before Describing the Solution," SRI International (1-page note; reprinted *ACM SIGSOFT
  SEN*) — `lamport.azurewebsites.net/pubs/state-the-problem.pdf` (HTTP 200, extracted full text).

**`[UNVERIFIED from fetched source]` — network-blocked, fetch before Phase 2:**
- S. Keshav, "How to Read a Paper," *ACM SIGCOMM CCR* 37(3), July 2007, pp. 83–84 (three-pass method, five Cs,
  literature survey). DOI `10.1145/1273445.1273458`. Mirrors tried (all HTTP 000): `ccr.sigcomm.org/online/files/
  p83-keshavA.pdf`, `web.stanford.edu/class/ee384m/Handouts/HowtoReadPaper.pdf`, `cs.unb.ca/.../Keshav_2007_HReadPaper.pdf`.
- T. Roscoe, "Writing Reviews for Systems Conferences" (reviewing/reading heuristics) — `cl.cam.ac.uk` blocked.
- M. Mitzenmacher, "How to Read a Research Paper," Harvard — `eecs.harvard.edu/~michaelm/postscripts/ReadPaper.pdf` blocked.
- A. J. Smith, "The Task of the Referee," *IEEE Computer*, 1990 — no reachable URL; pub details are training-data recall.

---

## 3. Why it is this way — the forcing functions

1. **Papers front-load signal** (abstract → intro → conclusion) because expert readers have always triaged there; a
   staged read exploits the structure instead of fighting it. *(method rationale; structurally sound, but the specific
   Keshav framing is `[UNVERIFIED]`.)*
2. **Time is the budget.** A researcher processes dozens of papers/month; you cannot deep-read all of them, so you need
   an explicit escalation rule (only go to pass 3 to build on / review / teach). *(`[UNVERIFIED]` framing.)*
3. **Correctness ≠ comprehension** (VERIFIED via Lamport §1.1): if a paper states its correctness condition *in terms
   of its own solution*, understanding the mechanism tells you nothing about whether it solves the real problem. The
   reader must reconstruct a solution-independent spec — the hard, enlightening task Lamport describes.
4. **Citation convergence beats keyword search** because terminology drifts ("log-structured" vs "write-optimized") but
   shared references are concept-agnostic evidence of foundational status. *(`[UNVERIFIED]` framing.)*

---

## 4. Common misconceptions to preempt

- "Read top-to-bottom once, carefully." → conflates triage, comprehension, and critique; reading related-work before
  you understand the contribution is backwards.
- "If I understand it, it's correct." → comprehension is pass 2; correctness needs pass 3 and (per Lamport) a
  solution-independent restatement of the problem.
- "The abstract gives you the paper." → the abstract is the most polished, most novelty-overstating part; the real
  contribution lives in the results, the real limits between the lines of the evaluation.
- "A proof of correctness means it's correct." → only if the correctness *condition* is stated independently of the
  solution (Lamport's whole point). A proof that the algorithm does what the algorithm does is vacuous.
- "Surveys give you the bibliography." → a survey is a biased snapshot; citation convergence across recent primaries is
  more reliable.
- "Pass 3 is just reading more." → pass 3 is active re-derivation with the paper closed, not extended passive reading.

---

## 5. Best build-your-own target(s)

- **Structured three-pass reading log:** a per-paper Markdown template — pass 1 (five Cs), pass 2 (one-paragraph
  summary + figure audit), pass 3 (strongest criticism + 3 follow-ups + a *solution-independent* restatement of the
  problem à la Lamport). Operationalizes the method as a habit.
- **Canon annotation harness for Substrate itself:** for each paper Cluster B walks through, the learner produces the
  three-pass artifact. Directly reuses the already-verified line receipts in 07–11 factchecks as an answer key.
- **Citation-convergence explorer (stretch):** build the snowball survey as a graph traversal (nodes = papers, edges =
  cited-by; centrality surfaces the canon). Needs a reachable citation API — out of scope while the network is blocked.

All build-lab candidates only. Do NOT start `/build` during Phase 1.

---

## 6. Open questions / gaps (DO NOT erase on later edits)

- **HIGH — Keshav primary unfetched.** Three-pass timings, the five-Cs labels, and the literature-survey steps are all
  `[UNVERIFIED from fetched source]`. Fetch `p83-keshavA.pdf` and verify before any Phase 2 prose.
- **Roscoe / Mitzenmacher / Smith unfetched.** All reviewing-mindset claims (§1.3, §3, §4) are `[UNVERIFIED]`.
- **Method-by-genre gap.** Keshav is systems-flavored. Theory papers (check the proof steps) and modern ML papers
  (architecture + training + benchmark tables) need different pass-3 behavior; not sourced.
- **Digital-first reading gap.** Keshav predates arXiv-era click-through reading; whether the method changes with
  hyperlinked references is unaddressed by any fetched source.
- **"What to do when a paper is wrong"** (replication, retraction, commentary norms) is outside Keshav and unsourced.
