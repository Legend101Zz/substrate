# 24 — Prompts and Context Engineering · _structure.md

**Identity:** refines the "assemble context" box of the 22 loop — deciding what enters the window, in
what form, in what order, and what gets thrown out. The one idea: **context is rent, not a purchase.**
Because the loop re-sends the whole window every turn, every token you leave in is re-billed every turn.

**Bespoke shape — "context is a fixed budget to be engineered" (a resource-allocation walkthrough).**
NOT prompt-engineering tips. The forcing functions are concrete and inherited: 22's O(T²) input growth
+ 23's toolbox tax K·S. So context engineering is capacity planning (13) + cache eviction (08) +
load-shedding (18), applied to tokens: ALLOCATE the fixed budget W across competing tenants, COMPRESS
what won't fit, PLACE the load-bearing tokens where the model attends. The headline result —
compaction converts O(T²)→O(T) — is the single most important thing in the sub-course. CoT is the
primary (it proves FORM changes capability). Math recomputed (18/18). Third harness upgrade.

## Dependency position
- **Depends on:** 22 (the O(T²) it must tame; the assemble box), 23 (the toolbox tax K·S, a fixed
  prefix addend), 08/16 (cache eviction + prefix caching = cache-key hygiene), 13 (window = a capacity
  budget), 18 (compaction = load-shedding on the window), 06 (retrieval structures preview).
- **Feeds into:** 25 (what the compactor EXTERNALIZES to — the persistent memory tier), 30 (retrieved
  tenant = RAG; retrieve few-shot per query), 26 (transcript tenant = the durable WAL), 32 (cost is the
  bill this controls), 33 (injection via retrieved/tool tokens), 31 (context poisoning shows up in eval).
- **Appendix links DOWN:** N-math (token-budget arithmetic), M-agentic-papers (CoT, Lost-in-the-Middle).
  24 owns the allocator + the compaction result.

## Chapter specs (3–5 lines each)
1. **The one idea: context is rent** — the loop re-sends the whole window every turn (22), so every
   resident token is re-billed every turn. Context engineering = minimize rent while preserving exactly
   the tokens the NEXT decision needs. It is capacity planning + cache eviction + load-shedding on tokens.
2. **CoT proves form changes capability** — the primary, because it shows STRUCTURE and ORDER (not just
   content) swing behavior. VERIFIED: prompts are programming-by-example; format allocates compute
   ("additional computation ... allocated to problems that require more reasoning steps"); permuting
   few-shot exemplars moves GPT-3 on SST-2 54.3%→93.4% (same tokens, different order); emergent at ~100B
   yet style-robust (engineer structure/selection, not voice). CoT = the open-loop sibling of 22's ReAct.
3. **The window is a budget** — `W = system + tools + memory + retrieved + transcript + reserve_output`,
   and the sum must be < W WITH output reserved (the classic bug: fill input to W, leave 0 to generate).
   Each tenant is owned downstream (tools→23, retrieved→30, memory→25, transcript→26, output→22/32); 24
   is the ALLOCATOR arbitrating them.
4. **Lever 1 — few-shot cost** — exemplars buy accuracy (CoT) but are a fixed prefix addend paid every
   turn (8×250=2000 tok ×20 turns = 40k input tok); they AMPLIFY the quadratic. Use the fewest that hit
   the bar; if many are needed, RETRIEVE them per-query (same law as 23 tool-retrieval / 30 RAG).
5. **Lever 2 (HEADLINE) — compaction: O(T²)→O(T)** — cap the transcript at ceiling C and summarize older
   turns → per-turn prompt ≤ p+C → cumulative input ≤ T·(p+C) = O(T). First triggers at `t*=C/g+1=17`;
   at T=200, 10.35M vs 2.0M tok (5.2× cheaper, gap widens with T). Taxonomy: truncate / summarize /
   evict-by-relevance / externalize — cache eviction (08) + load-shedding (18) on the window. Plus
   prefix caching (08/16): providers discount the byte-stable prefix but NOT the growing transcript, so
   compaction is STILL required; keep volatile content out of the prefix.
6. **Placement: fitting ≠ being attended** — "lost in the middle" (UNVERIFIED, Liu 2023): only a
   head+tail band (~25%·W = 32k of 128k) is high-salience. Placement is a SECOND, tighter budget than
   fitting — instruction + current query at the edges, most-relevant chunk last. The CoT exemplar-order
   lesson (54.3%→93.4%) generalized from few-shot order to whole-context layout.
7. **Failure modes** — prompt injection via retrieved/tool tokens (→33) · instruction drift as the
   transcript grows (→re-assert at the tail) · context poisoning by a bad summary (→25 hygiene + ReAct
   grounding) · over-compaction dropping the needed token (the 08 evicted-hot-key error) · format
   brittleness the 23 parser can't read (→structured outputs). All are systems failures of the assemble box.

## Paired build lab (/build → context-manager stage of own-coding-agent-harness, 28)
Add a context manager to the 22/23 loop: budget allocator (W partitioned, output reserved) + retrieved
few-shot block + compactor (ceiling C, summarize at t*) + edge-placement rules + cache-stable layout.
Break it: drop the compactor → overflow at the 22 exhaustion turn; bury the query → accuracy drops.
Third harness upgrade (loop → tools → context → …).

## Diagrams needed
- "Context is rent": the window re-sent every turn, each token re-billed.
- CoT exemplar-order swing (54.3%→93.4%, same tokens) — form changes capability.
- The window budget partitioned across tenants, with output reserved (and the fill-to-W bug).
- Few-shot as a fixed prefix addend amplifying the O(T²) curve.
- Compaction converting O(T²)→O(T) (the two curves diverging with T); compaction taxonomy.
- Prefix caching discounting the stable prefix but NOT the growing transcript.
- Placement salience band (head+tail high, middle low) — fitting vs attending.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED primary:** Chain-of-Thought (arXiv 2201.11903; `meta/fetched_primaries/cot-2201.11903.*`,
  receipt `_VERIFIED_2026-06-10_agentic.md`) — programming-by-example, format-allocates-compute,
  54.3%→93.4% order swing, emergent-at-~100B, style-robust.
- **RECOMPUTED (18/18):** budget partition, few-shot cost, compaction O(T²)→O(T), ratio/payoff,
  retrieval fit, prefix-cache discount, placement band.
- **`[UNVERIFIED]` carry-forward (none load-bearing for the allocation/compaction model):**
  Lost-in-the-Middle (arXiv 2307.03172); provider prompt-caching specs; MemGPT/summarization-memory
  designs (→25); prompt-injection taxonomy (→33); "context rot" idiom. Teach the model now; do NOT
  harden the placement-band exact percentages or vendor caching specifics until fetched.
- **Boundary discipline:** the persistent tier the compactor externalizes to → 25; retrieved tenant →
  30; transcript durability → 26; cost → 32; injection → 33; cache mechanics → 08/16; token arithmetic
  → appendix N. 24 owns ONLY the allocator + compaction + placement.
