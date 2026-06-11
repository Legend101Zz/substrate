# 30 · rag-retrieval-and-grounding — research brief (Phase 1, briefs only)

> Bespoke structure: a **RETRIEVAL-PIPELINE WALKTHROUGH** (corpus → chunk → embed → index → retrieve
> → rank → inject/ground → answer-with-provenance) — NOT abstract source clusters and NOT the 13-20
> four-cluster shape. 30 is where the agent stops relying only on what's in its weights (25
> parametric memory) and learns to **pull facts from an external corpus into context at query time**.
> Primary: **RAG (Lewis et al., NeurIPS 2020, arXiv 2005.11401) FETCHED+VERIFIED**. Math:
> `_recompute.py`. Factcheck: `_factcheck_phase1.md`.

---

## 0. What this sub-course IS

24 said *engineer the context*; 25 said *externalize memory to a store*; 30 answers the operational
question both raise: **how do you find the *right* tokens to put in the window, out of a corpus far
bigger than any window?** RAG is the answer — **retrieval-augmented generation** — and it is the
worked example. The transferable concept is **grounding**: anchoring the model's output in
retrieved, citable evidence rather than in its (fixed, stale, hallucination-prone) weights.

30 is mostly an **application of Part I/II data systems** to the agent: it's an index (06/07), a
partitioned store (14), a cache (08/16), and a read path (08) — wired into the 22 loop's
"assemble context" box (24) and the 25 memory hierarchy. The *new* idea is small and verified
(parametric vs non-parametric memory + ANN top-K); the *engineering* is all reused.

---

## 1. The headline idea (VERIFIED)

**Two memories, not one.** VERIFIED (RAG abstract): models "combine pre-trained **parametric** and
**non-parametric** memory" — parametric = the seq2seq model's weights; non-parametric = "a **dense
vector index** of Wikipedia, accessed with a **pre-trained neural retriever**." For an agent:
parametric memory = the base model (frozen, stale, can hallucinate); non-parametric memory = an
external corpus you can **revise, expand, and inspect** at query time *without retraining*.

VERIFIED motivation (RAG intro): parametric-only models "cannot easily expand or revise their
memory, can't straightforwardly provide insight into their predictions, and may produce
'hallucinations'." So grounding buys exactly three things, all VERIFIED as the paper's stated gaps:
1. **Updatable knowledge** (edit the corpus, not the weights),
2. **Provenance / inspectability** (cite the retrieved passage),
3. **Reduced hallucination** (RAG generates "more specific, diverse and **factual** language" than
   a parametric-only baseline — VERIFIED result).

---

## 2. The pipeline, walked (the bespoke spine)

### 2.1 Corpus → chunks (reuse 14 partitioning + 06)
Split documents into retrievable units ("passages"). Chunk size is a tradeoff: too big wastes the
24 budget and dilutes relevance; too small loses context. This is 14's partitioning problem (choose
the unit so each piece is independently useful) applied to text.

### 2.2 Chunk → embedding (the new primitive — a learned hash into semantic space)
Each chunk is encoded to a dense vector by a **bi-encoder** (VERIFIED: RAG's retriever "is based on
**DPR**", a BERT bi-encoder — query encoder + document encoder). Mental model from 06: an embedding
is a *similarity-preserving* fingerprint — like a hash, but where *near* means *semantically
similar* instead of *identical*. (Contrast 06's exact-match hashing: embeddings enable approximate
*semantic* match.)

### 2.3 Embeddings → vector index (reuse 06 ANN structures)
VERIFIED: "build a single **MIPS** index using **FAISS** with a **Hierarchical Navigable Small
World**" — i.e. an **Approximate Nearest Neighbor** index. Retrieval = **Maximum Inner Product
Search**, which VERIFIED "can be approximately solved in **sub-linear time**." This is exactly the
06 lesson: the right structure turns an O(N) scan into a sub-linear lookup (HNSW is a skip-list-like
navigable graph; the same family as 06's skiplist/B-tree "structure buys sub-linear search").

### 2.4 Query → top-K retrieve (the read path, reuse 08)
VERIFIED: "For query x, we use MIPS to find the **top-K** documents z_i." Embed the query with the
same encoder, ANN-search the index, return the K nearest chunks. K is a budget knob (more below).
Optional rerank with a (slower, more accurate) cross-encoder over the top-K candidates — the
classic 08 two-tier read path (cheap broad filter → expensive precise filter), `[UNVERIFIED]` depth.

### 2.5 Inject + ground (reuse 24/25 — retrieval-into-context)
Place the retrieved passages into the window (24 allocation/placement) and instruct the model to
**answer only from them and cite them**. VERIFIED, RAG marginalizes over the retrieved doc as a
"latent variable" (two formulations: **RAG-Sequence** = same passages for the whole output;
**RAG-Token** = different passages per token). The *agent* analogue is the prompt-time version:
stuff top-K into context and condition generation on it (the engineering pattern the field calls
"RAG" today). Provenance = return the citations alongside the answer.

---

## 3. The economics (RECOMPUTED — why the structure is mandatory)
- **Why ANN, not scan:** semantic search over N chunks is O(N) brute force; an HNSW/MIPS index is
  ~O(log N) (sub-linear, VERIFIED). For N=10M chunks that's ~10M ops → ~23 ops: the 06 structure
  payoff, ~430,000× fewer comparisons (recomputed).
- **Retrieval beats stuffing the whole corpus (the 24 budget argument):** a corpus is far larger
  than any window; you can only afford K chunks of size c. Retrieval picks the *relevant* K instead
  of paying to (impossibly) send all N — the same break-even as 23's retrieval-over-tools, now over
  *documents* (recomputed). K·c must fit the 24 budget `W-(p+(t-1)g)`.
- **K is a precision/recall/cost knob:** bigger K raises recall (the answer is more likely present)
  but costs K·c tokens and adds distractors (24's "lost-in-the-middle" + dilution); there's an
  optimal K where marginal recall < marginal cost+distraction (recomputed).
- **Caching (08/16):** embeddings are deterministic per (model, chunk) → cache them (compute once,
  reuse forever); query results are cacheable per (query, index-version) with TTL/invalidation on
  corpus update (16). Recomputed: caching embeddings turns re-index cost from O(N) re-embeds to ~0.
- **Staleness vs freshness (16/15):** the index is a replica of the corpus → it has *replication
  lag*; an edited document is invisible until re-embedded/re-indexed (the 15/16 consistency-of-a-
  cache problem). Grounding is only as fresh as the index.

## 4. Grounding ⊂ memory ⊂ context (where 30 sits)
30 is the *retrieval mechanism* for 25's non-parametric tier: 25 said "externalize to a store with
pager tools"; 30 says "make that store a vector index and the pager a semantic top-K retriever."
Retrieved chunks then flow through 24 (budget/placement) into the 22 loop. RAG-as-a-tool is also a
23 contract / 29 connector (a `search_corpus` tool / an MCP **resource**). So 30 unifies 06+14+08+16
(data systems) with 24+25 (context/memory) and 22 (the loop).

## 5. Failure modes (mostly data-system failures + one new one)
Retriever misses the relevant chunk (recall failure → answer ungrounded → hallucinate anyway) ·
top-K full of distractors (precision failure → 24 dilution) · chunk too big/small (14 unit choice) ·
**stale index** (16/15 lag — edited doc not re-indexed) · embedding-model drift (re-embed whole
corpus on model change — expensive, cache-busting) · **corpus poisoning / injection-via-retrieved-
passage** (33 + 25: a malicious document in the corpus is retrieved and its text treated as
instructions — the 25 poisoning blast radius over a *shared* corpus; never trust retrieved text as
commands) · provenance mismatch (cited passage doesn't actually support the claim → 31 faithfulness
eval). **All but injection are 06/14/08/15/16 problems.**

## 6. Build-your-own
Add a `search_corpus` tool (23) to the 28 harness: chunk a doc set (14) → embed with a bi-encoder →
build an ANN index (06 HNSW) → on each relevant turn, embed the query, MIPS top-K, inject the
passages into context (24) with a "cite your sources" instruction (25 non-parametric tier). Cache
embeddings (08) and results (16). Break it: ask about a doc you edited but didn't re-index → stale
answer (16 lag); set K too high → window dilution + cost (24); drop a poisoned doc in the corpus →
watch it hijack the answer (33). Eighth harness upgrade
(loop→tools→context→memory→persistence→orchestration→connectors→**grounding**).

## 7. Provenance + `[UNVERIFIED]`
- **PRIMARY (FETCHED+VERIFIED):** RAG (Lewis et al. 2020, arXiv 2005.11401) —
  `meta/fetched_primaries/rag-2005.11401.{pdf,txt}`, receipt `_VERIFIED_2026-06-10_rag.md`
  (parametric vs non-parametric memory; DPR bi-encoder; MIPS top-K sub-linear; FAISS+HNSW;
  marginalize latent doc; cures hallucination + supplies provenance + updatable knowledge).
- **RECOMPUTED:** `_recompute.py` — ANN vs scan (sub-linear payoff), retrieval-vs-stuff budget, K
  precision/recall/cost knob, embedding-cache reuse, index staleness/lag.
- **REUSED:** 06 (ANN/HNSW/skiplist sub-linear search), 07 (index), 08 (read path/cache), 14
  (chunking/partitioning), 15/16 (replica lag/cache invalidation), 22 (loop), 23 (search-as-tool),
  24 (retrieval-into-context/budget/placement), 25 (non-parametric memory tier), 28 (harness), 29
  (RAG-as-MCP-resource).
- **`[UNVERIFIED]` carry-forward (none load-bearing):** DPR primary (arXiv 2004.04906); FAISS
  (Johnson et al.) + HNSW (Malkov & Yashunin 2016) algorithm primaries; BM25/sparse + hybrid
  retrieval; cross-encoder reranking; chunking strategies; embedding-model specifics; RAG eval
  (RAGAS, faithfulness/groundedness → 31); long-context-vs-RAG tradeoff; GraphRAG/agentic-RAG;
  injection-via-retrieved-passage mitigations (→33).
