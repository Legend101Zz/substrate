# 31 · evaluation-tracing-and-guardrails — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 31 is the **trust layer** of an agentic
> system: how you KNOW it works (evaluation), how you SEE what it did (tracing), and how you keep
> it ON-RAILS (guardrails). Bespoke structure: a **trust-loop walkthrough** (NOT four clusters,
> NOT a copy of 19). Primary fetched+verified: **SWE-bench (arXiv 2310.06770)** for the "is it
> useful" definition owed from 28/30; tracing reuses local **Dapper (19)**; judging reuses **27**;
> guardrails reuse **18**. Full depth: `_research_evaluation-tracing-and-guardrails.md`. Math:
> `_recompute.py` (19/19). Factcheck: `_factcheck_phase1.md` (0 blockers).

## 1. The one idea (VERIFIED)
**A stochastic agent is untrustworthy until you DEFINE correct, MEASURE it, WATCH it, and CONSTRAIN
it.** The load-bearing definition (owed from 28/30) is settled by SWE-bench: **correctness = task
resolution under EXECUTION, not surface similarity.** VERIFIED: "we apply the generated patch ...
then execute the unit and system tests ... If the patch applies successfully and all of these tests
pass we consider the proposed solution to have successfully resolved the issue"; "The metric ... is
the percentage of task instances that are resolved." A 95%-token-overlap patch can FAIL; a
40%-overlap patch can PASS — correctness is **binary under execution**, never BLEU.

## 2. The trust loop, walked (the bespoke spine)
- **Define correct (§1, SWE-bench):** the golden artifact is a **test suite** (fail-to-pass +
  pass-to-pass = fix-without-regression), not a reference string. Three eval families: programmatic/
  execution-based (preferred — the 23 deterministic oracle), LLM-as-judge (when no oracle exists),
  human (calibration). Hard evals discriminate: Claude-2 resolved "a mere 1.96%".
- **Measure offline (13/19):** a pass rate is an *estimate*. 95% CI = ±1.96√(p(1-p)/N): N=10→±31%,
  N=1000→±3% (~1067 tasks for ±3%). Nondeterminism: report **pass@k** (lenient best-of-k) AND
  **pass^k** (strict all-k); one run is noise. Eval costs S·(22 O(T²)) → gate/sample (→32).
- **Grade the un-gradeable (27):** LLM-as-judge is a noisy instrument; a **majority-of-3 ensemble**
  (the 27 Condorcet identity over GRADERS) cuts judge error (a=0.8: 0.20→0.104, 1.9×) — but
  BACKFIRES below the coin line (a=0.4→0.352). The 27 critic IS an LLM-as-judge.
- **Watch live (19 Dapper):** a trace is the **22 loop made observable** — run=root span, turn=child
  span, tool/LLM call=leaf span; 1+T+T·m spans/run (49 at T=12,m=3). Sample at rate s; rare/low-
  volume failures need higher s (RSE √((1-s)/(s·n))); keep 100% of error traces. Multi-agent
  trace-id propagation = a distributed trace (11/27).
- **Constrain inline (18/33):** guardrails = 18 validation every step (input / tool-arg-schema 23 /
  output / safety 33). **Defence-in-depth**: 3×80% layers → 0.8% escape; but an **over-refusal
  tax**: 3×2%-FP layers → 5.9% of good outputs rejected. Tune; measure FP as its own metric.
- **Close the loop:** failed golden tasks → drop into their trace; bad production traces → become
  new golden tasks (the regression set grows from real failures).

## 3. The economics (RECOMPUTED — headlines, `_recompute.py` 19/19)
Sample size ±3% ≈ 1067 tasks · pass@3=0.936 vs pass^3=0.216 (same agent) · majority-of-3 judges
1.9–3.6× fewer errors, backfires <0.5 · 49 spans/run, sampling RSE collapses with volume ·
defence-in-depth 0.8% escape vs 5.9% over-refusal tax · 95%-overlap patch FAILS / 40% PASSES ·
2,294-task suite ≈ 837M tokens (eval is an O(T²)·S budget line → 32).

## 4. Where 31 sits
31 is the agentic counterpart of **19 observability + 18 control**: 19/18 sense+steer a *service*;
31 senses+steers a *stochastic loop*. Eval (offline, before deploy) ↔ 28 harness + 30 grounding
faithfulness; tracing (online) = 19 Dapper over the 22 loop; guardrails (inline) = 18 validation +
33 safety. Reuses the entire toolkit; the one twist is **nondeterminism** (the thing under test
answers differently to the same input → CIs, pass@k/pass^k, judge ensembles).

## 5. Failure modes
Eval overfit (tune to test set) · lexical-oracle trap (BLEU rewards plausible-but-wrong) ·
single-run verdict (noise as signal) · uncalibrated judge (<0.5, ensembling amplifies the bias) ·
trace blind spots (sample too low for rare bugs; missing cross-agent causal propagation) ·
guardrail extremes (too few → escape; too many → over-refusal) · eval cost blowout (full O(T²)
suites per commit → 32). All but the judge/nondeterminism ones are 13/18/19 problems.

## 6. Build-your-own
Ninth harness upgrade (after 30 grounding): wrap the 28 harness in a trust layer — `run_evals()`
over 5-10 execution-oracle golden tasks reporting **% resolved + 95% CI**; repeat-k → pass@k AND
pass^k; a 3-judge majority-vote (27) for the one open-ended task (+ show it backfire); a span per
turn/tool call (Dapper, 19) with token/cost annotations (→32); input/output/tool-arg guardrails
(18/23) that catch a planted injection-in-a-retrieved-passage (30→33) and whose over-refusal FP
rate you measure; then turn a real failed run's trace into a new golden task.

## 7. Provenance summary
- **PRIMARY (FETCHED+VERIFIED):** SWE-bench (Jimenez/Yang et al., ICLR 2024, arXiv 2310.06770) —
  `meta/fetched_primaries/swe-bench-2310.06770.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_swe-bench.md`.
- **PRIMARY (REUSED, local):** Dapper (2010, verified in 19) for tracing; Reflexion (2303.11366,
  verified in 25) for self-eval-as-learning-signal (→33); SRE SLO/alerting (19) for precision.
- **RECOMPUTED:** `_recompute.py` (19/19).
- **REUSED:** 13, 18, 19, 20, 22, 23, 24, 25, 27, 28, 30 (+32/33 forward).
- **`[UNVERIFIED]` carry-forward (none load-bearing):** LLM-as-judge primary (MT-Bench / Zheng
  2306.05685) + judge-bias taxonomy; SWE-bench-Verified / SWE-agent (2405.15793) / HumanEval
  (2021); RAGAS faithfulness eval (30 owed); OpenTelemetry GenAI + W3C trace-context (carried from
  19); tail-based sampling; guardrail frameworks (NeMo/Guardrails-AI); eval harnesses (OpenAI
  Evals / lm-eval-harness); self-consistency (2203.11171).

---
**31 reconciled.** Part III "Phase 1 batch 3" now stands at **22-31 reconciled** (10 of 13 agentic
sub-courses). **BONUS:** SWE-bench fetch also upgrades 28's carried `[UNVERIFIED]` SWE-bench note →
VERIFIED (see receipt). Next in dependency order: **32-cost-observability-and-ops** (the 22 O(T²)
economics made operational), then 33 safety, 34 design-your-own.
