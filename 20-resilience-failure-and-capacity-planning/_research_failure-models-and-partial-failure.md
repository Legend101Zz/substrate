# 20 · Cluster A — failure models & partial failure (research brief)

> Phase-1 brief. NO course prose. Mechanisms-first, sources cited, math flagged for `_recompute.py`.
> This is the vocabulary cluster: it gives 20 the precise language of failure that the other three
> clusters (tail, patterns, capacity math) all reuse. Reuses 11 (FLP/partitions/fault taxonomy),
> 12 (Byzantine), 18 (cascading failure/retry storms), 13 (tails as a failure mode), 15 (failover).

## 1. Fault → error → failure (the causal chain)
The load-bearing distinction (textbook dependability taxonomy, Avizienis et al. 2004 — `[UNVERIFIED]`
source, but the chain is standard):
- **Fault** = the root cause / defect (a bad disk sector, a null-deref bug, a cut fibre, a config
  typo). A fault can lie *dormant*.
- **Error** = the fault *activated* — the system is now in an incorrect internal state (corrupted
  page, wrong variable, stuck thread).
- **Failure** = the error *propagates to the service boundary* — the system no longer delivers its
  specified behaviour (wrong answer, timeout, 5xx).
Why it matters: **fault tolerance = stopping the fault→error→failure propagation.** Every pattern in
Cluster C is an interrupt placed somewhere on this chain (redundancy masks the fault; a bulkhead
contains the error; graceful degradation downgrades the failure instead of crashing).

## 2. Partial failure is the defining property of a distributed system
- In a single process, a failure is *total and detectable*: the process is up or it has crashed
  (fail-stop), and you find out. In a distributed system, **some components fail while others keep
  running, and you cannot reliably tell which** — this is *partial failure* (reuses 11).
- The deep reason you cannot tell is **FLP + the impossibility of distinguishing a slow node from a
  dead node over an asynchronous network** (line-verified in 11). A timeout is a *guess*, not a
  fact. This is the forcing function behind timeouts, failure detectors, and quorums.
- Corollary: **"is it down?" has no ground truth** — only suspicion. Hence failure detectors are
  characterised by completeness vs accuracy (Chandra–Toueg, reused from 11), and every actuator
  (failover in 15, breaker in 18) acts on a *suspicion*, risking false positives (e.g. split-brain).

## 3. Failure-mode taxonomy (what can go wrong, ordered by nastiness)
From 11/12, applied here as the model 20 plans against:
- **Fail-stop / crash**: node halts and stops emitting. Easiest to handle (cleanly absent). Most
  HA design assumes this.
- **Omission**: messages/requests silently dropped (lossy link, full queue → 18). Looks like
  slowness or partial unavailability.
- **Timing / performance failure**: correct answer, too late. **This is the tail (Cluster B).** A
  node that is *slow* is often worse than a node that is *dead*, because it stays in rotation and
  poisons every fan-out that touches it (Dean, Tail-at-Scale).
- **Byzantine / arbitrary**: node lies / sends inconsistent or corrupt output (reuses 12 Byzantine
  Generals: needs 3m+1 nodes to tolerate m liars). Rare inside one trust domain; assumed away by
  most non-blockchain infra (we assume fail-stop, not Byzantine).

## 4. Independent vs correlated failure (the assumption that breaks the math)
- All redundancy math (Cluster D: A = 1 − (1−a)^n) assumes **independent** failures. Reality:
  failures **correlate** — shared power, shared rack/switch, shared AZ, shared deploy, shared
  dependency, shared bug, shared config push, thundering-herd retries (18).
- **Correlated failure is the silent killer of availability estimates.** Two replicas behind one
  switch are not 2 nines better — they share a common-mode fault. RECOMPUTE (D): independent
  3-replica availability vs the same with a correlated common-mode factor — the budget collapses.
- This is *why* placement matters: spread replicas across failure domains (rack/AZ/region) to make
  failures *as independent as possible*. Cells & shuffle-sharding (Cluster C) are correlation-
  reduction machines.

## 5. The fallacies of distributed computing (the wrong defaults)
Peter Deutsch / James Gosling, ~1994–1997 (Sun) — `[UNVERIFIED]` exact source (no free canonical
primary fetched; widely cited list). The eight false assumptions engineers smuggle in:
1. The network is reliable. 2. Latency is zero. 3. Bandwidth is infinite. 4. The network is secure.
5. Topology doesn't change. 6. There is one administrator. 7. Transport cost is zero. 8. The network
is homogeneous. Each fallacy *is* a failure mode 20 must design around (1→omission; 2/3→tail; 5→
failover/rebalancing; 7→capacity cost). Useful as a checklist; attributions carried `[UNVERIFIED]`.

## 6. Blast radius (the unit of failure accounting)
- **Blast radius = the fraction of users/requests/data harmed when one fault fires.** It is the
  central design metric of 20: you cannot prevent all faults, so you *bound their scope*.
- Levers that shrink it: sharding (1/shards), shuffle-sharding (1/C(n,k) — Cluster C, RECOMPUTE),
  cells, bulkheads (18), per-tenant limits (18), AZ/region isolation, canary/staged rollout.
- Blast radius is the bridge to capacity (D): a smaller cell needs more *relative* headroom (fewer
  peers to absorb a failure), so blast-radius reduction trades efficiency for containment — the
  exact trade AWS names in shuffle-sharding ("trade efficiency for scope of impact").

## 7. Cascading failure vs a single fault (why systems die whole)
Reuses 18 (line-verified retry-amplification, queue-collapse, goodput collapse):
- A **single fault** harms its blast radius and stops. A **cascade** is a fault whose *handling*
  creates new load that triggers the next fault: node dies → its load shifts to peers → peers now
  over-utilised → peers slow/die → more load shifts → **metastable failure** (the system stays
  down even after the trigger is removed, sustained by retries + cold caches).
- Mechanisms (all from 18/AWS-builders, verified): retry amplification 1/(1−r) → retry storm;
  bounded-queue overflow; thundering-herd on recovery; cache stampede after a flush (16). AWS
  builders' (verified): a 5-deep call stack with 3 retries/layer multiplies load ~ catastrophically
  on failure → circuit breakers + retry budgets exist to break the loop.
- **The distinction is the whole point of 20**: resilience ≠ preventing faults; it is preventing a
  fault from *recruiting* the rest of the system. RECOMPUTE the multi-layer retry amplification (D).

## 8. CAP as a failure-model statement (bridge to D)
- Brewer PODC 2000 (VERIFIED `brewer-podc-2000.txt`): of {Consistency, Availability, Partition-
  tolerance} you get "**at most two**"; under a partition you must *forfeit* C or A. BASE =
  **B**asically **A**vailable, **S**oft state, **E**ventual consistency (verified verbatim) — the
  availability-first dual of ACID.
- Kleppmann 2015 (VERIFIED `kleppmann-cap-2015.txt`): CAP is a *narrow* theorem (linearizability +
  total availability + arbitrary partitions); it is a poor general design taxonomy. **The honest
  framing for 20: a partition is a fault you don't get to choose; CAP just says you must pre-decide
  the C-vs-A behaviour for when it fires.** Connects to 15 failover/split-brain (forfeiting A via
  fencing to keep C) and to error-budget policy (19).

## Sources
- VERIFIED this session: Brewer PODC 2000 keynote (`brewer-podc-2000.{pdf,txt}`); Kleppmann CAP
  blog 2015 (`kleppmann-cap-2015.{html,txt}`); AWS "Timeouts, retries, backoff w/ jitter"
  (`aws-timeouts-retries-backoff.txt`, for cascade mechanics).
- REUSED (line-verified earlier): 11 (FLP, partitions, failure detectors, Byzantine 3m+1, no global
  clock); 12 (Byzantine Generals primary); 18 (retry amplification, queue collapse, goodput
  collapse, metastability); 13 (timing failures = tail); 15 (failover, split-brain, fencing).
- `[UNVERIFIED]` carried: Avizienis et al. "Basic Concepts and Taxonomy of Dependable and Secure
  Computing" (IEEE TDSC 2004) for the fault/error/failure chain; Deutsch/Gosling "Fallacies of
  Distributed Computing" exact source; Gilbert–Lynch 2002 formal CAP proof (still blocked).
