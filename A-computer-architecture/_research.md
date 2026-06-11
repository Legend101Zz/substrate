# Appendix A · computer-architecture — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). A is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). Spine **01** *builds* a correct CPU from a NAND gate up to
> fetch-decode-execute + a clean ISA. A is the deep reference for the question 01 hands UP: **"given a
> correct CPU, what makes a REAL one fast?"** — the memory hierarchy, pipelining + hazards,
> instruction-level parallelism, and virtual memory/TLB. Spine 01 cross-links DOWN into A; A feeds
> appendix **B** (page tables / VM) and underpins spine **13**'s latency numbers + **06**'s locality.
> **Bespoke structure: a performance ladder — from the correct-but-slow machine 01 built, up each
> layer that real hardware adds to close the gap to peak** — NOT four clusters, NOT a build
> progression. Math: `_recompute.py` (15/15). Factcheck: `_factcheck_phase1.md` (0 blockers). Network:
> eater.net / CS:APP hosts HTTP **000** this wave → constants reused from 01's line-verified
> nand2tetris + CS:APP/CMU-15-213 + Eater reads; nothing new hardened.

## 1. Thesis
01 proves a CPU is *possible* (NAND → ALU → fetch-decode-execute → ISA). A explains why a real CPU is
*fast*, and it all traces to ONE forcing function: **the processor can do arithmetic far faster than
memory can feed it data or than a serial instruction stream can supply independent work.** So real
hardware spends its transistor budget on three families of tricks: (1) a **memory hierarchy** (caches,
TLB, virtual memory) to hide the memory wall behind locality; (2) **pipelining** to overlap the stages
01 ran serially; and (3) **instruction-level parallelism** (superscalar/out-of-order/branch
prediction) to find independent work to keep the pipeline full. Every one of these is *speculative or
locality-dependent*, which is why software layout and access patterns — not clock speed — decide real
performance.

## 2. The performance ladder (the bespoke spine)

### Rung 0 — The correct machine 01 built (recap, the baseline)
- NAND → gates → ripple/carry-lookahead adder → ALU → registers/PC/RAM → fetch-decode-execute → ISA.
- **Two's complement** is the keystone (carried up from 01): RECOMPUTED 8-bit range [−128, 127]
  (asymmetric — one extra negative, one zero, uniform ordering), and `5 − 3 = 5 + (~3+1)` mod 2^8 = 2 →
  ONE adder + invert does add *and* subtract (Eater realizes it physically). Control = decode opcode →
  micro-sequence of control words.
- This machine is *correct* and *slow*: ~1 instruction at a time, every memory access at full DRAM
  latency. The rest of the ladder closes the gap.

### Rung 1 — Hide memory: the cache hierarchy + AMAT (CS:APP ch.6 / 13)
- The **memory wall**: RECOMPUTED latency ladder spans ~6 orders of magnitude L1 (~1 ns) → disk seek
  (~2 ms). The *ratios*, not absolute ns, are the load-bearing fact (13 caveat).
- Caches turn DRAM latency into ~cache latency *when locality holds*. RECOMPUTED **AMAT = hit +
  miss_rate·penalty**: a 95% L1 hit rate → AMAT ≈ 6 ns vs 100 ns raw DRAM. The **locality cliff**:
  drop hit rate to 80% → AMAT ≈ 21 ns (3.5× worse). Performance is *governed by hit rate*.
- **Spatial locality**: a **64-byte line** holds 16 ints → stride-1 access pays 1 miss per 16 elements;
  stride-64 wastes 60/64 of every fetched line. This is the slope of CS:APP's **memory mountain** and
  WHY row-major traversal and cache-friendly data layout (06) dominate real throughput.

### Rung 2 — Overlap the stages: pipelining + hazards (01/CS:APP)
- 01 ran fetch/decode/execute serially. A k-stage **pipeline** overlaps them: RECOMPUTED a 5-stage
  pipe → ~4.98× throughput on a 1000-instruction stream (the (k−1) fill cost amortizes away).
- The catch is **hazards**: data (need a not-yet-written result), control (don't know the next PC until
  a branch resolves), structural (resource conflict). RECOMPUTED CPI = 1 + f·s → 20% of instrs
  stalling 3 cycles = CPI 1.6. **Forwarding/bypassing** cuts data-hazard stalls; **branch prediction**
  cuts control-hazard stalls.

### Rung 3 — Predict the future: branch prediction (uarch)
- A branch stalls the pipe until resolved; deeper pipes cost more on a miss. RECOMPUTED mispredict CPI
  add = branch_frac · mispredict_rate · pipe_depth → 20% branches × 5% miss × 15-deep = +0.15 CPI; a
  99% predictor cuts that 5× vs 95%. WHY predictor accuracy dominates branch-heavy code and earns huge
  silicon on deep out-of-order cores. (Specific predictor designs — TAGE/perceptron — `[UNVERIFIED]`.)

### Rung 4 — Find independent work: superscalar + OOO/ILP (uarch)
- A **w-wide superscalar** can retire up to w instructions/cycle (IPC up to w) — but RECOMPUTED only
  if there's independent work: a single dependency chain pins IPC to 1 regardless of issue width. WHY
  hardware adds **out-of-order execution + register renaming** (break false WAR/WAW deps) +
  reservation stations + a reorder buffer to *expose* instruction-level parallelism. This is the
  hardware analogue of the parallelism limits 13/20/27 hit at the system scale.

### Rung 5 — The illusion of private, infinite memory: virtual memory + TLB (CS:APP ch.9 / B)
- Every process sees a private linear address space; the MMU translates virtual → physical per access.
- RECOMPUTED: a 4 KB page → 12 offset bits; a 48-bit VA → 36 VPN bits → a flat table would need 2^36
  entries (impossible) → **multi-level page tables**: 4 KB tables of 8-byte PTEs index 9 bits/level →
  **4 levels** for x86-64.
- A walk is therefore expensive: the **TLB** caches recent translations; RECOMPUTED a TLB *miss* costs
  ~4 dependent memory accesses (~400 ns) → WHY huge pages / TLB reach matter for large working sets.
  This rung hands directly DOWN into appendix B (Linux page tables, `mmap`, page cache).

### Rung 6 — Keep many cores consistent: coherence + ordering (CS:APP, conceptual)
- Multiple cores with private caches need **cache coherence** (MESI-style invalidation) so a write on
  one core is visible to others, plus a **memory-ordering** model so reordering doesn't break
  synchronization. Mechanism reused conceptually; exact MESI/MOESI transition tables `[UNVERIFIED]`
  (H&P not fetched). This is the hardware floor under spine 11's "shared memory is itself a tiny
  distributed system."

## 3. The "one wall, three families of tricks" reconciliation (appendix payload)
| rung | trick | wall it fights | load-bearing number | anchor |
|---|---|---|---|---|
| 1 | cache hierarchy / AMAT | memory latency wall | 95% hit → 6 ns vs 100 ns | CS:APP ch.6 / 13 |
| 1 | 64B line / spatial locality | memory bandwidth wall | 16 ints/line; stride-64 = 25% useful | CS:APP / 06 |
| 2 | pipelining | serial stage execution | 5-stage ≈ 4.98× | 01/CS:APP |
| 2 | forwarding/prediction | hazards (CPI > 1) | CPI 1 + f·s = 1.6 | 01/CS:APP |
| 3 | branch prediction | deep-pipe mispredict | +0.15 CPI; 99% vs 95% = 5× | uarch |
| 4 | superscalar + OOO | dependency serialization | IPC pinned to 1 by 1 chain | uarch |
| 5 | virtual memory + TLB | translation cost / isolation | 4-level walk = 400 ns | CS:APP ch.9 / B |
| 6 | coherence + ordering | multicore inconsistency | MESI invalidation | CS:APP (conceptual) |

## 4. Common misconceptions to preempt
- "Faster clock = faster computer." The memory wall + hazards + ILP limits dominate; locality and IPC
  decide real throughput.
- "Caches are automatic, so I can ignore them." The locality cliff (95%→80% hit = 3.5× AMAT) means
  access pattern *is* the performance.
- "A cache miss costs one DRAM access." Spatial misses fetch a whole 64B line; TLB misses cost a
  multi-level page walk (~4 accesses).
- "Pipelining makes each instruction faster." It improves *throughput*, not single-instruction latency.
- "More issue width = more performance." Only with independent work; a dependency chain pins IPC to 1.
- "Virtual memory is just swapping to disk." It's primarily address translation + isolation; swapping
  is one consequence.
- "A flat page table works." 2^36 entries is impossible → multi-level tables + TLB are forced.
- "Two's complement is symmetric." TMin has no positive counterpart (−TMin overflows).

## 5. Provenance summary
- **REUSED (line-verified in 01):** NAND→ALU→CPU→ISA path, two's complement encoding, microcode/control
  word, Harvard-vs-von-Neumann, CS:APP ch.6 memory mountain / cache line, CS:APP ch.9 virtual memory /
  page-table sizing. (01 cited nand2tetris + CS:APP/CMU 15-213 + Ben Eater + Petzold/Scott.)
- **REUSED:** 06 (locality), 13 (latency ladder), N (math).
- **RECOMPUTED:** `_recompute.py` (15/15) — two's-complement range + subtract-via-add, pipeline
  speedup + CPI, branch-mispredict CPI, superscalar IPC ceiling, AMAT + locality cliff, cache-line
  stride utilization, multi-level page-table sizing + TLB-miss cost, latency-ladder span.
- **`[UNVERIFIED]` carry-forward (not load-bearing):** Hennessy & Patterson primary text; exact
  micro-uarch (predictor designs, ROB/RS sizes, associativity, MESI tables); SAP-1 control-word bit
  map + Eater 6502 memory map + Petzold/Scott figures (carried from 01); latency absolute numbers
  (ratios are the claim). All blocked behind unreachable hosts / paywalled books; logged, none hardened.

---
**Appendix A reconciled.** Reference-grade, exercise-free, 15/15 recomputed, all mechanisms reused
from 01's line-verified source reads. No chapters yet.
