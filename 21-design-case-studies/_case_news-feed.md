# 21 · Case study — News feed / timeline (fan-out-on-write vs read; the celebrity problem)

> Phase-1 brief (NO course prose). Bespoke walkthrough. Math RECOMPUTED in `_recompute.py`
> (Case 2). The canonical fan-out trade-off: this case turns 14's hot-key, 17's async fan-out,
> and 16's cache into one decision (push vs pull vs hybrid).

## 1. Requirements
- **Functional:** post; follow; render a user's home timeline (recent posts from people they
  follow, ranked/reverse-chron); like/comment counts.
- **Non-functional:** timeline read p99 < 200 ms (it's the app's home screen); eventual freshness
  is acceptable (a post appearing seconds late is fine); read-availability >> write-availability.
- **Scale (RECOMPUTED, Case 2):** 300M DAU, 10 views/user/day -> **feed reads ~34,722 QPS**
  (peak ~69k); 0.1 posts/user/day -> **posts ~347 QPS**; avg 200 followers ->
  **fan-out-on-write ~69,444 inbox-writes/s** (200x the post rate). One 100M-follower celebrity
  post = **1e8 inbox writes** = a write hot-spot.

## 2. Data model + API
- **Model:** `posts {post_id, author, body, ts}`; `follows {follower, followee}`; and (for push)
  **`inbox/timeline {user_id -> [post_id...]}`** — a per-user materialized feed.
- **API:** `POST /posts`; `GET /feed?user=...&cursor=...`; `POST /follow`.
- The model choice IS the push-vs-pull choice: push materializes `inbox` at write time; pull
  computes the feed at read time from `posts` + `follows`.

## 3. Bottleneck analysis — the central trade-off
- **Fan-out-on-write (push):** on each post, append `post_id` to every follower's `inbox`. Reads
  are O(1) (just read your inbox). **Cost = write amplification** (RECOMPUTED: 200x average; 1e8
  for a celebrity). The celebrity post is a classic **14 hot key / hot shard**: one write becomes
  100M writes -> unbounded latency + a thundering write storm.
- **Fan-out-on-read (pull):** store only `posts`; at read time, gather recent posts from everyone
  you follow and merge. Writes are O(1). **Cost = expensive reads** (scatter across followees +
  merge) and reads are 100x more frequent than writes -> doesn't scale for the common user.
- **The resolution = hybrid (RECOMPUTED crossover):** push for normal users (200 writes/post is
  cheap), **pull for celebrities** (skip fan-out; their followers merge celebrity posts at read
  time). Threshold on follower count. This is the standard "merge a small pulled set into a mostly
  pushed timeline" design.

## 4. Design + cross-links to 13-20
- **13:** the back-of-envelope (write amplification 200x; celebrity 1e8) is exactly what forces the
  hybrid — pure push or pure pull each fail a sizing check.
- **14:** the celebrity is the textbook **hot key**; the fix (read-time merge for hot authors) is
  14's hot-key mitigation. `inbox` is partitioned by `user_id`; `posts` by `post_id`.
- **15:** feeds tolerate **eventual consistency** + **read-your-writes** (you must see your own
  post immediately -> write to your own inbox synchronously, fan out to others async). Maps onto
  15's session-guarantee ladder.
- **16:** the hot timeline pages + hot author posts live in cache; render = mostly cache hits;
  count fields (likes) are cached approximate counters.
- **17:** fan-out-on-write **is** an async EDA job — a post emits an event; consumers fan it into
  inboxes off a queue/log (reuse 09/17), with per-user ordering and at-least-once + idempotent
  inbox append (dedup on post_id).
- **18:** the fan-out workers are the backpressure point — a celebrity burst must be shed/queued,
  not allowed to starve normal fan-out (bounded queues, priority).
- **19:** fan-out lag (post->visible), inbox-write QPS, feed read hit ratio = golden signals.
- **20:** fan-out is **fault-tolerant + replayable** (it's a log); a slow fan-out degrades
  freshness, not availability; the read path survives fan-out outage by falling back to pull.

## 5. Failure modes (20)
- **Celebrity post storm:** pure push would melt a shard -> hybrid pull avoids it; if pushed,
  rate-limit + spread fan-out over time (freshness SLO relaxed for huge audiences).
- **Fan-out backlog:** queue grows -> posts appear late; bounded queue + shed/deprioritize
  low-value fan-out; freshness degrades gracefully (20).
- **Inbox write duplication:** at-least-once delivery -> idempotent append keyed on post_id (17).
- **Hot timeline read:** cache + CDN for hot pages; coalesce stampede on a viral post (16).

## 6. Tradeoffs
- **Push:** fast reads, heavy + bursty writes, wasted work for inactive users (writing inboxes
  nobody reads). **Pull:** cheap writes, expensive reads, bad at scale for the common path.
  **Hybrid:** best of both, more complex (two code paths + a merge + a follower-count threshold).
- **Freshness vs cost:** stronger freshness pushes more synchronously (costlier); feeds buy scale
  by relaxing freshness (eventual) — a direct 15 trade.
- **Ranking:** chronological is cheap; ML-ranked feeds add a scoring read-path cost (out of scope
  here but stacks on the pull/merge cost).

## 7. Sources / gaps
- **REUSED (line-verified):** 13 (write-amplification sizing, fan-out tail), 14 (hot key /
  celebrity, partition by user/post), 15 (eventual + read-your-writes session guarantees), 16
  (timeline + count caching, stampede), 17 (async fan-out as EDA, per-partition order, idempotent
  append), 18 (fan-out backpressure/shedding), 19 (fan-out lag signal), 20 (degrade freshness,
  replayable log).
- **RECOMPUTED:** feed read/post QPS, fan-out-on-write QPS (200x), celebrity 1e8, push/pull cost
  comparison.
- **`[UNVERIFIED]`:** the push/pull/hybrid feed design is a community idiom (Twitter/Instagram eng
  blogs, Grokking) with no single canonical paper; mechanisms grounded in 14/16/17. Specific
  vendor numbers (e.g. real follower distributions) not fetched.
