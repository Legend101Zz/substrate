# 21 · Case study — URL shortener (write-once, read-heavy)

> Phase-1 brief (NO course prose). Bespoke per-case-study walkthrough. Math RECOMPUTED in
> `_recompute.py` (Case 1). Canon REUSED from line-verified 13-20 + 06; primaries flagged.
> This is the simplest capstone case: it exercises key generation (14), read-heavy caching
> (16), and storage sizing (13) with almost no consistency tax.

## 1. Requirements
- **Functional:** create a short code for a long URL; redirect `GET /{code}` -> 301/302 to the
  original; optional custom alias; optional expiry; click analytics (out of the hot path).
- **Non-functional:** redirect p99 < 50 ms (it sits in front of every click); very high read
  availability (a dead shortener breaks every link that uses it); durability of the mapping;
  codes never collide; codes are short.
- **Scale (RECOMPUTED, Case 1):** 100M new URLs/day -> **write ~1,157 QPS** (peak ~2,315);
  read:write = 100:1 -> **read ~115,741 QPS** (peak ~231k). 5-yr horizon -> **1.825e11 records**,
  **~91 TB** at 500 B/record.

## 2. Data model + API
- **Model:** `code (PK) -> {long_url, created_at, owner, expiry}`. This is a pure key-value lookup
  -> a KV store or a single-column-indexed table; no joins, no relations (reuse 14: data model =
  access-pattern contract; the access pattern is point-get by `code`).
- **API:** `POST /urls {long_url, alias?, ttl?} -> {code}`; `GET /{code} -> 301 Location`.
- **Key generation — the one real design decision:**
  - **Hash-of-URL (e.g. base62 of a truncated hash):** deterministic, dedups identical URLs, but
    must handle truncation collisions (check-and-retry or salt). 
  - **KGS (Key Generation Service) — counter/range-allocated IDs encoded base62:** pre-mint unique
    keys in ranges handed to app servers; no collision check on the hot path. Reuse 14 (ID
    allocation / range partitioning) + 11 (a counter is a tiny consensus/lease problem).
  - **Length math (RECOMPUTED):** base62^6 = **56.8B** codes; base62^7 = **3.52e12**. At 100M/day,
    5 yr = 1.825e11 records = **5.2% of base62^7** (safe) but **3.2x over base62^6** (overflows).
    -> **7 chars** is the right floor.

## 3. Bottleneck analysis
- The system is **overwhelmingly reads** (100:1). The redirect path is the bottleneck, and it is a
  cache problem, not a DB problem.
- Hot-set is tiny: cache the **top ~10M codes/day** at 500 B = **~5 GB** (RECOMPUTED) -> fits in
  RAM on a single cache tier; CDN/edge can serve 301s for the hottest links without touching the
  origin at all (reuse 16: placement ladder + a redirect is cacheable).
- With a **90% hit ratio**, origin read load = (1-h)·reads = **~11,574 QPS** (RECOMPUTED; reuse 16
  origin-load = (1-h)). 99% hit -> ~1,157 QPS. The cache, not the DB, sets the scaling story.

## 4. Design + cross-links to 13-20
- **13:** the back-of-envelope above is the whole sizing argument; redirect latency budget drives
  the cache decision.
- **14:** partition the `code` keyspace by hash of code (uniform, point-gets) — no hot shard
  because reads spread across a huge key space (unlike the feed). KGS uses range allocation.
- **15:** mapping is **write-once, never updated** -> consistency is trivial; async replication /
  read replicas are fine (a brand-new code not yet replicated 301s from the primary or is created
  read-through). This is the *easiest* possible consistency case — contrast with payments (Case 5).
- **16:** the core of the design — CDN + cache-aside on `code`; immutable values mean **infinite
  TTL** (no invalidation problem) until expiry; negative-cache unknown codes to blunt scans.
- **17:** click analytics is **fire-and-forget** onto a queue/log (never block the redirect);
  aggregated downstream (reuse 09/17). Expiry is a lazy/async sweep.
- **18:** rate-limit `POST /urls` per API key (abuse/spam control) — direct hand-off to Case 6.
- **19:** redirect QPS, hit ratio, p99, 4xx (unknown code) as the golden signals (reuse 19).
- **20:** read path must survive a DB outage -> serve from cache/CDN (stale-but-correct because
  immutable) = graceful degradation; the cache *is* the resilience story.

## 5. Failure modes (20)
- **Cache cold-start / flush:** origin sees the full 115k QPS -> size the DB read tier for the
  uncached worst case OR warm the cache; coalesce (16 stampede) so a popular cold key doesn't
  trigger a herd.
- **KGS outage:** app servers hold a pre-fetched key range -> keep redirecting and minting from
  the local range (no hard dependency on KGS per request); replenish async.
- **Collision (hash mode):** check-and-set on insert; on collision, re-salt and retry.
- **Hot link (one viral URL):** served entirely from CDN/edge -> not a hot shard for reads
  (contrast feed celebrity); the only hot spot is analytics writes -> absorb on the queue.

## 6. Tradeoffs
- **Hash vs KGS:** hash dedups + is stateless but needs collision handling; KGS is collision-free
  + sequential but adds a (cheap, range-leased) coordination dependency. Most large systems use
  **KGS-style range allocation** to keep the hot path collision-free.
- **301 vs 302:** 301 (permanent) is cacheable by browsers -> fewer origin hits but **kills click
  analytics** (browser never re-asks); 302 (temporary) preserves analytics at the cost of more
  redirects. Classic correctness-vs-measurability trade (ties to 19).
- **Custom alias:** human-chosen aliases reintroduce collisions + a uniqueness check on the write
  path (small QPS, acceptable).

## 7. Sources / gaps
- **REUSED (line-verified):** 13 (back-of-envelope, latency budget), 14 (KV model, keyspace
  partitioning, ID allocation), 15 (write-once = trivial consistency, read replicas), 16
  (cache-aside, CDN, origin-load (1-h), stampede coalescing, negative caching, immutable=infinite
  TTL), 17 (fire-and-forget analytics), 18 (write-path rate limiting), 19 (golden signals), 20
  (degrade-to-cache), 06 (base62 encoding / hashing).
- **RECOMPUTED:** all QPS, keyspace (62^6/62^7), 5-yr fill %, storage, cache size, origin load.
- **`[UNVERIFIED]`:** no design-specific external primary needed beyond reused canon; the
  "KGS" pattern is a community design idiom (Grokking/DDIA-adjacent) with no single canonical
  paper — flagged as idiom, mechanisms grounded in 11/14.
