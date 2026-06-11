# 20 · Phase-1 factcheck — resilience-failure-and-capacity-planning

> Method: every load-bearing claim is either (a) RECOMPUTED in `_recompute.py` (38/38 pass),
> (b) VERIFIED verbatim against a primary fetched this session to `meta/fetched_primaries/`,
> (c) REUSED from a previously line-verified sub-course (11/12/13/14/15/16/18/19), or
> (d) flagged `[UNVERIFIED]` and carried forward (must not harden into Phase-2 prose).
> 0 blockers. No raccoon-shaped completeness.

## Primaries fetched + verified this session (network heal continued)
| source | file | what it anchors |
|--------|------|-----------------|
| Dean & Barroso, "The Tail at Scale" | `tail-at-scale-cacm2013.{pdf,txt}` | Cluster B: fan-out 63%, hedged/tied requests + measured tables, micro-partitioning, selective replication, probation, tainted results |
| AWS Builders', "Workload isolation using shuffle-sharding" | `aws-shuffle-sharding.{html,txt}` | Cluster C: C(8,2)=28→1/28→7×, Route 53 2048-choose-4≈730B, plain-shard 1/K, recursive |
| AWS Builders', "Timeouts, retries, and backoff with jitter" | `aws-timeouts-retries-backoff.{html,txt}` | Clusters A/C: backoff, jitter, retry budgets, breakers, multi-layer amplification, idempotency |
| Brewer, "Towards Robust Distributed Systems" (PODC 2000) | `brewer-podc-2000.{pdf,txt}` | Clusters A/D: CAP "at most two", forfeit C/A/P, BASE |
| Kleppmann, "Please stop calling databases CP or AP" (2015) | `kleppmann-cap-2015.{html,txt}` | Cluster A: CAP as a narrow theorem; partition = unchosen fault |
| Netflix, "The Netflix Simian Army" (2011) | `netflix-simian-army.{html,txt}` | Cluster C: Chaos/Latency/Gorilla monkeys = failure injection as verification |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_resilience.md`.

## Cluster A — failure models & partial failure
- VERIFIED verbatim (`brewer-podc-2000.txt`): CAP "at most two of these properties"; Forfeit
  Partitions / Availability / Consistency; BASE = Basically Available, Soft state, Eventual
  consistency.
- VERIFIED (`kleppmann-cap-2015.txt`): CAP is a narrow formal result; poor general design taxonomy;
  a partition is a fault you don't choose.
- VERIFIED (`aws-timeouts-retries-backoff.txt`): cascade mechanics — retries amplify load on an
  overloaded dependency; circuit breakers "widely promoted"; idempotency required to retry safely;
  4xx-not-retryable / 5xx-maybe.
- RECOMPUTED (A1): multi-layer retry amplification (1+r)^L = 1024× for 5 layers×3 retries; single-
  layer 1/(1−r).
- REUSED (line-verified): 11 (FLP, partition undetectability, failure detectors completeness/
  accuracy, Byzantine 3m+1, no global clock); 12 (Byzantine Generals primary); 18 (retry storm,
  queue collapse, goodput collapse, metastability — all line-verified there); 13 (timing failure =
  tail); 15 (failover, split-brain, fencing).
- `[UNVERIFIED]` carried (none load-bearing): Avizienis et al. IEEE TDSC 2004 (fault/error/failure
  chain — standard, no free primary fetched); Deutsch/Gosling "Fallacies of Distributed Computing"
  exact source; Gilbert–Lynch 2002 formal CAP proof (still blocked — we hold Brewer's keynote +
  Kleppmann's critique instead).

## Cluster B — the tail at scale
- VERIFIED verbatim (`tail-at-scale-cacm2013.txt`): "touch 100 → 63% take ≥1 sec"; "overall latency
  ≥ slowest component"; backup-request table (33→14 ms avg, 994→50 ms p99.9, "<5%"/"<1%" extra);
  tied-request table (−43% / −38% p99, "~1% extra disk reads"); micro-partitioning (10–100/machine);
  selective replication ("Chinese docs"); latency-induced probation; canary requests; tainted
  partial results ("99.9% in 200 ms > 100% in 1000 ms"); synchronized disruption.
- RECOMPUTED (B1–B4): fan-out 1−0.99^100=0.634; hedge overhead = 1−deadline-percentile (5%/1%);
  hedged effective tail ≈ p²; Dean p99.9 994/50=19.88×; tied −43%/−38% from the tables.
- REUSED (line-verified): 13 (fan-out identity, percentiles, coordinated omission), 18D (hedged/tied
  requests, latency-keyed breaker), 19 (latency percentiles signal), 14 (micro-partitioning, hot-
  shard replication), 16 (tainted cache results).
- `[UNVERIFIED]` carried (non-load-bearing): exact CACM-2013 article pagination/DOI (we hold the
  companion Dean talk deck whose numbers match CACM; deep per-figure factcheck deferred to Phase 2).

## Cluster C — resilience patterns, redundancy, cells & chaos
- VERIFIED verbatim (`aws-shuffle-sharding.txt`): no-sharding blast radius 100%; plain 4 shards →
  25%; 8 workers shard-of-2 → "28 unique combinations" → 1/28 → "7 times better"; Route 53 "2048
  virtual name servers", shard-of-4 → "730 billion possible shuffle shards"; "at most one of
  another shuffle shard's workers will be affected"; recursive shuffle-sharding; Infima library.
- VERIFIED verbatim (`aws-timeouts-retries-backoff.txt`): exponential backoff; jitter breaks retry
  correlation ("if all failed calls back off to the same time, they cause contention again");
  per-host deterministic jitter for scheduled work; retry budgets/token buckets; circuit breakers.
- VERIFIED (`netflix-simian-army.txt`): Chaos Monkey (kills prod instances), Latency Monkey (induces
  latency/errors → degradation + partial failure), Chaos Gorilla (kills an entire AWS AZ), plus
  Conformity/Doctor/Janitor/Security/10-18 monkeys.
- RECOMPUTED (C1–C5): 1/K plain; C(8,2)=28, 1/28, 7×; C(2048,4)=730,862,190,080≈730.9B; full-
  collision 1/C(n,k); expected k-subset overlap k²/n.
- REUSED (line-verified): 18 (timeouts, breakers, bulkheads, hedging, shedding, degradation), 15
  (failover/split-brain/fencing/quorum), 14 (sharding), 13 (capacity/headroom).
- `[UNVERIFIED]` carried (non-load-bearing): Nygard "Release It!" circuit-breaker/bulkhead/stability-
  pattern attribution (book, no free primary — mechanisms verified via 18 + AWS builders'); Hystrix
  docs; a formal shuffle-shard overlap-distribution paper (we RECOMPUTED the combinatorics instead).

## Cluster D — capacity planning & reliability math
- RECOMPUTED (D1–D8, all in `_recompute.py`): utilization wall 1/(1−ρ) ladder (2/5/10/20×);
  headroom provisioning C=D/ρ\* (8000/0.8=10000); USL knee N\*=√((1−α)/β)=98.49; serial
  availability ∏aᵢ (0.999^5=0.99501); parallel 1−(1−a)^n (2 nines→4, 3→6); **correlated-failure
  correction collapsing six nines to ~three nines (1001× worse unavailability)** — the headline
  result; headroom-to-survive-f = f/n (N+1/N+2); Little's-Law sizing L=λW + N+1 → 5 servers.
- VERIFIED context (`brewer-podc-2000.txt`): CAP bounds what "available" means during a partition
  (D §6 / A §8).
- REUSED (line-verified + recomputed in 13): M/M/1 wall, M/G/1 P-K variance term, USL knee, Little's
  Law, capacity loop, coordinated omission. REUSED (line-verified in 19): error budget = (1−SLO)·
  window as a capacity-shortfall signal.
- `[UNVERIFIED]` carried (non-load-bearing): Gunther USL book pagination; Kleinrock *Queueing
  Systems v1* (both carried from 13); cloud-provider AZ-failure-correlation statistics.

## Carry-forward still-blocked primaries (retried this session — STILL blocked)
- CoDel — `queue.acm.org` HTTP **403** (deadline-drop / bounded-queue already covered via 18 + SEDA).
- `raft.github.io/raft.pdf` HTTP **000** (Raft consensus already line-verified via Lamport primaries
  in 11/12; not load-bearing for 20).
- Gilbert–Lynch 2002 formal CAP proof (still blocked; Brewer keynote + Kleppmann critique held).

## Verdict
20 coverage is honest and primary-anchored on its load-bearing core: Tail-at-Scale + AWS shuffle-
sharding + AWS backoff/jitter + Brewer CAP + Kleppmann + Netflix Simian Army all fetched & verified
this session, and 38/38 math claims recomputed (including the correlated-failure result that is the
intellectual punchline of the whole sub-course). Reconcile into `_research.md`. Residual
`[UNVERIFIED]` items are non-load-bearing book/spec attributions, carried forward.
