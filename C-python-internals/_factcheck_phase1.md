# Appendix C · python-internals — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). This pass verifies the
> load-bearing claims of C against **line-verified spine canon** — primarily **05** (which cited the
> CPython source tree directly: `Include/object.h`, `InternalDocs/interpreter.md`+`frames.md`,
> `Python/ceval_gil.c`, `Python/gc.c`, `generated_cases.c.h`, `pycore_*`) — plus appendix **K**
> (compiler/JIT theory), 06 (data-structure costs), and N (math). **NO new primary fetched this
> wave** — docs.python.org / devguide.python.org HTTP **000** (re-checked Wave 19). Every
> quantitative claim is re-derived in `_recompute.py` (15/15). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | Every value is a heap `PyObject` with `ob_refcnt` + `ob_type`; `PyObject_HEAD` embedded first; `PyVarObject` adds element-count `ob_size` | VERIFIED (reuse) | 05 §1.1 (`Include/object.h`, line-cited) |
| 2 | `Py_DECREF`→0 calls `_Py_Dealloc` **immediately**, stack-recursive (chain-frees contents) | VERIFIED (reuse) + RECOMPUTED | 05 §1.1; `_recompute.py` #1 |
| 3 | Refcount taxes every pointer copy/delete with a counter write | VERIFIED (reuse) + RECOMPUTED | 05 §1.1 / §3 table; `_recompute.py` #2 |
| 4 | Immortal objects (PEP 683, 3.12+) carry `_Py_IMMORTAL_REFCNT`; count never modified (avoids false sharing) | VERIFIED (reuse) + RECOMPUTED | 05 §1.1; `_recompute.py` #3 |
| 5 | GIL = `bool locked` + `gil_mutex` + `gil_cond`; one global lock around object/refcount mutation | VERIFIED (reuse) | 05 §1.3 (`Python/ceval_gil.c`, line-cited) |
| 6 | Default switch interval 5 ms; waiter sets `gil_drop_request`; holder checks `eval_breaker`; `FORCE_SWITCHING` | VERIFIED (reuse) + RECOMPUTED | 05 §1.3; `_recompute.py` #4 |
| 7 | GIL serializes CPU-bound bytecode but I/O & C-ext release it; `multiprocessing` bypasses | VERIFIED (reuse) + RECOMPUTED | 05 §4 misconception #2; `_recompute.py` #4 |
| 8 | Free-threaded build (PEP 703, `python3.13t`) removes GIL; biased reference counting | VERIFIED (reuse) | 05 §1.3 (`Py_GIL_DISABLED`) |
| 9 | Bytecode = 16-bit code unit (8-bit op + 8-bit arg) + EXTENDED_ARG; CPython is a **stack** VM | VERIFIED (reuse) + RECOMPUTED | 05 §1.2; `_recompute.py` #5,#6 |
| 10 | `_PyInterpreterFrame` = `[Specials\|Locals\|Stack]`, bump-allocated on a per-thread frame stack; `PyFrameObject` lazy | VERIFIED (reuse) + RECOMPUTED | 05 §1.2 (`InternalDocs/frames.md`); `_recompute.py` #7 |
| 11 | Computed-goto threaded dispatch removes the loop-back branch | VERIFIED (reuse) | 05 §1.2 (`USE_COMPUTED_GOTOS`) |
| 12 | Adaptive specializing interpreter (PEP 659, 3.11+): inline caches in the bytecode stream, opcode rewrite, deopt on type surprise | VERIFIED (reuse) + RECOMPUTED | 05 §1.2 (`generated_cases.c.h`); appendix K Stage 5; `_recompute.py` #8 |
| 13 | Tier 2 (3.13 experimental) = traces + copy-and-patch machine-code JIT | VERIFIED (reuse) | 05 §1.2 / §6; appendix K Stage 5 |
| 14 | Cyclic GC: 3 generations, `PyGC_Head` linked lists, gc_refs algorithm, container-only tracking | VERIFIED (reuse) + RECOMPUTED | 05 §1.4 (`Python/gc.c`); `_recompute.py` #10 |
| 15 | Gen-0 threshold default 700 (≤3.13) → 2000 (3.14+ main); 10× promotion ratio → gen-2 ~1/100 of gen-0 | VERIFIED (reuse) + RECOMPUTED | 05 §1.4; `_recompute.py` #9 |

## `[UNVERIFIED]` carry-forward (none load-bearing — all recomputed or reused from 05's line-cited source reads)
- **docs.python.org / devguide.python.org primary text** (language reference, `dis` docs, dev guide) —
  HTTP **000** this wave. All mechanism claims reused from 05's line-verified `github.com/python/cpython`
  source reads (main branch, 2026-06-09); docs naming is illustrative until a fetch heals.
- **PEP 703 free-threaded exact perf numbers** + the `young`/`old[2]` GC restructure details — moving
  target; structural mention only.
- **Tier 2 copy-and-patch JIT speedup & internals** (`--enable-experimental-jit`) — moving target
  (matches 05 §6 open-question #1); described structurally only, no fixed numbers.
- **Exact adaptive-specialization warmup counters** (`ADAPTIVE_COUNTER_TRIGGERS` thresholds) —
  version-dependent; taught as a *mechanism with a break-even* (appendix K caveat), never as fixed
  numbers.
- **Small-int byte size (~28 B)** — illustrative for a 64-bit CPython build; the *claim that matters*
  (ints are boxed heap objects, not machine words) is line-verified in 05 §1.1.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 15/15);
all mechanisms reused from 05's line-verified CPython source reads + appendix K.