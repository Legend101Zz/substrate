# 30 · Phase-1 factcheck — rag-retrieval-and-grounding

> Method (same discipline as 13-29): every load-bearing claim is (a) VERIFIED verbatim against the
> fetched RAG paper, (b) RECOMPUTED in `_recompute.py` (15/15 pass), (c) REUSED from a line-verified
> Part I/II + 22-29 anchor, or (d) flagged `[UNVERIFIED]` carry-forward. 0 blockers.

## Bespoke structure note
30 is a **RETRIEVAL-PIPELINE WALKTHROUGH** (corpus → chunk → embed → index → retrieve → rank →
inject/ground → answer-with-provenance), NOT abstract clusters and NOT the 13-20 four-cluster shape.
It is the retrieval mechanism for 25's non-parametric memory tier. Plan-sanctioned ("FETCH RAG,
Lewis et al. 2020, arXiv 2005.11401; ↔ 06 structures + 08/16 caching + 24/25 retrieval-into-context
+ 14 partitioning").

## Primary fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020 (arXiv 2005.11401) | `rag-2005.11401.{pdf,txt}` | parametric vs non-parametric memory; DPR bi-encoder retriever; MIPS top-K sub-linear; FAISS+HNSW; latent-doc marginalization; hallucination/provenance/updatable-knowledge |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_rag.md` (verbatim quotes logged there).

### Verified claims (RAG — verbatim)
- **Parametric vs non-parametric memory:** "combine pre-trained parametric and non-parametric memory
  for language generation"; "parametric memory is a pre-trained seq2seq model and the non-parametric
  memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever."
  VERIFIED. (THE load-bearing concept — §1.)
- **Motivation (the three gaps):** parametric-only models "cannot easily expand or revise their
  memory, can't straightforwardly provide insight into their predictions, and may produce
  'hallucinations'." VERIFIED. (Updatable knowledge + provenance + anti-hallucination — §1.)
- **MIPS top-K, sub-linear:** "we use Maximum Inner Product Search (MIPS) to find the top-K
  documents"; MIPS "can be approximately solved in sub-linear time." VERIFIED. (§2.3/2.4 — the 06
  ANN payoff.)
- **FAISS + HNSW:** "build a single MIPS index using FAISS with a Hierarchical Navigable Small
  World" approximation. VERIFIED. (§2.3 — the concrete ANN structure, 06 family.)
- **Retriever = DPR bi-encoder:** "The retrieval component p_η(z|x) is based on DPR" (BERT
  bi-encoder). VERIFIED. (§2.2 — embeddings as similarity-preserving fingerprints.)
- **Latent-doc marginalization, two formulations:** RAG-Sequence (same passages whole sequence) vs
  RAG-Token (different per token); doc treated as latent variable, "marginalize" via top-K. VERIFIED.
  (§2.5 — the inject/ground mechanism.)
- **Result:** SOTA on three open-domain QA tasks; generates "more specific, diverse and factual
  language" than parametric-only baseline. VERIFIED. (Grounding improves factuality measurably — §1.)

## Recomputed claims (`_recompute.py`, 15/15)
- **ANN vs scan:** O(N) brute force vs ~O(log N) HNSW/MIPS; 10M chunks → ~23 ops, ~430,000× fewer
  comparisons (06 structure payoff, matches VERIFIED "sub-linear"). PASS.
- **Retrieve top-K vs stuff corpus:** all-corpus (5B tok) overflows window absurdly; top-K fits the
  24 budget `W-(p+(t-1)g)`; K_max=248 chunks. PASS.
- **K precision/recall/cost knob:** recall = 1-(1-r)^K diminishing (0.5/0.75/0.9375 at K=1/2/4);
  marginal recall shrinks while cost is constant → finite optimal K; big K adds distractors (recall
  saturates by K~10, rest dilute → 24 lost-in-the-middle). PASS.
- **Embedding cache (08):** embeddings deterministic per (model, chunk) → re-index only changed
  chunks (1M → 1k, 1000× less). PASS.
- **Index staleness (15/16):** index is a replica → re-index lag = staleness window; grounding only
  as fresh as the index (edited fact invisible until re-indexed). PASS.

## Reused (line-verified Part I/II + 22-29)
06 (ANN/HNSW/skiplist sub-linear search, hashing→embeddings contrast); 07 (index); 08 (read path/
cache, two-tier filter); 14 (chunking/partitioning); 15 (replica lag); 16 (cache invalidation/TTL);
22 (the loop); 23 (search-as-tool contract); 24 (retrieval-into-context, budget, placement/lost-in-
the-middle); 25 (non-parametric memory tier); 28 (the harness); 29 (RAG-as-MCP-resource/tool).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- DPR primary (Karpukhin et al. 2020, arXiv 2004.04906) — referenced by RAG, not separately fetched.
- FAISS (Johnson et al.) + HNSW (Malkov & Yashunin 2016) algorithm primaries — named, ANN math
  deferred (06 cross-link carries the structure).
- BM25/TF-IDF sparse + hybrid (dense+sparse) retrieval; cross-encoder reranking; chunking
  strategies; embedding-model specifics.
- RAG eval (RAGAS, faithfulness/groundedness/answer-relevance) → 31.
- Long-context-vs-RAG tradeoff; GraphRAG/agentic-RAG; injection-via-retrieved-passage mitigations
  → 33. None load-bearing for the grounding model.

## Verdict
30 is honest and pipeline-appropriate: the new concept (parametric vs non-parametric memory + ANN
top-K retrieval + latent-doc grounding) is VERIFIED verbatim against RAG; the economics (sub-linear
ANN payoff, retrieve-vs-stuff budget, K knob, embedding cache, index staleness) are RECOMPUTED; the
entire engineering REUSES line-verified 06/07/08/14/15/16/24/25. Residual `[UNVERIFIED]` are
sub-component primaries (DPR/FAISS/HNSW) + eval + advanced variants, none load-bearing for the
grounding model. Reconcile into `_research.md`.
