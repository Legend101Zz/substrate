# 01 — Research brief: Ben Eater breadboard CPU + CS:APP machine-level

Scope: the physical/electrical reality of a CPU (Ben Eater 8-bit breadboard + 6502) and the
machine-level/bit-level representation of programs (CS:APP / CMU 15-213). Briefs only.

---

## 1. Key mechanisms (deep & precise, each with its forcing constraint)

### A. The clock & synchronous logic (Eater 8-bit, clock module)
- A 555 timer drives the whole machine. Three configurations are used: **astable** (free-running
  oscillator, adjustable <1 Hz → few hundred Hz), **monostable** (single clean pulse for one-shot
  step), **bistable** (flip-flop, a toggle/latch). The astable + monostable + bistable are combined
  so the operator can switch between *automatic run* and *manual single-step*. Glue: 74LS04 (hex
  inverter), 74LS08 (quad AND), 74LS32 (quad OR) implement the run/step select and a HLT (halt) gate
  that can stop the clock.
- **Forcing constraint:** every register latches on the *same* clock edge. Without one shared clock
  there is no defined moment when "the bus value is valid and may be captured," so a global clock is
  what makes the design *synchronous* (state changes only at edges, combinational logic settles
  between edges). Single-step exists because at human speed you can *see* one micro-operation at a
  time. Src: https://eater.net/8bit/clock

### B. Shared bus + tri-state (Eater 8-bit, registers module)
- All major modules hang off ONE 8-bit bus. Registers are **74LS173** 4-bit D registers, two
  cascaded per 8-bit register (A, B, IR, MAR built this way). Bus driving uses **74LS245** octal
  bus transceivers / tri-state buffers.
- A tri-state output has three states: drive 0, drive 1, or **high-impedance (Hi-Z)** = electrically
  disconnected. At most one device may drive the bus per cycle; everyone else is Hi-Z.
- Each register has two control lines: **"in"/load** (latch bus → register on clock edge) and
  **"out"/enable** (drive register → bus via 245). These are the AI/AO, BI/(no BO), II/IO, etc.
- **Forcing constraint:** if two outputs drove the same wire simultaneously (one 0, one 1) you'd get
  a short / contention / damage. Tri-state is the *only* way to multiplex many sources onto one set
  of wires without point-to-point routing. This is literally why a "bus" needs tri-state.
  Src: https://eater.net/8bit/registers

### C. ALU (Eater 8-bit, alu module)
- Adder = two **74LS283** 4-bit adders cascaded (carry chained) → 8-bit add. **74LS86** quad XOR
  gates sit on the B input: when **SU (subtract)** is asserted, XOR inverts B's bits AND the same
  SU line feeds carry-in = 1 → this computes `A + (~B) + 1 = A − B` (two's complement subtraction
  with one adder). Output to bus via **74LS245** (EO = "sum out"). Flags (carry, zero) computed with
  74LS02/74LS08 NOR/AND and latched into a **74LS173** flags register on **FI**; zero flag = NOR of
  all 8 sum bits, carry from the high adder's carry-out.
- **Forcing constraint:** one adder must do both add and subtract → two's complement is chosen so
  subtraction = "invert + add one," requiring only XOR gates + carry-in, no second subtractor.
  Src: https://eater.net/8bit/alu

### D. Program counter (Eater 8-bit, pc module)
- **74LS161** 4-bit synchronous binary counter. Control lines: **CE** (count enable → increment),
  **CO** (counter out → tri-state value onto bus via 245), **J** (jump = parallel-load the bus value
  into the counter). It feeds the MAR for instruction fetch.
- **Forcing constraint:** the machine needs to remember "which instruction is next" across cycles
  and support non-sequential control flow (jumps) → a loadable counter. Jump = load PC from bus.
  Src: https://eater.net/8bit/pc

### E. RAM + Memory Address Register (Eater 8-bit, ram module)
- Storage = **74189** (a.k.a. 74LS189) 16×4 SRAM; paired for 16 bytes × 8 bits → only **16 bytes**,
  the machine's "biggest limitation," because addresses are 4 bits. MAR = **74LS173** latches a 4-bit
  address. **74LS157** multiplexer selects between *program-mode* (DIP switches) and *run-mode* (bus)
  addressing so you can hand-enter a program; 74LS00/74LS04 for read/write control.
- **Forcing constraint:** RAM is addressed, not bussed-directly — you must first *latch an address*
  (MAR) then *access*; that's the two-step that makes load/store instructions take ≥2 microsteps.
  Src: https://eater.net/8bit/ram

### F. Control logic / microcode — fetch-decode-execute on real hardware (Eater 8-bit, control)
- The CPU is driven by a **16-bit control word** (one bit per control line). Canonical signal set:
  **HLT** (halt clock), **MI** (MAR in), **RI** (RAM in), **RO** (RAM out), **IO** (instruction reg
  out), **II** (instruction reg in), **AI** (A in), **AO** (A out), **EO** (ALU sum out), **SU**
  (subtract), **BI** (B in), **OI** (output reg in), **CE** (counter enable), **CO** (counter out),
  **J** (jump), **FI** (flags in).
- Each control word is one **T-state (microstep)**. A **74LS161** acts as the **step/ring counter**
  (T0..T5, ~6 microsteps max per instruction). The first two microsteps are the **fetch** common to
  every instruction: **T0 = CO|MI** (PC→MAR), **T1 = RO|II|CE** (RAM→IR, increment PC). Remaining
  microsteps are the per-opcode **execute**, looked up from the **instruction register's high nibble
  (opcode)** + step counter + flags.
- Microcode is stored in **28C16 EEPROMs** (programmed via an Arduino). The EEPROM address = {flags,
  opcode (4 bits), step (3 bits)}; the data = the active control bits. Conditional jumps (**JC/JZ**)
  work by feeding the carry/zero flags into the microcode address so the same opcode maps to
  different control words depending on flags.
- Instruction set is 4-bit opcode + 4-bit operand: **NOP, LDA, ADD, SUB, STA, LDI, JMP, JC, JZ,
  OUT, HLT** — Turing-completeness reached once conditional jumps exist.
- **Forcing constraint:** "decode" = combinational/lookup mapping from opcode bits to a *sequence*
  of control words. Microcode-in-ROM is chosen over hard-wired gates because it's *reprogrammable* —
  you change behavior by reflashing, not rewiring. Src: https://eater.net/8bit/control ;
  control-word signal list mirrored at https://www.ullright.org/ullWiki/show/ben-eater-8-bit-computer-sap1
  (this is the SAP-1 "Simple-As-Possible" architecture from Malvino, which Eater's build follows).

### G. A REAL ISA on a breadboard (Eater 6502 series)
- Builds a working computer around the **WDC 65C02** (CMOS 6502): hardwire power/clock/reset, then
  use an **Arduino Mega** as a logic analyzer to watch the **16-bit address bus + 8-bit data bus +
  R/W + clock (Φ2)** on every cycle (sketch `6502-monitor.ino`). You literally watch the CPU fetch
  the reset vector at $FFFC/$FFFD and start executing.
- **Address decoding** uses a **74HC00 quad NAND** (Eater uses ~3 NAND gates): high address bits
  select ROM vs RAM vs I/O. Eater memory map: **RAM 16K $0000–$3FFF, I/O $4000–$7FFF, ROM 32K
  $8000–$FFFF** (ROM at top because the 6502 reads its reset/IRQ vectors from $FFFA–$FFFF). ROM =
  28C256 EEPROM (machine code generated by a Python script); RAM = 62256.
- **65C22 VIA** (Versatile Interface Adapter) provides parallel I/O ports to drive a HD44780 LCD and
  read buttons; later videos add interrupts and serial.
- **Forcing constraint:** a real CPU is *passive* — it only does fetch-execute over a bus; everything
  else (memory, I/O) must be **memory-mapped** and selected by **address decoding**, and ROM must
  live where the reset vector points. Propagation delay matters: Eater keeps only one NAND-gate delay
  in the Φ2→chip-select path so memory is selected before the access window closes.
  Src: https://eater.net/6502 ; decoding detail:
  https://www.wilsonminesco.com/6502primer/addr_decoding.html (one citation hop, WHY of decode budget)

### H. Data representation — bits/bytes, integers, two's complement (CS:APP ch 2)
- Two's complement: for N bits, value = `−x_{N−1}·2^{N−1} + Σ x_i·2^i`. Range is **asymmetric**:
  `TMin = −2^{N−1}` … `TMax = 2^{N−1}−1` (one more negative than positive). `−TMin = TMin`
  (overflows). Non-negative values share encodings with unsigned. Sign = top bit.
- Unsigned/signed addition wrap modulo 2^N; this is exactly the breadboard adder's behavior.
- Floating point (IEEE 754, CS:APP 2.4): value = `(−1)^s · M · 2^E`; fields sign|exp|frac;
  normalized vs denormalized (gradual underflow near 0), special values ∞/NaN; rounding (round-to-
  even). Not the same as reals: not associative, finite precision.
- **Forcing constraint:** two's complement is chosen because **one adder does add AND subtract**
  (no separate negate hardware, no −0), and comparison/carry logic is uniform. Src: CS:APP3e ch 2
  (2.2 integer encodings, 2.3 integer arithmetic, 2.4 floating point):
  https://csapp.cs.cmu.edu/ ; lecture mapping "Bits, Bytes & Ints" (2.1–2.3) and "Floating Point"
  (2.4): https://www.cs.cmu.edu/afs/cs/academic/class/15213-f15/www/schedule.html

### I. x86-64 machine-level: registers, addressing, control, the stack & calling convention (CS:APP ch 3)
- 16 general-purpose 64-bit registers (%rax,%rbx,…,%rsp,%rbp,%r8–%r15); %rip = program counter;
  condition codes (CF/ZF/SF/OF) set by arithmetic, tested by jumps (control = ch 3.6).
- Memory operand addressing mode: `D(Rb,Ri,S)` → address = `Rb + Ri·S + D` (base + index·scale +
  displacement). One mode covers array/struct access.
- **Stack** grows toward lower addresses; **%rsp** points at the top. `call` pushes return address
  and jumps; `ret` pops it. A **stack frame** per call holds saved registers, locals, spilled args.
- **System V AMD64 calling convention:** first 6 integer args in **%rdi,%rsi,%rdx,%rcx,%r8,%r9**;
  return in %rax; **caller-saved** (%rax,%rdi,…,%r10,%r11) vs **callee-saved**
  (%rbx,%rbp,%r12–%r15); 16-byte stack alignment.
- **Forcing constraint:** procedures nest and recurse → you need LIFO storage that the hardware
  supports cheaply → a stack with push/pop + a return-address discipline. A *convention* is needed
  because separately-compiled functions must agree on where args/return/saved registers live.
  Src: CS:APP3e ch 3 (3.4 access, 3.6 control, 3.7 procedures, 3.8–3.9 arrays/structs); lecture
  mapping: https://www.cs.cmu.edu/afs/cs/academic/class/15213-f15/www/schedule.html

### J. Memory hierarchy, caches, locality, the memory mountain (CS:APP ch 6)
- Hierarchy: registers → L1/L2/L3 SRAM cache → DRAM main memory → SSD/disk. Each level is a cache
  for the one below; smaller/faster/costlier per byte as you go up.
- Caches exploit **locality**: *temporal* (reuse same data soon) and *spatial* (use nearby data
  soon). Cache organized in **sets / lines / blocks**; access classified as hit, cold/compulsory
  miss, conflict miss, capacity miss. Direct-mapped vs set-associative.
- **The memory mountain**: a 2-D plot of read throughput vs (working-set size, stride) — ridges =
  cache levels, slopes = spatial locality. CS:APP's signature demonstration that effective memory
  speed depends on access pattern, not just hardware.
- **Forcing constraint:** fast SRAM is small & expensive, big DRAM/disk is slow & cheap — physics +
  economics force a *hierarchy* and make locality the lever programmers pull. Src: CS:APP3e ch 6
  (6.1–6.3 hierarchy, 6.4–6.7 cache memories, 6.6 memory mountain):
  https://www.cs.cmu.edu/afs/cs/academic/class/15213-f15/www/schedule.html

---

## 2. Foundational sources (one canonical per claim)

Ben Eater 8-bit (eater.net):
- Overview / part list: https://eater.net/8bit
- Clock module: https://eater.net/8bit/clock
- Registers + bus + tri-state: https://eater.net/8bit/registers
- ALU: https://eater.net/8bit/alu
- RAM + MAR: https://eater.net/8bit/ram
- Program counter: https://eater.net/8bit/pc
- Output register: https://eater.net/8bit/output
- Control logic / microcode / instruction decode: https://eater.net/8bit/control
- SAP-1 control-word signal reference (mirror): https://www.ullright.org/ullWiki/show/ben-eater-8-bit-computer-sap1

Ben Eater 6502 (real ISA):
- Series hub + schematics + monitor sketch: https://eater.net/6502
- 6502 address-decoding WHY (one hop): https://www.wilsonminesco.com/6502primer/addr_decoding.html

CS:APP / CMU 15-213:
- Book site: https://csapp.cs.cmu.edu/  (3e: https://csapp.cs.cmu.edu/3e/)
- 15-213 F15 lecture→chapter schedule (canonical topic/chapter map): https://www.cs.cmu.edu/afs/cs/academic/class/15213-f15/www/schedule.html
- Current course home: https://www.cs.cmu.edu/~213/
- Labs (Data/Bomb/Attack/Cache/Arch/…): https://csapp.cs.cmu.edu/3e/labs.html
- Courses-based-on-CSAPP index: http://www.csapp.cs.cmu.edu/3e/courses.html

---

## 3. "Why it's this way" — forcing constraints

- **Why a global clock / synchronous logic:** combinational logic has *propagation delay*; outputs
  are garbage until signals settle. The clock period must exceed the worst-case path so that at the
  edge all inputs are valid. The edge is the single agreed moment to capture state. (Eater clock;
  CS:APP/15-213 timing.)
- **Why tri-state + a shared bus:** point-to-point wiring of N modules is N² wires; a shared bus is
  O(N) but then only one driver may talk at a time → tri-state Hi-Z lets non-drivers disconnect,
  preventing bus contention/shorts. (Eater registers.)
- **Why two's complement:** a single adder performs both add and subtract (`A−B = A+~B+1`), there is
  exactly one zero, and ordering/carry logic is uniform — minimizing gates/power/cost. (CS:APP 2.2–
  2.3; physically realized by Eater's XOR+carry-in ALU.)
- **Why a memory hierarchy:** SRAM is fast but low-density/expensive; DRAM/disk are dense/cheap but
  slow. No single technology is both fast and big and cheap, so you stack them and rely on locality.
  (CS:APP 6.)
- **Why a stack:** function calls nest and recurse (LIFO lifetime). A stack gives O(1) push/pop
  allocation of frames + a natural place for the return address. Hardware `call`/`ret`/`%rsp` bake
  this in. (CS:APP 3.7.)
- **Why a calling convention:** separately compiled code must agree where args, return value, and
  saved registers live, and which registers a callee may clobber — otherwise functions can't
  interoperate. (CS:APP 3.7, System V AMD64 ABI.)
- **Why memory-mapped I/O + address decoding (6502):** the CPU only knows fetch/load/store over an
  address bus; peripherals must masquerade as memory addresses, and decode logic routes each address
  to the right chip. ROM must sit where the reset vector ($FFFC) points. Decode delay budget is set
  by Φ2 timing. (Eater 6502; Wilson Mines primer.)

---

## 4. Common misconceptions to preempt

- "The CPU executes high-level code / the clock 'is' the program." No — the clock only sequences
  micro-operations; meaning lives in memory contents + microcode.
- "One instruction = one clock cycle." False on Eater's machine: each instruction is **multiple
  T-states/microsteps** (fetch is 2, execute is up to ~4). Even on real CPUs, micro-ops/pipelining
  hide multi-cycle work.
- "Subtraction needs a subtractor circuit." No — invert + add-one through the *same* adder (two's
  complement). The breadboard ALU proves it with XOR gates + carry-in.
- "A bus means everything connected can talk at once." No — exactly one driver per cycle; the rest
  must be Hi-Z or you get contention.
- "Tri-state's third state is a voltage between 0 and 1." No — it's high-impedance (disconnected),
  not an analog mid-level.
- "Two's complement is symmetric." No — `TMin = −2^{N−1}` has no positive counterpart; `−TMin`
  overflows back to `TMin`.
- "Floating point is just decimals in binary / is associative." No — finite precision, rounding,
  denormals, NaN/∞; `(a+b)+c ≠ a+(b+c)` in general.
- "%rbp is always the frame pointer." Modern x86-64 often omits it; frames are addressed off %rsp.
- "Cache speed is a hardware constant." No — *effective* bandwidth depends on access pattern
  (the memory mountain): same hardware, 10×+ swing from stride/working-set.
- "The 6502 ‘runs’ a program by itself." It passively fetches from whatever the address bus selects;
  without correct address decoding + ROM at the reset vector, nothing happens.

---

## 5. Best build-your-own target(s)

- **Eater 8-bit breadboard CPU (SAP-1)** — the keystone build for sub-course 01: clock → registers/
  bus → ALU → RAM/MAR → PC → control/microcode, ending in a programmable computer with NOP/LDA/ADD/
  SUB/STA/LDI/JMP/JC/JZ/OUT/HLT. Cheaper software alternatives if breadboarding is infeasible:
  Logisim Evolution recreation, or the XarkLabs VHDL port (https://github.com/XarkLabs/BenEaterVHDL)
  to run the same design on an FPGA/simulator.
- **Eater 6502 build** — graduate from a toy ISA to a *real* one: hardwire a 65C02, watch the bus
  with an Arduino, do address decoding, run hand-assembled machine code, drive an LCD via the 65C22.
- **CS:APP labs** (https://csapp.cs.cmu.edu/3e/labs.html), in pedagogical order for this course:
  - **Data Lab** — implement int/two's-complement/float ops with restricted bit operators (ch 2).
  - **Bomb Lab** — disassemble + GDB a binary to recover inputs (ch 3 machine-level + tools).
  - **Attack Lab** — buffer-overflow code injection + ROP on x86-64 (ch 3 stack discipline).
  - **Cache Lab** — write a cache simulator + cache-optimized matrix transpose (ch 6 locality).
  - (Optional bridge) **Architecture Lab** — Y86-64 processor design / CPE optimization, which
    connects Eater's hardware view to CS:APP's hardware view.

---

## 6. Open questions / where sources disagree

- **Exact control-word bit ordering & whether there's a "BO":** Eater's control page defers signal
  details to videos; the 16-signal list above is sourced from a community SAP-1 mirror, not the
  eater.net page text. Note Eater's B register is read-only to the ALU (no "B out" to bus). Treat the
  precise EEPROM bit map as **[UNVERIFIED]** against the primary page — confirm from the control
  videos / official schematics PDF before teaching exact bit positions.
- **T-state count:** "up to 5–6 microsteps, fetch=2" is consistent across community builds but the
  per-instruction microstep tables should be verified against Eater's microcode video, not assumed.
- **Eater 6502 memory map numbers** ($0000–$3FFF RAM / $4000–$7FFF I/O / $8000–$FFFF ROM) come from
  community write-ups echoing the series; confirm against the official eater.net/6502 schematics, as
  some builders alter decoding. **[Partly UNVERIFIED]**
- **74189 vs 74LS189 / 7489** RAM part: sources vary on exact part suffix; functionally a 16×4 SRAM.
- **CS:APP edition drift:** chapter numbers above follow **3e**; the F15 schedule is 3e-aligned, but
  some CMU offerings reorder lectures and lab due-dates change each term — cite the *book chapter*,
  not a specific semester's lecture number, as canonical.
- **Y86-64 vs x86-64:** CS:APP teaches the simplified Y86-64 for the *processor-design* chapter (4)
  but real x86-64 for machine-level programming (ch 3). Don't conflate; Eater's hardware is closest
  in spirit to Y86-64's sequential implementation.
- Did NOT independently fetch full text of eater.net/8bit/output and the per-video transcripts
  (control word, microcode) — flagged as the main primary-source gap. **[GAP]**
