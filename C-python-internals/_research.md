# Appendix C · python-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). C is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for **how CPython actually
> runs Python** — the one concrete dynamic-managed-runtime that instantiates appendix **K**'s generic
> pipeline (front-end → bytecode VM → specialization) and spine **05**'s runtime canon (refcount,
> eval loop, GIL, cyclic GC). Spine 05 + appendix K cross-link DOWN into C for the CPython-specific
> mechanism. **Bespoke structure: the life of a `PyObject` through the CPython machine** — header →
> refcount death → the GIL that protects the count → the stack-based eval loop that adapts itself →
> the cyclic GC that mops up what refcount can't. NOT the K three-stage shape, NOT four clusters, NOT
> a build progression. Math: `_recompute.py` (15/15). Factcheck: `_factcheck_phase1.md` (0 blockers).
> Network: docs.python.org / devguide.python.org HTTP **000** this wave → every claim reused from
> 05's line-verified CPython source reads (github.com/python/cpython main branch, 2026-06-09) +
> appendix K. Nothing new hardened.

## 1. Thesis
CPython is the **reference implementation built around one decision: manage memory by reference
counting, in C, with no built-in GC infrastructure.** That single choice is the forcing function for
almost everything else. Refcounting gives *deterministic, immediate* cleanup and a trivial C-API —
but (a) it is **not thread-safe** without a lock, which is *why the GIL exists*; (b) it **cannot
collect reference cycles**, which is *why a supplementary cyclic GC exists*; and (c) it taxes every
pointer copy with a counter write, which is *why immortal objects and specialization matter*. CPython
is not "Python is slow because interpreted" — it is "Python is shaped by deterministic refcounting,"
and the eval loop has, since 3.11, become a **self-modifying adaptive interpreter** (appendix K's
speculate→guard→deopt cycle, applied in-place to the bytecode array).

## 2. The life of a PyObject (the bespoke spine)

### Stage 0 — Every value is a heap `PyObject` with its type at runtime (05 §1.1)
- **Forcing constraint:** dynamic typing ⇒ every object must carry its type at runtime. The
  `PyObject` header is `{ ob_refcnt; PyTypeObject *ob_type; }`; `PyObject_HEAD` is embedded first in
  every concrete struct (the same C "struct embedding"/upcast trick as clox's `Obj`). `PyVarObject`
  adds `ob_size` (element *count*, not bytes) for variable-length objects (list, tuple, str).\ Even `1`, `None`, `True` are heap objects with a header — there are no unboxed primitives (contrast
  V8 SMIs / JVM primitives). This is WHY a Python `int` is ~28 bytes, not 8.

### Stage 1 — Refcount: the object lives and dies by a counter (05 §1.1)
- `Py_INCREF(op)` bumps `ob_refcnt` on every new reference; `Py_DECREF(op)` drops it and, **at zero**,
  calls `_Py_Dealloc(op)` **immediately** (deterministic, stack-recursive — freeing a container can
  chain-free its contents). RECOMPUTED: a 3-element list at refcount 0 → 1 list dealloc + up to 3
  child decrefs in one synchronous cascade.
- **Cost:** every pointer copy/delete is a counter write. RECOMPUTED: passing one object through 5
  frames that each hold a temporary reference = up to 10 refcount ops (5 incref + 5 decref) for *zero*
  real work — the refcount tax.
- **Immortal objects (PEP 683, 3.12+):** small ints, `None`, `True`/`False`, interned strings, type
  objects carry `_Py_IMMORTAL_REFCNT` and their count is **never modified** — avoids cache-line
  false-sharing when many threads touch `None`. RECOMPUTED: marking the N hottest shared singletons
  immortal removes their refcount writes entirely (the contended ones).

### Stage 2 — The GIL: the lock that makes refcounting safe (05 §1.3; appendix K speculation context)
- **Forcing constraint:** `ob_refcnt++` is not atomic; making *every* refcount op atomic, or giving
  every object its own lock, would crush the single-threaded common case. The **GIL** is one global
  lock (`bool locked` + `gil_mutex` + `gil_cond`) so that only one thread mutates Python objects /
  refcounts at a time.
- **Switching:** a waiting thread waits `sys.getswitchinterval()` (default **5 ms**) then sets
  `gil_drop_request`; the holder checks `eval_breaker` (an OR of GIL-drop / pending-calls / GC / signal
  flags) and releases at the next bytecode boundary; `FORCE_SWITCHING` stops it re-grabbing instantly.
- **What the GIL does NOT mean:** it serializes *CPU-bound Python bytecode*, not the process. I/O,
  `time.sleep`, and well-behaved C extensions (NumPy) **release** the GIL; `multiprocessing` sidesteps
  it with separate interpreters. RECOMPUTED: 4 CPU-bound threads ≈ 1 core of throughput (GIL-bound);
  4 I/O-bound threads ≈ overlap, because each releases the GIL while blocked.
- **Free-threaded build (PEP 703, `python3.13t`):** removes the GIL; uses **biased reference
  counting** (a thread-local count merged periodically into a shared count) to cut atomics, plus
  per-object locks. Single-threaded regression documented; production-nascent. `[UNVERIFIED]` exact
  perf numbers (moving target).

### Stage 3 — The eval loop: a stack VM that rewrites itself (05 §1.2; appendix K Stages 2 & 5)
- **Bytecode = 16-bit code unit** = 8-bit opcode + 8-bit oparg; opargs >255 use up to 3
  `EXTENDED_ARG` prefixes (32-bit effective). RECOMPUTED (shared with K): arg 255 → 1 unit; arg 256 →
  2 units. CPython is a **stack VM** (operands on a value stack) — contrast V8 Ignition's register
  model (appendix D). Stack VM ⇒ trivially simple compiler; more, narrower instructions.
- **Frames are cheap:** `_PyInterpreterFrame` = `[Specials | Locals | Stack]`, bump-allocated on a
  **per-thread frame stack** (not malloc-per-call, not the C stack). The Python-visible `PyFrameObject`
  is only lazily heap-allocated when `sys._getframe()`/traceback needs it. RECOMPUTED: N nested calls
  = N bump-pointer pushes, not N mallocs.
- **Dispatch:** `USE_COMPUTED_GOTOS` turns the `switch` into a `&&label` table — each opcode handler
  ends by jumping directly to the next opcode (threaded code), removing the loop-back branch
  (appendix A branch-prediction win).
- **The adaptive specializing interpreter (PEP 659, 3.11+) — this is appendix K's JIT cycle, in
  bytecode:** each specializable opcode has an **inline cache** (zero-initialized cache slots living
  *in the bytecode stream*, right after the opcode) plus a counter. When `ADAPTIVE_COUNTER_TRIGGERS`
  fires, `_Py_Specialize_*` inspects the runtime types and **overwrites the live opcode** with a
  specialized form (`BINARY_OP` → `BINARY_OP_ADD_FLOAT`). On a type surprise it **deoptimizes** back
  to the generic opcode. RECOMPUTED (shared with K): a monomorphic specialized op = 1 type-check + a
  direct path vs the generic dispatch + type-dispatch every time; deopt pays only if the type is
  stable (guard-fail-rate low). This is CPython's "JIT-lite."
- **Tier 2 (3.13 experimental, `--enable-experimental-jit`):** builds *traces* of hot micro-ops and a
  **copy-and-patch** machine-code JIT (appendix K Stage 5 template-JIT). Structural mention only;
  speedup `[UNVERIFIED]` (moving target).

### Stage 4 — The cyclic GC: cleaning up what refcount can't (05 §1.4)
- **Forcing constraint:** refcount cannot collect a cycle (`A→B→A` keeps each at ≥1 forever). A
  **supplementary generational mark-sweep** finds cycles among *container* objects only (list, dict,
  set, instances — never int/str/float leaves; `_PyObject_GC_MAY_BE_TRACKED`).
- **3 generations** (`NUM_GENERATIONS = 3`), each a doubly-linked list of `PyGC_Head` prepended before
  the object (`_Py_AS_GC(op) = (char*)op - sizeof(PyGC_Head)`). Gen-0 threshold default **700**
  (raised to **2000** on the 3.14+ main branch); gen-0 collected 10× triggers gen-1, gen-1 10×
  triggers gen-2 (**generational hypothesis:** most objects die young, so collect the young often and
  cheaply). RECOMPUTED: with the 10× promotion ratio, gen-2 runs ~1/100 as often as gen-0.
- **Algorithm:** `update_refs` copies `ob_refcnt`→`gc_refs`; `subtract_refs` walks internal references
  decrementing `gc_refs`; objects left at `gc_refs == 0` are reachable only via the cycle → moved to
  the unreachable list (and their transitive reachables rescued); finalize (`__del__`) then sweep.
  RECOMPUTED: for an isolated `A↔B` 2-cycle, after subtract_refs both reach gc_refs 0 → both collected;
  if anything external still points at A, A and B are both rescued.
- **Free-threaded GC:** replaces the flat `generations[3]` with `young`/`old[2]` and uses `ob_gc_bits`
  for per-object state (PEP 703). `[UNVERIFIED]` details (moving target).

## 3. The "one decision, many consequences" reconciliation (appendix payload)
| consequence | mechanism | forced by | anchor |
|---|---|---|---|
| deterministic free | `Py_DECREF`→0→immediate dealloc | refcounting | 05 §1.1 |
| every value boxed | `PyObject` header + `ob_type` | dynamic typing | 05 §1.1 |
| the GIL exists | one global lock around object/refcount mutation | refcount not atomic | 05 §1.3 |
| cyclic GC exists | generational mark-sweep over containers | refcount can't collect cycles | 05 §1.4 |
| immortal objects | `_Py_IMMORTAL_REFCNT`, count never written | refcount false-sharing on singletons | 05 §1.1 |
| adaptive interp | inline caches + opcode rewrite + deopt (K cycle) | dynamic dispatch is the cost | 05 §1.2 / K |
| cheap frames | per-thread bump-allocated frame stack | per-call malloc too slow | 05 §1.2 |

## 4. Common misconceptions to preempt
- "CPython has no JIT." False since 3.11: the **adaptive specializing interpreter** rewrites live
  bytecode (Tier 1); 3.13 ships an experimental copy-and-patch machine-code JIT (Tier 2).
- "The GIL makes Python single-threaded." It serializes CPU-bound *bytecode*; I/O and C extensions
  release it; `multiprocessing` bypasses it; free-threaded builds remove it.
- "Reference counting collects everything." It can't collect cycles — that's the *entire reason* the
  cyclic GC exists.
- "The cyclic GC scans every object." Only GC-tracked *containers*; leaf immutables (int/str/float)
  are never tracked.
- "Ignition-style register VM." No — CPython's eval loop is a **stack** VM (appendix D contrasts).
- "`int` is a machine word." It's a heap `PyObject` (~28 B for a small int); small ints are cached &
  immortal.
- "GC threshold is fixed at 700." It's tunable and was raised to 2000 on the 3.14+ main branch.
- "Frames are heap-allocated per call." They're bump-allocated on a per-thread frame stack; the
  Python-visible `PyFrameObject` is lazy.

## 5. Provenance summary
- **REUSED (line-verified in 05 §1.1–1.4):** PyObject header + refcount + immortal objects;
  16-bit code unit + EXTENDED_ARG + inline caches + PEP 659 adaptive specialization + Tier 2;
  `_PyInterpreterFrame` per-thread frame stack; GIL as bool+mutex+condvar + `eval_breaker` +
  switchinterval + PEP 703 free-threaded/biased refcount; 3-generation cyclic GC + gc_refs algorithm +
  thresholds. (05 cited `Include/object.h`, `InternalDocs/interpreter.md`+`frames.md`,
  `Python/ceval_gil.c`, `Python/gc.c`, `generated_cases.c.h` directly.)
- **REUSED:** appendix K (front-end/VM/specialize-guard-deopt theory), 06 (data-structure costs), N.
- **RECOMPUTED:** `_recompute.py` (15/15) — refcount cascade & tax; immortal savings; GIL CPU-vs-IO
  scaling; EXTENDED_ARG encoding; stack-VM instr count; per-thread frame bump vs malloc; specialize
  break-even & deopt cost; GC generation frequency; 2-cycle collection; threshold 700→2000; int boxing
  size.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** docs.python.org / devguide (000) primary text;
  exact PEP 703 free-threaded perf numbers; Tier-2 JIT speedup & internals (moving target); exact
  adaptive-specialization warmup counters (version-dependent — taught as a mechanism with a
  break-even, never as fixed numbers, per K's caveat).

---
**Appendix C reconciled.** Reference-grade, exercise-free, 15/15 recomputed, all mechanisms reused
from 05's line-verified CPython source reads + appendix K. No chapters yet.