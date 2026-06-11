# Appendix N · math-for-systems — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). N is a **reference appendix**: deep info
> ONLY, **NO exercises, NO tests** (CONSTITUTION non-negotiable #5). It introduces no system; it
> COLLECTS and RE-DERIVES the recurring quantitative tools the spine leans on, so spine chapters
> cross-link DOWN to one verified place. Bespoke structure: a **formula compendium organized by the
> question each tool answers** (NOT four clusters, NOT a build progression). Math: `_recompute.py`
> (20/20). Factcheck: `_factcheck_phase1.md` (0 blockers). NO new primary — these are standard
> results; each is RE-DERIVED first-principles and anchored to the spine sub-course that uses it.

## 1. Thesis
Most "scaling intuition" in the spine is a handful of formulas wearing different costumes. This
appendix is the single, recomputed home for them. Every entry says: **the question → the formula →
the first-principles derivation → the spine anchors that depend on it.**

## 2. Queueing & capacity (the "how fast / how many" math) — anchors 13/17/18/20
- **Little's Law `L = λ·W`** (long-run averages, distribution-free). The most-reused identity in the
  course: concurrency = arrival-rate × residence-time. Forward → pool/queue sizing (λ=500/s, W=0.2s
  ⇒ L=100 in flight). Inverted → a bounded queue of depth Q draining at μ has worst wait `Q/μ`
  (200/1000 ⇒ 200 ms): **queue depth is a latency budget** (18 backpressure).
- **M/M/1**: `ρ = λ/μ`, mean wait `W = 1/(μ−λ)`, in-system `L = ρ/(1−ρ)`. At λ=900,μ=1000 a 1 ms
  service balloons to a 10 ms wait — queueing, not service, dominates near saturation (13/18).
- **The utilization wall `1/(1−ρ)`**: latency multiplier 2×/5×/10×/20× at ρ=0.5/0.8/0.9/0.95. This
  single curve is WHY headroom is non-optional (13/20) and WHY load-shedding exists (18).
- **Capacity sizing `servers = ⌈D/ρ*⌉`** (D = offered load in erlangs). 4 erlangs at ρ*=0.8 ⇒ 5
  servers — N+1 headroom falls out of the wall (20).

## 3. Hashing & probabilistic structures (the "how to be small + fast" math) — anchors 06/08/14/19
- **Birthday/collision**: `P(collision) = 1 − ∏(slots−i)/slots`. 23 people/365 days > 50% (the
  canonical surprise); rule of thumb ≈ `1.1774·√m` keys for 50% in m slots. WHY hash spaces need to
  be ≫ key counts, and WHY 64-bit IDs are not collision-proof at scale (06/14).
- **Consistent hashing**: adding a node moves `~K/(N+1)` keys vs mod-N's "almost all". Add 1 node to
  100: ~9,901 vs ~990,099 keys move — **~100× less churn** ⇒ the partitioning/rebalancing backbone
  (06/14/15).
- **Bloom filter**: `p_fp = (1−e^{−kn/m})^k`; optimal `k* = (m/n)·ln2`; min fp `≈ 0.6185^{m/n}`. At
  10 bits/item ⇒ k*≈6.93, fp≈0.82%. WHY a tiny bit-budget kills almost all wasted disk lookups
  (LSM read path, 07/08).
- **HyperLogLog**: relative std error `≈ 1.04/√m`. m=16,384 registers (~16 KB) ⇒ ~0.81% error to
  count BILLIONS of distinct items — the cardinality estimator behind metrics (19) and analytics (06).

## 4. Tail, fan-out & availability (the "what happens at scale / on failure" math) — anchors 13/20/27
- **Fan-out tail `1−(1−p)^N`**: one slow-in-100 (p=0.01, N=100) ⇒ **63.4%** of fan-out requests are
  slow. The p99 of the parts becomes the p63 of the whole — the Tail-at-Scale result (Dean &
  Barroso, local `tail-at-scale-cacm2013`). Same identity = join tail over agents (27).
- **Availability**: serial deps MULTIPLY (`∏a_i`; 5×99.9% ⇒ 99.501%); parallel redundancy
  `1−(1−a)^n` (3×99% ⇒ 99.9999%) **only if failures are independent** — the correlated-failure
  caveat is the load-bearing lesson (20).
- **Amdahl `1/(s+(1−s)/n)`** → ceiling `1/s` (5% serial ⇒ 20× max). **USL** adds a coordination term
  `N/(1+a(N−1)+bN(N−1))` that PEAKS then retrogrades (a=0.03,b=1e-4 ⇒ peak ~N=98 then declines):
  more workers can make a system SLOWER (20/27).

## 5. Statistics for measurement (the "do I believe this number" math) — anchors 19/31
- **Sampling CI `1.96·√(p(1−p)/N)`**; invert for N at worst-case p=0.5: **±3% needs ~1068 samples**.
  WHY small eval sets prove nothing (31) and WHY sampled tracing has a quantifiable error (19).
- (Cross-link only — full derivations live in 19/31: burn-rate windows, percentiles ≠ means,
  tail-based sampling RSE.)

## 6. The "one identity, many costumes" map (the appendix's reconciliation payload)
| identity | costume in spine |
|---|---|
| `1−(1−p)^N` | fan-out tail (13/20), tool-selection error (23), join tail (27), defence escape complement (33) |
| `L = λ·W` | pool sizing (13), in-flight messages (17), queue-as-latency-budget (18), in-system jobs (20) |
| `1/(1−ρ)` | latency wall (13), shed threshold (18), headroom (20) |
| `K/N` movement | consistent hashing (06/14), resharding (15) |
| `1.96√(p(1−p)/N)` | sampling error (19), eval set size (31) |
This table is the appendix's reason to exist: it lets a spine chapter say "this is the SAME math as
X" and link down to the verified derivation instead of re-deriving inline.

## 7. Provenance summary
- **NO new primary** — all results are standard (Little 1961; queueing theory; Bloom 1970; Flajolet
  HLL 2007; Karger consistent hashing 1997; Amdahl 1967; Gunther USL; Dean & Barroso tail). Each is
  **RE-DERIVED first-principles** in `_recompute.py` (20/20) rather than asserted.
- **REUSED (line-verified):** the spine anchors 06/07/08/13/14/15/17/18/19/20/27/31 that consume
  this math; Tail-at-Scale already local + VERIFIED.
- **`[UNVERIFIED]` carry-forward:** the original-paper *attributions* (Little 1961, Bloom 1970,
  Flajolet 2007, Karger 1997, Amdahl 1967, Gunther USL) are not separately fetched — but the
  **results are recomputed, not taken on faith**, so none is load-bearing. Logged, not hardened.

---
**Appendix N reconciled.** Reference-grade, exercise-free, fully recomputed. Next appendix candidates
this batch: **L-consensus-replication-and-transactions** and **M-ai-agent-memory-tools-and-evaluation**
(both fully serviceable from local primaries). No chapters yet.
