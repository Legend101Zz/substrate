# 23 — Tools and Tool Contracts · _structure.md

**Identity:** refines the "parse decision" + "act" boxes of the 22 loop — how the model chooses,
calls, validates, and incorporates a tool. The one idea: **a tool is a contract, not a function** —
an API contract between a stochastic caller and deterministic, side-effecting, failure-prone code.

**Bespoke shape — "walk the contract surface, defending against a stochastic caller at each seam."**
NOT a function-calling tutorial. A tool is the bridge from token-space to deterministic code, and the
hard part is that the caller is STOCHASTIC — no compiler enforces the contract at the call site, so it
must be advertised well enough to be picked correctly AND validated+repaired because the model will
violate it. The sub-course walks Toolformer's four-decision contract surface (which / when / what args
/ how to incorporate) and at every seam shows that Part I/II already solved the callee side (RPC/18,
idempotency/17, transactions/07, schemas/07). Toolformer is the primary (VERIFIED). Math recomputed
(15/15). Second harness upgrade after the 22 loop.

## Dependency position
- **Depends on:** 22 (the loop boxes this refines), 07 (schemas = type system, transactions for
  mutating tools), 17 (idempotency → exactly-once-effect for side-effecting tools), 18 (execution =
  RPC → timeout/retry/breaker), 03 (RPC transport), 08/16 (tool-result caching), 13/20/21 (selection
  compounding = the fan-out identity).
- **Feeds into:** 24 (the toolbox tax K·S amplifies the quadratic; result-size bounding), 30 (retrieve
  tools when K is large — same law as RAG), 33 (allow-list/authz; untrusted results = injection
  carrier), 29 (MCP as the transport for tool contracts), 28 (the typed tool registry stage).
- **Appendix links DOWN:** I-sandboxing (the act box's blast radius), M-agentic-papers (Toolformer),
  F-postgres (transactions/outbox for mutating tools). 23 owns the contract model.

## Chapter specs (3–5 lines each)
1. **The one idea: a tool is a contract, not a function** — name + typed parameter schema + when-to-use
   description + typed result. Everything hard is the impedance mismatch between a stochastic caller and
   a deterministic, side-effecting, failure-prone callee — and Part I/II already solved the callee side.
2. **The four-decision contract surface (Toolformer)** — a model decides WHICH api, WHEN, WHAT args, and
   HOW to incorporate results (VERIFIED) — these four decisions organize the sub-course. The why
   (VERIFIED): LMs "struggle with basic functionality such as arithmetic or factual lookup" → tools
   offload what the model is bad at (compute, current facts, side effects). Teaching contrast: Toolformer
   BAKES tool use into weights (self-supervised); the agent loop (22) does it IN-CONTEXT via schemas +
   a parser. Same contract, different enforcement locus.
3. **Schema = the type system** — JSON-Schema-shaped, triple duty: discovery (model only knows a tool
   from context → fixed prompt cost), generation guidance (enums/required steer valid calls), validation
   key. Rules from 07/17: small orthogonal schemas, enums over free text, explicit side-effecting params,
   versioned + backward-compatible (a tool schema is a published contract like a DB/event schema —
   additive safe, rename/remove breaking).
4. **Selection (which) & the scaling pains** — the model picks one tool; two pains: context cost (K·S
   tokens every turn, feeds the 22 quadratic) and mis-selection (overlap). Fix at scale: RETRIEVE tools
   (advertise k≪K, handoff to 30) — O(K)→O(k) prompt cost + better accuracy. P(≥1 wrong) = 1−(1−q)^N
   (the fan-out identity) → long tasks REQUIRE validation/repair.
5. **Invocation, validation & repair (the stochastic-caller defense)** — prefer structured outputs over
   free-text parsing; validate against schema; repair loop (feed the error back as an Observation =
   ReAct "handle exceptions"; bound repairs via 18+22 budget, R_max=3 → ≤4 calls/step); authorize
   against an allow-list + permissions before exec (hallucinated tool/arg dies here → 33).
6. **Execution = the world** — it's an RPC → timeout/retry/breaker (18) + observe-the-error (22); side
   effects need idempotency keys → exactly-once-effect (17/21); mutating tools may need a transaction/
   outbox (07/17); the result becomes an Observation that must be TYPED, SIZE-BOUNDED before re-entering
   the transcript (a 1MB JSON ≈ 250k tok overflows the window — 24/25/22), and treated as UNTRUSTED
   (prompt-injection carrier → 33).

## Paired build lab (/build → tool-registry stage of own-coding-agent-harness, 28)
Add a typed tool registry to the 22 loop: `{name, json_schema, handler, side_effecting}` + validator +
repair loop + allow-list + per-tool timeout/retry (18) + idempotency keys for writes (17) + result-size
bounding. Break it: remove validation → malformed-arg crashes; remove idempotency → double side-effect;
feed an oversized result → window overflow. Second harness upgrade (loop → tools → …).

## Diagrams needed
- The contract: stochastic caller (token distribution) → contract surface → deterministic callee.
- The four decisions (which/when/what-args/how-to-incorporate) as the sub-course map.
- Schema's triple duty (discovery / generation guidance / validation).
- Selection at scale: K-tool toolbox tax vs retrieved k≪K (break-even K > k + r/S).
- Invocation pipeline: parse → validate → repair-loop (bounded) → authorize → execute.
- Execution as RPC with 18/17 defenses; result → typed + size-bounded + untrusted before transcript.
- Selection compounding 1−(1−q)^N over loop steps (why long tasks need repair).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED primary:** Toolformer (arXiv 2302.04761; `meta/fetched_primaries/toolformer-2302.04761.*`,
  receipt `_VERIFIED_2026-06-10_agentic.md`) — the four decisions, "struggle with arithmetic/lookup,"
  bake-vs-in-context.
- **RECOMPUTED (15/15):** toolbox tax K·S; retrieval break-even K > k + r/S; result budget; repair bound
  R_max; selection compounding 1−(1−q)^N; idempotency retention 86400s.
- **`[UNVERIFIED]` carry-forward (none load-bearing for the contract model):** provider function-calling/
  structured-output specs (OpenAI/Anthropic); JSON Schema spec; MCP transport (→29); deeper Toolformer
  benchmark numbers. Teach the contract model now; do NOT harden vendor specifics until fetched.
- **Boundary discipline:** tool retrieval at scale → 30; allow-list/authz/untrusted-results → 33; MCP
  transport → 29; idempotency/transactions/outbox internals → 17/07; RPC/timeout/breaker → 18/03;
  sandbox → appendix I. 23 owns the contract surface only.
