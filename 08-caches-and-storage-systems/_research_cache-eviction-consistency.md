# Research Brief — Sub-course 08: Cache Architecture, Eviction, Consistency
## Source cluster: Memcached/Facebook, Redis source/docs, TTL/eviction/admission, cache consistency patterns
## Researcher: brain-manual (fallback after researcher `httpx.ReadError`) | Date: 2026-06-09

---

## 1. Key Mechanisms

### 1.1 Cache shape: key/value memory in front of slower truth

**Forcing constraint:** storage systems cannot make every read hit the database. A cache trades
freshness and memory for latency and load shedding: keep the hot working set in memory, miss to
slower storage, and decide what to evict when memory is full.

**Cache-aside baseline:** application reads cache first; on miss, it reads the backing store and
sets the cache. Writes update the database and then invalidate/update cache. This pattern is common
but not directly sourced to a primary implementation in this brief; treat exact pattern taxonomy
(`cache-aside`, `write-through`, `write-back`) as `[UNVERIFIED taxonomy]` until anchored in a
specific system document.

### 1.2 TTL and expiration: logical deletion before physical memory reclamation

TTL means an entry can be logically expired even if still present in memory. Reads must check expiry;
background maintenance eventually reclaims memory.

**Redis expiration model** (verified from source):
- `redisDb` has `kvstore *keys` for the keyspace and `kvstore *expires` for timeout metadata.
  Source: `src/server.h` lines around `typedef struct redisDb`.
- `activeExpireCycle()` is the incremental collector. Source comments say keys expire on access,
  but active expiration is needed so expired keys are eventually removed even when never read.
- Baseline active-expire constants: `ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP = 20`,
  `ACTIVE_EXPIRE_CYCLE_FAST_DURATION = 1000` microseconds, `ACTIVE_EXPIRE_CYCLE_SLOW_TIME_PERC = 25`,
  `ACTIVE_EXPIRE_CYCLE_ACCEPTABLE_STALE = 10`.
- Expire effort tunes how much CPU Redis spends on active expiration.

**Memcached expiration model** (verified from protocol docs):
- `exptime=0` means item never expires; nonzero expiration can be relative seconds or Unix time.
- Very low TTLs are rough because Memcached updates internal time on second boundaries; protocol docs
  warn TTL 1 can sometimes immediately expire.
- `touch` changes an existing item's expiration; `gat/gats` fetch and update expiration.
- `flush_all` invalidates existing items.

### 1.3 Eviction: choosing what to forget under memory pressure

**Redis maxmemory policy set** (verified from `src/server.h`):
- `volatile-lru`, `volatile-lfu`, `volatile-ttl`, `volatile-random`
- `allkeys-lru`, `allkeys-lfu`, `allkeys-random`
- `noeviction`
- Newer source also exposes LRM variants: `volatile-lrm`, `allkeys-lrm`.
- Flags distinguish LRU, LFU, allkeys, and LRM policy families. `lruclock` tracks logical LRU time;
  LFU has `LFU_INIT_VAL = 5`, `lfu_log_factor`, and `lfu_decay_time`.

**Important nuance:** Redis docs/source describe policies, but this brief has not yet traced the
exact sampled-eviction algorithm in `evict.c` end-to-end. Do not claim “true LRU” unless source
is traced; Redis eviction is known to be approximate/sampled, but exact current mechanics need a
follow-up source pass.

**Memcached eviction / allocation** (verified from source/docs):
- Memcached stores items in slab classes: `slabs.c` computes chunk sizes, items per slab, and per-class
  free lists. Slab allocation avoids general malloc fragmentation for many object sizes.
- `items.c` has segmented LRU structures: HOT, WARM, COLD, TEMP; `lru_pull_tail()` is used when
  memory pressure forces reclaim/eviction.
- Item stats track `evicted`, `expired_unfetched`, `evicted_unfetched`, `evicted_active`, and LRU
  maintenance counters.
- The protocol supports CAS tokens (`gets`/`cas`) and item metadata (`mg` flags can return TTL,
  CAS, hit/fetch status, size, and stale marker).

### 1.4 Admission and thundering herd control

Eviction asks “which existing item leaves?” Admission asks “should this new/missed item enter?”
Without admission control, one-time scans can evict the real hot set. This brief has not yet traced
TinyLFU/ARC/admission papers directly, so keep exact algorithm claims `[UNVERIFIED]` until sourced.

**Facebook Memcached paper status:** The NSDI 2013 PDF `memcache-fb` was fetched successfully
from USENIX, but this session lacked `pdftotext`; strings extraction did not reveal body text.
Known claims such as leases, stale sets, gutter pools, regional pools, and thundering-herd control
must remain `[UNVERIFIED from text]` until the PDF can be read directly.

### 1.5 Persistence and write paths

Caches range from purely ephemeral to durable-ish.

**Redis persistence docs (reachable):** Redis official docs page for persistence was fetched (HTTP
200). High-level Redis mechanisms to verify in a deeper pass:
- RDB snapshots: point-in-time compact snapshots.
- AOF: append-only command log with fsync policy and rewrite/compaction.
- Persistence choice changes cache semantics: ephemeral cache can drop data; Redis-as-primary-store
  needs durability and recovery settings.

**Memcached:** protocol/source in this pass focus on in-memory items/slabs/LRU. `doc/storage.txt`
describes an external storage design with items moved to storage and recached on repeated hits, but
that is not the baseline in-memory mental model. Treat Memcached as primarily an in-memory cache
unless the storage-extension path is explicitly included and sourced.

### 1.6 Cache consistency and stale reads

Every cache coherence design chooses where staleness can appear:
- **Invalidate-after-write:** write DB, delete cache key. Race: a read miss may refill stale data if it
  overlaps the write. Needs ordering, leases, version checks, or delayed double-delete. `[UNVERIFIED taxonomy]`
- **Write-through:** write cache and DB synchronously. Lower staleness, higher write latency and more failure modes. `[UNVERIFIED taxonomy]`
- **Write-back:** write cache first, flush DB later. Fast writes but durability risk if cache fails. `[UNVERIFIED taxonomy]`
- **Lease/token approaches:** one client is granted permission to refill; others wait/use stale value.
  Facebook Memcached details remain `[UNVERIFIED from text]` pending PDF extraction.

---

## 2. Foundational Sources

| Claim/source area | Primary source | Verification status |
|---|---|---|
| Redis maxmemory policy constants | `https://raw.githubusercontent.com/redis/redis/unstable/src/server.h` | VERIFIED |
| Redis DB keyspace + expires metadata | `https://raw.githubusercontent.com/redis/redis/unstable/src/server.h` | VERIFIED |
| Redis active expiration constants and comments | `https://raw.githubusercontent.com/redis/redis/unstable/src/expire.c` | VERIFIED |
| Redis persistence high-level docs | `https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/` | REACHABLE; detailed claims need reading pass |
| Redis eviction docs | `https://redis.io/docs/latest/develop/reference/eviction/` | REACHABLE; detailed claims need reading pass |
| Memcached text protocol TTL/CAS/touch/gat/mg flags | `https://raw.githubusercontent.com/memcached/memcached/master/doc/protocol.txt` | VERIFIED |
| Memcached segmented LRU/source counters | `https://raw.githubusercontent.com/memcached/memcached/master/items.c` | VERIFIED snippets; full algorithm not traced |
| Memcached slabs allocator | `https://raw.githubusercontent.com/memcached/memcached/master/slabs.c` | VERIFIED snippets |
| Memcached external storage design | `https://raw.githubusercontent.com/memcached/memcached/master/doc/storage.txt` | VERIFIED snippets; optional path |
| Facebook Memcached NSDI 2013 paper | `https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf` | PDF fetched; body text `[UNVERIFIED]` |

---

## 3. Why It's This Way — Forcing Constraints

- **TTL exists because invalidation is incomplete:** not every writer can reliably notify every cache;
  expiration bounds staleness and memory lifetime.
- **Active expiration exists because cold expired keys would otherwise leak memory until accessed.**
- **Sampled/approximate eviction exists because exact global LRU/LFU metadata updates on every access
  can dominate cache CPU time and lock contention.
- **Slab allocation exists because variable-sized key/value objects fragment memory; fixed-size chunk
  classes make allocation/reuse predictable at the cost of internal fragmentation.
- **Segmented LRU exists because one LRU list mixes new, hot, warm, and temporary objects poorly.
  Separating segments lets maintenance demote/promote without every access taking the same lock-heavy path.
- **CAS exists because clients need conditional mutation when multiple writers race on the same key.**
- **Persistence is optional because a cache and a primary store have different failure contracts.**

---

## 4. Common Misconceptions to Preempt

1. **“TTL deletes memory exactly at expiry time.”** False. Expiry is logical first; physical deletion is
   on access or active/background maintenance.
2. **“LRU is always exact.”** False in high-throughput caches; approximate/sampled LRU often wins on CPU.
3. **“A cache hit is always correct.”** False; it may be stale relative to the database.
4. **“Write-through/write-back/cache-aside are just naming differences.”** False; they move latency,
   durability, and stale-read risk to different parts of the system.
5. **“Memcached is just a hashmap.”** False; slabs, item headers, LRU maintenance, TTL, CAS, and protocol
   behavior are core to its systems design.
6. **“Redis persistence makes it a free database replacement.”** False; persistence changes failure
   recovery but not all data-model/consistency/operational tradeoffs.
7. **“Eviction and expiration are the same.”** False; expiration is time-based invalidity, eviction is
   memory-pressure removal.

---

## 5. Best Build-Your-Own Targets

1. **TTL cache with active expiry** — hashmap + expires map + read-time expiry + incremental expiry loop.
2. **Approximate LRU cache** — clock or sampled-LRU; compare CPU and hit ratio against exact LRU.
3. **Slab allocator toy** — fixed-size classes, internal fragmentation metrics, per-class free lists.
4. **Segmented LRU cache** — HOT/WARM/COLD queues; promote on hit, evict from cold tail.
5. **CAS-enabled cache API** — `gets` returns token, `cas` succeeds only if token matches.
6. **Dogpile prevention toy** — per-key lease/singleflight so one client refills while others wait or serve stale.
7. **Redis-lite persistence** — optional append-only command log + snapshot rewrite.

---

## 6. Open Questions / Source Gaps

- Extract/read the NSDI 2013 Facebook Memcached paper directly; keep leases/gutter/regional-pool claims
  `[UNVERIFIED from text]` until then.
- Trace Redis `evict.c` end-to-end: sample pool, LRU/LFU counters, LRM policy, eviction under memory
  pressure, and interaction with TTL-only `volatile-*` policies.
- Read Redis official eviction and persistence docs deeply; current brief only confirmed pages are reachable
  and source constants exist.
- Memcached full LRU maintainer behavior, crawler, slab automove, extstore, and thread model need a deeper
  source pass.
- Cache consistency taxonomy needs primary anchors from a real production cache/system paper or official
  vendor documentation before exact pattern names become course prose.
- Admission policies (TinyLFU/W-TinyLFU/ARC) are queued; no primary algorithm paper/source was fetched in
  this fallback pass.
