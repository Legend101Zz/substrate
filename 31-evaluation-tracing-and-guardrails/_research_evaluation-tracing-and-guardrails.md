# 31 · evaluation-tracing-and-guardrails — cluster research (full depth)

> Phase-1 brief (NO course prose). 31 is the **trust layer** of an agentic system: how you KNOW
> the agent works (evaluation), how you SEE what it did (tracing), and how you keep it ON-RAILS
> (guardrails). Bespoke structure: a **trust-loop walkthrough** — Define correct → Measure it
> offline → Watch it live → Constrain it inline — NOT the 13-20 four-cluster shape, NOT a copy of
> 19's signal taxonomy.
>
> Primary fetched+verified THIS session: **SWE-bench (Jimenez/Yang et al., ICLR 2024, arXiv
> 2310.06770)** for the execution-based "is it useful" definition owed from 28/30. Tracing reuses
> the already-local **Dapper (2010)** primary from 19. LLM-as-judge voting reuses 27; guardrails
> reuse 18. Math: `_recompute.py` (19/19). Factcheck: `_factcheck_phase1.md` (0 blockers).

---

## 0. Where 31 sits (the gap it fills)

- 22-30 built an agent that *runs*. 31 answers the three questions you can't ship without:
  1. **Does it work?** (evaluation — offline, before deploy)
  2. **What did it just do?** (tracing — online, after/while it runs)
  3. **Can it go off the rails?** (guardrails — inline, every step)
- 31 is the agentic counterpart of Part II's **19 observability** + **18 control**: 19/18 sense
  and steer a *service*; 31 senses and steers a *stochastic loop*. The mechanisms are REUSED, the
  twist is **nondeterminism** — the thing under test gives different answers to the same input.

---

## 1. DEFINE "CORRECT" — the owed "is it useful" definition (VERIFIED: SWE-bench)

The hardest part of agent eval is that "correct" is not obvious. SWE-bench settles it for the
coding regime and the lesson generalizes:

- **Correctness = task resolution under EXECUTION, not surface similarity.** VERIFIED (SWE-bench
  §2.2): "we apply the generated patch, using unix's patch program, to the codebase and then
  execute the unit and system tests... If the patch applies successfully and all of these tests
  pass we consider the proposed solution to have successfully resolved the issue." The metric is
  "the percentage of task instances that are resolved."
- **Lexical/BLEU/exact-match is the WRONG oracle.** RECOMPUTED (`_recompute.py` §6): a patch with
  95% token overlap with the golden patch can FAIL the tests (wrong line), while a 40%-overlap
  patch PASSES. Correctness is **binary under execution**, not a similarity score. This is exactly
  the "is it useful" definition owed from 28 (the harness) and 30 (grounding/faithfulness).
- **The golden artifact is a test suite, not a reference string.** VERIFIED (SWE-bench §2.1):
  "the user likely contributed tests to check whether the issue has been resolved"; tasks have
  **fail-to-pass** and **pass-to-pass** tests (40% have ≥2 fail-to-pass). The agent must make the
  red tests green WITHOUT breaking the green ones (no-regression).
- **Frontier benchmarks exist because old ones saturate.** VERIFIED (SWE-bench §1): "existing
  benchmarks have become saturated... fail to capture the frontier." Lesson: build evals that
  *discriminate* — Claude-2 scored a "mere 1.96%", i.e. a hard eval reveals real capability gaps.
- **Three eval families (taxonomy, only the first is fully VERIFIED here):**
  1. **Programmatic / execution-based** (SWE-bench style): deterministic oracle (tests, exact
     match on a closed task, schema validity). Cheap to trust, hard to author. PREFERRED whenever
     a deterministic oracle exists — this is the 23 "deterministic code" half judging the 22
     "stochastic caller" half.
  2. **LLM-as-judge** (§3): a model grades open-ended output against a rubric. Use only when no
     programmatic oracle exists; treat the judge as a noisy instrument (calibrate, ensemble).
  3. **Human eval**: ground truth, expensive, doesn't scale → used to calibrate (1) and (2).
- **Golden tasks / regression set:** a curated, version-pinned set of (input, oracle) pairs that
  the agent must keep passing. This is the agentic **regression test suite**; a new prompt/model/
  tool that drops the pass rate is a regression (caught offline, before deploy).

---

## 2. MEASURE IT OFFLINE — sampling, precision, and nondeterminism (RECOMPUTED)

Once "correct" is defined, a pass rate is a *statistical estimate*, not a fact.

- **How many golden tasks to trust a number?** RECOMPUTED (§1): a pass rate p̂ over N tasks has
  SE = √(p(1-p)/N); 95% CI half-width ≈ 1.96·SE. N=10 → ±31% (useless); N=100 → ±10%; N=1000 →
  ±3%. To pin a rate to ±3% at p=0.5 you need **~1067 tasks**. (This is 19's measurement-precision
  lesson applied to eval — a 60%→62% "improvement" on 50 tasks is noise.)
- **Nondeterminism: pass@k vs pass^k.** RECOMPUTED (§2): a flaky agent that passes with p=0.6
  shows **pass@3 = 0.936** (best-of-3, lenient) but **pass^3 = 0.216** (all-3-succeed, strict
  reliability). A single run is an unreliable verdict; you MUST repeat and **report which metric**.
  pass@k flatters; pass^k is what a user who can't retry actually experiences.
- **Eval is expensive — each task is a full O(T²) loop (22).** RECOMPUTED (§7): a 2,294-task suite
  at T=20 turns ≈ 837M tokens; per-task cost is quadratic in turns. So eval is a real budget line
  item (→32): **gate it** (run the full suite nightly, a smoke subset per commit) and **cap eval
  turns**. This is the 13/20 "sampling under cost" discipline over a test suite.
- **Eval hygiene:** version-pin the set; hold out a private subset to detect train/eval leakage
  (SWE-bench's whole point is *real, post-cutoff* issues); separate the dev set you tune on from
  the test set you report on (don't overfit the prompt to the eval).

---

## 3. LLM-AS-JUDGE — the noisy grader, and the 27 ensemble that rescues it (RECOMPUTED, reuse 27)

When no deterministic oracle exists (summaries, plans, "is this answer grounded?"), grade with a
model — but treat it as an instrument with error.

- **A single judge has an error rate.** Model the judge as correct with prob a. Known judge
  pathologies (carried `[UNVERIFIED]`, flagged): position bias, verbosity bias, self-preference,
  leniency drift. Mitigations: a rubric, reference answers, randomized option order, calibration
  against human labels.
- **A voting ensemble beats a single judge — the 27 Condorcet identity, reused over GRADERS.**
  RECOMPUTED (§3): majority-of-3 independent judges is correct with a³+3a²(1-a). a=0.8 → 0.896
  (judge error 0.20 → 0.104, **1.9× fewer**); a=0.9 → 0.972 (**3.6× fewer**). This is *exactly*
  27's majority-of-3 voting (worker ensemble), now applied to judges.
- **But it backfires below the coin line.** RECOMPUTED (§3): a=0.4 → maj3 = 0.352 < 0.4. Condorcet
  only helps if each judge is **better than chance** — a biased judge, ensembled, gets *more*
  confidently wrong. So calibrate first, then ensemble.
- **The critic from 27 IS an LLM-as-judge.** The 27 "critic/voting" ensemble and 31's "LLM-as-
  judge" are the same mechanism viewed from two angles: 27 uses it to pick a *worker's* output at
  runtime; 31 uses it to *grade* outputs at eval time. Self-consistency (sample N, majority-vote
  the answer) is the same identity again.

---

## 4. WATCH IT LIVE — tracing the loop = Dapper spans over agent steps (VERIFIED via 19 Dapper)

Offline eval tells you the aggregate; tracing tells you *what this specific run did*.

- **A trace IS the agent loop made observable.** Reuse 19/Dapper: a **span** = one timed unit of
  work with a name, span-id, parent-id, and a 64-bit trace-id (VERIFIED in 19). For an agent: the
  run is the **root span**; each loop turn (22) is a **child span**; each tool call (23) and each
  LLM call is a **leaf span**. RECOMPUTED (§4): a T=12, m=3 run emits **1 + T + T·m = 49 spans** —
  the loop tree becomes a Dapper trace tree. Annotate spans with tokens-in/out, model, tool name,
  result size, retries (the 22/24/32 quantities).
- **Causal propagation:** Dapper's parent-id chain (VERIFIED in 19, thread-local + async context
  propagation) is how you reconstruct "the agent thought X → called tool Y → got Z → decided W."
  In a multi-agent system (27) the trace-id propagates across agents = a distributed trace (11).
- **Sampling, because traces aren't free.** Reuse 19/Dapper: sample at rate s; the relative
  standard error of a measured rate over n events ≈ √((1-s)/(s·n)). RECOMPUTED (§4): at s=0.1%,
  RSE is 0.032 at 1e6 events but 0.999 at 1e3 — **rare bugs / low-traffic agents need a higher
  sample rate** (Dapper's adaptive-sampling lesson). Keep 100% of error/timeout traces (tail-based
  sampling, carried `[UNVERIFIED]` as a named technique).
- **Eval ↔ tracing closes the loop:** a failed golden task should drop you straight into its
  trace; production traces of bad runs become *new golden tasks* (the regression set grows from
  real failures). This is 19's "signals drive action (18)" but the action is "add a test."

---

## 5. CONSTRAIN IT INLINE — guardrails = 18 validation + 33 safety, defence-in-depth (RECOMPUTED, reuse 18/33)

Eval and tracing are after-the-fact; guardrails act *every step, in the loop*.

- **Guardrails are 18's validation made agentic.** Reuse 18: validate every boundary crossing.
  Layers: **input** guardrails (reject/clean malicious or off-policy requests — incl. prompt-
  injection, carried to 33), **tool-arg** validation (23's JSON-Schema contract — the deterministic
  half refusing a malformed call), **output** guardrails (schema/format check, PII/secret scan,
  policy filter), and **safety** filters (33). Each is an admission controller (18) on the loop.
- **Defence-in-depth multiplies safety.** RECOMPUTED (§5): L independent layers each catching a
  bad output with prob c let through (1-c)^L. Three 80%-effective layers → **0.8% escape** (vs 20%
  for one). This is 18/20's redundancy identity over *checks* instead of *replicas*.
- **But guardrails have a false-positive (over-refusal) tax.** RECOMPUTED (§5): layers with FP
  rate f reject a GOOD output with prob 1-(1-f)^L; three 2%-FP layers over-refuse **5.9%** of good
  outputs. So guardrails are the 18 throughput-vs-safety tradeoff again: too few → unsafe; too many
  → useless/annoying. Tune, measure the FP rate as its own eval metric.
- **Guardrails are evaluable.** A guardrail is just another component with a golden set (known-bad
  inputs it MUST block + known-good inputs it must NOT block) → precision/recall on the guardrail
  itself. Tracing records every guardrail decision (which layer fired, why) for audit (19 logs).

---

## 6. The bespoke spine (how 31 is taught, not four clusters)

A **trust loop**: Define correct (§1, SWE-bench execution oracle) → Measure offline (§2, golden
set + CI + pass@k/pass^k under cost) → Grade the un-gradeable (§3, LLM-as-judge + 27 ensemble) →
Watch live (§4, Dapper trace tree over the 22 loop) → Constrain inline (§5, 18 defence-in-depth +
33 safety) → feed live failures back into the golden set (close the loop). Every box cross-links
DOWN: oracle→23/28, sampling cost→13/20/32, judge ensemble→27, trace→19/11, guardrail→18/33.

---

## 7. Failure modes (eval/trust-specific)

- **Eval overfit:** tuning the prompt to the test set → looks great offline, fails in prod (hold
  out a private set; SWE-bench's real-issue design).
- **Lexical-oracle trap:** scoring with BLEU/exact-match → rewards plausible-but-wrong (use
  execution where possible — §1).
- **Single-run verdict:** judging a stochastic agent on one run → noise mistaken for signal (§2).
- **Uncalibrated judge:** trusting an LLM grader below the coin line → confidently wrong, amplified
  by ensembling (§3).
- **Trace blind spots:** sampling too low for rare/low-traffic failures (§4); missing causal
  propagation across multi-agent hops (27/11).
- **Guardrail extremes:** too few → unsafe escape; too many → over-refusal tax (§5).
- **Eval cost blowout:** running full O(T²) suites per commit → 32 budget burn (§2/§7).

---

## 8. Build-your-own (ties to the 28 harness)

Ninth harness upgrade (after 30 grounding): wrap the 28 harness in a **trust layer**.
1. **Golden set:** 5-10 tasks each with a deterministic oracle (a test that goes red→green, SWE-
   bench style); a `run_evals()` that runs the loop on each and reports **% resolved** + a 95% CI.
2. **Repeat-k:** run each task k times, report pass@k AND pass^k (expose nondeterminism — §2).
3. **LLM-as-judge** for the one open-ended task; ensemble 3 judges, majority-vote (27) — and show
   it backfires with a bad rubric.
4. **Tracing:** emit a span per turn + per tool call (Dapper model, 19); dump the trace tree for a
   failed task; annotate tokens/cost (→32).
5. **Guardrails:** add input + output + tool-arg validators (18/23); plant a prompt-injection in a
   retrieved passage (30→33) and watch a layer catch it; measure the over-refusal FP rate.
6. **Close the loop:** turn a real failed run's trace into a new golden task.

---

## 9. Provenance

- **PRIMARY (FETCHED+VERIFIED this session):** SWE-bench (Jimenez/Yang et al., ICLR 2024, arXiv
  2310.06770) — `meta/fetched_primaries/swe-bench-2310.06770.{pdf,txt}`, receipt
  `_VERIFIED_2026-06-10_swe-bench.md`. Anchors §1 (execution-based "is it useful").
- **PRIMARY (REUSED, already local):** Dapper (Google TR, 2010) — `dapper-2010.{pdf,txt}`,
  verified in 19. Anchors §4 (spans/trace-tree/sampling). SRE SLO/monitoring/alerting (19) for the
  precision/burn-rate framing. Reflexion (arXiv 2303.11366, verified in 25) for self-eval-as-
  learning-signal (the eval→improve loop, deepened in 33).
- **RECOMPUTED:** `_recompute.py` (19/19) — binomial CI/sample size, pass@k vs pass^k, majority-of-3
  judge voting (27), spans/run + Dapper sampling RSE (19), defence-in-depth escape + FP tax (18),
  lexical≠correctness + %resolved (SWE-bench), suite cost O(T²) (22).
- **REUSED:** 13 (sampling-under-cost), 18 (validation/admission/defence-in-depth), 19 (Dapper
  spans/trace/sampling, SLO precision), 20 (redundancy math), 22 (the loop/O(T²)), 23 (tool
  contract = deterministic oracle), 24 (context budget for traces/judges), 25 (Reflexion self-
  eval), 27 (voting/critic ensemble = LLM-as-judge), 28 (the harness under test), 30 (faithfulness/
  grounding eval), 32 (eval cost), 33 (safety guardrails/injection).
- **`[UNVERIFIED]` carry-forward (none load-bearing):**
  - LLM-as-judge primary (e.g. MT-Bench / Zheng et al. 2306.05685) + the bias taxonomy (position/
    verbosity/self-preference) — named, not fetched.
  - SWE-bench-Verified subset; SWE-agent (2405.15793); HumanEval (Chen 2021) as the saturated
    contrast — referenced, not fetched.
  - RAGAS / faithfulness-groundedness-answer-relevance eval (the 30 grounding-eval owed) — named.
  - OpenTelemetry GenAI semantic conventions + W3C trace-context (the concrete agent-tracing
    standard) — carried from 19, still `[UNVERIFIED]`.
  - Tail-based sampling, guardrail frameworks (NeMo Guardrails / Guardrails-AI), eval harnesses
    (OpenAI Evals / lm-eval-harness) — named, not fetched.
  - Self-consistency (Wang et al. 2203.11171) as the self-vote primary — named.
