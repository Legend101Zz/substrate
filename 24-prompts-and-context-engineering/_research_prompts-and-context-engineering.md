# 24 · prompts-and-context-engineering — research brief (full depth)

> Phase-1 research brief (NO course prose; briefs only). 24 refines the **"assemble context"** box
> of the 22 loop. Bespoke structure: context is a **fixed budget that must be engineered** — a
> resource-allocation problem, not a writing problem. Forcing functions (carried in verbatim from
> upstream): 22's input tokens are **O(T²)** (`T*p + g*T*(T-1)/2`, transcript re-sent + grows every
> turn) and 23's **toolbox tax** (K·S tokens every turn). 24 is where those two pressures are
> actively managed. Math: `_recompute.py` (18/18). Primary: Chain-of-Thought (Wei et al., NeurIPS
> 2022, arXiv 2201.11903). Reconciliation: `_research.md`. Factcheck: `_factcheck_phase1.md`.

---

## 0. Scope and the one-sentence thesis
**A prompt is a program written in examples and instructions; context is the runtime memory that
program executes against — and that memory is a hard, fixed-size budget.** "Context engineering" is
the discipline of deciding *what goes in the window, in what form, in what order, and what gets
thrown out* — under the O(T²) and toolbox-tax pressures from 22/23. The skill is **allocation +
compression + placement**, three jobs that map cleanly onto Part I/II primitives (caching 08/16,
sizing 13, eviction 06/08, load-shedding 18).

Two layers (per CONSTITUTION):
- **Intuitive:** the window is a desk. You can only fit so much paper on it; the model only reads
  what is on the desk *right now*; old paper has to be filed or shredded to make room.
- **Mechanism:** the window is a token budget `W`. Every turn the loop re-sends the whole desk
  (22). So every token you leave on the desk is re-billed every turn — context is *rent*, not a
  one-time purchase. Engineering it = minimizing rent while preserving the tokens the next decision
  actually needs.

---

## 1. Prompt anatomy — the parts of the "assemble" box
The assembled context is a **concatenation of tenants competing for one budget**:
1. **System / role instruction** — the standing contract (who the model is, rules, output format).
2. **Tool schemas** — 23's contract surface; K·S tokens, paid every turn (the toolbox tax).
3. **Exemplars (few-shot)** — input→output demonstrations; the CoT primary lives here.
4. **Retrieved knowledge** — RAG chunks (handoff to 30).
5. **Memory** — distilled long-term + working memory (handoff to 25).
6. **Transcript / scratchpad** — the growing Thought/Action/Observation log (22's quadratic source).
7. **The current query / cursor.**
8. **Reserved output space** — *not optional*: the model cannot generate if input fills `W`.

Each tenant is owned downstream: tools→23, retrieved→30, memory→25, transcript→26, output reserve→
22/32. 24's job is the **allocator** that arbitrates between them.

---

## 2. Primary: Chain-of-Thought (what it proves about prompts) — VERIFIED
CoT is the load-bearing primary because it is the cleanest demonstration that **the *form* of the
context, not just its content, changes model capability** — the foundational premise of context
engineering. Verified verbatim from `meta/fetched_primaries/cot-2201.11903.txt`:
- **In-context few-shot learning is the substrate** (lineage Brown et al. 2020): "instead of
  finetuning a separate language model checkpoint for each new task, one can simply 'prompt' the
  model with a few input–output exemplars demonstrating the task." → prompts are *programming by
  example*; this is why "assemble context" is a control surface at all.
- **Format allocates computation:** CoT "allows models to decompose multi-step problems into
  intermediate steps, which means that additional computation can be allocated to problems that
  require more reasoning steps." → emitting reasoning tokens *is* spending compute; the prompt
  decides how much. (This is the open-loop sibling of 22's ReAct: CoT reasons, ReAct adds the
  feedback edge.)
- **Capability can be emergent in the prompt regime:** "chain-of-thought prompting is an emergent
  ability of model scale ... only yields performance gains when used with models of ∼100B
  parameters." → prompting techniques are model-dependent; a brief is not portable across scales.
- **Order/selection of exemplars is load-bearing (the key context-engineering lever):** "varying
  the permutation of few-shot exemplars can cause the accuracy of GPT-3 on SST-2 to range from near
  chance (54.3%) to near state of the art (93.4%)" (citing Zhao et al. 2021). → *the same tokens in
  a different order can swing accuracy ~40 points.* Placement/order is a first-class design
  variable, not cosmetics. (Connects to §6 position budget.)
- **But style is robust:** "successful use of chain of thought does not depend on a particular
  linguistic style" (different annotators all beat baseline). → engineer *structure and selection*,
  do not fuss over prose voice.

Teaching takeaway: CoT licenses the entire sub-course — if format/order can swing capability by
this much, then *engineering the window is engineering the system's behavior.*

---

## 3. The window is a budget (RECOMPUTED §1, §5)
The first and most violated rule: `W = system + tools + memory + retrieved + transcript +
reserve_output`, and **the sum must be < W with output reserved.** The classic bug is filling the
input to `W` and leaving zero room to generate (recompute §1: input=128k → 0 output room → the
model cannot answer). Recomputed example partition: a 128k window with 31.5k of fixed tenants
leaves 96.5k for transcript; retrieved budget of 12k fits ⌊12000/800⌋ = 15 chunks, the rest must be
re-ranked/dropped (handoff to 30). This is **identical to capacity planning (13) and admission
control (18)** applied to tokens: you size tenants, reserve headroom, and shed the overflow.

---

## 4. Few-shot exemplars are a token-cost lever (RECOMPUTED §2)
Exemplars buy accuracy (CoT) but are a **fixed addend to the prefix `p`, paid every turn** (22
re-send). Recomputed: 8 CoT exemplars at 250 tok = 2000 tok added to `p`; over a 20-turn loop
that's 40,000 input tokens just for the demonstrations. So the shot count is a real
accuracy-vs-cost dial, and it *amplifies the quadratic* because it inflates `p`. Design rule:
use the fewest exemplars that hit the accuracy bar; if many are needed, **retrieve** the most
relevant ones per-query (same law as 23's tool-retrieval and 30's RAG) rather than carrying all of
them every turn.

---

## 5. Compaction: converting O(T²) → O(T) (RECOMPUTED §3, §4 — THE HEADLINE)
This is the single most important result in 24. 22 proved cumulative input is `T*p + g*T*(T-1)/2`
= **O(T²)** because the transcript grows unbounded and is re-sent. 24's fix: **cap the transcript
at a ceiling `C`; when it would exceed `C`, summarize older turns down.** Then per-turn prompt ≤
`p + C` (bounded), so cumulative input ≤ `T*(p+C)` = **O(T)**. Recomputed:
- compaction first triggers at turn `t* = C/g + 1 = 17` (before that, no compaction needed — don't
  pay the summarizer early);
- at T=200, uncompacted = 10.35M tok vs compacted-bound = 2.0M tok → **5.2× cheaper**, and the
  gap widens with T (quadratic 3.87× per doubling vs linear 2.0×);
- **compaction ratio** ρ = s/(R·g): summarizing 12 turns (6000 raw tok) into 600 = ρ=0.10 (10×),
  reclaiming 5400 tok *returned to every future turn's prefix*;
- compaction has its **own cost** (an extra summarizer call ≈ raw input + s output) but pays for
  itself when re-send savings over remaining turns exceed the one-time cost (270k ≫ 6k in the
  example).

Compaction strategies (taxonomy, structure-bearing): **truncate** (drop oldest — cheapest, lossy),
**summarize** (LLM-compress old turns — costs a call, keeps gist), **evict by relevance**
(score+drop — reuse 06/08 eviction, e.g. LRU/LFU on context items), **externalize** (write to
memory/files, keep a pointer — handoff to 25/26). This is **cache eviction (08) and load-shedding
(18) applied to the window**: when the working set exceeds capacity, you must drop something; the
art is dropping the least-needed token.

---

## 6. Placement / "lost in the middle" (RECOMPUTED §7)
Fitting in the window is **necessary but not sufficient**. Empirically, content in the *middle* of
a long context is attended to less than content at the *head* or *tail* (Liu et al. 2023,
"Lost in the Middle" — `[UNVERIFIED]`, not fetched). The recomputable, actionable consequence: only
a head+tail band (~25% of `W` in the model used here = 32k of 128k) is high-salience real estate, so
**placement is a second, tighter budget than fitting.** Design rules: put the instruction and the
current query at the edges; put the most relevant retrieved chunk last (recency); never bury the
ask in the middle of a giant dump. This is the same "the order of exemplars swings accuracy
54.3%→93.4%" lesson from CoT (§2), generalized from few-shot order to whole-context layout.

---

## 7. Prefix caching: discount the re-sent prefix (RECOMPUTED §6 — reuse 08/16)
22's quadratic comes from re-sending the prefix every turn. Providers cache the **byte-identical**
prefix at a discount `d` (cached input billed at ~d× full). Recomputed: at d=0.1 the stable prefix
`p` costs (1−d)·p = 1800 tok less per turn. Crucial nuance the recompute proves: **caching helps
the stable prefix but NOT the growing transcript term** — the `(t−1)·g` growth is not byte-stable,
so it's not cacheable; **compaction (§5) is still required.** Design consequence: keep volatile
content (timestamps, fresh tool results) *out of the cacheable prefix* so the prefix stays
byte-stable across turns (cache-stable context design — a direct application of 08/16 cache-key
hygiene to prompt layout).

---

## 8. Robustness & failure modes of the assemble box (motivates 31/33)
- **Prompt injection via retrieved/tool content** — untrusted tokens in the window can hijack the
  instruction (handoff to 33; the result-as-untrusted rule from 23 §3).
- **Instruction drift / dilution** — as the transcript grows, the system instruction's relative
  weight falls; mitigations: re-assert key rules near the tail, or pin them (placement, §6).
- **Context poisoning** — a wrong fact summarized into memory compounds (handoff to 25 hygiene; the
  ReAct grounding cure from 22).
- **Over-compaction** — summaries that drop the token the next step needed (lossy eviction error;
  the "evicted the hot key" failure from 08).
- **Format brittleness** — output-format instructions that the parser (23) can't reliably read;
  prefer structured outputs (23 §3).

---

## 9. Build-your-own (toward the 28 capstone)
Add a **context manager** to the 22/23 loop: a budget allocator (`W` partitioned across tenants
with reserved output), a few-shot block (retrieved, not static), a **compactor** (ceiling `C` +
summarize/evict at `t*`), placement rules (instruction+query at edges), and prefix-cache-stable
layout. Break it on purpose: remove the compactor → watch O(T²) overflow the window at `T*` (the 22
exhaustion turn); bury the query in the middle → watch accuracy drop. Third upgrade in the harness
arc (loop → tools → **context** → memory → subagents → budgets).

---

## 10. Sources & provenance
- **VERIFIED primary:** Chain-of-Thought (Wei et al., NeurIPS 2022, arXiv 2201.11903) —
  `meta/fetched_primaries/cot-2201.11903.{pdf,txt}`; receipt in `_factcheck_phase1.md`.
- **RECOMPUTED:** `_recompute.py` (18/18) — window partition, few-shot cost, **compaction
  O(T²)→O(T)**, compaction ratio/payoff, retrieval fit, prefix-cache discount, placement band.
- **REUSED (line-verified Part I/II):** 06 (eviction structures), 08/16 (caching, eviction,
  cache-key hygiene), 13 (sizing/capacity), 18 (admission/load-shedding), 22 (the quadratic,
  assemble box), 23 (toolbox tax, structured outputs, untrusted results).
- **`[UNVERIFIED]` carry-forward (do NOT harden into prose):**
  - "Lost in the Middle" (Liu et al. 2023, arXiv 2307.03172) — position bias; not fetched.
  - Provider prompt-caching specs (Anthropic prompt caching, OpenAI) — vendor docs, not fetched.
  - Specific compaction/summarization-memory designs (deferred to 25; MemGPT 2310.08560).
  - Prompt-injection taxonomy (deferred to 33).
  - "Context rot" / long-context degradation beyond Liu et al. — community idiom, not primary.
