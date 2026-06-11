# 32 · cost-observability-and-ops — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 32 takes **22's O(T²) token economics and
> makes it OPERATIONAL**: token/$ accounting, budgets, caching ROI, per-tenant quotas, cost
> dashboards, and day-2 ops for a fleet of agents. Bespoke structure: a **cost-lifecycle
> walkthrough** (Account → Attribute → Budget/Cap → Optimize → Operate), NOT four clusters.
> NO new load-bearing primary — like 21, it APPLIES already-verified mechanisms (22 loop economics,
> 24 caching/compaction, 18 admission control, 19 observability, 20 tail, 30 retrieval, 31 eval
> cost). Math: `_recompute.py` (14/14). Factcheck: `_factcheck_phase1.md` (0 blockers).

## 1. The one idea (RECOMPUTED, no new primary)
**An agent's bill is the 22 quadratic, priced.** Because the transcript is re-sent and grows by ~g
tokens/turn, input cost is **O(T²)** (RECOMPUTED: T=20 costs >2× T=10; the input/quadratic term
dominates the bill at high T). So cost is not a flat per-call number — it is a *function of loop
depth*, and the levers that bound it are the levers from 24/18/20 re-priced in dollars. There is no
new physics here; 32 is the *operations* discipline (19 for services) applied to *token spend*.

## 2. The cost lifecycle, walked (the bespoke spine)
- **Account (22):** $ = in·P_in + out·P_out; in = T·p + g·T(T-1)/2 (the 22 transcript growth);
  input (cheap/token) usually dominates because it's quadratic, output is linear. Attack the
  transcript, not the replies.
- **Attribute (19/31):** cost is just another **signal** — annotate every 31/19 span with
  tokens-in/out·price → attribute $ per (model, tenant, tool, feature, run). Unattributed spend is
  un-optimizable (the 19 cardinality lesson); the cost dashboard is the 19 metrics pipeline over $.
- **Budget/Cap (22/18/20):** per-run **turn/token caps** (22 budgets) collapse the **cost tail**
  (RECOMPUTED: one 100-turn runaway run drags the mean to 20× the median; capping at T≤20 cuts the
  total 10×). Per-tenant **quotas** = the 18 token-bucket/admission-control identity over dollars
  (fair-share pool/N; shed the runaway tenant at its cap → bounded blast radius, 18/20).
- **Optimize (24/30):** **compaction** (24) converts O(T²)→O(T) → a dollar saving that GROWS with
  T (RECOMPUTED: T=100 input 7.8M→1.5M tok, saves ~$18.8/run). **Prefix/prompt caching** (24
  discount) makes the *static* prefix ~10× cheaper on hits but **does NOT touch the quadratic
  transcript** (caching ≠ compaction). **Retrieval** (30) beats stuffing (send K relevant chunks,
  not the corpus). **Model routing** = a cheap model for easy turns, dear for hard (RECOMPUTED:
  70/30 mix → blended $1.04/M vs $3/M).
- **Operate (19/20/26):** day-2 ops for an agent fleet — cost SLOs + burn-rate alerts (19) over $;
  p99-cost alerting (20 tail); rate-limit/quota dashboards (18); resume/idempotency so a crash
  doesn't re-bill work (26); capacity planning (20) in tokens/sec and $/day.

## 3. The economics (RECOMPUTED — headlines, `_recompute.py` 14/14)
Cost is O(T²) (doubling turns >2× the bill; input term dominates) · compaction O(T²)→O(T) saves
~$18.8/run at T=100 and the saving grows unbounded with T · prefix cache 10× cheaper prefix on hits
but leaves the 1.84M-token quadratic transcript uncached · per-tenant fair-share cap = pool/N,
runaway tenant shed at cap (18 over $) · cost tail: mean 20× median, per-run cap cuts total 10×
(20 tail + 22 budget) · cost is an attributable signal (LLM = 80% of the bill → optimize the
biggest tag, 19) · model routing 70/30 → blended $1.04/M vs $3/M.

## 4. Where 32 sits
32 is **19 observability + 18 control + 20 capacity, denominated in dollars/tokens** instead of
latency/availability, sitting on top of **22's** quadratic. It consumes 31's traces (the spans that
carry token counts) and prices the levers already proven in 24 (compaction/caching), 30 (retrieval),
18 (quotas/shedding), 22 (turn caps). It feeds 34 (the design canvas budgets every component).
The 31↔32 pair is the agentic **observability** twins: 31 = "is it correct?", 32 = "what does
correct cost, and can we afford it at scale?"

## 5. Failure modes (cost/ops-specific)
Unbounded loop (no turn cap → O(T²) runaway → 20 tail dominates the bill) · unattributed spend
(can't optimize what you can't see, 19) · caching mistaken for compaction (prefix cache leaves the
quadratic, 24) · no per-tenant quota (one tenant starves/bankrupts the pool, 18) · over-eager
expensive model on easy turns (no routing) · eval cost blowout (31 full O(T²) suites per commit) ·
crash re-billing (no idempotent resume, 26) · cost-SLO blindness (no burn-rate alert on $, 19/20).

## 6. Build-your-own
Tenth harness upgrade (after 31 trust): a **cost meter** on the 28 harness. Tag each turn/tool
span (31/19) with tokens·price; print a per-run $ breakdown by (model, tool); enforce a per-run
token/turn cap (22) and a per-session budget (18 bucket over $); flip compaction (24) on/off and
watch $ go O(T²)→O(T); flip prefix caching on and watch ONLY the prefix get cheaper; route easy
turns to a cheap model; alert when a run's burn rate exceeds budget (19/20 over $).

## 7. Provenance summary
- **NO new primary** (operational synthesis, like 21's capstone). Every mechanism cross-links to a
  line-verified anchor: 22 (loop O(T²) cost), 24 (compaction/prefix-cache, both VERIFIED via CoT +
  recomputed in 24), 18 (token-bucket/admission/load-shedding, VERIFIED via RFC 6585 + SRE), 19
  (Dapper spans + metrics/cardinality + SLO/burn-rate, VERIFIED), 20 (tail + capacity, VERIFIED via
  Tail-at-Scale), 30 (retrieve-vs-stuff), 31 (eval cost + trace spans carry tokens), 26 (idempotent
  resume so crashes don't re-bill).
- **RECOMPUTED:** `_recompute.py` (14/14) — token/$ over 22's O(T²); compaction $ saving; prefix-
  cache ROI + its limit; per-tenant quota (18 over $); cost tail (20) + per-run cap; attributable
  cost signal (19); model routing.
- **REUSED:** 18, 19, 20, 22, 24, 26, 30, 31.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** provider pricing/prompt-caching/batch-API
  specifics (vendor docs, deliberately illustrative knobs here); FinOps frameworks; concrete
  cost-observability tooling (Helicone/Langfuse/OpenTelemetry GenAI cost conventions — carried from
  19/31); spot/commit-discount infra economics (→Appendix O). None load-bearing for the model.

---
**32 reconciled.** Part III "Phase 1 batch 3" now stands at **22-32 reconciled** (11 of 13 agentic
sub-courses). Next in dependency order: **33-safety-and-proactive-self-evolving-agents** (prompt-
injection via tool-result/memory/retrieved-passage carried from 23/25/29/30; sandboxing/ACE;
self-improvement loops Reflexion 25; alignment/oversight), then **34-design-your-own-agentic-system**
(the Part III CAPSTONE DESIGN CANVAS, applying all of 22-33 the way 21 applied 13-20).
