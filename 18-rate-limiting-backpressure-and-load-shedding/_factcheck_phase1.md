# 18 — rate-limiting / backpressure / load-shedding — Phase-1 factcheck

> Validates the load-bearing claims of clusters A–D before reconciliation (RESEARCH_PROTOCOL
> step 5). Three buckets: **RECOMPUTE** (math re-derived in `_recompute.py`), **REUSE** (already
> line-verified in an earlier reconciled sub-course), **PRIMARY** (verified against a primary
> fetched this session). `[UNVERIFIED]` = carried forward, not load-bearing for the
> method/math. **Blockers: 0.**

## A. RECOMPUTE — `_recompute.py` (pure stdlib, 9/9 pass, exit 0)

| # | Claim | Result |
|---|-------|--------|
| A1 | Token bucket: long-run admit = min(arrival, refill); instantaneous burst ≤ capacity B; from full bucket burst admits exactly B | **VERIFIED** (empty burst 100→10; 5/s/100s→~510; full burst→10) |
| A2 | Leaky bucket: output smoothed to leak rate; admits ≤ depth, rest dropped | **VERIFIED** (burst 50, depth 10, 5/s → 10 served, 40 dropped, peak ≤ 6/s) |
| A3 | Fixed window admits up to 2·limit at boundary; sliding-window-log caps at exactly limit | **VERIFIED** (2·100=200; 1000 reqs/0.5s, limit 100 → exactly 100) |
| A4 | Sliding-window-counter est = curr + prev·(1−frac); worst over-admit = prev·frac; O(1) memory vs O(limit) log | **VERIFIED** (prev=100, frac=0.1 → est 90, over-admit 10) |
| A5 | Distributed counter worst over-admit = (cells−1)·sync_batch | **VERIFIED** (batch 1, 10 cells → 9; batch 100 → 900) |
| B1 | Bounded queue adds ≤ Q/drain latency; SRE 10×-pool → ~1.0 s, 0.5×-pool → 0.05 s | **VERIFIED** (reproduced both) |
| C1 | Retry amplification = 1/(1−r): .5→2×, .9→10×, .99→100×; 3-attempt cap & 10% budget bound it | **VERIFIED** |
| C2 | Goodput plateaus at capacity w/o retries; COLLAPSES below capacity with naive retries + reject cost | **VERIFIED** (3× retry + 0.5 cost → goodput 0 < 1000; worse as overload grows) |
| D1 | Adaptive throttling reject p = max(0,(req−K·acc)/(req+1)); K=2 tolerates 2×, K=1.1 throttles ~half | **VERIFIED** (req=acc→0; 200/100,K2→0; 300/100→100/301≈0.332) |

## B. PRIMARY — fetched + verified this session (`meta/fetched_primaries/`)

| Source | Claims verified | File |
|--------|-----------------|------|
| **RFC 6585 §4** (Nottingham & Fielding, Apr 2012) | 429 "Too Many Requests" = rate limiting; SHOULD include explanation; MAY include `Retry-After`; "does not define how the origin identifies the user nor how it counts" — per-resource / entire-server / set-of-servers; user by credentials or cookie; 429 MUST NOT be cached | `rfc6585.txt` |
| **Google SRE — Handling Overload** (Forero Cuervo) | "Pitfalls of QPS" (cost varies/drifts → poor metric; provision against CPU); per-customer limits (only misbehaving customers get errors under global overload); client-side **adaptive throttling** (2-min requests/accepts, reject p formula, K=2 default, K=1.1 aggressive, "reject one per processed" steady state, sporadic-client caveat); **criticality** 4 tiers (CRITICAL_PLUS/CRITICAL/SHEDDABLE_PLUS/SHEDDABLE) + "reject a criticality only when already rejecting all lower" + per-criticality stats; graceful **degradation** (partial corpus / stale local copy); retry handling (per-request budget = **3**, per-client budget = **10%**, attempt counter, "overloaded; don't retry") | `sre_handling_overload.txt` |
| **Google SRE — Addressing Cascading Failures** | resource-exhaustion cascade (thread starvation, missed RPC deadlines → wasted work + retries, GC death spiral, FD exhaustion); **queue in front of thread pool**, queue 10×pool@100ms→~1.0s wait, "queue ≤ 50% of pool, reject early"; **fail early and cheaply** (HTTP 503 past in-flight threshold); FIFO→**LIFO**/**CoDel [Nichols 2012]** under overload (drop work unlikely to be worth processing); enforce rate limits at reverse proxies / load balancers / individual tasks; "rate limiting doesn't take service health into account... may not stop a failure already begun... leaves capacity unused"; the **10,000-QPS retry-storm** worked example (100→200→300 QPS, goodput melts); "capacity planning is necessary but not sufficient" | `sre_cascading_failures.txt` |

## C. REUSE — mechanisms inherited from line-verified reconciled sub-courses (NOT re-derived)

- **13** — Little's Law, M/M/1 `W=S/(1−ρ)`, `ρ→1` ⇒ unbounded latency (the queueing wall behind
  B1 and all backpressure); tail latency + the knee (D adaptive limits, hedging); USL.
- **03** — TCP **flow control** = receiver window = credit scheme (B1.3 backpressure); **AIMD
  congestion control** (D1.6 adaptive concurrency); flow-vs-congestion distinction; connection
  limits.
- **17** — the queue as a buffer + consumer lag as backpressure signal (pull = built-in
  backpressure); retry budgets, capped exponential backoff **+ jitter**, DLQ for poison;
  idempotency (safe retries).
- **16** — jitter + request coalescing (reduce upstream load); stale-serve as degradation; hot
  key.
- **14** — hot shard / celebrity key, sticky routing + rebalance cost (distributed limiter
  placement, 18A).
- **11** — no global coordination for free (distributed counter slop, 18A; adaptive throttling
  local decisions, 18D).
- **15** — stale replica = degraded read (brownout, 18C).
- **10** — reverse proxy as the enforcement point for rate limits / connection caps.

## D. `[UNVERIFIED]` — carried forward (NOT load-bearing for method/math; fetch when reachable)

- **A:** Envoy/Nginx `limit_req`/Cloudflare/Stripe/AWS-API-Gateway exact algorithms + default
  knobs; GCRA; Redis cell-based limiter (`CL.THROTTLE`); Lyft global rate-limit service.
- **B:** **SEDA** paper (Welsh, Culler & Brewer, SOSP 2001) — exact stage-controller equations +
  overload graphs (Harvard mirror + USENIX unreachable this session); Reactive Streams spec
  (`request(n)` demand, JDK `Flow`); Akka/Reactor/RxJava/Netty/gRPC-HTTP2 flow-control defaults.
- **C:** **CoDel** paper (Nichols & Jacobson, "Controlling Queue Delay," ACM Queue/CACM 2012) —
  named by SRE, exact target/interval not fetched; AWS Builders' Library "Timeouts, retries and
  backoff with jitter" (Brooker) — blocked this session.
- **D:** Netflix **Hystrix** (circuit breaker + bulkhead) + **concurrency-limits**
  (gradient/Little's-Law AIMD) docs; resilience4j; Envoy circuit-breaking/outlier-detection
  knobs; Nygard *Release It!* (circuit-breaker/bulkhead pattern origin); Dean & Barroso "The Tail
  at Scale" CACM 2013 (hedged/tied requests — also carried by 13/20).

## E. Verdict
- **0 blockers.** Every load-bearing claim is verified by **recomputation** (9/9), **reuse** of
  line-checked 03/11/13/14/15/16/17/10, or a **fetched primary** (RFC 6585 + two Google SRE
  chapters). The remaining gaps are vendor/paper *attributions* (SEDA, CoDel, Hystrix, GCRA,
  Tail-at-Scale) — none changes the mechanism or the math; none may harden into Phase-2 prose
  until fetched. 18 is honest to reconcile.

## F. Network status this session (probed)
- **HTTP 200:** `rfc-editor.org` (RFC 6585 fetched), `sre.google` (3 SRE chapters reachable;
  Handling Overload + Addressing Cascading Failures fetched + extracted).
- **HTTP 000 / 404 (still blocked):** `usenix.org` (000 — SEDA/NSDI/OSDI mirrors unreachable),
  Harvard `eecs.harvard.edu` SEDA PDF (000), `aws.amazon.com/builders-library` (000). arxiv,
  dl.acm, research.google, raft.github.io, postgresql.org, kafka.apache.org,
  allthingsdistributed, martin.kleppmann — assumed still 000 (not re-probed individually this
  session; carry forward).

## UPGRADE 2026-06-10 (Wave 8, observability session) — SEDA finally fetched + VERIFIED
The carry-forward `[UNVERIFIED]` "SEDA SOSP'01 (Welsh) [Harvard+usenix-nonlegacy 000]" in
Cluster B is now **VERIFIED** from a fetched primary. Network healed:
`https://www.sosp.org/2001/papers/welsh.pdf` (and `people.eecs.berkeley.edu/~brewer/
papers/SEDA-sosp.pdf`) returned HTTP 200. Saved to `meta/fetched_primaries/seda-sosp01.{pdf,txt}`.
Verified verbatim: stage = event handler + bounded incoming event queue + thread pool, each
managed by a controller pulling batches off its queue and enqueuing onto other stages' queues
(S3.2); well-conditioned = graceful degradation, throughput plateaus at saturation rather than
collapsing, linear response-time penalty (S2); dynamic resource controllers do thread-pool
sizing + event batching + admission control (Abstract/S3.1); explicit/bounded queues enable
per-stage load conditioning by thresholding/filtering (S2/S3). This confirms 18B's stage/queue/
thread-pool/controller model and the goodput-plateau thesis (18B/18C). Receipt:
`meta/fetched_primaries/_VERIFIED_2026-06-10_observability.md` (BONUS UPGRADE section).
Nothing erased; remaining 18 `[UNVERIFIED]` (CoDel 403, Hystrix/resilience4j/Envoy knobs,
GCRA, Redis cell limiter, Lyft RLS, Reactive Streams, AWS builders', Nygard) carried forward.
Deep per-figure SEDA factcheck deferred to 18 Phase 2.
