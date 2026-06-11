# 20 · Cluster D — capacity planning & reliability math (research brief)

> Phase-1 brief. NO course prose. This is the quantitative cluster: it turns the patterns (C) and
> failure models (A) into numbers. Reuses 13 (M/M/1, M/G/1 P-K, USL, Little's Law, headroom — all
> line-verified + recomputed there), 19 (error budget as a capacity input). ALL math → `_recompute.py`.

## 1. Capacity planning is a closed loop (reuse 13)
The loop (line-verified in 13D): **forecast demand → model the system → size capacity with headroom
→ load-test to validate → observe (19) → re-forecast.** 20 adds the *reliability* dimension: capacity
must cover not just peak demand but **peak demand during a failure** (the surviving nodes absorb the
dead node's share — see §4).

## 2. Demand forecasting & headroom (why you never run at 100%)
- **The utilization wall (reuse 13, RECOMPUTE):** for M/M/1, mean wait W ∝ 1/(1−ρ). As utilization
  ρ→1 latency → ∞. RECOMPUTE the ladder: ρ=0.5 → 2×; ρ=0.8 → 5×; ρ=0.9 → 10×; ρ=0.95 → 20× the
  service time. **This is why you provision headroom: the last 10–20% of utilization buys unbounded
  latency** (B's tail). Headroom is not waste; it is tail insurance.
- **Headroom definition (RECOMPUTE):** if you target max utilization ρ\*, then usable capacity =
  ρ\*·C and headroom fraction = 1−ρ\*. To serve peak demand D at ρ\*, provision C = D/ρ\*. E.g.
  D=8000 rps at ρ\*=0.8 → C ≥ 10000 rps.
- **M/G/1 (Pollaczek–Khinchine, reuse 13):** wait grows with the *variance* of service time, not
  just the mean → highly variable workloads (B's variability) need *more* headroom for the same
  latency target. RECOMPUTE the P-K wait for two CV values.
- **USL (Gunther, reuse 13):** throughput has a knee N\* = √((1−α)/β) beyond which contention (α)
  and coherency (β) make adding capacity *counterproductive*. Capacity planning must stop at the
  knee, not assume linear scaling. RECOMPUTE N\* for sample coefficients.

## 3. Availability math — the serial chain (dependencies multiply)
- A request that needs **all** of n components in series succeeds with **A_serial = ∏ aᵢ**.
  RECOMPUTE: 5 dependencies each at 99.9% → 0.999^5 = 0.9950 → **~99.5%**, i.e. ~5× the downtime of
  one component. **Availability erodes as you add dependencies** — the deep argument for minimizing
  the critical path (B tainted partial results / graceful degradation make non-critical deps
  *optional*, lifting them out of the serial product).
- Connect to 19: serial availability ≤ the weakest dependency, so the error budget (19) of a service
  is bounded by the *sum* of its dependencies' budgets it spends on the critical path.

## 4. Availability math — parallel redundancy (the headline formula)
- n **independent** redundant replicas, each available a; the group is down only if **all** fail:
  **A_parallel = 1 − (1−a)^n.** RECOMPUTE:
  - a=0.99, n=2 → 1−0.01² = 0.9999 (two nines → four nines).
  - a=0.99, n=3 → 1−0.01³ = 0.999999 (six nines).
  - a=0.9, n=3 → 1−0.1³ = 0.999. → each independent replica adds ~the same number of nines.
- **The independence caveat (A §4), RECOMPUTE the correction:** if a fraction c of failures are
  *correlated* (common-mode: shared AZ/switch/deploy), effective availability ≈
  1 − [c·(1−a) + (1−c)·(1−a)^n]. RECOMPUTE for a=0.99, n=3, c=0.1: the (1−a)^n term (1e-6) is
  swamped by c·(1−a)=0.001 → effective ~99.9%, i.e. **three orders of magnitude worse than the naive
  six nines.** This is the single most important number in 20: *correlation, not replica count,
  sets your real availability.* It is why failure-domain spread (cells, AZ/region) matters more than
  raw replica count.

## 5. Capacity-during-failure (redundancy and headroom are the same budget)
- If you run n nodes and design to survive f simultaneous failures, the surviving (n−f) must carry
  100% of load → each node may run at most ρ\* = (n−f)/n of "even" load in steady state, i.e.
  **required headroom fraction = f/n.** RECOMPUTE:
  - n=3, f=1 → each runs ≤ 2/3 ≈ 67% normally (33% headroom) so one death is absorbable.
  - n=10, f=1 → each runs ≤ 9/10 = 90% (only 11% headroom needed). **Bigger pools need less
    *relative* headroom** — the efficiency argument *against* tiny cells (C), the exact counter-trade
    to blast-radius reduction. Small cells = small blast radius (good) but more relative slack
    (costly). This is the central tension of 20's capacity story.
- N+1 vs N+2: f=1 vs f=2 → headroom f/n. RECOMPUTE n=5: N+1→20%, N+2→40%.

## 6. Capacity as an SLO input (reuse 19)
- The error budget (19, line-verified: budget = (1−SLO)·window) is *spent* by both bad deploys
  (18 policy) AND capacity shortfalls (queueing latency breaches the latency SLO). So **capacity is
  a reliability input**: under-provisioning burns error budget via tail latency (B); the burn-rate
  alert (19) is an early capacity-shortfall signal.
- Little's Law (reuse 13, RECOMPUTE) closes the loop: L = λ·W. To hold W (latency SLO) as λ (demand)
  rises, you must add capacity to keep ρ below the wall (§2). RECOMPUTE: λ=500 rps, W=0.2 s →
  L=100 concurrent; if each server handles 25 concurrent → need ≥4 servers, +1 for f=1 → 5.

## 7. Common misconceptions
- "Provision for the average" — provision for peak-during-failure with headroom (§2, §5).
- "Three replicas = six nines" — only if independent; correlation dominates (§4, the key result).
- "100% utilization is efficient" — it's a latency cliff (§2 the wall).
- "Adding nodes always adds throughput" — USL knee says it can reverse (§2).
- "Redundancy and headroom are separate budgets" — they're the same f/n slack (§5).
- "Availability adds across dependencies" — it *multiplies* (and erodes) in series (§3).

## 8. Build-your-own targets
- Availability calculator: serial ∏aᵢ + parallel 1−(1−a)^n + the correlated-failure correction;
  show the c-knob collapsing six nines to three.
- Capacity planner: given λ, service time, target ρ\*, and f → output node count + headroom + the
  M/M/1 latency at that ρ; cross-check against Little's Law.

## Sources
- REUSED (line-verified + recomputed in 13): M/M/1 1/(1−ρ) wall, M/G/1 P-K variance term, USL knee
  N\*=√((1−α)/β), Little's Law L=λW, headroom/capacity loop, coordinated omission.
- REUSED (line-verified in 19): error budget = (1−SLO)·window, burn rate as capacity-shortfall
  signal.
- RECOMPUTED this session (`_recompute.py`): serial ∏aᵢ, parallel 1−(1−a)^n, correlated-failure
  correction, f/n headroom, N+1/N+2, utilization-wall ladder, USL knee, Little's-Law sizing.
- VERIFIED context this session: CAP (Brewer PODC 2000) for the C-vs-A-under-partition framing that
  bounds what "available" can mean during a partition (A §8).
- `[UNVERIFIED]` carried: Gunther's USL book pagination; Kleinrock *Queueing Systems v1* (M/M/1,
  M/G/1) — both carried from 13; specific cloud-provider AZ-failure-correlation statistics.
