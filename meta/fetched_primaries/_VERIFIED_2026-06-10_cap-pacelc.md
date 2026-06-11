# VERIFIED 2026-06-10 — CAP formal + PACELC primaries (network heal, Wave 10)

Two long-blocked carry-forward primaries finally returned HTTP 200 this session and were
fetched + text-extracted (throwaway uv venv + pypdf, removed after) + verified verbatim.

## Sources fetched
| source | file | http | size |
|--------|------|------|------|
| Gilbert & Lynch, "Perspectives on the CAP Theorem" (IEEE Computer / Proc. IEEE, 2012; restates & situates the 2002 SIGACT News formalization, ref [16]) | `gilbert-lynch-2002.{pdf,txt}` | 200 (groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf) | 136 KB, 10 pp |
| Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design" (IEEE Computer, 2012) — the PACELC paper | `abadi-pacelc-2012.{pdf,txt}` | 200 (cs.umd.edu/~abadi/papers/abadi-pacelc.pdf) | 805 KB, 6 pp |

## Gilbert–Lynch — verbatim load-bearing claims (`gilbert-lynch-2002.txt`)
- L8/L14: "consistency, availability, and partition tolerance. This trade-off … has become known
  as the CAP Theorem."
- L19/L28: the CAP Theorem is "one example of the fundamental fact that you cannot achieve both
  safety and liveness in an unreliable distributed system."
- L65–L70: they formalize the service as an **atomic** (linearizable) read/write shared register;
  "A web service is atomic if, for every operation, there is a single instant in between the
  request and the response" at which it appears to take effect.
- L83/L97: the impossibility argument — when servers "may be partitioned into multiple groups that
  cannot communicate," a process p2 "cannot distinguish" a lost message from a slow one, "and hence
  it cannot determine whether to return" → cannot be both consistent and available.
- L122: "[impossible for a] read/write register to guarantee both safety and liveness in a system
  prone to partitions."
- L140: "the CAP Theorem also implies that you cannot achieve consensus in a system subject to
  partitions." (ties CAP to FLP — reuse 11.)
- Note: this is the 2012 retrospective that *cites and restates* the 2002 SIGACT News proof [16];
  the formal proof statement (atomic register impossibility in the asynchronous + partitionable
  model) is reproduced here. The original 2002 *SIGACT News* PDF specifically remains separately
  unfetched, but the load-bearing formalization is now primary-anchored.

## Abadi PACELC — verbatim load-bearing claims (`abadi-pacelc-2012.txt`)
- L17–L21: "one particular tradeoff—between consistency and latency—arguably has been more
  influential on DDBS design than the CAP tradeoffs … unifying CAP and the consistency/latency
  trade-off into a single formulation—PACELC."
- L25–L30: restates CAP (choose two of C/A/P; CA, CP, AP system classes).
- L476–L482: **the PACELC definition, verbatim** — "rewriting CAP as PACELC (pronounced
  'pass-elk'): if there is a **partition (P)**, how does the system trade off **availability and
  consistency (A and C)**; else **(E)**, when the system is running normally in the absence of
  partitions, how does the system [trade off **latency (L) and consistency (C)**]."
- L495–L510: worked classifications — Dynamo/Cassandra/Riak are **PA/EL** (give up consistency
  under partition, give up consistency for latency normally); fully-ACID stores (VoltDB/H-Store,
  BigTable/HBase) are **PC/EC**; PNUTS is **PC/EL**.

## Upgrades to apply (carry-forward `[UNVERIFIED]` -> VERIFIED; nothing erased)
- **11** `_factcheck_cluster4.md`: Gilbert–Lynch formal CAP (atomic-register impossibility, safety-
  vs-liveness framing, CAP⇒no-consensus-under-partition) — upgrade.
- **15** `_factcheck_phase1.md`: PACELC PA/EL vs PC/EC and the else-latency limb — upgrade (was
  carried alongside CAP).
- **20** `_factcheck_phase1.md` / `_research.md` gap ledger: Gilbert–Lynch 2002 formal proof is no
  longer "still blocked" — primary-anchored (note the 2012 retrospective caveat above).

Still blocked this session: CoDel `queue.acm.org` HTTP 403; `raft.github.io` HTTP 000;
`dl.acm.org` HTTP 403 (canonical DOI landing). arxiv.org + kafka.apache.org + postgresql.org are
now 200 (used opportunistically below if time permits).
