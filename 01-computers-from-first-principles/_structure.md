# 01 — Computers From First Principles · _structure.md

**Identity:** the absolute floor of the course. Build a computer from a single logic
primitive up to a running program, so every later abstraction (process, socket, pointer,
cache) rests on something the reader has personally assembled.

**Bespoke shape — "the build-up ladder."** This sub-course is NOT taught as
theory→case-study. It is a strict CONSTRUCTIVE ascent: each chapter is one rung that uses
only what previous rungs built, ending in a running program on a CPU you understand. The
ordering IS the pedagogy — you may never use a part you haven't built. (Grounded in the
two reconciled clusters: nand2tetris/Petzold build-path + Eater/CS:APP physical & program
view, which interlock at two altitudes telling one story.)

## Dependency position
- **Depends on:** nothing (foundation floor).
- **Feeds into:** 04 (OS needs CPU+memory model), 05 (runtimes need ISA/bytecode mental
  model), 06 (cache-line/locality intuition), A (architecture goes deeper on this exact
  ladder), B (kernel sits on this hardware).
- **Appendix link DOWN:** A-computer-architecture continues this ladder into the
  performance era (cache/pipeline/OOO/TLB/coherence). 01 ends exactly where A begins.

## Chapter specs (3–5 lines each)
1. **Bits, two's complement, and why** — 0s/1s as voltage; binary/hex; the keystone:
   two's complement chosen so ONE adder does add AND subtract (`A−B = A+~B+1`), one zero,
   uniform ordering. Range/TMin asymmetry (CS:APP ch.2). Sets up the ALU.
2. **From NAND to gates** — NAND functional completeness → NOT/AND/OR/XOR/MUX/DEMUX
   (nand2tetris Ch.1). The "one primitive, everything else derived" thesis of the whole
   course in miniature.
3. **Arithmetic: adders → ALU** — half/full/ripple adder → carry-lookahead as the
   optimization; two's-complement subtract via XOR-invert + carry-in. Eater's 74LS283/86
   as the physical proof; nand2tetris ALU as the logical one.
4. **Memory: latch → flip-flop → register → RAM → PC** — the sequential-logic seam.
   Bridge the one altitude gap: SR-latch → D flip-flop (Petzold/Scott) that nand2tetris
   treats as primitive. Clock, registers, addressable RAM, program counter.
5. **The CPU: fetch–decode–execute** — tie datapath + control. Two real teaching designs
   contrasted: nand2tetris Hack (Harvard, clean ISA) vs Eater SAP-1 (von-Neumann-ish,
   microcoded 16 control lines, T-state ring counter, EEPROM microcode). Teach the
   Harvard/von-Neumann distinction explicitly (reconciliation note).
6. **Instruction sets: from Hack to real silicon** — Hack ISA (`111a cccc ccdd djjj`)
   as clean model; then a real ISA: registers, addressing modes, the x86-64 machine-level
   view (stack frames, System V AMD64 calling convention) (CS:APP ch.3). Don't conflate
   Y86-64 with x86-64.
7. **A program, end to end** — walk one tiny program from C → assembly → machine code →
   fetch-decode-execute on the CPU built in ch.5. The payoff: nothing magic remains.
   Hands off UPWARD to memory hierarchy → appendix A.

## Paired build lab (/build → own-cpu, optional own-assembler)
**Keystone:** Ben Eater 8-bit SAP-1 breadboard CPU (clock→bus/registers→ALU→RAM/MAR→PC→
microcode). Software fallbacks: Logisim Evolution / nand2tetris HDL. Ladder:
**nand2tetris Projects 1–5** (gates→ALU→memory→CPU) as the from-logic path; **Eater 6502**
to graduate to a real ISA; **CS:APP Data/Bomb/Attack/Cache labs** for the program-level view.
Lab rungs mirror chapter rungs 1:1.

## Diagrams needed
- NAND→gate derivation tree; full-adder → ripple/CLA adder; SR-latch→D-flip-flop timing;
  register/RAM addressing; the datapath+control block diagram (Hack AND SAP-1 side by
  side); fetch-decode-execute cycle as a state loop; one annotated machine-instruction
  bitfield (`111a cccc ccdd djjj`).
- `<!-- IMAGE PROMPT -->` candidate: a real Eater breadboard photo-style render labeling
  clock/bus/ALU/RAM modules (a real visual beats prose here).

## Sources / gaps to honor (from _research.md)
- `[UNVERIFIED]` exact SAP-1 control-word bit order / EEPROM bit map / per-instruction
  T-states — confirm against Eater's control/microcode videos before teaching exact bits.
  (Eater's B register is ALU-read-only — no "B out".)
- `[PARTIAL]` Eater 6502 memory map; Scott/Petzold exact figures (paywalled book text) —
  verify against print before quoting. Cite CS:APP by CHAPTER (3e), not lecture number.
- `[GAP]` eater.net/8bit/output page + video transcripts not fully fetched — the main
  primary-source gap; fetch during drafting if reachable.
