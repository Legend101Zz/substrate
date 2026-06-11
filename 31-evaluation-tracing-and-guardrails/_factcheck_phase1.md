# 31 · Phase-1 factcheck — evaluation-tracing-and-guardrails

> Method (same discipline as 13-30): every load-bearing claim is (a) VERIFIED verbatim against a
> fetched primary, (b) RECOMPUTED in `_recompute.py` (19/19 pass), (c) REUSED from a line-verified
> Part I/II + 22-30 anchor, or (d) flagged `[UNVERIFIED]` carry-forward. **0 blockers.**

## Bespoke structure note
31 is a **TRUST-LOOP WALKTHROUGH** (Define correct → Measure offline → Grade the un-gradeable →
Watch live → Constrain inline → feed failures back), NOT abstract clusters and NOT the 13-20
four-cluster shape, and deliberately NOT a copy of 19's signal taxonomy. It is the agentic trust
layer: eval (does it work?) + tracing (what did it do?) + guardrails (can it go off-rails?).

## Primary fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Jimenez, Yang, Wettig, Yao, Pei, Press, Narasimhan, "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ICLR 2024 (arXiv 2310.06770) | `swe-bench-2310.06770.{pdf,txt}` | execution-based "is it useful" definition (owed from 28/30); % resolved metric; tests-as-oracle; lexical≠correctness; benchmark-saturation motivation |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_swe-bench.md` (verbatim quotes + line refs).

### Verified claims (SWE-bench — verbatim)
- **Execution-based evaluation (THE owed "is it useful" definition):** "we apply the generated
  patch, using unix's patch program, to the codebase and then execute the unit and system tests
  associated with the task instance. If the patch applies successfully and all of these tests pass
  we consider the proposed solution to have successfully resolved the issue." VERIFIED. (§1, §6.)
- **The metric:** "The metric for our benchmark is the percentage of task instances that are
  resolved." VERIFIED. (§1/§2 — binary aggregate, not a similarity mean.)
- **Tests are the oracle:** "the user likely contributed tests to check whether the issue has been
  resolved"; "40% of instances have at least two fail-to-pass tests." VERIFIED. (§1 — golden
  artifact is a test suite + no-regression via pass-to-pass.)
- **Headline difficulty:** "The best-performing model, Claude 2, is able to solve a mere 1.96% of
  the issues." VERIFIED. (§1 — hard evals discriminate.)
- **Saturation motivation:** "existing benchmarks have become saturated ... fail to capture the
  frontier of what state-of-the-art LMs can and cannot do." VERIFIED. (§1.)
- **Edits as patches / multi-file:** "we represent edits as patch files"; resolving "frequently
  requires ... coordinating changes across multiple functions, classes, and even files ...
  interact with execution environments." VERIFIED. (§1/§8 — ties to the 28 harness.)

### Verified-by-reuse (Dapper, already local + verified in 19)
- **Span / trace tree / parent-id / 64-bit trace-id; thread-local + async context propagation;
  send-before-receive clock bounds; 1/1024 + adaptive sampling.** VERIFIED in 19's
  `_VERIFIED_2026-06-10_observability.md`; REUSED here for §4 (the agent loop as a Dapper trace
  tree, sampling RSE). No re-verification needed — same fetched primary.

## Recomputed claims (`_recompute.py`, 19/19)
- **Golden-set sample size:** 95% CI half-width 1.96·√(p(1-p)/N); N=10→±31%, N=1000→±3%; ~1067
  tasks for ±3% at p=0.5. PASS. (19 measurement-precision over an eval set.)
- **pass@k vs pass^k:** p=0.6 → pass@3=0.936 (lenient) vs pass^3=0.216 (strict); a single run is
  an unreliable verdict for a stochastic agent. PASS.
- **LLM-as-judge ensemble (27 Condorcet):** majority-of-3, a³+3a²(1-a): a=0.8→0.896 (1.9× fewer
  errors), a=0.9→0.972 (3.6×); backfires at a=0.4→0.352. PASS. (27 voting reused over GRADERS.)
- **Tracing (19 Dapper):** 1+T+T·m spans/run (=49 at T=12,m=3); sampling RSE √((1-s)/(s·n)) →
  rare/low-volume failures need higher s. PASS.
- **Guardrails (18 defence-in-depth):** escape (1-c)^L → 3×80% layers = 0.8% escape; FP tax
  1-(1-f)^L → 3×2% = 5.9% over-refusal. PASS.
- **Lexical≠correctness + %resolved (SWE-bench):** 95%-overlap patch can FAIL, 40%-overlap can
  PASS; metric = mean of binary resolutions. PASS.
- **Eval cost = S·(22 O(T²)):** 2,294 tasks × 365k tok = 837M tok; quadratic in turns → gate/sample
  (→32). PASS.

## Reused (line-verified Part I/II + 22-30)
13 (sampling under cost); 18 (validation/admission control/defence-in-depth redundancy);
19 (Dapper spans/trace/sampling, SLO/precision); 20 (redundancy math); 22 (the loop, O(T²) cost);
23 (tool contract = the deterministic oracle half); 24 (context budget for traces/judges);
25 (Reflexion self-eval as learning signal); 27 (voting/critic ensemble ≡ LLM-as-judge);
28 (the harness under test; SWE-bench upgrade); 30 (faithfulness/grounding eval).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- LLM-as-judge primary (MT-Bench / Zheng et al. 2306.05685) + judge bias taxonomy
  (position/verbosity/self-preference/leniency) — named, not fetched.
- SWE-bench-Verified subset; SWE-agent (2405.15793); HumanEval (Chen et al. 2021) saturated
  contrast — referenced, not fetched.
- RAGAS / faithfulness-groundedness eval (the 30 grounding-eval owed) — named.
- OpenTelemetry GenAI semantic conventions + W3C trace-context (concrete agent-tracing standard) —
  carried from 19, still `[UNVERIFIED]`.
- Tail-based sampling; guardrail frameworks (NeMo Guardrails / Guardrails-AI); eval harnesses
  (OpenAI Evals / lm-eval-harness); self-consistency (Wang et al. 2203.11171). None load-bearing.

## Verdict
31 is honest and trust-layer-appropriate: the load-bearing new concept — **correctness =
execution-based task resolution, % resolved, tests-as-oracle, lexical≠correct** — is VERIFIED
verbatim against SWE-bench; tracing REUSES the already-verified Dapper primary (19); the judge
ensemble REUSES 27's Condorcet identity; guardrails REUSE 18's defence-in-depth; all economics are
RECOMPUTED. Residual `[UNVERIFIED]` are secondary primaries (LLM-judge/RAGAS/OTel) + advanced
techniques, none load-bearing for the trust model. Reconcile into `_research.md`. **0 blockers.**
