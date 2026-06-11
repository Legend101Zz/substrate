# Factcheck — Sub-course 12 (research-papers-for-engineers), Phase 1 clusters A + B

## Factchecker: brain (manual; `researcher` subagent confirmed zero method-source fetches) | Date: 2026-06-10

Scope: the load-bearing claims in `_research_how-to-read-a-paper.md` (Cluster A) and
`_research_paper-canon-walkthroughs.md` (Cluster B). Sources fetched this session live in
`/tmp/substrate-12-sources/` (extracted via a throwaway `uv run --with pypdf` on the Walmart index). Network reality:
only `lamport.azurewebsites.net` reachable (HTTP 200); all academic/ACM/arXiv/raw.github hosts HTTP 000.
`/Users/m0t0hu6/.code-puppy-venv` was NOT modified; Code Puppy was NOT reinstalled.

Verdict legend: **VERIFIED** (exact text receipt) · **NEEDS-SOURCE (properly flagged)** (brief marks `[UNVERIFIED]`) ·
**BLOCKER** (load-bearing, wrong/unflagged — none found).

---

## Cluster A — reading method

| # | Claim | Verdict | Receipt / note |
|---|-------|---------|----------------|
| A1 | Lamport's flawed-but-common paper organization: (1) informal problem, (2) solution, (3) correctness stated/proved. | **VERIFIED** | `state-the-problem.txt` verbatim list. |
| A2 | Lamport's urged organization: (1) informal problem, (2) precise correctness conditions, (3) solution, (4) proof it satisfies them. | **VERIFIED** | `state-the-problem.txt` verbatim. |
| A3 | The "why": in the flawed form, correctness conditions are stated in terms of the solution itself, so it's unclear what problem is solved and solutions can't be compared. | **VERIFIED** | `state-the-problem.txt` verbatim ("stated in terms of the solution itself … comparison of two different solutions rather difficult"). |
| A4 | Specifying the problem independently "has on several occasions led me to discover that a 'correct' algorithm did not really accomplish what I wanted." | **VERIFIED** | `state-the-problem.txt` verbatim. |
| A5 | Keshav three-pass method, five Cs (Category/Context/Correctness/Contributions/Clarity), pass timings, literature-survey steps. | **NEEDS-SOURCE (properly flagged)** | Keshav PDF HTTP 000 across 5 mirrors; brief tags every such claim `[UNVERIFIED from fetched source]`. Training-data recall only. |
| A6 | Roscoe / Mitzenmacher / Smith reviewing-mindset heuristics. | **NEEDS-SOURCE (properly flagged)** | All hosts blocked; brief tags `[UNVERIFIED]`. |

No Cluster A blockers. The verified Lamport backbone carries the section; the Keshav/Roscoe/Smith specifics are honestly
flagged and must be fetched before Phase 2 prose.

---

## Cluster B — paper canon

| # | Claim | Verdict | Receipt / note |
|---|-------|---------|----------------|
| | B1 | Byzantine Generals: "solvable if and only if more than two-thirds of the generals are loyal; so a single traitor can confound two loyal generals" (oral messages); written/signed messages solvable for any number. | **VERIFIED** | `byz.txt` lines 9–11 (abstract), verbatim. |
| B2 | Byzantine `3m+1` bound: no solution with fewer than `3m+1` generals copes with `m` traitors; `OM(m)` works for `3m+1`+. | **VERIFIED** | `byz.txt` lines 156, 229, 234–235, 261. |
| B3 | Byzantine conditions A ("All loyal generals decide upon the same plan of action") and B ("A small number of traitors cannot cause the loyal generals to adopt a bad plan"). | **VERIFIED** | `byz.txt` lines ~52–66, verbatim. |
| B4 | Byzantine §2 is "IMPOSSIBILITY RESULTS" and proves the 3-general/1-traitor case impossible before giving an algorithm. | **VERIFIED** | `byz.txt` line 110 (section heading), 154–156. |
| B5 | Reaching Agreement: "solvable for, and only for, n ≥ 3m+1"; with omission-only (non-relaying) faults "solvable for arbitrary n ≥ m ≥ 0 … approximated in practice using cryptographic methods"; framed via interactive consistency. | **VERIFIED** | `reaching.txt` lines 12, 14, 38, 75, 77, 82–83. |
| B6 | Reaching Agreement (1980) and Byzantine Generals (1982) are the same `3m+1` result, the latter retelling the former with the metaphor. | **VERIFIED (inference, well-supported)** | Both abstracts state identical `3m+1`; shared authors (Pease/Shostak/Lamport ↔ Lamport/Shostak/Pease). Reasonable teaching claim, not a quoted assertion. |
| B7 | Part-Time Parliament is the original Paxos; "provides a new way of implementing the state-machine approach"; progress needs a majority. | **VERIFIED** | `lamport-paxos.txt` line 13 (abstract), majority at lines 108/461/641/1007–1008. |
| B8 | Part-Time Parliament was deliberately obscure (editor's-note allegory framing); read alongside Paxos Made Simple to show exposition matters. | **VERIFIED** | `lamport-paxos.txt` lines 19–32 (editor's note, verbatim satire). |
| B9 | §4.1 state-machine approach: a general algorithm ensures all servers obtain the same command sequence → same responses/state, assuming same initial state; attributes the approach to [Lamport 1978]. | **VERIFIED** | `lamport-paxos.txt` lines 1018–1075 verbatim; attribution line 1052. |
| B10 | Time/Clocks, Chandy-Lamport, FLP, Paxos Made Simple, Raft, Spanner, Gray&Lamport "verified elsewhere in this repo." | **VERIFIED (cross-reference)** | Confirmed present in `11/_factcheck_phase1.md`, `_cluster2.md`, `_cluster3.md`, `_cluster4.md`. |
| B11 | MapReduce, GFS, Bigtable, Dynamo, Dapper, Tail at Scale, Chubby, ZooKeeper, Herlihy/Wing, End-to-End, Lampson Hints — canon to walk through. | **NEEDS-SOURCE (properly flagged)** | All HTTP 000 this session; brief tags `[UNVERIFIED from fetched source]`. |
| B12 | Byzantine needs `3m+1`, but crash/omission tolerance can use `2f+1` (misconception §4). | **VERIFIED (Byzantine half)** | `3m+1` verified per B2/B5; the `2f+1` crash bound is the standard consensus result also referenced in 11/_factcheck_cluster4 (Gray&Lamport `2F+1`). Consistent. |

No Cluster B blockers. 0 unsupported/misattributed claims. 4 fresh Lamport primaries verified this session; the
unfetched storage/ops canon is honestly flagged.

---

## Citation-precision warnings (carry-forward, not blockers)
- W1 — Byzantine TOPLAS 4(3) pp.382–401 and Reaching Agreement JACM 27(2) pp.228–234 page ranges read from PDF
  text/running headers; re-confirm against the ACM record if exact pagination is needed for Phase 2.
- W2 — Part-Time Parliament is TOCS 16(2) May 1998, "minor corrections … 29 August 2000" per the fetched PDF header;
  cite the 2000-corrected version.
- W3 — All Keshav timings/labels and all Roscoe/Mitzenmacher/Smith content remain `[UNVERIFIED from fetched source]`.

## Summary
- Cluster A: 4 VERIFIED (Lamport backbone), 2 properly-flagged NEEDS-SOURCE, 0 blockers.
- Cluster B: 9 VERIFIED (incl. 4 fresh Lamport primaries + cross-refs), 2 properly-flagged NEEDS-SOURCE groups, 0 blockers.
- Total: 0 blockers. 12 has honest, primary-anchored coverage sufficient to reconcile into `_research.md` — with every
  unfetched method/storage source preserved as `[UNVERIFIED]`.

---

## UPGRADE 2026-06-10 (network heal — storage trilogy + Dynamo + Spanner + Tail-at-Scale FETCHED)

`research.google` mirrors + `usenix.org/legacy` + `allthingsdistributed.com` reachable. Fetched +
extracted to `meta/fetched_primaries/` (full receipts in `_VERIFIED_2026-06-10_canon.md`):
- **MapReduce** OSDI 2004, **Bigtable** OSDI 2006, **GFS** SOSP 2003, **Dynamo** SOSP 2007,
  **Spanner** OSDI 2012, **Tail at Scale** CACM 2013 — all PDF + text saved; key terms/claims
  verified verbatim (see canon receipt). → Clears the carried-forward 12 canon-walkthrough
  `[UNVERIFIED]` for the Google storage trilogy + Dynamo + Spanner + Tail-at-Scale.

**Still `[UNVERIFIED]`:** Keshav "How to Read a Paper" CCR 2007; Dapper; Chubby/ZooKeeper;
Saltzer/Reed/Clark End-to-End; Lampson "Hints"; ACM-record pagination re-pins.
