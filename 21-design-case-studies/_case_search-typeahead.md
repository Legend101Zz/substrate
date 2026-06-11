# 21 · Case study — Web search / typeahead (inverted index, sharding, scatter-gather tail)

> Phase-1 brief (NO course prose). Bespoke walkthrough. Math RECOMPUTED in `_recompute.py`
> (Case 4). The canonical scatter-gather case: it makes 13/20's fan-out tail the central
> problem, sits on 06/12's inverted index, and shards with 14.

## 1. Requirements
- **Functional:** full-text search over a huge corpus returning ranked results; **typeahead**
  (prefix suggestions as the user types); spelling tolerance.
- **Non-functional:** search p99 < 200 ms; **typeahead p99 < 100 ms** (must feel instant per
  keystroke); high read availability; freshness of the index is eventual (new docs appear in
  seconds-to-minutes, acceptable).
- **Scale (RECOMPUTED, Case 4):** 100M searches/day, 20 keystrokes/search ->
  **typeahead ~23,148 prefix QPS** (peak ~46k); 50B docs / 500M per shard -> **100 index shards**;
  scatter-gather tail with p_slow=0.01: N=10 -> 9.6% slow, N=50 -> 39.5%, **N=100 -> 63.4%**.

## 2. Data model + API
- **Model:** an **inverted index** (reuse 06/12): `term -> posting list [doc_id, positions, tf]`,
  plus a `doc_store {doc_id -> metadata/snippet}`. Typeahead uses a **prefix structure** (trie /
  FST / completion suggester) mapping prefixes -> top-k completions with precomputed scores.
- **API:** `GET /search?q=...&page=...`; `GET /suggest?prefix=...` (returns top-k instantly).
- The index is **partitioned by document** (each shard holds a slice of the corpus + its own
  complete inverted index) -> a query must hit **all** shards and merge (scatter-gather). Alt:
  partition by term (each shard owns some terms) — fewer shards per query but hot terms become hot
  shards; document-partitioning is the common choice for balanced load.

## 3. Bottleneck analysis — the tail is the enemy
- **Scatter-gather over 100 shards:** every query fans out to all shards; the response is as slow
  as the **slowest** shard. With per-shard p99 slowness p=0.01, **P(>=1 slow of 100) = 63.4%**
  (RECOMPUTED; identical math to 13/20 fan-out). The mean shard is fast; the *tail* dominates the
  user-visible latency. This is the textbook **20 tail-at-scale** problem.
- **Typeahead QPS is 20x search QPS** (per keystroke) -> the prefix service is the highest-QPS
  component and must be almost entirely cache/RAM-served with a strict latency budget.

## 4. Design + cross-links to 13-20
- **06/12:** the inverted index + posting-list intersection is the core data structure (reuse 06);
  ranking (TF-IDF/BM25) layered on top.
- **13:** the fan-out tail identity 1-(1-p)^N is the sizing argument; latency budget forces the
  scatter-gather mitigations.
- **14:** document-partition into 100 shards (balanced); replicate each shard for read throughput +
  availability; hot query terms handled by caching, not by term-partitioning (avoids hot shard).
- **15:** index shards are **read-replicated**; index updates are eventually consistent (a new doc
  is indexed async); no strong consistency needed — searching slightly stale results is fine.
- **16:** **heavy caching** — popular queries + typeahead prefixes cached (a small set of prefixes
  covers most keystrokes); result caching with short TTL; the typeahead service is essentially a
  cache.
- **17:** indexing is an **async pipeline** — crawled/ingested docs flow through a queue/log to
  indexers that update shards (reuse 09/17); the read path never waits on indexing.
- **18:** rate-limit expensive queries; shed/deprioritize under load; per-shard bounded queues.
- **19:** per-shard p99 + overall p99, slow-shard rate, cache hit ratio, fan-out tail = the golden
  signals; tracing (Dapper, 19) makes the slow shard in a scatter-gather *legible*.
- **20:** **the headline mitigations** — **hedged / tied requests** to a replica of the slow shard
  (cut the tail; reuse 20/Dean); **"good enough" partial results** (return after 95/100 shards
  respond rather than wait for the straggler — Dean's "99.9% in 200ms > 100% in 1s", reuse 20
  tainted/partial results); micro-partitioning + replica probation.

## 5. Failure modes (20)
- **Straggler shard:** without mitigation, one slow shard slows 63% of queries -> hedge to a
  replica + return partial results past a deadline (20).
- **Shard outage:** serve from a replica; if a shard is fully down, return partial results flagged
  incomplete (graceful degradation > error).
- **Cache miss storm on a trending query:** coalesce (16 stampede) so one trending term doesn't
  hammer all 100 shards simultaneously.
- **Indexing backlog:** freshness degrades (results lag) but search stays up — the read path is
  decoupled from the async indexer (17).

## 6. Tradeoffs
- **Document- vs term-partitioning:** document-partition = every query hits every shard (fan-out
  tail) but balanced load + easy updates; term-partition = fewer shards/query but hot terms = hot
  shards + harder updates. Document-partition + tail mitigations is the common answer.
- **Completeness vs latency:** waiting for all 100 shards maximizes recall but inflates p99;
  returning partial results past a deadline trades a little recall for a huge tail win (20).
- **Freshness vs index cost:** real-time indexing is expensive; near-real-time (seconds-minutes)
  via the async pipeline is the standard compromise (17/15).
- **Typeahead precompute vs compute:** precomputed top-k per prefix is fast but storage-heavy and
  staler; on-the-fly is fresher but slower — precompute wins for the 100 ms budget.

## 7. Sources / gaps
- **REUSED (line-verified):** 06 (inverted index, posting lists, intersection), 12 (canon reading /
  index structures), 13 (fan-out tail sizing, latency budget), 14 (document-partition sharding,
  replication, hot-term-via-cache), 15 (read replicas, eventual index consistency), 16 (query +
  prefix caching, stampede coalescing), 17 (async indexing pipeline), 18 (query shedding), 19
  (per-shard p99, tracing the straggler), 20 (hedged/tied requests, partial results, probation —
  the tail-at-scale core).
- **RECOMPUTED:** typeahead QPS, shard count, scatter-gather tail at N=10/50/100.
- **`[UNVERIFIED]`:** specific search-engine designs (Google/Elasticsearch/Lucene internals) not
  fetched as primaries this session; BM25/Lucene segment mechanics are an Appendix-P candidate.
  Mechanisms grounded in 06/13/20.
