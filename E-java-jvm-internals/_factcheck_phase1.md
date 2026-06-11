# Appendix E · java-jvm-internals — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). This pass verifies the
> load-bearing claims of E against **line-verified spine canon** — primarily **05** (which cited the
> HotSpot source tree directly: `classFileParser.cpp`, `verifier.cpp`, `compilerDefinitions.hpp`,
> `compilationPolicy.cpp`, `safepoint.hpp`+`.cpp`, `g1CollectedHeap.hpp`) — plus appendix **K**
> (compiler/JIT theory), 06 (data-structure costs), and N (math). **NO new primary fetched this
> wave** — docs.oracle.com / openjdk.org HTTP **000** (re-checked Wave 19). Every quantitative claim
> is re-derived in `_recompute.py` (13/13). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | Classes load lazily; `ClassFileParser` validates `0xCAFEBABE` + version + constant pool | VERIFIED (reuse) + RECOMPUTED | 05 §1.8 (`classFileParser.cpp`); `_recompute.py` #2 |
| 2 | Class identity = `(name, ClassLoader)`; same bytes via 2 loaders → 2 distinct types | VERIFIED (reuse) + RECOMPUTED | 05 §1.8; `_recompute.py` #1 |
| 3 | Verifier proves type safety pre-execution; since Java 6 a **single forward pass** via StackMapTable | VERIFIED (reuse) + RECOMPUTED | 05 §1.8 (`verifier.cpp`); `_recompute.py` #3 |
| 4 | Prepare/Resolve/Initialize; `<clinit>` runs **at most once** per class under a per-class mutex | VERIFIED (reuse) + RECOMPUTED | 05 §1.8; `_recompute.py` #4 |
| 5 | CompLevel 0–4: interp → C1(1–3, level 3 = MethodData) → C2(4) | VERIFIED (reuse) + RECOMPUTED | 05 §1.9 (`compilerDefinitions.hpp`, line-cited); `_recompute.py` #5 |
| 6 | Tiering has a break-even N*; cold methods stay at level 0; counters drive promotion | RECOMPUTED | `_recompute.py` #5; appendix K; 05 §1.9 |
| 7 | C1 level 3 profiles type/branch freq to feed C2 speculation; C2 deopts to interpreter on guard fail | VERIFIED (reuse) + RECOMPUTED | 05 §1.9; appendix K Stage 5; `_recompute.py` #6 |
| 8 | OSR swaps a hot loop's interpreted frame for a compiled frame at a back-edge safepoint | VERIFIED (reuse) + RECOMPUTED | 05 §1.9; `_recompute.py` #7 |
| 9 | Safepoint states `_not_synchronized`/`_synchronizing`/`_synchronized`; polling page + back-edge/return polls | VERIFIED (reuse) + RECOMPUTED | 05 §1.10 (`safepoint.hpp`+`.cpp`); `_recompute.py` #8 |
| 10 | Safepoints are cooperative: a poll-less native loop can delay the global stop (`SafepointTimeout`) | VERIFIED (reuse) + RECOMPUTED | 05 §1.10 misconception #7; `_recompute.py` #9 |
| 11 | G1 (default since JDK 9): equal regions, garbage-first selection to meet a pause-time goal; concurrent marking | VERIFIED (reuse) + RECOMPUTED | 05 §1.10 (`g1CollectedHeap.hpp`); `_recompute.py` #10 |
| 12 | ZGC (JDK 15+): colored pointers + load barriers → sub-ms pause, per-access overhead (inverse tradeoff) | VERIFIED (reuse) + RECOMPUTED | 05 §6 open-question #5; `_recompute.py` #11 |
| 13 | Generational hypothesis: young GC runs far more often than old GC → short frequent pauses | VERIFIED (reuse) + RECOMPUTED | 05 §1.10; `_recompute.py` #12 |

## `[UNVERIFIED]` carry-forward (none load-bearing — all recomputed or reused from 05's line-cited source reads)
- **docs.oracle.com / openjdk.org primary text + the JVM Specification §4** — HTTP **000** this wave.
  All mechanism claims reused from 05's line-verified `github.com/openjdk/jdk` master source reads
  (2026-06-09); spec/doc naming is illustrative until a fetch heals.
- **Exact `-XX:CompileThreshold` / tier-transition counters** — flag/version-dependent; taught as a
  *mechanism with a break-even*, never as fixed numbers (appendix K caveat).
- **Thread-local handshakes (JEP 312, Java 10+) vs full-safepoint op mapping** — lives in
  `handshake.cpp`; which operation uses which is not clearly documented in the source read (05 §6 #6).
- **ZGC colored-pointer / load-barrier internals** — deliberate depth gap (05 §6 #5); described
  qualitatively only (pause-vs-throughput inversion), no internal-mechanism numbers.
- **invokedynamic / method handles + Shenandoah GC internals** — out of scope (05 "Gaps Not Covered").
- **G1 pause / ZGC pause numbers (~50 ms / ~0.5 ms)** — illustrative for relative comparison; the
  *claim that matters* (G1 = region/garbage-first/pause-goal; ZGC = concurrent-compaction sub-ms) is
  line-verified in 05.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 13/13);
all mechanisms reused from 05's line-verified HotSpot source reads + appendix K.