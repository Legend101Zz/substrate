# Factcheck Report — Sub-course 08 Caches and Storage Systems (Phase 1)
## Scope: Redis, Memcached, Facebook Memcache, admission/dogpile/consistency
## Factchecker: brain-manual fallback after `factchecker` subagent `httpx.ReadTimeout` | Date: 2026-06-10

The formal `factchecker` subagent was invoked sequentially but timed out while streaming. No Code Puppy
venv changes were made. This report records the manual primary-source spot-check used before reconciliation.

---

## Summary Verdict

- **PASS with warnings.** Load-bearing Redis, Memcached, Facebook Memcache, TinyLFU/W-TinyLFU, singleflight,
  RFC 5861, and RFC 9111 claims are source-backed.
- **No blockers remain before 08 reconciliation.**
- **Warnings preserved:** unstable-branch Redis/Memcached code should be pinned before Phase 2/chapter prose;
  application pattern names `write-through` and `write-back` still need stronger primary taxonomy sources;
  ARC exact pseudo-code/patent details need a deeper pass if taught beyond mechanism level.

---

## PASS Items

### Redis eviction policies and approximate sampling — PASS

- **Claim checked:** Redis exposes volatile/allkeys LRU/LFU/random/TTL/noeviction policies plus newer LRM
  variants, and LRU/LFU/LRM eviction is approximate/sampled.
- **Evidence:**
  - `https://raw.githubusercontent.com/redis/redis/unstable/src/server.h` defines `MAXMEMORY_VOLATILE_LRU`,
    `MAXMEMORY_VOLATILE_LFU`, `MAXMEMORY_VOLATILE_TTL`, `MAXMEMORY_VOLATILE_RANDOM`,
    `MAXMEMORY_ALLKEYS_LRU`, `MAXMEMORY_ALLKEYS_LFU`, `MAXMEMORY_ALLKEYS_RANDOM`,
    `MAXMEMORY_NO_EVICTION`, `MAXMEMORY_VOLATILE_LRM`, `MAXMEMORY_ALLKEYS_LRM`, plus policy flags.
  - `https://raw.githubusercontent.com/redis/redis/unstable/src/evict.c` defines `EVPOOL_SIZE = 16`, uses
    `server.maxmemory_samples`, samples with `kvstoreDictGetSomeKeys()`, scores LRU/LRM by idle time, LFU by
    inverse frequency (`255 - LFUDecrAndReturn(kv)`), and TTL by expiry time.
  - Redis eviction docs (`https://redis.io/docs/latest/develop/reference/eviction/`) explicitly call Redis LRU
    “approximated,” describe sampling, document `maxmemory-samples`, and say LFU is approximated similarly.
- **Patch status:** `_research_cache-eviction-consistency.md` was patched to remove “needs follow-up” wording.

### Redis TTL active expiration constants and behavior — PASS

- **Claim checked:** Redis has read-time expiration plus active expiration with baseline constants and effort tuning.
- **Evidence:**
  - `https://raw.githubusercontent.com/redis/redis/unstable/src/server.h` defines `redisDb` with `kvstore *keys`
    and `kvstore *expires`.
  - `https://raw.githubusercontent.com/redis/redis/unstable/src/expire.c` defines
    `ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP = 20`, `ACTIVE_EXPIRE_CYCLE_FAST_DURATION = 1000`,
    `ACTIVE_EXPIRE_CYCLE_SLOW_TIME_PERC = 25`, and `ACTIVE_EXPIRE_CYCLE_ACCEPTABLE_STALE = 10`.
  - `activeExpireCycle()` rescales baseline parameters from `server.active_expire_effort`, samples expires via
    `kvstoreScan()`, and repeats while stale percentage exceeds the acceptable threshold.
- **Patch status:** no blocker.

### Redis RDB/AOF persistence details — PASS

- **Claim checked:** Redis docs describe no persistence, RDB, AOF, and combined RDB+AOF; RDB is snapshot/fork-based;
  AOF logs writes, has fsync modes, rewrite, and Redis 7 multi-part AOF.
- **Evidence:** `https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/` states:
  - RDB performs point-in-time snapshots.
  - AOF logs every write operation and replays on startup.
  - RDB uses a child process after `fork()` to write a temporary RDB and replace the old file.
  - AOF has `appendfsync always`, `appendfsync everysec`, and `appendfsync no`; docs say `everysec` may lose
    about one second of data in a disaster.
  - Since Redis 7.0, AOF is multi-part: base file + incremental files tracked by a manifest.
- **Patch status:** no blocker.

### Memcached TTL/CAS/stale protocol claims — PASS

- **Claim checked:** Memcached protocol supports expiration, CAS, touch/gat/gats, and meta-protocol stale metadata.
- **Evidence:** `https://raw.githubusercontent.com/memcached/memcached/master/doc/protocol.txt` documents:
  - `exptime` as 0/relative/absolute timestamp behavior and second-level internal time caveat.
  - `gets`/`cas` token flow.
  - `touch`, `gat`, and `gats` expiration update/fetch operations.
  - Meta protocol flags for TTL/CAS/size/hit-fetch/stale-marker style metadata.
- **Patch status:** no blocker; exact flag letters are version-sensitive and left as a warning.

### Memcached slabs, segmented LRU, crawler, slab automove, extstore, threading — PASS

- **Claim checked:** Memcached internals brief accurately describes slab classes, segmented LRU maintenance,
  crawler/maintainer, automove, extstore, and worker/item-lock threading at mechanism level.
- **Evidence:**
  - `slabs.c` defines `slabclass_t`, class sizing, `perslab`, free list, and allocation paths.
  - `items.c` references `HOT_LRU`, `WARM_LRU`, `COLD_LRU`, `TEMP_LRU`, `lru_pull_tail()`,
    `lru_maintainer_juggle()`, crawler hooks, and `lru_maintainer_thread()`.
  - `slab_automove.c` defines the automove stats/window mechanism and `slab_automove_run()`.
  - `doc/storage.txt` and `extstore.c` document external storage, `ITEM_HDR`, async IO objects, and IO threads.
  - `thread.c` creates worker threads, event notifications, and hash-bucketed item locks.
- **Patch status:** no blocker.

### Facebook Memcache paper claims — PASS

- **Claim checked:** leases, stale values, Gutter, pools, regional pools, and the 17K/s vs 1.3K/s lease experiment.
- **Evidence:** Nishtala et al., “Scaling Memcache at Facebook,” NSDI 2013,
  `https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf`, extracted with a throwaway
  `/tmp` `uv run --with pypdf` process:
  - Section 3.2.1 says leases address stale sets and thundering herds.
  - Lease is described as a 64-bit token bound to a key.
  - The one-week herd-prone key experiment reports 17K/s peak database query rate without leases and 1.3K/s
    with leases.
  - Section 3.2.2 describes pools; Section 3.3 describes Gutter at about 1% of memcached servers and short
    expiry; Section 4.2 describes regional pools.
- **Patch status:** previous `[UNVERIFIED from text]` wording was patched out where stale.

### TinyLFU / W-TinyLFU / Caffeine admission claims — PASS

- **Claim checked:** TinyLFU is an approximate frequency admission policy; W-TinyLFU uses a recency window plus
  main SLRU/TinyLFU admission; Caffeine implements a 4-bit frequency sketch with reset/aging.
- **Evidence:**
  - Einziger/Friedman arXiv paper `https://arxiv.org/abs/1512.00727` / PDF text verifies approximate LFU
    admission, Doorkeeper, W-TinyLFU window+SLRU design, and Caffeine integration.
  - `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/FrequencySketch.java`
    verifies 4-bit CountMinSketch, max counter 15, `sampleSize = 10 * maximum`, and reset halving.
  - `https://raw.githubusercontent.com/ben-manes/caffeine/master/caffeine/src/main/java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java`
    verifies `PERCENT_MAIN = 0.99d`, `PERCENT_MAIN_PROTECTED = 0.80d`, `ADMIT_HASHDOS_THRESHOLD = 6`, and
    hill-climber constants.
  - `https://raw.githubusercontent.com/ben-manes/caffeine/master/simulator/src/main/java/com/github/benmanes/caffeine/cache/simulator/admission/TinyLfu.java`
    verifies candidate/victim frequency comparison.
- **Patch status:** no blocker.

### ARC mechanism-level claim — PASS with warning

- **Claim checked:** ARC adaptively balances recency/frequency using real and ghost lists.
- **Evidence:** Megiddo/Modha FAST 2003 PDF was fetched from USENIX legacy and extracted with pypdf. Mechanism-level
  T1/T2/B1/B2 and self-tuning recency/frequency framing are supported.
- **Warning:** exact pseudo-code, target update formulas, and patent/licensing details are not yet reconciled into
  this brief. Keep ARC at high-level mechanism in 08 unless deepened later.

### singleflight / RFC 5861 / RFC 9111 claims — PASS

- **Claim checked:** singleflight suppresses duplicate concurrent calls but is not a cache; RFC 5861 defines
  stale-while-revalidate/stale-if-error; RFC 9111 defines cache keys, freshness, validation, stale constraints,
  request collapsing, and unsafe-method invalidation.
- **Evidence:**
  - `https://raw.githubusercontent.com/golang/sync/master/singleflight/singleflight.go` shows `Group.Do`,
    in-flight `call`, waiter behavior, `shared` result, `DoChan`, and `Forget`; entries are deleted after completion.
  - `https://www.rfc-editor.org/rfc/rfc5861.txt` defines `stale-while-revalidate` and `stale-if-error` with
    `delta-seconds`.
  - `https://www.rfc-editor.org/rfc/rfc9111.txt` covers `Vary`, freshness, age, validation, stale response
    constraints, collapsed forwarding, 304 updates, and invalidation after unsafe methods.
- **Patch status:** no blocker.

---

## WARN Items / Residual Gaps

1. **Release pinning:** Redis `unstable` and Memcached `master` are moving targets. Before Phase 2 or chapter prose,
   pin exact commits or use release tags for source citations.
2. **Pattern taxonomy:** `cache-aside` is anchored by Facebook’s lookaside shape; `write-through` and `write-back`
   remain useful but need an official/system source before being presented as canonical definitions.
3. **ARC depth:** exact ARC pseudo-code and patent status are not yet factchecked enough for deep teaching.
4. **Count-Min math:** Caffeine implementation is verified; formal Count-Min Sketch error-bound derivation is not.
5. **XFetch/probabilistic early expiration:** not primary-sourced; do not include exact formula yet.
6. **Memcached meta stale flags:** mechanism is verified, but exact flag letters should be release-pinned.

---

## Blockers

None after patching stale `[UNVERIFIED from text]` statements about Facebook Memcache extraction.
