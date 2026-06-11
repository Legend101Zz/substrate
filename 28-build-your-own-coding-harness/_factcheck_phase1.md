# 28 · Phase-1 factcheck — build-your-own-coding-harness

> Method (same discipline as 13-27): every load-bearing claim is (a) RECOMPUTED in `_recompute.py`
> (31/31 pass), (b) REUSED from a line-verified Part I/II + 22-27 anchor, or (c) flagged
> `[UNVERIFIED]` carry-forward. 0 blockers. **No new primary fetched — 28 is a CAPSTONE
> APPLICATION** (like 21 for Part II): it introduces no new load-bearing claim, so it needs no new
> source; it assembles already-VERIFIED anchors.

## Bespoke structure note
28 is a **BUILD PROGRESSION**, not abstract source clusters and not the 13-20 four-cluster shape.
The brief grows one program through 7 stages (loop→tools→budget→compaction→memory→persistence→
orchestration), **breaking it on purpose at each stage** so the next primitive is motivated by an
observed failure. Plan-sanctioned (the plan names this the "build-lab bespoke structure = a build
progression").

## No primary fetched this session (by design)
28 cites no new paper because every mechanism is a CROSS-LINK to an already-verified anchor:

| Stage | Mechanism | Verified anchor (where it was proven) |
|------|-----------|----------------------------------------|
| 0 | control loop; O(T²) tokens; window overflow T* | ReAct 22 (`react-2210.03629`) + 22 `_recompute.py` 18/18 |
| 1 | tool = contract; ReAct observation = test result; four decisions | Toolformer 23 (`toolformer-2302.04761`) + 23 `_recompute.py` 15/15 |
| 2 | step/$/time budget; retry/breaker | 22 §6 budget + 18 (RFC 6585 / SRE overload, verified) |
| 3 | compaction O(T²)→O(T); placement | CoT 24 (`cot-2201.11903`) + 24 `_recompute.py` 18/18 |
| 4 | memory = paging; AMAT; poisoning | MemGPT/Reflexion 25 (`memgpt-2310.08560`,`reflexion-2303.11366`) + 25 `_recompute.py` 13/13 |
| 5 | transcript = WAL; resume = crash recovery; idempotent replay | Postgres-WAL 26 (`postgres-wal-intro.txt`) + 26 `_recompute.py` 12/12 |
| 6 | multi-agent = distributed system; Amdahl/join-tail/YAGNI | 27 `_recompute.py` 16/16 (applies 11/13/17/20 toolkit) |

## Recomputed claims (`_recompute.py`, 31/31)
Re-derived in the **coding-agent regime** (bigger p=4000, g=1500: code is verbose), not re-cited:
- **S0:** cumulative input tokens = `T*p + g*T*(T-1)/2` (closed form == brute sum, T=1/5/10/20);
  quadratic (g-term ~4.22× when T doubles); window overflow at `T*=83` for coding vs `253` for
  chat — **the quadratic bites SOONER for coding** (verbose files/logs). PASS.
- **S1:** selection compounding `1-(1-q)^N` (9.6%/18.3%/63.6% at N=5/10/50) — the 13/20/21/23
  identity over loop steps; result budget `W-(p+(t-1)g)` shrinks 124000→95500 over 20 turns; a
  ~250k-token 1 MB file overflows even an empty window; toolbox tax `K·S=2400` tok/turn. PASS.
- **S2:** cumulative input T=20 = 365000; step-budget bounds worst-case cost ($1.275); wall-clock
  bound 600s; **budget caps but does not cure** (prompt at cap 32500 ≫ 4000). PASS.
- **S3:** compacted cumulative is O(T) (≤ T·(p+C)); compaction win **grows without bound** (ratio
  T=200 → T=1000); prefix-cache helps the prefix only, still O(T²) on the tail (**caching ≠
  compaction**). PASS.
- **S4:** AMAT over tokens — hit 0.80→0.95 cuts effective cost **4×** (matches 25's verified model);
  poisoning blast radius 1 write → 15 reads. PASS.
- **S5:** write-ahead loss ≤1 step vs whole run; checkpoint knee `I*=√(2·N·c_ckpt)=20`; idempotency
  prevents double-applied edits (no-keys 3 → keys 0). PASS.
- **S6:** Amdahl speedup 3.57× / ceiling 5×; join tail `1-(1-p)^N=63.4%@N=100`; aggregation tax
  compaction 6.67×; **YAGNI payoff** — multi-agent WINS on big decomposable task, **LOSES on small
  task**. PASS.

## Reused (line-verified Part I/II + 22-27)
22 (loop, quadratic, step budget, window exhaustion); 23 (tool contracts, selection compounding,
result budget, security/ACE); 24 (compaction O(T²)→O(T), placement, prefix-cache); 25 (memory
paging, AMAT, poisoning); 26 (WAL, checkpoint knee, idempotent replay); 27 (Amdahl, join tail,
aggregation tax, YAGNI); 17/21 (idempotency/exactly-once-effect); 18 (timeout/retry/breaker/
bulkhead); 20 (tail, partial results, correlated failure); 09 (the log/offset); Appendix I
(sandbox/containers, deferred).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Real coding-agent implementations as design references (Claude Code, Aider, OpenAI Codex CLI,
  SWE-agent, Cursor, Code Puppy) — design folklore, not fetched primaries.
- ~~**SWE-bench** (Jimenez et al., arXiv 2310.06770) ... NOT fetched this session.~~ **UPGRADED
  2026-06-10 (Wave 14): SWE-bench FETCHED+VERIFIED** while building 31 — `meta/fetched_primaries/
  swe-bench-2310.06770.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_swe-bench.md`. The canonical
  coding-agent benchmark + the execution-based definition of "useful" for Stage 1 + 31 is now
  VERIFIED (execution-based: apply patch → run unit+system tests → all pass = resolved; metric =
  % resolved; Claude-2 baseline 1.96%). Nothing erased.
- Sandboxing/ACE-mitigation specifics (containers/cgroups/seccomp → Appendix I) — reuse, deferred.
- prompt-injection-via-tool-result (→33), memory-poisoning mitigations (→25/33) — carry-forward.
- All prior 22-27 + 01-21 carried `[UNVERIFIED]` remain logged and untouched.

## Verdict
28 is honest and lab-appropriate: it is the **assembly** of seven already-verified primitives into a
single coding harness via a build progression whose every "wall" is RECOMPUTED in the coding regime
and whose every mechanism CROSS-LINKS to a line-verified anchor. No new load-bearing claim → no new
primary required (capstone, like 21). Residual `[UNVERIFIED]` are implementation references +
SWE-bench + sandbox specifics, none load-bearing for the progression. Reconcile into `_research.md`.
