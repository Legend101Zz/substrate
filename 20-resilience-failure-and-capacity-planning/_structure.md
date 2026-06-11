# 20 — Resilience, Failure, and Capacity Planning · _structure.md

**Identity:** the synthesis sub-course of Part II — it takes 18's overload controls + 19's signals/
SLOs/error-budgets and turns them into a discipline for surviving partial failure and planning
capacity. One sentence: you cannot prevent all faults, so bound their blast radius, add redundancy
sized by the math, verify it with chaos, and govern it with the error budget.

**Bespoke shape — "name → tolerate → pattern → quantify (failure as a discipline)."** NOT a
pattern grab-bag. The arc: **A — NAME the failure (fault→error→failure; partial failure; CAP) → B —
TOLERATE the tail (fan-out makes one slow leaf dominate p99; hedged/tied requests) → C — PATTERN
the defenses (the 18 patterns PLUS the isolation layer: cells & shuffle-sharding + chaos
engineering) → D — DO THE MATH (availability algebra, the correlated-failure correction, headroom
sizing).** Two threads bind it: "a slow node is worse than a dead node" (appears in all four) and
"correlation is the master enemy" (A names it, C reduces it, D prices it). 20 is the discipline that
WIRES the closed loop (19 senses → 18+C actuate → D sizes). Math heavily recomputed (38/38); six
primaries VERIFIED this session (Tail-at-Scale, AWS shuffle-sharding + backoff/jitter, Brewer,
Kleppmann, Netflix).

## Dependency position
- **Depends on:** 11 (FLP, partition undetectability, failure detectors, Byzantine 3m+1, no global
  clock), 12 (Byzantine Generals), 13 (fan-out, M/M/1 wall, P-K, USL, Little's Law, headroom, CO),
  14 (sharding, micro-partitioning, hot-shard replication), 15 (failover, split-brain, fencing,
  quorum), 16 (tainted cache results, stampede), 18 (timeouts/breakers/bulkheads/hedging/shedding/
  degradation/retry-storm/metastability), 19 (golden signals + error budget + burn rate as capacity
  signals).
- **Feeds into:** 21 (every case study has failure modes + a "degrade-to-something"; the resilience
  toolkit), Part III (agent failure modes, capacity for agentic systems).
- **Appendix links DOWN:** N-math (queueing/probability/availability algebra), L-consensus (BFT/
  failure detectors), O-cloud (AZ/region failure domains). 20 owns the resilience discipline + the
  reliability math.

## Chapter specs (3–5 lines each)
### A — name the failure
1. **The failure chain & partial failure** — fault → error → failure; partial failure is the DEFINING
   property of a distributed system (a slow node is indistinguishable from a dead one — FLP, 11).
   Taxonomy: crash / omission / timing(=tail) / Byzantine. The killer assumption is INDEPENDENCE;
   reality is correlation (shared failure domains).
2. **CAP as a failure choice** — a partition forces a PRE-DECIDED C-vs-A choice (Brewer; Kleppmann:
   the partition is an unchosen fault, CAP is narrow). Sets up that resilience ≠ preventing faults; it
   is preventing a fault from RECRUITING the rest of the system.

### B — tolerate the tail
3. **The tail dominates fan-out** — `1−0.99^100=63%`; latency ≥ the slowest component. The same
   redundancy that masks faults also masks VARIABILITY, at a faster time scale. (Tail-at-Scale,
   VERIFIED.)
4. **Tail-tolerance techniques** — hedged requests (fire a backup past a high percentile → small %
   extra: Dean's 994→50ms p99.9 at <5%/<1% extra) and tied requests (−43%/−38% p99, ~1% extra);
   micro-partitioning (10–100/machine), selective replication, latency-induced probation, canary
   requests, tainted partial results, synchronized disruption. Hedging ADDS load → stands down under
   18's shedding.

### C — pattern the defenses
5. **Resilience patterns (reuse) + the isolation layer** — timeouts/retries+jitter/breakers/
   bulkheads/shedding/degradation (18) PLUS blast-radius reduction: cells & shuffle-sharding shrink
   impact COMBINATORIALLY — plain sharding is linear `1/K`, shuffle is `1/C(n,k)` (C(8,2)=28 → 1/28
   → 7×; Route 53 k=4 → 730B shards, VERIFIED). Smaller cells need more relative headroom (efficiency
   vs containment).
6. **Chaos engineering** — redundancy = availability ONLY if tested; untested failover is hope. Chaos
   FINDS hidden correlation (Netflix Chaos/Latency/Gorilla monkeys, VERIFIED). The recklessness is
   shipping untested failover, not running chaos.

### D — do the math
7. **Availability algebra** — serial `∏aᵢ` (erodes — availability multiplies down in series), parallel
   `1−(1−a)^n` (each independent replica ≈ +nines). The utilization wall (13) makes nodes slow before
   they die → capacity is a reliability input.
8. **Correlation & headroom** — the correlated-failure correction: six nines → THREE nines (1001×
   worse, RECOMPUTED) — three replicas only give six nines IF independent. Headroom-to-survive-f =
   `f/n` (N+1/N+2); under-provisioning burns the error budget (19) through tail latency (B). Retry
   amplification `(1+r)^L=1024×` + metastability (reuse 18). Capacity planning is necessary but NOT
   sufficient (the 18 handoff, inverted).

## Paired build labs (/build — simulators + a chaos harness)
Fan-out simulator (N leaves with a latency distribution → p99 of the max; add hedged + tied requests;
measure tail collapse + % extra load; reproduce Dean's table by Monte-Carlo) → shuffle-shard assigner
(n workers, k-subset/customer; empirically measure full-collision vs `1/C(n,k)`; show 8→28 +
recursive sharding) → availability calculator (serial `∏aᵢ` + parallel `1−(1−a)^n` + correlated-
failure c-knob; watch six nines collapse to three) → capacity planner (λ, service time, target ρ*, f
→ node count + headroom + M/M/1 latency; cross-check Little's Law; couple to a chaos harness that
trips the breaker and tracks 19's burn rate).

## Diagrams needed
- The name→tolerate→pattern→quantify arc; "a slow node is worse than a dead node" as recurring motif.
- Fault→error→failure chain; failure taxonomy (crash/omission/timing/Byzantine).
- Fan-out tail (one slow leaf dominates p99); hedged + tied request timelines (% extra load).
- Plain sharding `1/K` (linear) vs shuffle-sharding `1/C(n,k)` (combinatorial); recursive sharding.
- Serial `∏aᵢ` erosion vs parallel `1−(1−a)^n` improvement.
- Correlated-failure correction (six nines → three nines, the c-knob).
- Headroom `f/n` (N+1/N+2); retry amplification `(1+r)^L`.
- The closed loop wired: 19 senses → 18+C actuate → D sizes → error-budget policy governs.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED PRIMARIES this session (`meta/fetched_primaries/`):** Tail-at-Scale (fan-out 63%, backup
  table 33→14ms / 994→50ms p99.9 at <5%/<1%, tied −43%/−38% ~1%, micro-partitioning, selective
  replication, probation, canary, tainted results, synchronized disruption); AWS shuffle-sharding
  (100%→1/K→1/C(n,k); C(8,2)=28→7×; Route 53 k=4→730B); AWS backoff/jitter (jitter breaks retry
  correlation, retry budgets, 4xx-vs-5xx retryability); Brewer PODC 2000 (CAP "at most two", BASE);
  Kleppmann 2015 (CAP narrow); Netflix Simian Army.
- **RECOMPUTED (38/38):** fan-out tail; hedge overhead = 1−deadline-percentile; hedged tail ≈ p²;
  Dean 994/50=19.88×; tied −43%/−38%; plain 1/K; C(8,2)=28→1/28→7×; C(2048,4)=730.9B; util wall;
  headroom C=D/ρ*; USL knee 98.49; serial ∏aᵢ=0.99501; parallel 1−(1−a)^n; **correlated six-nines→
  three-nines (1001×)**; headroom f/n; Little's-Law sizing → 5 servers; retry amplification (1+r)^L=
  1024× + 1/(1−r).
- **`[UNVERIFIED]` — book/spec attributions, non-load-bearing:** Avizienis 2004 (fault chain),
  Deutsch/Gosling Fallacies, Nygard *Release It!* (verified via 18 + AWS), Hystrix docs, Gunther USL
  book + Kleinrock pagination (from 13), a formal shuffle-shard overlap-distribution paper (combinatorics
  RECOMPUTED instead), cloud AZ-failure-correlation stats; Tail-at-Scale CACM pagination/DOI (deep
  per-figure factcheck deferred to Phase 2). Teach mechanisms now; do NOT harden specifics until fetched.
- **Still network-blocked (retried, STILL down):** CoDel (queue.acm.org 403; covered via 18+SEDA),
  raft.github.io (000; covered via 11/12), Gilbert-Lynch formal CAP proof (later VERIFIED in 21).
- **Boundary discipline:** queueing/probability/availability algebra → appendix N; BFT/failure
  detectors → 11 (+ L); AZ/region failure domains → O; the 18 patterns themselves → 18 (20 adds the
  isolation + math + chaos layer); golden signals/error budget → 19.
