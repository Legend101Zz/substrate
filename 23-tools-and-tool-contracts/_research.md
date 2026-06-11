# 23 · tools-and-tool-contracts — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 23 refines the **"parse decision" + "act"**
> boxes of the 22 loop: how the model chooses, calls, validates, and incorporates a **tool**.
> Bespoke structure: a tool is an **API contract between a stochastic caller and deterministic
> code** (not abstract clusters). Full depth: `_research_tools-and-tool-contracts.md`. Math:
> `_recompute.py` (15/15). Primary: Toolformer (Schick et al., NeurIPS 2023). Factcheck:
> `_factcheck_phase1.md` (0 blockers).

## 1. The one idea
**A tool is a contract, not a function.** The bridge from token-space to deterministic
code/the world is a contract — name, typed parameter schema, when-to-use description, typed result.
The hard part isn't calling a function; it's that **the caller is stochastic**: no compiler
enforces the contract at the call site (a probability distribution over tokens), so the contract
must be advertised well enough to be picked correctly AND validated+repaired because the model will
sometimes violate it. Everything hard about tools is the **impedance mismatch between a stochastic
caller and a deterministic, side-effecting, failure-prone callee** — and Part I/II already solved
the callee side (RPC/18, idempotency/17, transactions/07, schemas/07).

## 2. Primary: the four-decision contract surface (Toolformer)
Toolformer (VERIFIED) names exactly the contract surface: a model that decides **which** API,
**when**, **what arguments**, and **how to incorporate results** — from "a handful of
demonstrations." Those four decisions organize the sub-course. The *why* is also verbatim: LMs
"struggle with basic functionality, such as arithmetic or factual lookup" — tools offload what the
model is bad at (compute, current facts, side effects); paper tools = calculator, Q&A, search,
translation, calendar. Teaching contrast (VERIFIED method): Toolformer **bakes** tool use into
weights (self-supervised sample→execute→filter-by-loss→finetune); the modern agent loop (22) does
it **in-context** via prompt schemas + a parser. Same contract, different enforcement locus.

## 3. The contract, walked
- **Schema = the type system** (JSON-Schema-shaped). Triple duty: discovery (model only knows a
  tool from context → fixed prompt cost, §5), generation guidance (enums/required steer valid
  calls), validation key (validates output before exec). Rules from 07/17: small orthogonal
  schemas, enums over free text, explicit side-effecting params, versioned + backward-compatible
  (a tool schema is a published contract like a DB/event schema — additive safe, rename/remove
  breaking).
- **Selection** (which): the model picks one tool. Two scaling pains — context cost (K·S tokens
  every turn, feeds the 22 quadratic) and mis-selection (overlap). Fix at scale: **retrieve tools**
  (advertise k≪K, handoff to 30) — O(K)→O(k) prompt cost + better accuracy.
- **Invocation + validation + repair** (the stochastic-caller defense): parse (prefer structured
  outputs over free-text), validate against schema, **repair loop** (feed the error back as an
  Observation = ReAct "handle exceptions"; bound repairs via 18+22 budget), **authorize** against an
  allow-list + permissions before exec (hallucinated tool/arg dies here; handoff to 33).
- **Execution = the world** (reuse 17/18/07/03): it's an RPC → timeout/retry/breaker (18) +
  observe-the-error (22); side effects need idempotency keys → exactly-once-effect (17/21);
  mutating tools may need a transaction/outbox (07/17); the result becomes an Observation that must
  be **typed**, **size-bounded** before re-entering the transcript (oversized result blows the
  window — 24/25/22 quadratic), and **untrusted** (prompt-injection carrier → 33).

## 4. The economics (RECOMPUTED — `_recompute.py`, 15/15)
- **Toolbox tax**: K·S tokens/turn (40·150=6000 = 4.69% of a 128k window, 120k tokens over 20
  turns) — a fixed addend to the 22 prefix `p`, so it amplifies the quadratic.
- **Retrieval break-even**: K > k + r/S ≈ 5.33 → retrieving relevant tools wins for any real
  toolbox (saving 5200 tok/turn at K=40,k=5). Same "don't put everything in context" law as 25/30.
- **Result budget**: max result tokens = W−(p+(t−1)g) (120k@t1, 110.5k@t20); a 1 MB JSON (~250k
  tok) overflows → keep ≤44.2% at t20.
- **Repair bound**: R_max=3 → ≤4 model calls/step worst case.
- **Selection compounding**: P(≥1 wrong tool) = 1−(1−q)^N (q=0.02 → 9.6%/18.3%/63.6% at N=5/10/50)
  — the 13/20/21 fan-out identity, now over loop steps → long tasks REQUIRE validation/repair.
- **Idempotency retention** = 86400s for write tools (17/21).

## 5. Failure modes (tool subset of the 22 table)
wrong tool (→ tighter schemas + retrieve, 30) · malformed args (→ validate+repair, structured
outputs) · hallucinated tool/arg (→ allow-list+authz, 33) · timeout/5xx (→ 18 + observe) · double
side-effect (→ idempotency, 17) · oversized result (→ bound/summarize/reference, 24/25) · prompt
injection via result (→ untrusted results, 33).

## 6. Build-your-own
Add a **typed tool registry** to the 22 loop: `{name, json_schema, handler, side_effecting}` +
validator + repair loop + allow-list + per-tool timeout/retry (18) + idempotency keys for writes
(17) + result-size bounding. Second upgrade toward the 28 capstone (loop → **tools** → memory →
subagents → budgets → compaction).

## 7. Provenance summary
- **VERIFIED primary**: Toolformer (arXiv 2302.04761) — `meta/fetched_primaries/toolformer-2302.04761.{pdf,txt}`,
  receipt `_VERIFIED_2026-06-10_agentic.md`.
- **RECOMPUTED**: `_recompute.py` (15/15).
- **REUSED**: 03, 07, 08/16, 13, 17, 18, 20, 21, 22.
- **`[UNVERIFIED]` carry-forward**: provider function-calling/tool-use specs (OpenAI/Anthropic,
  structured outputs); JSON Schema spec; MCP transport (→ 29); Toolformer deeper benchmark numbers.
  None load-bearing for the contract model.

---
**23 reconciled.** Next in dependency order: **24-prompts-and-context-engineering** (refines the
"assemble context" box; the quadratic of 22 + the toolbox tax of 23 are its forcing functions).
