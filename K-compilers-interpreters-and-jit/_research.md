# Appendix K · compilers-interpreters-and-jit — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). K is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for "how does source text
> become fast machine code" — the front-end → middle-end → back-end → JIT/deopt pipeline that spine
> **05** (language runtime internals) teaches transferably and that appendices **C** (CPython), **D**
> (V8/Node) and **E** (JVM/HotSpot) instantiate as concrete production tiers. Spine 05 cross-links
> DOWN into K for the full pipeline mechanism. **Bespoke structure: the journey of a translation unit
> through the three stages of a compiler + the speculation cycle** — NOT four clusters, NOT a build
> progression, NOT a capstone canvas. Math: `_recompute.py` (15/15). Factcheck: `_factcheck_phase1.md`
> (0 blockers). Network: llvm.org / gcc.gnu.org / docs.python.org HTTP **000** this wave → constants
> reused from 05's line-verified CPython / V8 / HotSpot / Crafting-Interpreters source reads; nothing
> new hardened.

## 1. Thesis
A compiler/JIT is a **stack of lowerings**, each trading a higher-level, easier-to-analyze
representation for a lower-level, faster-to-execute one. Every design choice traces to ONE forcing
tension: **the representation that is easiest to reason about (source text, AST, SSA) is the slowest
to run, and the representation that runs fastest (machine code) is the hardest to analyze or change.**
So a translation pipeline (a) parses text into a tree it can check, (b) lowers to an IR flat enough to
optimize, (c) lowers again to machine code with finite registers — and a JIT adds a fourth move: defer
the expensive lowerings until profiling proves a piece of code is *hot*, then **speculate** on the
runtime facts it observed, guarding so it can **deoptimize** when those facts change.

## 2. The journey of a translation unit (the bespoke spine)

### Stage 0 — Two strategies, one spectrum (interpret ↔ compile; 05)
- **Tree-walk interpreter** (jlox/Monkey): scan → recursive-descent/Pratt parse → AST → walk the AST
  recursively. Simple, but every node is a heap pointer-chase with virtual dispatch.
- **Bytecode VM** (clox/CPython): compile AST (or parse directly) to a compact bytecode array, then
  run a tight dispatch loop. RECOMPUTED: 1000 ops scattered as AST ≈ 1000 cache misses vs a
  contiguous bytecode array ≈ 32 misses (32 × 16-bit instrs per 64 B line) → WHY production runtimes
  compile to bytecode.
- **AOT compiler** (gcc/clang/LLVM): lower all the way to machine code *before* running. Pays the full
  compile cost once, offline; cannot see runtime types.
- **JIT**: bytecode first, then compile *hot* code at runtime — gets startup of an interpreter AND the
  peak of a compiler, at the cost of speculation + deopt machinery. These are points on one spectrum,
  not separate worlds.

### Stage 1 — Front-end: text → AST (05 §1)
- **Lexer/scanner**: a small state machine producing `(type, lexeme, location)` tokens; clox stores
  slices into the source buffer (zero-copy), jlox/Monkey copy strings. Lexing and scanning are the
  same pass in practice (misconception preempted).
- **Parser**: recursive descent maps grammar rules → functions (readable, multi-pass friendly); **Pratt
  / top-down operator-precedence** maps token types → prefix/infix functions + binding power (compact
  for operator-heavy expression grammars, single-pass). Output = an **AST** (for analysis/multiple
  passes) OR direct bytecode emission (clox, no AST — saves memory, constrains forward references).
- Forcing function: the parser must preserve enough structure + source location for static analysis
  and diagnostics without rescanning raw text.

### Stage 2 — VM shape: stack vs register (05 §1, §3)
- **Stack VM** (clox, JVM bytecode): operands implicit on a value stack; compiler is trivial. `a*b+c*d`
  → `PUSH a, PUSH b, MUL, PUSH c, PUSH d, MUL, ADD` = RECOMPUTED **7 instructions**.
- **Register VM** (V8 Ignition: accumulator + explicit registers; Lua): 3-address ops over virtual
  registers → same expression = RECOMPUTED **3 instructions**. Fewer, wider instructions ⇒ fewer
  dispatch cycles (the dominant interpreter cost) — at the price of register allocation + operand
  encoding. This is WHY Ignition is register-based, not stack-based (misconception preempted).
- **Operand encoding**: CPython's 16-bit code unit = 8-bit opcode + 8-bit oparg; operands >255 need
  `EXTENDED_ARG` prefixes. RECOMPUTED: arg 255 → 1 code unit; arg 256 → 2 units. Compact bytecode
  bounds operand size by design.

### Stage 3 — Middle-end: optimize on SSA IR (05 §1)
- The bytecode/AST is lowered to a typed **IR in SSA form** (Static Single Assignment): each variable
  is assigned exactly once; control-flow merges insert **phi** nodes. SSA makes def-use chains explicit
  → cheap dataflow analysis.
- Canonical passes (recomputed where numeric):
  - **Constant folding**: `3*4+2` → `14` at compile time → RECOMPUTED 2 runtime ops → 0.
  - **Strength reduction**: `x*8` → `x<<3` → RECOMPUTED cheaper op, identical result.
  - **Inlining** a hot tiny callee called 1e6× → RECOMPUTED removes ~5e6 cycles of call/return/frame
    overhead AND exposes the body to folding in the caller's context — budgeted to avoid code bloat.
  - (plus dead-code elimination, common-subexpression elimination, loop-invariant code motion — same
    SSA machinery.)

### Stage 4 — Back-end: IR → machine code (05 §3, 06)
- **Instruction selection**: tile the IR with target instructions (e.g. multiply-add fusion).
- **Register allocation = graph coloring** (Chaitin-style): build an interference graph of
  simultaneously-live values; k-color it with k physical registers; any node that can't get a color is
  **spilled** to the stack. RECOMPUTED: 20 live values > 16 registers ⇒ ≥4 spills; 10 live ⇒ 0 spills.
  Register *pressure* — not instruction count — drives memory traffic. (Chaitin paper attribution
  `[UNVERIFIED]`; mechanism recomputed.)
- **Instruction scheduling**: reorder to hide latency / fill pipeline slots (ties back to appendix A's
  pipeline + hazards).

### Stage 5 — The JIT speculation cycle: profile → specialize → guard → deopt (05 §1)
- **Tiering** exists because fast startup and peak throughput conflict. RECOMPUTED **break-even**:
  compiling pays when N > compile_cost/(interp−compiled); with the illustrative units N* = 500
  executions. Below it, interpret; above it, compile. This is WHY hot-loop counters, OSR
  (on-stack-replacement) thresholds, and tier ladders (Ignition→Maglev→TurboFan; interp→C1→C2) exist —
  cold code must *not* be compiled (RECOMPUTED: at N=5 the compile path costs 90× the interpret path).
- **Inline caches + hidden classes** (V8 **Maps**, CPython **PEP 659** adaptive specialization): record
  the runtime types/shapes seen at a call site, then rewrite the generic op into a specialized one.
  RECOMPUTED: a monomorphic IC turns property lookup into 1 shape-compare + 1 fixed-offset load (O(1),
  independent of #fields) vs ~1.5 dict probes; polymorphic ICs degrade with #shapes; >~4 shapes →
  **megamorphic** generic dict path. WHY stable object shape matters.
- **Speculation + deoptimization**: the JIT speculates ("x is always a small int"), inserts a **guard**,
  and on guard failure **deopts** — bails to the interpreter, reconstructing live state. RECOMPUTED:
  speculation pays iff guards rarely fail (p=0.001 → 0.15× interpreted cost) and is a net loss when
  they fail often (p=0.5 → 25× cost). WHY type-unstable code stays interpreted / gets permanently
  deoptimized. This is the dynamic-language analogue of the AOT compiler's static type guarantees.
- **Copy-and-patch / template JITs** (CPython 3.13 experimental; clox stretch): a cheap codegen scheme
  — stitch pre-compiled machine-code templates per opcode — between a pure interpreter and a full
  optimizing JIT. Structural description only (moving target).

## 3. The "one tension, many lowerings" reconciliation (appendix payload)
| stage | representation | what it buys | what it costs | anchor |
|---|---|---|---|---|
| parse | tokens → AST | structure + static checks | memory + a pass | 05 |
| VM shape | stack vs register bytecode | locality + tight dispatch | reg alloc / encoding | 05 |
| optimize | SSA IR | cheap dataflow → fold/inline | build + pass time | 05/06 |
| codegen | machine code | raw speed | finite regs → spills | 05/06 |
| JIT | tiered + speculative | startup AND peak | guards + deopt machinery | 05 |

## 4. Common misconceptions to preempt
- "Lexing and scanning are separate phases." In these sources they're one pass.
- "There's always an AST." clox and direct-emission compilers skip it.
- "Bytecode is slow forever." It's the *profiling substrate* for specialization/JIT.
- "A JIT is always faster than an interpreter." Only above the break-even N*; cold code is cheaper
  interpreted, and frequent deopt makes speculation a net loss.
- "Ignition is stack-based." It's register/accumulator-based.
- "Optimization happens on the AST." Real middle-ends optimize on a flat **SSA IR**, not the tree.
- "Register allocation just assigns names." It's NP-hard graph coloring; when colors run out it
  *spills* to memory.
- "Hidden classes/inline caches are permanent." They deopt the moment object shape / value type
  changes — speculation is revocable.
- "AOT and JIT are opposites." Same lowerings; the only difference is *when* (and therefore what type
  information is available).

## 5. Provenance summary
- **REUSED (line-verified in 05):** lexer/parser strategies, stack-vs-register VM, CPython 16-bit code
  unit + EXTENDED_ARG + inline caches, V8 Ignition/Maglev/TurboFan + Maps + PEP 659, HotSpot tiers,
  SSA-based middle-end, deopt-on-fact-change, copy-and-patch experimental JIT. (05 cited the CPython /
  V8 / libuv / OpenJDK / Crafting-Interpreters source trees directly.)
- **REUSED:** 06 (data-structure / cache costs), N (math).
- **RECOMPUTED:** `_recompute.py` (15/15) — stack-vs-register instr count, AST-vs-bytecode misses, JIT
  break-even N*, IC vs dict lookup, constant-fold / strength-reduce / inline savings, graph-coloring
  spills, deopt expected-cost, EXTENDED_ARG encoding.
- **`[UNVERIFIED]` carry-forward (not load-bearing):** LLVM/GCC primary text (IR ref, pass pipeline,
  SelectionDAG/GlobalISel, GIMPLE/RTL — hosts 000); Chaitin 1982 (graph coloring) + Cytron 1991 (SSA)
  + Pratt 1973 original-paper attributions; exact JIT hotness thresholds (version/flag-dependent);
  copy-and-patch / Tier-2 specifics (moving target). All blocked behind llvm.org/gcc.gnu.org (000) /
  ACM; logged, none hardened.

---
**Appendix K reconciled.** Reference-grade, exercise-free, 15/15 recomputed, all mechanisms reused
from 05's line-verified source reads. No chapters yet.
