# VERIFIED 2026-06-10 — SWE-bench (Jimenez, Yang et al., ICLR 2024, arXiv 2310.06770)

Opportunistic fetch this session (Wave 14). arxiv.org reachable (HTTP 200). PDF fetched to
`swe-bench-2310.06770.pdf` (4.5 MB, 52 pp), text extracted to `swe-bench-2310.06770.txt`
(153,448 chars) via a THROWAWAY `/tmp/pdfx-venv` (uv + pypdf from Walmart external-pypi),
REMOVED after extraction. `.code-puppy-venv` never touched.

Anchors the **31 "is it useful" execution-based evaluation** definition owed from 28/30, and
upgrades the carried `[UNVERIFIED]` SWE-bench note in **28** (build-your-own-coding-harness).

## Verbatim load-bearing quotes (line refs into the .txt)

- **The benchmark (abstract):** "we introduce SWE-bench, an evaluation framework consisting of
  2,294 software engineering problems drawn from real GitHub issues and corresponding pull
  requests across 12 popular Python repositories. Given a codebase along with a description of an
  issue to be resolved, a language model is tasked with editing the codebase to address the issue."
- **Why it is hard (abstract):** resolving issues "frequently requires understanding and
  coordinating changes across multiple functions, classes, and even files simultaneously, calling
  for models to interact with execution environments, process extremely long contexts and perform
  complex reasoning that goes far beyond traditional code generation tasks."
- **Headline result (abstract):** "The best-performing model, Claude 2, is able to solve a mere
  1.96% of the issues." (Restated §1: "Using a BM25 retriever, Claude 2 is only able to resolve
  1.96% of the issues.")
- **Execution-based evaluation metric (§2.2, lines 132-136):** "To evaluate a proposed solution,
  we apply the generated patch, using unix's patch program, to the codebase and then execute the
  unit and system tests associated with the task instance. If the patch applies successfully and
  all of these tests pass we consider the proposed solution to have successfully resolved the
  issue. The metric for our benchmark is the percentage of task instances that are resolved."
- **Edits as patches (§2.2, lines 130-131):** "we represent edits as patch files, which specify
  which lines in the codebase to modify in order to resolve the issue."
- **Tests are the oracle (§2.1, line 115):** "the user likely contributed tests to check whether
  the issue has been resolved." Stage III execution filter (line 116): "For each candidate task,
  we apply the PR's test content."
- **Fail-to-pass / pass-to-pass tests (§2.2, line 153):** tests "to test the reference solution,
  and 40% of instances have at least two fail-to-pass tests."
- **Saturation motivation (§1):** "existing benchmarks have become saturated ... and fail to
  capture the frontier of what state-of-the-art LMs can and cannot do."

## What this anchors in 31 (and 28)
- **The "is it useful" definition (owed from 28/30):** correctness for an agent is *task
  resolution under execution*, NOT lexical/surface similarity to a reference. A patch that
  "looks right" but fails the tests is NOT resolved. This grounds 31's offline-eval +
  golden-task spine: the golden artifact is a **test suite that must go red→green**, the metric
  is **% resolved**, and the judge is a **deterministic test harness**, not a model.
- **28 upgrade:** the carried `[UNVERIFIED]` SWE-bench note in 28 → VERIFIED (benchmark exists,
  execution-based, % resolved, Claude-2 1.96% baseline).

Still `[UNVERIFIED]` / not fetched: SWE-bench-Verified subset, SWE-agent (2405.15793),
LLM-as-judge primaries (e.g. MT-Bench / Zheng 2306.05685), RAGAS, OpenTelemetry/W3C
trace-context. Noted for later; none load-bearing for 31's model.
