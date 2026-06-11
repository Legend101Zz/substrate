# Appendix A · computer-architecture — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). Verifies the load-bearing
> claims of A against **line-verified spine canon** — primarily **01** (which cited nand2tetris +
> CS:APP/CMU 15-213 + Ben Eater + Petzold/Scott) plus **06** (locality), **13** (latency ladder), **N**
> (math). **NO new primary fetched this wave** — eater.net / CS:APP hosts HTTP **000** (re-checked
> Wave 18). Every quantitative claim re-derived in `_recompute.py` (15/15). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | NAND functional completeness → gates → adder → ALU → CPU (fetch-decode-execute) → ISA | VERIFIED (reuse) | 01 `_research.md` (nand2tetris Ch.1–5, Eater SAP-1) |
| 2 | **Two's complement**: range asymmetric [−2^(N−1), 2^(N−1)−1]; one ALU does add+subtract via A+~B+1 | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #1; 01 (CS:APP ch.2 encoding; Eater 74LS283+74LS86) |
| 3 | Control = decode opcode → micro-sequence of control words (microcode/ring counter) | VERIFIED (reuse) | 01 (Eater SAP-1 16-control-line word, T-state ring counter; exact bit map `[UNVERIFIED]`) |
| 4 | Harvard (Hack: separate instr/data) vs von-Neumann (SAP-1: single bus) distinction | VERIFIED (reuse) | 01 reconciliation note (teach explicitly) |
| 5 | **Pipelining**: k-stage pipe → ~k× throughput after fill; fill cost amortizes | RECOMPUTED | `_recompute.py` #2 (5000/1004 = 4.98×) |
| 6 | Hazards (data/control/structural) raise CPI above 1.0; forwarding + prediction cut it | RECOMPUTED | `_recompute.py` #2 (CPI = 1 + f·s = 1.6) |
| 7 | **Branch misprediction** penalty ∝ pipeline depth; predictor accuracy dominates branch-heavy perf | RECOMPUTED | `_recompute.py` #3 (+0.15 CPI; 99% vs 95% = 5×); uarch *mechanism* (specific predictor designs `[UNVERIFIED]`) |
| 8 | **Superscalar/ILP**: w-wide issue → IPC up to w *only* with independent work; OOO + register renaming expose ILP | RECOMPUTED | `_recompute.py` #4 (dep chain pins IPC to 1) |
| 9 | **Memory hierarchy / AMAT** = hit + miss_rate·penalty; high hit rate hides DRAM latency | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #5 (95%→6 ns vs 100 ns); 01/CS:APP ch.6 memory mountain |
| 10 | The **locality cliff**: small hit-rate drops multiply AMAT (95%→80% ≈ 3.5×) | RECOMPUTED | `_recompute.py` #5 |
| 11 | **64-byte cache line**; spatial locality → stride sets effective bandwidth (16 ints/line) | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #6; CS:APP memory mountain |
| 12 | **Virtual memory**: 4 KB page → 12 offset bits; flat table impossible → multi-level (4-level for 48-bit VA) | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #7; CS:APP ch.9 (page-table sizing) |
| 13 | **TLB** caches translations; a miss = full page walk ≈ #levels dependent memory accesses (~4×) | RECOMPUTED | `_recompute.py` #7 (4 × 100 ns = 400 ns); feeds appendix B |
| 14 | **Latency ladder** spans ~6 orders of magnitude L1→disk — the GAPS, not absolute ns, are load-bearing | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #8; 13 latency-number ladder |
| 15 | Cache coherence (MESI-style) + memory ordering exist so multicore stays consistent | VERIFIED (reuse, conceptual) | CS:APP / 01 multicore note; exact MESI transition table `[UNVERIFIED]` (Hennessy-Patterson not fetched) |

## `[UNVERIFIED]` carry-forward (none load-bearing — recomputed or reused from 01's line-cited reads)
- **Hennessy & Patterson (CA:AQA) primary text** — pipeline/ILP/cache/coherence canon; not fetched
  (no reachable host). Mechanisms reused from 01's CS:APP citations; H&P-specific figures illustrative.
- **Exact micro-uarch specifics** — branch-predictor designs (TAGE/perceptron), ROB/reservation-station
  sizes, real cache associativity/inclusion policies, MESI/MOESI transition tables — version/uarch
  dependent; taught as *mechanisms with arithmetic*, never as fixed silicon numbers.
- **Carried from 01 (unchanged):** exact SAP-1 control-word bit order / EEPROM map / per-instruction
  T-states (community mirror, not eater.net text); Eater 6502 memory map; Petzold *Code* / Scott
  *But How Do It Know?* exact figures (paywalled book text).
- **Latency ladder absolute numbers** are order-of-magnitude / year-sensitive (13 caveat) — the
  *ratios* are the load-bearing claim.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 15/15);
all mechanisms reused from 01's line-verified source reads.
