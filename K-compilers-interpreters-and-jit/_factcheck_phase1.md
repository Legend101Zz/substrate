# Appendix K · compilers-interpreters-and-jit — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). This pass verifies the
> load-bearing claims of K against **line-verified spine canon** (primarily 05, which cited the
> CPython / V8 / HotSpot / Crafting Interpreters source trees directly) plus 06 (data-structure
> costs) and N (math). **NO new primary fetched this wave** — llvm.org / gcc.gnu.org / docs.python.org
> all HTTP **000** (re-checked Wave 18). Every quantitative claim is re-derived in `_recompute.py`
> (15/15). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | Front-end = lex → parse (recursive-descent / Pratt) → AST or direct bytecode | VERIFIED (reuse) | 05 `_research.md` §1 (clox/jlox/Monkey, line-cited) |
| 2 | Stack VM emits more, narrower instructions than a register VM (a*b+c*d: 7 vs 3) | RECOMPUTED | `_recompute.py` #1; 05 (clox stack VM vs V8 Ignition register/accumulator) |
| 3 | V8 Ignition is **register/accumulator-based**, not stack-based | VERIFIED (reuse) | 05 §1 "V8 Ignition is register-based (accumulator + explicit registers)" |
| 4 | AST tree-walk loses locality vs a contiguous bytecode array; bytecode → far fewer cache misses | RECOMPUTED | `_recompute.py` #2; 05 §1 "Bytecode turns execution into a tight loop … AST nodes … lose locality" |
| 5 | CPython bytecode = 16-bit code unit (8-bit opcode + 8-bit oparg) + EXTENDED_ARG + inline caches | VERIFIED (reuse) | 05 §1 (CPython `generated_cases.c.h`, `pycore_*` cited) |
| 6 | Operand ≤255 fits one code unit; bigger needs EXTENDED_ARG prefixes | RECOMPUTED | `_recompute.py` #9 |
| 7 | Middle-end optimizes on **SSA** IR (single assignment, phi at merges); folding/strength-reduction/inlining | VERIFIED (reuse) + RECOMPUTED | 05 §1 (V8 TurboFan / HotSpot C2 IR); `_recompute.py` #5,#6 |
| 8 | JIT tiering has a **break-even** N* = compile_cost/(interp−compiled); cold code must NOT compile | RECOMPUTED | `_recompute.py` #3; 05 §1 "fast startup and peak optimization conflict … interpreters start immediately" |
| 9 | Tier ladder: interpreter → baseline → optimizing (V8 Ignition→Maglev→TurboFan; HotSpot interp→C1→C2) | VERIFIED (reuse) | 05 §1 (V8 + HotSpot tier names, line-cited) |
| 10 | Inline caches + hidden classes (V8 Maps / CPython PEP 659) turn lookup into O(1) offset load | VERIFIED (reuse) + RECOMPUTED | 05 §1; `_recompute.py` #4 |
| 11 | Polymorphic IC degrades with #shapes; megamorphic → generic dict path | RECOMPUTED | `_recompute.py` #4; 05 (Maps/feedback-vector) |
| 12 | Back-end: instruction selection + **register allocation = graph coloring**; spills when live-set > #regs | RECOMPUTED | `_recompute.py` #7; 05 §3 "register VMs … need register allocation" (Chaitin coloring is the canonical mechanism — *technique* `[UNVERIFIED]` to original paper) |
| 13 | **Deoptimization**: speculate on profiled types, guard, bail to interpreter on surprise; pays iff guards rarely fail | VERIFIED (reuse) + RECOMPUTED | 05 §1 "speculate — then deoptimize when facts change"; `_recompute.py` #8 |
| 14 | Optional **copy-and-patch / template JIT** as a cheap codegen path (CPython 3.13 experimental, clox stretch) | VERIFIED (reuse) | 05 §5 stretch + §6 "CPython Tier 2 JIT … experimental" |
| 15 | AOT (gcc/clang/LLVM) vs JIT split: AOT pays compile cost once offline; JIT pays it at runtime but sees runtime types | VERIFIED (reuse) | 05 §1/§3 startup-vs-peak tradeoff; LLVM/GCC primary text `[UNVERIFIED]` (hosts 000) |

## `[UNVERIFIED]` carry-forward (none load-bearing — all recomputed or reused from 05's line-cited source reads)
- **LLVM / GCC primary text** (IR reference, pass pipeline, SelectionDAG/GlobalISel, GCC GIMPLE/RTL) —
  llvm.org + gcc.gnu.org HTTP **000** this wave. Tier/IR *concepts* are reused from 05's line-verified
  V8/HotSpot reads; LLVM/GCC-specific naming is illustrative until a fetch heals.
- **Chaitin (1982) graph-coloring register allocation** + **Cytron et al. (1991) SSA construction** —
  original-paper attributions; the *mechanisms* are recomputed/reused, the historical citations are
  `[UNVERIFIED]` (ACM blocked / not fetched).
- **Pratt (1973)** top-down operator-precedence paper — carried from 05 (Nystrom blog used; original
  paper `[UNVERIFIED]`).
- **Exact JIT thresholds** (V8 Maglev/TurboFan hotness counters, HotSpot `-XX:CompileThreshold`,
  CPython adaptive-specialization warmup) are version/flag-dependent — taught as a *mechanism with a
  break-even*, never as fixed numbers (matches 05 §6 caveat).
- **Copy-and-patch / CPython Tier-2 JIT** specifics are a moving target (05 §6) — described
  structurally only.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 15/15);
all mechanisms reused from 05's line-verified source reads.
