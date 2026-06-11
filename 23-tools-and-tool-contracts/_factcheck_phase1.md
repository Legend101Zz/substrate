# 23 · Phase-1 factcheck — tools-and-tool-contracts

> Method (same discipline as 13-22): every load-bearing claim is (a) RECOMPUTED in `_recompute.py`
> (15/15 pass), (b) VERIFIED verbatim against a primary in `meta/fetched_primaries/`, (c) REUSED
> from a line-verified Part I/II sub-course, or (d) flagged `[UNVERIFIED]` carry-forward. 0 blockers.

## Bespoke structure note
23 models a tool as an **API contract between a stochastic caller and deterministic code**, so the
brief walks the contract (schema → selection → invocation/validation → execution → failure →
security), NOT abstract source clusters and NOT the 13-20 four-cluster shape. Plan-sanctioned.

## Primary fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools", NeurIPS 2023 (arXiv 2302.04761) | `toolformer-2302.04761.{pdf,txt}` | §1-2: the four contract decisions (which/when/what-args/how-incorporate); why tools (offload arithmetic/lookup); self-supervised baking vs in-context use |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_agentic.md`.

### Verified claims (Toolformer)
- "a model trained to decide which APIs to call, when to call them, what arguments to pass, and how
  to best incorporate the results into future token prediction ... requiring nothing more than a
  handful of demonstrations for each API" — VERIFIED verbatim. Anchors the four-decision contract
  surface (§2) that organizes the whole sub-course.
- LMs "struggle with basic functionality, such as arithmetic or factual lookup, where much simpler
  and smaller models excel" — VERIFIED verbatim. Anchors WHY tools exist (§2).
- Tools used: "a calculator, a Q&A system, a search engine, a translation system, and a calendar"
  — VERIFIED verbatim.
- Method "Sample → Execute → Filter [calls that don't reduce loss] → finetune" (self-supervised)
  — VERIFIED (§2 of paper). Anchors the bake-into-weights vs in-context contrast (§2).

## Recomputed claims (`_recompute.py`, 15/15)
- Toolbox prompt cost = K·S tokens/turn (40·150=6000), 4.69% of a 128k window, 120k tokens billed
  over a 20-turn task (feeds the 22 quadratic). PASS.
- Retrieval-over-tools net saving (K-k)·S - r = 5200 tok/turn; break-even K = k + r/S ≈ 5.33
  (retrieval wins for any real toolbox; handoff to 30). PASS.
- Tool-result size budget: max result tokens = W-(p+(t-1)g) (120000 at t=1, 110500 at t=20); a
  ~250k-token 1 MB JSON result overflows → keep ≤44.2% at t=20 (must summarize/reference; 24/25). PASS.
- Repair-retry bound R_max=3 → ≤4 model calls/step worst case (reuse 18 + 22 budget). PASS.
- Selection-error compounding 1-(1-q)^N over loop steps (q=0.02 → 9.6% / 18.3% / 63.6% at N=5/10/50;
  the SAME fan-out identity as 13/20/21). PASS.
- Idency-key retention 86400s for write tools → exactly-once-effect (17/21). PASS.

## Reused (line-verified Part I/II)
- 03 (a tool call is an RPC); 07 (schema-on-write, transactions); 08/16 (result caching); 17
  (idempotency/exactly-once-effect, schema evolution, outbox/CDC); 18 (timeout/retry/breaker);
  13/20/21 (the `1-(1-q)^N` identity); 22 (the loop, the quadratic, the step budget, observe-error).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Provider function-calling / tool-use specs (OpenAI function calling, Anthropic tool use, JSON
  mode / structured outputs) — the de-facto contract format; NOT fetched (provider docs historically
  blocked; retry next session).
- JSON Schema spec (json-schema.org) as the formal type system — referenced, not fetched.
- MCP as a tool transport/registry standard — deferred to 29.
- Toolformer's specific downstream benchmark numbers beyond the abstract — only abstract + method
  verbatim-verified; deeper numbers deferred to Phase 2.

## Verdict
23 is honest and contract-appropriate: the four-decision contract surface + the "why tools" motive
are VERIFIED against Toolformer; the contract economics (toolbox cost, retrieval break-even, result
budget, repair bound, selection compounding, idempotency) are RECOMPUTED; execution semantics are
REUSED from line-verified 03/07/17/18. Residual `[UNVERIFIED]` are provider/spec formats, none
load-bearing for the contract model. Reconcile into `_research.md`.
