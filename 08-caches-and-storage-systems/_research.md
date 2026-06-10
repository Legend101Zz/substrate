# Reconciled Research Brief — 08 Caches and Storage Systems
## Phase 1 corpus synthesis | Date: 2026-06-10

Cluster briefs reconciled:
- `_research_cache-eviction-consistency.md`
- `_research_memcached-internals.md`
- `_research_admission-dogpile-consistency.md`
- `_factcheck_phase1.md`

This is a research brief only. No chapters, no Phase 2 structure.

---

## 1. Key Mechanisms

### 1.1 Cache role: bounded, faster memory in front of slower truth

A cache improves latency and origin load only by choosing what to remember, when to forget it, and how much
staleness the system can tolerate. The fundamental trade is not “cache good”; it is memory + freshness +
coordination cost versus latency + backend protection.

Common dimensions:
- **Placement:** client-side, service-side, distributed key/value cache, HTTP intermediary, CDN.
- **Lifetime:** explicit invalidation, TTL/expiry, memory-pressure eviction, stale serving windows.
- **Write contract:** lookaside/cache-aside, write-through, write-back/write-behind. The pattern names are
  useful taxonomy, but only cache-aside/lookaside is strongly anchored in this pass by the Facebook Memcache
  paper; write-through/write-back still need stronger primary taxonomy sources.
- **Correctness:** stale reads, stale fills, duplicate refills, lost writes, and multi-region invalidation are
  application-visible behaviors, not implementation trivia.

### 1.2 Expiration: logical invalidity before physical reclamation

TTL makes a key invalid after time T, but memory reclamation is usually lazy/incremental.

**Redis:** `redisDb` has `kvstore *keys` and `kvstore *expires` in `server.h`. `expire.c` defines active
expiration constants: `ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP = 20`, fast duration `1000` microseconds, slow CPU
budget `25%`, and acceptable stale baseline `10%`. `activeExpireCycle()` samples expiry metadata and spends
more work when the expired/stale percentage is high; `active_expire_effort` adjusts the baseline parameters.
Source: `https://raw.githubusercontent.com/redis/redis/unstable/src/server.h`,
`https://raw.githubusercontent.com/redis/redis/unstable/src/expire.c`.

**Memcached:** `exptime=0` means never expire; otherwise expiration can be relative seconds or absolute Unix
time. `touch`, `gat`, and `gats` update/fetch expiration. Internal time granularity is coarse enough that very
low TTLs can surprise users. Source: `https://raw.githubusercontent.com/memcached/memcached/master/doc/protocol.txt`.

### 1.3 Eviction: approximate choice under memory pressure

Exact global LRU/LFU is often too expensive for high-throughput caches. Real systems use approximations.

**Redis:** `server.h` defines maxmemory policies: volatile/allkeys LRU, LFU, random, TTL-only, noeviction, and
newer LRM variants. `evict.c` uses a candidate pool (`EVPOOL_SIZE = 16`) populated by sampling up to
`server.maxmemory_samples` keys. LRU/LRM score by idle time, LFU uses inverse frequency (`255 - LFUDecrAndReturn`),
and TTL policy scores by expiry time. Official Redis eviction docs call LRU/LFU approximated and expose
`maxmemory-samples`. Sources: Redis `server.h`, `evict.c`, and
`https://redis.io/docs/latest/develop/reference/eviction/`.

**Memcached:** memory is partitioned into slab classes and eviction happens within class/LRU structures, not one
monolithic heap. `items.c` uses HOT/WARM/COLD/TEMP LRU segments, `lru_pull_tail()` as the central reclaim path,
and `lru_maintainer_thread()` to rebalance/clean in the background. Source:
`https://raw.githubusercontent.com/memcached/memcached/master/items.c`.

### 1.4 Allocation: slabs and optional external storage

Memcached’s slab allocator creates fixed-size chunk classes with `perslab = slab_page_size / class_size`.
This reduces external fragmentation and allocator overhead for millions of variable-sized items, at the cost
of internal fragmentation and class imbalance. `slab_automove.c` samples stats and can move pages between
classes when workload sizes shift. Sources: `slabs.c`, `slab_automove.c` in `memcached/memcached`.

Extstore optionally moves cold value bytes out of DRAM while keeping key/header metadata resident. `doc/storage.txt`
describes `ITEM_HDR`, async reads, and IO-thread callbacks; `extstore.c` implements page/bucket IO threads and
page lifecycle operations. This is capacity extension, not a database durability contract.

### 1.5 Admission: prevent scans from entering the cache

Eviction and admission are separate. Eviction picks a resident victim; admission decides whether a miss deserves
space. TinyLFU uses approximate recent frequency to reject one-time scan items; W-TinyLFU adds a small LRU window
so newly hot items can build evidence before competing with main-cache residents.

Primary findings:
- TinyLFU paper: approximate frequency admission over a recent sample; Doorkeeper Bloom filter avoids spending
  multi-bit counters on first-time tail items. Source: `https://arxiv.org/abs/1512.00727`.
- Caffeine `FrequencySketch`: 4-bit CountMinSketch, max counter 15, reset/aging at `10 * maximumSize`, reset mask
  `0x7777777777777777L`. Source: `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/FrequencySketch.java`.
- Caffeine W-TinyLFU: `PERCENT_MAIN = 0.99d`, `PERCENT_MAIN_PROTECTED = 0.80d`, candidate/victim admission, and
  hash-DOS randomness threshold in `BoundedLocalCache.java`.
- ARC: FAST 2003 ARC uses recency/frequency lists plus ghost history to adapt the split. Mechanism verified from
  extracted USENIX PDF, but exact pseudo-code/patent status needs deeper pass before teaching in detail.

### 1.6 Dogpile prevention: coordinate refill, not just storage

A hot key expiry can turn one miss into N concurrent origin calls.

Mechanisms:
- **Leases:** Facebook Memcache gives the first miss client a 64-bit token; only that client may fill successfully
  if no invalidation intervened. The NSDI paper reports a herd-prone key set with peak DB query rate 17K/s without
  leases versus 1.3K/s with leases. Source: Nishtala et al. NSDI 2013.
- **Singleflight:** Go `x/sync/singleflight` suppresses duplicate concurrent calls per key and shares the result,
  but it is not a cache: after the function returns, the in-flight entry is removed. Source:
  `https://raw.githubusercontent.com/golang/sync/master/singleflight/singleflight.go`.
- **Stale-while-revalidate / stale-if-error:** RFC 5861 permits bounded stale serving while revalidation happens
  or when origin errors occur. Source: `https://www.rfc-editor.org/rfc/rfc5861.txt`.

### 1.7 Consistency: invalidation, validation, and stale-fill races

Facebook’s Memcache paper anchors the common lookaside shape: web servers read memcache first, query MySQL on
miss, set cache after fetching, and delete/invalidate cache after writes. This creates races: a reader can miss,
a writer can update DB and delete cache, then the reader can refill stale data. Leases, CAS/version checks,
short TTLs, delayed double-delete, or source-of-truth validation are ways to constrain this race; the exact choice
is workload-specific.

HTTP cache semantics are better standardized. RFC 9111 defines cache keys (`Vary`), freshness, Age, validators
(`ETag`, `If-None-Match`, `Last-Modified`, `If-Modified-Since`), 304 revalidation, collapsed forwarding, stale
constraints, and invalidation after unsafe methods such as PUT/POST/DELETE.

### 1.8 Persistence: Redis changes the cache/database boundary

Redis can be an ephemeral cache or a durable-ish data store depending on persistence configuration:

- No persistence.
- RDB point-in-time snapshots.
- AOF append-only write log replayed on startup.
- Combined RDB+AOF.

Official docs describe RDB as compact/forked snapshots that can lose data between snapshots and pause during
large forks. AOF offers `appendfsync always`, `everysec`, and `no`; since Redis 7.0, AOF is multi-part with base
and incremental files tracked by a manifest. Source:
`https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/`.

---

## 2. Foundational Sources

### Redis
- `https://raw.githubusercontent.com/redis/redis/unstable/src/server.h` — maxmemory policies, `redisDb` keyspace/expires, LRU/LFU knobs.
- `https://raw.githubusercontent.com/redis/redis/unstable/src/evict.c` — sampled eviction pool, LRU/LFU/LRM/TTL scoring, `performEvictions()`.
- `https://raw.githubusercontent.com/redis/redis/unstable/src/expire.c` — active expiration constants and effort tuning.
- `https://redis.io/docs/latest/develop/reference/eviction/` — eviction policy docs, approximate LRU/LFU, `maxmemory-samples`, LRM note.
- `https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/` — RDB/AOF/fsync/rewrite/multi-part AOF.

### Memcached
- `https://raw.githubusercontent.com/memcached/memcached/master/doc/protocol.txt` — TTL, CAS, touch/gat/gats, meta protocol/stale metadata.
- `https://raw.githubusercontent.com/memcached/memcached/master/slabs.c` — slab classes, chunk sizing, allocation.
- `https://raw.githubusercontent.com/memcached/memcached/master/items.c` — HOT/WARM/COLD/TEMP LRU, maintainer, crawler, eviction path.
- `https://raw.githubusercontent.com/memcached/memcached/master/slab_automove.c` — slab automove.
- `https://raw.githubusercontent.com/memcached/memcached/master/thread.c` — worker threads and item locks.
- `https://raw.githubusercontent.com/memcached/memcached/master/doc/storage.txt` and `extstore.c` — external storage.
- `https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf` — Scaling Memcache at Facebook.

### Admission / dogpile / HTTP caching
- `https://arxiv.org/abs/1512.00727` — TinyLFU and W-TinyLFU.
- `https://raw.githubusercontent.com/wiki/ben-manes/caffeine/Efficiency.md` — Caffeine W-TinyLFU overview and comparisons.
- Caffeine `FrequencySketch.java`, `BoundedLocalCache.java`, simulator `TinyLfu.java` — implementation anchors.
- `https://www.usenix.org/legacy/events/fast03/tech/full_papers/megiddo/megiddo.pdf` — ARC.
- `https://raw.githubusercontent.com/golang/sync/master/singleflight/singleflight.go` — request collapsing.
- `https://www.rfc-editor.org/rfc/rfc5861.txt` — stale-while-revalidate and stale-if-error.
- `https://www.rfc-editor.org/rfc/rfc9111.txt` — HTTP caching semantics.

---

## 3. Why It’s This Way — Constraints

- **Caches are bounded.** Every cached byte competes with another; eviction/admission are forced by finite memory.
- **Exact metadata is expensive.** Exact LRU/LFU across millions of keys increases CPU, lock contention, and memory.
- **Expired cold keys still occupy RAM.** Active expiration/crawlers exist because read-time expiry alone misses cold dead entries.
- **Variable object sizes fragment memory.** Slabs trade external fragmentation for internal fragmentation and rebalance needs.
- **Hot expiry synchronizes clients.** Leases/singleflight/stale serving reduce duplicate origin work.
- **Freshness is not free.** Stronger write synchronization increases write latency and failure coupling.
- **Durability changes the product.** Redis persistence makes recovery possible but introduces fork/fsync/rewrite operational costs.
- **Regions add lag.** Facebook’s multi-region memcache design accepts transient stale reads and uses delete streams/markers because cross-region synchronous invalidation would be too slow and fragile.

---

## 4. Misconceptions to Preempt

1. **“TTL deletes memory at exactly T.”** It usually makes the item logically invalid; physical removal is lazy/active.
2. **“LRU means perfect global LRU.”** Redis and Memcached use approximations/segments/sampling.
3. **“Eviction and admission are the same.”** Admission rejects bad candidates before they pollute the cache.
4. **“Memcached is just a hashmap.”** Slabs, segmented LRU, CAS, threading, crawler, and protocol semantics are core.
5. **“Singleflight caches values.”** It only deduplicates concurrent work.
6. **“Stale-while-revalidate gives strong freshness.”** It explicitly permits bounded stale responses.
7. **“Persistence makes Redis a free database replacement.”** Persistence changes recovery, not all consistency/query/ops tradeoffs.
8. **“Cache invalidation after write is enough.”** Concurrent stale refill can reintroduce old data unless guarded.
9. **“Write-back is just faster.”** It can acknowledge data that is not yet durable in the source of truth.

---

## 5. Build-Your-Own Targets

1. **TTL cache:** hashmap + expires map + read-time expiry + active expiry sampling loop.
2. **Approximate Redis-style eviction:** sampled candidate pool with LRU/LFU/TTL scoring; compare to exact LRU.
3. **Memcached slab allocator:** size classes, `perslab`, free lists, internal-fragmentation reporting.
4. **Segmented LRU:** HOT/WARM/COLD queues plus background maintainer tick.
5. **CAS cache API:** `gets` token + conditional `cas`; demonstrate stale-write rejection.
6. **TinyLFU gate:** 4-bit sketch + aging + candidate/victim comparator; run scan-pollution benchmark.
7. **W-TinyLFU toy:** LRU window + probation/protected main + TinyLFU admission.
8. **Singleflight/dogpile demo:** N concurrent misses collapse to one origin fetch.
9. **Stale-while-revalidate middleware:** bounded stale serving with background refresh.
10. **Redis-lite persistence:** append-only log + snapshot/rewrite toy; measure fsync tradeoffs.

---

## 6. Open Questions / Gaps

- Pin Redis and Memcached source citations to release tags or commit SHAs before Phase 2/chapter prose.
- Source-level Redis RDB/AOF implementation tracing is deferred to Redis appendix G unless spine 08 needs it.
- `write-through` and `write-back` taxonomy still need stronger primary/official anchors.
- ARC exact pseudo-code, p-adjustment, and patent/licensing status need a deeper pass if taught beyond mechanism level.
- Count-Min Sketch mathematical error bounds need the Cormode/Muthukrishnan paper or another primary source.
- Probabilistic early expiration/XFetch was not primary-sourced; do not teach exact formula yet.
- Facebook 2013 production numbers are architecture evidence, not current capacity claims.
- Memcached meta-protocol stale flag letters are version-sensitive; pin release docs before prose.
