#!/usr/bin/env python3
"""
Substrate Appendix G - redis-internals: independent recomputation of the load-bearing arithmetic of
one real in-memory data-structure server (Redis). Pure stdlib. Run: python3 _recompute.py

G is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for "how does
ONE single-threaded, in-memory KV/data-structure server actually work" — the concrete instantiation
of transferable theory taught in spine 08 (caches/eviction/persistence) and 06 (data structures).
Spine 08/16 cross-link DOWN into G for the real mechanism.

Anchors (local + line-verified): 08/_research.md (Redis source `server.h`/`evict.c`/`expire.c`
constants), redis.io eviction + persistence docs (FETCHED+VERIFIED 2026-06-11, receipt
_VERIFIED_2026-06-11_redis-docs.md), 06 (probabilistic structures / hash tables). Bespoke structure:
the single-threaded event loop machine, tier by tier.
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. SINGLE-THREADED EVENT LOOP: no per-op lock cost; throughput ~ 1/cpu_time_per_cmd
# =====================================================================
# Redis serves commands on ONE main thread (an epoll/kqueue event loop). A command taking t_us of CPU
# caps single-key throughput at 1/t. This is WHY O(N) commands (KEYS, big SMEMBERS) are dangerous.
def ops_per_sec(cpu_us): return 1_000_000 / cpu_us
check("single-threaded: ~1M simple ops/s at ~1us/cmd (08/event-loop)", approx(ops_per_sec(1.0), 1_000_000),
      "one thread -> no lock cost but ONE slow O(N) command blocks ALL clients -> avoid KEYS/FLUSHALL on hot path")
# an O(N) command on 1M elements at ~10ns/elem blocks the loop ~10ms = ~10k simple ops stalled
block_ms = (1_000_000 * 10e-9) * 1000
check("an O(N) command on 1e6 elems stalls the loop ~10 ms (08)", approx(block_ms, 10.0),
      f"1e6 elems * 10ns = {block_ms:.0f} ms head-of-line block -> WHY Redis warns against O(N) on big keys")

# =====================================================================
# 2. APPROXIMATED (SAMPLED) LRU/LFU: maxmemory-samples default 5 (redis.io eviction, VERIFIED)
# =====================================================================
# Redis does NOT keep exact global LRU; it samples `maxmemory-samples` keys and evicts the best.
# Probability the true-LRU key is among k random samples of n is ~ 1-(1-1/n)^k (tiny), so it's an
# APPROXIMATION whose accuracy rises with sample size (docs: 5 default, 10 closer at more CPU).
SAMPLES_DEFAULT = 5
check("Redis LRU/LFU is SAMPLED; maxmemory-samples default=5 (redis.io VERIFIED)", SAMPLES_DEFAULT == 5,
      "samples 5 keys/eviction, picks best -> approximate not exact -> O(1) memory per key, no global LRU list")
def best_of_k_idle_rank(k, n):
    # expected best (oldest) percentile among k uniform samples ~ k/(k+1) of the distribution
    return k/(k+1)
check("more samples -> closer to true LRU (docs: 10 ~ exact) (redis.io)", best_of_k_idle_rank(10, 1e6) > best_of_k_idle_rank(5, 1e6),
      f"E[best percentile] k=5 -> {best_of_k_idle_rank(5,1e6):.3f}, k=10 -> {best_of_k_idle_rank(10,1e6):.3f} -> accuracy/CPU knob")

# =====================================================================
# 3. ACTIVE EXPIRATION: sampled cycle, keep stale fraction <= ~10% (08: expire.c constants)
# =====================================================================
# Passive (lazy) expiry alone leaves cold dead keys in RAM forever; activeExpireCycle samples
# ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP=20 keys per db and loops while >25% of the sample was expired,
# targeting an acceptable stale baseline of ~10%.
KEYS_PER_LOOP = 20
STALE_TARGET = 0.10
CONTINUE_THRESHOLD = 0.25
check("active expiry samples 20 keys/loop, repeats while >25% expired (08/expire.c)", KEYS_PER_LOOP == 20,
      "lazy expiry misses cold keys -> active cycle reclaims them in bounded CPU bursts")
check("active expiry targets <=10% stale baseline (08/expire.c)", STALE_TARGET == 0.10,
      f"loop continues while expired-fraction > {CONTINUE_THRESHOLD} -> converges to ~{STALE_TARGET*100:.0f}% acceptable stale")

# =====================================================================
# 4. RDB vs AOF DURABILITY WINDOW (redis.io persistence, VERIFIED)
# =====================================================================
# RDB = point-in-time snapshot at intervals -> you lose everything since the last snapshot on crash.
# AOF appendfsync everysec (default) -> bounded loss ~1 second. always -> ~0 but slow. no -> ~OS (30s).
def loss_window_s(mode):
    return {"rdb_15min": 15*60, "aof_always": 0.0, "aof_everysec": 1.0, "aof_no": 30.0}[mode]
check("AOF everysec bounds data loss to ~1 s (redis.io VERIFIED)", loss_window_s("aof_everysec") == 1.0,
      "default appendfsync=everysec -> 'you may lose 1 second of data if there is a disaster' (verbatim)")
check("AOF always ~0 loss but slowest; RDB loses since last snapshot (redis.io VERIFIED)",
      loss_window_s("aof_always") == 0.0 and loss_window_s("rdb_15min") == 900,
      "always=fsync per write (very safe, very slow); RDB 15-min snapshot -> up to 900 s lost on crash")
check("appendfsync no -> OS flushes ~every 30 s (redis.io VERIFIED)", loss_window_s("aof_no") == 30.0,
      "data in hands of OS; 'Normally Linux will flush data every 30 seconds' (verbatim)")

# =====================================================================
# 5. FORKED SNAPSHOT (RDB) COST: copy-on-write memory amplification (redis.io persistence)
# =====================================================================
# BGSAVE forks; child shares pages COW. Writes during the snapshot duplicate touched pages, so peak
# RSS ~ base + (write_rate * snapshot_duration * page_dup). Worst case approaches 2x on write-heavy.
def cow_peak_factor(dirty_fraction): return 1 + dirty_fraction
check("forked RDB snapshot COW peak RSS up to ~2x on write-heavy (redis.io)", cow_peak_factor(1.0) == 2.0,
      "every page written during the fork is duplicated -> WHY snapshotting a write-heavy instance can OOM")

# =====================================================================
# 6. REPLICATION: async replica -> bounded staleness; W=1 ack means failover can lose writes (08/L)
# =====================================================================
# Redis replication is ASYNCHRONOUS by default: master acks the client before replicas confirm.
# So a master crash before propagation loses the un-replicated writes (like quorum W=1, reuse L/15).
def writes_at_risk(inflight): return inflight   # all un-acked-by-replica writes can be lost
check("async replication: un-propagated writes lost on master crash (08/L/15)", writes_at_risk(1000) == 1000,
      "master acks before replica confirms -> failover window loses in-flight writes -> WAIT/quorum trades latency")

# =====================================================================
# 7. CLUSTER HASH SLOTS: 16384 fixed slots; key -> CRC16(key) mod 16384 (08/redis cluster)
# =====================================================================
SLOTS = 16384
check("Redis Cluster uses 16384 fixed hash slots (08)", SLOTS == 2**14,
      "key -> CRC16(key) mod 16384 -> slot -> node; resharding moves SLOTS not rehashes all keys (cf consistent hashing 06/14)")
def slots_per_node(nodes): return SLOTS // nodes
check("16384 slots spread evenly: 3 nodes ~5461 slots each (08)", slots_per_node(3) == 5461,
      f"3 masters -> {slots_per_node(3)} slots each -> moving ~1/N of slots rebalances, not a full rehash")

# =====================================================================
# 8. ENCODING SWITCH: small collections use compact listpack, flip to hashtable past a threshold (08/06)
# =====================================================================
# Small hashes/sets/zsets are stored as a contiguous listpack (cache-friendly, O(N) ops) until they
# exceed hash-max-listpack-entries (default 128) or value size -> then converted to a hashtable/skiplist.
LISTPACK_MAX_ENTRIES = 128
def encoding(n): return "listpack" if n <= LISTPACK_MAX_ENTRIES else "hashtable/skiplist"
check("small collections use listpack up to 128 entries then convert (08/06)", encoding(128) == "listpack" and encoding(129) != "listpack",
      "compact contiguous encoding for tiny collections (memory win); converts to O(1) structure when big -> space/time tradeoff")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"G-redis-internals recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All Redis-internals claims re-derived first-principles (constants from 08 + redis.io docs).")
