# 20 · Cluster B — the tail at scale (research brief)

> Phase-1 brief. NO course prose. PRIMARY fetched + verified: `meta/fetched_primaries/
> tail-at-scale-cacm2013.{pdf,txt}` (Dean & Barroso). Reuses 13 (fan-out tail, percentiles,
> coordinated omission), 18 (hedging as a within-request controller), 19 (latency percentiles as
> the signal). All math → `_recompute.py`.

## 1. The core theorem: fan-out amplifies the tail
Dean, Tail-at-Scale (VERIFIED verbatim, `tail-at-scale-cacm2013.txt`):
> "Server with 1 ms avg. but 1 sec 99%ile latency — touch 1 of these: 1% of requests take ≥1 sec;
>  touch 100 of these: 63% of requests take ≥1 sec."
- Mechanism: a root request fans out to N leaves and must wait for **the slowest**. If each leaf
  independently exceeds threshold T with probability p, then
  **P(at least one slow) = 1 − (1−p)^N.**
- RECOMPUTE: p=0.01, N=100 → 1 − 0.99^100 = 0.634 ≈ **63%** (matches the paper). Same identity as
  13's fan-out tail and 14's scatter-gather tail — verified once, reused everywhere.
- Consequence (verified): **"Overall latency ≥ latency of slowest component."** The p99 of the
  *whole* is driven by the p99 of *each leaf* × the fan-out. This is why **a slow node is worse than
  a dead node**: a dead leaf is removed; a slow leaf stays in every fan-out and taxes the tail.

## 2. Where variability comes from (why you cannot just "fix" the slow server)
Verified (`tail-at-scale-cacm2013.txt`): squashing all variability is "not tenable at large scale:
need to share resources." Sources of latency variability listed in the deck: shared resources
(CPU/network contention from co-tenants), background daemons (log compaction → reuse 06/07 LSM, 16),
queueing (13 M/M/1 wall), GC pauses (05), maintenance, power/sleep states, "wimpy cores → higher
fan-out → more variability." **Forcing function: at scale, tail latency is structural, not a bug to
exterminate — so you *tolerate* it, the same way you tolerate faults with redundancy.**

## 3. Faults vs variability (the framing that organises the techniques)
Verified verbatim: "Tolerating faults: rely on extra resources … make a reliable whole out of
unreliable parts. Tolerating variability: use these same extra resources … make a *predictable*
whole out of *unpredictable* parts. Time scales very different: variability = 1000s of
disruptions/sec at ms scale; faults = 10s of failures/day at tens-of-seconds scale." → 20's
unifying idea: **the same redundancy that buys fault tolerance (D) also buys tail tolerance, just at
a different time scale.**

## 4. Within-request adaptation (right-now, while the user waits)
### 4a. Hedged / backup requests (the headline technique)
Verified (`tail-at-scale-cacm2013.txt`): send the request, and if no reply by a deadline (e.g. p95),
send a **backup** to a second replica; take the first to answer. Measured in-memory BigTable lookup
(1000 keys / 100 tablets):
| policy | avg | p95 | p99 | p99.9 |
|--------|-----|-----|-----|-------|
| No backups | 33 ms | 24 ms | 52 ms | **994 ms** |
| Backup after 10 ms | **14 ms** | 20 ms | 23 ms | **50 ms** |
| Backup after 50 ms | 16 ms | 57 ms | 63 ms | 68 ms |
- VERIFIED quote: "10 ms delay: <5% extra requests; 50 ms delay: <1%." → **~20× p99.9 improvement
  for <5% extra load.** RECOMPUTE: send the backup at the p95 deadline → only ~5% of requests ever
  fire a backup (by construction p95 ⇒ 5% exceed it), so the load overhead ≈ (1−deadline_percentile).
- RECOMPUTE the hedging tail model: with the backup, the request is slow only if **both** the
  primary AND the backup are slow → effective tail ≈ p² (if independent), e.g. p=0.01 → 0.0001.

### 4b. Tied requests (backup with cross-server cancellation)
Verified: send to two replicas; each request carries the identity of the other; whichever server
*starts* the work tells the other to cancel ("Server 2: Starting req 9"). Measured DFS read:
| state | policy | p50 | p90 | p99 | p99.9 |
|-------|--------|-----|-----|-----|-------|
| Mostly idle | no backups | 19 | 38 | 67 | 98 ms |
| Mostly idle | tied @2ms | 16 | 28 | 38 | 51 ms (**−43% p99**) |
| +Terasort | no backups | 24 | 56 | 108 | 159 ms |
| +Terasort | tied @2ms | 19 | 35 | 67 | 108 ms (**−38% p99**) |
- VERIFIED: "Backups cause about ~1% extra disk reads"; "Backups w/ big sort job gives same read
  latencies as no backups w/ idle cluster." Cross-server cancellation is what keeps the duplicate
  cheap → directly extends 18D's hedged-requests cluster with the *cancellation* mechanism.

### 4c. Other within-request techniques (verified, listed)
- **Canary requests**: send to one node first; if it fails fast (e.g. crashes on a poison query),
  don't fan out to 1000s → protects against data-dependent correlated failure (Cluster A).
- **Tainted partial results**: "search 99.9% of docs in 200 ms better than 100% in 1000 ms";
  proactively abandon slow subsystems, mark results tainted in caches (reuse 16). = graceful
  degradation (Cluster C) applied within one request.

## 5. Cross-request adaptation (seconds-to-minutes time scale)
Verified techniques:
- **Fine-grained dynamic (micro-)partitioning**: many more partitions than machines (10–100/machine,
  "e.g. BigTable, GFS"). Lets the system shed load in small increments and recover failures fast
  (many machines each recover one partition) → reuse 14 (partitioning) + the recovery-speed argument
  feeds Cluster D capacity.
- **Selective replication**: detect hot items, make more replicas (static or dynamic — "more
  replicas of Chinese docs as Chinese query load rises") → reuse 14 hot-shard/celebrity + 15
  read-replicas.
- **Latency-induced probation**: "Non-intuitive: remove capacity under load to improve latency" —
  take a slow server out of rotation, keep sending it a shadow request stream, return it when its
  latency recovers. = a circuit breaker (18) keyed on *latency* not errors.
- **Synchronized disruption**: counter-intuitively, *synchronize* background-task blips ("on the
  dot every 5 min") rather than randomize, because with high fan-out, randomized blips mean at any
  instant ≥1 machine is slow → the tail is always hit. One synchronized blip < many unsynchronized.
  (Note: contrast with AWS *jitter* for retries in Cluster A — jitter de-synchronizes *load*;
  synchronized disruption de-synchronizes the *tail*. Both manage correlation, opposite directions.)

## 6. Common misconceptions
- "Optimise the average" — averages hide the tail that fan-out amplifies (reuse 13/19).
- "A slow node is harmless if it eventually answers" — at fan-out N it dominates p99 (§1).
- "Hedging doubles load" — no; fire at a high percentile ⇒ small % overhead, with cancellation ~1%.
- "More replicas just for durability" — replicas also cut the tail (selective replication, hedging).
- "Randomize background jobs to spread load" — for high fan-out, synchronize them instead (§5).

## 7. Build-your-own targets
- Fan-out simulator: N leaves, per-leaf latency distribution → measure p99 of the max; add hedged +
  tied requests, measure the tail collapse and the % extra load.
- Reproduce the Dean table numerically (Monte-Carlo) and compare to the paper's measured table.

## Sources
- VERIFIED this session: Dean & Barroso, "The Tail at Scale" (`tail-at-scale-cacm2013.{pdf,txt}`) —
  every quoted number above is verbatim from the fetched text.
- REUSED (line-verified): 13 (fan-out 1−(1−p)^N, percentiles, coordinated omission, M/M/1 tail), 18D
  (hedged/tied requests, latency-keyed circuit breaker), 19 (latency percentiles as the signal),
  14 (micro-partitioning, hot-shard selective replication), 16 (tainted cache results).
- `[UNVERIFIED]` carried: the CACM 2013 *article* pagination/DOI (we hold the companion talk deck
  text, which matches CACM's numbers; deep per-figure factcheck deferred to Phase 2).
