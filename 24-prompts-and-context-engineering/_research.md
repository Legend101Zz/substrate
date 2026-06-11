# 24 · prompts-and-context-engineering — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 24 refines the **"assemble context"** box
> of the 22 loop: deciding *what enters the window, in what form, in what order, and what gets
> thrown out.* Bespoke structure: context is a **fixed budget to be engineered** (a
> resource-allocation problem). Forcing functions: 22's **O(T²)** input growth + 23's **toolbox
> tax** K·S. Full depth: `_research_prompts-and-context-engineering.md`. Math: `_recompute.py`
> (18/18). Primary: Chain-of-Thought (Wei et al., NeurIPS 2022). Factcheck: `_factcheck_phase1.md`
> (0 blockers).

## 1. The one idea
**Context is rent, not a purchase.** Because the loop re-sends the whole window every turn (22),
every token you leave in the window is re-billed every turn. So context engineering is the
discipline of minimizing rent while preserving exactly the tokens the *next* decision needs:
**allocate** the fixed budget `W` across competing tenants, **compress** what won't fit, **place**
the load-bearing tokens where the model will actually attend. It is capacity planning (13), cache
eviction (08), and load-shedding (18) — applied to tokens.

## 2. Primary: CoT proves *form changes capability* (VERIFIED)
CoT is the anchor because it shows the *structure and order* of context — not just its content —
swing model behavior, which is the entire premise of the sub-course. VERIFIED verbatim: prompts are
**programming-by-example** ("simply 'prompt' ... with a few input–output exemplars"); **format
allocates compute** ("additional computation can be allocated to problems that require more
reasoning steps"); the swing is huge — permuting few-shot exemplars moves GPT-3 on SST-2 from
**54.3% → 93.4%** (same tokens, different order); it's **emergent at ∼100B** (techniques are
model-dependent) yet **style-robust** (engineer structure/selection, not voice). CoT is the
open-loop sibling of 22's ReAct: reasoning in the prompt vs reasoning + a feedback edge.

## 3. The window is a budget (RECOMPUTED)
`W = system + tools + memory + retrieved + transcript + reserve_output`, and the sum must be < `W`
**with output reserved** — the classic bug is filling input to `W` and leaving 0 room to generate.
Recomputed: a 128k window with 31.5k fixed tenants leaves 96.5k for transcript; a 12k retrieved
budget fits 15 chunks of 800, rest dropped (→30). Each tenant is owned downstream (tools→23,
retrieved→30, memory→25, transcript→26, output→22/32); 24 is the **allocator** arbitrating them.

## 4. Two levers and one headline
- **Few-shot cost (lever, RECOMPUTED):** exemplars buy accuracy (CoT) but are a fixed prefix addend
  paid every turn — 8×250=2000 tok, ×20 turns = 40k input tok. They *amplify the quadratic*. Use
  the fewest that hit the bar; if many are needed, **retrieve** them per-query (same law as 23
  tool-retrieval / 30 RAG).
- **Compaction (HEADLINE, RECOMPUTED):** cap the transcript at ceiling `C` and summarize older
  turns → per-turn prompt ≤ `p+C` → cumulative input ≤ `T*(p+C)` = **O(T)**. This converts 22's
  **O(T²) → O(T)** — the most important result in 24. First triggers at `t*=C/g+1=17`; at T=200,
  10.35M vs 2.0M tok (5.2× cheaper, gap widens with T). Compaction ratio ρ=s/(R·g)=0.10 reclaims
  5400 tok returned to *every future turn*; it has its own summarizer cost but pays off when
  re-send savings ≫ that one-time cost. Taxonomy: **truncate / summarize / evict-by-relevance /
  externalize** — i.e. cache eviction (08) + load-shedding (18) on the window.
- **Prefix caching (RECOMPUTED, reuse 08/16):** providers discount the byte-stable prefix by (1−d);
  but it does NOT touch the growing transcript term, so **compaction is still required.** Keep
  volatile content out of the prefix (cache-stable layout = 08 cache-key hygiene).

## 5. Placement: fitting ≠ being attended (RECOMPUTED)
"Lost in the middle" (`[UNVERIFIED]`, Liu et al. 2023): only a head+tail band (~25%·W = 32k of
128k) is high-salience. So **placement is a second, tighter budget than fitting** — instruction +
current query at the edges, most-relevant chunk last. This is the CoT exemplar-order lesson
(54.3%→93.4%) generalized from few-shot order to whole-context layout.

## 6. Failure modes (motivate 25/31/33)
Prompt injection via retrieved/tool tokens (→33) · instruction drift as transcript grows (→re-assert
at tail, §5) · context poisoning by a bad summary (→25 hygiene + 22 ReAct grounding) ·
over-compaction dropping the needed token (→the 08 "evicted hot key" error) · format brittleness
the 23 parser can't read (→structured outputs). **All are systems failures of the assemble box,
not model failures.**

## 7. Build-your-own
Add a **context manager** to the 22/23 loop: budget allocator (`W` partitioned, output reserved) +
retrieved few-shot block + **compactor** (ceiling `C`, summarize at `t*`) + edge-placement rules +
cache-stable layout. Break it: drop the compactor → overflow at the 22 exhaustion turn; bury the
query → accuracy drops. Third harness upgrade (loop → tools → **context** → memory → subagents →
budgets).

## 8. Provenance summary
- **VERIFIED primary:** Chain-of-Thought (arXiv 2201.11903) —
  `meta/fetched_primaries/cot-2201.11903.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_agentic.md`.
- **RECOMPUTED:** `_recompute.py` (18/18) — budget, few-shot cost, compaction O(T²)→O(T), ratio/
  payoff, retrieval fit, prefix-cache discount, placement band.
- **REUSED:** 06, 08/16, 13, 18, 22, 23.
- **`[UNVERIFIED]` carry-forward:** Lost-in-the-Middle (arXiv 2307.03172); provider prompt-caching
  specs; MemGPT/summarization-memory designs (→25); prompt-injection taxonomy (→33); "context rot"
  idiom. None load-bearing for the allocation/compaction model.

---
**24 reconciled.** Next in dependency order: **25-memory-short-term-long-term-and-safety** (what
24's compactor *externalizes to* — working vs long-term memory; ↔ 08/16 caching + 06 structures +
22 quadratic; primaries MemGPT arXiv 2310.08560 + Reflexion arXiv 2303.11366).
