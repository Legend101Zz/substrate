# 20 · Cluster C — resilience patterns, redundancy, cells & chaos (research brief)

> Phase-1 brief. NO course prose. PRIMARIES verified: AWS shuffle-sharding + AWS timeouts/retries/
> backoff + Netflix Simian Army. Reuses 18 (timeouts/breakers/bulkheads/hedging/shedding/degradation
> — line-verified), 15 (failover/quorum), 14 (sharding), 13 (capacity). Math → `_recompute.py`.

## 1. The pattern catalogue (each interrupts the fault→error→failure chain from A)
These mechanisms are LINE-VERIFIED in 18 already; 20 reuses them as the resilience toolkit and adds
the *isolation/redundancy* layer (cells, shuffle-sharding, chaos) that 18 did not cover.
- **Timeouts + deadline propagation** (18D): bound the wait so a slow dependency (B's tail) can't
  pin your threads. Without a timeout, partial failure (A) becomes total (thread-pool exhaustion).
- **Retries + backoff + jitter** (18C + AWS verified): mask transient faults, but **bounded** —
  exponential backoff to avoid hammering a recovering dependency; **jitter** to break the retry
  *correlation* that re-creates the overload (AWS verified: "if all failed calls back off to the
  same time, they cause contention again"). Retry **budgets** / token buckets cap amplification.
- **Circuit breakers** (18D, AWS verified "widely promoted"): stop calling a failing dependency
  entirely after an error threshold → prevents cascade (A §7). Nygard "Release It!" is the usual
  attribution — `[UNVERIFIED]` (book, no free primary); mechanism verified via 18 + AWS builders'.
- **Bulkheads** (18D): isolate resources (separate thread/connection pools per dependency) so one
  saturated dependency can't sink the whole ship. Named after ship compartments. Bounds blast
  radius *inside one process*.
- **Load shedding / graceful degradation** (18C): when overloaded, drop low-priority work and serve
  a degraded-but-up response (B's tainted partial results is the within-request version). Fail
  *partial*, not *total*.
- **Hedged / tied requests** (18D + B verified): tail tolerance as a resilience pattern.

## 2. Redundancy & failover (the "extra resources" from B §3, at fault time scale)
- **Redundancy levels**: N+1 (one spare beyond demand), N+2 (survive a second failure during repair
  or during a planned maintenance), 2N (full duplicate). The choice is a capacity/availability trade
  computed in Cluster D. Key caveat (A §4): redundancy only helps if the spare is in a *different
  failure domain* (independent), else common-mode fault kills both.
- **Failover** (reuse 15, line-verified): detect (failure detector, A §2) → elect/promote → reconfig.
  Risk = split-brain when the "failure" was a partition (15 fencing/quorum/STONITH). Failover is
  redundancy *actuated* — it inherits the false-positive risk of suspicion-based detection (A §2).
- **Isolation as redundancy's partner**: redundancy adds spares; isolation ensures a failure can't
  consume them all at once. Cells & shuffle-sharding (§3) are isolation machines.

## 3. Cells & shuffle-sharding (bounding blast radius — the math headline)
PRIMARY VERIFIED (`aws-shuffle-sharding.txt`, Colm MacCárthaigh, AWS Builders' Library):
- **No sharding**: one poison request / DDoS / flood cascades through all workers → blast radius =
  **100%** ("everything and everyone").
- **Plain sharding**: split fleet into K shards → blast radius = **1/K** (verified: "4 shards … 25%
  impact … much better than 100%"). Trade efficiency (more slack per shard) for scope.
- **Shuffle-sharding**: assign each customer a *virtual shard* = a random k-subset of n workers.
  Two customers collide *fully* only if they draw the *same* k-subset.
  - VERIFIED numbers: **8 workers, shard size 2 → C(8,2) = 28 combinations → blast radius 1/28 ≈
    3.6%, "7 times better than regular sharding"** (1/4). RECOMPUTE C(8,2)=28 and 28/4=7.
  - VERIFIED: **Route 53 = 2048 virtual name servers, shard of 4 → C(2048,4) ≈ 730 billion shuffle
    shards** → effectively per-customer isolation. RECOMPUTE C(2048,4) ≈ 7.3×10^11.
  - Deeper combinatoric (RECOMPUTE, the real isolation guarantee): probability two customers share
    **all** k workers = 1/C(n,k). Probability they **overlap in ≥1** worker is much higher but a
    fault on a shared worker is *survivable* if clients are fault-tolerant (verified: "at most one
    of another shuffle shard's workers will be affected" → the victim retries onto its non-
    overlapping workers). Expected overlap of two random k-subsets = k·k/n (hypergeometric mean) —
    RECOMPUTE. With clients that retry/are fault-tolerant, the *effective* full-impact blast radius
    is ~1/C(n,k). Verified: "recursive shuffle sharding" isolates a customer's customers.

## 4. Chaos engineering (failure injection as continuous verification)
PRIMARY VERIFIED (`netflix-simian-army.txt`, Netflix 2011):
- **Chaos Monkey**: randomly terminates instances *in production* during business hours → forces
  engineers to build services that survive instance loss (tests the A §2 "fail-stop" assumption for
  real, not on a slide).
- **Latency Monkey**: induces artificial delays + errors in client-server calls → simulates service
  *degradation* and partial failure (B's tail + Cluster A omission/timing failures) without killing
  the instance. Verified: lets you test if upstreams degrade gracefully.
- **Chaos Gorilla**: simulates an **entire AWS Availability Zone** outage → tests the correlated-
  failure / failure-domain story (A §4) at AZ granularity.
- Others verified: Conformity / Doctor / Janitor / Security Monkey / 10-18 Monkey. Thesis:
  **resilience is a property you must continuously *prove* by injecting failure, because untested
  failover/redundancy is just hope** (the redundancy math in D assumes the spare *works* — chaos is
  how you check). Gameday/fault-injection is the verification step in 20's loop.

## 5. The cross-cluster control loop (how 20 composes 18 + 19)
- 19 SENSES (Four Golden Signals, error-budget burn, queue depth, retry ratio, breaker state,
  latency percentiles — line-verified).
- 18 + this cluster ACTUATE (shed, break, hedge, fail over, degrade).
- 20 is the DISCIPLINE that wires them: define failure domains → bound blast radius (cells/shuffle-
  sharding) → add redundancy sized by D's math → verify with chaos → govern with the error-budget
  policy (19). Capacity (D) is the input that says *how much* redundancy/headroom each cell needs.

## 6. Common misconceptions
- "Retries improve reliability" — unbounded retries *cause* cascades (A §7); only bounded+jittered+
  budgeted retries help (AWS verified).
- "More shards = always better isolation" — plain sharding is linear (1/K); shuffle-sharding is
  combinatorial (1/C(n,k)) for the *same* workers (verified "exponentially better").
- "Redundancy = availability" — only if failures are independent (A §4) and the failover actually
  works (verify with chaos §4).
- "Chaos engineering is reckless" — it's controlled, in-prod, blast-radius-bounded experiments; the
  recklessness is shipping *untested* failover.
- "Graceful degradation = giving up" — it's choosing a partial failure over a total one (B §4c).

## 7. Build-your-own targets
- Shuffle-shard assigner: n workers, k-subset per customer; empirically measure full-collision rate
  vs 1/C(n,k); show the 8→28 and the recursive variant.
- Chaos harness for the capstone (28): kill/slow a dependency, assert the breaker trips + degraded
  response is served + error budget (19) tracks the burn.

## Sources
- VERIFIED this session: AWS "Workload isolation using shuffle-sharding" (`aws-shuffle-sharding.txt`)
  — 8→C(8,2)=28→1/28→7×, Route 53 2048-choose-4≈730B, recursive; AWS "Timeouts, retries, backoff
  with jitter" (`aws-timeouts-retries-backoff.txt`) — backoff/jitter/budgets/breakers/idempotency;
  Netflix "Simian Army" (`netflix-simian-army.txt`) — Chaos/Latency/Gorilla monkeys.
- REUSED (line-verified): 18 (timeouts, breakers, bulkheads, hedging, shedding, degradation, retry
  amplification), 15 (failover, split-brain, fencing, quorum), 14 (sharding), 13 (capacity/headroom).
- `[UNVERIFIED]` carried: Nygard "Release It!" (circuit-breaker/bulkhead/stability-pattern
  attribution; book, no free primary — mechanisms verified via 18+AWS); Hystrix docs; formal
  shuffle-sharding overlap-distribution paper (combinatorics RECOMPUTED here instead).
