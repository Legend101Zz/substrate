# 13 — Scaling Fundamentals · _structure.md

**Identity:** the mathematics and method of capacity — why a wall must exist, which resource
owns it, how to push past it structurally, and how to measure it honestly. The quantitative
floor under all of Part II.

**Bespoke shape — "one curve, derived → located → spread → measured."** NOT a topic survey.
The whole sub-course is the SAME `1/(1−ρ)` curve seen four ways, taught as a single argument:
**A proves the wall is mathematical → B finds which resource owns it → C gives the structural
moves to spread load off it → D measures it without lying.** Each part is a movement that
needs the previous one. Theorem-and-measurement driven (this is the most math-forward spine
sub-course after 11), with simulators as labs and a back-of-envelope drill kit as the bridge
into 21.

## Dependency position
- **Depends on:** 01 (latency hierarchy, cache lines/false sharing = the USL β made physical),
  06 (consistent hashing as Z-substrate), 10 (LB peer selection = X-axis fan-out), 11 (scale-out
  owes replication/consensus = the β cost), 08 (stampede for test realism).
- **Feeds into:** ALL of 14–21 — 13 is the quantitative spine. X-axis→10/15, Y-axis→17/19,
  Z-axis→14/15; USE/RED defs here, SLOs→19; capacity loop here, failure-mode capacity + tail
  tolerance→20; back-of-envelope→21.
- **Appendix links DOWN:** N-math-for-systems (full queueing/probability derivations),
  B-linux-internals (the actual /proc counters). 13 owns the method/math; the appendices own the
  derivations and the kernel knobs — don't duplicate.

## Chapter specs (3–5 lines each)
### Part A — the wall is mathematical
1. **Little's Law & back-of-envelope** — `L=λW`, distribution-free; `concurrency=throughput×
   latency`; server form `U=X·S`. Applies to any box you draw; pool sizing is arithmetic, not
   taste. The foundational conservation law of the whole sub-course.
2. **The utilization wall** — M/M/1 `W=S/(1−ρ)`; `W/S=1/(1−ρ)` (2× at 50%, 10× at 90%, 100× at
   99%); M/G/1 P-K adds variance (`C²ₛ`) inflation. Why you buy headroom with idle capacity —
   queues integrate variability and the last few % cost order-of-magnitude latency.
3. **Parallel speedup limits: Amdahl & USL** — Amdahl ceiling `1/(1−p)`; USL adds a coherency
   term → throughput goes RETROGRADE past `N*=√((1−α)/β)`. The `β` (N² coordination cost) is the
   physical price of agreement — exactly what scale-out (C) and consensus (11) must bound.
4. **Tail & fan-out** — `P(slow)=1−(1−q)^N` (≈63% at N=100, q=1%); the latency hierarchy
   (register→…→cross-continent RTT, ~9 orders of magnitude). Teach RATIOS/ordering, not memorized
   ns. The operational basis of "report p99/p99.9," used everywhere downstream.

### Part B — which resource owns it
5. **The USE method** — per resource: Utilization / Saturation / Errors; resource (bottom-up) vs
   workload (top-down) analysis meet via Little's Law. Saturation IS the operational face of A's
   queue — non-zero saturation means you're already paying `1/(1−ρ)`. Resource-complete by
   construction. (RED is the request-side cousin → 19.)
6. **Profiling & the moving bottleneck** — averages lie (variance + sampling aliasing) so read
   the queue itself; statistical sampling (width=cost), flame graphs (x=merged stacks NOT time),
   on-CPU+off-CPU = all of `W`. Relieving the top resource MOVES the wall to the next — capacity
   is a loop, not a one-shot.

### Part C — spread load off it
7. **Scale up vs out & statelessness** — up is cheap until Amdahl/USL/physics; out passes the
   ceiling but creates the distributed-systems problem (the β cost, 11). Statelessness is the
   lever: relocate state (session→token/cache, durable→DB, hot reads→cache/CDN) so the X-axis is
   embarrassingly parallel. State is relocated, not deleted.
8. **The AKF scale cube** — X (clone), Y (functional split), Z (shard by key); orthogonal,
   composable. Cloning a stateless tier in front of an unscaled DB just MOVES the wall to the DB —
   which is why 14/15/16 exist. Each axis hands off downstream (X→10/15, Y→17/19, Z→14/15).

### Part D — measure it honestly
9. **Load models & coordinated omission** — a load test IS a model: closed (`N=X·R`, self-limits,
   hides overload) vs open (exogenous arrivals, exposes it); most internet traffic is open. The
   killer bug: coordinated omission deletes the tail exactly when latency is worst (~3 orders of
   magnitude understatement). Never average percentiles — merge HDR histograms.
10. **The capacity loop** — find bottleneck (B) → measure the wall open + CO-corrected (D) → pick
    target ρ with headroom (A) → size via Little's Law → re-test (the bottleneck moved, B). The
    repeatable method that becomes step 2 of 21's design method.

## Paired build labs (/build — simulators + drill kit)
Queueing-wall simulator (M/M/1→M/M/c→M/G/1: measured `W` vs ρ over analytic `S/(1−ρ)`; watch
variance inflate) → USE-sweep harness + flame-graph-from-scratch + "bottleneck moves" demo (add a
second serial resource; relieve the first; watch the wall reappear) → stateless-ify refactor lab +
AKF-cube decision worksheet + "shared bottleneck defeats scale-out" demo → coordinated-omission
demo + open-vs-closed curve plotter + capacity-planning notebook (locate knee, pick ρ, size via
Little's Law) → **back-of-envelope drill kit** (QPS/storage/bandwidth/concurrency) — the connective
tissue into 21.

## Diagrams needed
- The single `1/(1−ρ)` curve as the spine motif (re-shown in A/B/C/D framings).
- M/M/1 latency-vs-utilization hockey stick; M/G/1 variance inflation overlay.
- Amdahl ceiling vs USL retrograde curve (knee at `N*`).
- Fan-out tail `1−(1−q)^N` rising with N; the 9-order latency hierarchy ladder.
- USE table (resource × {U,S,E}); flame graph anatomy (width=cost, NOT time).
- AKF cube (X/Y/Z axes) + "clone in front of unscaled DB moves the wall."
- Open vs closed load model; coordinated-omission tail deletion timeline.
- The capacity loop as a cycle (bottleneck→measure→ρ→size→re-test).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED BY RECOMPUTATION:** Little's Law; M/M/1 `W/S=1/(1−ρ)` table; Amdahl ceiling; USL form
  + knee; fan-out `0.99^100≈0.366`; coordinated-omission (naive p99.9=1ms vs corrected ≈989ms);
  closed `N=X·R`. The math/method is theorem-grade — no fetch needed.
- **`[UNVERIFIED]` — entirely network-blocked, fetch before hardening any exact number:** Jeff Dean
  latency table (exact ns/ms), Drepper memory paper, Little 1961, Kleinrock, Amdahl 1967, Gunther
  USL, Dean&Barroso Tail-at-Scale (A); Gregg USE + flame graphs + RED + PSI (B); AKF cube + Art of
  Scalability + Twelve-Factor + Fowler (C); Tene coordinated omission + HdrHistogram + wrk2 + NSDI
  2006 open-vs-closed + Harchol-Balter (D). NOTE: Tail-at-Scale later VERIFIED in 20 — reconcile at
  draft time. Teach ratios/ordering now; do NOT harden exact ns until fetched.
- **Disagreements to resolve with sources:** Amdahl vs Gustafson (strong vs weak scaling); exact
  scope of "coordinated omission"; "scale cube" attribution.
- **Boundary discipline:** queueing derivations → appendix N; Linux counters → appendix B; SLO/
  tracing machinery → 19; tail-tolerant/hedged patterns → 20. Don't duplicate downstream.
