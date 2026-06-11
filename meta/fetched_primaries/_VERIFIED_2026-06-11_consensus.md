# VERIFIED 2026-06-11 — Lamport consensus primaries (Appendix L)

Opportunistic fetch this session (Wave 16). Lamport's host (`lamport.azurewebsites.net`) was HTTP
200 (reachable); raft.github.io still 000, queue.acm.org still 403 (CoDel). Saved to
`meta/fetched_primaries/`. PDF text extracted via throwaway `/tmp/pdfx-venv-l` (pypdf) —
`.code-puppy-venv` UNTOUCHED.

## Files
- `lamport-paxos.pdf` / `.txt` — Leslie Lamport, "The Part-Time Parliament" (original Paxos),
  ACM TOCS 16(2), 1998 (2000-corrected). 33 pages, 93,341 chars.
- `lamport-byz.pdf` / `.txt` — Lamport, Shostak, Pease, "The Byzantine Generals Problem,"
  ACM TOPLAS 4(3), 1982. 20 pages, 56,465 chars.

## Verified verbatim (load-bearing)
- **Byzantine bound `3m+1`** — `lamport-byz.txt`:
  - line 10: "solvable if and only if more than two-thirds of the generals are loyal; so a single
    traitor can confound …"
  - line 156: "no solution with fewer than 3m + 1 generals" (to tolerate m traitors with oral msgs).
  - line 234–235: "to cope with m traitors, there must be at least 3m + 1 generals … a solution that
    works for 3m + 1 or more generals."
  - ⇒ Byzantine fault tolerance needs **n ≥ 3f+1** (tolerate f Byzantine faults). (Anchors L's BFT
    tier; contrasts with crash-fault `n ≥ 2f+1` majority.)
- **Paxos majority/quorum** — `lamport-paxos.txt`:
  - line 108: "If a majority of the legislators …"
  - line 131: footnote rendering the Paxon word as **majority**.
  - line 189–193: "A ballot succeeded iff every priest in the quorum voted for the decree … Bqrm A
    nonempty set of priests (the ballot's quorum)."
  - line 18: "State machines, three-phase commit, voting" (key phrases).
  - ⇒ Paxos = **majority-quorum voting** implementing the **state-machine approach** (crash-fault,
    `n ≥ 2f+1`). (Anchors L's consensus core; cross-links 11/12.)

## Applies to
- Appendix **L-consensus-replication-and-transactions** (BFT bound, Paxos majority/state machine).
- Upgrades 12's carry-forward Byzantine/Paxos `[UNVERIFIED]` → text now LOCAL+VERIFIED (the `.txt`
  files 12 referenced were not committed; they are now present under fetched_primaries).
