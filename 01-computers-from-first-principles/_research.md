# 01 — computers-from-first-principles · reconciled research brief

Status: Wave 1 research complete (2 of 2 clusters). Formal `factchecker` pass DEFERRED
(blocked by spend limit — see meta/SESSION_LOG.md and ADR-002).

This file reconciles the per-cluster briefs. Read those for full depth:
- `_research_nand2tetris-petzold.md` — NAND→ALU→CPU→ISA build path (nand2tetris, Petzold *Code*, Scott *But How Do It Know?*). 13 primary sources.
- `_research_eater-csapp.md` — physical/electrical CPU (Ben Eater 8-bit SAP-1 + 6502) and machine-level/bit-level representation (CS:APP / CMU 15-213). 10 primary sources.

## Cross-cluster synthesis (the through-line)
The two clusters are the SAME story told at two altitudes and they interlock cleanly:
- **Logic → arithmetic:** NAND functional completeness → gates → half/full/ripple adder →
  carry-lookahead as the optimization (nand2tetris Ch.1–2; Eater realizes it physically with
  74LS283 adders + 74LS86 XOR for two's-complement subtract).
- **Two's complement** is the shared keystone: chosen so ONE adder does add *and* subtract
  (`A−B = A+~B+1`), one zero, uniform carry/ordering. nand2tetris states the rule; CS:APP ch.2
  gives the encoding/range math (TMin=−2^(N−1), asymmetric); Eater's ALU is the physical proof.
- **Memory → sequential logic:** DFF/clock/register/RAM/PC. nand2tetris treats the DFF as a
  primitive; Petzold/Scott fill in the SR-latch→flip-flop rung (the one altitude seam to bridge).
- **CPU = fetch-decode-execute:** nand2tetris Hack CPU (Harvard) vs Eater's SAP-1 microcoded
  control word (von-Neumann-ish, 16 control lines, T-state ring counter, microcode in EEPROM).
  Decode = combinational/lookup from opcode→sequence of control words.
- **Real ISA:** Hack ISA (`111a cccc ccdd djjj`) as a clean teaching ISA; Eater 6502 + CS:APP
  x86-64 (System V AMD64 calling convention, stack frames, addressing modes) as real ISAs.
- **Up into the appendix:** memory hierarchy / caches / the memory mountain (CS:APP ch.6) is the
  natural hand-off into Appendix A (computer-architecture) and toward sub-course 04/06.

## Reconciliation notes / no conflicts
The clusters do not contradict each other. One framing nuance to handle in prose: nand2tetris's
Hack is a **Harvard** architecture (separate instr/data memory) though the book initially calls
it "von Neumann"; Eater's SAP-1 is closer to a classic single-bus von Neumann machine. Teach the
distinction explicitly rather than glossing.

## Best build-your-own targets (this sub-course → /build)
- Keystone: **Ben Eater 8-bit SAP-1** breadboard CPU (clock→registers/bus→ALU→RAM/MAR→PC→
  microcode). Software fallbacks: Logisim Evolution, or XarkLabs VHDL port (FPGA/sim).
- **nand2tetris Projects 1–5** (gates → ALU → memory → CPU) as the from-logic path.
- **Eater 6502** to graduate to a real ISA on hardware.
- **CS:APP labs** for the program-level view: Data → Bomb → Attack → Cache (+ optional Y86-64 Arch lab).

## Consolidated open questions / gaps (load-bearing — verify before drafting)
- [UNVERIFIED] Exact SAP-1 control-word bit order / EEPROM bit map and per-instruction T-state
  tables — sourced from a community SAP-1 mirror, not the eater.net page text. Confirm against
  Eater's control/microcode videos before teaching exact bit positions. (Eater's B register is
  ALU-read-only — no "B out".)
- [PARTIAL] Eater 6502 memory map ($0000–$3FFF RAM / $4000–$7FFF I/O / $8000–$FFFF ROM) echoed
  from community write-ups — confirm against official eater.net/6502 schematics.
- [PARTIAL] Scott *But How Do It Know?* exact per-step control micro-wiring and Petzold *Code*
  Ch.17 figures rest partly on paywalled book text + Wikipedia corroboration (two's-complement,
  flip-flop). Verify exact wording/figures against print copies before quoting.
- CS:APP edition drift: cite the BOOK CHAPTER (3e), not a specific semester's lecture number.
- Don't conflate Y86-64 (CS:APP processor-design ch.4) with x86-64 (machine-level ch.3).
- [GAP] eater.net/8bit/output page and per-video transcripts (control word, microcode) not fully
  fetched — the main primary-source gap for this sub-course.
