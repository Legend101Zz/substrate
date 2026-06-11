# 21 · Case study — Distributed rate limiter (direct 18 application; token bucket; cell counters)

> Phase-1 brief (NO course prose). Bespoke walkthrough. Math RECOMPUTED in `_recompute.py`
> (Case 6). The most direct application: 21 builds the distributed limiter that Cases 1/5 and
> every API hand off to. Pure 18, made concrete + distributed with 14.

## 1. Requirements
- **Functional:** enforce per-key limits (per-user / per-API-key / per-IP / per-endpoint), e.g.
  "1000 req/min/key"; allow short bursts up to a cap; return **429 + Retry-After** when limited;
  support multiple tiers/policies.
- **Non-functional:** the check must be **cheap** (it's on every request -> sub-millisecond, can't
  add real latency); accurate enough (small over/under-admission acceptable); highly available
  (the limiter failing shouldn't take down the API — fail-open vs fail-closed is a policy choice);
  fair across keys.
- **Scale (RECOMPUTED, Case 6):** **1M limit-checks/s** fleet-wide; 1M unique keys * 64 B state =
  **64 MB** counter store (RAM-resident); sharded by key for the QPS.

## 2. Data model + API
- **Model:** per-key counter state. For **token bucket**: `{key -> (tokens, last_refill_ts)}`;
  refill `r` tokens/s up to capacity `C`; each request costs 1 token (reuse 18 algorithm). Stored
  in a fast in-memory store (Redis-class), **sharded by key** (reuse 14).
- **API (library/sidecar, not a user API):** `allow(key, cost=1) -> {allowed: bool, retry_after}`.
- **Algorithm choice (reuse 18):** token bucket (smooth + bursty), leaky bucket (smooth output),
  fixed window (cheap but 2x boundary burst), sliding window log (accurate, costly), sliding window
  counter (good approximation). Token bucket is the common default: `r` = steady rate, `C` = burst.

## 3. Bottleneck analysis
- **The distributed-counter problem (the only hard part):** with many app nodes checking the same
  key, a single global counter per key is a hot spot (every check = a network round-trip + a
  contended write). Options:
  1. **Centralized store (Redis) with atomic INCR/Lua token-bucket:** accurate, but a network hop
     per check + a hot key for popular limits.
  2. **Cell-based / local-then-sync:** each node grants from a **local batch** of `B` tokens leased
     from the global limit, syncing periodically. Cheap (mostly local) but **over-admits** by up to
     `(M-1)*B` across M cells (RECOMPUTED: M=8, B=5 -> 35 extra grants worst case, reuse 18
     distributed over-admit). Tune `B`: small B = accurate + chatty, large B = cheap + looser.
- **State size is trivial** (64 MB) — the problem is QPS + accuracy, solved by sharding (14) +
  choosing the local-batch granularity.

## 4. Design + cross-links to 13-20
- **18 (CORE):** this case *is* 18 — token/leaky bucket, window algorithms, 429+Retry-After,
  fail-open vs fail-closed, enforce at the edge/LB/gateway. Everything else supports it.
- **13:** sizing (1M checks/s, 64 MB) shows it's a QPS-distribution problem, not a storage one.
- **14:** **shard counters by key** so no single node owns all checks; consistent hashing (06) maps
  key -> counter shard; hot limit keys handled by local batching (avoids a hot shard).
- **15:** counter replication is **best-effort / eventual** — a rate limiter that's occasionally
  slightly off is fine (contrast payments); no quorum needed -> a PA/EL choice (cheap + available).
- **16:** the counter store IS a cache-class system (RAM, TTL'd windows); expired windows
  auto-evict.
- **17:** async aggregation of per-cell counts for accurate accounting / billing (off the hot
  path).
- **19:** rate-limit hit rate, 429 rate, over/under-admission error, per-key skew = golden signals;
  feeds back into 18's adaptive controls (the limiter is both actuator (18) and a sensed signal
  (19)).
- **20:** **fail-open** (allow on limiter outage) protects availability; **fail-closed** (deny)
  protects the backend — a 20 blast-radius decision per endpoint; the limiter must not become a
  single point of failure that takes down the whole API.

## 5. Failure modes (20)
- **Counter store outage:** fail-open (serve, lose enforcement) or fail-closed (reject, protect
  backend) per policy; local batches keep working briefly without the global store.
- **Hot limit key (one key gets all the traffic):** local batching + key-sharding so the hot key
  doesn't serialize on one counter; accept looser accuracy for that key.
- **Clock skew across nodes:** token-bucket refill uses local monotonic time per node -> small
  drift, bounded by sync interval (reuse 11: no global clock; design for skew).
- **Over-admission under partition:** cells can't sync -> they keep granting local batches ->
  bounded over-admit `(M-1)*B`; acceptable because the limiter is PA/EL by choice.

## 6. Tradeoffs
- **Accuracy vs cost (the central knob):** centralized atomic counter = accurate + a network hop +
  hot key; local batch = cheap + bounded over-admit. Pick `B` to trade.
- **Fail-open vs fail-closed:** availability of the protected service vs protection of the backend
  — opposite failure philosophies, chosen per endpoint criticality (18/20).
- **Algorithm:** fixed window (cheapest, 2x boundary burst) vs sliding (accurate, costlier) vs
  token bucket (burst-friendly default). RECOMPUTED elsewhere in 18; reused here.
- **Per-key granularity vs cardinality:** per-user limits = high cardinality (more counter state +
  shards); coarser (per-tier) limits = cheaper but less fair.

## 7. Sources / gaps
- **REUSED (line-verified):** 18 (token/leaky bucket, window algorithms, distributed over-admit
  (M-1)*B, 429+Retry-After, fail-open/closed, enforce-at-edge — all line-verified there, incl. the
  recomputed 18 math), 06 (consistent hashing for counter sharding), 13 (QPS/state sizing), 14
  (shard by key, hot-key via local batch), 15 (best-effort/eventual counters = PA/EL), 16 (RAM/TTL
  counter store), 17 (async count aggregation), 19 (429 rate / over-admit signals), 20 (fail-open
  blast radius, limiter not a SPOF), 11 (no global clock -> per-node monotonic refill).
- **RECOMPUTED:** check QPS, token-bucket steady rate, distributed over-admit (M-1)*B, counter store
  size.
- **`[UNVERIFIED]` carried:** GCRA (generic cell rate algorithm) + Stripe/Cloudflare rate-limiter
  eng posts not fetched as primaries (carried from 18); RFC 6585 §4 (429) already VERIFIED in 18.
