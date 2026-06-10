# Research Brief — Sub-course 12 / Cluster B: The Paper Canon to Walk Through (catalog + verified anchors)

## Researcher: brain (manual) | Date: 2026-06-10 | Phase: 1 (research only — NO chapter prose)

12 is two halves: (A) *how to read a paper* (the method, see `_research_how-to-read-a-paper.md`), and (B) *which papers
to walk through, and why each one matters* — this file. The point of B is NOT to re-derive every paper (07–11 already
did that with line receipts); it is to (1) assemble the canon, (2) record which entries are already primary-verified
elsewhere in this repo so 12 can reuse those receipts as an answer key, and (3) verify a fresh sub-cluster of Lamport
foundation papers fetched THIS session that 11 did not cover.

**Network reality:** only `lamport.azurewebsites.net` reachable (HTTP 200). Every other academic/ACM/arXiv host = HTTP
000. So the freshly-verified additions below are all Lamport papers; the rest of the canon is either "verified elsewhere
in this repo" (cite the existing factcheck file) or `[UNVERIFIED from fetched source]` (fetch before Phase 2 prose).

---

## 1. Key mechanisms — the canon, organized as a teaching DAG

### 1.1 Fresh VERIFIED this session — the Lamport fault-tolerance trilogy (NEW, not in 11)
Fetched + extracted via `uv run --with pypdf` into `/tmp/substrate-12-sources/`. These are the natural "walkthrough"
exemplars because they are short, self-contained, and show the field's method (problem-first, impossibility-then-
algorithm) in its purest form.

- **Lamport, Shostak, Pease — "The Byzantine Generals Problem," ACM TOPLAS 4(3), July 1982, pp. 382–401**
  (`byz.pdf` → `byz.txt`, 20 pages). VERIFIED load-bearing claims:
  - Abstract (verbatim): "using only oral messages, this problem is solvable if and only if more than two-thirds of the
    generals are loyal; so a single traitor can confound two loyal generals. With unforgeable written messages, the
    problem is solvable for any number of generals and possible traitors." (`byz.txt` lines 9–11)
  - The `3m+1` bound (verbatim, line 156 / restated 229, 234): "no solution with fewer than 3m + 1 generals can cope
    with m traitors … to cope with m traitors, there must be at least 3m + 1 generals." Algorithm `OM(m)` solves it for
    `3m+1` or more (lines 235, 261).
  - The two conditions a solution must guarantee (the *problem statement first* — exactly Lamport's expository rule in
    action): A. "All loyal generals decide upon the same plan of action." B. "A small number of traitors cannot cause
    the loyal generals to adopt a bad plan." (`byz.txt` lines ~52–66)
  - Method exemplar: §2 is titled "IMPOSSIBILITY RESULTS" and proves the three-general/one-traitor case impossible
    BEFORE giving any algorithm — the canonical "impossibility then construction" shape (line 110).
- **Pease, Shostak, Lamport — "Reaching Agreement in the Presence of Faults," JACM 27(2), April 1980, pp. 228–234**
  (`reaching.pdf` → `reaching.txt`, 7 pages). VERIFIED:
  - Abstract (verbatim): "the problem is solvable for, and only for, n ≥ 3m + 1, where m is the number of faulty
    processors and n is the total number." And: with non-relaying (omission-only) faults "the problem is solvable for
    arbitrary n ≥ m ≥ 0. This weaker assumption can be approximated in practice using cryptographic methods."
    (`reaching.txt` abstract block)
  - Introduces **interactive consistency** as the formal frame (abstract + §1). This is the earlier (1980) result that
    the 1982 Byzantine Generals paper re-tells with the famous metaphor — a great "two papers, one result, different
    exposition" teaching pair.
- **Lamport — "The Part-Time Parliament," ACM TOCS 16(2), May 1998, pp. 133–169** (the *original* Paxos; distinct from
  the 11-verified "Paxos Made Simple") (`lamport-paxos.pdf` → `lamport-paxos.txt`, 33 pages). VERIFIED:
  - It is the original Paxos paper and an exemplar of how *exposition can sink a great result*: the Greek-parliament
    allegory famously obscured the algorithm, motivating the later "Paxos Made Simple." The editor's note in the PDF
    (verbatim, lines 19–32) literally frames it as recovered-from-behind-a-filing-cabinet satire.
  - Verified core: the protocol "provides a new way of implementing the state-machine approach to the design of
    distributed systems" (abstract, line 13) and progress requires a **majority** ("majority set") in the chamber
    (lines 108, 461, 641, 1007–1008).
  - §4 "Relevance to Computer Science" / §4.1 "The State Machine Approach" (lines 1018–1075) is verified: servers
    transform client requests into state-machine commands, "A general algorithm ensures that all servers obtain the
    same sequence of commands, thereby ensuring that they all produce the same sequence of responses and state
    changes—assuming they all start from the same initial state." This is the bridge from consensus → replicated state
    machines, and explicitly attributes the state-machine approach to "[Lamport 1978]" (line 1052).
  - Teaching value: read alongside "Paxos Made Simple" (verified in 11) to make the reading-method point — *the same
    algorithm, two expositions, wildly different readability.* Direct payoff of Cluster A's Lamport "State the Problem"
    backbone.

### 1.2 Already VERIFIED elsewhere in this repo (reuse the receipts as answer keys)
These canon papers were fetched + line-verified in earlier waves; 12 walkthroughs should cite the existing factcheck
file rather than re-fetching:
- **Lamport, "Time, Clocks, and the Ordering of Events," CACM 1978** — verified in `11/_factcheck_phase1.md` (22
  claims, 0 blockers). Happened-before, logical clocks, state-machine approach origin.
- **Chandy & Lamport, "Distributed Snapshots," ACM TOCS 1985** — verified in `11/_factcheck_phase1.md`.
- **Fischer, Lynch, Paterson (FLP), JACM 1985** — verified in `11/_factcheck_phase1.md` (asynchronous impossibility).
- **Lamport, "Paxos Made Simple," 2001** — verified/extracted, `11/_factcheck_cluster2.md` + `_cluster3.md`.
- **Ongaro & Ousterhout, "Raft," USENIX ATC 2014** — verified in `11/_factcheck_cluster3.md`.
- **Corbett et al., "Spanner," OSDI 2012** — verified in `11/_factcheck_cluster3.md` + `_cluster4.md`.
- **Gray & Lamport, "Consensus on Transaction Commit," ACM TODS 2006** — verified in `11/_factcheck_cluster4.md`.
- Storage/database canon partially anchored to production source (not papers) in 06–09 factchecks: B-tree/LSM/Bloom
  mechanics (`06`), BusTub/Postgres/InnoDB internals (`07`), Redis/Memcached + Facebook-Memcached NSDI 2013 (`08`),
  Kafka design docs + KIP-98 (`09`).

### 1.3 Canon still `[UNVERIFIED from fetched source]` — the walkthrough wishlist (fetch before Phase 2)
Google systems trilogy + scaling/observability classics, all network-blocked this session:
- **Dean & Ghemawat, "MapReduce," OSDI 2004.**
- **Ghemawat, Gobioff, Leung, "The Google File System (GFS)," SOSP 2003.**
- **Chang et al., "Bigtable," OSDI 2006.**
- **DeCandia et al., "Dynamo," SOSP 2007** (also a carried-forward 11 gap).
- **Sigelman et al., "Dapper," Google tech report 2010** (distributed tracing — feeds sub-course 19).
- **Dean & Barroso, "The Tail at Scale," CACM 2013** (feeds 20).
- **Burrows, "The Chubby Lock Service," OSDI 2006**; **Hunt et al., "ZooKeeper," USENIX ATC 2010.**
- **Herlihy & Wing, "Linearizability," TOPLAS 1990** (carried-forward 11 gap).
- Method-canon cross-cut: **Saltzer/Reed/Clark "End-to-End Arguments," 1984** (anchored in 03's index),
  **Lampson "Hints for Computer System Design," 1983.**
All `[UNVERIFIED from fetched source]` — do not write exact quotes/figures until fetched.

### 1.4 The teaching DAG (which paper unlocks which)
A defensible reading order for the walkthroughs, by dependency:
1. **Method first** (Cluster A: Lamport "State the Problem" verified; Keshav three-pass `[UNVERIFIED]`).
2. **Ordering & impossibility** — Time/Clocks → FLP (both verified in 11).
3. **Agreement under faults** — Reaching Agreement (1980) → Byzantine Generals (1982) [both fresh-verified here] →
   Part-Time Parliament (1998) → Paxos Made Simple (2001) → Raft (2014). This chain is the single best
   "same-problem-told-five-ways" spine for teaching the *reading* skill, because four of the five are already verified.
4. **Replicated state machines & transactions** — Spanner, Gray&Lamport (verified in 11).
5. **Scale-out storage** — GFS → MapReduce → Bigtable → Dynamo (all `[UNVERIFIED]`, fetch later).
6. **Operating at scale** — Dapper, The Tail at Scale (`[UNVERIFIED]`; feed 19/20).

---

## 2. Foundational sources

**VERIFIED / fetched this session (`/tmp/substrate-12-sources/`):**
- Lamport, "State the Problem Before Describing the Solution" — `lamport.azurewebsites.net/pubs/state-the-problem.pdf`.
- Lamport/Shostak/Pease, "The Byzantine Generals Problem," TOPLAS 1982 — `lamport.azurewebsites.net/pubs/byz.pdf`.
- Pease/Shostak/Lamport, "Reaching Agreement in the Presence of Faults," JACM 1980 —
  `lamport.azurewebsites.net/pubs/reaching.pdf`.
- Lamport, "The Part-Time Parliament" (original Paxos), TOCS 1998 — `lamport.azurewebsites.net/pubs/lamport-paxos.pdf`.

**VERIFIED elsewhere in this repo:** see §1.2 (point at the named `11/_factcheck_*.md`, `06–09/_factcheck_phase1.md`).

**`[UNVERIFIED from fetched source]`:** MapReduce, GFS, Bigtable, Dynamo, Dapper, Tail at Scale, Chubby, ZooKeeper,
Herlihy/Wing, End-to-End Arguments, Lampson Hints, Keshav (§1.3 + Cluster A). Network-blocked this session.

---

## 3. Why it is this way — the forcing functions

1. **A reading course needs a fixed, high-signal corpus.** Citation convergence (Cluster A §1.2) repeatedly surfaces
   the same ~15 papers; teaching the *method* on random papers wastes the lesson. Use the convergent canon.
2. **The agreement chain is the ideal teaching spine** because the *same problem* (get nodes to agree despite faults)
   is told five ways with escalating clarity — Reaching Agreement (formal, terse) → Byzantine Generals (metaphor) →
   Part-Time Parliament (allegory, infamously unreadable) → Paxos Made Simple (the rewrite) → Raft (designed *for*
   understandability). It is a live demonstration of Cluster A's whole thesis: exposition is a property of papers worth
   grading, and the same result can be near-unreadable or crystal-clear.
3. **Reuse beats re-fetch.** 07–11 already paid the cost of verifying much of the canon with line receipts; 12 should
   stand on those receipts, not redo them, and spend its scarce network budget on the still-blocked storage trilogy.
4. **Impossibility-then-construction is the field's signature move** (verified in Byzantine §2 and FLP). Teaching readers
   to find the impossibility result first is teaching them where the real constraint lives.

---

## 4. Common misconceptions to preempt

- "Paxos is impossible to understand / was always badly explained." → The Part-Time Parliament was deliberately obscure
  (allegory); Paxos Made Simple and Raft are the antidotes. The algorithm isn't the problem; the *first exposition* was.
- "Byzantine fault tolerance needs `2f+1`." → No: crash/omission tolerance can use `2f+1`, but *Byzantine* (arbitrary,
  lying) faults need `3m+1` with oral messages (VERIFIED, Byzantine + Reaching Agreement). Signatures relax this.
- "Reaching Agreement and Byzantine Generals are different results." → They are the *same* `3m+1` result; the 1982 paper
  is the famous re-telling of the 1980 one with the metaphor. (VERIFIED across both abstracts.)
- "The canon is networking/theory trivia." → Each entry maps to a Part II/III sub-course (Spanner→15, Dynamo→15,
  GFS/Bigtable→14, Dapper→19, Tail at Scale→20, MapReduce→17). The canon IS the foundation of the headline course.
- "You must read every paper end-to-end." → Cluster A's whole point: triage, and only go deep on the canon you'll build
  on, review, or teach.

---

## 5. Best build-your-own target(s)

- **The canon three-pass workbook:** for each agreement-chain paper, the learner fills the three-pass artifact, using
  the existing `11/_factcheck_*` line receipts as the answer key for "did I find the load-bearing claim?"
- **Exposition diff lab:** read Part-Time Parliament §3 vs Paxos Made Simple's protocol section, and write down *what
  changed in the telling* (not the algorithm). Makes Cluster A's thesis tangible.
- **`3m+1` simulator:** a tiny commander/lieutenant message-passing toy that reproduces the impossible 3-general /
  1-traitor case and the working 4-general / 1-traitor case (`OM(1)`). Directly from verified Byzantine §3.

All build-lab candidates only. Do NOT start `/build` during Phase 1.

---

## 6. Open questions / gaps (DO NOT erase on later edits)

- **Storage trilogy unfetched (HIGH):** MapReduce, GFS, Bigtable, Dynamo all `[UNVERIFIED from fetched source]`
  (network-blocked). These are the most-requested walkthroughs and must be fetched before Phase 2 prose.
- **Ops classics unfetched:** Dapper, The Tail at Scale, Chubby, ZooKeeper — `[UNVERIFIED]`. Feed 19/20/L.
- **Method-canon cross-cuts unfetched:** End-to-End Arguments, Lampson "Hints," Herlihy/Wing — `[UNVERIFIED]`.
- **Citation pinning:** Reaching Agreement page range (JACM 27(2), pp.228–234) and Byzantine (TOPLAS 4(3), pp.382–401)
  read from the PDF text/headers; re-confirm exact pagination against the ACM record before Phase 2 if precise
  citations are required.
- **Scope note (not a gap):** 12 is *paper-walkthroughs + reading method*, NOT a re-derivation of each result — that
  depth lives in 11/L and the storage sub-courses. Deliberate boundary.
