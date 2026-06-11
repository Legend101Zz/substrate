# Appendix G · Phase-1 factcheck — redis-internals

> Method (spine discipline): every load-bearing claim is (a) RECOMPUTED in `_recompute.py` (14/14) or
> (b) VERIFIED verbatim against a local primary. G is a **reference appendix** (no exercises). **0
> blockers.** Network: redis.io HTTP **200** this wave → fetched eviction + persistence docs fresh
> (receipt `meta/fetched_primaries/_VERIFIED_2026-06-11_redis-docs.md`). Redis C-source constants
> reused from **08** (which cited `server.h`/`evict.c`/`expire.c` GitHub-raw); not re-fetched here.

## Bespoke structure note
G is a **"single-threaded in-memory machine" tier walkthrough** (event loop → data-structure
encodings → expiration → eviction → persistence → replication → cluster), NOT the 13-20 four-cluster
shape and NOT a build progression. Reference-grade, deep on ONE engine (Redis).

## Primaries fetched + VERIFIED verbatim this wave (redis.io HTTP 200)
- **Eviction** (`redis_develop_reference_eviction.txt`): "Approximated LRU algorithm" (L195); "keys
  rather than calculating them exactly. It samples a small number of keys" (L197); "`maxmemory-samples`
  configuration directive: `maxmemory-samples 5`" (L203-204); "a sample size of 10 … the
  approximation is very close … at the cost of some additional CPU" (L216/221) — all VERBATIM. ⇒
  sampled/approximate LRU/LFU, default sample 5.
- **Persistence** (`redis_operate_oss_and_stack_management_persistence.txt`): "RDB persistence
  performs point-in-time snapshots" (L79); "fsync policies: no fsync at all, fsync every second,
  fsync at every query" (L95); "`appendfsync everysec` … you may lose 1 second of data if there is a
  disaster" (L177); "`appendfsync no` … Normally Linux will flush data every 30 seconds" (L178); "The
  suggested (and default) policy is to fsync every second" (L179) — all VERBATIM.

## Reused from 08 (line-verified Redis C source, GitHub-raw)
- `expire.c`: `ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP=20`, slow CPU budget 25%, ~10% acceptable stale
  baseline → active-expiry recompute.
- `server.h`/`evict.c`: maxmemory policies (volatile/allkeys LRU/LFU/random/TTL/noeviction), eviction
  candidate pool `EVPOOL_SIZE=16`, LFU `255 - LFUDecrAndReturn` → eviction-sampling recompute.
- Encoding thresholds (listpack→hashtable/skiplist) — `hash-max-listpack-entries` default 128 family.

## Recomputed claims (`_recompute.py`, 14/14)
- Single-thread: ~1M simple ops/s at 1us/cmd; O(N) on 1e6 elems stalls loop ~10 ms. PASS×2.
- Sampled LRU/LFU; `maxmemory-samples` default 5; accuracy↑ with samples. PASS×2.
- Active expiry: 20 keys/loop, repeats >25% expired, ~10% stale target. PASS×2.
- Durability windows: RDB ~snapshot interval; AOF everysec ~1 s; always ~0; no ~30 s. PASS×4.
- Forked RDB COW peak ~2× on write-heavy. PASS.
- Async replication loses un-propagated writes on master crash (reuse L/15). PASS.
- Cluster 16384 fixed slots; 3 nodes ~5461 each. PASS×2.
- Encoding switch listpack→hashtable at 128 entries. PASS.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- **Event-loop source** (`ae.c`/`networking.c`, epoll/kqueue, I/O threads for net read/write since
  6.0) — mechanism reused from 08 narrative, source not re-fetched this wave.
- **Data-structure encoding internals** (`rax`/radix tree, `ziplist`→`listpack` migration,
  `quicklist`, `intset`, skiplist for zset) — exact byte layouts not line-verified; redis.io
  internals-rax page returned **HTTP 404** this wave.
- **RESP protocol** grammar (RESP2/RESP3) — not fetched.
- **Cluster gossip** (`CLUSTER` bus, failure detection, `CRC16` slot hashing exact polynomial) —
  16384 + mod model used; gossip detail not fetched.
- **Multi-part AOF since 7.0** (base + incremental + manifest) — cited from 08; not re-verified.
- Exact `cow`/RSS amplification depends on workload — modeled as ≤2×, not measured.
All reachable via redis.io / GitHub-raw in a later wave; logged, none load-bearing (numbers
recomputed or from 08's line-verified source).

## Verdict
G is honest and appendix-appropriate: the eviction (sampled LRU/LFU, default 5) and persistence
(RDB point-in-time, AOF everysec ~1 s loss) cores are VERIFIED verbatim against freshly-fetched
redis.io docs; expiration/encoding/cluster constants come from 08's line-verified C-source reads and
every derived number is recomputed (14/14). Reconcile into `_research.md`. **0 blockers.**
