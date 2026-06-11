#!/usr/bin/env python3
"""
Substrate Appendix N - math-for-systems: independent recomputation of the load-bearing
quantitative tools the spine leans on. Pure stdlib. Run: python3 _recompute.py

N is a REFERENCE appendix (deep info only, NO exercises). It does not introduce a system; it
collects + RE-DERIVES the math that recurs across Part I/II/III so spine chapters can cross-link
DOWN to one verified place:
  Little's Law            L = lambda * W                         (13, 17, 18, 20)
  M/M/1 queue            W = 1/(mu - lambda); rho = lambda/mu    (13, 18)
  Utilization wall       W grows as 1/(1-rho)                    (13, 18, 20)
  Erlang / knee          response time blows up near rho->1      (13, 20)
  Birthday / collisions  hash collision probability             (06, 14)
  Consistent hashing     key movement on resize = K/N           (06, 14, 15)
  Bloom filter           p_fp = (1-e^{-kn/m})^k ; optimal k      (06, 08)
  HyperLogLog            std error ~ 1.04/sqrt(m)                (06, 19 cardinality)
  Tail / fan-out         P(slow) = 1-(1-p)^N                     (13, 20, 27)
  Availability           serial prod ; parallel 1-(1-a)^n        (20)
  Amdahl / USL           speedup ceilings                        (20, 27)
  Sampling CI            95% CI = 1.96 sqrt(p(1-p)/N)            (19, 31)
Every number is re-derived first-principles and cross-linked to its spine anchor.
"""

import math

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-6): return abs(a - b) <= tol * max(1.0, abs(b))

# =====================================================================
# 1. LITTLE'S LAW  L = lambda * W  (13/17/18/20)
# =====================================================================
# A system serving lambda=500 req/s with mean residence W=0.2s holds L=100 in flight.
lam, W = 500.0, 0.2
L = lam * W
check("Little's Law L = lambda*W (13/17/18)", approx(L, 100.0),
      f"lambda={lam}/s, W={W}s -> L={L:.0f} concurrent -> sets pool/queue sizing")
# Inverted: a bounded queue of Q with drain mu gives max wait Q/mu (18 backpressure).
Q, mu = 200, 1000.0
check("bounded-queue max wait = Q/mu (18)", approx(Q/mu, 0.2),
      f"Q={Q}, mu={mu}/s -> worst wait {Q/mu*1000:.0f} ms -> queue depth IS a latency budget")

# =====================================================================
# 2. M/M/1  W = 1/(mu - lambda), rho = lambda/mu  (13/18)
# =====================================================================
def mm1_W(lam, mu): return 1.0 / (mu - lam)
def mm1_L(lam, mu): rho = lam/mu; return rho/(1-rho)
mu = 1000.0
check("M/M/1 wait W=1/(mu-lambda) (13)", approx(mm1_W(900, mu), 0.01),
      f"lambda=900,mu=1000 -> W={mm1_W(900,mu)*1000:.0f} ms (vs 1ms service) -> queueing dominates near saturation")
check("M/M/1 in-system L=rho/(1-rho) matches Little (13)",
      approx(mm1_L(900, mu), 900*mm1_W(900, mu)),
      f"L={mm1_L(900,mu):.1f} == lambda*W={900*mm1_W(900,mu):.1f} -> consistency check")

# =====================================================================
# 3. UTILIZATION WALL  W ~ 1/(1-rho)  (13/18/20) -- the knee
# =====================================================================
def latency_factor(rho): return 1.0/(1.0-rho)
walls = {0.5: 2.0, 0.8: 5.0, 0.9: 10.0, 0.95: 20.0}
ok = all(approx(latency_factor(r), f) for r, f in walls.items())
check("utilization wall: latency multiplier 1/(1-rho) (13/20)", ok,
      "rho 0.5/0.8/0.9/0.95 -> 2x/5x/10x/20x service time -> WHY headroom is non-optional")
# Required servers for target rho* given offered load (capacity planning, 20)
D, rho_star = 4.0, 0.8   # D = offered load in erlangs (lambda/mu_per_server)
servers = math.ceil(D / rho_star)
check("capacity: servers = ceil(D/rho*) (20)", servers == 5,
      f"offered {D} erlangs at rho*={rho_star} -> {servers} servers (N+1 headroom baked in)")

# =====================================================================
# 4. BIRTHDAY / HASH COLLISION  (06/14)
# =====================================================================
def p_no_collision(n, slots):
    p = 1.0
    for i in range(n): p *= (slots - i) / slots
    return p
def p_collision(n, slots): return 1 - p_no_collision(n, slots)
# 23 people, 365 days -> >50% shared birthday (the canonical surprise)
check("birthday paradox: 23/365 > 50% collision (06)", p_collision(23, 365) > 0.5,
      f"P(collision)={p_collision(23,365):.3f} -> why small key counts collide in big spaces")
# sqrt(slots) rule of thumb: ~sqrt(N) insertions for ~50% collision
slots = 1_000_000
approx_n = int(1.1774 * math.sqrt(slots))   # n ~ 1.1774*sqrt(m) for p=0.5
check("birthday sqrt rule ~1.1774*sqrt(m) for 50% (06/14)", abs(p_collision(approx_n, slots)-0.5) < 0.02,
      f"m={slots:,} -> ~{approx_n:,} keys for 50% collision (~sqrt scale)")

# =====================================================================
# 5. CONSISTENT HASHING  movement on resize = K/N  (06/14/15)
# =====================================================================
K, N = 1_000_000, 100
mod_n_moved = K * (N) / (N+1)             # naive mod-N: almost ALL keys move on N->N+1
consistent_moved = K / (N+1)              # consistent hashing: ~K/N move
check("consistent hashing moves ~K/(N+1) vs mod-N moves ~all (06/14)",
      consistent_moved < mod_n_moved/50,
      f"add 1 node to {N}: consistent ~{consistent_moved:,.0f} keys move vs mod-N ~{mod_n_moved:,.0f} -> ~{mod_n_moved/consistent_moved:.0f}x less churn")

# =====================================================================
# 6. BLOOM FILTER  p_fp = (1-e^{-kn/m})^k ; optimal k = (m/n) ln2  (06/08)
# =====================================================================
def bloom_fp(n, m, k): return (1 - math.exp(-k*n/m))**k
def bloom_opt_k(m, n): return (m/n)*math.log(2)
n_items, m_bits = 1_000_000, 10_000_000   # 10 bits/item
k_opt = bloom_opt_k(m_bits, n_items)
check("Bloom optimal k=(m/n)ln2 ~6.93 at 10 bits/item (06/08)", approx(k_opt, 10*math.log(2), 1e-3),
      f"m/n=10 -> k*={k_opt:.2f} hashes")
fp = bloom_fp(n_items, m_bits, round(k_opt))
check("Bloom fp ~0.82% at 10 bits/item, k=7 (06/08)", abs(fp - 0.0082) < 0.002,
      f"p_fp={fp*100:.2f}% -> WHY a tiny bit-budget kills most disk lookups (LSM, 07/08)")
# closed form for optimal fp: (1/2)^k  ~ 0.6185^(m/n)
fp_closed = 0.6185 ** (m_bits/n_items)
check("Bloom min fp ~0.6185^(m/n) (06/08)", abs(fp_closed - fp) < 0.002,
      f"closed-form min fp={fp_closed*100:.2f}% matches numeric")

# =====================================================================
# 7. HYPERLOGLOG  std error ~ 1.04/sqrt(m)  (06/19)
# =====================================================================
def hll_rse(m): return 1.04/math.sqrt(m)
for m_reg, want in [(2**10, 0.0325), (2**14, 0.00813)]:
    check(f"HLL RSE 1.04/sqrt(m) at m={m_reg}", abs(hll_rse(m_reg)-want) < 5e-4,
          f"m={m_reg} registers -> ~{hll_rse(m_reg)*100:.2f}% error; m=16384 (~16KB) -> ~0.81% to count BILLIONS (19 cardinality)")

# =====================================================================
# 8. TAIL / FAN-OUT  P(>=1 slow) = 1-(1-p)^N  (13/20/27)
# =====================================================================
def fanout_slow(p, N): return 1-(1-p)**N
check("fan-out tail 1-(1-p)^N: p=0.01,N=100 -> 63.4% (13/20/27)",
      abs(fanout_slow(0.01, 100)-0.634) < 1e-3,
      f"one slow in 100 -> {fanout_slow(0.01,100)*100:.1f}% of requests slow -> WHY p99 of parts = p63 of whole")

# =====================================================================
# 9. AVAILABILITY  serial=prod(a_i) ; parallel=1-(1-a)^n  (20)
# =====================================================================
serial = 0.999**5
parallel = 1-(1-0.99)**3
check("serial availability = prod(a_i) (20)", abs(serial-0.99501) < 1e-4,
      f"5 deps @ 99.9% in series -> {serial*100:.3f}% (deps MULTIPLY down)")
check("parallel redundancy = 1-(1-a)^n (20)", abs(parallel-0.999999) < 1e-6,
      f"3x 99% replicas -> {parallel*100:.4f}% (IF failures independent -- the 20 caveat)")

# =====================================================================
# 10. AMDAHL / USL speedup ceilings  (20/27)
# =====================================================================
def amdahl(s, n): return 1.0/(s + (1-s)/n)
check("Amdahl ceiling 1/s as n->inf (20/27)", approx(amdahl(0.05, 10**9), 1/0.05, 1e-3),
      f"5% serial -> max speedup {1/0.05:.0f}x no matter how many workers")
# USL: C(N) = N / (1 + a(N-1) + b*N(N-1)) ; has a knee then RETROGRADES
def usl(N, a, b): return N/(1 + a*(N-1) + b*N*(N-1))
a, b = 0.03, 0.0001
peak_N = max(range(1, 2000), key=lambda N: usl(N, a, b))
check("USL has a throughput PEAK then retrogrades (20/27)", 1 < peak_N < 2000,
      f"a={a},b={b} -> peak throughput at N~{peak_N} then DECLINES (coordination cost wins)")

# =====================================================================
# 11. SAMPLING CI  95% CI = 1.96 sqrt(p(1-p)/N)  (19/31)
# =====================================================================
def ci95(p, N): return 1.96*math.sqrt(p*(1-p)/N)
# Invert for N at worst-case p=0.5 (p(1-p)=0.25), half-width 3%: N = 0.25/(half/1.96)^2
N_for_3pct = math.ceil(0.25 / ((0.03/1.96)**2))
check("eval sample size for +-3% CI at p=0.5 ~1068 (31)", abs(N_for_3pct-1068) < 5,
      f"need N~{N_for_3pct} golden tasks for +-3% -> WHY small eval sets prove nothing (19/31)")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"N-math-for-systems recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All math-for-systems claims re-derived first-principles.")
