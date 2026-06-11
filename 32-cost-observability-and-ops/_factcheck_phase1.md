# 32 · Phase-1 factcheck — cost-observability-and-ops

> Method (same discipline as 13-31): every load-bearing claim is (a) RECOMPUTED in `_recompute.py`
> (14/14 pass), (b) REUSED from a line-verified Part I/II + 22-31 anchor, or (c) flagged
> `[UNVERIFIED]` carry-forward. **NO new primary required** — 32 is an operational synthesis
> (like 21): it prices already-verified mechanisms. **0 blockers.**

## Bespoke structure note
32 is a **COST-LIFECYCLE WALKTHROUGH** (Account → Attribute → Budget/Cap → Optimize → Operate),
NOT abstract clusters and NOT the 13-20 four-cluster shape. It is 19 observability + 18 control +
20 capacity **denominated in dollars/tokens**, sitting on 22's quadratic. Plan-sanctioned ("the 22
O(T²) economics made operational: token/$ accounting, budgets, caching ROI 24, per-tenant quotas
18, the cost dashboards 19").

## No new primary (why)
Every claim reduces to an already-FETCHED+VERIFIED mechanism, re-priced:
- **22 loop O(T²)** — the transcript-regrowth cost model, recomputed in 22 (ReAct-anchored loop).
- **24 compaction + prefix-cache** — VERIFIED via CoT (format/context) + recomputed in 24
  (O(T²)→O(T); prefix-cache discount helps prefix only).
- **18 token-bucket / admission / load-shedding** — VERIFIED via RFC 6585 §4 + SRE Handling-
  Overload (recomputed in 18); here applied over $ as per-tenant quotas.
- **19 Dapper spans + metrics/cardinality + SLO/burn-rate** — VERIFIED in 19; here the cost
  dashboard attributes $ per span tag.
- **20 tail + capacity** — VERIFIED via Tail-at-Scale; here the cost tail (runaway runs).
- **30 retrieve-vs-stuff**, **31 eval cost / token-carrying spans**, **26 idempotent resume**.

## Recomputed claims (`_recompute.py`, 14/14)
- **Token/$ over 22's O(T²):** run cost super-linear in turns (T=20 >2× T=10); input/quadratic term
  dominates the bill at high T. PASS.
- **Compaction $ saving (24):** capped input O(T) vs uncapped O(T²); T=100 saves ~$18.8/run, saving
  grows with T. PASS.
- **Prefix-cache ROI + limit (24):** 10× cheaper prefix on hits; does NOT touch the 1.84M-token
  quadratic transcript (caching ≠ compaction). PASS.
- **Per-tenant quota (18 over $):** fair-share pool/N; runaway tenant shed at cap → bounded blast
  radius. PASS.
- **Cost tail (20) + per-run cap (22):** mean 20× median from one runaway; T≤20 cap cuts total 10×.
  PASS.
- **Attributable cost signal (19):** LLM = 80% of the bill → optimize the biggest tag. PASS.
- **Model routing:** 70/30 cheap/dear → blended $1.04/M vs $3/M. PASS.

## Reused (line-verified Part I/II + 22-31)
18 (rate-limiting/admission/load-shedding); 19 (Dapper spans/metrics/cardinality/SLO/burn-rate);
20 (tail/capacity); 22 (loop O(T²) cost); 24 (compaction O(T²)→O(T), prefix-cache discount);
26 (idempotent resume so crashes don't re-bill); 30 (retrieve-vs-stuff budget); 31 (eval cost,
trace spans carry token counts).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Provider pricing tables, prompt-caching mechanics, batch-API discounts — vendor docs; prices in
  `_recompute.py` are deliberately illustrative knobs, not quoted figures.
- FinOps / cloud-cost-management frameworks; cost-observability tooling (Helicone, Langfuse,
  OpenTelemetry GenAI cost semantic conventions) — carried from 19/31, named not fetched.
- Spot/commitment-discount infra economics (→ Appendix O cloud-infra). None load-bearing.

## Verdict
32 is honest and ops-appropriate: it introduces NO new load-bearing claim — it prices the 22
quadratic and applies the 24/18/19/20/30 toolkit in dollars, every number RECOMPUTED, every
mechanism cross-linked to a line-verified anchor (capstone-style, like 21). The only residual
`[UNVERIFIED]` are vendor pricing specifics and FinOps tooling, deliberately abstracted to knobs.
Reconcile into `_research.md`. **0 blockers.**
