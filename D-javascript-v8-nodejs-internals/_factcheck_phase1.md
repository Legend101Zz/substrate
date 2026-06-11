# Appendix D · javascript-v8-nodejs-internals — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). This pass verifies the
> load-bearing claims of D against **line-verified spine canon** — primarily **05** (which cited the
> V8 + libuv source trees directly: `src/objects/map.h`+`map-inl.h`, `feedback-vector.h`,
> `interpreter/*`, `maglev/*`, `heap/scavenger.h`+`heap.h`, `libuv/src/unix/core.c`+`docs/src/design.rst`)
> — plus appendix **K** (compiler/JIT theory), 06 (data-structure costs), and N (math). **NO new
> primary fetched this wave** — nodejs.org / v8.dev HTTP **000** (re-checked Wave 19). Every
> quantitative claim is re-derived in `_recompute.py` (13/13). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | Every V8 heap object's first word is a `Map*` (hidden class): instance type + property→offset descriptors + prototype + transition table | VERIFIED (reuse) | 05 §1.5 (`src/objects/map.h`, line-cited) |
| 2 | Same key-insertion order → shared Map chain (struct layout); divergent order → shape explosion | VERIFIED (reuse) + RECOMPUTED | 05 §1.5; `_recompute.py` #1 |
| 3 | FeedbackVector ICs: monomorphic = Map-compare + offset load; ≤4 polymorphic; >4 megamorphic → dict | VERIFIED (reuse) + RECOMPUTED | 05 §1.5 (`feedback-vector.h`); appendix K Stage 5; `_recompute.py` #2 |
| 4 | Ignition is a **register/accumulator** bytecode interpreter (NOT stack-based) | VERIFIED (reuse) + RECOMPUTED | 05 §1.6 (`src/interpreter/*`); `_recompute.py` #3 |
| 5 | Maglev (~Chrome 117) = mid-tier optimizing JIT on a background thread, fewer passes than TurboFan | VERIFIED (reuse) | 05 §1.6 (`src/maglev/maglev-compiler.h`) |
| 6 | TurboFan = sea-of-nodes IR + speculative type specialization + **deopt** to an Ignition frame | VERIFIED (reuse) + RECOMPUTED | 05 §1.6; appendix K Stage 5; `_recompute.py` #4 |
| 7 | Tier promotion has break-even N* = compile_cost/(interp−compiled); cold/unstable code not optimized | RECOMPUTED | `_recompute.py` #4; 05 §1.6 startup-vs-peak |
| 8 | Young gen = semi-space; Scavenger = Cheney copying collector; survivors promoted to old gen | VERIFIED (reuse) + RECOMPUTED | 05 §1.6 (`heap/scavenger.h`); `_recompute.py` #5 |
| 9 | Old gen = concurrent Mark-Sweep-Compact; default max ~4 GB on 64-bit (`kDefaultMaxHeapSize`) | VERIFIED (reuse) + RECOMPUTED | 05 §1.6 (`heap/heap.h`); `_recompute.py` #6 |
| 10 | `uv_run()` phase order: timers → pending → idle → prepare → io_poll → check → close; io_poll is the only blocking point | VERIFIED (reuse) + RECOMPUTED | 05 §1.7 (`libuv/src/unix/core.c`, verified loop order); `_recompute.py` #7 |
| 11 | `process.nextTick` + Promise microtasks drain **between phases** (Node layer), before next libuv phase | VERIFIED (reuse) + RECOMPUTED | 05 §1.7; `_recompute.py` #8 |
| 12 | File/DNS/crypto I/O runs on a libuv worker thread pool (default 4); network I/O is true epoll/kqueue | VERIFIED (reuse) + RECOMPUTED | 05 §1.7 (`uv__work_submit`); `_recompute.py` #9 |
| 13 | Generational split: young scavenged far more often than old mark-compacts → short pauses | VERIFIED (reuse) + RECOMPUTED | 05 §1.6; `_recompute.py` #10 |

## `[UNVERIFIED]` carry-forward (none load-bearing — all recomputed or reused from 05's line-cited source reads)
- **nodejs.org / v8.dev primary text** (V8 blog, Node docs) — HTTP **000** this wave. All mechanism
  claims reused from 05's line-verified `github.com/v8/v8` + `github.com/libuv/libuv` source reads
  (2026-06-09); doc naming is illustrative until a fetch heals.
- **Exact Ignition→Maglev→TurboFan promotion thresholds** — flag/version-dependent (05 §6 open-question
  #2); taught as a *mechanism with a break-even*, never as fixed numbers.
- **`setTimeout(fn, 0)` minimum delay & timer precision** — per-OS (1–15 ms Windows, ~1 ms Linux;
  05 §6 #3); the *mechanism* (timers phase, computed poll timeout) is line-verified.
- **`UV_THREADPOOL_SIZE` default (4)** — version-stable but configurable; the *claim that matters*
  (file I/O is pool-bounded, network I/O is epoll-scaled) is line-verified in 05 §1.7.
- **Turboshaft** (TurboFan successor) + **WebAssembly Liftoff/TurboFan** pipeline — too early / out of
  scope (05 "Gaps Not Covered").

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 13/13);
all mechanisms reused from 05's line-verified V8 + libuv source reads + appendix K.