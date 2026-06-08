# 01 — Research brief: nand2tetris + Petzold + But How Do It Know

Source cluster: the bottom-up build path from a single NAND gate → logic gates → adders/ALU → memory → CPU → machine language. Primary spine is Nisan & Schocken's *The Elements of Computing Systems* (nand2tetris), the free Project 1–5 book chapters (read in full, PDF text extracted, not summarized). Petzold's *Code* supplies the physical (relay/gate) layer and the latch/flip-flop construction nand2tetris abstracts away. Scott's *But How Do It Know?* supplies the bus-based CPU datapath model with an explicit stepper/control unit.

All page/figure references below are to the nand2tetris free chapter PDFs unless noted. Direct quotes and exact tables were transcribed from the extracted PDF text.

---

## 1. Key mechanisms (deep & precise, each with its forcing constraint)

### 1.1 NAND universality (functional completeness)
- **Claim (exact):** "any Boolean function can be constructed using only NAND gates." Justified constructively: NOT, AND, OR are all built from NAND, and {NOT, AND, OR} is already universal because any Boolean function has a canonical (DNF / sum-of-products) form expressed in those three ops. (Ch.1, §1.1)
- **Gate-level constructions from NAND (Ch.1, transcribed):**
  - **NOT(a)** = Nand(a,a) — tie both inputs together.
  - **AND(a,b)** = NOT(Nand(a,b)) — Nand then invert.
  - **OR(a,b)** = Nand(NOT a, NOT b) — De Morgan: a OR b = NOT(NOT a AND NOT b).
  - **XOR(a,b)** = (a AND NOT b) OR (NOT a AND b) — a multi-NAND network.
  - **Mux(a,b,sel)** = (a AND NOT sel) OR (b AND sel): selects a when sel=0, b when sel=1.
  - **DMux(in,sel)** routes `in` to one of two outputs {a,b} by sel.
- **Multi-bit / multi-way variants:** Not16, And16, Or16, Mux16 apply the 1-bit op bitwise across a 16-bit bus. Or8Way ORs 8 inputs. Mux4Way16 / Mux8Way16 cascade 2-way muxes; DMux4Way / DMux8Way likewise. Forcing constraint: hardware is built from one repeated cheap primitive; everything else is composition, so a fab only needs to perfect one gate.
- **Forcing constraint:** functional completeness means a single mass-produced primitive (NAND, or dually NOR) can realize *all* combinational logic — minimizes the physical gate vocabulary to one.

### 1.2 Boolean function representation
- n-input function ⇒ truth table with 2^n rows; the output column uniquely defines the function. Any such table is mechanically convertible to a canonical sum-of-products (DNF) over AND/OR/NOT, which is then convertible to NAND-only. This is the bridge from "spec as a table" to "circuit." (Ch.1, §1.1)

### 1.3 Two's complement (signed numbers)
- **Definition (Ch.2, §2.1):** in an n-bit system, the code of −x is `2^n − x` (for x≠0). Property giving the method its name: `x + (−x)` always sums to `2^n` (= 1 followed by n zeros), and the overflow MSB is discarded, leaving 0.
- **Negation shortcut (Ch.2, exact):** "flip all the bits of x and add 1 to the result." (Equivalent longhand: keep trailing 0s and the first 1, flip the rest.)
- **Range:** n bits encode 2^n values, max `2^(n-1) − 1`, min `−2^(n-1)` (asymmetric — one extra negative). Positive codes start with 0; negative codes start with 1; MSB carries negative weight `−2^(n-1)`.
- **The payoff (Ch.2):** "addition of any two signed numbers in 2's complement is exactly the same as addition of positive numbers." Subtraction is just `x − y = x + (−y)`. ⇒ one adder serves signed and unsigned; no special sign-handling hardware.
- **WHY (citation hop, Wikipedia *Two's complement*):** (a) single representation of zero — sign-magnitude and one's complement both have +0 and −0; (b) the *same* arithmetic circuit works for signed and unsigned, differing only in overflow detection; no end-around carry (which one's complement requires); (c) the known failure edge case: negating the most-negative value overflows (no positive counterpart). This is why IBM System/360 (1964) cemented it as the industry standard.

### 1.4 Half-adder, full-adder, ripple-carry adder
- **Half-adder (Ch.2, fig 2.2):** adds 2 bits → `sum = a XOR b`, `carry = a AND b`. (The chapter notes sum/carry are *identical* to the already-built Xor/And gates.)
- **Full-adder (Ch.2, fig 2.3):** adds 3 bits (a,b,c) → sum = LSB of a+b+c, carry = MSB. Built from **two half-adders + one OR gate** (or directly).
- **Add16 / n-bit adder (Ch.2, fig 2.4):** array of n full-adders, carry-out of bit i wired to carry-in of bit i+1 (LSB→MSB). "Overflow is neither detected nor handled."
- **Inc16:** an adder wired to add the constant 1.
- **Forcing constraint / tradeoff (Ch.2, §2.4 Perspective, exact):** the naive ripple-carry adder is "rather inefficient, due to the long delays incurred while the carry bit propagates from the least significant bit pair to the most significant bit pair." Fix named explicitly: **carry look-ahead** techniques. Because addition is the most prevalent op, any per-adder improvement gives global speedup. (This is the ripple-vs-carry-lookahead tradeoff the brief asked for; nand2tetris builds ripple, names lookahead as the optimization.)

### 1.5 The Hack ALU (the centerpiece combinational chip)
- **Interface (Ch.2, fig 2.5):** two 16-bit data inputs `x,y`; six control bits `zx,nx,zy,ny,f,no`; 16-bit `out`; two status outputs `zr` (out==0), `ng` (out<0).
- **Operation pipeline (exact pseudocode, Ch.2 fig 2.5):**
  1. `if zx then x=0` (zero x)
  2. `if nx then x=!x` (bitwise negate x)
  3. `if zy then y=0`
  4. `if ny then y=!y`
  5. `if f then out=x+y else out=x&y` (f=1 → 2's-comp add; f=0 → bitwise And)
  6. `if no then out=!out` (negate output)
  7. `zr = (out==0); ng = (out<0)`
- **The trick:** 6 control bits ⇒ 2^6=64 possible functions; **18 are documented as useful**. The full ALU truth table (Ch.2, fig 2.6), columns `zx nx zy ny f no → out`:

  | zx nx zy ny f no | out |
  |---|---|
  | 1 0 1 0 1 0 | 0 |
  | 1 1 1 1 1 1 | 1 |
  | 1 1 1 0 1 0 | -1 |
  | 0 0 1 1 0 0 | x |
  | 1 1 0 0 0 0 | y |
  | 0 0 1 1 0 1 | !x |
  | 1 1 0 0 0 1 | !y |
  | 0 0 1 1 1 1 | -x |
  | 1 1 0 0 1 1 | -y |
  | 0 1 1 1 1 1 | x+1 |
  | 1 1 0 1 1 1 | y+1 |
  | 0 0 1 1 1 0 | x-1 |
  | 1 1 0 0 1 0 | y-1 |
  | 0 0 0 0 1 0 | x+y |
  | 0 1 0 0 1 1 | x-y |
  | 0 0 0 1 1 1 | y-x |
  | 0 0 0 0 0 0 | x&y |
  | 0 1 0 1 0 1 | x\|y |

- **Worked example (Ch.2, transcribed):** compute `x-1`. zx=nx=0 (x untouched); zy=ny=1 ⇒ y becomes 0 then `!0 = 111…1` = the 2's-comp code of −1; f=1 ⇒ add ⇒ `x + (−1)`; no=0 ⇒ output unchanged ⇒ `x-1`.
- **Design method (Ch.2, exact):** list the desired ops, then *backward-reason* the binary pre/post-processing needed — yielding 6 orthogonal 1-bit controls. Forcing constraint: maximal function repertoire from minimal, cheap, composable logic.

### 1.6 The clock, the DFF, and sequential logic
- **Combinational vs sequential (Ch.3):** combinational chips (gates, adder, ALU) compute `out = f(in)` with no memory. To store/recall state you need **sequential** chips, all of which embed Data Flip-Flops (DFFs).
- **DFF (Ch.3, §3.2.1):** primitive in nand2tetris. Behavior `out(t) = in(t−1)` — outputs its input from the *previous* clock cycle. Clocked; treated as a built-in (not implemented in HDL).
- **Clock:** a master oscillator alternating 0–1 (tick–tock); one tick+tock = a **cycle** = one discrete time unit, broadcast simultaneously to every sequential chip.
- **1-bit register / Bit (Ch.3, fig 3.1):** DFF + a Mux on its input; the Mux's select bit becomes the **load** bit. `if load(t−1) then out(t)=in(t−1) else out(t)=out(t−1)`. The naive "feed DFF output to its own input" design is *invalid* because internal pins must have fan-in 1 and there's no way to choose between in-wire and out-wire — the Mux resolves this.
- **Register (16-bit):** array of 16 Bits sharing one load line. RAM: stack n registers + direct-access (address-decode) logic; built **recursively** (RAM8→RAM64→…→RAM16K). Read is combinational; write commits next cycle.
- **PC / counter (Ch.3, §3.2.4):** register + incrementer, with `reset`, `load`, `inc`. Priority: `if reset then 0 else if load then in else if inc then out+1 else out`. This is the program counter.
- **Why clocking synchronizes the machine (Ch.3, exact):** because signals for x and y arrive at the ALU at different times (distance/resistance/noise), the ALU briefly emits garbage. Since ALU output always feeds a sequential chip, we just make the **clock cycle slightly longer than the worst-case signal propagation across the chip**, guaranteeing inputs are valid by the next clock edge. Feedback loops are safe in sequential (but not combinational) chips precisely because the DFF's `t−1` delay breaks the self-dependence that would otherwise be a data race.

### 1.7 SR latch → D latch → edge-triggered flip-flop (Petzold + Wikipedia; abstracted away by nand2tetris)
- nand2tetris treats the DFF as primitive but notes (Ch.3 Perspective, exact): "one classic design is based on Nand gates alone," via a **master-slave** design — "a clocked flip-flop is obtained by cascading two simple flip-flops, the first being set when the clock ticks and the second when the clock tocks." This is the citation hop into Petzold/Wikipedia for the gate-level story.
- **SR latch (Petzold Ch.17; Wikipedia):** two **cross-coupled NOR gates** (output of each feeds an input of the other). Table: S=0,R=0 hold; S=1,R=0 set Q=1; S=0,R=1 reset Q=0; **S=1,R=1 forbidden** — both NOR outputs go 0, breaking the invariant `Q = NOT Q̄` (Q and Q̄ no longer complementary). (NAND version exists dually.)
- **Gated D latch:** add a Clock/enable gate and derive R = NOT S from a single Data line, so S and R can never both be 1 — eliminates the forbidden state. **Level-triggered / transparent:** while Clock=1 the output tracks Data continuously.
- **Edge-triggered D flip-flop (Petzold, exact):** "the Q output is set from the Data input only when the Clock input transitions from 0 to 1." **Master-slave** = two latches in series clocked oppositely: when clock rises, master locks and slave opens. WHY edge-triggering matters: it prevents the output from racing back through feedback into the input *within the same cycle* — required for synchronous sequential logic where next-state depends on current state.
- **Scaling (Petzold Ch.17):** 1 flip-flop = 1 bit of memory → registers → an 8-bit accumulating adder (adder + flip-flops) → RAM. Petzold's relevant chapters: **Ch.8 Relays and Gates, Ch.14 Adding with Logic Gates, Ch.17 Feedback and Flip-Flops, Ch.20 Automating Arithmetic.** The physical substrate Petzold starts from is the **relay** (electricity controlling electricity), which makes the gate idea physical before silicon.

### 1.8 Machine language — the Hack ISA (Ch.4)
- **16-bit machine, two instruction types** distinguished by the leading opcode bit:
- **A-instruction `@value`:** binary `0vvvvvvvvvvvvvvv` — loads a 15-bit constant into the **A register**. Three uses: enter a constant; set up a data-memory access (A → address of M); set up a jump target (A → instruction address).
- **C-instruction `dest=comp;jump`:** binary `111a cccc ccdd djjj`. Leading `1` = C-type; next two bits unused; then `a`+six `c` bits = **comp**, three `d` bits = **dest**, three `j` bits = **jump**.
- **comp field (Ch.4, fig 4.3):** the `a` bit selects whether the ALU's y-operand is **A (a=0)** or **M=Memory[A] (a=1)**; the six c-bits are exactly the ALU control bits. 28 documented computations: `0,1,-1,D,A/M,!D,!A/!M,-D,-A/-M,D+1,A+1/M+1,D-1,A-1/M-1,D+A/D+M,D-A/D-M,A-D/M-D,D&A/D&M,D|A/D|M`. (Note the deliberate isomorphism to ALU fig 2.6.)
- **dest field (Ch.4, fig 4.4):** 3 bits `d1 d2 d3` = store into {A, D, M} respectively; any subset: null, M, D, MD, A, AM, AD, AMD.
- **jump field (Ch.4, fig 4.5):** 3 bits keyed on the ALU output sign: `j1`(out<0) `j2`(out=0) `j3`(out>0) → null, JGT, JEQ, JGE, JLT, JNE, JLE, JMP. "Jump" means continue at the instruction addressed by **A**.
- **Why two registers, why two instructions (Ch.4/Ch.5):** 16-bit instruction can't hold both an opcode and a 15-bit address, so every memory or jump op is a pair: an A-instruction to set the address, then a C-instruction. Hack is described as a "½-address machine." A doubles as data/data-address/instruction-address register; M is the implicit `Memory[A]`.
- **Conflict rule:** a C-instruction that may jump (nonzero j-bits) should not also reference M, since both uses contend for A.
- **Symbols/assembler (Ch.4):** predefined R0–R15 (→ addr 0–15), SP/LCL/ARG/THIS/THAT (→ 0–4), SCREEN (16384/0x4000), KBD (24576/0x6000); `(LABEL)` pseudo-commands; variables auto-allocated from address 16. The assembler (Ch.6) resolves symbols → addresses.

### 1.9 CPU: fetch–decode–execute and von Neumann/Harvard (Ch.5)
- **Stored-program concept:** fixed hardware + a small fixed instruction repertoire; programs live in memory *as data*, so one machine runs infinitely many programs. (Roots: universal Turing machine 1936, von Neumann 1945.)
- **CPU = ALU + registers + control unit.** Hack CPU = ALU (project 2) + D register + A register + PC (project 3) + decode/route gates.
- **The three sub-tasks (Ch.5, §5.3.1):**
  - **Decode:** parse the 16-bit instruction into `i xx a cccccc ddd jjj`. i-bit picks A- vs C-instruction.
  - **Execute:** for a C-instruction, the `a`-bit chooses A-vs-M as ALU input, the 6 c-bits set the ALU function, the 3 d-bits enable loading of the result into {A,D,M} (writeM asserted for M), .
  - **Fetch (next-instruction logic):** PC holds the next address. Default = **PC++**. Jump logic: `if jump then PC=A else PC++`, where `jump` is computed from the j-bits AND the ALU's `zr/ng` outputs. `reset=1` ⇒ PC=0 (restart). PC output → instruction-memory address input → instruction → CPU instruction input, closing the loop.
- **Combinational vs clocked CPU outputs (Ch.5, exact):** `outM` and `writeM` are combinational (instantaneous); `addressM` and `pc` are clocked (commit next time step).
- **Memory map (Ch.5):** unified 32K data address space — `0x0000–0x3FFF` RAM16K, `0x4000–0x5FFF` Screen (8K, 256×512 b/w pixels, 1=black), `0x6000` Keyboard (1 word, scan-code or 0). **Memory-mapped I/O**: devices look like ordinary memory registers.
- **von Neumann vs Harvard (Ch.5 Perspective, exact and load-bearing):** Hack is a **Harvard** variant — *separate* instruction (ROM32K) and data memories. This lets fetch+execute happen in a **single clock cycle**. Classic single-address-space von Neumann machines must use **two-cycle** logic (fetch cycle loads instruction into an instruction register; execute cycle uses the data address) because one address port can't serve instruction-fetch and data-access simultaneously. **Price of Hack's simplicity: programs can't modify themselves / can't be loaded dynamically** (ROM). Also notes the CISC vs RISC performance debate, which Hack sidesteps.

### 1.10 Scott CPU datapath (But How Do It Know?) — the bus model nand2tetris lacks
- **Single shared system bus** (8-bit in book; 16-bit in djhworld's faithful sim): every component reads from and writes to the *same* bus; no dedicated point-to-point paths. Only one component may *drive* (enable onto) the bus per step.
- **Register = memory bits + an "enabler."** Each register has two control wires: **set** (latch the bus value in) and **enable** (drive its value out onto the bus). Moving a byte = enable source register + set destination register in the same step.
- **Named registers:** R0–R3 (general purpose), **IAR** (Instruction Address Register = program counter), **IR** (Instruction Register, holds current instruction), **MAR** (Memory Address Register), **ACC** (Accumulator, holds ALU result), **TMP** (temp for the ALU's second operand).
- **ALU + flags:** ADD, SHL/SHR, NOT, AND, OR, XOR, CMP; flag bits **carry, A-larger, equal, zero**. Flags drive conditional jumps (JMPIF/JC/JZ etc.).
- **Control unit = a STEPPER (ring counter)** producing steps 1..6/7, each step a single clock cycle. The control unit ANDs each stepper step with decoded instruction bits to assert the right enable/set wires, sequencing fetch→decode→execute as a fixed micro-program. Canonical **fetch** micro-steps: (step1) IAR→MAR and IAR→ALU+1; (step2) RAM[MAR]→IR; (step3) ACC(IAR+1)→IAR; then execute steps depend on the decoded IR.
- **Clock:** three derived signals — base **clk**, **clk-enable (clke)** (gates bus-output/enable timing), **clk-set (clks)** (gates latching/set timing); clke and clks are offset so a value is reliably on the bus *before* it's latched. The stepper advances on clk.
- **Instruction categories (book / djhworld):** ALU ops (ADD, SHL, SHR, NOT, AND, OR, XOR, CMP); **LOAD/STORE** (RAM↔register via MAR); **DATA** (load next word as immediate); **JMP / JMPIF (JR/JMP + conditionals)**; **CLF** (clear flags); **IN/OUT** (I/O). Known omissions (book's design, flagged by the implementer): **no subtract instruction, no stack pointer / stack, no interrupts.**

---

## 2. Foundational sources (one canonical source per claim)

nand2tetris free chapter PDFs (Nisan & Schocken, *The Elements of Computing Systems*; links 301-redirect from nand2tetris.org to filesusr.com host — both forms given):
- **Course / project index:** https://www.nand2tetris.org/course
- **Project pages:** https://www.nand2tetris.org/project01 … /project05
- **Ch.1 Boolean Logic (NAND universality, gate constructions):** https://www.nand2tetris.org/_files/ugd/44046b_f2c9e41f0b204a34ab78be0ae4953128.pdf
- **Ch.2 Boolean Arithmetic (two's complement, adders, ALU truth table):** https://www.nand2tetris.org/_files/ugd/44046b_f0eaab042ba042dcb58f3e08b46bb4d7.pdf
- **Ch.3 Sequential Logic (clock, DFF, register, RAM, PC, master-slave note):** https://www.nand2tetris.org/_files/ugd/44046b_862828b3a3464a809cda6f44d9ad2ec9.pdf
- **Ch.4 Machine Language (Hack ISA: A/C instructions, comp/dest/jump tables):** https://www.nand2tetris.org/_files/ugd/44046b_7ef1c00a714c46768f08c459a6cab45a.pdf
- **Ch.5 Computer Architecture (von Neumann/Harvard, CPU fetch-decode-execute, memory map):** https://www.nand2tetris.org/_files/ugd/44046b_b2cad2eea33847869b86c541683551a7.pdf

Petzold, *Code: The Hidden Language* (official companion site with interactive figures):
- **Ch.17 Feedback and Flip-Flops (oscillator, SR latch, level- vs edge-triggered, accumulating adder):** https://www.codehiddenlanguage.com/Chapter17/
- (Companion site root, all chapters incl. Ch.8 Relays/Gates, Ch.14 Adding with Logic Gates, Ch.20 Automating Arithmetic: https://www.codehiddenlanguage.com/ )
- Book overview: https://en.wikipedia.org/wiki/Code:_The_Hidden_Language_of_Computer_Hardware_and_Software

Scott, *But How Do It Know?* — faithful open-source implementation + write-up (book itself is not free online; these reproduce its architecture verbatim):
- **Reference implementation (registers, ALU, stepper, bus, ISA):** https://github.com/djhworld/simple-computer  (README: https://github.com/djhworld/simple-computer/blob/master/README.md )
- **Implementer's design write-up:** https://djharper.dev/post/2019/05/21/i-dont-know-how-cpus-work-so-i-simulated-one-in-code/

WHY citation hops (primary references encyclopedic but authoritative):
- **Two's complement rationale (single zero, unified add/sub, no end-around carry, MSB negative weight, System/360 1964):** https://en.wikipedia.org/wiki/Two%27s_complement
- **SR latch forbidden state, gated D latch, master-slave edge-triggering rationale:** https://en.wikipedia.org/wiki/Flip-flop_(electronics)

---

## 3. "Why it's this way" (the forcing constraints)

- **One primitive gate (NAND):** functional completeness lets a fab perfect a *single* cheap primitive and compose everything else. Dual choice NOR works identically. (Constraint: manufacturability/cost of physical gates.)
- **Two's complement:** chosen so signed add/subtract reuse the *unsigned* adder with no special hardware, and so zero is unique. The asymmetric range (one extra negative) and the "negate most-negative overflows" edge case are accepted prices. (Constraint: minimize arithmetic hardware.)
- **Ripple-carry adder built, carry-lookahead named:** ripple is the simplest correct design; its serial carry propagation delay is the bottleneck, so real machines spend transistors on lookahead. nand2tetris teaches the simple version and flags the optimization. (Constraint: gate-delay vs area/complexity.)
- **6-control-bit ALU:** designed by backward-reasoning from a desired op list to orthogonal 1-bit zero/negate/select pre- and post-processing knobs — maximal repertoire from minimal logic. Multiply/divide/float deliberately *omitted* from hardware and pushed to software/OS (Ch.12). (Constraint: hardware cost vs do-it-in-software performance.)
- **Clocked sequential logic:** the clock discretizes time so feedback loops don't become data races, and so the machine can wait out worst-case signal propagation before latching. Cycle length is set just above the longest cross-chip signal path. (Constraint: physical signal-propagation skew.)
- **Edge-triggered (master-slave) flip-flops:** prevent the output from feeding back into the input within one cycle; the gated-D structure removes the SR forbidden state. (Constraint: race-free synchronous state.)
- **Two registers + two-instruction ISA (Hack):** a 16-bit word can't hold both an opcode and a 15-bit address, forcing the @addr / op pairing and the dual-role A register. (Constraint: instruction-word width.)
- **Harvard split memory (Hack):** separate ROM/RAM allows single-cycle fetch-execute; price is no self-modifying/dynamically loaded code. Classic von Neumann's shared bus needs two cycles. (Constraint: one address port can't serve fetch and data access at once.)
- **Memory-mapped I/O:** makes every device look like memory so the CPU/ISA need no device-specific instructions; new devices = new memory region. (Constraint: keep CPU device-agnostic.)
- **CPU-resident registers:** RAM access is slow and needs wide address fields; a few local registers (2–32) give fast operands and thinner instructions, avoiding ALU "starvation." (Constraint: memory latency + instruction width.)

---

## 4. Common misconceptions to preempt

- **"NAND is special / magic."** NOR is equally universal; "universal" just means {it} can express all of {NOT,AND,OR}. The deep fact is functional completeness, not NAND itself.
- **"Two's complement is an arbitrary trick."** It's forced: it's the encoding under which the *unsigned* adder also computes signed results, with a single zero. The MSB isn't a "sign flag" — it's a digit with weight −2^(n-1).
- **"The ALU 'decides' what to do."** The ALU is purely combinational — it continuously computes on whatever is on its inputs and emits garbage until they settle. The *clock + registers* impose order; the *control bits* select the function.
- **"A flip-flop stores a bit by holding charge."** In the logic model it holds state via cross-coupled feedback (each gate sustaining the other). Real DRAM uses charge, but that's a separate physical optimization (Ch.3 notes modern memory isn't built from standard flip-flops).
- **"Level-triggered and edge-triggered are interchangeable."** A transparent latch passes input through while enabled; an edge-triggered flip-flop samples only at the clock transition — essential to avoid feedback races. nand2tetris' DFF is edge-behaved (`out(t)=in(t−1)`).
- **"Instructions and data are fundamentally different in memory."** Physically identical bit patterns; meaning comes only from whether the CPU fetches a word as an instruction or reads it as data (stored-program concept). (Hack happens to physically separate them — Harvard — but that's an implementation choice, not a logical necessity.)
- **"Fetch-decode-execute needs a microprocessor's worth of magic."** It's a fixed loop: PC→instruction memory→decode bits→route to ALU/registers→compute next PC. In Scott's model it's literally a ring-counter (stepper) asserting enable/set wires.
- **"Jump sets the PC to an address baked in the instruction."** In Hack, jumps go to whatever address is currently in **A**; the jump instruction itself carries no address — you must `@target` first.
- **"`D=D+M` does algebra."** `+` is not an operator here; the whole 3-char string `D+M` is one mnemonic selecting one fixed ALU operation (Ch.4 Perspective, explicit).

---

## 5. Best build-your-own target(s)

The canonical, sequenced, free, auto-graded build is **nand2tetris Projects 1–5** (hardware simulator + HDL; each chip ships a `.hdl` skeleton, `.tst` script, `.cmp` compare file):
- **Project 1 — Boolean Logic:** Not, And, Or, Xor, Mux, DMux, and 16-bit/multi-way variants, all from the built-in **Nand** primitive. (Teaches NAND universality + composition.)
- **Project 2 — Boolean Arithmetic:** HalfAdder, FullAdder, Add16, Inc16, and the **ALU** (the project-2 capstone). (Teaches two's complement + the 6-control-bit ALU.)
- **Project 3 — Memory:** Bit (DFF+Mux), Register, RAM8→RAM16K (recursive), PC. (DFF is given as primitive.) (Teaches clocking, state, recursive memory.)
- **Project 4 — Machine Language:** write `Mult.asm` (multiply via repeated add) and `Fill.asm` (keyboard→screen) in Hack assembly; run on the supplied **CPU emulator** + **assembler**. (Teaches the ISA before the CPU exists.)
- **Project 5 — Computer Architecture:** build the **CPU** (ALU+A+D+PC+decode), wire **Memory** (RAM16K+Screen+Keyboard) and **ROM32K**, assemble the top-level **Computer** chip; test by running Add.hack / Max.hack / Rect.hack. (Teaches fetch-decode-execute end to end.)

Tools: nand2tetris hardware simulator, CPU emulator, assembler (all in the `tools/` dir of the free software suite). Recommended scaffolding order is exactly 1→2→3→4→5; each project may use built-in versions of prior chips for speed/correctness.

Complementary build targets (for the layers nand2tetris abstracts):
- **Petzold's relay/gate path** (Code companion site, interactive): build SR latch → D latch → edge-triggered flip-flop → accumulating adder by hand to *see inside* the nand2tetris primitive DFF.
- **Scott CPU** (djhworld/simple-computer, Go) to internalize the **bus + enable/set + stepper** datapath, which nand2tetris's HDL hides behind direct wiring.

---

## 6. Open questions / where sources disagree

- **DFF / flip-flop as primitive vs built:** nand2tetris *intentionally* treats the DFF as an atomic primitive (Ch.3 Perspective: the master-slave NAND construction is "rather elaborate" and abstracted away). Petzold and Scott *do* build it from gates. Not a contradiction — a deliberate altitude choice — but a writer must flag that the "gates all the way down" promise has one pedagogically-skipped rung (the flip-flop's internal feedback) unless Petzold is used to fill it.
- **Harvard vs von Neumann labeling:** nand2tetris calls Hack a "von Neumann machine" in the chapter intro but then (Ch.5 §5.1.3 and Perspective) explicitly says its separate instruction/data memories make it **Harvard**, enabling single-cycle fetch-execute. The writer should present Hack as a *Harvard-style variant of the von Neumann family* to avoid confusion. Most real general-purpose CPUs are single-address-space (two-cycle) von Neumann.
- **Bus-based (Scott) vs direct-wired (Hack) datapath:** the two models teach the same concepts with different mental images. Scott's *single shared bus with enable/set per register* is closer to a textbook datapath and makes data movement explicit; Hack wires chips directly and has no general bus. A writer mixing them must be explicit about which model a given diagram follows.
- **Bus width:** Scott's book CPU is **8-bit**; the widely-cited djhworld implementation widened it to **16-bit**. State the book's 8-bit as canonical.
- **Petzold edition differences:** *Code* 2nd ed. (2022) reorganizes/expands chapters and adds the interactive companion site; chapter numbers cited here (8/14/17/20) match the companion site's current numbering but a writer using a 1st-ed. print copy may see different numbers.

### Gaps / verification notes
- **[PARTIAL] Scott CPU fine-grained micro-steps:** the exact per-step enable/set wiring and full stepper sequence come from the book + the faithful djhworld implementation; the free blog post confirms the architecture (single bus, 4 GP registers, fetch-decode-execute, missing stack/interrupts, 8→16-bit) but does not enumerate every micro-step. The fetch sequence and register set given in §1.10 are consistent across sources but the book itself (paywalled) is the only fully authoritative source for the precise step-by-step control signals — treat the per-step detail as **[VERIFY against the book or the GitHub source files]** if a writer needs exact wiring.
- **[PARTIAL] Petzold Ch.17 internals via WebFetch:** the companion page is interactive/JS-heavy; the SR-latch forbidden-state and edge-vs-level distinctions were corroborated against the Wikipedia *Flip-flop* article (cited). Exact Petzold wording/figures should be checked against the book or the live interactive page.
- **No gap on the nand2tetris spine:** Chapters 1–5 were read in full from the official free PDFs (text extracted with pdftotext); all ALU/ISA tables, the two's-complement rule, the clocking rationale, and the CPU fetch-decode-execute description are transcribed directly, not summarized.
