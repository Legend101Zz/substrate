# 08 — Caches and Storage Systems · _structure.md

**Identity:** how to put bounded, faster memory in front of slower truth without lying to
your users. The discipline of remembering, forgetting, and tolerating staleness.

**Bespoke shape — "the five forced questions of any cache."** NOT a tour of products. Every
cache, from a CPU line to a CDN, must answer the SAME five questions, and the sub-course is
organized as those questions in order: **(1) what do I store & where? (2) when do I forget
it — expiry? (3) when do I evict under pressure — and should I even admit it? (4) how do I
stop a hot miss from stampeding the origin? (5) how do I stay correct under writes &
regions?** Each chapter answers one question with the clean trade first, then two real
instantiations (Redis + Memcached source, HTTP/CDN RFCs). The opening states the master
trade: memory + freshness + coordination cost vs latency + backend protection.

## Dependency position
- **Depends on:** 04 (page cache, memory pressure), 06 (eviction structures, ring buffers,
  TinyLFU sketch ↔ count-min), 07 (the buffer pool is a cache with extra invariants — direct
  contrast), 03 (HTTP semantics for the CDN chapter).
- **Feeds into:** 16 (caching-and-cdn-strategies = the system-design application of this),
  09 (page-cache-friendly log), 24/25 (prompt/memory caching reuse stampede + TTL ideas),
  32 (prefix-cache economics).
- **Appendix links DOWN:** G-redis-internals (the single-threaded machine: encodings,
  expiry, eviction, persistence in full), F (buffer-pool contrast). 08 teaches the cache
  concept; G is the Redis deep-dive.

## Chapter specs (3–5 lines each)
0. **What a cache actually buys you** (short opener) — the master trade; the four
   dimensions (placement / lifetime / write contract / correctness). "Cache good" is not a
   design — naming the cost is. Frames the five questions.
1. **Placement & write contracts** — client / service / distributed KV / HTTP intermediary
   / CDN; lookaside (cache-aside) vs write-through vs write-back/behind. Only cache-aside is
   strongly primary-anchored (FB Memcache) — flag the others as taxonomy needing sources.
   Why write-back can ack data not yet durable.
2. **Expiration — logical invalidity ≠ physical reclamation** — TTL makes a key invalid at
   T; memory is reclaimed lazily/actively. Redis: `expires` kvstore + active-expire cycle
   (20 keys/loop, 25% CPU budget, 10% stale baseline, effort tuning). Memcached:
   exptime=0=never, relative vs absolute, coarse time granularity surprises.
3. **Eviction — approximate choice under pressure** — exact global LRU/LFU is too expensive.
   Redis sampled pool (EVPOOL_SIZE=16, maxmemory-samples) scoring LRU/LFU(255−decr)/TTL;
   policies (volatile/allkeys × LRU/LFU/random + noeviction). Memcached slab classes +
   HOT/WARM/COLD/TEMP segmented LRU + maintainer/automove. Approximation is the point.
4. **Admission — should this miss even get space?** — eviction picks a victim; admission
   decides if a candidate deserves entry. Scan pollution motivates it. TinyLFU (approx
   frequency + Doorkeeper Bloom), W-TinyLFU (small LRU window: PERCENT_MAIN=0.99,
   protected=0.80), Caffeine 4-bit FrequencySketch (max 15, aging at 10×maxSize). ARC's
   recency/frequency + ghost lists. Math → N/06.
5. **Dogpile / stampede — coordinate the refill** — one hot expiry → N origin calls.
   Leases (FB Memcache: 64-bit token, first-miss fills; 17K/s→1.3K/s DB query rate);
   singleflight (dedups concurrent work — NOT a cache); stale-while-revalidate /
   stale-if-error (RFC 5861, bounded stale serving). XFetch probabilistic early expiry is
   NOT primary-sourced — don't teach the formula.
6. **Consistency — invalidation, validation, stale-fill races** — lookaside race: reader
   misses, writer updates DB + deletes cache, reader refills stale. Guards: leases / CAS-
   version / short TTL / delayed double-delete / source validation (workload-specific).
   HTTP is better standardized: RFC 9111 (Vary cache key, freshness, Age, ETag/304,
   collapsed forwarding, invalidation after unsafe methods). FB multi-region delete streams.
7. **Persistence — when a cache becomes a store** — Redis: none / RDB point-in-time (fork,
   can lose between snapshots) / AOF (appendfsync always|everysec|no; 7.0 multi-part +
   manifest) / combined. Persistence changes RECOVERY, not all consistency/query/ops
   tradeoffs — it doesn't make Redis a free database. → G.

## Paired build labs (/build → own-cache, parts of own-redis)
TTL cache (hashmap + expires + read-time + active-expiry sampling) → approximate Redis-style
eviction (sampled pool LRU/LFU/TTL vs exact LRU) → Memcached slab allocator (size classes,
perslab, internal-frag report) → segmented LRU (HOT/WARM/COLD + maintainer) → CAS cache API
(gets token + cas, reject stale write) → TinyLFU gate (4-bit sketch + aging + scan-pollution
benchmark) → W-TinyLFU toy → singleflight/dogpile demo (N misses → 1 fetch) →
stale-while-revalidate middleware → Redis-lite persistence (AOF + snapshot, measure fsync).

## Diagrams needed
- The five-questions map (placement→expiry→eviction/admission→stampede→consistency).
- Cache-aside vs write-through vs write-back sequence (where the ack happens, durability gap).
- Redis active-expire cycle (sample → spend-more-if-stale-high) loop.
- Sampled eviction pool (sample k → pool of 16 → evict best score).
- Memcached slabs (size classes + segmented LRU) — contrast with Redis single heap.
- Admission gate: TinyLFU sketch deciding candidate vs victim; W-TinyLFU window→main.
- Stampede: N concurrent misses → leases/singleflight collapsing to 1 origin call.
- Lookaside stale-fill race timeline + the guard that fixes it.

## Sources / gaps to honor (from _research.md)
- Pin Redis/Memcached source to release tags/commit SHAs before chapter prose.
- `[UNVERIFIED]`/needs-source: write-through/write-back taxonomy (stronger primary needed);
  ARC exact pseudo-code/p-adjustment/patent status; count-min error bounds (Cormode-
  Muthukrishnan); XFetch probabilistic early-expiry formula. Don't harden these.
- FB 2013 production numbers (17K→1.3K) are architecture evidence, not current capacity.
  Memcached meta-protocol stale flags are version-sensitive — pin release docs.
- Source-level Redis RDB/AOF tracing deferred to appendix G unless 08 needs it.
