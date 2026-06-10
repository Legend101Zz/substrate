# Research Brief — Sub-course 08: Memcached Internals
## Source cluster: slabs, segmented LRU, crawler/maintainer, slab automove, extstore, threading, CAS/stale flags
## Researcher: brain-manual | Date: 2026-06-10

---

## 1. Key Mechanisms

### 1.1 Object storage: hash table + item headers + slab allocation

Memcached is not “just a hashmap.” The user-visible model is key/value lookup, but the performance
model is a hash table whose item payloads are allocated out of slab classes.

- `slabs.c` defines `slabclass_t` with chunk size, chunks-per-slab (`perslab`), free-list accounting,
  and per-class slab arrays. Source: `https://raw.githubusercontent.com/memcached/memcached/master/slabs.c`.
- `slabs_init()` builds size classes by starting from a base item size and multiplying by a growth
  factor until the maximum chunk size; each class computes `perslab = settings.slab_page_size / size`.
- `do_slabs_alloc()` allocates an item-sized chunk from the right slab class; this trades external
  fragmentation for internal fragmentation. A 97-byte object may live in a 112-byte-ish class rather
  than asking general `malloc` for a bespoke block.

**Why it matters:** cache systems store enormous numbers of variably-sized values. Without slab classes,
allocator metadata, fragmentation, and lock contention can become the cache’s real bottleneck rather
than network or hash lookup.

### 1.2 Expiration, protocol-level CAS, and stale flags

The text protocol is the stable external contract for several internal mechanisms.

- `exptime` is either 0 (never expire), a relative TTL in seconds, or an absolute Unix timestamp;
  protocol docs warn low TTLs are coarse because internal time advances in seconds. Source:
  `https://raw.githubusercontent.com/memcached/memcached/master/doc/protocol.txt`.
- `gets` returns a CAS token; `cas` stores only if the supplied token still matches the item’s current
  CAS value. This gives clients conditional mutation without a distributed lock.
- `touch`, `gat`, and `gats` update/fetch TTLs, so expiry is not only a set-time property.
- The newer meta protocol (`mg`/`ms`/`md`) exposes metadata such as TTL, CAS, size, hit/fetch state,
  and stale markers; stale serving is a first-class protocol-level path rather than merely app folklore.

### 1.3 Segmented LRU: HOT/WARM/COLD/TEMP instead of one giant list

Current Memcached uses multiple LRU segments per slab class:

- `items.c` references `HOT_LRU`, `WARM_LRU`, `COLD_LRU`, and `TEMP_LRU` queues.
- `lru_pull_tail()` is the central maintenance/eviction routine. It can expire old items, unlink unfetched
  items, delete external-storage payloads, move active cold items to WARM, and reclaim COLD tails.
- `lru_maintainer_juggle()` embodies the policy: if HOT or WARM grows too large, push tails toward
  COLD; if COLD grows too large, poke COLD’s tail. Source:
  `https://raw.githubusercontent.com/memcached/memcached/master/items.c`.
- `lru_maintainer_thread()` runs in a background thread, sleeps/adapts, triggers LRU juggling, and can
  kick the crawler.

**Mental model:** HOT is probation for recently inserted/active objects; WARM is retained working-set
material; COLD is the eviction frontier; TEMP is for very-short-lived objects. This is a cheaper, more
cache-friendly approximation than updating one exact global LRU on every read.

### 1.4 LRU crawler: expiration/statistics without blocking the hot path

`items.c` includes crawler support (`lru_crawler_start`, `lru_maintainer_crawler_check`, crawler stats).
The maintainer can periodically kick crawlers per slab/LRU class to find expired objects and collect
statistics. This matters because many expired items may never be read again; a purely read-time expiry
scheme leaves dead objects resident until pressure finds them.

### 1.5 Slab automove: rebalance memory between size classes

The slab allocator creates a second problem: the wrong classes can own the memory. If traffic shifts from
small values to larger values, small-value slab pages may sit underused while large classes evict hot data.

- `slab_automove.c` samples per-class item and slab stats before/after a window.
- `slab_automove_run()` chooses source and destination classes based on free chunks, eviction/age
  signals, and configured window/ratio settings. Source:
  `https://raw.githubusercontent.com/memcached/memcached/master/slab_automove.c`.

### 1.6 External storage (extstore): move cold value bytes off DRAM

Memcached is primarily an in-memory cache, but extstore adds an optional flash/disk-backed value path.

- `doc/storage.txt` says `extstore_write()` synchronously copies an input buffer into a staging buffer,
  `extstore_read()` is asynchronous through IO objects, and IO callbacks execute from IO threads.
- In the POC design, `items.c`’s `lru_maintainer_thread` writes items to storage when LRU tails are old;
  an in-memory `ITEM_HDR` keeps key/header metadata while value bytes live in storage.
- `extstore.c` creates IO threads and a background IO thread, tracks pages/buckets, and supports write,
  read, delete, close-page, and evict-page operations. Sources:
  `https://raw.githubusercontent.com/memcached/memcached/master/doc/storage.txt` and
  `https://raw.githubusercontent.com/memcached/memcached/master/extstore.c`.

**Constraint:** DRAM is precious; cold large values can consume huge memory. Extstore buys capacity at
latency/complexity cost. It is not the baseline “everything is RAM” Memcached model.

### 1.7 Threading: event workers, item locks, and maintenance threads

- `thread.c` creates worker event-handler threads (`LIBEVENT_THREAD`) and uses eventfd/notification
  paths to dispatch work. Source: `https://raw.githubusercontent.com/memcached/memcached/master/thread.c`.
- Item mutation is guarded by hash-bucketed item locks; comments state `item_lock()` must be held before
  modifying an item or its associated hash table bucket.
- Worker threads serve network operations; maintainer/crawler/extstore threads do background memory and
  IO work. This separation keeps common get/set latency from directly paying every housekeeping cost.

### 1.8 Facebook production extensions: leases, pools, Gutter, regional pools

The NSDI 2013 paper verifies production-scale mechanisms around Memcached rather than only inside the
daemon:

- Web servers use memcache as a demand-filled lookaside cache; writes go to MySQL and then delete/invalidate
  memcache keys to avoid stale cache hits.
- Consistent hashing spreads keys across memcached servers inside a cluster.
- Leases address stale sets and thundering herds. The paper defines a lease as a 64-bit token bound to a key;
  a client presents the token when setting after a miss, so the server can reject stale fills after deletes.
- The lease experiment reports peak database query rate of 17K/s without leases versus 1.3K/s with leases
  for a herd-prone key set over one week.
- Pools isolate key classes by access rate/miss cost; Gutter is a small pool (~1% of memcached servers in
  a cluster) for failed-server spillover; regional pools hold one copy per region for selected data classes.
- Multi-region writes rely on master-region writes, replication lag awareness, delete streams, and remote
  markers; the paper intentionally treats slightly stale reads as a tunable availability/latency tradeoff.

Source: Nishtala et al., “Scaling Memcache at Facebook,” NSDI 2013,
`https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf`.

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| Memcached text/meta protocol, TTL, CAS, touch/gat, stale metadata | `https://raw.githubusercontent.com/memcached/memcached/master/doc/protocol.txt` | VERIFIED |
| Slab classes, chunk sizing, allocation/free lists | `https://raw.githubusercontent.com/memcached/memcached/master/slabs.c` | VERIFIED |
| Segmented LRU, maintainer, crawler hooks, eviction/reclaim behavior | `https://raw.githubusercontent.com/memcached/memcached/master/items.c` | VERIFIED |
| Item/LRU declarations | `https://raw.githubusercontent.com/memcached/memcached/master/items.h` | VERIFIED |
| Slab automove | `https://raw.githubusercontent.com/memcached/memcached/master/slab_automove.c` | VERIFIED |
| Worker/event threading, item locks | `https://raw.githubusercontent.com/memcached/memcached/master/thread.c` | VERIFIED |
| Extstore design | `https://raw.githubusercontent.com/memcached/memcached/master/doc/storage.txt` | VERIFIED |
| Extstore implementation | `https://raw.githubusercontent.com/memcached/memcached/master/extstore.c` | VERIFIED snippets |
| Facebook production Memcache architecture | `https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf` | VERIFIED via extracted PDF text |

---

## 3. Why It’s This Way — Forcing Constraints

- **Slabs exist because object sizes vary.** Fixed chunk classes make allocation/reuse predictable but
  introduce internal fragmentation and require class rebalancing.
- **Segmented LRU exists because exact global LRU is too expensive.** Read-heavy caches cannot afford a
  single globally-mutated list on every hit; segments plus background maintenance approximate retention.
- **Crawler/maintainer threads exist because expiration and rebalancing are housekeeping.** The hot request
  path should not synchronously scan cold tails or every expired object.
- **CAS exists because clients race.** Conditional set gives a simple compare-and-swap protocol without
  building transactions into Memcached.
- **Gutter and pools exist because cache failure can overload the origin.** A failed cache server should not
  instantly redirect all of its misses to databases.
- **Regional pools exist because cross-cluster duplication wastes memory and can increase invalidation load.**
  One copy per region is cheaper for some data, at the price of staleness/latency tradeoffs.

---

## 4. Common Misconceptions to Preempt

1. **“Memcached eviction is one LRU list.”** Current source uses HOT/WARM/COLD/TEMP LRU segments per slab class.
2. **“TTL means memory disappears exactly at expiry.”** Expired objects can remain until read, crawled, or reclaimed.
3. **“Slabs eliminate fragmentation.”** They reduce external fragmentation but create internal fragmentation.
4. **“CAS makes multi-key operations safe.”** CAS is per item; multi-key invariants remain application-owned.
5. **“Extstore turns Memcached into a database.”** It extends capacity for cached values; it does not add database
   durability, indexing, or transaction semantics.
6. **“Gutter is just another replica.”** The Facebook paper describes it as a small failure spillover pool with
   short-lived entries, trading slight staleness for backend protection.

---

## 5. Build-Your-Own Targets

1. **Slab allocator simulator** — size classes, internal-fragmentation metrics, per-class free lists.
2. **Segmented LRU toy cache** — HOT/WARM/COLD queues and a background maintainer tick.
3. **CAS protocol** — `gets` returns token; `cas` succeeds only on token match.
4. **Crawler/expiry loop** — periodic scan of cold tails to reclaim expired entries.
5. **Slab automove simulator** — shift pages between size classes based on eviction/free-chunk stats.
6. **Gutter simulation** — model failed cache nodes and compare database load with/without a small spillover pool.

---

## 6. Open Questions / Source Gaps

- Exact meta protocol stale-marker flag names are source/doc-version sensitive; pin a Memcached release before
  chapter prose.
- Deeper extstore internals should be moved to appendix G or a real-system appendix unless spine 08 needs them.
- Facebook production numbers are from 2013; treat them as architecture evidence, not current Facebook capacity.
- The paper’s delete-stream tooling (`mcsqueal`, `mcrouter`) deserves a separate source pass if 08 teaches
  multi-region invalidation deeply.
