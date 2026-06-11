# 24 · Phase-1 factcheck — prompts-and-context-engineering

> Method (same discipline as 13-23): every load-bearing claim is either (a) RECOMPUTED in
> `_recompute.py` (18/18 pass), (b) VERIFIED verbatim against a primary fetched to
> `meta/fetched_primaries/`, (c) REUSED from a previously line-verified Part I/II sub-course, or
> (d) flagged `[UNVERIFIED]` and carried forward (must not harden into Phase-2 prose). 0 blockers.

## Bespoke structure note
Per the Part III plan: 24 refines the **"assemble context"** box of the 22 loop. Its single brief
is therefore organized as a **budget/allocation walkthrough** (anatomy → CoT primary → budget →
exemplar cost → compaction → placement → caching → failures), NOT abstract source clusters and NOT
the 13-20 four-cluster shape. Plan-sanctioned departure, consistent with 22/23.

## Primary fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022 (arXiv 2201.11903) | `cot-2201.11903.{pdf,txt}` (43 pp) | §2: prompts are programming-by-example; format allocates compute; exemplar ORDER swings accuracy; emergent at ∼100B; style-robust |

Fetch method: `curl https://arxiv.org/pdf/2201.11903`; text via throwaway `/tmp/pdfx-venv`
(uv + pypdf), `.code-puppy-venv` untouched. Receipt appended to
`meta/fetched_primaries/_VERIFIED_2026-06-10_agentic.md` (Wave 11 cont'd).

### Verified claims (Chain-of-Thought)
- "instead of finetuning a separate language model checkpoint for each new task, one can simply
  'prompt' the model with a few input–output exemplars demonstrating the task" — VERIFIED verbatim
  (Intro, l.93-96). Anchors: prompts = programming by example (§1, §2).
- "[chain of thought] allows models to decompose multi-step problems into intermediate steps, which
  means that additional computation can be allocated to problems that require more reasoning steps"
  — VERIFIED verbatim (Intro property 1). Anchors: format allocates compute (§2).
- "chain-of-thought prompting is an emergent ability of model scale ... only yields performance
  gains when used with models of ∼100B parameters" — VERIFIED verbatim (§3, l.273-276). Anchors:
  prompt techniques are model-dependent (§2).
- "varying the permutation of few-shot exemplars can cause the accuracy of GPT-3 on SST-2 to range
  from near chance (54.3%) to near state of the art (93.4%)" — VERIFIED verbatim (§ robustness,
  l.431-434, citing Zhao et al. 2021). Anchors: ORDER/placement is load-bearing (§2, §6). **The
  single most important context-engineering citation: same tokens, different order, ~40pt swing.**
- "successful use of chain of thought does not depend on a particular linguistic style" — VERIFIED
  verbatim (§ robustness). Anchors: engineer structure/selection, not prose voice (§2).

## Recomputed claims (`_recompute.py`, 18/18)
- Window partition is a budget; sum < W with output reserved; naive fill-to-W → 0 output room. PASS.
- Few-shot exemplar cost = n·e, a fixed prefix addend paid every turn (8·250=2000; ×20 turns=40k).
  PASS. Amplifies the 22 quadratic.
- **Compaction converts O(T²)→O(T)** (cap transcript at C, summarize): uncompacted T=20=135k;
  first trigger at t*=C/g+1=17; at T=200, 10.35M vs 2.0M (5.2× cheaper); quad 3.87×/doubling vs
  lin 2.0×. PASS. **Headline.**
- Compaction ratio ρ=s/(R·g)=0.10 (10×), reclaims 5400 tok; pays off when re-send savings
  (270k) ≫ one-time summarizer cost (6k). PASS.
- Retrieval fit: ⌊12000/800⌋=15 chunks; rest dropped (→30). PASS.
- Prefix caching discounts stable prefix by (1−d) (saved 1800 tok at d=0.1) but does NOT touch the
  growing transcript term → compaction still required. PASS.
- Placement: high-salience head+tail band ≈25%·W=32k of 128k → fitting ≠ being attended; placement
  is a second, tighter budget. PASS.

## Reused (line-verified Part I/II) — mechanisms, not re-derived
- 06 eviction structures (LRU/LFU) → context-item eviction (§5).
- 08/16 caching, eviction, cache-key hygiene → compaction = window eviction (§5); prefix caching
  = stable-key design (§7).
- 13 sizing/capacity → the window-as-budget partition (§3).
- 18 admission control / load-shedding → "shed the overflow chunks/turns" (§3, §5).
- 22 the quadratic (`T*p + g*T*(T-1)/2`), the assemble box, exhaustion turn T* → the entire forcing
  function (§5).
- 23 toolbox tax K·S, structured outputs, untrusted results → tools tenant (§1, §3), format
  brittleness + injection (§8).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- "Lost in the Middle" (Liu et al. 2023, arXiv 2307.03172) — the position-bias empirical basis for
  §6; modeled here as a recomputable salience band, but the empirical curve itself is NOT fetched.
- Provider prompt-caching specs (Anthropic prompt caching, OpenAI cached input pricing) — the d
  discount in §7 is illustrative; vendor docs not fetched.
- MemGPT-style summarization memory + specific compaction designs — deferred to 25 (arXiv 2310.08560).
- Prompt-injection taxonomy / defenses — deferred to 33.
- "Context rot"/long-context degradation as a general phenomenon — community idiom, not primary.

## Verdict
24 is honest and box-appropriate: the foundational premise (format/order of context changes
capability) is VERIFIED against CoT — including the load-bearing exemplar-order swing
(54.3%→93.4%); the economics (window budget, few-shot cost, **compaction O(T²)→O(T)**, compaction
ratio/payoff, prefix-cache discount, placement band) are RECOMPUTED; the mechanisms (eviction,
caching, sizing, shedding, the quadratic, toolbox tax) are REUSED from line-verified 06/08/13/18/22/23.
Residual `[UNVERIFIED]` are adjacent empirical papers + vendor docs, none load-bearing for the
allocation/compaction model. Reconcile into `_research.md`.
