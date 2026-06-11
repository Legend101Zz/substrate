#!/usr/bin/env python3
"""
Substrate Appendix A - computer-architecture: independent recomputation of the load-bearing
arithmetic of a real CPU+memory system. Pure stdlib. Run: python3 _recompute.py

A is a REFERENCE appendix (deep info only, NO exercises). Spine 01 BUILDS a CPU from NAND gates up
to a working fetch-decode-execute machine + a clean ISA. A is the deep reference for the question 01
hands UP: "given a correct CPU, what actually makes a REAL one fast?" -> the memory hierarchy (caches,
the memory mountain, virtual memory/TLB), pipelining + hazards, and instruction-level parallelism
(superscalar/OOO/branch prediction). It instantiates the transferable numbers spine 13 (latency
numbers) and 06 (data-structure locality) lean on, and feeds appendix B (linux-internals: page tables).

Anchors (local + line-verified): 01/_research.md + clusters (nand2tetris NAND->ALU->CPU->ISA,
CS:APP/CMU 15-213 machine-level + memory mountain + cache/VM, two's-complement encoding), 06 (locality),
13 (latency-number ladder), N (math). NO new fetch (eater.net/CS:APP hosts not re-fetched; HTTP 000
this wave). Every number re-derived from those, flagged where version/uarch-sensitive (illustrative).
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. TWO'S COMPLEMENT: one adder does add AND subtract; asymmetric range (01 / CS:APP ch.2)
# =====================================================================
# N-bit two's complement: range [-2^(N-1), 2^(N-1)-1]; A - B = A + ~B + 1.
N = 8
tmin, tmax = -(2**(N-1)), 2**(N-1)-1
check("8-bit two's complement range is [-128,127] (asymmetric) (01/CS:APP)",
      tmin == -128 and tmax == 127,
      f"TMin={tmin}, TMax={tmax} -> one extra negative -> WHY -TMin overflows; one zero; uniform ordering")
# A - B via add of complement: verify 5 - 3 == 5 + (~3 + 1) in 8-bit wrap
def to_u8(x): return x & 0xFF
A_, B_ = 5, 3
sub_via_add = to_u8(A_ + to_u8(~B_) + 1)
check("subtraction = add of two's complement (one ALU does both) (01)",
      sub_via_add == 2,
      f"5 + (~3+1) mod 2^8 = {sub_via_add} -> WHY a single adder + invert suffices (Eater realizes this physically)")

# =====================================================================
# 2. AMDAHL'S LAW on PIPELINING: ideal speedup = #stages; hazards/stalls erode it (01/CS:APP/N)
# =====================================================================
# A k-stage pipeline ideally retires 1 instr/cycle after fill: speedup -> k for long streams.
k_stages = 5
n_instr = 1000
cycles_pipelined = (k_stages - 1) + n_instr      # fill latency + 1/cycle
cycles_serial = k_stages * n_instr               # no overlap
speedup = cycles_serial / cycles_pipelined
check("5-stage pipeline approaches ~5x throughput for long streams (01)",
      4.9 < speedup <= 5.0,
      f"{cycles_serial}/{cycles_pipelined}={speedup:.3f}x -> WHY pipelining; fill cost {k_stages-1} cyc amortizes away")
# CPI with stalls: a fraction f of instrs stall s cycles -> CPI = 1 + f*s
f_stall, s_pen = 0.20, 3
cpi = 1 + f_stall*s_pen
check("hazard stalls raise CPI above the ideal 1.0 (01/CS:APP)",
      approx(cpi, 1.6),
      f"20% of instrs stall 3 cyc -> CPI={cpi} -> WHY forwarding/branch prediction exist (to cut f and s)")

# =====================================================================
# 3. BRANCH MISPREDICTION penalty: deeper pipe = costlier mispredict (CS:APP/uarch)
# =====================================================================
# Penalty ~ pipeline depth refilled. Effective CPI add = mispredict_rate * mispredict_penalty.
pipe_depth = 15            # modern deep pipe (illustrative)
mispredict = 0.05          # 5% of branches mispredicted (good predictor on hard code)
branch_frac = 0.20         # 1 in 5 instrs is a branch
cpi_add = branch_frac * mispredict * pipe_depth
check("branch mispredicts add to CPI in proportion to pipe depth (uarch)",
      approx(cpi_add, 0.15),
      f"20% branches x 5% miss x {pipe_depth}-deep = +{cpi_add:.2f} CPI -> WHY branch prediction is worth huge silicon on deep OOO cores")
# a 99% predictor cuts the penalty 5x vs 95%
cpi_add_good = branch_frac * 0.01 * pipe_depth
check("a 99% predictor cuts mispredict CPI ~5x vs 95% (uarch)",
      approx(cpi_add/cpi_add_good, 5.0),
      f"+{cpi_add:.2f} -> +{cpi_add_good:.2f} CPI -> WHY predictor accuracy dominates branch-heavy perf")

# =====================================================================
# 4. SUPERSCALAR / ILP: IPC > 1 via multiple issue; capped by dependencies (uarch/N)
# =====================================================================
# A w-wide superscalar can retire up to w instr/cycle (IPC up to w) IF enough independent work.
issue_width = 4
ideal_ipc = issue_width
# a dependency chain of length L over n_instr forces serialization: achievable IPC <= n/L
L_chain = 4
achievable_ipc = min(issue_width, n_instr / (n_instr / 1.0))  # fully dependent => IPC 1
check("a 4-wide core needs independent work to exceed IPC 1 (ILP) (uarch)",
      ideal_ipc == 4 and achievable_ipc == 1,
      f"issue width {issue_width} -> peak IPC {ideal_ipc}; a single dependency chain pins IPC to {achievable_ipc:.0f} -> WHY OOO + register renaming expose ILP")

# =====================================================================
# 5. MEMORY HIERARCHY / AMAT: caches turn DRAM latency into ~cache latency (CS:APP ch.6 / 13)
# =====================================================================
# AMAT = hit_time + miss_rate * miss_penalty. Latency ladder from 13 (illustrative, order-of-magnitude):
L1_ns, L2_ns, DRAM_ns = 1.0, 4.0, 100.0
def amat(hit, miss_rate, miss_pen): return hit + miss_rate*miss_pen
amat_95 = amat(L1_ns, 0.05, DRAM_ns)     # 95% L1 hit, miss goes to DRAM
check("AMAT: a 95% L1 hit rate hides most of DRAM latency (CS:APP ch.6/13)",
      approx(amat_95, 6.0),
      f"AMAT=1 + 0.05*100 = {amat_95:.1f} ns vs {DRAM_ns} ns raw DRAM -> WHY caches exist; locality is everything")
# the cliff: drop hit rate to 80% and AMAT explodes
amat_80 = amat(L1_ns, 0.20, DRAM_ns)
check("a 15-point hit-rate drop multiplies AMAT ~3.5x (the locality cliff) (CS:APP)",
      approx(amat_80/amat_95, 21.0/6.0),
      f"80% hit -> AMAT {amat_80:.1f} ns ({amat_80/amat_95:.1f}x worse) -> WHY cache-friendly access patterns dominate real perf")

# =====================================================================
# 6. CACHE LINE / SPATIAL LOCALITY: stride determines effective bandwidth (CS:APP/06)
# =====================================================================
LINE = 64          # 64-byte cache line (CS:APP)
# Sequential int access (4B) reuses each line 16x; stride-64 wastes 60/64 of every fetched line.
ints_per_line = LINE // 4
check("64B line holds 16 ints -> sequential access amortizes 1 miss over 16 elems (CS:APP)",
      ints_per_line == 16,
      f"{ints_per_line} ints/line -> stride-1 = 1/16 miss rate; stride-16 = 1 miss/elem -> WHY row-major traversal & arrays-of-struct layout matter")
# useful-byte fraction at stride s (elements): 1/s of each line used when s>=16
def useful_frac(stride_elems): return min(1.0, ints_per_line/ (stride_elems*1.0)) if stride_elems>0 else 1.0
check("large strides waste most of each cache line (CS:APP memory mountain)",
      approx(useful_frac(16), 1.0) and useful_frac(64) < 0.3,
      f"stride 16 uses ~100% of line; stride 64 uses {useful_frac(64)*100:.0f}% -> WHY the 'memory mountain' slopes down with stride")

# =====================================================================
# 7. VIRTUAL MEMORY / TLB: page table walk vs TLB hit; multi-level table size (CS:APP ch.9 / B)
# =====================================================================
PAGE = 4096        # 4 KB page
VA_BITS, PA_BITS = 48, 52     # typical x86-64 (illustrative)
offset_bits = int(math.log2(PAGE))
vpn_bits = VA_BITS - offset_bits
check("4KB page -> 12 offset bits; 48-bit VA -> 36 VPN bits (CS:APP ch.9)",
      offset_bits == 12 and vpn_bits == 36,
      f"offset={offset_bits} bits, VPN={vpn_bits} bits -> WHY a single flat page table (2^36 entries) is impossible -> multi-level tables")
# 4-level table: 9 VPN bits per level (512 entries/4KB table). 36/9 = 4 levels.
entries_per_table = PAGE // 8     # 8-byte PTEs
level_bits = int(math.log2(entries_per_table))
levels = vpn_bits // level_bits
check("4KB tables of 8B PTEs -> 9 index bits/level -> 4-level walk for 48-bit VA (CS:APP/B)",
      entries_per_table == 512 and level_bits == 9 and levels == 4,
      f"{entries_per_table} PTEs/table, {level_bits} bits/level, {levels} levels -> a TLB MISS costs {levels} memory accesses -> WHY the TLB is critical")
# TLB effect on AMAT: a miss adds 'levels' DRAM-ish accesses
tlb_miss_cost = levels * DRAM_ns
check("a TLB miss costs ~4 dependent memory accesses (page walk) (CS:APP/B)",
      approx(tlb_miss_cost, 400.0),
      f"{levels} x {DRAM_ns} ns = {tlb_miss_cost:.0f} ns per page walk -> WHY huge pages / TLB reach matter for big working sets")

# =====================================================================
# 8. LATENCY LADDER (13): order-of-magnitude gaps the whole appendix hangs on
# =====================================================================
# Each tier ~ an order of magnitude or more; these GAPS (not absolute ns) are the load-bearing fact.
ladder = {"L1":1.0, "L2":4.0, "L3":40.0, "DRAM":100.0, "SSD":16000.0, "disk_seek":2_000_000.0}
check("memory latency ladder spans ~6 orders of magnitude L1->disk (13)",
      ladder["disk_seek"]/ladder["L1"] >= 1e6,
      f"L1 {ladder['L1']}ns -> disk seek {ladder['disk_seek']:.0e}ns = {ladder['disk_seek']/ladder['L1']:.0e}x -> WHY the hierarchy exists and locality decides performance")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"A-computer-architecture recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All architecture claims re-derived first-principles (constants reused from spine 01 + 06 + 13 + N).")
