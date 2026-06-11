# VERIFIED — Redis official docs (fetched 2026-06-11, Wave 17, Appendix G)

Network: `redis.io` HTTP **200** (reachable this wave; postgresql.org / kafka.apache.org /
raft.github.io / arxiv.org all **000**, queue.acm.org **403** — still blocked).

Fetched + text-extracted (no JS, plain `curl` + stdlib HTML strip; `.code-puppy-venv` untouched):

## 1. Eviction (`redis_develop_reference_eviction.txt`, 17.8 KB)
Source: https://redis.io/docs/latest/develop/reference/eviction/ (HTTP 200)
- L195 "Approximated LRU algorithm" — VERBATIM.
- L197 "keys rather than calculating them exactly. It samples a small number of keys" — VERBATIM.
  ⇒ Redis LRU/LFU is SAMPLED/approximate, not exact global LRU.
- L203–204 "the number of samples to check before every eviction with the `maxmemory-samples`
  configuration directive: `maxmemory-samples 5`" — VERBATIM (default sample size = 5).
- L216/221 "a sample size of 10 in Redis 3.0 the approximation is very close … you can raise the
  sample size to 10 at the cost of some additional CPU" — VERBATIM (accuracy/CPU knob).
- allkeys-lru / volatile-lru / allkeys-lfu / noeviction policy names present — VERBATIM.

## 2. Persistence (`redis_operate_oss_and_stack_management_persistence.txt`, 24.7 KB)
Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/ (HTTP 200)
- L79 "RDB (Redis Database): RDB persistence performs point-in-time snapshots of your dataset at
  specified intervals." — VERBATIM.
- L95 "Using AOF Redis is much more durable: you can have different fsync policies: no fsync at all,
  fsync every second, fsync at every query." — VERBATIM.
- L176 "`appendfsync always` : fsync every time new commands are appended to the AOF. Very very
  slow, very safe." — VERBATIM.
- L177 "`appendfsync everysec` : fsync every second. Fast enough … you may lose 1 second of data if
  there is a disaster." — VERBATIM (the bounded data-loss window = 1 s).
- L178 "`appendfsync no` : Never fsync … Normally Linux will flush data every 30 seconds" — VERBATIM.
- L179 "The suggested (and default) policy is to fsync every second." — VERBATIM (default = everysec).

## Cross-links / upgrades
- Confirms + extends 08's Redis citations (08 already cited eviction sampling + RDB/AOF/`appendfsync`
  policies). These docs are the appendix-G load-bearing anchors for the eviction + persistence tiers.
- Carry-forward `[UNVERIFIED]` for G (NOT hardened): Redis source `server.h`/`evict.c`/`expire.c`
  constants (cited from 08 GitHub-raw, not re-fetched this wave); single-threaded event-loop +
  `ae.c`/`networking.c` internals; `rax`/`ziplist`/`listpack`/`quicklist`/`intset` encodings;
  cluster hash-slots (16384) + gossip; RESP protocol grammar. All reachable via redis.io / GitHub
  raw in a later wave; logged, none hardened into claims here.
