# Reconciled Research Brief — 05 Programming Language Runtime Internals

Cluster briefs reconciled:
- `_research_interpreters-compilers.md` — Crafting Interpreters + Thorsten Ball/Monkey style builds.
- `_research_production-runtimes.md` — CPython + V8/Node/libuv + JVM/HotSpot anchors.

Phase 1 artifact only. No chapters. Use cluster briefs for full detail and exact source tables.

---

## 1. Key mechanisms — consolidated spine

### Source text to tokens
A runtime starts with bytes/characters but the parser needs structured tokens. Scanners use a small state machine with current/start pointers (clox) or position/readPosition/ch (Monkey) to produce token type + lexeme. clox stores slices into the original source buffer to avoid allocation; jlox/Monkey copy strings because Java/Go ergonomics accept that cost. Constraint: tokens must preserve enough source location/lexeme info for parsing and diagnostics without forcing the parser to rescan raw input.

### Parsing and executable structure
Recursive descent maps grammar rules to functions and is easiest to teach; precedence is encoded by calling tighter-binding parse functions. Pratt parsing maps token types to prefix/infix parse functions plus precedence, making operator-heavy expression grammars compact and single-pass friendly. jlox/Monkey build ASTs for later interpretation/resolution; clox compiles directly to bytecode while parsing. The forcing tradeoff: ASTs enable multiple passes and cleaner static analysis; direct bytecode emission avoids memory and pointer-chasing but constrains language features like arbitrary forward references.

### Environments, scopes, closures
Lexical scoping requires lookup relative to declaration site, not call site. jlox uses linked `Environment` objects and a resolver pass that precomputes scope depth for each variable reference. Monkey uses an outer environment pointer. clox uses local slots on the VM stack until a local escapes; then closures capture `ObjUpvalue` objects. Open upvalues point to stack slots; closed upvalues copy the value to heap storage when the defining stack frame exits. Critical misconception: closures capture bindings/references, not simple value copies.

### Bytecode, stacks, frames, and dispatch
Tree-walk interpretation is simple but slow: heap-scattered AST nodes and virtual/interface dispatch lose locality. Bytecode turns execution into a tight loop over compact instructions. clox chunks contain bytecode, line info, and constants; the VM keeps a value stack and CallFrames with instruction pointer + slot window. CPython bytecode uses 16-bit code units (opcode + oparg), EXTENDED_ARG for larger operands, inline cache entries adjacent to instructions, and `_PyInterpreterFrame` as `[Specials | Locals | Stack]` on a per-thread frame stack. V8 Ignition is register-based (accumulator + explicit registers), not stack-based. JVM bytecode is stack-machine oriented but HotSpot quickly tiers to compiled code.

### Values and object layout
Dynamic languages need runtime type tags. clox starts with tagged unions and optionally uses NaN boxing to pack numbers, booleans, nil, and object pointers into 64 bits. All heap objects embed an `Obj` header with type + mark bit + next pointer. CPython embeds `PyObject_HEAD` (refcount + type pointer) first in every object; variable-size objects add `ob_size`. V8 uses object Maps (hidden classes) to describe property layout and transitions. JVM class metadata, constant pools, and verifier data support statically typed bytecode with runtime loading.

### Garbage collection and memory management
clox implements stop-the-world tri-color mark-sweep: mark roots, trace gray objects, sweep unmarked objects from an intrusive linked list. CPython primarily uses refcounting for deterministic acyclic cleanup plus a generational cyclic collector for container cycles; immortal objects reduce refcount churn for global/static objects. V8 uses generational GC: young-generation scavenging (semi-space copying) plus old-generation collection. HotSpot's G1 divides heap into regions with young STW collections and concurrent old marking. Constraint: every GC design trades pause time, throughput, memory overhead, implementation complexity, and pointer-update barriers.

### Inline caches, hidden classes, and JIT tiers
Production runtimes specialize repeated operations. CPython 3.11+ uses PEP 659 adaptive bytecode: generic opcodes count executions, inspect stable runtime types, and rewrite live bytecode to specialized variants. V8 records feedback per function/callsite, uses Maps/hidden classes to turn property lookup into offset loads, and tiers from Ignition to Maglev to TurboFan. HotSpot tiers from interpreter through C1 profiling to C2 optimized code. The first-principles forcing constraint: dynamic semantics are too flexible to optimize statically, so runtimes collect runtime facts and speculate — then deoptimize when facts change.

### Event loops and async runtime substrate
Node's JavaScript async model sits on libuv, whose loop runs timers, pending callbacks, idle/prepare, poll, check, and close callbacks. Network I/O is truly readiness/event driven via OS APIs; many file-system operations are simulated async through a libuv thread pool because portable async file I/O is not universal. Constraint: the language promise (“callback later”) is not the same as the OS mechanism; runtimes hide a mix of kernel readiness, timers, microtasks, and worker threads.

### Class loading, verification, safepoints
JVM loads classes lazily, parses class files, resolves constant-pool references, verifies StackMapTable/type safety, and initializes only when needed. HotSpot safepoints are cooperative: threads poll at backedges/returns; VM operations wait until all threads reach a safe state. Polling pages make the fast path cheap: normally readable; when a safepoint is needed, making the page faulting traps threads into the VM. Constraint: optimized code and moving/compacting collectors require points where the VM can precisely know stack/object state.

---

## 2. Foundational sources — canonical anchors

- Crafting Interpreters source/book: `github.com/munificent/craftinginterpreters` (`book/`, `c/`, `java/`). `craftinginterpreters.com` was blocked; GitHub raw files were used.
- Pratt parser explanation: Nystrom blog `journal.stuffwithstuff.com/2011/03/19/pratt-parsers-expression-parsing-made-easy/`; Pratt 1973 remains `[UNVERIFIED]` if citing original paper text.
- Monkey/Ball: Ball's exact book code is paywalled; community ports (`github.com/zanshin/interpreter`, `github.com/ELD/monkey-lang-go`) were used to verify architecture, with Ball attribution treated carefully.
- CPython primary sources: `github.com/python/cpython` — `Include/object.h`, `InternalDocs/interpreter.md`, `InternalDocs/frames.md`, `Python/generated_cases.c.h`, `Python/ceval_gil.c`, `Python/gc.c`, `Include/internal/pycore_gc.h`.
- V8/libuv: `github.com/v8/v8` (`map.h`, `feedback-vector.h`, `interpreter.h`, `maglev-compiler.h`, `scavenger.h`, `heap.h`); `github.com/libuv/libuv` (`docs/src/design.rst`, `src/unix/core.c`, `include/uv.h`).
- HotSpot/OpenJDK: `github.com/openjdk/jdk` — compiler levels, safepoints, class parser/verifier, G1 heap.

---

## 3. Why it's this way — constraints/tradeoffs

- **AST vs bytecode:** ASTs maximize clarity and multi-pass analysis; bytecode maximizes locality and dispatch speed.
- **Recursive descent vs Pratt:** recursive descent is readable and maps grammar to code; Pratt keeps expression parsing compact and table-driven.
- **Stack VM vs register VM:** stack VMs simplify compilers; register VMs reduce instruction count but need register allocation/operand encoding.
- **Refcount vs tracing GC:** refcount gives deterministic cleanup but misses cycles and costs per pointer update; tracing collects cycles but causes pauses/barriers.
- **GIL:** CPython's refcounting and C extension ecosystem made one global lock simpler than per-object locks; cost is CPU-bound thread serialization.
- **Inline caches:** dynamic dispatch is too expensive if every lookup starts from scratch; cache stable type/shape facts at the callsite and invalidate/deopt when they change.
- **Hidden classes/Maps:** JS objects are semantically dictionaries, but most code constructs objects with stable field order; Maps exploit that shape regularity.
- **Tiered JIT:** fast startup and peak optimization conflict; interpreters start immediately, baseline/mid-tier compilers warm up quickly, optimizing tiers spend more time on hot code.
- **Safepoints:** GC/deopt/thread operations need precise stack maps; polling makes normal execution cheap while preserving stop-the-world coordination.
- **libuv thread pool:** portable async file I/O is inconsistent; using worker threads preserves API semantics while accepting bounded pool contention.

---

## 4. Common misconceptions to preempt

- Lexing and scanning are separate phases — in these sources they are the same practical pass.
- The AST is always built — clox and production VMs can compile directly to bytecode or IR.
- Closures copy values — they capture environments/upvalues/free-variable cells, usually by reference.
- Bytecode means “slow forever” — production runtimes use bytecode as profiling substrate for specialization/JIT.
- CPython has no optimization/JIT story — 3.11+ has adaptive specialization; Tier 2 JIT is experimental.
- The GIL means Python is single-threaded — I/O and C extensions can release it; CPU-bound Python bytecode is serialized.
- Ignition is stack-based — V8 Ignition is register/accumulator-based.
- JavaScript file I/O is async to the kernel — libuv often uses a worker thread pool for FS calls.
- JVM safepoints stop threads instantly — threads must reach polls; long native/no-poll code can delay safepoints.
- GC always runs in the background — clox is synchronous STW; many runtimes mix STW and concurrent phases.

---

## 5. Best build-your-own targets

Core ladder:
1. **Tree-walk interpreter** (jlox/Monkey style): scanner → recursive descent parser → AST → environment chain → closures.
2. **Bytecode VM** (clox/Monkey compiler style): Pratt parser → bytecode chunk/constants → stack VM → CallFrame → closures/upvalues.
3. **Mark-sweep GC**: roots, gray stack, mark children, sweep intrusive object list; then compare against CPython refcount + cycle detection.
4. **Inline cache extension**: add object shapes/hidden-class-like Maps and monomorphic property load cache to a toy VM.
5. **Toy event loop**: epoll/select/kqueue poll phase + timer heap + microtask/nextTick queue + worker-pool simulation.
6. **Class-file reader**: parse JVM constant pool, methods, Code, StackMapTable; print bytecode and verifier-relevant metadata.

Stretch:
- add NaN boxing to clox and benchmark vs tagged union.
- implement a two-generation GC with semi-space young gen + old mark-sweep + write barrier.
- add a tiny JIT stub or copy-and-patch hot opcode path after the VM is correct.

---

## 6. Open questions / gaps

- Ball's original code/books are paywalled; community ports verify architecture but exact Ball phrasing/stage order should not be quoted without book access.
- Pratt 1973, Gudeman 1993 NaN-boxing source, and The Garbage Collection Handbook are paywalled/secondary in this pass; treat exact historical attributions as `[UNVERIFIED]` until direct access.
- Unicode/string semantics are thin in CI/Ball; production runtimes need grapheme/codepoint/encoding design beyond this sub-course or in appendices.
- Register VM vs stack VM deserves a Lua/academic source if Phase 2 chooses to go deeper.
- CPython Tier 2 JIT and free-threaded PEP 703 behavior are moving targets; benchmark/adoption claims need current primary data.
- V8 Maglev/TurboFan thresholds are runtime-flag/version dependent; do not teach fixed thresholds.
- ZGC/Shenandoah, V8 Turboshaft/Wasm, JVM invokedynamic, and CPython asyncio are important but likely appendix-level unless this course expands.
