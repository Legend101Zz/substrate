# Factcheck — Sub-course 11 Phase 1 starter cluster
## Scope: `_research_time-clocks-ordering-failure.md`
## Date: 2026-06-10

Method: manual BRAIN spot-check against fetched primary sources in `/tmp/substrate-11-sources`. PDFs were downloaded
from source URLs and text-extracted with a throwaway `uv run --with pypdf` environment. Chandra-Toueg was fetched as
PostScript and inspected with `strings`, so exact CT96 definitions remain flagged for cleaner-text verification.

---

## Summary verdict

- Checked: **22 load-bearing claims** across Lamport clocks, Chandy-Lamport snapshots, FLP, Spanner TrueTime, and
  Chandra-Toueg failure detectors.
- Blockers: **0** after drafting.
- Warnings: **1** — Chandra-Toueg exact definitions are supported only by noisy PostScript text extraction; the brief
  keeps exact theorem/definition wording out of prose and marks it for cleaner-source verification.
- Acceptance: starter cluster is safe as a Phase 1 brief. It is **not** a reconciled full 11 corpus.

---

## Claim checks

| # | Claim | Source receipt | Verdict |
|---|-------|----------------|---------|
| 1 | Happened-before is defined from same-process order, send→receive, and transitivity. | Lamport 1978 extracted lines around 90–170; grep hits lines 144–150. | PASS |
| 2 | Concurrent events are events where neither happened-before relation holds. | Lamport 1978 extracted lines around 147–154 and 186–188. | PASS |
| 3 | Happened-before is a partial order over system events. | Lamport 1978 grep hit around line 154: “irreflexive partial ordering.” | PASS |
| 4 | Clock Condition: if `a -> b`, then `C(a) < C(b)`. | Lamport 1978 extracted lines around 230–245. | PASS |
| 5 | Lamport clocks do not satisfy the converse: `C(a) < C(b)` does not prove `a -> b`. | Lamport 1978 lines around 238–245 explicitly reject the converse because concurrent events would be forced to same time. | PASS |
| 6 | IR1 increments between successive events. | Lamport 1978 grep hit around line 297. | PASS |
| 7 | IR2 sends timestamp and receiver advances clock beyond current value and message timestamp. | Lamport 1978 grep hits around lines 300–314. | PASS |
| 8 | Logical-clock total order sorts by timestamp and breaks ties by arbitrary process order. | Lamport 1978 extracted lines around 318–332. | PASS |
| 9 | Lamport total order is not unique; only the partial order is determined by events. | Lamport 1978 grep hits around lines 338–342. | PASS |
| 10 | Lamport physical clocks require rate and synchronization bounds. | Lamport 1978 extracted lines around 543–610. | PASS |
| 11 | Spanner TrueTime returns an interval `[earliest, latest]`, not a point timestamp. | Spanner 2012 grep hits around lines 392–408. | PASS |
| 12 | TrueTime guarantees absolute invocation time lies inside the returned interval. | Spanner 2012 grep hits around lines 406–418. | PASS |
| 13 | Spanner slows down when uncertainty is large / waits out uncertainty. | Spanner 2012 grep hit around line 107; additional timestamp wait references around lines 733/767. | PASS |
| 14 | Chandy-Lamport assumes no shared clocks or memory. | Chandy-Lamport 1985 grep hit around line 51. | PASS |
| 15 | Global state comprises process and channel states. | Chandy-Lamport 1985 extracted lines around 159–168. | PASS |
| 16 | Naive cuts can duplicate or lose the token / be inconsistent. | Chandy-Lamport 1985 extracted lines around 263–292. | PASS |
| 17 | Recorded snapshot may differ from all physical states during the run but is meaningful through reachability. | Chandy-Lamport 1985 extracted lines around 383–410. | PASS |
| 18 | Failure is meaningful only in physical-time context; without time, failed vs paused is indistinguishable. | Lamport 1978 grep hits around lines 497–502. | PASS |
| 19 | FLP model is completely asynchronous with no process-speed or message-delay assumptions. | FLP grep hits around lines 72 and 81. | PASS |
| 20 | FLP excludes synchronized clocks/timeouts and death detectors. | FLP grep hits around lines 83–87. | PASS |
| 21 | FLP shows one unannounced process death can prevent consensus termination in the fully asynchronous model. | FLP extracted lines around 64–89 and 112–120; conclusion around 326–328. | PASS |
| 22 | Chandra-Toueg frames failure detectors using completeness and accuracy, with timeout/false-suspicion tradeoffs. | CT96 PostScript `strings` hits around lines 6608–7041 and 7317–7454. | PASS WITH WARNING |

---

## Patches required

None.

---

## Residual warnings/gaps

- Fetch a cleaner Chandra-Toueg PDF/text before Phase 2 prose. The current PostScript source is primary and accessible,
  but text extraction is noisy; exact formal definitions should not be quoted from this extraction.
- Add vector clocks/version vectors separately; scalar Lamport clocks intentionally cannot determine all causality.
- Add consistency/linearizability/replication/quorum clusters before reconciling `11-distributed-systems-foundations/_research.md`.
