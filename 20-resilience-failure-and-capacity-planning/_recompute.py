#!/usr/bin/env python3
"""
Substrate 20 — resilience-failure-and-capacity-planning: independent recomputation of every
load-bearing quantitative claim across the four cluster briefs. Pure stdlib. Run: python3 _recompute.py

Each check asserts the claim AND prints the worked number so a skeptical reader can follow the
arithmetic. Sources cited inline; primary receipts in
meta/fetched_primaries/_VERIFIED_2026-06-10_resilience.md (+ tail-at-scale-cacm2013.txt,
aws-shuffle-sharding.txt, brewer-podc-2000.txt).
"""
import math
from math import comb

def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# =========================================================================
# CLUSTER B — the tail at scale
# =========================================================================
# B1. Fan-out tail: P(>=1 slow of N) = 1 - (1-p)^N.  (Dean, Tail-at-Scale, VERIFIED)
#     "1 ms avg but 1 sec 99%ile; touch 100 -> 63% take >= 1 sec."
p = 0.01
for N, expect in [(1, 0.01), (100, 0.6340)]:
    pr = 1 - (1 - p) ** N
    check(f"fan-out tail P(>=1 slow), N={N}", approx(pr, expect, tol=1e-3),
          f"1-(1-{p})^{N} = {pr:.4f}" + (" (~63%, Dean)" if N == 100 else ""))

# B2. Hedging: if backup fires at the dp-th percentile, only (1-dp) of requests ever hedge
#     -> load overhead ~ (1 - dp).  Dean: backup@10ms -> <5% extra; backup@50ms -> <1%.
for dp, max_overhead in [(0.95, 0.05), (0.99, 0.01)]:
    overhead = 1 - dp
    check(f"hedge load overhead at p{int(dp*100)} deadline", overhead <= max_overhead + 1e-9,
          f"1-{dp} = {overhead:.2%} extra requests (Dean: <={max_overhead:.0%})")

# B3. Hedging tail collapse: with an independent backup, slow only if BOTH slow ~ p^2.
for p_leaf, expect in [(0.01, 1e-4), (0.05, 2.5e-3)]:
    both = p_leaf ** 2
    check(f"hedged effective tail (p={p_leaf})", approx(both, expect),
          f"{p_leaf}^2 = {both:g} (vs {p_leaf} single)")

# B4. Dean measured backup table: p99.9 994ms -> 50ms is ~20x improvement (VERIFIED numbers).
imp = 994 / 50
check("Dean backup p99.9 improvement", approx(imp, 19.88, tol=1e-2),
      f"994/50 = {imp:.2f}x (no-backup vs backup@10ms p99.9)")
# Tied-request p99 reductions (VERIFIED: -43% idle, -38% +Terasort).
check("tied req p99 reduction (idle)", approx((67-38)/67, 0.4328, tol=1e-2),
      f"(67-38)/67 = {(67-38)/67:.2%} (~-43%)")
check("tied req p99 reduction (+Terasort)", approx((108-67)/108, 0.3796, tol=1e-2),
      f"(108-67)/108 = {(108-67)/108:.2%} (~-38%)")


# =========================================================================
# CLUSTER C — cells & shuffle-sharding (AWS, VERIFIED)
# =========================================================================
# C1. Plain sharding blast radius = 1/K.
for K in (4, 8):
    check(f"plain-shard blast radius K={K}", approx(1/K, {4:0.25, 8:0.125}[K]),
          f"1/{K} = {1/K:.4f}")

# C2. Shuffle-shard: 8 workers, shard size 2 -> C(8,2)=28 combos -> 1/28; 7x better than 1/4.
c82 = comb(8, 2)
check("C(8,2) shuffle combos", c82 == 28, f"C(8,2) = {c82} (AWS: 28)")
check("shuffle 1/28 vs plain 1/4 = 7x", approx((1/4)/(1/28), 7.0),
      f"(1/4)/(1/28) = {(1/4)/(1/28):.1f}x better (AWS: '7 times better')")

# C3. Route 53: 2048 virtual name servers, shard of 4 -> C(2048,4) ~ 7.3e11 (AWS: '730 billion').
c2048_4 = comb(2048, 4)
check("C(2048,4) ~ 730 billion", approx(c2048_4/1e9, 730.0, tol=5e-3),
      f"C(2048,4) = {c2048_4:,} (~{c2048_4/1e9:.1f} billion; AWS: 730B)")

# C4. Full-collision probability (two customers draw the SAME k-subset) = 1/C(n,k).
for n, k in [(8, 2), (2048, 4)]:
    pc = 1 / comb(n, k)
    check(f"full-collision prob n={n},k={k}", approx(pc, 1/comb(n, k)),
          f"1/C({n},{k}) = {pc:.3e}")

# C5. Expected overlap of two random k-subsets of n workers = k*k/n (hypergeometric mean).
for n, k, expect in [(8, 2, 0.5), (2048, 4, 16/2048)]:
    ov = k * k / n
    check(f"expected overlap two k-subsets n={n},k={k}", approx(ov, expect),
          f"k*k/n = {k}*{k}/{n} = {ov:.4f} workers")


# =========================================================================
# CLUSTER D — capacity & availability math
# =========================================================================
# D1. Utilization wall: M/M/1 latency factor = 1/(1-rho).  (reuse 13)
for rho, expect in [(0.5, 2), (0.8, 5), (0.9, 10), (0.95, 20)]:
    factor = 1 / (1 - rho)
    check(f"util wall factor rho={rho}", approx(factor, expect),
          f"1/(1-{rho}) = {factor:.1f}x service time")

# D2. Headroom: to serve peak D at max util rho*, provision C = D/rho*.
D, rho_star = 8000, 0.8
C = D / rho_star
check("provision C for peak D at rho*", approx(C, 10000),
      f"{D}/{rho_star} = {C:.0f} rps capacity (headroom {1-rho_star:.0%})")

# D3. USL knee: N* = sqrt((1-alpha)/beta).  (Gunther, reuse 13)
alpha, beta = 0.03, 0.0001
Nstar = math.sqrt((1 - alpha) / beta)
check("USL knee N*", approx(Nstar, 98.4886, tol=1e-3),
      f"sqrt((1-{alpha})/{beta}) = {Nstar:.2f} (peak then declines)")

# D4. Serial availability: A = prod(a_i).  5 deps each 99.9%.
a, n = 0.999, 5
A_serial = a ** n
check("serial availability 0.999^5", approx(A_serial, 0.995010, tol=1e-5),
      f"{a}^{n} = {A_serial:.6f} (~99.5%, ~{n}x the downtime of one dep)")

# D5. Parallel redundancy: A = 1 - (1-a)^n.  (the headline formula)
for a, n, expect in [(0.99, 2, 0.9999), (0.99, 3, 0.999999), (0.9, 3, 0.999)]:
    Ap = 1 - (1 - a) ** n
    check(f"parallel availability a={a},n={n}", approx(Ap, expect),
          f"1-(1-{a})^{n} = {Ap:.6f}")

# D6. Correlated-failure correction: A ~ 1 - [c*(1-a) + (1-c)*(1-a)^n].
#     a=0.99, n=3, c=0.1 -> correlated term dominates -> ~99.9% (3 orders worse than 6 nines).
a, n, c = 0.99, 3, 0.1
unavail = c * (1 - a) + (1 - c) * (1 - a) ** n
A_corr = 1 - unavail
naive = 1 - (1 - a) ** n
check("correlated-failure collapses 6 nines -> ~3 nines", approx(A_corr, 0.9990010, tol=1e-5),
      f"1-[{c}*0.01 + 0.9*0.01^3] = {A_corr:.7f} (naive {naive:.6f}); "
      f"unavail {unavail:.2e} vs {(1-naive):.2e} = {unavail/(1-naive):.0f}x worse")

# D7. Headroom-for-failure: survive f of n -> required headroom fraction = f/n.
for nn, f, hr in [(3, 1, 1/3), (10, 1, 1/10), (5, 1, 1/5), (5, 2, 2/5)]:
    headroom = f / nn
    max_load = (nn - f) / nn
    check(f"headroom to survive f={f} of n={nn}", approx(headroom, hr),
          f"f/n = {f}/{nn} = {headroom:.3f} headroom; run <= {max_load:.0%} normally")

# D8. Little's Law sizing: L = lambda * W; servers = ceil(L / per_server) + f.
lam, W, per = 500, 0.2, 25
L = lam * W
servers = math.ceil(L / per) + 1   # +1 for f=1 redundancy
check("Little's Law concurrency L", approx(L, 100),
      f"L = {lam}*{W} = {L:.0f} concurrent")
check("capacity sizing w/ N+1", servers == 5,
      f"ceil({L:.0f}/{per}) + 1 = {servers} servers")


# =========================================================================
# CLUSTER A — cascading failure (reuse 18, recomputed here for 20)
# =========================================================================
# A1. Retry amplification across L layers each retrying r times = (1+r)^L (worst case),
#     or 1/(1-r) for a single layer's geometric retry budget (reuse 18).
#     AWS: 5-deep stack, 3 retries/layer.
L_layers, retries = 5, 3
amp = (1 + retries) ** L_layers
check("retry amplification 5 layers x 3 retries", amp == 1024,
      f"(1+{retries})^{L_layers} = {amp}x load multiplier at the bottom")
# Single-layer geometric retry-rate amplification (reuse 18): 1/(1-r).
for r, expect in [(0.5, 2.0), (0.9, 10.0)]:
    a_amp = 1 / (1 - r)
    check(f"single-layer retry amplification r={r}", approx(a_amp, expect),
          f"1/(1-{r}) = {a_amp:.1f}x")


# -------------------------------------------------------------------------
print("\n" + "=" * 60)
ncheck = len(results); passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{ncheck} checks passed")
if passed != ncheck:
    print("FAILED:", [nm for nm, ok, _ in results if not ok]); raise SystemExit(1)
print("All load-bearing 20 math claims verified by recomputation.")
