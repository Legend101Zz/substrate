# Appendix D · javascript-v8-nodejs-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). D is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for **how V8 runs JavaScript
> and how Node.js drives I/O** — the concrete *speculative, optionally-typed, single-threaded* runtime
> that instantiates appendix **K**'s generic pipeline (esp. the JIT speculate→guard→deopt cycle and
> the register-VM choice) and spine **05**'s runtime canon (hidden classes, inline caches, tiered JIT,
> generational GC, the libuv event loop). Spine 05 + appendix K cross-link DOWN into D. **Bespoke
> structure: one JS value's journey through V8 + one tick through the event loop** — shape it (hidden
> class) → speed it up (inline cache + 3 JIT tiers) → reclaim it (scavenger/mark-compact) → and the
> loop that schedules all of it (libuv phases + microtasks). NOT the K three-stage shape, NOT C's
> "one decision" shape, NOT four clusters. Math: `_recompute.py` (13/13). Factcheck:
> `_factcheck_phase1.md` (0 blockers). Network: nodejs.org / v8.dev HTTP **000** this wave → every
> claim reused from 05's line-verified V8 + libuv source reads (github.com/v8/v8, github.com/libuv/libuv,
> 2026-06-09) + appendix K. Nothing new hardened.

## 1. Thesis
JavaScript hands V8 a brutal contract: **objects are dictionaries by spec, types are dynamic, and the
language must run on the same thread as the UI.** V8's entire design is the answer to "make a
dictionary-of-everything language run near C speed without changing the spec." The trick is
**speculation backed by feedback**: discover the *de-facto* structure (hidden classes / Maps) and
*de-facto* types (FeedbackVector) that programs actually have at runtime, then compile specialized
machine code that assumes them — guarded so it can **deoptimize** when reality diverges (appendix K
Stage 5, in production). Node.js then wraps V8 in **libuv**: a single-threaded event loop that
multiplexes the OS's non-blocking I/O so the JS thread never blocks. Two engines, one story:
*observe the common case, bet on it, keep a way out.*

## 2. One value through V8, one tick through the loop (the bespoke spine)

### Stage 1 — Shape it: hidden classes (Maps) turn dicts into structs (05 §1.5)
- **Forcing constraint:** `obj.x` is spec'd as a dictionary lookup (O(1) but high constant). Hidden
  classes give struct-like fixed-offset access *without* changing the language.
- Every V8 heap object's first word is a `Map*` (the **hidden class**): instance type + a
  property→offset descriptor array + prototype pointer + a **transition table**. Adding property `x`
  to `{}` transitions Map_A→Map_B; objects that add properties **in the same order** share the same
  Map chain and get identical layouts. RECOMPUTED: 1000 objects built in the same key order share **1**
  Map chain; built in divergent orders → many Maps (the "shape explosion" anti-pattern).
- This is WHY constructor-initialized, stable-shape objects are fast and "monkey-patched," divergent
  objects are slow. (Contrast appendix C: CPython boxes everything and never reshapes a dict into a
  struct.)

### Stage 2 — Speed it up: inline caches + the three JIT tiers (05 §1.5, §1.6; appendix K Stage 5)
- **Inline caches (FeedbackVector):** each function has a `FeedbackVector` with typed slots
  (`kLoadProperty`, `kCall`, …). First run logs the observed Map (uninitialized→**monomorphic**). A
  monomorphic IC = 1 Map-compare + 1 fixed-offset load. Up to ~4 Maps → **polymorphic** (a small
  table). >4 → **megamorphic** → generic dict lookup. RECOMPUTED (shared with K/C): monomorphic IC =
  2 ops independent of #fields vs ~1.5 dict probes; polymorphic cost grows with #shapes; >4 falls back.
- **Three tiers (startup vs peak, appendix K's tiering rationale):**
  - **Ignition** — a **register/accumulator-based** bytecode interpreter (NOT stack-based — contrast
    CPython appendix C). Compiles each function to a `BytecodeArray`; collects profiling into the
    FeedbackVector as it runs. RECOMPUTED (shared K): `a*b+c*d` on a register VM = **3** instructions
    vs a stack VM's 7 → fewer dispatches.
  - **Maglev** (~Chrome 117) — mid-tier optimizing JIT: takes bytecode + FeedbackVector, emits native
    code with ICs baked in, on a background thread; fewer passes than TurboFan (fast warm code).
  - **TurboFan** — full optimizer on a **"sea of nodes"** IR (value+control edges in one graph);
    speculative type specialization from feedback; on guard failure **deoptimizes** — reconstructs the
    Ignition frame and resumes interpreting. RECOMPUTED (shared K): tier promotion has a break-even
    N* = compile_cost/(interp−compiled); cold code must NOT be optimized.
- Exact promotion thresholds are flag/version-dependent → `[UNVERIFIED]`, taught as *mechanism +
  break-even*, never fixed numbers (matches 05 §6 open-question #2).

### Stage 3 — Reclaim it: generational GC (Scavenger + Mark-Sweep-Compact) (05 §1.6)
- **Young generation** = semi-space (two equal halves); the **Scavenger** is a **Cheney copying
  collector** — copy live objects to the other half, survivors get **promoted** to old gen.
  RECOMPUTED: with the generational hypothesis (most objects die young), copying only *survivors*
  makes minor GC cost proportional to live young data, not total allocation.
- **Old generation** = **Mark-Sweep-Compact** with **concurrent marking** (default) to keep pauses
  short; `minor_ms` toggles minor mark-sweep vs scavenger. Default max old-gen ≈ **4 GB** on 64-bit
  (`kDefaultMaxHeapSize`) — RECOMPUTED: this is WHY Node OOMs need `--max-old-space-size`.
- (Contrast appendix C's *refcount + cyclic* GC and appendix E's *G1/ZGC region* GC — three different
  answers to the same reclaim problem; this is the appendix payload.)

### Stage 4 — Drive it: the libuv event loop (Node's I/O foundation) (05 §1.7)
- **Forcing constraint:** JS is single-threaded; network I/O must not block it. The OS gives
  non-blocking multiplexing (epoll/kqueue/IOCP) but needs explicit polling — libuv is the portable
  loop around it.
- **`uv_run()` phase order per iteration** (line-verified in 05 from `src/unix/core.c`): update time →
  **timers** (`setTimeout`/`setInterval` whose deadline ≤ now) → pending I/O callbacks → idle →
  prepare → **`uv__io_poll`** (the *only* place the thread blocks; timeout = 0 if work pending, else
  nearest timer, else ∞) → check (`setImmediate`) → close callbacks. RECOMPUTED: poll timeout is
  computed, not fixed — an idle loop sleeps until the next timer instead of busy-spinning.
- **Node's layer above libuv:** `process.nextTick()` and **Promise microtasks** drain **between
  phases** (Node's JS scheduler, not libuv) — *that's* WHY `nextTick` fires before `setImmediate` and
  before the next I/O phase. RECOMPUTED: ordering = (current op) → drain nextTick queue → drain
  microtask queue → next libuv phase.
- **Handles vs Requests; the thread pool:** handles are long-lived (`uv_tcp_t`, `uv_timer_t`),
  requests short-lived (`uv_write_t`, `uv_fs_t`). **File I/O is NOT kernel-async on most platforms** —
  libuv fakes it with a **worker thread pool** (`uv__work_submit`, default 4 threads). RECOMPUTED:
  network I/O scales with epoll (one thread, many fds) but file/DNS/crypto concurrency is bounded by
  the pool size → WHY `UV_THREADPOOL_SIZE` matters and a single thread can saturate it.

## 3. The "speculate on the common case" reconciliation (appendix payload)
| stage | mechanism | the bet | the way out | anchor |
|---|---|---|---|---|
| shape | hidden class / Map + transitions | objects share a stable layout | new Map on shape change | 05 §1.5 |
| dispatch | inline cache (FeedbackVector) | call site is monomorphic | poly→megamorphic→dict | 05 §1.5 |
| compile | Ignition→Maglev→TurboFan | code is hot + type-stable | deopt to Ignition frame | 05 §1.6 / K |
| reclaim | scavenger + mark-compact | most objects die young | promote survivors to old | 05 §1.6 |
| schedule | libuv loop + microtasks | I/O is non-blocking & multiplexable | thread pool for file I/O | 05 §1.7 |

## 4. Common misconceptions to preempt
- "V8's Ignition is stack-based." It is **register/accumulator**-based (contrast CPython appendix C).
- "Hidden classes are permanent." They transition on shape change and ICs deopt — speculation is
  revocable.
- "JS objects are always slow dicts." Stable-shape objects use fixed-offset struct access via Maps;
  only megamorphic/divergent shapes fall back to dictionary mode.
- "A JIT is always faster." Only above the break-even N*; cold code stays in Ignition, and
  type-unstable code that deopts repeatedly is a net loss (appendix K).
- "Node.js file I/O is async all the way down." libuv simulates it on a worker thread pool; only
  network I/O is truly epoll/kqueue-async.
- "`setImmediate` runs before `setTimeout`." Only inside an I/O callback; outside, order is
  implementation-dependent. `nextTick`/microtasks always drain *between* phases, before either.
- "`setTimeout(fn, 0)` runs immediately." Minimum is ~1 ms and bounded by OS tick; the loop fires it
  in the timers phase.
- "There's one GC." Young = copying scavenger; old = concurrent mark-sweep-compact — two collectors.

## 5. Provenance summary
- **REUSED (line-verified in 05 §1.5–1.7):** Map/hidden class + transitions; FeedbackVector ICs
  (mono/poly/megamorphic); Ignition register VM; Maglev mid-tier; TurboFan sea-of-nodes +
  speculation/deopt; scavenger semi-space copy + promotion; old-gen mark-sweep-compact + 4 GB default;
  libuv `uv_run` phase order + io_poll blocking point + thread-pool file I/O; Node nextTick/microtask
  ordering. (05 cited `src/objects/map.h`+`map-inl.h`, `feedback-vector.h`, `interpreter/*`,
  `maglev/*`, `heap/scavenger.h`+`heap.h`, `libuv/src/unix/core.c`+`docs/src/design.rst` directly.)
- **REUSED:** appendix K (register-VM choice, tiering break-even, IC O(1), speculate-guard-deopt),
  06 (data-structure costs), N (math).
- **RECOMPUTED:** `_recompute.py` (13/13) — shape sharing vs explosion; IC mono/poly/megamorphic;
  register-VM instr count; JIT break-even & deopt cost; scavenger survivor-proportional cost; 4 GB
  old-gen cap; libuv poll-timeout computation; nextTick/microtask ordering; thread-pool concurrency
  bound; minor-vs-major GC frequency.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** nodejs.org / v8.dev primary text (000); exact
  Ignition→Maglev→TurboFan promotion thresholds (flag/version-dependent — 05 §6 #2); exact
  `setTimeout(0)` minimum & timer precision per-OS (05 §6 #3); Turboshaft (TurboFan successor, too
  early for stable primaries); WebAssembly Liftoff/TurboFan pipeline (out of scope).

---
**Appendix D reconciled.** Reference-grade, exercise-free, 13/13 recomputed, all mechanisms reused
from 05's line-verified V8 + libuv source reads + appendix K. No chapters yet.