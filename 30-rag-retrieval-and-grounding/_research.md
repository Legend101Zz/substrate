# 30 · rag-retrieval-and-grounding — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 30 is the **retrieval mechanism for 25's
> non-parametric memory tier**: how the agent pulls the *right* facts from a corpus far bigger than
> any window into context at query time. Bespoke structure: a retrieval-pipeline walkthrough.
> Primary: **RAG (Lewis et al. 2020, arXiv 2005.11401) FETCHED+VERIFIED**. Full depth:
> `_research_rag-retrieval-and-grounding.md`. Math: `_recompute.py` (15/15). Factcheck:
> `_factcheck_phase1.md` (0 blockers).

## 1. The one idea (VERIFIED)
**Two memories, not one.** VERIFIED (RAG): models "combine pre-trained parametric and non-parametric
memory" — parametric = the model's weights (frozen, stale, hallucination-prone); non-parametric = an
external corpus you can **revise, expand, inspect** at query time *without retraining*, stored as "a
dense vector index ... accessed with a pre-trained neural retriever." **Grounding** = anchoring
output in retrieved, citable evidence instead of in weights. VERIFIED, it buys exactly the three
gaps the paper names: **updatable knowledge** (edit corpus, not weights), **provenance** (cite the
passage), **less hallucination** ("more specific, diverse and factual" than parametric-only).

## 2. The pipeline, walked (the bespoke spine)
- **Corpus → chunks (14/06):** split into retrievable passages; chunk size is a 14 partition
  tradeoff (too big = budget waste + dilution; too small = lost context).
- **Chunk → embedding (new primitive):** a **bi-encoder** (VERIFIED: RAG retriever "is based on
  DPR", BERT bi-encoder) maps text → a dense vector. Mental model from 06: a *similarity-preserving*
  fingerprint — like a hash, but "near = semantically similar" instead of "equal = identical."
- **Embeddings → vector index (06 ANN):** VERIFIED "MIPS index using FAISS with a Hierarchical
  Navigable Small World" — an Approximate Nearest Neighbor index; MIPS "solved in sub-linear time."
  The 06 lesson exactly: the right structure turns an O(N) scan into ~O(log N) lookup.
- **Query → top-K (08 read path):** embed query with same encoder → ANN top-K nearest chunks.
  Optional cross-encoder rerank over candidates (08 two-tier: cheap broad → precise narrow).
- **Inject + ground (24/25):** place passages in the window (24 allocation/placement), instruct
  "answer only from these and cite them." VERIFIED, RAG marginalizes the doc as a latent variable
  (RAG-Sequence vs RAG-Token); the agent analogue is the prompt-time stuff-top-K pattern.

## 3. The economics (RECOMPUTED — the headlines)
- **Why ANN not scan:** brute force O(N) vs HNSW/MIPS ~O(log N); 10M chunks → ~23 ops, **~430,000×
  fewer** comparisons (the 06 structure payoff, matches VERIFIED "sub-linear").
- **Retrieve top-K beats stuffing the corpus (24 budget):** a corpus dwarfs any window; you can only
  afford `K·c ≤ W-(p+(t-1)g)` (K_max≈248). Retrieval picks the *relevant* K — the 23 retrieval-over-
  tools break-even, now over documents.
- **K is a precision/recall/cost knob:** recall = 1-(1-r)^K (diminishing); cost = K·c (linear) →
  finite optimal K; beyond saturation (K~10 here) extra chunks are **distractors** (24 lost-in-the-
  middle). Don't max K blindly.
- **Caching (08/16):** embeddings deterministic per (model, chunk) → cache (re-index only *changed*
  chunks: 1M→1k, 1000× less). Results cacheable per (query, index-version) with TTL/invalidation.
- **Staleness (15/16):** the index is a **replica** of the corpus → re-index lag = staleness window;
  **grounding is only as fresh as the index** (edited fact invisible until re-embedded).

## 4. Where 30 sits (grounding ⊂ memory ⊂ context)
30 is the retrieval mechanism for 25's non-parametric tier (25 "externalize to a store"; 30 "make it
a vector index + a semantic top-K retriever"); retrieved chunks flow through 24 into the 22 loop;
RAG-as-a-tool is a 23 contract / 29 MCP **resource** (`search_corpus`). 30 unifies the data-systems
toolkit (06+14+08+16) with context/memory (24+25) and the loop (22).

## 5. Failure modes (data-system failures + one new one)
Recall miss (relevant chunk not retrieved → ungrounded → hallucinate) · precision miss (top-K
distractors → 24 dilution) · bad chunk size (14) · **stale index** (15/16 lag) · embedding-model
drift (re-embed whole corpus — expensive) · **corpus poisoning / injection-via-retrieved-passage**
(33 + 25 poisoning blast radius over a *shared* corpus; never trust retrieved text as commands) ·
provenance mismatch (cited passage doesn't support the claim → 31 faithfulness eval). **All but
injection are 06/14/08/15/16 problems.**

## 6. Build-your-own
Add a `search_corpus` tool (23) to the 28 harness: chunk (14) → embed (bi-encoder) → ANN index (06
HNSW) → per relevant turn: embed query, MIPS top-K, inject + "cite sources" (24/25). Cache
embeddings (08) + results (16). Break it: query an edited-but-not-reindexed doc → stale (16); set K
too high → dilution + cost (24); plant a poisoned doc → it hijacks the answer (33). Eighth harness
upgrade (loop→tools→context→memory→persistence→orchestration→connectors→**grounding**).

## 7. Provenance summary
- **PRIMARY (FETCHED+VERIFIED):** RAG (Lewis et al. 2020, arXiv 2005.11401) —
  `meta/fetched_primaries/rag-2005.11401.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_rag.md`.
- **RECOMPUTED:** `_recompute.py` (15/15) — ANN-vs-scan, retrieve-vs-stuff budget, K knob,
  embedding cache, index staleness.
- **REUSED:** 06, 07, 08, 14, 15, 16, 22, 23, 24, 25, 28, 29.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** DPR (arXiv 2004.04906); FAISS + HNSW
  (Malkov & Yashunin 2016) primaries; BM25/sparse + hybrid retrieval; cross-encoder reranking;
  chunking strategies; embedding-model specifics; RAG eval (RAGAS → 31); long-context-vs-RAG;
  GraphRAG/agentic-RAG; injection-via-retrieved-passage mitigations (→33).

---
**30 reconciled.** Part III "Phase 1 batch 3" now stands at **22-30 reconciled** (9 of 13 agentic
sub-courses). Next in dependency order: **31-evaluation-tracing-and-guardrails** (↔ 19 observability/
Dapper + 27 voting/critic + 18 guardrails), then 32 cost, 33 safety, 34 design-your-own.
