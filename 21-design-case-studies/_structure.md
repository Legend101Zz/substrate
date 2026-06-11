# 21 — Design Case Studies · _structure.md

**Identity:** the CAPSTONE of Part II. It introduces NO new primitives — it teaches the METHOD of
composing the entire 13–20 toolkit on six concrete designs. The thesis: a design is a sequence of
FORCED MOVES — the requirements + the arithmetic pick the primitives; the engineer's job is to see
the forcing function and price the tradeoff.

**Bespoke shape — "the method once, then six case-study walkthroughs that each force a different
bottleneck."** NOT abstract clusters and NOT new theory. Two movements. **Part A — the design
method:** one repeatable 6-step loop (requirements → back-of-envelope → data model + API →
bottleneck → design with cross-links → failure modes + tradeoffs). **Part B — six walkthroughs:**
each applies the loop end-to-end, and each is chosen because EXACTLY ONE bottleneck dominates it, so
together they tour the whole toolkit. The capstone payload is the toolkit-usage matrix (which case
forces which primitive, and why) — reading a column = a complete design, reading a row = how one
primitive changes shape under different pressure. Math recomputed (32/32); CAP + PACELC are VERIFIED
primaries.

## Dependency position
- **Depends on:** EVERYTHING in Part II — 13 (back-of-envelope, fan-out tail, latency budget), 14
  (data model = access contract, sharding, hot key, cross-shard txn/saga), 15 (consistency dial,
  quorum, read-your-writes, failover, CAP/PACELC concrete), 16 (cache patterns, origin-load,
  stampede, CDN, immutable=infinite-TTL), 17 (async fan-out, idempotency=exactly-once-effect,
  outbox/CDC, cursor/replay), 18 (token bucket, windows, over-admit, 429, fail-open/closed,
  backpressure/shedding), 19 (golden signals, tracing the straggler, error budget), 20 (hedged/tied,
  partial results, degrade, choose-C-over-A, blast radius); plus 06/09/11/12 for structures + theory.
- **Feeds into:** Part III (the agentic sub-courses reuse this design method on agent systems),
  interview/practice readiness.
- **Appendix links DOWN:** N-math (the back-of-envelope formulas), P-search-internals candidate
  (Lucene/BM25 for the search case). 21 owns the design method + the matrix.

## Section specs (3–5 lines each)
### Part A — the design method
1. **The 6-step loop** — (1) requirements: functional + the NON-functional SLOs (latency/consistency/
   availability/durability) that decide everything; (2) back-of-envelope: RECOMPUTE QPS (read:write
   ratio!), storage/yr, bandwidth, keyspace, working set, connections, fan-out, shard count — the
   ARITHMETIC reveals the bottleneck, not taste; (3) data model + API = the access-pattern contract
   (14); (4) bottleneck analysis: name the ONE thing that breaks first; (5) design with cross-links:
   apply the minimal primitives that relieve it, cite + price each; (6) failure modes + tradeoffs (20).

### Part B — the six walkthroughs (each forces a different bottleneck)
2. **URL shortener — reads dominate (100:1)** → the whole design is caching (16). Keyspace by code
   (KGS vs hash, base62^6/^7 + 5-yr fill); write-once = trivial consistency (15); degrade-to-cache
   (20). Bottleneck: reads.
3. **News feed — write-amplification (fan-out ~200×)** → fan-out-on-write vs read; the celebrity is a
   14 hot key; async fan-out (17); timeline + counts cache (16); eventual + read-your-writes (15);
   degrade freshness (20). Bottleneck: the write-amp + the read:write ratio choosing push vs pull.
4. **Chat / messaging — connections (1000 nodes)** → fan-out group delivery; per-conversation ordering
   (11/17); presence; at-least-once + dedup = exactly-once-EFFECT (17); leader-per-partition order
   (15); websockets; reconnect + resync (20). Bottleneck: connections + ordering.
5. **Search / typeahead — the scatter-gather tail** → inverted index (06/12); document-partition 100
   shards (14); scatter-gather tail at N=100 = 63.4% (13/20); query + prefix cache (16); hedged/tied
   + partial results (20); read replicas/eventual (15). Bottleneck: the tail.
6. **Payments / ledger — correctness under failure** → append-only double-entry ledger; idempotency =
   exactly-once-effect (17); 2PC/saga (11/14); strong consistency, sync quorum W+R>N, PC/EC (15);
   CAP/PACELC choose-C-over-A, fail CLOSED (20); reconciliation/audit (19). Bottleneck: correctness,
   not throughput (low QPS).
7. **Distributed rate limiter — the distributed counter** → direct 18 application; token bucket; shard
   counters by key + cell-based batching (over-admit `(M−1)·B=35`, 14/18); 1M checks/s (13); counter
   store = cache/RAM/TTL (16); best-effort PA/EL (15); fail-OPEN vs SPOF (20); 429-rate/over-admit
   SLO (19). Bottleneck: the distributed counter.

### Closing — the cross-case patterns (the synthesis)
8. **What the six cases teach together** — the read:write ratio decides the architecture; fan-out is
   one mechanism in three costumes (write cost / delivery cost / latency tail); exactly-once is ALWAYS
   exactly-once-EFFECT (one impossibility, one pattern, three cases); the consistency dial spans the
   whole catalog and PACELC orders all six; caching (scaling lever) vs consistency (correctness lever)
   oppose; resilience is always "degrade-to-SOMETHING" — different every time.

## Paired build labs (/build — the design toolkit)
Design canvas (the 6-step method as a fill-in template) → back-of-envelope calculator (DAU/ratios/
sizes → QPS, storage/yr, shard count, cache size, fan-out tail; wraps `_recompute.py`) → mini-
implementations: a KGS + redirect cache (URL); a push/pull/hybrid fan-out simulator (feed); a
per-conversation sequenced log with dedup (chat); a scatter-gather with hedged requests + partial
results (search); an idempotent double-entry ledger with saga compensation (payments); a token-bucket
limiter with cell-based batching (limiter — ties back to the 18 lab).

## Diagrams needed
- The 6-step design loop as the spine motif (reused at the top of each walkthrough).
- The toolkit-usage matrix (cases × primitives) — the capstone centerpiece.
- Per-case bottleneck callout (one dominant constraint highlighted per design).
- Fan-out as three costumes (feed write-amp / chat group delivery / search scatter tail).
- The PACELC spectrum with all six cases placed on it (URL→limiter→search→feed→chat→payments).
- Push vs pull vs hybrid feed fan-out; scatter-gather + hedged/partial-results.
- Idempotent double-entry ledger + saga compensation; cell-based counter over-admit.
- "Degrade-to-something" table (what each design gives up under stress).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED PRIMARIES this session:** Gilbert-Lynch "Perspectives on CAP" 2012 (no C+A in a
  partitionable async system; CAP ⇒ no consensus under partition); Abadi PACELC 2012 ("if Partition:
  A vs C; Else: Latency vs Consistency"; PA/EL vs PC/EC). Both also upgrade 11 + 15 carry-forwards.
- **RECOMPUTED (32/32):** all QPS (URL 1157/115741, feed 34722/347/69444+1e8, chat 23148/1000 nodes,
  search 23148/100 shards/tail 63.4%, payments 116, limiter 1M); base62^6/^7 + 5-yr fill; storage
  (91/73/3.74 TB); cache 5 GB; origin load (1−h); W+R>N (4>3 strict) + fault tolerance; distributed
  over-admit `(M−1)·B=35`; counter store 64 MB; scatter-gather tail at N=10/50/100.
- **`[UNVERIFIED]` — community design idioms, no single canonical primary (MECHANISMS are grounded in
  line-verified 06–20; only the attribution to a specific external write-up is unverified):** KGS
  key-gen (URL); push/pull/hybrid feed (Twitter/IG eng blogs); chat protocols (websocket/XMPP/MQTT) +
  vendor chat designs (WhatsApp/Signal); search internals (Lucene/Elasticsearch/BM25 — Appendix-P
  candidate); payment-system designs (Stripe/Square ledger talks); GCRA + vendor rate-limiter posts.
  Carried from home sub-courses if 21 ever needs them in prose: Skeen 1981 3PC + Berenson 1995 ANSI
  isolation (11); Sagas 1987 (14); Dynamo for PA/EL. Teach mechanisms now; do NOT harden external
  attributions until fetched.
- **Newly 200 but deferred to next opportunistic pass:** arxiv.org, kafka.apache.org, postgresql.org.
  Still blocked: CoDel (queue.acm.org 403), raft.github.io (000), dl.acm.org DOI (403) — non-load-
  bearing for 21.
- **Boundary discipline:** 21 introduces NO new primitives — every mechanism cross-links UP to its
  home sub-course (13–20) and structures/theory to 06/09/11/12; back-of-envelope formulas → appendix
  N; search-engine internals → appendix P candidate. 21 owns ONLY the design method + the matrix.
