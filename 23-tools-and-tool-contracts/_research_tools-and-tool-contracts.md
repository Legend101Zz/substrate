# 23 · tools-and-tool-contracts — section brief (contract/schema walkthrough)

> Phase-1 brief (NO course prose). 23 refines the **"parse decision" + "act"** boxes of the 22
> loop: how the model chooses, calls, and incorporates a **tool**. Bespoke structure: a tool is an
> **API contract** between a stochastic caller (the LLM) and deterministic code — so this brief
> walks the contract (schema → selection → invocation → result → failure → security), NOT abstract
> source clusters. Primary anchor: Toolformer (Schick et al., NeurIPS 2023). Math: `_recompute.py`.

Cross-link map (a tool call reuses Part I/II primitives):
- a tool call IS an RPC ↔ **03** networking, **18** timeout/retry/breaker on every call
- side-effecting tools ↔ **17** idempotency / exactly-once-effect; **07** transactions if it writes
- tool result caching ↔ **08/16** caching; tool selection at scale ↔ **30** retrieval over tools
- the schema is a **typed contract** ↔ **07** schema-on-write; **17** schema evolution discipline
- tool errors observed-and-adapted ↔ **22 §5**, **18** failure handling, **31** guardrails

---

## 1. The primitive — a tool is a contract, not a function
A "tool" is the bridge from the model's token space to deterministic code/the world. The bridge is
a **contract**: a name, a typed parameter schema, a description of *when* to use it, and a typed
result. The hard part is NOT "calling a function" — it is that the **caller is stochastic**. A
normal API has a compiler/type-checker enforcing the contract at the call site; here the call site
is a probability distribution over tokens. So the contract must be (a) *advertised* well enough
that the model picks the right tool with the right args, and (b) *validated + repaired* on the way
in because the model WILL sometimes violate it.

Thesis: **everything hard about tools is the impedance mismatch between a stochastic caller and a
deterministic, side-effecting, failure-prone callee.** Part I/II already solved the callee side
(RPCs/18, idempotency/17, transactions/07, schemas/07); 23 is about the *caller* side and the
*contract* in the middle.

## 2. Primary: Toolformer (Schick et al., NeurIPS 2023, arXiv 2302.04761)
Toolformer is the load-bearing primary for *why tools and what the contract must specify*. Verbatim
(abstract, VERIFIED in `meta/fetched_primaries/toolformer-2302.04761.txt`):

> "We introduce Toolformer, a model trained to **decide which APIs to call, when to call them, what
> arguments to pass, and how to best incorporate the results** into future token prediction. This
> is done in a self-supervised way, requiring nothing more than a handful of demonstrations for
> each API."

Those four decisions ARE the tool-use contract surface, and they organize this sub-course:
1. **which** API → tool selection (§4)
2. **when** → invocation policy / the loop's decision (22)
3. **what arguments** → the parameter schema + validation (§3, §5)
4. **how to incorporate results** → result typing + observation formatting (§6)

The *motivation* is also verbatim: LMs "struggle with basic functionality, such as arithmetic or
factual lookup, where much simpler and smaller models excel" — tools offload exactly the things the
model is bad at (compute, current facts, side effects). Tools fetched in the paper: "a calculator,
a Q&A system, a search engine, a translation system, and a calendar."

Method note (VERIFIED, §2 of paper): Toolformer is **self-supervised** — sample candidate API
calls, **execute** them, and **filter out all calls which do not reduce the loss** over the next
tokens; keep the helpful ones and finetune. This is a useful teaching contrast: Toolformer *bakes*
tool use into weights; the modern agent loop (22) does it *in-context* via the prompt + a parser.
Both rely on the same contract; only the enforcement locus differs.

## 3. The schema — the contract's type system
A tool is advertised to the model as a structured schema (in practice JSON-Schema-shaped: name,
description, parameters with types/enums/required/constraints). The schema does triple duty:
- **discovery**: the model only knows a tool exists if it's in the context (handoff to 24 — schemas
  are a fixed cost in the prompt budget; 30 — retrieve tools when there are too many).
- **generation guidance**: types/enums/`required` steer the model toward valid calls; the more
  constrained the schema, the fewer malformed calls.
- **validation key**: the same schema validates the model's output before execution (§5).

Design rules (grounded in 07 schema-on-write + 17 schema evolution): keep schemas small and
orthogonal; prefer enums over free text; make side-effecting params explicit; version schemas and
evolve them backward-compatibly (a tool's schema is a published contract, exactly like a DB schema
or an event schema in 17 — additive changes safe, renames/removals breaking).

## 4. Tool selection — the cost of a big toolbox
The model must pick one tool from the advertised set. Two scaling problems:
- **Context cost**: every tool schema sits in the prompt every turn → adds to the quadratic of
  22 §5. K tools × S tokens/schema is paid on *every* model call. RECOMPUTED in `_recompute.py`.
- **Selection accuracy**: more tools + overlapping descriptions → more mis-selection. The fix at
  scale is **retrieval over tools** (handoff to 30): embed the tools, retrieve the top-k relevant
  to the current step, advertise only those. This turns an O(K) prompt cost into O(k) and improves
  accuracy — the same "don't put everything in context" discipline as memory (25) and RAG (30).

## 5. Invocation + validation + repair (the stochastic-caller defense)
Because the caller is stochastic, the call MUST be treated as untrusted input:
1. **Parse** the model's proposed call out of its output (structured/function-calling output makes
   this reliable; free-text parsing is brittle — prefer provider structured outputs).
2. **Validate** against the schema (types, enums, required, ranges). Reject early on mismatch.
3. **Repair loop**: on validation failure, feed the error back as an Observation and let the loop
   retry (this is ReAct's "handle exceptions" applied to malformed calls). Bound the repair retries
   (reuse 18 + the 22 step budget) so a model that can't satisfy the schema doesn't loop forever.
4. **Authorize**: check the call against an allow-list + permissions BEFORE executing (handoff to
   33 safety). A hallucinated tool name or out-of-scope argument dies here.

## 6. Execution semantics — the callee is the world (reuse 17/18/07)
Once validated, executing a tool is a *systems* problem already solved in Part I/II:
- **It's an RPC** (03): network, latency, partial failure. Wrap every call in timeout + retry +
  circuit breaker (18). Observe the error and return it to the loop rather than crashing (22 §5).
- **Side effects need idempotency** (17): a retried "send_email"/"charge_card" must not double-fire.
  Attach an idempotency key per logical action → exactly-once-EFFECT (the same impossibility +
  pattern as 21 chat/payments). Read-only tools are safely retryable; write tools are not.
- **Transactional tools** (07): a tool that mutates shared state may need a transaction / outbox so
  the effect and its record commit together (reuse 17 outbox/CDC).
- **Result incorporation**: the tool result becomes an Observation. It must be (a) typed/parsed,
  (b) **size-bounded** before it re-enters the transcript (a tool returning 1 MB of JSON blows the
  context window — truncate/summarize/store-and-reference; ties to 24 + 25 + the 22 quadratic), and
  (c) **untrusted** (a tool result can carry a prompt-injection payload → 33).

## 7. Failure modes (the tool-specific subset of the 22 failure table)
| failure | mechanism | fix |
|---|---|---|
| wrong tool selected | overlapping/vague descriptions, too many tools | tighter schemas; retrieve tools (30) |
| malformed arguments | stochastic caller violates schema | validate + repair loop (§5); structured outputs |
| hallucinated tool/arg | model invents a name/param | allow-list + authz (§5, 33) |
| tool timeout / 5xx | the world fails (RPC) | timeout/retry/breaker (18); observe + adapt |
| double side-effect | retried write tool | idempotency key → exactly-once-effect (17) |
| oversized result | tool returns huge payload | bound/summarize/reference (24/25); the 22 quadratic |
| prompt injection via result | untrusted tool output steers the model | treat results as untrusted (33); sandboxing |

## 8. The quantitative core (RECOMPUTED in `_recompute.py`)
- **Toolbox prompt cost**: `K * S` tokens/turn just to advertise tools; its share of the window;
  break-even K where retrieval-over-tools (advertise k≪K) wins.
- **Result-size budget**: max tool-result tokens that keep turn `t` under the window given the 22
  prefix+growth model; what truncation ratio a big result needs.
- **Repair-retry bound**: validation-failure retries capped under the step budget (reuse 18/22).
- **Selection error compounding**: per-call mis-selection probability `q` over an N-step task →
  P(≥1 wrong tool) = `1-(1-q)^N` (the SAME fan-out identity as 13/20/21 — here over loop steps).
- **Idempotency-key retention** for side-effecting tools = max retry horizon (reuse 17/21).

## 9. Build-your-own target
Add a **typed tool registry** to the 22 minimal loop: `{name, json_schema, handler, side_effecting}`;
a validator + repair loop; an allow-list; per-tool timeout/retry (18); idempotency keys for write
tools (17); and result-size bounding. This is the second upgrade on the path to the 28 capstone
harness (loop → **tools** → memory → subagents → budgets → compaction).

## 10. Sources & provenance
- **PRIMARY (fetched + verified this session)**: Toolformer, Schick et al., NeurIPS 2023,
  arXiv 2302.04761 — `meta/fetched_primaries/toolformer-2302.04761.{pdf,txt}`; receipt
  `meta/fetched_primaries/_VERIFIED_2026-06-10_agentic.md`. Anchors §1-2 (the four decisions; why
  tools; self-supervised baking vs in-context use).
- **REUSED (line-verified Part I/II)**: 03 (RPC), 07 (schema/transactions), 08/16 (result caching),
  17 (idempotency/exactly-once-effect, schema evolution, outbox/CDC), 18 (timeout/retry/breaker),
  13/20/21 (the `1-(1-q)^N` identity), 22 (the loop, the quadratic, the step budget).
- **RECOMPUTED**: `_recompute.py` (toolbox cost, result budget, repair bound, selection compounding,
  idempotency retention).
- **`[UNVERIFIED]` (carry-forward — do NOT harden into prose):**
  - Provider function-calling / tool-use specs (OpenAI function calling, Anthropic tool use, JSON
    mode / structured outputs) — the de-facto contract format; NOT fetched this session.
  - JSON Schema spec (json-schema.org) as the formal type system — referenced, not fetched.
  - MCP as a *tool transport/registry* standard — deferred to 29 (mcp-skills-and-connectors).
  - Toolformer's quantitative downstream-task gains (specific benchmark numbers beyond the abstract)
    — only the abstract + method were verbatim-verified; deeper numbers deferred to Phase 2.
  - ReAct already verified in 22 (reused here for the act/observe edge).
