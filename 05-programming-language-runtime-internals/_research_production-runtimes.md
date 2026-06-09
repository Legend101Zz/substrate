# Phase 1 Research Brief — Production Runtimes
## Sub-course 05: Programming Language Runtime Internals
### Source cluster: CPython internals + V8/Node.js/libuv + JVM/HotSpot/GC
### Researcher: researcher-e1610d | Date: 2026-06-09

---

## 1. Key Mechanisms

### 1.1 CPython Object Layout and Reference Counting

**Forcing constraint:** Every Python object must carry its type at runtime (dynamic typing).
Memory must be reclaimed deterministically without a scanning GC for the common (acyclic) case.

**PyObject header (Include/object.h — primary source):**
On 64-bit non-GIL-disabled builds:
```c
struct _object {
    union {
        int64_t ob_refcnt_full;
        struct {
            uint32_t ob_refcnt;    // reference count
            uint16_t ob_overflow;
            uint16_t ob_flags;     // immortal flag, etc.
        };
    };
    PyTypeObject *ob_type;  // pointer to type object
};
```
`PyObject_HEAD` expands to `PyObject ob_base` — every concrete object struct embeds this first.
Variable-size objects (`PyVarObject`) add `Py_ssize_t ob_size` (element count, not bytes).
The C "struct embedding" trick (same as clox's `Obj` header) enables safe upcasts.

**Reference counting mechanics:**
`Py_INCREF(op)` increments `ob_refcnt`; `Py_DECREF(op)` decrements and calls `_Py_Dealloc(op)` when count reaches 0. Deallocation is immediate and stack-recursive (can trigger chain frees). Cost: every pointer copy/delete requires an atomic or non-atomic counter update.

**Immortal objects (CPython 3.12+, PEP 683):** Statically allocated objects (small ints, `None`, `True`, `False`, interned strings, type objects) carry `_Py_IMMORTAL_REFCNT` — their refcount is never modified, avoiding false sharing in multi-threaded scenarios. `ob_flags & _Py_STATICALLY_ALLOCATED_FLAG` guards this.

**Canonical sources:**
- `github.com/python/cpython/blob/main/Include/object.h` (PyObject struct, immortality)
- `github.com/python/cpython/blob/main/Include/cpython/code.h` (PyCodeObject layout)

---

### 1.2 CPython Bytecode Eval Loop and Frame Layout

**Forcing constraint:** Tree-walk interpretation over Python AST is slow (pointer chasing,
type dispatch overhead). A flat bytecode + tight eval loop is cache-friendlier and decouples
compilation from execution.

**Bytecode format (InternalDocs/interpreter.md — primary source):**
Each instruction is a 16-bit code unit (`_Py_CODEUNIT`): 8-bit opcode + 8-bit oparg. Large opargs
use `EXTENDED_ARG` prefixes (up to 3, giving 32-bit effective oparg). Inline cache
follow the opcode word in the bytecode array — they are zero-initialized at compile time and
filled by the specializing adaptive interpreter at runtime. Cache layout is per-opcode (e.g.,
`LOAD_ATTR` has a different cache struct than `BINARY_OP`).

**Eval loop dispatch (Python/ceval.c, Python/generated_cases.c.h):**
```c
_Py_CODEUNIT *next_instr = first_instr;
while (1) {
    _Py_CODEUNIT word = *next_instr++;
    unsigned char opcode = _Py_OPCODE(word);
    unsigned int oparg  = _Py_OPARG(word);
    switch (opcode) { /* generated case per opcode */ }
}
```
With `USE_COMPUTED_GOTOS` (GCC/Clang): `switch` becomes a dispatch table of `&&label` — each
opcode handler ends with a direct indirect jump to the next opcode's label (threaded code),
eliminating the loop-back branch.

**Frame layout (InternalDocs/frames.md — primary source):**
`_PyInterpreterFrame` layout: `[Specials | Locals | Stack]`. Specials include: globals dict,
builtins dict, locals dict, code object, heap `PyFrameObject*` (NULL until needed), function.
Stack is pre-allocated to `co_stacksize`. Most frames are allocated on a **per-thread
frame stack** (contiguous memory, not C stack, not heap per-call) — cheap bump-pointer allocation.
Generator/coroutine frames are embedded in their objects. `PyFrameObject` (visible to Python)
is only lazily heap-allocated when `sys._getframe()` or traceback is requested.

**Specializing adaptive interpreter (PEP 659, CPython 3.11+):**
`generated_cases.c.h` shows that `BINARY_OP` first checks a 16-bit counter field in its inline
cache. When `ADAPTIVE_COUNTER_TRIGGERS(counter)` fires, `_Py_Specialize_BinaryOp()` is called:
it inspects the runtime types and, if stable, **overwrites the opcode in the live bytecode array**
with a specialized variant (e.g., `BINARY_OP_ADD_FLOAT` for float+float). On deoptimization
(type change), the opcode reverts to generic. This is CPython's inline cache: the inline cache
slot directly precedes/follows the instruction in the bytecode stream. The Tier 2 optimizer
(`#ifdef TIER_TWO`) operates on traces of hot instructions (CPython 3.13 experimental).

**Canonical sources:**
- `github.com/python/cpython/blob/main/InternalDocs/interpreter.md`
- `github.com/python/cpython/blob/main/InternalDocs/frames.md`
- `github.com/python/cpython/blob/main/Python/generated_cases.c.h` (BINARY_OP specialization)
- `github.com/python/cpython/blob/main/Python/bytecodes.c` (LOAD_FAST, LOAD_CONST source defs)

---

### 1.3 CPython GIL and Thread Switching

**Forcing constraint:** CPython's reference counting is not thread-safe without locks; a global
lock avoids per-object locking overhead for the common single-threaded case.

**GIL implementation (Python/ceval_gil.c — primary source):**
The GIL is a `bool locked` variable protected by a mutex (`gil_mutex`) and a condition variable
(`gil_cond`). The lock is taken for "short periods" (mostly non-I/O-bound code) and is mostly
uncontended. A thread wanting the GIL waits `sys.getswitchinterval()` microseconds (default
5ms) before setting `gil_drop_request`. The eval loop checks `eval_breaker` (a `uintptr_t` that
ORs GIL drop, pending calls, GC triggers, signal flags) on every instruction via a branch. When
the holding thread sees `gil_drop_request`, it releases the lock and waits on `switch_cond` until
another thread acquires it (FORCE_SWITCHING prevents the same thread from re-acquiring immediately).

**Free-threaded builds (PEP 703, CPython 3.13+):** `Py_GIL_DISABLED` build skips the GIL.
`ob_gc_bits` field replaces `_gc_prev` for per-object GC state tracking. Reference counting
uses biased counting (each thread has a local refcount; global count is periodically merged) to
reduce atomic operations. This changes the `_gc_runtime_state` structure significantly
(`young`/`old[2]` generations replace the flat `generations[3]` array).

**Canonical sources:**
- `github.com/python/cpython/blob/main/Python/ceval_gil.c` (GIL as boolean + mutex + condvar)
- `github.com/python/cpython/blob/main/Include/internal/pycore_gc.h` (Py_GIL_DISABLED flags)

---

### 1.4 CPython Cyclic Garbage Collector

**Forcing constraint:** Reference counting cannot collect cycles (A→B→A stays at refcount 1
forever). A supplementary cycle detector is needed.

**Three-generation design (Python/gc.c, Modules/gcmodule.c — primary sources):**
`NUM_GENERATIONS = 3`. Each generation is a doubly-linked list of `PyGC_Head` structs (prepended
before the `PyObject` — i.e., `_Py_AS_GC(op)` = `(char*)op - sizeof(PyGC_Head)`). The GC
tracks only "container" objects that can hold references (lists, dicts, instances — not integers,
strings). Trigger: generation 0 collects when its count exceeds threshold (default 700 in CPython
≤3.13; changed to 2000 on the CPython 3.14+ main branch); gen 0 collected 10x triggers gen 1;
gen 1 collected 10x triggers gen 2.

**Collection algorithm (gc.c comments):**
1. `update_refs()`: Copy each object's true `ob_refcnt` into `gc_refs` (stored in `_gc_prev` field
   high bits during collection to avoid extra allocation).
2. `subtract_refs()`: For each object in the collected generation, walk its references and decrement
   `gc_refs` of referenced objects. After this, `gc_refs` counts only external references.
3. `move_unreachable()`: Objects with `gc_refs == 0` are unreachable (only internal cycle refs)
   — move to unreachable list. Objects reachable from them are also moved (transitively).
4. Finalize unreachable objects with `__del__` first; sweep the rest.

**Canonical sources:**
- `github.com/python/cpython/blob/main/Python/gc.c` (algorithm, generation structure)
- `github.com/python/cpython/blob/main/Modules/gcmodule.c` (Python-facing API)
- `github.com/python/cpython/blob/main/Include/internal/pycore_interp_structs.h` (`_gc_runtime_state`)

---

### 1.5 V8 Object Model: Hidden Classes (Maps) and Inline Caches

**Forcing constraint:** JavaScript objects are dictionaries by specification; dictionary lookup
is O(1) but has high constant overhead. Hidden classes enable struct-like field layout and
fast IC-guarded property access without changing the language spec.

**Maps (src/objects/map.h — primary source):**
Every V8 heap object has a `Map*` as its first word. A `Map` describes:
- Instance type (JS object, array, function, etc.)
- Property descriptor array (field name → offset in object)
- Prototype chain pointer
- Transitions table (map → next-map for each possible property addition)

When a new property is added to `{x: 1}`, V8 transitions from Map_A to Map_B. Objects that
always add properties in the same order share the same Map chain — they all get the same hidden
class and can use fast field-offset access. Map transitions are stored in a `TransitionArray`
(src/objects/map-inl.h: `raw_transitions` / `transitions_or_prototype_info_` union).

**Inline caches (FeedbackVector, src/objects/feedback-vector.h):**
Each function has a `FeedbackVector` with typed slots (`FeedbackSlotKind`): `kLoadProperty`,
`kCall`, `kStoreGlobalSloppy`, etc. On first execution (uninitialized IC), the slot logs the
observed Map. If the same Map is always seen (monomorphic), Ignition emits fast path code that
checks the Map and does a direct load by offset. If multiple Maps are seen (polymorphic up to 4),
a small table. If megamorphic (>4), falls back to generic lookup. TurboFan inlines these checks
at JIT compile time based on FeedbackVector data.

**Canonical sources:**
- `github.com/v8/v8/blob/main/src/objects/map.h` (Map = hidden class definition)
- `github.com/v8/v8/blob/main/src/objects/map-inl.h` (transitions)
- `github.com/v8/v8/blob/main/src/objects/feedback-vector.h` (FeedbackSlotKind enum, IC slots)

---

### 1.6 V8 JIT Tiers: Ignition → Maglev → TurboFan

**Forcing constraint:** Interpretation is slow for hot code; full optimizing JIT has high
compilation latency. Multiple tiers balance startup latency vs peak throughput.

**Ignition (src/interpreter/):**
Register-based bytecode interpreter (NOT stack-based, unlike CPython/JVM). Each function is
compiled to `BytecodeArray`. Bytecodes use an implicit accumulator register plus explicit
named registers. Dispatch: computed goto (threaded code). Ignition collects profiling data
into `FeedbackVector` slots as it runs.

**Maglev (src/maglev/, introduced ~Chrome 117):**
Mid-tier optimizing JIT. Takes Ignition bytecode + FeedbackVector as input. Produces native
code with ICs baked in. Compilation is on a background thread; faster than TurboFan because
it does fewer optimization passes. `MaglevCompiler::Compile()` is called from the main thread
after background compilation completes. Fills the gap between Ignition and TurboFan.

**TurboFan (full optimizer):**
Builds a "sea of nodes" IR (value+control edges on the same graph). Performs speculative
optimizations (type specialization based on FeedbackVector). If a speculation fails at runtime,
the generated code **deoptimizes**: the JIT frame is reconstructed as an Ignition frame and
execution continues in Ignition. TurboFan is invoked for very hot functions.

**V8 heap spaces:**
Young generation: semi-space (two equal halves, Cheney copy). Scavenger (`src/heap/scavenger.h`):
"A semi-space copying garbage collector" — objects surviving a Scavenge are promoted to old
generation. Old generation: Mark-Sweep-Compact (concurrent marking enabled by default).
`GarbageCollector::SCAVENGER` vs `GarbageCollector::MINOR_MARK_SWEEPER` controlled by
`v8_flags.minor_ms`. Default 4GB max old gen on 64-bit (`kDefaultMaxHeapSize`).

**Canonical sources:**
- `github.com/v8/v8/blob/main/src/interpreter/interpreter.h` (Ignition)
- `github.com/v8/v8/blob/main/src/interpreter/bytecodes.h` (BYTECODE_LIST, CALL_PROPERTY, Jump*)
- `github.com/v8/v8/blob/main/src/maglev/maglev-compiler.h` (Maglev mid-tier)
- `github.com/v8/v8/blob/main/src/heap/scavenger.h` (Scavenger = semi-space copy)
- `github.com/v8/v8/blob/main/src/heap/heap.h` (young/old gen, kDefaultMaxHeapSize)

---

### 1.7 libuv Event Loop (Node.js I/O foundation)

**Forcing constraint:** Network I/O cannot block the JS thread (single-threaded JS semantics
require non-blocking). OS provides multiplexing (epoll/kqueue/IOCP) but requires explicit
polling. libuv abstracts these into a portable event loop.

**Event loop phases (libuv/docs/src/design.rst + src/unix/core.c — primary sources):**

`uv_run()` in `core.c` executes in order per iteration:
1. `uv__update_time(loop)` — update the loop's "now" timestamp (single syscall, not per-timer).
2. `uv__run_timers(loop)` — fire all `setTimeout`/`setInterval` callbacks whose deadline <=
   loop->now. Timer resolution is bounded by OS tick and the `uv__update_time` rate.
3. `uv__run_pending(loop)` — I/O callbacks deferred from previous iteration (e.g., TCP errors).
4. `uv__run_idle(loop)` — idle handles (fire every iteration).
5. `uv__run_prepare(loop)` — prepare handles (fire before blocking for I/O).
6. `uv__io_poll(loop, timeout)` — **block for I/O** using epoll/kqueue/IOCP with computed
   timeout (0 if idle handles active or pending queue nonempty, else nearest timer deadline or
   infinity). This is the only place the thread blocks.
7. `uv__run_pending(loop)` again (up to 8 times to drain pending queue without starvation).
8. `uv__run_check(loop)` — check handles (fire right after I/O poll — `setImmediate` callbacks
   in Node.js land here).
9. `uv__run_closing_handles(loop)` — close callbacks.
10. `uv__update_time(loop)` + `uv__run_timers(loop)` — pick up timers that fired during polling.

**Node.js additions above libuv:**
`process.nextTick()` queue is drained **between phases** by Node's JS scheduler layer (not by
libuv directly). `Promise` microtasks also run between phases (via `queueMicrotask`). Both run
before the next libuv phase. This is why `nextTick` fires before `setImmediate`.

**Handles vs Requests:**
Handles = long-lived (`uv_tcp_t`, `uv_timer_t`, `uv_prepare_t`). Requests = short-lived
(`uv_write_t`, `uv_fs_t`). File I/O uses a thread pool (`uv__work_submit`) — there is no
async file I/O at the kernel level on most platforms; libuv simulates it with worker threads.

**Canonical sources:**
- `github.com/libuv/libuv/blob/v1.x/src/unix/core.c` (uv_run loop body, verified)
- `github.com/libuv/libuv/blob/v1.x/docs/src/design.rst` (authoritative design overview)
- `github.com/libuv/libuv/blob/v1.x/include/uv.h` (uv_run_mode enum)

---

### 1.8 JVM Class Loading, Verification, and Linking

**Forcing constraint:** JVM code can be loaded from untrusted sources at runtime. Bytecode must
be verified before execution to ensure type safety — the verifier is the JVM's security boundary.
Class loading is lazy by spec to avoid loading classes that are never used.

**Pipeline (HotSpot classFileParser.cpp, verifier.cpp — primary sources):**
1. **Load:** `ClassLoader` reads `.class` file bytes from bootstrap/platform/app classpath.
   `ClassFileParser` validates the magic number (`0xCAFEBABE`), version, and parses the
   constant pool, fields, methods, attributes.
2. **Verify:** `Verifier::verify()` runs bytecode verification. Since Java 6, uses StackMapTable
   attributes (pre-computed stack frame types at each branch target) for efficient single-pass
   verification instead of the older iterative data-flow analysis. Checks: type safety of every
   instruction, no uninitialized reads, no stack overflow/underflow.
3. **Prepare:** Allocate static fields and set default values (zero/null/false).
4. **Resolve:** Lazily resolve symbolic references in the constant pool to actual class/method/
   field pointers. First access triggers resolution.
5. **Initialize:** Run `<clinit>` (static initializer) — happens at most once per class, guarded
   by a per-class mutex.

**Class identity:** A class in the JVM is identified by `(name, ClassLoader)` — the same class
loaded by two different classloaders are distinct types. This is the root of framework isolation
(OSGi, application servers).

**Canonical sources:**
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/classfile/classFileParser.cpp`
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/classfile/verifier.cpp`

---

### 1.9 JVM HotSpot JIT: Tiered Compilation

**Forcing constraint:** Interpretation is slow; optimizing JIT has millisecond-scale compilation
latency that hurts startup. Tiered compilation amortizes compilation cost by using a fast
non-optimizing compiler for warm-up and a slow optimizing compiler only for hot code.

**CompLevel enum (compilerDefinitions.hpp — primary source, verified):**
```
CompLevel_none              = 0   // Interpreted (template interpreter)
CompLevel_simple            = 1   // C1, no profiling
CompLevel_limited_profile   = 2   // C1, invocation + backedge counters
CompLevel_full_profile      = 3   // C1, invocation + backedge + MethodData (MDO)
CompLevel_full_optimization = 4   // C2 (server compiler, aggressive optimization)
```

**Tiered compilation flow:**
All methods start at level 0. Invocation/backedge counters trigger C1 (levels 1-3). C1 at
level 3 collects MethodData (type profiles, branch frequencies). When the MDO shows hot paths,
C2 (`opto/c2compiler`) is triggered: it runs the Ideal graph optimizer with inlining,
escape analysis, loop unrolling, vectorization. `CompilationPolicy` in `compilationPolicy.cpp`
makes tier transitions.

**On-Stack Replacement (OSR):** When a method is hot *inside a loop*, the JVM can replace the
interpreted frame mid-execution with a compiled frame at a safepoint — OSR entry points are
at back-edge branch targets.

**Canonical sources:**
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/compiler/compilerDefinitions.hpp`
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/compiler/compilationPolicy.cpp`
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/compiler/compilerDefinitions.inline.hpp`

---

### 1.10 JVM Safepoints

**Forcing constraint:** GC, deoptimization, and thread dumps require that all Java threads
stop at a consistent state where the GC can walk all object references. Inserting a lock check
on every instruction is too expensive.

**Mechanism (runtime/safepoint.hpp, runtime/safepoint.cpp — primary sources):**
`SafepointSynchronize::SynchronizeState` is a `volatile` enum with three states:
`_not_synchronized = 0`, `_synchronizing = 1`, `_synchronized = 2`.

**Requesting a safepoint:**
The VM thread calls `SafepointSynchronize::begin()`. It sets `_state = _synchronizing` and
arms a **polling page** (memory-mapped page that is marked non-readable). Compiled code
contains safepoint polls — a `test` or `load` instruction on the polling page address at
loop back-edges and method returns. When the page is non-readable, the access faults, and the
signal handler brings the thread to a safe state. Interpreted threads check `eval_breaker`
(analogous to CPython's `eval_breaker`). JNI threads already outside Java code are in a safe
state by definition. `_waiting_to_block` counts outstanding threads. Once zero,
`_state = _synchronized` and the VM thread proceeds. After the safepoint operation,
`end()` restores the polling page and wakes threads.

**G1 GC context:** G1 (`g1CollectedHeap.hpp`) uses concurrent marking (most work done
concurrently with mutators) with brief STW safepoints for initial-mark and remark phases.
Young GC is STW. Old GC is concurrent with brief STW pauses.

**Canonical sources:**
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/runtime/safepoint.hpp`
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/runtime/safepoint.cpp`
- `github.com/openjdk/jdk/blob/master/src/hotspot/share/gc/g1/g1CollectedHeap.hpp`

---

## 2. Foundational Sources

| Claim | Source |
|-------|--------|
| PyObject struct with refcount + ob_type | `github.com/python/cpython/blob/main/Include/object.h` |
| Immortal objects (ob_flags) | `github.com/python/cpython/blob/main/Include/object.h` (Py_GIL_DISABLED block) |
| Bytecode as 16-bit code units; inline cache; eval stack | `github.com/python/cpython/blob/main/InternalDocs/interpreter.md` |
| Frame layout (Specials+Locals+Stack, per-thread stack) | `github.com/python/cpython/blob/main/InternalDocs/frames.md` |
| BINARY_OP specialization (PEP 659 implementation) | `github.com/python/cpython/blob/main/Python/generated_cases.c.h` |
| LOAD_FAST, LOAD_CONST bytecode definitions | `github.com/python/cpython/blob/main/Python/bytecodes.c` |
| GIL = boolean + mutex + condvar; eval_breaker; FORCE_SWITCHING | `github.com/python/cpython/blob/main/Python/ceval_gil.c` |
| CPython 3-generation GC; gc_refs algorithm | `github.com/python/cpython/blob/main/Python/gc.c` |
| _gc_runtime_state; NUM_GENERATIONS=3; Py_GIL_DISABLED GC bits | `github.com/python/cpython/blob/main/Include/internal/pycore_interp_structs.h` |
| _Py_AS_GC pointer arithmetic | `github.com/python/cpython/blob/main/Include/internal/pycore_gc.h` |
| V8 Map = hidden class; transitions_or_prototype_info_ | `github.com/v8/v8/blob/main/src/objects/map.h` + `map-inl.h` |
| FeedbackSlotKind (IC kinds: kLoadProperty, kCall, etc.) | `github.com/v8/v8/blob/main/src/objects/feedback-vector.h` |
| Ignition = register-based bytecode; InterpreterAssembler | `github.com/v8/v8/blob/main/src/interpreter/interpreter.h` |
| V8 Maglev mid-tier JIT | `github.com/v8/v8/blob/main/src/maglev/maglev-compiler.h` |
| V8 Scavenger = semi-space copying | `github.com/v8/v8/blob/main/src/heap/scavenger.h` |
| V8 heap: young/old gen, 4GB default max | `github.com/v8/v8/blob/main/src/heap/heap.h` |
| libuv event loop phases (authoritative) | `github.com/libuv/libuv/blob/v1.x/docs/src/design.rst` |
| uv_run() source code (verified loop order) | `github.com/libuv/libuv/blob/v1.x/src/unix/core.c` |
| uv_run_mode enum | `github.com/libuv/libuv/blob/v1.x/include/uv.h` |
| CompLevel enum (0–4) | `github.com/openjdk/jdk/blob/master/src/hotspot/share/compiler/compilerDefinitions.hpp` |
| C1/C2 tier transition logic | `github.com/openjdk/jdk/blob/master/src/hotspot/share/compiler/compilationPolicy.cpp` |
| Safepoint states (_not_synchronized/_synchronizing/_synchronized) | `github.com/openjdk/jdk/blob/master/src/hotspot/share/runtime/safepoint.hpp` |
| Safepoint polling page mechanism | `github.com/openjdk/jdk/blob/master/src/hotspot/share/runtime/safepoint.cpp` |
| HotSpot class file parsing pipeline | `github.com/openjdk/jdk/blob/master/src/hotspot/share/classfile/classFileParser.cpp` |
| HotSpot bytecode verification (StackMapTable) | `github.com/openjdk/jdk/blob/master/src/hotspot/share/classfile/verifier.cpp` |
| G1 GC concurrent marking structure | `github.com/openjdk/jdk/blob/master/src/hotspot/share/gc/g1/g1CollectedHeap.hpp` |

---

## 3. Why It's This Way — Constraints and Tradeoffs

| Design | Forcing constraint | Tradeoff accepted |
|---|---|---|
| **CPython refcount** | Deterministic cleanup without GC pause; simple to implement in C without GC infrastructure | Cannot collect cycles; every pointer op costs a counter update; threads need GIL or biased refcount |
| **CPython supplementary cyclic GC** | Refcount cannot collect `A→B→A`; pure mark-and-sweep is whole-heap | Generation 0 collects frequently (cheap); only containers tracked; `__del__` still breaks it |
| **CPython GIL** | Refcount is not thread-safe; per-object locking has high overhead for single-threaded common case | True parallelism blocked for CPU-bound code; GIL is released for I/O and C extensions |
| **PEP 659 inline caches in bytecode stream** | Avoids a separate cache data structure; cache is exactly co-located with the instruction | Mutates the bytecode array at runtime; requires per-thread copies in free-threaded builds |
| **V8 hidden classes (Maps)** | JS dict objects need struct-like speed for JIT | Map transitions create memory overhead when object shapes diverge; megamorphic sites degrade to hash lookup |
| **V8 FeedbackVector per-function** | JIT needs per-callsite type profiles to specialize | Function-level granularity means type pollution across callers sharing a function |
| **V8 Maglev mid-tier** | TurboFan latency too high for medium-hot code; Ignition too slow for sustained load | Three-tier complexity; Maglev produces less optimal code than TurboFan |
| **libuv thread pool for file I/O** | OS async file I/O (io_uring excluded on many platforms) is not universally available | File I/O is not truly event-driven — blocking calls on thread pool threads; pool size limits concurrency |
| **JVM lazy class loading** | Loading all classes at startup would be prohibitively slow (thousands of classes in a typical app) | First access of a class has loading latency; `ClassNotFoundException` at runtime rather than startup |
| **JVM StackMapTable verification (Java 6+)** | Old iterative data-flow verification was O(n^2) per method | `javac` must compute stack frame types at branches and embed them — compiler complexity moved out of the verifier |
| **HotSpot safepoint polling pages** | Checking a lock on every instruction is too expensive | Non-readable page causes a fault — fault handler is slow, but safepoints are rare; fault overhead is amortized |
| **JVM C1+C2 tiered compilation** | C2 has 10–100ms compile latency; interpreting until C2 ready is slow | C1 at level 3 collects profiling data to guide C2; three compilation artifacts (bytecode + C1 + C2) coexist per method |

---

## 4. Common Misconceptions to Preempt

1. **"CPython has no JIT."** Partially false. CPython 3.11+ has a specializing adaptive
   interpreter (Tier 1) that writes specialized opcodes into the live bytecode array. CPython 3.13
   ships experimental Tier 2 (a copy-and-patch JIT emitting machine code). It is not TurboFan-class
   but it is not purely interpreted.

2. **"The GIL means Python is single-threaded."** The GIL serializes CPU-bound Python bytecode
   execution. I/O-bound threads release the GIL during system calls. C extensions (NumPy, etc.) can
   release the GIL for their compute. `multiprocessing` bypasses the GIL entirely.

3. **"V8's Ignition is a stack-based interpreter."** Ignition is **register-based**, not stack-
   based. It uses an implicit accumulator register plus explicit named registers. CPython's eval loop
   is stack-based; V8/Ignition is not.

4. **"setImmediate runs before setTimeout in Node.js."** Only within an I/O callback. Outside
   any I/O context (main module), the order is implementation-dependent. `process.nextTick` fires
   before either, between phases; Promise microtasks also run between phases.

5. **"JavaScript file I/O is async all the way down."** libuv simulates async file I/O using a
   thread pool (`uv__work_submit`). The JS side sees callbacks, but blocking `pread/pwrite` is
   issued on a worker thread. Network I/O is truly async (epoll/kqueue).

6. **"JVM bytecode verification is expensive at runtime."** Since Java 6, verification uses
   pre-computed StackMapTable attributes embedded in the `.class` file. The verifier makes a
   single forward pass — it does not run iterative data-flow analysis. The cost is startup-time, not
   per-call.

7. **"JVM safepoints stop all threads immediately."** Safepoint synchronization is cooperative:
   threads reach safepoint polls at back-edges and method returns. A long-running native loop
   with no back-edge poll can delay the safepoint. `SafepointTimeout` can detect this.

8. **"CPython's cyclic GC tracks all objects."** Only container types (list, dict, set, user-
   defined classes with `__dict__`) are tracked by the cyclic GC. Immutable leaf types (int, float,
   str, bytes) are never added to the GC lists — `_PyObject_GC_MAY_BE_TRACKED` reflects this.

---

## 5. Best Build-Your-Own Targets

### Tier 1 — Core mechanism demonstrations
- **CPython `dis` module walkthrough:** `import dis; dis.dis(fn)` shows the bytecode, inline
  cache entries, and specialized opcodes for any Python function. No build required. Use
  `dis.code_info()` for `co_stacksize`, `co_consts`, `co_localsplusnames`. Direct window into
  sections 1.2 and 1.3. Source: `python.org/3/library/dis` (stdlib, no dependency).

- **Implement a minimal refcount runtime in C:** Struct with `int refcount + void* type_ptr`.
  `INCREF`/`DECREF` macros. A linked list of heap objects. Demonstrates why cycles don't collect.
  ~100 LOC. Then add a mark-and-sweep pass to handle cycles — this is the CPython model at micro
  scale.

- **Build a toy event loop:** Single-threaded loop over `epoll_wait` / `kqueue` / `select`.
  Add a min-heap timer queue. Add a "nextTick" queue drained between I/O phases. ~300 LOC in C
  or Python. Directly reproduces libuv's structure. libuv source `core.c` is the reference.

### Tier 2 — Deeper mechanisms
- **Write a JVM `.class` file reader:** Parse magic, version, constant pool, methods, attributes
  (Code, StackMapTable, LineNumberTable). Print bytecodes. ~500 LOC in any language.
  Teaches class file format, constant pool resolution, bytecode format. Use JVM spec §4 as guide.

- **Add a FeedbackVector + monomorphic IC to an interpreter:** Extend clox (from source cluster 1)
  with a per-call-site Map + cached field offset. On Map mismatch, fall back to dict lookup.
  Directly demonstrates V8's hidden-class + IC design at small scale.

### Tier 3 — Stretch / cross-cutting
- **Implement a two-generation GC:** Young gen = bump-pointer allocation in a fixed-size arena
  with semi-space copy (Cheney's algorithm). Old gen = mark-sweep. Write barrier on pointer
  stores. ~500 LOC. Teaches the generational hypothesis, remembered sets, and write barriers.

---

## 6. Open Questions / Where Sources Disagree

1. **CPython Tier 2 JIT status:** The `TIER_TWO` path in `generated_cases.c.h` is present in
   main but CPython 3.13 ships it as experimental with `--enable-experimental-jit`. The extent
   of its real-world speedup vs Tier 1 specialization is not yet settled. `[UNVERIFIED — stable
   benchmark data not found in primary sources at time of research]`

2. **V8 Maglev vs TurboFan boundary:** The exact invocation-count thresholds at which Ignition
   hands off to Maglev vs Maglev hands off to TurboFan are runtime-flag-controlled and not
   documented in a stable design doc. They differ across Chrome versions. `[UNVERIFIED — no
   canonical threshold values found in v8/v8 source without reading runtime flag defaults]`

3. **libuv timer resolution:** The design.rst says timers are processed after `uv__update_time`,
   but actual timer precision depends on the OS tick (1–15ms on Windows, ~1ms on Linux). Node.js
   docs acknowledge `setTimeout(fn, 0)` is actually `setTimeout(fn, 1)` minimum. Sources agree
   on the mechanism, disagree on exact minimum delay across platforms.

4. **CPython free-threaded (PEP 703) production readiness:** CPython 3.13 ships `python3.13t`
   as an opt-in free-threaded build. The GC structure (`young`/`old[2]` instead of
   `generations[3]`) differs significantly from the GIL build. Performance regressions on single-
   threaded workloads are documented but not yet fully characterized. Sources (CPython issue
   tracker, PEP 703) discuss tradeoffs but real-world adoption is nascent.

5. **JVM G1 vs ZGC for production:** G1 is the default GC since JDK 9. ZGC (sub-millisecond
   STW, concurrent compaction) is available since JDK 15 as production-ready. Which is "better"
   depends on heap size and latency requirements — OpenJDK docs acknowledge this without a clear
   winner. ZGC internals (colored pointers, load barriers) are out of scope for this brief but
   represent a significant gap vs the G1 anchor here.

6. **HotSpot safepoint polling vs thread-local handshakes (JEP 312):** Java 10+ introduced
   thread-local handshakes, allowing the JVM to stop individual threads without a full safepoint.
   This is used for deoptimization and stack sampling. The `safepoint.hpp` code still describes
   the global safepoint mechanism; thread-local handshakes live in `handshake.cpp`. Sources do
   not clearly document which operations use which mechanism.

---

## Gaps Not Covered in This Brief

- ZGC / Shenandoah GC internals (colored pointers, load barriers) — deeper GC theory
- V8 Turboshaft (successor to TurboFan, in progress) — too early for stable primary sources
- CPython `asyncio` event loop vs libuv — asyncio sits above the OS; libuv is a C library
- JVM invokedynamic / method handles (critical for Groovy/Kotlin/JRuby interop)
- V8 WebAssembly (Liftoff baseline + TurboFan) — separate compilation pipeline
- Node.js worker threads vs libuv thread pool distinction at the V8 isolate level

---
*All mechanism claims verified against primary source files at github.com/python/cpython,
github.com/v8/v8, github.com/libuv/libuv, github.com/openjdk/jdk (master branch, 2026-06-09).
devguide.python.org blocked by Walmart proxy; Python devguide content verified via
raw.githubusercontent.com/python/cpython/main/InternalDocs/. [UNVERIFIED] flags mark two
claims where primary source data was not found.*
