# 31 — Evaluation, Tracing & Guardrails · _structure.md

**Identity:** the **trust layer** of an agentic system — how you KNOW it works (evaluation), how you
SEE what it did (tracing), and how you keep it ON-RAILS (guardrails). 19 + 18 sense and steer a
*service*; 31 senses and steers a *stochastic loop*. The one genuinely new twist over 19/18 is
**nondeterminism**: the thing under test answers differently to the same input, so every measurement
becomes a statistical estimate (CIs, pass@k/pass^k, judge ensembles).

**Bespoke shape — "a trust-loop walkthrough: DEFINE correct → MEASURE it → GRADE the un-gradeable →
WATCH it live → CONSTRAIN it inline → CLOSE the loop."** NOT four clusters, NOT a copy of 19. The
load-bearing definition owed from 28/30 is settled VERIFIED by SWE-bench: **correctness = task
resolution under EXECUTION, not surface similarity** — a 95%-overlap patch can FAIL; a 40%-overlap
patch can PASS; correctness is binary under execution, never BLEU. Tracing reuses local Dapper (19);
judging reuses 27's Condorcet voting; guardrails reuse 18 validation. Primary FETCHED+VERIFIED
(SWE-bench, arXiv 2310.06770) — which also upgrades 28's carried SWE-bench `[UNVERIFIED]` → VERIFIED.
Math recomputed (19/19). The `/build` deliverable: wrap the 28 harness in a trust layer — the ninth
harness upgrade.

## Dependency position
- **Depends on:** 19 (Dapper — a trace is the 22 loop made observable; SLO/alerting precision) + 18
  (guardrails = validation every step) + 27 (LLM-as-judge = the critic; Condorcet majority-vote) + 13
  (back-of-envelope for sample size) + 20 (tail/keep-100%-of-error-traces) + 22 (the loop under test;
  eval costs S·O(T²)) + 23 (tool-arg-schema validation; execution oracle) + 24/25 (what eval measures)
  + 28 (the harness wrapped) + 30 (grounding/faithfulness eval).
- **Feeds into:** 32 (eval is an O(T²)·S budget line — gate/sample it; traces carry token counts) + 33
  (guardrails are the inline screens of defence-in-depth; caught attacks become golden tests; the
  critic is the LLM-supervisor; self-improvement is gated by the eval oracle) + 34 ("always before
  deploy: 31 eval with a budgeted CI + tracing" is a fixed branch of the design tree).
- **Appendix links DOWN:** M-agentic-papers (SWE-bench, Reflexion, LLM-as-judge anchors) · F-postgres
  (the trace/eval store) · N-math (CI arithmetic, pass@k/pass^k, RSE). 31 owns the trust loop;
  service-level observability stays in 19, admission control in 18, voting math in 27.

## Section specs (3–5 lines each)
1. **The one idea: a stochastic agent is untrustworthy until you DEFINE / MEASURE / WATCH / CONSTRAIN
   it** — and the definition is settled VERIFIED by SWE-bench: "we apply the generated patch ... then
   execute the unit and system tests ... If the patch applies successfully and all of these tests pass
   we consider the proposed solution to have successfully resolved the issue"; the metric is "the
   percentage of task instances that are resolved." Correctness = resolution under EXECUTION, binary,
   never lexical overlap.
2. **Define correct (SWE-bench)** — the golden artifact is a **test suite** (fail-to-pass +
   pass-to-pass = fix-without-regression), not a reference string. Three eval families: programmatic/
   execution-based (preferred — the 23 deterministic oracle), LLM-as-judge (when no oracle exists),
   human (calibration). Hard evals discriminate: Claude-2 resolved "a mere 1.96%." A 95%-overlap patch
   FAILS; a 40%-overlap patch PASSES.
3. **Measure offline (13/19)** — a pass rate is an *estimate*. 95% CI = ±1.96√(p(1-p)/N): N=10→±31%,
   N=1000→±3% (~1067 tasks for ±3%). For nondeterminism report **pass@k** (lenient best-of-k) AND
   **pass^k** (strict all-k) — one run is noise (RECOMPUTED: pass@3=0.936 vs pass^3=0.216, same agent).
   Eval costs S·(22 O(T²)) → gate/sample (→32).
4. **Grade the un-gradeable (27)** — LLM-as-judge is a noisy instrument; a **majority-of-3 ensemble**
   (the 27 Condorcet identity over GRADERS) cuts judge error (a=0.8: 0.20→0.104, 1.9×) — but BACKFIRES
   below the coin line (a=0.4→0.352). The 27 critic IS an LLM-as-judge; calibrate before you ensemble.
5. **Watch live (19 Dapper)** — a trace is the **22 loop made observable**: run = root span, turn =
   child span, tool/LLM call = leaf span; 1+T+T·m spans/run (49 at T=12, m=3). Sample at rate s;
   rare/low-volume failures need higher s (RSE √((1-s)/(s·n))); keep 100% of error traces. Multi-agent
   trace-id propagation = a distributed trace (11/27).
6. **Constrain inline (18/33)** — guardrails = 18 validation every step (input / tool-arg-schema 23 /
   output / safety 33). **Defence-in-depth**: 3×80% layers → 0.8% escape; but an **over-refusal tax**:
   3×2%-FP layers → 5.9% of good outputs rejected. Tune the depth; measure the FP rate as its own
   first-class metric.
7. **Close the loop** — failed golden tasks → drop into their trace to debug; bad production traces →
   become new golden tasks. The regression set GROWS from real failures. This is the agentic mirror of
   SRE's blameless-postmortem-into-test-suite loop.

## The economics (RECOMPUTED — `_recompute.py` 19/19)
Sample size ±3% ≈ 1067 tasks · pass@3=0.936 vs pass^3=0.216 (same agent) · majority-of-3 judges
1.9–3.6× fewer errors, backfires <0.5 · 49 spans/run, sampling RSE collapses with volume ·
defence-in-depth 0.8% escape vs 5.9% over-refusal tax · 95%-overlap patch FAILS / 40% PASSES ·
2,294-task suite ≈ 837M tokens (eval is an O(T²)·S budget line → 32).

## Paired build lab (/build → own-coding-agent-harness, ninth upgrade)
Wrap the 28 harness in a trust layer: `run_evals()` over 5–10 execution-oracle golden tasks reporting
**% resolved + 95% CI**; repeat-k → pass@k AND pass^k; a 3-judge majority-vote (27) for the one
open-ended task (and SHOW it backfire below the coin line); a span per turn/tool call (Dapper, 19)
with token/cost annotations (→32); input/output/tool-arg guardrails (18/23) that catch a planted
injection-in-a-retrieved-passage (30→33) and whose over-refusal FP rate you measure; then turn a real
failed run's trace into a new golden task.

## Diagrams needed
- The trust loop: define → measure → grade → watch → constrain → close (the bespoke spine).
- SWE-bench execution oracle: patch → apply → run fail-to-pass + pass-to-pass → binary verdict.
- CI shrinking with N (±31% at N=10 → ±3% at N=1000) — why one run is noise.
- pass@k vs pass^k for the same agent (lenient vs strict over k runs).
- Condorcet judge ensemble: error vs single judge above the line, backfire below 0.5.
- A run as a Dapper span tree (run→turn→tool/LLM leaf; 1+T+T·m spans).
- Defence-in-depth: escape rate vs over-refusal tax as layers stack.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **PRIMARY (FETCHED+VERIFIED):** SWE-bench (Jimenez/Yang et al., ICLR 2024, arXiv 2310.06770) —
  `meta/fetched_primaries/swe-bench-2310.06770.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_swe-bench.md`.
  **Reconcile-note:** this fetch upgraded 28's carried SWE-bench `[UNVERIFIED]` → VERIFIED (receipt
  logged); the original 28 flag is preserved, not erased.
- **PRIMARY (REUSED, local):** Dapper (2010, verified in 19) for tracing; Reflexion (2303.11366,
  verified in 25) for self-eval-as-learning-signal (→33); SRE SLO/alerting (19) for precision.
- **RECOMPUTED:** `_recompute.py` (19/19).
- **REUSED:** 13, 18, 19, 20, 22, 23, 24, 25, 27, 28, 30 (+ 32/33 forward).
- **`[UNVERIFIED]` carry-forward (none load-bearing):** LLM-as-judge primary (MT-Bench / Zheng
  2306.05685) + judge-bias taxonomy; SWE-bench-Verified / SWE-agent (2405.15793) / HumanEval (2021);
  RAGAS faithfulness eval (30 owed); OpenTelemetry GenAI + W3C trace-context (carried from 19);
  tail-based sampling; guardrail frameworks (NeMo/Guardrails-AI); eval harnesses (OpenAI Evals /
  lm-eval-harness); self-consistency (2203.11171).
- **Boundary discipline:** service observability stays in 19, admission control in 18, voting math in
  27, cost of eval in 32, threat mitigations in 33. 31 owns the trust loop + the execution-oracle
  definition + the nondeterminism statistics.
