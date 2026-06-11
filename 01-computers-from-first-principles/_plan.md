# 01 — Computers From First Principles · _plan.md (Phase 3 PLAN — outline only, NOT a draft)

> **Status:** PLAN for annotation. No prose written. Per START_HERE Phase 3, this outline STOPS for
> your notes before `writer` drafts anything. Derived from `01/_structure.md` (the "build-up ladder"
> — a strict constructive ascent where ordering IS the pedagogy: never use a part you haven't built)
> + the two reconciled clusters (nand2tetris/Petzold build-path + Eater/CS:APP physical/program view).

## Target shape & length
- 7 chapters, each a single rung that uses ONLY what previous rungs built, ending in a running
  program on a CPU the reader has assembled. The ladder discipline is the whole point.
- Each chapter: intuitive model THEN deep mechanism (STYLE arc), ≥1 precise diagram per major
  mechanism, every non-obvious claim cited to a primary, cross-link DOWN to appendix A where it
  continues the ladder into the performance era, link to the paired /build rung.
- Voice: senior mentoring a capable junior; define jargon on first use; no hand-waving.

## Chapter-by-chapter outline (content to draft after sign-off)
1. **Bits, two's complement, and why**
   - Intuitive: 0/1 as voltage thresholds; binary/hex as human-readable groupings.
   - Mechanism: two's complement chosen so ONE adder does add AND subtract (`A−B = A+~B+1`), one
     zero, uniform ordering; TMin/TMax asymmetry. Cite CS:APP ch.2.
   - Sets up the ALU (ch.3). Diagram: number-circle + the add/subtract-with-one-adder identity.
2. **From NAND to gates**
   - Intuitive: one brick, everything else is arrangement.
   - Mechanism: NAND functional completeness → NOT/AND/OR/XOR/MUX/DEMUX. Cite nand2tetris Ch.1.
   - This is the course's "one primitive → everything" thesis in miniature. Diagram: derivation tree.
3. **Arithmetic: adders → ALU**
   - Intuitive: addition is just gates that carry.
   - Mechanism: half → full → ripple adder; carry-lookahead as the speed optimization; two's-comp
     subtract via XOR-invert + carry-in. Eater 74LS283/86 = physical proof; nand2tetris ALU = logical.
   - Diagram: full-adder → ripple/CLA. Reuses only ch.1–2.
4. **Memory: latch → flip-flop → register → RAM → PC**
   - Intuitive: how a circuit "remembers" — feedback.
   - Mechanism: the sequential-logic seam. Bridge the altitude gap nand2tetris glosses: SR-latch →
     D flip-flop (Petzold/Scott) that nand2tetris treats as primitive. Clock, registers, addressable
     RAM, program counter. Diagram: SR→D timing + RAM addressing. **Reconciliation note** (cluster
     interlock at the flip-flop altitude).
5. **The CPU: fetch–decode–execute**
   - Intuitive: the machine that does one tiny thing, forever, fast.
   - Mechanism: datapath + control tied together. Contrast two real teaching designs: nand2tetris
     **Hack** (Harvard, clean ISA) vs Eater **SAP-1** (von-Neumann-ish, microcoded 16 control lines,
     T-state ring counter, EEPROM microcode). Teach Harvard vs von-Neumann explicitly.
   - Diagram: datapath+control for Hack AND SAP-1 side by side; fetch-decode-execute as a state loop.
6. **Instruction sets: from Hack to real silicon**
   - Intuitive: an ISA is the contract between software and the datapath.
   - Mechanism: Hack ISA (`111a cccc ccdd djjj`) as the clean model; then a real ISA — registers,
     addressing modes, x86-64 machine-level view (stack frames, System V AMD64 calling convention).
     Cite CS:APP ch.3. **Do NOT conflate Y86-64 with x86-64.** Diagram: annotated instruction bitfield.
7. **A program, end to end**
   - The payoff chapter: walk one tiny program C → assembly → machine code → fetch-decode-execute on
     the CPU built in ch.5. Nothing magic remains.
   - Hands off UPWARD: memory hierarchy → appendix A (01 ends exactly where A begins).

## Paired build lab (/build → own-cpu, optional own-assembler) — lab rungs mirror chapters 1:1
- Keystone: Ben Eater 8-bit SAP-1 breadboard CPU (clock → bus/registers → ALU → RAM/MAR → PC →
  microcode). Software fallbacks: Logisim Evolution / nand2tetris HDL.
- Ladder: nand2tetris Projects 1–5 (gates→ALU→memory→CPU) = the from-logic path; Eater 6502 to
  graduate to a real ISA; CS:APP Data/Bomb/Attack/Cache labs for the program-level view.

## Diagrams (author in IMPLEMENT)
- NAND→gate derivation tree; full-adder→ripple/CLA; SR-latch→D-flip-flop timing; register/RAM
  addressing; datapath+control (Hack AND SAP-1 side by side); fetch-decode-execute state loop;
  one annotated machine-instruction bitfield (`111a cccc ccdd djjj`).
- **`<!-- IMAGE PROMPT -->` candidate:** Eater breadboard photo-style render labeling
  clock/bus/ALU/RAM modules (a real visual beats prose). Log in assets/diagrams/image-prompts.md.

## Sources / gaps to honor (carried verbatim from _research.md — erase nothing)
- `[UNVERIFIED]` exact SAP-1 control-word bit order / EEPROM bit map / per-instruction T-states —
  confirm against Eater's control/microcode videos before teaching exact bits. (Eater's B register
  is ALU-read-only — no "B out".) **Retry receipt: eater.net/8bit + /8bit/output still 000 this
  session — gap stands, carried, nothing erased.** Teach the CONCEPT (microcode/T-states/control
  lines) now; do NOT assert exact bit positions until the bit-map is fetched.
- `[PARTIAL]` Eater 6502 memory map; Scott/Petzold exact figures (paywalled) — verify against print
  before quoting. Cite CS:APP by CHAPTER (3e), not lecture number.
- `[GAP]` eater.net/8bit/output page + video transcripts not fully fetched — the main primary-source
  gap; re-fetch during drafting if reachable (still unreachable as of this PLAN).

## Open questions for your annotation
- Q1: x86-64 vs RISC-V as the "real ISA" in ch.6. Structure says x86-64 (CS:APP/System V). Want me
  to add a short RISC-V sidebar (cleaner ISA, increasingly the teaching default), or stay x86-64-only?
- Q2: Ch.5 teaches BOTH Hack and SAP-1 side by side — keep both (Harvard vs von-Neumann is the
  lesson), or lead with one and make the other the cross-link? (Lean: keep both, it's the reconciliation.)
- Q3: Given the SAP-1 bit-map is still `[UNVERIFIED]` (network blocked), confirm you're OK with ch.5
  teaching microcode/T-states conceptually with the exact EEPROM bits deferred behind the flag.
