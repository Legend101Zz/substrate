# 13 — scaling-fundamentals — RECONCILED research (`_research.md`)

> **Phase 1 deliverable (NO course prose).** Synthesis of four factchecked clusters into the
> standard six sections. Full depth lives in the cluster files; this file reconciles overlaps,
> states the cross-cluster thesis, and consolidates sources + gaps. Every `[UNVERIFIED from
> fetched source]` / residual gap from the clusters is preserved here verbatim in intent.
>
> **Cluster files (read for full depth):**
> - A — `_research_back-of-envelope-latency-queueing.md` + `_factcheck_clusterA.md`
>   (Little's Law, M/M/1 utilization wall, M/G/1 variance, Amdahl, USL, fan-out tail, latency hierarchy)
> - B — `_research_bottlenecks-use-method.md` + `_factcheck_clusterBCD.md`
>   (USE method, resource-vs-workload, sampling profilers, flame graphs, on/off-CPU)
> - C — `_research_horizontal-vertical-akf-cube.md` + `_factcheck_clusterBCD.md`
>   (scale up vs. out, statelessness, AKF X/Y/Z cube, axis→downstream handoffs)
> - D — `_research_load-testing-capacity-planning.md` + `_factcheck_clusterBCD.md`
>   (open vs. closed models, coordinated omission, percentile/histogram discipline, capacity loop)
>
> **Reconciliation verdict:** 13 is reconciled on the basis that its load-bearing content —
> the *method and mathematics* of capacity reasoning — is verified end-to-end (by recomputation
> or by reuse of earlier line-checked sources), **0 factcheck blockers across A–D**. The
> remaining gaps are *empirical/historical/tooling attributions* (Dean latency table, Drepper,
> Gregg USE+flame graphs, AKF cube, Tene coordinated omission, HdrHistogram/wrk2, NSDI
> open-vs-closed), all uniformly network-blocked and carried forward `[UNVERIFIED]`. None of
> them is load-bearing for the *method*; none may harden into Phase-2 prose until fetched.

---

## The cross-cluster thesis (what this sub-course actually teaches)

Scaling is one idea seen four ways, and the four clusters are a single arc:

> **A proves a wall must exist; B finds which resource owns it; C gives the structural moves to
> push past it; D measures it honestly so you provision before you hit it.**

1. **A — the wall is mathematical.** Little's Law (`L = λW`, distribution-free) fixes
   concurrency given throughput and latency. The queue then makes response time hyperbolic in
   utilization: `W/S = 1/(1−ρ)` (2× at 50%, 10× at 90%, 100× at 99%). Amdahl caps parallel
   speedup at `1/(1−p)`; the USL adds a coherency term that makes throughput go *retrograde*
   past `N*=√((1−α)/β)`. Fan-out turns a 1% backend tail into `1−(1−q)^N` ≈ 63% at N=100. The
   shapes are theorem-grade — verified by recomputation, no source needed.
2. **B — the wall belongs to whatever saturates first.** The USE method (Utilization /
   Saturation / Errors, per resource) is a *resource-complete* search for that resource.
   *Saturation is the operational face of the queue A modeled* — non-zero saturation means you
   are already paying `1/(1−ρ)`. Averages lie (M/G/1 variance + sampling aliasing), so you read
   the queue itself; profilers (sampling, flame graphs, on/off-CPU) localize *within* the hot
   resource, where width = cost and busy + waiting = `W`.
3. **C — the structural moves.** Scale up (cheap, but Amdahl/USL + physics cap it) → scale out
   (passes the ceiling, but *creates the distributed-systems problem* = the USL `β` cost).
   Statelessness is the lever that makes the X-axis cheap by *relocating* state to systems you
   scale on purpose. The AKF cube names the three orthogonal splits — **X** clone, **Y**
   functional split, **Z** shard-by-key — and they compose. Cloning a stateless tier in front
   of an unscaled DB just *moves the wall to the DB*, which is why 14/15/16 exist.
4. **D — measure it without lying.** A load test *is* a model: closed (fixed users,
   self-limiting, `N=X·R`) hides overload; open (exogenous arrivals) exposes it — and most
   internet traffic is open. The killer bug is **coordinated omission**: a blocked client stops
   sampling exactly when latency is worst, understating p99.9 by ~3 orders of magnitude (1 ms
   → ~989 ms, recomputed this session). Fix with constant-rate issuance / back-fill correction,
   report the *tail* the fan-out math (A) demands, and provision to a target ρ with headroom.

The through-line: **every cluster is the same `1/(1−ρ)` curve** — A derives it, B finds whose
it is, C decides how to spread load so no resource climbs it, D measures where it bites.

---

## 1. Key mechanisms (consolidated)

- **Little's Law** `L = λW`, distribution-free; back-of-envelope form `concurrency =
  throughput × latency`; server form `U = X·S`. Applies to *any* box you draw. *(A §1.1)*
- **Utilization wall** (M/M/1) `W = S/(1−ρ)`, `W/S = 1/(1−ρ)`; M/G/1 P-K adds variance
  (`C²ₛ`) inflation. *(A §1.2)*
- **Amdahl** `1/((1−p)+p/N)`, ceiling `1/(1−p)`. **USL** `C(N)=N/(1+α(N−1)+βN(N−1))`, knee
  `N*=√((1−α)/β)`; `β` = coordination/coherency, the `N²` shadow of "everyone must agree." *(A §1.3–1.4)*
- **Tail/fan-out** `P(slow)=1−(1−q)^N`; the operational basis of "report p99/p99.9." *(A §1.5)*
- **Latency hierarchy** register→L1→L2→memory→SSD→disk→same-DC RTT→cross-continent RTT,
  ~9 orders of magnitude; *teach ratios/ordering, not memorized ns* (exact numbers blocked). *(A §1.6)*
- **USE method** — per resource, check Utilization, Saturation, Errors; resource (bottom-up)
  vs. workload (top-down) analysis meet via Little's Law. Saturation = the queue. *(B §1.2–1.4)*
- **Profiling** — statistical sampling (width = cost), flame graphs (x = merged stacks, NOT
  time), on-CPU + off-CPU = all of `W`. *(B §1.5)*
- **Bottlenecks shift** — relieving the top resource moves the wall to the next; capacity is a
  loop, not a one-shot. *(B §1.6)*
- **Scale up vs. out** — up is cheap until Amdahl/USL/physics; out passes the ceiling but owes
  replication+consistency (sub-course 11). *(C §1.1–1.2)*
- **Statelessness** — relocate session→token/cache, durable→DB(14), hot reads→cache/CDN(16);
  makes X-axis embarrassingly parallel. *(C §1.3)*
- **AKF cube** — X (clone), Y (functional split), Z (shard by key); orthogonal, composable;
  each axis hands off downstream (X→10/15, Y→17/19, Z→14/15). *(C §1.4–1.5)*
- **Open vs. closed load models** — closed self-limits (`N=X·R`), open can overload; pick the
  model that matches the real arrival process. *(D §1.1)*
- **Coordinated omission** — closed-loop generators delete slow samples; fix via constant-rate
  issuance or back-fill (HdrHistogram); ~3-orders-of-magnitude tail understatement otherwise. *(D §1.2)*
- **Percentile discipline** — never average percentiles/latencies; merge HDR histograms;
  report the percentile fan-out demands. *(D §1.3)*
- **Capacity loop** — find bottleneck (B) → measure wall open+CO-corrected (D) → pick target ρ
  with headroom (A) → size via Little's Law → re-test (bottleneck moves, B). *(D §1.4)*

## 2. Foundational sources (consolidated)

**Verified by recomputation/derivation this session (theorem-grade, no fetch):** Little's Law
`L=λW`; M/M/1 `L=ρ/(1−ρ)`, `W/S=1/(1−ρ)` table; Amdahl ceiling; USL form + knee `N*`; fan-out
`1−(1−q)^N` (`0.99^100≈0.366`); coordinated-omission percentiles (naive p99.9=1 ms vs corrected
≈989 ms); closed-model `N=X·R`. *(see `_factcheck_clusterA.md` and `_factcheck_clusterBCD.md`)*

**Verified by reuse (line-checked in earlier sub-courses — NOT re-fetched):**
- Memory hierarchy / SRAM-DRAM / memory mountain — 01 `_research_eater-csapp.md` §J (CS:APP ch.6).
- 64-byte cache line / false sharing (the USL `β` made physical) — 06 Disruptor + RocksDB
  `bloom_impl.h` briefs.
- Consistent hashing / partitioning (Z substrate) — 06.
- Replication / quorum = majority intersection / consistency models (X read-replicas, Z cross-shard) — 11 `_research.md` + cluster factchecks.
- LB peer selection / smooth weighted RR / `ip_hash` (X fan-out) — 10 `_research_load-balancing-peer-selection.md` (NGINX `release-1.31.1`).
- Cache stampede / stale-while-revalidate (test realism) — 08 `_research.md`.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals):**
- *(A)* Jeff Dean "Latency Numbers Every Programmer Should Know" exact ns/ms table (jboner gist
  `2841832` / Colin Scott interactive / Stanford-295 PDF); Ulrich Drepper "What Every
  Programmer Should Know About Memory" (akkadia/LWN 2007); Little (1961); Kleinrock *Queueing
  Systems v1* (M/M/1, M/G/1 P-K); Amdahl (1967); Gunther USL; Dean & Barroso "The Tail at
  Scale" (CACM 2013).
- *(B)* Brendan Gregg "The USE Method" + per-resource checklist/tool mappings; flame-graph
  pages + FlameGraph scripts (incl. off-CPU); _Systems Performance_ (2nd ed.); RED method
  (Wilkie/Weaveworks); Linux PSI `/proc/pressure` docs.
- *(C)* AKF "Scale Cube" articles (akfpartners.com); Abbott & Fisher _The Art of Scalability_
  (2nd ed.); Twelve-Factor App factor VI; microservices Y-axis tradeoffs (Fowler;
  distributed-monolith antipattern).
- *(D)* Gil Tene "How NOT to Measure Latency" (coordinated omission); HdrHistogram
  (`recordValueWithExpectedInterval`); `wrk2`; Schroeder/Wierman/Harchol-Balter "Open Versus
  Closed: A Cautionary Tale" (NSDI 2006); Harchol-Balter _Performance Modeling..._.

## 3. "Why it's this way" — the forcing functions (consolidated)

- **Little's Law is conservation — uncheatable.** Fix throughput and latency and concurrency is
  determined; pool sizing is arithmetic, not taste. *(A)*
- **The wall exists because queues integrate variability;** the last few % of utilization cost
  order-of-magnitude latency, so you buy headroom with idle capacity. *(A)*
- **Amdahl/USL exist because coordination is physical** (a lock serializes; coherence is real
  interconnect traffic); the `N²` term is the cost of agreement — exactly what scale-out (C)
  and consensus (11) must bound. *(A/C)*
- **USE is resource-complete because the wall belongs to whoever saturates first;** enumerating
  every resource × {U,S,E} makes omission structurally impossible. *(B)*
- **Sampling/off-CPU are forced by `W = busy + waiting`** and the observer effect — you can't
  measure everything without changing the timing, and you can't ignore wait time. *(B)*
- **Statelessness is the lever** that makes the easy axis (X) cheap so you spend the hard
  budget on the data tier (Z→14, replication→15). State is relocated, not deleted. *(C)*
- **The load model is part of the experiment;** closed feedback (`N=X·R`) can't express
  overload, and coordinated omission deletes the tail exactly when it matters. Honest
  measurement is the precondition for honest capacity planning. *(D)*

## 4. Common misconceptions to preempt (consolidated)

- "Run servers near 100% to be efficient" — no; latency is `1/(1−ρ)`. *(A)*
- "More cores ⇒ proportional speedup" — no; Amdahl caps, USL goes retrograde. *(A)*
- "Average latency is the SLO" / "Little's Law needs Poisson" — no and no. *(A)*
- "Latency numbers are exact constants" — no; ratios drift with hardware (and are blocked this session). *(A)*
- "Low average utilization ⇒ no problem" / "100% CPU = CPU-bound" — no; read saturation; could be lock spin. *(B)*
- "Fix the top bottleneck and you're done" — no; it moves. *(B)*
- "Flame-graph x-axis is time" — no; it's merged stacks, width = cost. *(B)*
- "Scale up vs. out is either/or" / "horizontal scaling is automatically linear" — no; do both; USL bounds linearity; a shared DB re-imposes Amdahl. *(C)*
- "Stateless means we deleted the state" — no; relocated. *(C)*
- "AKF axes are alternatives — pick one" / "microservices always scale better" — no; orthogonal+compose; bad cuts = distributed monolith. *(C)*
- "Concurrency = arrival rate" / "our load test shows great p99" — no; open vs. closed differ; suspect coordinated omission. *(D)*
- "Average the per-host p99s" / "run at 100% to find max throughput" — no; merge histograms; useful capacity is the knee under your tail SLO. *(D)*

## 5. Best build-your-own target(s) (consolidated)

- **Queueing-wall simulator** (M/M/1 → M/M/c → M/G/1): plot measured `W` vs. ρ over analytic
  `S/(1−ρ)`; watch variance inflate the queue. *(A; pairs with appendix N)*
- **USE-sweep harness + flame graph from scratch + "bottleneck moves" demo** (add a second
  serial resource to the sim, relieve the first, watch the wall reappear). *(B; appendix B/N)*
- **Stateless-ify refactor lab + AKF-cube decision worksheet + "shared bottleneck defeats
  scale-out" demo.** *(C; feeds 21)*
- **Coordinated-omission demo harness + open-vs-closed curve plotter + capacity-planning
  notebook** (locate knee, pick target ρ, size via Little's Law). *(D; feeds 21, appendix N)*
- **Back-of-envelope drill kit** (size QPS/storage/bandwidth/concurrency via Little's Law +
  the latency hierarchy) — the connective tissue into **21-design-case-studies**.

## 6. Open questions / gaps to close (consolidated — preserved verbatim in intent)

- **The empirical latency table (A, Pillar 2) is entirely network-blocked** — every exact Dean
  ns/ms figure + Drepper measurement is `[UNVERIFIED]`. Teach ratios/ordering now; do NOT
  harden any exact number into prose until fetched.
- **Historical/canonical attributions across A–D are blocked:** Little (1961), Kleinrock,
  Amdahl (1967), Gunther USL, P-K (A); Gregg USE + flame graphs + RED + PSI (B); AKF cube +
  _Art of Scalability_ + Twelve-Factor + Fowler (C); Tene coordinated omission + HdrHistogram +
  wrk2 + NSDI 2006 open-vs-closed + Harchol-Balter (D). The *math/method* is verified; the
  *citations/exact wording* need primaries when the network heals.
- **Disagreements to resolve with sources:** Amdahl vs. Gustafson (weak vs. strong scaling, A);
  precise scope of "coordinated omission" (broad Tene framing vs. narrow back-fill, D);
  attribution of the "scale cube" to AKF alone vs. antecedents (C).
- **Modeling judgments to keep honest:** "most internet services are open-model" (true for
  exogenous arrivals; fixed pools are closed); the D2 back-fill model is *a* model, not the
  HdrHistogram algorithm — the order-of-magnitude understatement is the robust claim.
- **Boundary discipline (cross-link, do NOT duplicate downstream mechanics):**
  - X-axis → **10** (load balancing) + **15** (read replicas/consistency).
  - Y-axis → **17** (async/event-driven) + **19** (observability across services).
  - Z-axis → **14** (data modeling/partitioning/sharding) + **15** (replication/consistency).
  - USE/RED *definitions* live here; SLO/tracing/Dapper machinery is **19**.
  - The capacity *loop/headroom method* is here; *failure-mode* capacity, tail-tolerant
    patterns, hedged/tied requests are **20** (resilience), drawing on "The Tail at Scale".
  - Full queueing/probability derivations cross-link *down* into appendix **N-math-for-systems**;
    Linux counters into **B-linux-internals** — per the two-tier design, don't duplicate.
- **Next 13 work (optional, before Phase 2 prose):** fetch the blocked A/B/C/D primaries when a
  healthier network exists and upgrade the `[UNVERIFIED]` flags; otherwise 13 is
  research-complete at the *method/math* level. Next Phase-1 batch: **14–21** (Part II), still
  untouched.
