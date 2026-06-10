# 16 — caching-and-cdn-strategies — Cluster A: cache placement + read/write patterns

> **Phase 1 research brief (NO course prose).** Briefs only per RESEARCH_PROTOCOL. Standard six
> sections. Cited primary sources are network-blocked this session (HTTP 000 on every non-Lamport
> host, 8th consecutive session) and are flagged `[UNVERIFIED from fetched source]`; mechanisms are
> verified by REUSE of line-checked 08/06/13/14/15, and any math by recomputation.
>
> Cluster scope: where a cache physically sits (the placement ladder) and the contract each layer
> signs with the read path and the write path (cache-aside / read-through / write-through /
> write-back / write-around). This is the entry cluster — it frames what 16 caches and why before B
> (sizing), C (consistency), and D (CDN/edge) deepen each axis.

---

## 1. Key mechanisms

### 1.1 A cache is bounded faster memory in front of slower truth — the same trade as 08

08 §1.1 already established the invariant and 16 inherits it verbatim: a cache buys latency and
origin protection **only** by choosing what to remember, when to forget, and how much staleness the
system tolerates. 16's job is to take that single-box trade and stretch it across a *distributed*
topology — many caches, many layers, one source of truth — and to reconcile it with the read-scale
and staleness pressures that 13 (X-axis read-scale), 14 (hot shards / Zipf skew) and 15 (read
replicas, replication lag, the staleness ladder) hand off.

### 1.2 The placement ladder — where a cache can sit, request-order, near→far from the user

Reads flow down this ladder until one layer answers; the closer the hit, the cheaper the request.
Each rung is a cache with its own lifetime + invalidation contract:

1. **Client / browser cache** — in the user's process. Governed by HTTP `Cache-Control`/`Expires`/
   `ETag` (08 §1.7, RFC 9111 `[UNVERIFIED]`). Zero network cost on a hit; totally uncontrollable
   once shipped (you cannot purge a browser) — only TTL + validators bound staleness.
2. **CDN / edge PoP** — a shared HTTP cache geographically near the user (Cluster D). Absorbs read
   fan-out for static + cacheable dynamic content before it crosses the backbone.
3. **Reverse-proxy / gateway cache** — nginx/Varnish in front of the app tier (reuse 10:
   event-driven reverse proxy, `proxy_cache`). Shared across all users of one origin region.
4. **Application / in-process cache** — a local map (Caffeine W-TinyLFU, 08 §1.5) inside the service
   process. Nanosecond hits, but *per-instance* — N app instances ⇒ N independent caches ⇒ N-fold
   duplication + N independent invalidation surfaces.
5. **Distributed / remote cache tier** — Redis/Memcached (08 entire) shared by all app instances.
   One coherent cache, but a network hop (sub-ms LAN, 13 latency hierarchy) and its own scaling/
   sharding (14) + replication (15) story.
6. **Database-side caches** — buffer pool / page cache (07), materialized views, query-result cache.
   The last cache before disk; owned by the engine, not the app.

The ladder is the read path's miss chain: client miss → CDN miss → proxy miss → app-local miss →
remote-cache miss → DB buffer miss → disk. Each rung multiplies effective capacity and divides
origin load, at the cost of one more place a stale copy can live (Cluster C's problem).

### 1.3 Inclusive vs exclusive multi-layer caching, and the duplication tax

Stacking caches is not free coherence. Two layers caching the *same* hot key (e.g. app-local +
remote) is **inclusive** duplication: it doubles freshness surface and can serve two different
stale values. Practical multi-tier designs either (a) keep a tiny near cache for the hottest keys
(Zipf head, 14) over a large shared cache for the long tail, accepting bounded near-cache staleness
with short TTL, or (b) make the near cache write-through to / invalidated-by the shared tier. The
near/far split is the same head/tail logic as W-TinyLFU's window vs main (08 §1.5), now spanning
machines.

### 1.4 The five write/read patterns — who writes the cache, and when

The pattern is the *contract* between the cache, the application, and the source of truth (SoT).
08 §1.1/§1.7 anchored cache-aside from the Facebook Memcache paper and flagged the others as needing
stronger taxonomy sources; 16 owns the full taxonomy as the load-bearing teaching unit.

- **Cache-aside (lookaside / lazy loading).** App owns the cache. **Read:** check cache; on miss,
  read SoT, populate cache, return. **Write:** write SoT, then *invalidate* (delete) the cache key.
  Cache holds only what was actually requested (demand-filled). Failure mode: the stale-fill race
  (08 §1.7) — a concurrent reader can repopulate the old value between the SoT write and the delete.
  This is the Memcache-paper default and the most common pattern. `[UNVERIFIED: Nishtala NSDI 2013]`.
- **Read-through.** Cache sits *inline*; app talks only to the cache, which fetches from SoT on miss
  via a loader. Same population timing as cache-aside but the cache (not app code) owns the miss
  path — centralizes the loader, removes duplicated read logic. (Caffeine `LoadingCache`,
  08 reuse.)
- **Write-through.** **Write:** app writes the cache, cache synchronously writes SoT before acking.
  Cache and SoT are always in lock-step on the write path ⇒ no stale-fill on the written key, at the
  cost of write latency = cache + SoT. Pairs with read-through. Does NOT pre-warm reads unless
  combined with population.
- **Write-back (write-behind).** **Write:** app writes the cache, cache acks immediately, flushes to
  SoT asynchronously (batched/coalesced). Lowest write latency + write coalescing for hot counters,
  but **acks data not yet durable in SoT** — a cache crash loses the un-flushed window. This is the
  cache analogue of 15's async replication lost-write window, and of 07's WAL/buffer-flush ordering.
- **Write-around.** **Write:** app writes SoT directly and does *not* populate the cache (the key is
  filled later by a normal read miss, or never). Keeps write-once / rarely-read data from polluting
  the cache (the admission intuition of 08 §1.5, applied to the write path). Pairs with cache-aside
  reads.

### 1.5 The read path and the write path are different problems

Reads are about *placement + hit ratio* (Clusters A/B): make the answer close and resident. Writes
are about *consistency timing* (Cluster C): when does the cached copy stop telling the old story.
The five patterns are exactly the cross-product of "does the write touch the cache?" (through/back =
yes, aside/around = invalidate-or-ignore) and "is the SoT write synchronous?" (through = sync,
back = async). Picking a pattern = picking where you pay: write latency, durability window, or
stale-read risk.

### 1.6 Why caching is the natural sink for 14's hot keys and 15's read pressure

14 ends with hot shards / celebrity keys (Zipf head) that no shard-key choice can spread, and 15
ends with read replicas that scale reads only by accepting replication lag (staleness). A cache in
front of both is the shared mitigation: it absorbs the hot-key read fan-out **before** it reaches
the shard or replica (so one Justin-Bieber row is served from cache, not from a melting shard), and
it is itself "yet another replica" whose staleness is governed by TTL/invalidation instead of a
replication log. Cluster B quantifies how well (hit ratio under Zipf); Cluster C governs how stale.

## 2. Foundational sources (consolidated)

**Verified by REUSE (line-checked earlier, NOT re-fetched this session):**
- Cache = bounded faster memory; eviction/admission forced by finite memory; cache-aside shape;
  stale-fill race; TTL = logical invalidity before reclamation; write-through/write-back caveats —
  08 `_research.md` §§1.1–1.7 (+ 08 `_factcheck_phase1.md`).
- In-process W-TinyLFU near cache (window vs main = head vs tail) — 08 §1.5 (Caffeine line anchors).
- Reverse-proxy `proxy_cache` / event-driven proxy — 10 `_research_event-driven-reverse-proxy.md`
  (NGINX `release-1.31.1`).
- Latency hierarchy (process ns vs LAN sub-ms vs cross-region ms) governing the ladder rungs;
  X-axis read-scale — 13 `_research.md` (+ clusters).
- Hot shards / celebrity keys / Zipf skew that the cache absorbs — 14 `_research.md` §§ hot-shard.
- Read replicas scale reads not writes; replication lag = staleness; the staleness ladder —
  15 `_research.md` (Clusters A/B).

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when net heals):**
- Nishtala et al. "Scaling Memcache at Facebook" NSDI 2013 (cache-aside/lookaside default + leases),
  already carried in 08. URL: `https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf`.
- RFC 9111 HTTP caching semantics (client/proxy/CDN freshness, `Cache-Control`, `Age`, validators)
  — `https://www.rfc-editor.org/rfc/rfc9111.txt` (carried in 08; load-bearing for Cluster D).
- Pattern-taxonomy primary anchors for read-through / write-through / write-back / write-around
  (vendor docs: AWS caching whitepaper, Oracle Coherence, Ehcache, Caffeine `CacheLoader`/
  `CacheWriter` docs). All HTTP 000 this session.

## 3. "Why it's this way" — the forcing functions

- **There is no single best place to cache** because the latency hierarchy (13) is a ladder: each
  rung trades reach (how many users share it) against proximity (how cheap the hit). You cache at
  *several* rungs because no one rung is both close to every user and coherent across all of them.
- **Per-instance app caches duplicate** because process memory is not shared; the remote tier exists
  precisely to trade a network hop for one coherent copy. Choosing app-local vs remote is choosing
  proximity vs coherence — the same near/far tension as W-TinyLFU's window (08).
- **The five patterns exist because reads and writes have different costs.** You cannot simultaneously
  minimize write latency, guarantee durability, and guarantee no stale reads — write-through buys
  freshness with latency, write-back buys latency with a durability window, cache-aside buys
  simplicity with a stale-fill race. Conservation of pain, identical in shape to 15's
  durability-vs-latency dial.
- **Demand-fill (cache-aside) wins by default** because you cannot afford to cache everything
  (caches are bounded, 08) and the working set you actually serve is far smaller than the keyspace
  (Zipf, Cluster B) — let traffic reveal the working set instead of guessing it.

## 4. Common misconceptions to preempt

- "Add a cache" = one box. No — caching is a *ladder* of layers, each with its own lifetime +
  invalidation contract; the bug is usually a layer you forgot you had (the browser, the CDN).
- "More cache layers = more correct." More layers = more places a stale copy lives ⇒ *harder*
  coherence (Cluster C). Layers help latency, not consistency.
- "Cache-aside and read-through are the same." Same population timing; different owner of the miss
  path (app vs cache) ⇒ different failure surface and different code.
- "Write-through makes everything consistent." It only keeps the *written* key in lock-step with SoT;
  other replicas/layers (browser, CDN, peer app instances) are still governed by their own TTLs.
- "Write-back is just a faster write-through." It acks data not yet durable in SoT — a cache crash
  loses the un-flushed window (the cache analogue of 15 async lost-writes).
- "App-local caching is always fastest, so always use it." It is fastest *per hit* but per-instance ⇒
  duplication + N invalidation surfaces; for shared mutable state the remote tier is usually correct.
- "The cache is the source of truth." Only write-back blurs this, and only transiently; for every
  other pattern the SoT is authoritative and the cache is a disposable accelerator.

## 5. Best build-your-own target(s)

- **Pattern bake-off harness:** one key-value SoT (sqlite, reuse 07) + a toy cache; implement all
  five patterns behind one interface; drive a read/write mix and measure read latency, write
  latency, durability window (kill the cache mid-write-back), and stale-read count (concurrent
  writer + reader to expose the cache-aside stale-fill race). Makes §1.4/§1.5 tangible.
- **Placement-ladder simulator:** model client→CDN→proxy→app-local→remote→DB rungs with the 13
  latency hierarchy as per-rung costs; replay a Zipf trace (Cluster B) and report hit ratio + mean
  latency per rung and end-to-end. Shows why you cache at several rungs.
- **Near/far two-tier cache:** small per-instance W-TinyLFU window over a shared Redis-style tier;
  measure duplication and the inclusive-staleness window vs a single shared tier. Pairs 08.

## 6. Open questions / gaps to close (preserved)

- Pattern-taxonomy attributions (read-through/write-through/write-back/write-around) still lack a
  fetched primary — carried from 08 §6, still HTTP 000 this session. Teach the mechanism (verified by
  reuse + first-principles); do NOT pin a canonical source name into Phase-2 prose until fetched.
- Nishtala NSDI 2013 + RFC 9111 carried `[UNVERIFIED]` from 08; both needed before D hardens.
- Boundary: cache *eviction/admission internals* (slabs, sampled LRU, TinyLFU) live in 08/appendix
  G — 16 reuses, does not re-derive. Distributed-cache *sharding/replication* of the remote tier =>
  14/15, not re-taught here.
- Decision deferred to Cluster C: exact stale-fill mitigation (lease vs CAS vs delayed double-delete)
  for cache-aside writes.
