# 13 scaling-fundamentals — Factcheck: Clusters B, C, D

Method note: like Cluster A, these clusters are **method/logic + flagged empirical/historical
attributions**, with one piece of **arithmetic verified by independent recomputation** (the
coordinated-omission percentiles, Cluster D). The verification mode per claim:
- *Derivation/recomputation* for anything closed-form (Python this session).
- *Reuse* for canon already line-verified in 01/06/10/11/Cluster-A (not re-fetched).
- *Flag* `[UNVERIFIED from fetched source]` for any external talk/paper/book/tool whose host
  was unreachable.

**Network reality (5th consecutive session):** only `lamport.azurewebsites.net` + Walmart
artifactory resolve. Verified by direct `curl` this session (all HTTP 000): `brendangregg.com`
(USE method + flame graphs), `akfpartners.com` (Scale Cube), `gist.githubusercontent.com`,
`raw.githubusercontent.com`, `arxiv.org`. Gil Tene talk hosts, HdrHistogram, wrk2, and the
Schroeder/Harchol-Balter NSDI 2006 paper were not separately reachable (same host families).

---

## Cluster B — USE method / bottlenecks

### VERIFIED (reasoning from already-verified math — 0 blockers)
| # | Claim | Check | Verdict |
|---|-------|-------|---------|
| B1 | Saturation (queued work) = the queue Little's Law/M-M-1 model; non-zero saturation ⇒ paying `1/(1−ρ)` | Same identity verified in Cluster A #1–#4 | VERIFIED (reuse) |
| B2 | Variance inflates the queue at modest mean utilization (M/G/1 direction) | Consistent with Cluster A §1.2; *direction* only (formula itself flagged in A) | VERIFIED (direction) |
| B3 | Flame-graph width ≈ proportion of samples ≈ proportion of time (law of large numbers on stack samples) | Statistical reasoning; sampling fraction → time fraction | VERIFIED (reasoning) |
| B4 | On-CPU + off-CPU accounts for all of `W` (busy + waiting), closing with Little's Law | Residence-time decomposition from Cluster A #1 | VERIFIED (reuse) |
| B5 | Removing the top bottleneck moves the wall to the next resource | Corollary of `1/(1−ρ)` existing for *some* resource (Cluster A) | VERIFIED (reasoning) |

### VERIFIED BY REUSE (line-checked earlier — not re-fetched)
| # | Claim | Source already verified in | Verdict |
|---|-------|----------------------------|---------|
| B6 | Memory bandwidth vs. capacity are distinct resources; "why a hierarchy" | 01 `_research_eater-csapp.md` §J (CS:APP ch.6) | VERIFIED (reuse) |
| B7 | False sharing = coherency-interconnect cost (the USL `β` term made physical) | 06 Disruptor + RocksDB `bloom_impl.h` briefs | VERIFIED (reuse) |

### FLAGGED — `[UNVERIFIED from fetched source]` (network-blocked, carried forward)
| # | Claim | Why flagged |
|---|-------|-------------|
| BF1 | "The USE Method" name, definition, per-resource checklist + tool mappings (Gregg) | `brendangregg.com/usemethod.html` HTTP 000 |
| BF2 | Flame-graph construction/format + FlameGraph scripts; off-CPU variant (Gregg) | `brendangregg.com/flamegraphs.html` + GitHub HTTP 000 |
| BF3 | RED method (Wilkie/Weaveworks) name + Rate/Errors/Duration definitions | host unreachable |
| BF4 | Linux PSI `/proc/pressure` saturation semantics | kernel.org unreachable |
| BF5 | _Systems Performance_ (Gregg, 2nd ed.) USE checklist tables | book/host unreachable |

**Cluster B blockers: 0.** The method's *logic* is verified by reuse of Cluster-A math; the
*canonical wording/checklists/tooling* are honestly deferred.

---

## Cluster C — horizontal vs. vertical / statelessness / AKF cube

### VERIFIED (reasoning from already-verified math — 0 blockers)
| # | Claim | Check | Verdict |
|---|-------|-------|---------|
| C1 | Vertical scaling capped by Amdahl `1/(1−p)` + USL retrograde knee `N*=√((1−α)/β)` | Cluster A #5–#6 (verified by recomputation) | VERIFIED (reuse) |
| C2 | Horizontal scaling trades a hardware ceiling for coordination cost (USL `β·N²`) | Cluster A USL term #6 | VERIFIED (reuse) |
| C3 | X-axis (clone) needs statelessness/replication to be cheap; scales throughput/availability, not data size | Definitional + LB fan-out reasoning | VERIFIED (reasoning) |
| C4 | Y-axis (functional split) adds inter-service coordination (`β`); Z-axis (shard by key) scales data size, adds rebalancing/hot-shard/cross-shard cost | Definitional + USL; sharding mechanics verified in 06/11 | VERIFIED (reasoning) |
| C5 | "Stateless app tier + unscaled shared DB" just relocates the wall to the DB | Direct corollary of Cluster A `1/(1−ρ)` for the DB resource | VERIFIED (reasoning) |
| C6 | The three axes are orthogonal and compose (X∧Y∧Z) | Geometric/definitional | VERIFIED (reasoning) |

### VERIFIED BY REUSE (line-checked earlier — not re-fetched)
| # | Claim | Source already verified in | Verdict |
|---|-------|----------------------------|---------|
| C7 | Consistent hashing / partitioning substrate (Z-axis) | 06 consistent-hashing brief | VERIFIED (reuse) |
| C8 | Replication, quorum = majority intersection, consistency models (X read-replicas / Z cross-shard) | 11 `_research.md` + cluster factchecks | VERIFIED (reuse) |
| C9 | LB peer selection / smooth weighted RR / `ip_hash` (X fan-out mechanism) | 10 `_research_load-balancing-peer-selection.md` (NGINX `release-1.31.1`) | VERIFIED (reuse) |

### FLAGGED — `[UNVERIFIED from fetched source]` (network-blocked, carried forward)
| # | Claim | Why flagged |
|---|-------|-------------|
| CF1 | AKF Scale Cube exact X/Y/Z definitions, diagram, and "AKF" attribution | `akfpartners.com` HTTP 000 |
| CF2 | _The Art of Scalability_ (Abbott & Fisher, 2nd ed.) as the book-length source | book/host unreachable |
| CF3 | Twelve-Factor App factor VI ("processes are stateless") exact wording | `12factor.net` unreachable |
| CF4 | Microservices Y-axis tradeoffs / distributed-monolith antipattern (Fowler) | `martinfowler.com` unreachable |

**Cluster C blockers: 0.** The cube's *geometry/logic and the scaling math* are verified
(recomputation + reuse); the *AKF wording/diagram/attribution* are deferred. Note: the term
"AKF Scale Cube" and its X/Y/Z labels are used in the brief as the working taxonomy but must
not harden into asserted-attribution prose until CF1/CF2 are fetched.

---

## Cluster D — load testing / open-vs-closed / coordinated omission

### VERIFIED (recomputation this session — 0 blockers)
| # | Claim | Check (Python, this session) | Verdict |
|---|-------|------------------------------|---------|
| D1 | Naive closed measurement of (9999×1 ms + 1×1000 ms) hides the tail | `p99=1.00, p99.9=1.00, p99.99≈1.10 ms, max=1000 ms` | VERIFIED (exact) |
| D2 | Coordinated-omission correction (back-fill ~1000 samples 1000→1 ms) restores the tail | `p99≈890 ms, p99.9≈989 ms, p99.99≈999 ms` over ~10 999 samples | VERIFIED (exact) |
| D3 | The understatement is ~3 orders of magnitude at p99.9 (1 ms → ~989 ms) | D1 vs D2 | VERIFIED (exact) |
| D4 | Closed model has Little's-Law feedback `N = X·R` ⇒ throughput falls as response time rises | `N=200`: R=.02→X=10000/s; R=.10→X=2000/s | VERIFIED (exact) |
| D5 | Fan-out sets the percentile you must report; q=.01,N=100 ⇒ ~63% slow ⇒ median user hits backend tail | `0.99^100=0.366`, slow=0.634 (Cluster A #7) | VERIFIED (reuse) |
| D6 | Percentiles are non-linear ⇒ merge histograms, don't average percentiles | Elementary statistics | VERIFIED (reasoning) |

### FLAGGED — `[UNVERIFIED from fetched source]` (network-blocked, carried forward)
| # | Claim | Why flagged |
|---|-------|-------------|
| DF1 | "Coordinated omission" term + canonical exposition (Gil Tene, "How NOT to Measure Latency") | talk/slides hosts HTTP 000; *mechanism+arithmetic* verified, *attribution* not |
| DF2 | HdrHistogram `recordValueWithExpectedInterval` exact back-fill algorithm | `hdrhistogram.org` + GitHub unreachable |
| DF3 | `wrk2` constant-throughput / CO-corrected generator | GitHub `giltene/wrk2` unreachable |
| DF4 | Schroeder/Wierman/Harchol-Balter "Open Versus Closed: A Cautionary Tale" (NSDI 2006) | host unreachable; *model distinction* is first-principles, *citation* flagged |
| DF5 | Harchol-Balter, _Performance Modeling..._ as textbook backing | book/host unreachable |

### Warnings / precision notes (no blockers)
- DW1: The back-fill model in D2 (one omitted sample per intended 1 ms interval) is *a*
  reasonable model, not *the* HdrHistogram algorithm (DF2). The exact corrected percentiles
  shift with the model; the order-of-magnitude understatement (D3) is the robust claim.
- DW2: "Most internet services are open-model" is a modeling judgment (true for exogenous
  client arrivals); fixed client pools are correctly closed. Stated as such, not absolute.
- DW3: Do NOT harden the Tene/NSDI/HdrHistogram/wrk2 attributions into Phase-2 prose until
  DF1–DF4 are fetched.

**Cluster D blockers: 0.** The coordinated-omission *arithmetic* and open/closed *feedback*
are verified by recomputation; the canonical *talk/paper/tool attributions* are deferred.

---

## Overall: 0 blockers across B, C, D.
All three clusters' load-bearing **logic and math** are verified by recomputation or by reuse
of earlier line-checked sources. The **empirical/historical/tooling attributions** (Gregg
USE+flame graphs, AKF cube, Tene coordinated omission, HdrHistogram/wrk2, NSDI open-vs-closed,
Twelve-Factor) are uniformly network-blocked and carried forward as `[UNVERIFIED from fetched
source]`, consistent with Cluster A's Dean/Drepper flags. This is why 13 can now be honestly
reconciled (method/math complete across A–D) while the carry-forward primary list stays open.
