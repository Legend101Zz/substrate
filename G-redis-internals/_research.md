# Appendix G · redis-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). G is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for "how ONE single-threaded,
> in-memory data-structure server — Redis — actually works," instantiating the transferable theory
> taught in spine **08** (caches/eviction/persistence) and **06** (data structures). Spine 08/16
> cross-link DOWN into G. Bespoke structure: **the single-threaded in-memory machine, tier by tier**,
> NOT four clusters and NOT a build progression. Math: `_recompute.py` (14/14). Factcheck:
> `_factcheck_phase1.md` (0 blockers). **NEW primaries fetched+verified this wave** (redis.io HTTP
> 200): eviction + persistence docs — receipt `meta/fetched_primaries/_VERIFIED_2026-06-11_redis-docs.md`.

## 1. Thesis
Redis is fast for ONE reason: **it keeps everything in RAM and serves commands on a single thread.**
That single decision cascades into every other design. No RAM-vs-disk latency → microsecond ops. One
thread → no per-operation locking (huge simplification) BUT one slow command blocks *every* client.
RAM is finite and volatile → it needs **eviction** (approximate, because exact global LRU is too
expensive), **expiration** (active + lazy, because cold dead keys waste RAM), and **persistence**
(RDB/AOF, because RAM dies on crash). Each is a deliberate trade of accuracy/durability for speed.

## 2. The single-threaded in-memory machine (the bespoke spine)

### Tier 1 — The event loop (08)
- One main thread runs an epoll/kqueue **event loop** (`ae.c`); commands execute serially. (Since 6.0
  there are I/O helper threads for socket read/write, but command *execution* stays single-threaded.)
- Consequence (RECOMPUTED): ~**1M simple ops/s** at ~1µs/cmd; but an **O(N)** command over 1e6
  elements (`KEYS *`, big `SMEMBERS`/`SORT`) stalls the loop **~10 ms** = head-of-line block for all
  clients. This is THE Redis operational rule: never run O(N) on big keys on the hot path.

### Tier 2 — Data-structure encodings (08/06)
- Each value type has a **compact small encoding** that flips to a scalable one past a threshold:
  small hash/set/zset = contiguous **listpack** (cache-friendly, O(N)); beyond
  `hash-max-listpack-entries` (default **128**) or value size → **hashtable/skiplist** (O(1)/O(log N)).
- RECOMPUTED: ≤128 entries → listpack; 129 → convert. Trades memory (tiny collections) for time
  (big collections). Other encodings: `intset` (all-int sets), `quicklist` (list of listpacks),
  `rax` (radix tree, e.g. streams), skiplist (zset). `[UNVERIFIED]` byte layouts (carry-forward).

### Tier 3 — Expiration: lazy + active (08, `expire.c`)
- A TTL makes a key **logically** invalid at time T; memory reclaim is lazy (on access) + **active**
  (`activeExpireCycle`).
- RECOMPUTED + 08 source: the active cycle samples **20 keys/loop** per db, repeats while **>25%** of
  the sample was expired, converging to a **~10%** acceptable stale baseline within a bounded CPU
  budget (slow cycle ≤25% CPU). WHY both: lazy alone never reclaims **cold** dead keys.

### Tier 4 — Eviction: approximate, sampled (redis.io, VERIFIED verbatim)
- When `maxmemory` is hit, Redis evicts per policy (allkeys/volatile × LRU/LFU/random/TTL, or
  noeviction). Crucially it does **NOT** keep an exact global LRU list — it **samples** keys.
- VERBATIM (redis.io): "**Approximated LRU algorithm** … It samples a small number of keys" with
  "`maxmemory-samples 5`" default; raising to 10 "is very close" to exact "at the cost of some
  additional CPU." RECOMPUTED: more samples → closer to true-LRU (the accuracy/CPU knob); O(1) memory
  per key vs an exact intrusive LRU list. LFU uses an 8-bit log counter with decay (`255 −
  LFUDecrAndReturn`, from 08 source). Candidate pool `EVPOOL_SIZE=16` (08).

### Tier 5 — Persistence: RDB vs AOF (redis.io, VERIFIED verbatim)
- RAM is volatile → two durability modes (combinable):
  - **RDB**: "**point-in-time snapshots** … at specified intervals" (verbatim). Compact single file,
    great for backups; **you lose everything since the last snapshot** on crash. Taken by `fork()` +
    copy-on-write → RECOMPUTED **COW peak RSS up to ~2×** on write-heavy instances (every page
    written during the fork duplicates → can OOM).
  - **AOF**: append every write command; replay on restart. `appendfsync` policies (verbatim):
    **`always`** (fsync per write — very safe, very slow, ~0 loss); **`everysec`** (the **default** —
    "**you may lose 1 second of data if there is a disaster**"); **`no`** (OS decides — "Normally
    Linux will flush data every 30 seconds"). Since 7.0 AOF is multi-part (base+incr+manifest;
    `[UNVERIFIED]`).
- RECOMPUTED loss windows: RDB ≈ snapshot interval (e.g. 900 s); AOF always 0; everysec 1 s; no 30 s.
  This is the durability ⇄ throughput dial — the appendix payload that spine 08 cross-links to.

### Tier 6 — Replication + HA (08/L/15)
- Default replication is **ASYNCHRONOUS**: the master acks the client *before* replicas confirm.
- RECOMPUTED: a master crash before propagation **loses the un-replicated writes** — identical to a
  quorum with effective W=1 (reuse L/15). `WAIT numreplicas timeout` lets you trade latency for a
  stronger ack. Sentinel/Cluster provide failover; a stale replica promoted can lose committed-looking
  writes (the Redis analogue of unclean leader election in 09/H).

### Tier 7 — Redis Cluster: 16384 hash slots (08/14)
- Keys map to one of **16384** fixed slots via `CRC16(key) mod 16384`; slots are assigned to master
  nodes. RECOMPUTED: 3 masters → ~**5461** slots each. Resharding moves **slots**, not a full rehash
  of all keys — a coarse-grained cousin of consistent hashing (cf 06/14). `{hashtag}` forces
  multi-key ops onto one slot.

## 3. The "speed forces every trade" reconciliation (appendix payload)
| tier | mechanism | the trade speed forces | anchor |
|---|---|---|---|
| event loop | single thread, serial cmds | no locks, but O(N) blocks everyone | 08 |
| encodings | listpack → hashtable @128 | memory (small) vs time (big) | 08/06 |
| expiration | lazy + active sampling | CPU burst vs RAM held by dead keys | 08/expire.c |
| eviction | sampled approximate LRU/LFU | O(1) mem/key vs exact-LRU accuracy | redis.io (VERIFIED) |
| persistence | RDB snapshot / AOF fsync | durability window vs throughput | redis.io (VERIFIED) |
| replication | async ack | latency vs lost-write window | 08/L/15 |
| cluster | 16384 fixed slots | move-slots vs full rehash | 08/14 |

## 4. Common misconceptions to preempt
- "Redis is just a hashmap." It's a single-threaded event loop with typed encodings, sampled
  eviction, active expiry, persistence, replication, and clustering.
- "Redis LRU is exact." No — it's **sampled/approximate** (default 5 samples; verbatim docs).
- "Persistence makes Redis a free database." It changes recovery, not the consistency/query model;
  AOF everysec still has a **1-second** loss window.
- "Replication is synchronous." Default is **async** — failover can lose in-flight writes (use `WAIT`).
- "Single-threaded means slow." It means ~1M ops/s with no locks — until one O(N) command blocks all.
- "TTL frees memory at exactly T." Logical invalidity is immediate; reclaim is lazy + active sampling.

## 5. Provenance summary
- **NEW primaries fetched+verified (redis.io HTTP 200):** eviction (sampled LRU/LFU, `maxmemory-
  samples 5`) + persistence (RDB point-in-time, AOF `appendfsync` everysec ~1 s loss) — receipt
  `_VERIFIED_2026-06-11_redis-docs.md`.
- **REUSED (line-verified in 08):** `expire.c` active-cycle constants, `evict.c`/`server.h` policies +
  LFU + pool, encoding thresholds. Spine 06/08/16 + appendix L/15.
- **RECOMPUTED:** `_recompute.py` (14/14).
- **`[UNVERIFIED]` carry-forward (not load-bearing):** event-loop source (`ae.c`/`networking.c`),
  encoding byte layouts (`rax`/`listpack`/`quicklist`/`intset`/skiplist; redis.io internals-rax 404
  this wave), RESP grammar, cluster gossip + CRC16 polynomial, multi-part AOF 7.0, exact COW/RSS.
  Logged, none hardened.

---
**Appendix G reconciled.** Reference-grade, exercise-free, 14/14 recomputed, eviction+persistence
cores verified verbatim against fresh redis.io docs. No chapters yet.
