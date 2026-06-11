# VERIFIED — 2026-06-10 — RAG (Lewis et al. 2020)

Plan-mandated fetch for **30-rag-retrieval-and-grounding**. Network healed: arxiv.org reachable
(200). Saved to `meta/fetched_primaries/`.

## Source fetched
- **Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, Küttler, M. Lewis, Yih, Rocktäschel, Riedel,
  Kiela — "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020**
  (arXiv:2005.11401v4, 12 Apr 2021). Facebook AI Research / UCL / NYU.
  Files: `rag-2005.11401.pdf` (19 pp) + `rag-2005.11401.txt` (extracted via throwaway
  `/tmp/pdfx-venv` uv+pypdf 6.13.2 from Walmart external-pypi; venv removed after).
  `.code-puppy-venv` never touched.

## Verified VERBATIM claims (anchor 30)
- **The problem RAG solves (from abstract/intro, verbatim):** LLMs "store factual knowledge in
  their parameters" but "their ability to access and precisely manipulate knowledge is still
  limited"; "providing provenance for their decisions and updating their world knowledge remain
  open research problems." Parametric-only models "cannot easily expand or revise their memory,
  can't straightforwardly provide insight into their predictions, and may produce 'hallucinations'."
  → grounding = the cure for hallucination + the source of provenance + the updatable-knowledge path.
- **The core dichotomy (verbatim):** "models which combine pre-trained **parametric** and
  **non-parametric** memory for language generation." "the parametric memory is a pre-trained
  seq2seq model and the non-parametric memory is a **dense vector index of Wikipedia, accessed with
  a pre-trained neural retriever**." This is THE load-bearing concept of 30: model weights
  (parametric) + an external retrievable corpus (non-parametric).
- **Retrieval mechanism (verbatim):** "For query x, we use **Maximum Inner Product Search (MIPS)**
  to find the **top-K** documents z_i." MIPS "can be approximately solved in **sub-linear time**."
  "build a single MIPS index using **FAISS** with a **Hierarchical Navigable Small World**
  approxim[ation]." → the retriever = embed query + ANN top-K over a vector index (06 HNSW/ANN;
  sub-linear like the 06 structures).
- **Retriever = DPR (verbatim):** "The retrieval component p_η(z|x) is based on **DPR**." DPR uses a
  BERT-based **bi-encoder** (query encoder + document encoder) → dense embeddings.
- **Two formulations (verbatim):** "two RAG formulations, one which conditions on the same retrieved
  passages across the whole generated sequence" (**RAG-Sequence**) "and another which can use
  different passages per token" (**RAG-Token**). The retrieved document is treated as "a **latent
  variable**" that is "**marginalize[d]**" via a top-K approximation.
- **Result (verbatim):** "set the state of the art on three open domain QA tasks"; for generation,
  "RAG models generate more **specific, diverse and factual** language than a state-of-the-art
  parametric-only seq2seq baseline." → grounding improves factuality, measurably.

## What this anchors in 30
The whole sub-course: grounding = parametric (weights, 25 long-term memory) + non-parametric
(external corpus) memory; the retriever = embed → ANN/MIPS top-K over a vector index (06 HNSW,
sub-linear); chunk + embed + index the corpus (14 partitioning, 06 structures); inject retrieved
passages into context (24/25 retrieval-into-context); cache embeddings/results (08/16); grounding
cures hallucination + supplies provenance + makes knowledge updatable without retraining.

## Still NOT fetched (carry-forward `[UNVERIFIED]` for 30)
- **DPR** (Karpukhin et al. 2020, arXiv 2004.04906) as the dense-retriever primary — referenced by
  RAG, not separately fetched.
- **FAISS** (Johnson et al.) + **HNSW** (Malkov & Yashunin 2016) algorithm primaries — named in RAG,
  the ANN math deferred (the 06 cross-link carries the structure).
- BM25/TF-IDF sparse retrieval baseline; hybrid (dense+sparse) retrieval; reranking (cross-encoder);
  chunking strategies; embedding-model specifics; eval (RAGAS, faithfulness/groundedness → 31);
  long-context-vs-RAG tradeoff; GraphRAG/agentic-RAG. None load-bearing for the grounding model.
