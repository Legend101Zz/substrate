# Appendix E · java-jvm-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). E is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for **how the HotSpot JVM runs
> Java bytecode** — the concrete *statically-typed-but-dynamically-loaded, verified, managed* runtime
> that instantiates appendix **K**'s generic pipeline (tiered JIT + speculate→guard→deopt) and spine
> **05**'s runtime canon (classloading, verifier, tiered C1/C2, G1/ZGC, safepoints). Spine 05 +
> appendix K cross-link DOWN into E. **Bespoke structure: the life of a class through the JVM** — load
> the `.class` bytes → *verify* them (the JVM's security boundary) → link & initialize → interpret →
> tier up C1→C2 with deopt → and the two cross-cutting global services every Java thread obeys:
> **safepoints** (stop-the-world rendezvous) and the **GC** (G1/ZGC). NOT C's "one decision" shape,
> NOT D's "value + tick" shape, NOT the K three-stage shape, NOT four clusters. Math:
> `_recompute.py` (13/13). Factcheck: `_factcheck_phase1.md` (0 blockers). Network: docs.oracle.com /
> openjdk.org HTTP **000** this wave → every claim reused from 05's line-verified HotSpot source reads
> (github.com/openjdk/jdk master, 2026-06-09) + appendix K. Nothing new hardened.

## 1. Thesis
The JVM's defining contract is the opposite of CPython's and V8's: **bytecode is statically typed and
verifiable, but loaded dynamically from possibly-untrusted sources at runtime.** So the JVM front-loads
*safety* — a one-pass **bytecode verifier** is the security boundary that lets the runtime then trust
the code and optimize aggressively. Everything downstream follows: **lazy class loading** (don't pay
for classes you never touch), **identity by `(name, ClassLoader)`** (framework isolation),
**tiered C1/C2 compilation** (appendix K's startup-vs-peak, with C1 *also* collecting profiles to feed
C2's speculation), and two global coordination services — **safepoints** (a cooperative stop-the-world
rendezvous so the GC can walk references and the JIT can deopt) and a **region/generational GC**
(G1 by default, ZGC for sub-millisecond pauses). One sentence: *verify once so you can trust forever,
then speculate like everyone else.*

## 2. The life of a class through the JVM (the bespoke spine)

### Stage 1 — Load: read the `.class` bytes, lazily (05 §1.8)
- **Forcing constraint:** a real app has thousands of classes; loading all at startup is prohibitive.
  Classes load **lazily** — on first active use. `ClassFileParser` validates the magic number
  (`0xCAFEBABE`), version, and parses the **constant pool**, fields, methods, attributes.
- **Class identity = `(name, ClassLoader)`.** The *same* `.class` loaded by two classloaders is two
  distinct types — this is the root of OSGi / app-server / plugin isolation. RECOMPUTED: `com.X`
  loaded by 2 loaders ⇒ 2 runtime types ⇒ a cast between them throws `ClassCastException` (the "same
  class but not assignable" gotcha).

### Stage 2 — Verify: the security boundary (05 §1.8)
- **Forcing constraint:** bytecode may be hostile. The **verifier** proves type safety *before*
  execution: every instruction's operand types check, no uninitialized reads, no stack
  overflow/underflow, control flow lands on instruction boundaries.
- Since **Java 6**, verification uses **StackMapTable** attributes (the compiler pre-computes the stack
  frame types at each branch target), so the verifier is a **single forward pass**, not the old
  iterative O(n²)-ish dataflow fixpoint. RECOMPUTED: with pre-computed frame types, verification cost
  is ~linear in bytecode length (one pass) vs the old quadratic re-iteration → WHY the cost moved from
  `javac` to *load-time, once* rather than per-call.

### Stage 3 — Prepare / Resolve / Initialize (05 §1.8)
- **Prepare:** allocate static fields, set defaults (0/null/false). **Resolve:** lazily turn symbolic
  constant-pool references into real class/method/field pointers on first access. **Initialize:** run
  `<clinit>` (static initializer) **at most once per class**, guarded by a per-class mutex.
  RECOMPUTED: N threads racing to first-use a class ⇒ exactly **1** runs `<clinit>`; the rest block on
  the init mutex then proceed → WHY the "lazy holder" idiom is a correct thread-safe singleton.

### Stage 4 — Execute & tier up: interpreter → C1 → C2, with deopt (05 §1.9; appendix K Stage 5)
- **Forcing constraint:** the template interpreter is slow; C2 has 10–100 ms compile latency that
  hurts startup. **Tiered compilation** uses a fast non-optimizing compiler to warm up and the slow
  optimizing one only for hot code.
- **CompLevel ladder (line-verified in 05):** 0 = interpreted; 1 = C1 no profiling; 2 = C1 +
  invocation/backedge counters; 3 = C1 + full profiling (**MethodData / MDO**); 4 = **C2** (server
  compiler: inlining, escape analysis, loop unrolling, vectorization). RECOMPUTED (shared K): tiering
  has a break-even N*; cold methods stay at level 0; only methods past the counter thresholds climb.
- **C1-collects-for-C2:** level 3 gathers type profiles + branch frequencies that let C2 **speculate**
  — the JVM analogue of V8's FeedbackVector. On a wrong speculation, C2 code **deoptimizes** back to
  the interpreter. RECOMPUTED (shared K): speculation pays iff guards rarely fail.
- **On-Stack Replacement (OSR):** a method hot *inside a loop* gets its interpreted frame swapped for a
  compiled frame mid-execution at a back-edge safepoint → WHY a long `for` loop speeds up without ever
  returning. Exact `-XX:CompileThreshold` values are flag/version-dependent → `[UNVERIFIED]`.

### Stage 5 — Cross-cutting service A: safepoints (05 §1.10)
- **Forcing constraint:** GC, deopt, and thread dumps need every Java thread parked at a state where
  the GC can walk all object references. Polling a lock on *every* instruction is too expensive.
- **Mechanism:** `SafepointSynchronize` state ∈ {`_not_synchronized`, `_synchronizing`,
  `_synchronized`}. The VM thread arms a **polling page** (mmap'd page marked non-readable); compiled
  code has cheap safepoint polls (a load/test on that page) at **loop back-edges and method returns**.
  When armed, the access faults → the signal handler parks the thread. Interpreted threads check
  `eval_breaker` (same idea as CPython appendix C). RECOMPUTED: a poll is ~free when the page is
  readable (1 load that never faults) and only the rare arming costs a fault → WHY safepoints are cheap
  in steady state. **Cooperative, not instant:** a native loop with no back-edge poll can delay the
  safepoint (`SafepointTimeout` detects it). Java 10+ adds **thread-local handshakes** (stop one thread
  without a full safepoint) → `[UNVERIFIED]` which ops use which (lives in `handshake.cpp`).

### Stage 6 — Cross-cutting service B: garbage collection (G1 default, ZGC low-latency) (05 §1.10, §6)
- **G1 (default since JDK 9):** heap split into equal **regions**; young GC is STW (copy survivors);
  old GC is **mostly concurrent marking** with brief STW initial-mark/remark safepoints. RECOMPUTED:
  region granularity lets G1 collect the regions with the most garbage first ("garbage first") and
  target a pause-time goal instead of collecting the whole heap.
- **ZGC (production since JDK 15):** sub-millisecond STW via **colored pointers + load barriers** doing
  concurrent compaction; chosen for large heaps / strict latency. RECOMPUTED (qualitative): ZGC trades
  per-access load-barrier overhead for near-zero pause — the inverse tradeoff to throughput-first GCs.
  ZGC internals are a deliberate `[UNVERIFIED]` depth gap (05 §6 #5).
- (Contrast appendix C's refcount+cyclic GC and appendix D's scavenger+mark-compact — three answers to
  the same reclaim problem; the appendix payload.)

## 3. The "verify once, then trust & speculate" reconciliation (appendix payload)
| stage | mechanism | the bet / guarantee | the way out / cost | anchor |
|---|---|---|---|---|
| load | lazy `(name,ClassLoader)` loading | only touched classes load | distinct types per loader | 05 §1.8 |
| verify | StackMapTable single pass | bytecode is type-safe | load-time cost, once | 05 §1.8 |
| init | `<clinit>` once per class, mutex | thread-safe lazy init | first-use latency | 05 §1.8 |
| compile | interp → C1(0-3) → C2(4) | code is hot + type-stable | deopt to interpreter | 05 §1.9 / K |
| safepoint | polling page + back-edge polls | cheap in steady state | cooperative delay | 05 §1.10 |
| GC | G1 regions / ZGC colored ptrs | pause-time goal / sub-ms | concurrent-work overhead | 05 §1.10 |

## 4. Common misconceptions to preempt
- "Bytecode verification is expensive at runtime." Since Java 6 it's a single forward pass using
  pre-computed StackMapTable; cost is load-time, once — not per-call.
- "A class is identified by its name." It's `(name, ClassLoader)`; two loaders ⇒ two incompatible types.
- "Safepoints stop all threads instantly." Cooperative — threads stop at back-edge/return polls; a
  native loop with no poll can delay it.
- "The JVM is just an interpreter / has no JIT." It tiers interp→C1→C2 with profile-guided
  speculation and deopt (appendix K).
- "C1 and C2 are alternatives." They coexist per method: C1 warms up *and* profiles (level 3) to feed
  C2's speculation.
- "There's one GC." G1 (default), ZGC, Shenandoah, Parallel, Serial — different pause/throughput
  tradeoffs; G1 ≠ ZGC.
- "`<clinit>` can run twice under contention." No — per-class init mutex guarantees exactly once
  (basis of the thread-safe lazy-holder singleton).
- "ZGC is always better than G1." ZGC minimizes pause at the cost of load-barrier throughput; the
  right choice depends on heap size & latency SLO.

## 5. Provenance summary
- **REUSED (line-verified in 05 §1.8–1.10):** class file parsing (`0xCAFEBABE`, constant pool);
  `(name, ClassLoader)` identity; StackMapTable single-pass verification; prepare/resolve/initialize +
  `<clinit>` once; CompLevel 0–4 (C1/C2) + MethodData profiling; OSR; deopt; safepoint states +
  polling page + back-edge polls + thread-local handshakes; G1 concurrent marking; ZGC. (05 cited
  `classFileParser.cpp`, `verifier.cpp`, `compilerDefinitions.hpp`+`compilationPolicy.cpp`,
  `safepoint.hpp`+`.cpp`, `g1CollectedHeap.hpp` directly.)
- **REUSED:** appendix K (tiering break-even, speculate-guard-deopt), 06 (costs), N (math).
- **RECOMPUTED:** `_recompute.py` (13/13) — `(name,ClassLoader)` distinct types / ClassCastException;
  StackMapTable linear vs quadratic verify; `<clinit>` exactly-once under N-thread race; CompLevel
  ladder + tier break-even; C2 speculation/deopt cost; OSR back-edge trigger; safepoint poll near-free
  + cooperative delay; G1 garbage-first region selection; ZGC pause-vs-throughput inversion;
  magic-number constant; generational young-vs-old GC frequency.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** docs.oracle.com / openjdk.org primary text +
  the JVM Spec §4 (hosts 000); exact `-XX:CompileThreshold` / tier counters (flag/version-dependent —
  taught as mechanism + break-even, never fixed numbers); thread-local handshakes vs full-safepoint
  op mapping (`handshake.cpp`, 05 §6 #6); ZGC colored-pointer / load-barrier internals (05 §6 #5);
  invokedynamic / method handles; Shenandoah internals (out of scope, 05 "Gaps Not Covered").

---
**Appendix E reconciled.** Reference-grade, exercise-free, 13/13 recomputed, all mechanisms reused
from 05's line-verified HotSpot source reads + appendix K. No chapters yet.