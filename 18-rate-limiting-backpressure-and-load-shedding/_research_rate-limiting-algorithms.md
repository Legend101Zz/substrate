# 18 · Cluster A — Rate-limiting algorithms (the request admission valve)

> Phase-1 brief (NO course prose). One source cluster per ADR-001. Math claims here are
> RECOMPUTED in `_recompute.py` (blocks A1–A5). `[UNVERIFIED]` = not confirmed from a
> fetched primary this session; carried forward, must not harden into Phase-2 prose.

## Scope
Rate limiting = a **deliberate admission valve** placed *before* the work, deciding which
requests are allowed to consume capacity and which are rejected (typically HTTP **429 Too
Many Requests**, RFC 6585 §4 — **VERIFIED** from `meta/fetched_primaries/rfc6585.txt`).
It is the *proactive* dual of load shedding (Cluster C, which sheds *reactively* under
measured overload). This cluster covers the four canonical algorithms, their burst/accuracy/
memory tradeoffs, distributed enforcement, fairness, and where in the topology to enforce.

## 1. Key mechanisms

### 1.1 The four canonical algorithms
- **Token bucket** — a bucket holds up to `B` tokens, refilled at `r` tokens/sec; each request
  consumes a token, rejected if empty. **Allows bursts up to `B`, long-run rate capped at `r`.**
  - VERIFIED (A1): from an empty bucket an instantaneous burst of 100 admits exactly `B=10`;
    long-run admitted ≈ `r·T + B` (5/s for 100 s from cap 10 ⇒ ~510); from a full bucket an
    instant burst admits exactly `B`. So `B` *is* the burst allowance and `r` *is* the
    sustained ceiling — two independent knobs. This is why token bucket is the default for
    "steady rate but tolerate spikes."
- **Leaky bucket (as a queue/meter)** — requests enter a FIFO of depth `D`, drained
  ("leaked") at a fixed rate `r`; overflow past `D` is dropped. **Output is *smoothed* to
  exactly `r`** regardless of arrival burstiness (it is a shaper, not just a limiter).
  - VERIFIED (A2): a burst of 50 into depth 10 leaking 5/s ⇒ 10 served, 40 dropped, and the
    measured peak output never exceeds the leak rate. Token bucket *permits* bursts; leaky
    bucket *erases* them. (Leaky-bucket-as-meter ≅ token bucket mathematically; the
    queue form additionally adds latency — the 13/B1 queue-bound tradeoff.)
- **Fixed window counter** — count requests per calendar window (e.g. per second); reset at
  the boundary. O(1) memory, but **a boundary burst admits up to `2·limit`** within one
  window-width (limit at the end of window *k*, limit at the start of *k+1*).
  - VERIFIED (A3): `fixed_window_boundary_burst(100) == 200`.
- **Sliding window log** — store the timestamp of every admitted request; admit iff fewer than
  `limit` fall in the trailing `window`. **Exact** (never exceeds `limit` in any window-width
  span) but costs **O(limit) memory per key**.
  - VERIFIED (A3): hammering 1000 requests into 0.5 s with `limit=100, window=1.0` admits
    exactly 100.
- **Sliding window counter (approximate)** — keep two counts (previous + current window) and
  estimate `est = curr + prev·(1 − elapsed_fraction)`. **O(1) memory**, smooths the fixed-window
  boundary spike, at the cost of an approximation error.
  - VERIFIED (A4): worst-case over-admission vs the exact log = `prev·elapsed_fraction` (e.g.
    if the previous window's traffic was actually clustered at its end, being 10% into the
    current window under-counts by `0.1·prev`). The whole tradeoff: **O(1) memory and no
    boundary spike, but bounded inaccuracy**, because it assumes the previous window was
    uniform.

### 1.2 The cross-product (why these are one family)
Burst tolerance and accuracy are the axes. Token bucket = "rate + an explicit burst budget."
Leaky bucket = "rate + zero burst (smoothed output) + added latency." Fixed window = cheap but
2× boundary leak. Sliding log = exact but O(limit). Sliding counter = the practical middle
(O(1), bounded error). Choosing one is choosing *how much burst you tolerate* × *how much
memory/accuracy you'll pay*.

### 1.3 Distributed rate limiting
A single shared counter (e.g. Redis `INCR`+TTL, or a Lua script for atomicity) is the simplest
correct distributed limiter but puts a **synchronous round trip on every request** and makes
the counter a hot key / SPOF (reuse 14 hot-shard, 16 hot-key, 11 "no global coordination for
free").
- **Local-token + periodic-sync (cell-based / approximate):** each node/cell limits locally
  against a slice of the global budget and reconciles periodically. Cheaper, but **over-admits**.
  - VERIFIED (A5): worst-case global over-admission ≈ `(cells − 1)·sync_batch`. Sync on every
    admit (`batch=1`) ⇒ at most `cells−1` slop; batch of 100 across 10 cells ⇒ up to 900 over
    the global limit. **Bigger sync batch = less chatter, more slop** — the same
    coordination/accuracy dial as everywhere in 11/15.
- Approaches in the wild: a central store (strong, chatty), sticky routing so a key always
  hits one limiter node (no coordination, but rebalancing breaks it — reuse 14), or
  gossip/approximate counters (eventually-consistent budget).

### 1.4 Fairness & burst
- **Per-key isolation** prevents one noisy tenant from starving others (RFC 6585 §4 explicitly
  notes the server may count "on a per-resource basis, across the entire server, or among a set
  of servers" and identify the user by credentials or cookie — **VERIFIED**). This is the
  rate-limit analog of Cluster C's **per-customer limits** (Google SRE — VERIFIED).
- **Burst vs sustained** are separate guarantees: token-bucket `B` vs `r`. Weighted/priority
  fairness (e.g. WFQ-style, or criticality tiers from Cluster C) lets important traffic keep its
  share under contention.

### 1.5 Where to enforce (the placement ladder)
Reuse 10 (proxy) / 03 (connection limits). Google SRE (cascading-failures, **VERIFIED**)
enumerates the layers: **reverse proxies / edge** (cheap, coarse, blocks abusive IPs / DoS
before they cost anything — reuse 16 CDN/edge), **load balancers** (drop on global overload,
indiscriminate or selective), and **individual tasks** (protect against load-balancer
fluctuations). Caveat (SRE, VERIFIED): "rate limiting often doesn't take overall service
health into account, it may not be able to stop a failure that has already begun, and simple
implementations are likely to leave capacity unused" — which is exactly why Cluster C's
health-aware *shedding* is needed in addition.

## 2. Foundational sources
- **VERIFIED (recomputation, `_recompute.py` A1–A5):** token-bucket burst/rate split; leaky-
  bucket smoothing+drop; fixed-window 2× boundary burst; sliding-log exactness vs O(limit);
  sliding-counter estimate + `prev·frac` error; distributed over-admit `(cells−1)·batch`.
- **VERIFIED (fetched primary):** RFC 6585 §4 — 429 status, `Retry-After`, per-resource /
  cross-server / set-of-servers counting, user identified by credentials or cookie
  (`meta/fetched_primaries/rfc6585.txt`).
- **VERIFIED (fetched primary):** Google SRE *Handling Overload* + *Addressing Cascading
  Failures* — per-customer limits, enforcement layers, "rate limiting doesn't see health"
  caveat (`meta/fetched_primaries/sre_handling_overload.txt`, `sre_cascading_failures.txt`).
- **Reuse (line-verified earlier):** 11 (no free global coordination), 14 (hot key/shard,
  sticky routing rebalance cost), 16 (hot-key, edge/CDN placement, coalescing), 10 (reverse
  proxy as the enforcement point), 03 (connection limits), 13 (queue latency bound for the
  leaky-bucket queue form).
- **`[UNVERIFIED]` (blocked / not fetched this session):** Stripe/Cloudflare/AWS/Envoy/Nginx
  `limit_req` exact algorithm docs and default knobs; the GCRA (generic cell rate algorithm)
  formulation; Redis cell-based rate-limiter (`CL.THROTTLE`) semantics; Lyft/Envoy global
  rate-limit service design; the classic ATM/leaky-bucket traffic-shaping literature.

## 3. "Why it's this way" — forcing functions
- **Capacity is finite and shared** ⇒ you must decide admission *before* the work, or the work
  decides it for you by failing (Cluster C). Rate limiting is the proactive valve.
- **Real traffic is bursty** ⇒ a pure rate cap is too strict; token bucket separates a *burst
  budget* (`B`) from a *sustained rate* (`r`) so legitimate spikes pass.
- **Exact accounting costs memory/coordination** ⇒ sliding-log exactness is O(limit) per key and
  a shared counter is a synchronous hot key; so production trades a little accuracy
  (sliding-counter, cell-based) for O(1) memory and no per-request round trip (A4/A5).
- **One tenant must not starve the rest** ⇒ per-key/per-customer isolation and fairness.
- **The valve must sit where it's cheapest to say no** ⇒ push enforcement toward the edge
  (reject before it costs CPU/RAM/FDs), the same "fail early and cheaply" rule as Cluster C.

## 4. Common misconceptions to preempt
- "Rate limiting and load shedding are the same." No: rate limiting is a *static, health-blind*
  admission cap (Cluster A); load shedding is *dynamic, health-aware* dropping under measured
  overload (Cluster C). SRE explicitly warns the static limiter "may not stop a failure already
  begun" and "leaves capacity unused" — **VERIFIED**.
- "Fixed-window counters are accurate." They admit up to **2× limit** at the boundary (A3).
- "Sliding-window-log is always best." It's exact but **O(limit) memory per key**; at scale the
  approximate counter (O(1)) is usually the right call (A4).
- "A shared Redis counter scales fine." It's a synchronous round trip per request and a hot
  key / SPOF (14/16); cell-based local limiting trades exactness for scale (A5).
- "Token bucket and leaky bucket are interchangeable." Token bucket *permits* bursts up to `B`;
  leaky bucket *smooths them away* (and the queue form adds latency). Different output shapes.
- "Rate limiting fixes overload." It's *necessary but not sufficient* — it's health-blind, so it
  must be paired with shedding + backpressure (B/C).

## 5. Best build-your-own target(s)
- **Four-algorithm limiter bench:** implement token bucket, leaky bucket, fixed window, sliding
  log, sliding counter; replay the same bursty trace through each; chart admitted-vs-rejected
  and measure the fixed-window 2× boundary leak and the sliding-counter `prev·frac` error live.
- **Distributed limiter:** local-token + periodic-sync across N cells; sweep `sync_batch` and
  measure global over-admission ≈ `(cells−1)·batch` (A5); compare to a shared-counter baseline's
  per-request latency.
- (Pairs with 10 own-proxy: enforce the limiter as a reverse-proxy middleware returning 429 +
  `Retry-After`.)

## 6. Open questions / gaps
- **Vendor specifics `[UNVERIFIED]`:** Envoy/Nginx/Cloudflare/Stripe/AWS API-Gateway exact
  algorithms + defaults; GCRA; Redis cell-based limiter; Lyft global rate-limit service. Fetch
  when those hosts are reachable; teach the mechanisms now, not the knob names.
- **Boundary discipline:** algorithms + admission valve live here (18A); *reactive* shedding +
  criticality live in 18C; backpressure/bounded-queue mechanics in 18B; queueing theory
  (`ρ→1`) is owned by 13; consistency of distributed counters is 11/15; edge placement is 16/10.
