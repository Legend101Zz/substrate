# 21 · design-case-studies — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 21 is the **CAPSTONE of Part II**: it
> introduces NO new primitives — it APPLIES the entire 13-20 toolkit to six concrete designs.
> Bespoke structure (per-case-study walkthroughs, not abstract clusters) per the plan. Full depth
> lives in the `_case_*.md` files; this file is the cross-case design method, the toolkit-usage
> matrix, consolidated sources, and the gap ledger. Math: `_recompute.py` (32/32 pass). New
> primaries this session: Gilbert-Lynch formal CAP + Abadi PACELC (receipt
> `meta/fetched_primaries/_VERIFIED_2026-06-10_cap-pacelc.md`).

Case files:
- `_case_url-shortener.md` (write-once / read-heavy; KGS vs hash; cache; 16/14)
- `_case_news-feed.md` (fan-out-on-write vs read; celebrity = 14 hot key; 17 async; 16 cache)
- `_case_chat-messaging.md` (fan-out, ordering 11/17, presence, delivery semantics 17, websockets)
- `_case_search-typeahead.md` (inverted index 06/12, sharding 14, scatter-gather tail 13/20)
- `_case_payments-ledger.md` (idempotency 17, exactly-once-effect, 2PC/saga 11/14, strong C 15, CAP/PACELC)
- `_case_rate-limiter.md` (direct 18 application; token bucket; cell counters 14)
Factcheck: `_factcheck_phase1.md`. Recompute: `_recompute.py`.

---

## 1. The spine — 21 is application, not theory
Every prior Part-II sub-course taught a *primitive*: 13 sizing, 14 partitioning, 15 replication/
consistency, 16 caching, 17 async/EDA, 18 rate-limiting/backpressure, 19 observability, 20
resilience/tail/capacity. 21 teaches the *method* of composing them: given requirements + a
back-of-envelope, which primitives does the bottleneck force you to reach for, and what does each
choice cost? The thesis: **a design is a sequence of forced moves — the requirements + the
arithmetic pick the primitives; the engineer's job is to see the forcing function and price the
tradeoff.**

## 2. The design method (the cross-cutting spine — the actual teachable content)
A repeatable 6-step loop, demonstrated six times:
1. **Requirements** — functional + **non-functional** (the SLOs: latency, consistency, availability,
   durability). The non-functionals decide everything; they are the constraints (13/19/20).
2. **Back-of-envelope** — RECOMPUTE QPS (read vs write ratio!), storage/yr, bandwidth, key space,
   cache working set, connection count, fan-out, shard count (13). *The arithmetic, not taste,
   reveals the bottleneck.*
3. **Data model + API** — the model is the **access-pattern contract** (14): point-get (URL),
   materialized inbox (feed), per-conversation log (chat), inverted index (search), append-only
   ledger (payments), per-key counter (limiter). The access pattern picks the model picks the engine.
4. **Bottleneck analysis** — name the one thing that breaks first: reads (URL), write-amplification
   (feed), connections (chat), the scatter-gather tail (search), correctness-under-failure
   (payments), the distributed counter (limiter). *Exactly one bottleneck dominates each design.*
5. **Design with cross-links** — apply the minimal primitives that relieve the bottleneck; cite
   which sub-course each comes from; price each.
6. **Failure modes + tradeoffs** — what breaks (20), and the explicit cost of every choice
   (push vs pull, 2PC vs saga, accuracy vs cost, fail-open vs fail-closed, C vs A, latency vs C).

## 3. The toolkit-usage matrix (which case forces which primitive, and why)
| primitive | URL | feed | chat | search | payments | limiter |
|---|---|---|---|---|---|---|
| **13** sizing | reads dominate (100:1) | write-amp 200x | connections 1000 nodes | tail at N=100 | low QPS/high correctness | 1M checks/s |
| **14** partition/shard | keyspace by code; KGS ranges | inbox by user; **celebrity hot key** | conversation; hot channel | document-partition 100 shards | account; **cross-shard txn+saga** | **shard counters by key** |
| **15** replication/consistency | write-once = trivial | eventual + read-your-writes | leader-per-partition order | read replicas/eventual | **sync quorum W+R>N; PC/EC** | best-effort PA/EL |
| **16** caching/CDN | **the whole design** | timeline + counts | recent/presence | **query+prefix cache** | counter store=cache | RAM/TTL store |
| **17** async/EDA | fire-and-forget analytics | **async fan-out** | **at-least-once+dedup=once-effect** | async indexing | **idempotency; outbox/CDC** | async count agg |
| **18** rate-limit/backpressure | write-path limit | fan-out backpressure | presence shed | query shed | fail-closed | **the whole design** |
| **19** observability/SLO | hit ratio/p99 | fan-out lag | deliver latency | per-shard p99/trace straggler | reconciliation/audit | 429 rate/over-admit |
| **20** resilience/tail | degrade-to-cache | degrade freshness | reconnect+resync | **hedged/tied + partial results** | **choose C over A** | fail-open vs SPOF |

Reading the matrix down a column = a complete design; reading across a row = how one primitive
shows up differently under different pressures. This matrix IS the capstone payload.

## 4. Cross-case reconciliations (the recurring patterns)
- **The read:write ratio decides the architecture.** URL (100:1 read) -> cache-everything; payments
  (correctness, low QPS) -> consistency-everything; feed -> the ratio is *why* push beats pull for
  reads. Step 2 of the method is load-bearing.
- **Fan-out is the unifying mechanism.** Feed (fan-out-on-write), chat (group delivery), search
  (scatter-gather) are the SAME `1-(1-p)^N` math (13/20) seen as a write cost, a delivery cost, and
  a latency tail respectively. The **celebrity/hot-key/hot-channel/straggler** are one phenomenon
  (14) wearing four costumes; the fixes (read-time merge, hedged requests, partial results) are 14
  + 20.
- **Exactly-once is always exactly-once-EFFECT, never transport.** Chat + payments + feed-append all
  resolve the same impossibility (11: FLP/2-generals) the same way: at-least-once delivery +
  idempotent apply keyed on an idempotency key (17). One impossibility, one pattern, three cases.
- **The consistency dial spans the whole catalog.** URL write-once (trivial) -> feed/search/limiter
  eventual (PA/EL) -> chat per-partition order -> payments strong (PC/EC). PACELC (VERIFIED) is the
  one axis that orders all six; the case studies are literally a tour of the PACELC spectrum.
- **Caching is the default scaling lever; consistency is the default correctness lever; they
  oppose.** Every read-heavy case reaches for 16; every correctness-heavy case reaches for 15; the
  art is knowing which pressure dominates (a cache is a deliberately-stale replica — 16/15 link).
- **Resilience is degrade-to-something.** URL degrades to cache, feed degrades freshness, chat
  degrades presence, search degrades to partial results, payments degrades to *rejecting* (fail
  closed), limiter degrades to fail-open. "Graceful degradation" (20) is concrete and different
  every time — the requirements decide what you're willing to give up.

## 5. Load-bearing facts, by provenance
**VERIFIED from primaries fetched this session** (`meta/fetched_primaries/`):
- Gilbert-Lynch "Perspectives on CAP" (2012): cannot guarantee both safety(C) + liveness(A) in a
  partitionable async system; CAP ⇒ no consensus under partition. (Case 5 forfeit-A.)
- Abadi PACELC (2012): "if Partition: A vs C; **Else**: **Latency vs Consistency**"; PA/EL (Dynamo-
  style) vs PC/EC (ACID). (Case 5 + the §4 consistency-dial reconciliation.)

**RECOMPUTED** (`_recompute.py`, 32/32): all QPS (URL 1157/115741, feed 34722/347/69444+1e8, chat
23148/1000 nodes, search 23148/100 shards/tail 63.4%, payments 116, limiter 1M); base62^6/^7 +
5-yr fill; storage (91 TB / 73 TB / 3.74 TB); cache 5 GB; origin load (1-h); W+R>N (4>3 strict) +
fault tolerance; distributed over-admit (M-1)*B=35; counter store 64 MB; scatter-gather tail at
N=10/50/100.

**REUSED from line-verified prior sub-courses**: 06 (inverted index, base62/hashing, consistent
hashing), 09 (the log), 11 (ordering/sequencer, FLP/2-generals, 2PC/consensus, no global clock),
12 (canon/index structures), 13 (back-of-envelope, fan-out tail, latency budget), 14 (data model =
access contract, sharding, hot key, cross-shard txn/saga), 15 (consistency dial, quorum W+R>N,
read-your-writes, failover, CAP/PACELC concrete), 16 (cache patterns, origin-load (1-h), stampede,
CDN, immutable=infinite-TTL), 17 (async fan-out, idempotency = exactly-once-effect, outbox/CDC,
cursor/replay), 18 (token bucket, windows, over-admit (M-1)*B, 429, fail-open/closed, backpressure/
shedding), 19 (golden signals, tracing the straggler, error budget), 20 (hedged/tied requests,
partial results, degrade, choose-C-over-A, blast radius).

## 6. Build-your-own targets
- **Design canvas**: the 6-step method as a fill-in template (requirements -> back-of-envelope ->
  model/API -> bottleneck -> primitives w/ cross-links -> failure modes + tradeoffs).
- **Back-of-envelope calculator**: input DAU/ratios/sizes -> QPS, storage/yr, shard count, cache
  size, fan-out tail (wraps `_recompute.py`'s formulas).
- **Mini-implementations**: a KGS + redirect cache (URL); a push/pull/hybrid fan-out simulator
  (feed); a per-conversation sequenced log with dedup (chat); a scatter-gather with hedged requests
  + partial results (search); an idempotent double-entry ledger with saga compensation (payments);
  a token-bucket limiter with cell-based batching (limiter, ties to the 18 lab).

## 7. Open questions / gaps (carry-forward `[UNVERIFIED]` — do NOT harden into prose)
- **Community design idioms (no single canonical primary):** KGS key-gen (URL); push/pull/hybrid
  feed (Twitter/IG eng blogs); chat protocols (websocket/XMPP/MQTT) + vendor chat designs
  (WhatsApp/Signal); search-engine internals (Lucene/Elasticsearch/BM25 — Appendix-P candidate);
  payment-system designs (Stripe/Square ledger talks); GCRA + vendor rate-limiter posts. All
  MECHANISMS are grounded in line-verified 06-20; only the *attribution to a specific external
  write-up* is unverified.
- **Carried from home sub-courses (still relevant if 21 ever needs them in prose):** Skeen 1981 3PC
  + Berenson 1995 ANSI isolation (11); Sagas SIGMOD 1987 (14); Dynamo (have it) for PA/EL framing.
- **NEWLY UNBLOCKED + verified this session:** Gilbert-Lynch formal CAP + Abadi PACELC (also upgrade
  11 + 15). NEWLY 200 but deferred to next session's opportunistic pass: arxiv.org,
  kafka.apache.org, postgresql.org.
- **Still blocked (retried):** CoDel (queue.acm.org 403), raft.github.io (000), dl.acm.org DOI (403)
  — all non-load-bearing for 21 (covered via 18/SEDA and Lamport primaries in 11/12).

---
**Part II (System Design, 13-21) is COMPLETE.** All eight primitive sub-courses (13-20) plus the
capstone application course (21) are reconciled + factchecked, math recomputed, primaries anchored.
Next batch: **Part III — Agentic System Design (22-the-agent-loop onward)**.
