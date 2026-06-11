# 20 · resilience-failure-and-capacity-planning — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). Synthesizes the four cluster files per
> ADR-001. Full depth lives in the cluster files; this file is the cross-cluster spine, consolidated
> sources, and the gap ledger. Math: `_recompute.py` (38/38 pass). Primaries fetched this session:
> Tail-at-Scale, AWS shuffle-sharding, AWS backoff/jitter, Brewer CAP keynote, Kleppmann CAP blog,
> Netflix Simian Army — in `meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_resilience.md`).

Cluster files:
- `_research_failure-models-and-partial-failure.md` (A)
- `_research_the-tail-at-scale.md` (B)
- `_research_resilience-patterns-and-redundancy.md` (C)
- `_research_capacity-planning-and-reliability-math.md` (D)
Factcheck: `_factcheck_phase1.md`. Recompute: `_recompute.py`.

---

## 1. The spine (how the clusters compose)
20 is the **synthesis sub-course of Part II**: it takes 18's overload controls + 19's signals/SLOs/
error-budgets and turns them into a *discipline* for surviving partial failure and planning capacity.
The arc is one sentence: **you cannot prevent all faults, so bound their blast radius, add redundancy
sized by the math, verify it with chaos, and govern it with the error budget.**

1. **Name the failure** (A) — fault→error→failure chain; partial failure is the defining property of
   a distributed system (a slow node is indistinguishable from a dead one — FLP, reuse 11). Taxonomy:
   crash / omission / timing(=tail) / Byzantine. The killer assumption is *independence*; reality is
   *correlation*. CAP says a partition forces a pre-decided C-vs-A choice.
2. **Tolerate the tail** (B) — fan-out makes one slow leaf dominate p99 (1−0.99^100=63%). The same
   redundancy that masks faults also masks variability, at a faster time scale: hedged & tied
   requests, micro-partitioning, selective replication, latency-induced probation, tainted results.
3. **Pattern the defenses** (C) — timeouts/retries+jitter/breakers/bulkheads/shedding/degradation
   (reuse 18) PLUS the isolation layer: cells & shuffle-sharding shrink blast radius combinatorially
   (C(8,2)=28 → 1/28 → 7×; Route 53 → 730B shards); chaos engineering proves the defenses actually
   work.
4. **Do the math** (D) — utilization wall, headroom, serial ∏aᵢ (erodes), parallel 1−(1−a)^n (each
   independent replica ≈ +nines), the **correlated-failure correction** (six nines → three nines),
   and headroom-to-survive-f = f/n. Capacity is a reliability input: under-provisioning burns error
   budget (19) through tail latency (B).

## 2. Cross-cluster reconciliations (where clusters meet)
- **A slow node is worse than a dead node** — the single thread tying A (timing failure), B (tail
  dominates fan-out), C (latency-induced probation = breaker keyed on latency), D (the utilization
  wall makes nodes slow before they die). Verified once (Dean), reused four ways.
- **Correlation is the master enemy** — A names it (shared failure domains), C reduces it (cells/
  shuffle-sharding/AZ spread; jitter de-correlates retries; chaos *finds* hidden correlation), D
  prices it (the c-knob collapses six nines to three — RECOMPUTED, 1001× worse). One concept, three
  consequences.
- **Redundancy = tail tolerance = capacity headroom = the same budget** — B §3 (extra resources buy
  both fault and variability tolerance) reconciles with D §5 (headroom f/n IS the redundancy slack).
  Hedged requests (B) and N+1 capacity (D) spend the same coin at different time scales.
- **Blast radius is the accounting unit** — A defines it, C shrinks it (1/K → 1/C(n,k)), D prices
  the trade (smaller cells need more relative headroom f/n → efficiency vs containment, the exact
  AWS "trade efficiency for scope of impact").
- **The closed control loop** — 19 SENSES (golden signals, burn rate, queue depth, breaker state),
  18+C ACTUATE (shed/break/hedge/fail over/degrade), 20 is the discipline that wires them and D
  sizes the redundancy. The error-budget policy (19) is the governor.
- **Cascade vs single fault** (A §7) — the whole reason 20 exists: resilience ≠ preventing faults; it
  is preventing a fault from *recruiting* the rest of the system (retry amplification (1+r)^L=1024×,
  metastability — reuse 18, RECOMPUTED).
- **Jitter vs synchronized disruption** — opposite tactics for the same goal: AWS jitter
  *de-synchronizes load* (break retry correlation); Dean's synchronized disruption *de-synchronizes
  the tail* (one shared blip beats many random ones at high fan-out). Both manage correlation.

## 3. Load-bearing facts, by provenance
**VERIFIED from primaries fetched this session** (`meta/fetched_primaries/`):
- Tail-at-Scale: fan-out 63% (=1−0.99^100); "latency ≥ slowest component"; backup table (33→14 ms
  avg, 994→50 ms p99.9, <5%/<1% extra); tied table (−43%/−38% p99, ~1% extra reads); micro-
  partitioning 10–100/machine; selective replication; latency-induced probation; canary requests;
  tainted partial results; synchronized disruption.
- AWS shuffle-sharding: 100% (no shard) → 1/K (plain) → 1/C(n,k) (shuffle); C(8,2)=28→1/28→7×;
  Route 53 2048 vnames, k=4 → 730B; "at most one of another shuffle shard's workers affected";
  recursive shuffle-sharding.
- AWS backoff/jitter: exponential backoff; jitter breaks retry correlation; per-host deterministic
  jitter; retry budgets/token buckets; breakers; idempotency-to-retry; 4xx-vs-5xx retryability.
- Brewer PODC 2000: CAP "at most two"; forfeit C/A/P; BASE. Kleppmann 2015: CAP is narrow; partition
  = unchosen fault. Netflix: Chaos/Latency/Gorilla monkeys.

**RECOMPUTED** (`_recompute.py`, 38/38): fan-out tail; hedge overhead = 1−deadline-percentile;
hedged tail ≈ p²; Dean 994/50=19.88×; tied −43%/−38%; plain 1/K; C(8,2)=28/1/28/7×; C(2048,4)=730.9B;
full-collision 1/C(n,k); overlap k²/n; util wall 2/5/10/20×; headroom C=D/ρ\*; USL knee 98.49; serial
∏aᵢ=0.99501; parallel 1−(1−a)^n; **correlated-failure six-nines→three-nines (1001×)**; headroom f/n
(N+1/N+2); Little's-Law sizing → 5 servers; retry amplification (1+r)^L=1024× + 1/(1−r).

**REUSED from line-verified prior sub-courses**: 11 (FLP, partition undetectability, failure
detectors, Byzantine 3m+1, no global clock), 12 (Byzantine Generals), 13 (fan-out, M/M/1 wall, M/G/1
P-K, USL, Little's Law, headroom, coordinated omission), 14 (sharding, micro-partitioning, hot-shard
replication), 15 (failover, split-brain, fencing, quorum), 16 (tainted cache results, stampede),
18 (timeouts, breakers, bulkheads, hedging, shedding, degradation, retry storm, metastability),
19 (golden signals, error budget, burn rate as capacity signal).

## 4. Common misconceptions (consolidated)
- A slow node is harmless (no — dominates fan-out p99); optimise the average (tails); hedging doubles
  load (fire at high percentile ⇒ small %, ~1% with cancellation); retries improve reliability
  (unbounded retries cause cascades); more shards = better isolation (plain is linear 1/K, shuffle is
  combinatorial 1/C(n,k)); three replicas = six nines (only if independent — correlation dominates);
  redundancy = availability (untested failover is hope — verify with chaos); 100% utilization is
  efficient (latency cliff); adding nodes always adds throughput (USL knee reverses it); availability
  adds across dependencies (it multiplies and erodes in series); graceful degradation = giving up
  (it's choosing partial over total failure); chaos engineering is reckless (the recklessness is
  shipping untested failover); randomize background jobs (synchronize them at high fan-out).

## 5. Build-your-own targets
- Fan-out simulator: N leaves with a latency distribution → p99 of the max; add hedged + tied
  requests; measure tail collapse and % extra load; reproduce Dean's table by Monte-Carlo.
- Shuffle-shard assigner: n workers, k-subset/customer; empirically measure full-collision vs
  1/C(n,k); show 8→28 and recursive sharding.
- Availability calculator: serial ∏aᵢ + parallel 1−(1−a)^n + correlated-failure c-knob (watch six
  nines collapse to three).
- Capacity planner: λ, service time, target ρ\*, f → node count + headroom + M/M/1 latency; cross-
  check Little's Law; couple to a chaos harness that trips the breaker and tracks 19's burn rate.

## 6. Open questions / gaps (carry-forward `[UNVERIFIED]` — do NOT harden into prose)
- **Book/spec attributions (non-load-bearing):** Avizienis et al. IEEE TDSC 2004 (fault/error/
  failure chain — standard, no free primary); Deutsch/Gosling "Fallacies of Distributed Computing"
  exact source; Nygard "Release It!" (circuit-breaker/bulkhead/stability patterns — mechanisms
  verified via 18 + AWS builders'); Hystrix docs; Gunther USL book + Kleinrock *Queueing Systems v1*
  pagination (carried from 13); a formal shuffle-shard overlap-distribution paper (combinatorics
  RECOMPUTED instead); cloud-provider AZ-failure-correlation statistics.
- **CACM-2013 article pagination/DOI for Tail-at-Scale** (we hold the matching Dean talk deck; deep
  per-figure factcheck deferred to Phase 2).
- **Still network-blocked (retried this session, STILL down):** CoDel ACM Queue'12 (queue.acm.org
  403), raft.github.io (000), Gilbert–Lynch 2002 formal CAP proof. CoDel/Raft are already covered via
  18+SEDA and 11/12 respectively; not load-bearing for 20.
- **NEWLY UNBLOCKED + verified this session:** AWS Builders' Library (shuffle-sharding + backoff/
  jitter), Brewer PODC 2000 keynote, Kleppmann CAP blog, Netflix Simian Army.
