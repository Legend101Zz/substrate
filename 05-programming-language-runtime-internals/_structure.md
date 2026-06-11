# 05 — Programming Language Runtime Internals · _structure.md

**Identity:** what actually happens between source text and a running program — generically,
across interpreters and production VMs. The bridge from "I write code" to "I understand the
machine that runs my code."

**Bespoke shape — "the pipeline, then the speculation."** Two movements. **Part A — the
pipeline (build it):** a strict constructive ascent from characters to a running bytecode VM
with GC, taught the way you'd actually build it (clox/Monkey as the reference you re-derive).
**Part B — making it fast (understand it):** the production reality that Part A's clean VM is
too slow for — inline caches, hidden classes, tiered JIT, deopt — driven by ONE forcing
constraint: *dynamic semantics are too flexible to optimize statically, so runtimes collect
runtime facts and speculate, then deoptimize when facts change.* Closes with the async
substrate (event loop) that the language hides. This is the generic spine; appendices C/D/E
are its three concrete instances.

## Dependency position
- **Depends on:** 01 (ISA/bytecode/registers), 04 (processes/threads/mmap/signals; the
  event loop sits on epoll from 04/03).
- **Feeds into:** 07 (query planners/executors are interpreters), 22/24 (the agent loop and
  context engineering reuse "eval loop"/"frame"/"budget" intuitions), 06 (object layout).
- **Appendix links DOWN (this is the big one):** K-compilers (the generic pipeline goes
  deeper), then the three concrete runtimes — C-python (GIL+refcount+adaptive-spec),
  D-javascript/V8 (hidden-classes+Ignition→Maglev→TurboFan+libuv), E-java/JVM
  (classloading+verifier+C1/C2+G1/ZGC+safepoints). 05 teaches the concept; C/D/E instantiate.

## Chapter specs (3–5 lines each)
### Part A — the pipeline you build
1. **Source → tokens** — scanning as a small state machine; token type + lexeme +
   location; clox slices the source buffer (zero-alloc) vs jlox/Monkey copy. Lexing and
   scanning are the same pass here.
2. **Tokens → structure: parsing** — recursive descent (grammar→functions, precedence by
   call depth) and Pratt parsing (token→prefix/infix + precedence) for expression-heavy
   grammars. AST (multi-pass, analysis-friendly) vs direct-to-bytecode (locality) tradeoff.
3. **Scopes, environments, closures** — lexical scope = lookup by declaration site. jlox
   resolver precomputes depth; clox uses stack slots + `ObjUpvalue` (open=points to stack,
   closed=copied to heap on frame exit). Closures capture bindings/cells, NOT value copies.
4. **Bytecode, stacks, frames, dispatch** — why tree-walking is slow (scattered nodes,
   virtual dispatch) ⇒ a tight loop over compact instructions. Chunks (code+lines+constants),
   value stack, CallFrames (ip + slot window). Stack-VM (clox/JVM) vs register-VM (V8
   Ignition: accumulator + registers). CPython 16-bit code units + EXTENDED_ARG + inline caches.
5. **Values & object layout** — runtime type tags: tagged unions, NaN boxing (pack
   num/bool/nil/ptr in 64 bits). The object header pattern: clox `Obj`, CPython
   `PyObject_HEAD` (refcount+type), V8 Maps/hidden classes describing layout + transitions.
6. **Garbage collection** — clox tri-color mark-sweep (roots→gray→sweep intrusive list);
   then CPython refcount + generational cycle collector + immortal objects; V8 generational
   scavenge + old-gen; HotSpot G1 regions. The universal tradeoff: pause vs throughput vs
   memory vs complexity vs barriers.

### Part B — making it fast (and the hidden substrate)
7. **Inline caches, hidden classes, JIT tiers** — the speculation thesis. CPython PEP 659
   adaptive bytecode (count→specialize→deopt); V8 feedback + Maps + Ignition→Maglev→
   TurboFan; HotSpot interpreter→C1→C2. Speculate on stable runtime facts; deoptimize when
   they change. Don't teach fixed thresholds (version/flag dependent).
8. **The async substrate: event loops** — the language says "callback later"; the OS says
   "readiness." libuv loop phases (timers→pending→poll→check→close) + microtasks/nextTick;
   network I/O is true readiness, many FS ops are faked async via a worker thread pool.
   Bridges to 17 (event-driven architecture) and the agent loop.
9. **Loading & safety (bridge to E)** — lazy class loading, constant-pool resolution,
   verification (StackMapTable = a security boundary), cooperative safepoints (poll at
   backedges/returns; polling page trap) that moving GCs/deopt require. Light here; deep in E.

## Paired build lab (/build → own-interpreter, own-vm, own-gc)
Core ladder: **tree-walk interpreter** (scanner→RD parser→AST→env chain→closures) →
**bytecode VM** (Pratt→chunks→stack VM→CallFrames→upvalues) → **mark-sweep GC** (roots/gray
stack/sweep) then compare to refcount+cycles → **inline-cache extension** (shapes/Maps +
monomorphic property cache) → **toy event loop** (epoll poll phase + timer heap + microtask
queue + worker-pool sim) → **class-file reader** (constant pool, Code, StackMapTable).
Stretch: NaN boxing benchmark; two-gen GC with write barrier; copy-and-patch hot-opcode JIT.

## Diagrams needed
- The pipeline: source→tokens→AST/bytecode→VM loop→GC (the spine picture).
- Recursive-descent call tree vs Pratt precedence table; AST vs bytecode for one expression.
- Closure capture: open vs closed upvalue (stack vs heap).
- Value stack + CallFrame slot window during a call; tagged union vs NaN-boxed 64-bit value.
- Tri-color mark-sweep states; generational layout (young/old).
- Inline cache state (mono→poly→mega); hidden-class transition chain; JIT tier ladder + deopt.
- libuv loop phases + microtask interleave.

## Sources / gaps to honor (from _research.md)
- Ball/Monkey code is paywalled — verify architecture via community ports, don't quote
  exact Ball phrasing/stage order. Pratt 1973, Gudeman NaN-boxing, GC Handbook = paywalled
  ⇒ treat historical attributions `[UNVERIFIED]`.
- CPython Tier-2 JIT + free-threaded PEP 703 are moving targets — benchmark/adoption claims
  need current primary data. V8 Maglev/TurboFan thresholds are flag/version dependent —
  don't teach fixed numbers.
- Scope guard: ZGC/Shenandoah, V8 Turboshaft/Wasm, JVM invokedynamic, CPython asyncio are
  appendix-level (C/D/E), not 05, unless an ADR expands.
