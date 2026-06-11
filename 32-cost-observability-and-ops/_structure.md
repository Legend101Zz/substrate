# 32 — Cost, Observability & Ops · _structure.md

**Identity:** the chapter that takes **22's O(T²) token economics and makes it OPERATIONAL** —
token/$ accounting, budgets and caps, caching ROI, per-tenant quotas, cost dashboards, and day-2 ops
for a fleet of agents. There is no new physics here: 32 is the *operations* discipline (19 for
services) re-aimed at *token spend*. It is the cost-twin of 31: 31 asks "is it correct?", 32 asks
"what does correct cost, and can we afford it at scale?"

**Bespoke shape — "a cost-lifecycle walkthrough: ACCOUNT → ATTRIBUTE → BUDGET/CAP → OPTIMIZE →
OPERATE."** NOT four clusters. The thesis (RECOMPUTED, no new primary): **an agent's bill IS the 22
quadratic, priced.** Because the transcript is re-sent and grows ~g tokens/turn, input cost is
O(T²); cost is therefore a *function of loop depth*, not a flat per-call number, and every lever that
bounds it is a lever from 24/18/20/30 re-denominated in dollars. Like 21, 32 APPLIES already-verified
mechanisms — NO new load-bearing primary. Math recomputed (14/14). The `/build` deliverable: a cost
meter on the 28 harness — the tenth harness upgrade.

## Dependency position
- **Depends on:** 22 (the O(T²) loop economics — the master constraint) + 24 (compaction O(T²)→O(T);
  prefix/prompt caching) + 18 (token-bucket/admission control → per-tenant quotas; load-shedding) +
  19 (observability: cost is just another signal; cardinality; SLO/burn-rate) + 20 (the cost tail;
  capacity planning) + 30 (retrieve-vs-stuff is a cost lever) + 31 (eval cost; traces carry token
  counts) + 26 (idempotent resume so a crash doesn't re-bill work) + 28 (the harness metered).
- **Feeds into:** 33 (a runaway/abusive agent is a cost-availability attack; gating has a price) + 34
  ("price the whole design; budget every cross-cut" — 32 supplies the $ column of the ledger). The
  31↔32↔33 triad is the agentic trust set: correct? / affordable? / attackable+improvable?
- **Appendix links DOWN:** O-cloud-infra (spot/commit-discount infra economics; the rented compute
  plane the tokens run on) · G-redis (the prefix/result cache tier) · N-math (the O(T²) cost
  arithmetic, tail statistics). 32 owns the cost discipline; the underlying mechanisms stay in their
  home chapters (compaction in 24, quotas in 18, tracing in 19, tail in 20).

## Section specs (3–5 lines each)
1. **The one idea: the bill IS the quadratic, priced (RECOMPUTED)** — input cost = T·p + g·T(T-1)/2,
   so doubling turns more than doubles the bill (T=20 costs >2× T=10) and the quadratic input term
   dominates at high T. Cost is not a flat per-call number; it is a function of loop depth. Therefore:
   **attack the transcript, not the replies.** No new physics — 32 is operations applied to spend.
2. **Account (22)** — $ = in·P_in + out·P_out where in = T·p + g·T(T-1)/2 (the 22 transcript growth).
   Input (cheap per token) usually dominates the bill *because it's quadratic*; output is linear. Show
   the learner exactly which term to attack and why caching the static prefix is necessary but not
   sufficient.
3. **Attribute (19/31)** — cost is just another **signal**: annotate every 31/19 span with
   tokens-in/out·price → attribute $ per (model, tenant, tool, feature, run). Unattributed spend is
   un-optimizable (the 19 cardinality lesson); the cost dashboard is the 19 metrics pipeline over
   dollars. RECOMPUTED: LLM ≈ 80% of the bill → optimize the biggest tag first.
4. **Budget/Cap (22/18/20)** — per-run **turn/token caps** (22 budgets) collapse the **cost tail**
   (RECOMPUTED: one 100-turn runaway drags the mean to 20× the median; capping at T≤20 cuts the total
   10×). Per-tenant **quotas** = the 18 token-bucket/admission identity over dollars (fair-share
   pool/N; shed the runaway tenant at its cap → bounded blast radius, 18/20).
5. **Optimize (24/30)** — **compaction** (24) turns O(T²)→O(T): a dollar saving that GROWS with T
   (RECOMPUTED: T=100 input 7.8M→1.5M tok, ~$18.8/run saved). **Prefix/prompt caching** (24 discount)
   makes the *static* prefix ~10× cheaper on hits but **does NOT touch the quadratic transcript**
   (caching ≠ compaction — the key distinction). **Retrieval** (30) beats stuffing. **Model routing**:
   cheap model for easy turns, dear for hard (RECOMPUTED: 70/30 mix → blended $1.04/M vs $3/M).
6. **Operate (19/20/26)** — day-2 ops for an agent fleet: cost SLOs + burn-rate alerts (19) over $;
   p99-cost alerting (20 tail); rate-limit/quota dashboards (18); resume/idempotency so a crash
   doesn't re-bill work (26); capacity planning (20) in tokens/sec and $/day.
7. **Where 32 sits + failure modes** — 32 = 19 observability + 18 control + 20 capacity, denominated
   in dollars/tokens, on top of 22's quadratic. Failures: unbounded loop (no turn cap → O(T²) runaway,
   20 tail dominates the bill) · unattributed spend (19) · caching mistaken for compaction (24) · no
   per-tenant quota (one tenant bankrupts the pool, 18) · expensive model on easy turns (no routing) ·
   eval cost blowout (31 full O(T²) suites per commit) · crash re-billing (no idempotent resume, 26) ·
   cost-SLO blindness (no burn-rate alert, 19/20).

## The economics (RECOMPUTED — `_recompute.py` 14/14)
Cost is O(T²) (doubling turns >2× the bill; input term dominates) · compaction O(T²)→O(T) saves
~$18.8/run at T=100, saving grows unbounded with T · prefix cache 10× cheaper prefix on hits but
leaves the 1.84M-token quadratic transcript uncached · per-tenant fair-share cap = pool/N, runaway
shed at cap (18 over $) · cost tail: mean 20× median, per-run cap cuts total 10× (20 + 22) · cost is
an attributable signal (LLM ≈ 80% of bill → optimize the biggest tag, 19) · model routing 70/30 →
blended $1.04/M vs $3/M.

## Paired build lab (/build → own-coding-agent-harness, tenth upgrade)
Add a **cost meter** to the 28 harness: tag each turn/tool span (31/19) with tokens·price; print a
per-run $ breakdown by (model, tool); enforce a per-run token/turn cap (22) and a per-session budget
(18 bucket over $). Acceptance = DEMONSTRATE THE LEVER: flip compaction (24) on/off and watch $ go
O(T²)→O(T); flip prefix caching on and watch ONLY the prefix get cheaper (proving caching ≠
compaction); route easy turns to a cheap model; alert when a run's burn rate exceeds budget (19/20).

## Diagrams needed
- The cost lifecycle: account → attribute → budget/cap → optimize → operate (the bespoke spine).
- The bill decomposition: linear output vs quadratic input transcript (which term to attack).
- The cost dashboard as the 19 metrics pipeline over $ (attribution by model/tenant/tool/feature).
- The cost tail: runaway run drags mean to 20× median; per-run cap cuts total 10× (20/22).
- Compaction vs prefix-caching: O(T²)→O(T) saving vs a discounted-but-still-quadratic prefix.
- Per-tenant fair-share quota = pool/N with the runaway tenant shed at its cap (18).
- Model-routing mix → blended $/M (70/30 → $1.04/M vs $3/M).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **NO new primary** (operational synthesis, like 21). Every mechanism cross-links to a line-verified
  anchor: 22 (loop O(T²) cost, ReAct), 24 (compaction/prefix-cache — VERIFIED via CoT + recomputed in
  24), 18 (token-bucket/admission/load-shedding — VERIFIED via RFC 6585 + SRE), 19 (Dapper spans +
  cardinality + SLO/burn-rate), 20 (tail + capacity — VERIFIED via Tail-at-Scale), 30 (retrieve-vs-
  stuff), 31 (eval cost + spans carry tokens), 26 (idempotent resume so crashes don't re-bill).
- **RECOMPUTED:** `_recompute.py` (14/14) — token/$ over O(T²); compaction $ saving; prefix-cache ROI
  + its limit; per-tenant quota (18 over $); cost tail (20) + per-run cap; attributable signal (19);
  model routing.
- **REUSED:** 18, 19, 20, 22, 24, 26, 30, 31.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** provider pricing / prompt-caching / batch-API
  specifics (vendor docs — deliberately illustrative knobs here, NOT load-bearing); FinOps frameworks;
  concrete cost-observability tooling (Helicone/Langfuse/OpenTelemetry GenAI cost conventions —
  carried from 19/31); spot/commit-discount infra economics (→Appendix O).
- **Boundary discipline:** compaction depth stays in 24, quotas in 18, tracing in 19, tail/capacity in
  20, retrieval in 30, eval cost in 31, infra economics in appendix O. 32 owns ONLY the cost
  discipline (the "bill = quadratic, priced" thesis + the five-stage lifecycle).
