# 30 — RAG, Retrieval & Grounding · _structure.md

**Identity:** the Part III chapter that gives **25's non-parametric memory tier its retrieval
mechanism** — how an agent pulls the *right* facts from a corpus far bigger than any window into
context at query time, and grounds its output in citable evidence instead of in frozen weights. 25
said "externalize to a store"; 30 says "make it a vector index + a semantic top-K retriever."

**Bespoke shape — "a retrieval-pipeline walkthrough where every stage is a DATA-SYSTEMS chapter
(06+14+08+15+16) re-applied to text, plus one genuinely new primitive (the embedding) and one new
failure mode (corpus poisoning)."** NOT four clusters. Walk the pipeline corpus→chunks→embeddings→
index→query→inject end-to-end; at each stage name the Part I/II law it reuses (chunking = 14
partitioning; ANN = 06 right-structure-beats-scan; top-K = 08 read path; cache = 08/16; staleness =
15/16 replica lag). The two-memories thesis is VERIFIED from the RAG paper: parametric (weights:
frozen, stale, hallucination-prone) vs non-parametric (a corpus you can revise/expand/inspect at
query time without retraining). Grounding buys exactly the three gaps the paper names: **updatable
knowledge, provenance, less hallucination.** Primary FETCHED+VERIFIED (RAG, Lewis et al. 2020, arXiv
2005.11401). Math recomputed (15/15). The `/build` deliverable: a `search_corpus` tool on the 28
harness — the eighth harness upgrade.

## Dependency position
- **Depends on:** 25 (the non-parametric memory tier this retrieves into) + 06 (ANN/HNSW — the
  right-structure-beats-O(N)-scan lesson) + 14 (chunking = partitioning tradeoff) + 08 (two-tier read
  path: cheap-broad → precise-narrow; cache) + 15/16 (the index is a replica → staleness/lag) + 24
  (inject K chunks under the window budget; lost-in-the-middle dilution) + 22 (the loop the chunks
  flow into) + 23/29 (RAG-as-a-tool / MCP resource) + 28 (the harness it bolts onto).
- **Feeds into:** 31 (faithfulness/grounding eval — does the cited passage support the claim?) + 32
  (retrieve-vs-stuff is a cost lever; embedding/result caching ROI) + 33 (corpus poisoning /
  injection-via-retrieved-passage — never trust retrieved text as commands) + 34 ("+ large/changing
  knowledge → add 25 and/or 30" is a branch of the design tree).
- **Appendix links DOWN:** F-postgres (the index as a storage replica; pgvector-style) · G-redis
  (cache tier for embeddings/results) · N-math (vector similarity, recall/precision arithmetic) ·
  M-agentic-papers (RAG + DPR anchors). 30 owns the retrieval pipeline; structures live in 06,
  caching in 08/16, threats in 33.

## Section specs (3–5 lines each)
1. **The one idea: two memories, not one (VERIFIED)** — RAG: combine "pre-trained parametric and
   non-parametric memory." Parametric = weights (frozen, stale, hallucinate); non-parametric = an
   external corpus you can "revise, expand, inspect" at query time without retraining, stored as "a
   dense vector index ... accessed with a pre-trained neural retriever." Grounding = anchoring output
   in retrieved citable evidence. It buys the three named gaps: updatable knowledge, provenance,
   "more specific, diverse and factual" output.
2. **Corpus → chunks (14/06)** — split the corpus into retrievable passages; chunk size is a 14
   partition tradeoff (too big = budget waste + topic dilution; too small = lost surrounding context).
   This is the first design knob and it propagates through every downstream stage.
3. **Chunk → embedding (THE new primitive)** — a **bi-encoder** (VERIFIED: RAG's retriever "is based
   on DPR," a BERT bi-encoder) maps text → a dense vector. The 06 mental model: a *similarity-
   preserving fingerprint* — like a hash, but "near = semantically similar" instead of "equal =
   identical." This is the one genuinely new mechanism in the chapter; everything else is reused.
4. **Embeddings → vector index (06 ANN)** — VERIFIED: "MIPS index using FAISS with a Hierarchical
   Navigable Small World"; MIPS "solved in sub-linear time." Exactly the 06 lesson: the right
   structure turns an O(N) scan into ~O(log N) lookup. RECOMPUTED: 10M chunks → ~23 ops, ~430,000×
   fewer comparisons than brute force.
5. **Query → top-K → inject + ground (08/24/25)** — embed the query with the SAME encoder → ANN top-K
   nearest chunks; optional cross-encoder rerank (08 two-tier: cheap broad → precise narrow). Place
   passages in the window (24 allocation/placement) and instruct "answer only from these and cite
   them." VERIFIED: RAG marginalizes the doc as a latent variable (RAG-Sequence vs RAG-Token); the
   agent analogue is the prompt-time stuff-top-K pattern.
6. **The economics (RECOMPUTED)** — ANN not scan (~430,000× fewer comparisons, matches VERIFIED
   "sub-linear"). Retrieve top-K beats stuffing the corpus: `K·c ≤ W-(p+(t-1)g)`, K_max≈248 — pick
   the *relevant* K. K is a precision/recall/cost knob: recall `1-(1-r)^K` (diminishing) vs cost K·c
   (linear) → finite optimal K; past saturation (~K≈10) extra chunks become **distractors** (24
   lost-in-the-middle). Caching: embeddings deterministic per (model, chunk) → re-index only changed
   chunks (1M→1k, 1000×); results cacheable per (query, index-version) with TTL.
7. **Staleness: the index is a replica (15/16)** — re-index lag = the staleness window; **grounding is
   only as fresh as the index** — an edited fact is invisible until re-embedded. This is exactly the
   15/16 replica-lag law applied to a vector store.
8. **Where 30 sits + failure modes** — 30 is the retrieval mechanism for 25's non-parametric tier;
   RAG-as-a-tool is a 23 contract / 29 MCP resource. Failures (all 06/14/08/15/16 + one new): recall
   miss (ungrounded → hallucinate) · precision miss (top-K distractors → 24 dilution) · bad chunk
   size (14) · stale index (15/16) · embedding drift (re-embed whole corpus) · **corpus poisoning /
   injection-via-retrieved-passage** (→33: never trust retrieved text as commands; 25 poisoning blast
   radius over a *shared* corpus) · provenance mismatch (→31 faithfulness).

## Paired build lab (/build → own-coding-agent-harness, eighth upgrade)
Add a `search_corpus` tool (23) to the 28 harness: chunk (14) → embed with a bi-encoder → ANN index
(06 HNSW) → per relevant turn: embed query, MIPS top-K, inject + "cite sources" (24/25). Cache
embeddings (08) + results (16). Acceptance = DEMONSTRATE THE WALL THEN THE FIX: query an
edited-but-not-reindexed doc → stale answer (16); set K too high → dilution + cost (24); plant a
poisoned doc → it hijacks the answer (→33).

## Diagrams needed
- The full pipeline: corpus → chunks → embeddings → ANN index → query embed → top-K → inject+cite.
- Parametric vs non-parametric memory (weights vs revisable corpus) — the two-memories model.
- Embedding as a similarity-preserving fingerprint (near = semantically similar) vs a hash.
- ANN/HNSW vs brute-force scan: O(log N) vs O(N), the ~430,000× payoff (06).
- The K knob: recall `1-(1-r)^K` vs cost K·c → finite optimal K + distractor zone (24).
- Index-as-replica staleness window (15/16 lag applied to the vector store).
- The corpus-poisoning attack path (1 poisoned chunk → many ungrounded reads → 33).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **PRIMARY (FETCHED+VERIFIED):** RAG (Lewis et al. 2020, arXiv 2005.11401) —
  `meta/fetched_primaries/rag-2005.11401.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_rag.md`.
- **RECOMPUTED:** `_recompute.py` (15/15) — ANN-vs-scan, retrieve-vs-stuff budget, K knob, embedding
  cache, index staleness.
- **REUSED:** 06, 07, 08, 14, 15, 16, 22, 23, 24, 25, 28, 29.
- **`[UNVERIFIED]` carry-forward (none load-bearing) — STILL OWED, network blocked this session:**
  **DPR (arXiv 2004.04906)** — retried this session, host still 000; carry `[UNVERIFIED]`, erase
  nothing; the bi-encoder claim rides VERIFIED RAG-paper text ("retriever ... is based on DPR") until
  the DPR primary itself heals. Also carried: FAISS + HNSW (Malkov & Yashunin 2016) primaries;
  BM25/sparse + hybrid retrieval; cross-encoder reranking; chunking strategies; embedding-model
  specifics; RAG eval (RAGAS → 31); long-context-vs-RAG; GraphRAG/agentic-RAG; injection-via-
  retrieved-passage mitigations (→33).
- **Boundary discipline:** structures (HNSW/B-tree) live in 06; caching in 08/16; replica lag in
  15/16; faithfulness eval in 31; threats in 33. 30 owns the pipeline + the embedding primitive + the
  grounding thesis.
