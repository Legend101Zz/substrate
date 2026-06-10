# Research Brief — Sub-course 07: Optimizer, External Execution, Advanced Execution Models
## Source cluster: Selinger/System R, PostgreSQL optimizer/statistics, external sort, hash join, vectorized/compiled execution, storage models
## Researcher: researcher-053706 | Date: 2026-06-09

---

## 1. Key Mechanisms

### 1.1 Selinger 1979 / System R — Access-Path Selection

**Why:** Databases need to pick among exponentially many join orderings and access methods. The
forcing constraint is combinatorial explosion: n relations have O(n!) join orderings and each join
has multiple physical implementations (nested loop, merge, hash). Without a principled search
strategy, correct enumeration is impossible above n≈5.

**Core algorithm — Dynamic Programming over subsets:**
System R's optimizer (Selinger et al., SIGMOD 1979) introduced:
1. **Access paths for base relations:** for each table, enumerate: sequential scan, available
   B-tree index scans (matching predicates on prefix columns), and for each, compute an estimated
   cost + estimated output cardinality. Costs estimated from catalog statistics (relation size in
   pages, number of tuples, column histograms).
2. **Dynamic programming join enumeration:** build plans bottom-up — first compute optimal plans
   for each single table, then for each 2-table subset, using the best sub-plans from step 1,
   and so on. For n tables there are 2^n - 1 subsets, O(n·2^n) work — exponential but feasible
   for small n (practical limit ≈12 tables before switching to heuristic search).
3. **"Interesting orders":** not all sort orders are equivalent. An order is "interesting" if it
   is useful for a later GROUP BY, ORDER BY, or merge join. The optimizer keeps multiple best
   plans per subset: (a) the cheapest plan overall, (b) the cheapest plan for each interesting
   sort order — so an expensive sort at one level can be amortized across many later uses.
   [UNVERIFIED: exact Selinger 1979 paper text not directly extracted — PDF is scanned image.
   Source URL confirmed: https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf
   — 16-page scanned PDF, version 1.3. Algorithm attributed to this paper in all subsequent DB
   literature including PostgreSQL optimizer/README, below.]
4. **Selectivity estimation:** predicates are assigned a selectivity factor SF (fraction of tuples
   passing). Join cardinality = |A| * |B| * SF(join predicate). SF for equality = 1/n_distinct;
   SF for range predicates estimated from column histograms stored in catalog.

**Selinger's key insight:** the principle of optimality applies only within the set of plans that
produce the same output set AND the same sort order. The "interesting order" lattice means you
must retain a Pareto-optimal frontier (cost, sort-order), not a single best plan.

---

### 1.2 PostgreSQL Optimizer — Full Verified Mechanism

**Source:** `src/backend/optimizer/README` (GitHub postgres/postgres master branch).
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/README

**Overview:** Parser → Planner → Plan tree for Executor. The planner builds `RelOptInfo` trees
(one per relation or join), populates them with candidate `Path` nodes (implementations), and
selects the cheapest per-rel `Path` as the final plan.

**RelOptInfo:** One struct per base relation. Accumulates all feasible access Paths and all join
clauses linking it to other relations. For a join of {A, B, C}, there is exactly one `RelOptInfo`
regardless of join order; different join orders create different `Path` nodes inside it.

**Path types for base relations:**
- SeqScan (plain sequential)
- IndexScan (one B-tree/index)
- BitmapIndexScan + BitmapHeapScan (multiple indexes OR-ed/AND-ed)
- Function RTEs: one fixed Path

**Path types for joins:**
- NestLoopPath, MergePath, HashPath
- Inner/outer role: outer drives the inner. In merge join, both paths scanned in-sync.
- Build phase in hash join: inner scanned first → hash table; outer probes.

**Join enumeration — dynamic programming:**
Pass 1: pairs of base rels joined with available join clauses.
Pass 2: triples, etc. Last pass: all base rels joined.
Left-handed, right-handed, and bushy plans all considered.
`add_path()` discards dominated paths before inserting into pathlist.
`compare_path_costs_fuzzily()` uses `STD_FUZZ_FACTOR = 1.01` to avoid thrashing over nearly
identical costs. Source: `src/backend/optimizer/util/pathnode.c`.
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/util/pathnode.c

**GEQO fallback:** When n ≥ `geqo_threshold` (default 12), the standard DP planner is replaced
by Genetic Query Optimization (semi-random search through join orderings).
`from_collapse_limit` (default 8) and `join_collapse_limit` (default 8) control flattening of
subqueries and explicit JOINs before DP runs.
Source: https://www.postgresql.org/docs/current/runtime-config-query.html

**Interesting orders — PostgreSQL implementation as PathKeys:**
PathKey = (EquivalenceClass, opfamily, sort direction, nulls-first).
EquivalenceClass merges all expressions known equal (e.g., via JOIN or equality predicates).
`make_canonical_pathkey()` interns all PathKeys — the same path key reused across Paths so
pointer equality detects identity. Ordering-preserving paths are kept in pathlist alongside the
cheapest unordered path.
Source: `src/backend/optimizer/path/pathkeys.c`
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/path/pathkeys.c

---

### 1.3 PostgreSQL Cost Model

**Source:** `src/backend/optimizer/path/costsize.c` and `src/include/optimizer/cost.h`.
URLs:
- https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/path/costsize.c
- https://raw.githubusercontent.com/postgres/postgres/master/src/include/optimizer/cost.h

**Cost units:** Costs are in abstract "units" relative to `seq_page_cost=1.0`. All parameters
are user-settable GUCs. Default values verified from `cost.h`:

| Parameter | Default | Meaning |
|---|---|---|
| `seq_page_cost` | 1.0 | Cost of one sequential page fetch |
| `random_page_cost` | 4.0 | Cost of one non-sequential page fetch |
| `cpu_tuple_cost` | 0.01 | CPU cost to process one tuple |
| `cpu_index_tuple_cost` | 0.005 | CPU cost per index tuple |
| `cpu_operator_cost` | 0.0025 | CPU cost per operator/function eval |
| `parallel_tuple_cost` | 0.1 | Cost to pass a tuple worker→leader |
| `parallel_setup_cost` | 1000.0 | Shared memory setup for parallelism |
| `effective_cache_size` | 524288 pages | Postgres + OS-level disk cache estimate |

**Two cost components per path:**
- `startup_cost`: cost before first tuple is returned (e.g., building a hash table)
- `total_cost`: cost to fetch all tuples
For LIMIT/EXISTS, actual cost interpolated linearly between them.

**Disabled nodes:** `disable_cost = 1.0e10` added when a GUC like `enable_hashjoin=false` is
set. Paths with fewer disabled nodes win over any cost difference.

**External sort cost (`cost_tuplesort`):**
- In-memory: `cpu = comparison_cost * t * log2(t)` where `comparison_cost = 2 * cpu_operator_cost`
- External: `disk_traffic = 2 * relsize * ceil(logM(nruns))`; M = merge order;
  assumed 3/4 sequential + 1/4 random page accesses.

**Hash join cost (split across `initial_cost_hashjoin` + `final_cost_hashjoin`):**
Startup = cost to scan inner + build hash table.
`startup_cost += (cpu_operator_cost * num_hashclauses + cpu_tuple_cost) * inner_path_rows`
Run cost = scan outer + probe cost per outer tuple.
Multi-batch: total work scales with `nbatch * nbuckets`.

---

### 1.4 PostgreSQL Statistics — pg_statistic and Selectivity

**Source:** PostgreSQL docs https://www.postgresql.org/docs/current/planner-stats.html
and `src/backend/utils/adt/selfuncs.c`.
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/utils/adt/selfuncs.c

**Catalog anchors:**
- `pg_class.reltuples` / `pg_class.relpages`: total row and page counts per table/index.
  Updated lazily by VACUUM, ANALYZE, some DDL. Not updated per-write.
- `pg_statistic` / view `pg_stats`: per-column stats collected by ANALYZE.
  Key fields: `n_distinct` (negative = fraction of total rows; positive = absolute count),
  `most_common_vals` (MCV list), `most_common_freqs`, `histogram_bounds`, `correlation`.

**Selectivity estimation (`selfuncs.c`):**
- `oprrest` function (restriction estimator): returns selectivity ∈ [0,1].
  Called as `Selectivity oprrest(PlannerInfo*, Oid operator, List* args, int varRelid)`.
- `oprjoin` function (join estimator): also accounts for join type and `SpecialJoinInfo`.
- For equality: SF ≈ 1/n_distinct if no MCV. If value in MCV list, use MCV frequency directly.
- For range: interpolate within histogram_bounds buckets.

**Extended statistics (CREATE STATISTICS, PG10+):**
- `dependencies`: functional dependency coefficients between columns (e.g., zip→city: 1.0).
  Adjusts selectivity to avoid underestimating when columns are correlated.
- `ndistinct`: multivariate n-distinct counts for column groups (for GROUP BY estimation).
- `mcv`: multivariate MCV lists for correlated column combinations.

---

### 1.5 External Sort — PostgreSQL tuplesort.c

**Source:** `src/backend/utils/sort/tuplesort.c`
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/utils/sort/tuplesort.c

**Design history:** Before PG15: polyphase merge (Knuth's Algorithm 5.4.2D). Now: balanced k-way
merge. Reason: "tape drives" (i.e., temp file tapes) are cheap in software; the polyphase
algorithm was designed to keep real tape drives busy. With cheap tapes and sufficient work_mem,
we can have as many tapes as runs, eliminating repeated I/O passes entirely.

**Run generation:** Before PG15: replacement selection (priority heap / Knuth Algorithm 5.2.3H)
produced runs averaging 2× work_mem. Now: quicksort/radix sort. Replacement selection was
abandoned because its best-case behavior (sorted input → 1 run) is rarely seen in practice and
its worst-case (reverse-sorted) produces 1-tuple runs that are worse than quicksort.

**State machine (`TupSortStatus`):**
```
TSS_INITIAL    — loading tuples, in-memory only (within workMem)
TSS_BOUNDED    — TopN bounded heap (LIMIT case)
TSS_BUILDRUNS  — exceeded workMem, writing runs to tapes
TSS_SORTEDINMEM — completed in memory
TSS_SORTEDONTAPE — completed, final run on one tape
TSS_FINALMERGE — on-the-fly final merge (saves one read/write cycle)
```

**Key constants (verified):**
- `MINORDER = 6` (min merge fan-in)
- `MAXORDER = 500` (max merge fan-in)
- `MERGE_BUFFER_SIZE = BLCKSZ * 32` (pre-read buffer per tape, ~256KB at 8KB pages)
- `TAPE_BUFFER_OVERHEAD = BLCKSZ` (one page per tape)
- `SLAB_SLOT_SIZE = 1024` (merge slab allocation unit)
- `INITIAL_MEMTUPSIZE = max(1024, ALLOCSET_SEPARATE_THRESHOLD/sizeof(SortTuple)+1)`

**M-way merge:** tapes managed by `logtape.c`, which recycles disk space as soon as a block is
fully read — avoids space waste of traditional external sort implementations.

**Bounded sort (TopN):** if LIMIT k fits in work_mem, uses a heap of k elements.
Cost: `t * log2(k)` comparisons instead of `t * log2(t)`.

**Parallel sort:** each worker produces exactly one sorted run; leader creates a tapeset with
one run per worker, then merges.

---

### 1.6 Hash Join — Variants and PostgreSQL Implementation

**Source:** `src/backend/executor/nodeHashjoin.c`
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/executor/nodeHashjoin.c

**Three variants (per nodeHashjoin.c):**

1. **Simple/in-memory hash join (1 batch):** Build entire inner relation into in-memory hash
   table; probe with outer. Startup = O(inner), probe = O(outer). Requires inner fits in
   `hash_mem`.

2. **Grace hash join (conceptually):** Partition both relations into B buckets by hash(join key);
   process each bucket-pair independently. Never holds full relation in memory.

3. **Hybrid hash join (Zeller & Gray 1990, VLDB):** Keep the first batch in memory as a hot
   partition while partitioning the rest to disk. Reduces I/O vs pure grace by keeping one
   partition live. **This is what PostgreSQL actually implements.** Citation in nodeHashjoin.c:
   "Hansjörg Zeller; Jim Gray (1990). Proceedings of the 16th VLDB conference. Brisbane: 186–197."

**PostgreSQL hybrid hash join mechanics:**
- `nbatch` always a power of 2; doubles when current batch overflows `hash_mem`.
- Serial hash join: lazy batch sizing — detects overflow while loading, dumps and repartitions.
- Parallel hash join: eager batch sizing — all batch changes happen during build phase before
  probing begins.
- Tuple routing: hash bits split into high bits (batch number) and low bits (bucket number).
  Increasing batches = using more hash bits.

**State machine (serial):**
```
HJ_BUILD_HASHTABLE   — scan inner, build hash table for batch 0
HJ_NEED_NEW_OUTER    — fetch next outer tuple
HJ_SCAN_BUCKET       — probe hash bucket for current outer key
HJ_FILL_OUTER_TUPLE  — handle outer-join unmatched outer tuples
HJ_FILL_INNER_TUPLES — handle right/full join unmatched inner tuples
HJ_FILL_OUTER_NULL_TUPLES — null-fill for anti/right joins
HJ_FILL_INNER_NULL_TUPLES — similar for inner
HJ_NEED_NEW_BATCH    — current batch done, load next batch from disk
```

**Parallel hash join phases (verified from nodeHashjoin.c):**
Build barrier: `PHJ_BUILD_ELECT → PHJ_BUILD_ALLOCATE* → PHJ_BUILD_HASH_INNER →
PHJ_BUILD_HASH_OUTER (multi-batch only) → PHJ_BUILD_RUN → PHJ_BUILD_FREE*`
Per-batch: `PHJ_BATCH_ELECT → PHJ_BATCH_ALLOCATE* → PHJ_BATCH_LOAD → PHJ_BATCH_PROBE →
PHJ_BATCH_SCAN* → PHJ_BATCH_FREE*`
Batch 0 skips LOAD (its hash table built during PHJ_BUILD_HASH_INNER).

---

### 1.7 Vectorized Execution — MonetDB/X100 and DuckDB

**Why vectorized:**
Volcano (tuple-at-a-time) has high function call overhead per tuple. Each `Next()` call is an
indirect function pointer dispatch. For analytical workloads processing millions of tuples, this
overhead dominates. On modern CPUs, tight loops over arrays of primitive values enable:
- SIMD (CPU can operate on 4–16 values per instruction)
- Branch predictor stays warm (same loop, same branch pattern for thousands of iterations)
- L1/L2 cache stays hot (array elements accessed sequentially)

**MonetDB/X100 (Boncz, Zukowski, Nes — CIDR 2005):** [Paper URL not accessible directly;
attributed by DuckDB official docs: https://duckdb.org/why_duckdb]
Key insight: process data in "vectors" (arrays of ~1000 values) — small enough to fit in L1 cache,
large enough to amortize function call overhead. Called "vectorized execution" or
"hyper-pipelining." MonetDB/X100 later became Vectorwise (Actian Vector).

**DuckDB vectorized execution:**
- `STANDARD_VECTOR_SIZE = 2048` (a power of 2, enforced by compile-time `#error` if not a power of two).
  Source: `duckdb/common/vector_size.hpp`
  URL: https://raw.githubusercontent.com/duckdb/duckdb/main/src/include/duckdb/common/vector_size.hpp
- `DataChunk`: set of vectors all with same length. The intermediate representation.
  "It effectively represents a subset of a relation."
  Source: `duckdb/common/types/data_chunk.hpp`
  URL: https://raw.githubusercontent.com/duckdb/duckdb/main/src/include/duckdb/common/types/data_chunk.hpp
- A filter operator adds a **selection vector** to the DataChunk (doesn't copy data);
  DataChunk can hold "referencing vectors" pointing into another chunk's memory.
- PhysicalHashJoin: `PhysicalOperatorType::HASH_JOIN`, build side scanned first.
  Source: `duckdb/execution/operator/join/physical_hash_join.hpp`
  URL: https://raw.githubusercontent.com/duckdb/duckdb/main/src/include/duckdb/execution/operator/join/physical_hash_join.hpp
- DuckDB optimizer inspired by "Dynamic Programming Strikes Back" (Moerkotte & Neumann) and uses
  morsel-driven parallelism (Leis, Boncz, Kemper, Neumann).
  Source: https://duckdb.org/why_duckdb

---

### 1.8 Compiled Execution — HyPer/Neumann and PostgreSQL JIT

**Why compiled execution:**
Vectorized still has interpreter overhead for each operator boundary. Compiled execution
eliminates it by generating native machine code for the entire query pipeline, so the CPU never
leaves the tight inner loop.

**Neumann 2011 "Efficiently Compiling Efficient Query Plans for Modern Hardware" (VLDB 2011):**
[Paper fetched from CMU 15-721: https://15721.courses.cs.cmu.edu/spring2016/papers/p539-neumann.pdf
— 6-page PDF version 1.5, 200 OK, but pdftotext returned empty (likely scanned); claims below
are [UNVERIFIED from text] but are consistently cited across literature.]

**Key HyPer mechanism [UNVERIFIED from paper text]:**
- Convert the pull-based Volcano model to a **push-based pipeline** (producer→consumer).
- Each operator implements `produce()` and `consume()`. Data flows top-down on produce() calls,
  bottom-up (data pushed up) on consume() calls.
- The entire pipeline between blocking operators (sort, hash build) compiles to a single tight
  loop in LLVM IR, eliminating all operator boundary function calls.
- Blocking points (materialization) break pipelines; within a pipeline, all computation is fused.
- LLVM IR is generated at query compile time; LLVM backend JIT-compiles to native code.

**PostgreSQL JIT (PG11+):**
Source: `src/backend/jit/README`
URL: https://raw.githubusercontent.com/postgres/postgres/master/src/backend/jit/README

Verified mechanism:
- PostgreSQL uses LLVM for JIT. LLVM chosen for: large corporate backing (unlikely to be
  discontinued), PostgreSQL-compatible license, LLVM IR can be generated from C via Clang.
- JIT target: **expression evaluation** and **tuple deforming** — the parts where indirect
  function dispatch per column/operator is most expensive.
- Example: `WHERE a.col = 3` instead of evaluating via a generic expression-eval interpreter,
  JIT compiles a native function that directly compares the specific column to the constant 3,
  removing several hundred cycles of interpreter overhead.
- JIT provider in a shared library (`llvmjit`), loaded on demand; controlled by `jit_provider` GUC.
- `JITContext`: lifetime-scoped to a query; all JIT functions for one query created and freed together.
- The JIT version of expression evaluation is in `jit/llvm/` separate from `executor/execExprInterp.c`.

---

### 1.9 Storage Models — NSM, DSM, PAX

**NSM (N-ary Storage Model = row store):**
All columns of a tuple stored contiguously on the same page. Typical in OLTP systems.
- Good: full tuple fetched in one page access; no reconstruction needed.
- Bad: for queries touching 2 of 100 columns, 98 columns loaded and discarded.
- Cache line waste: on a 64-byte cache line with 100-byte tuples, ~37% of loaded bytes are
  irrelevant even for single-column queries.

**DSM (Decomposition Storage Model = column store):**
Each column stored in a separate file/segment; rows identified by position (offset).
Introduced: Copeland & Khoshafian, "A Decomposition Storage Model" (SIGMOD 1985). [UNVERIFIED from text]
- Good: queries on few columns load only those columns; SIMD over column arrays is natural.
- Bad: reconstruction of full tuples requires joining multiple column arrays by position;
  writes need to update multiple column files.

**PAX (Partition Attributes Across):**
Within each page, columns are stored separately ("minipages"), but the page is still the
unit of I/O. Paper: Ailamaki, DeWitt, Hill, Skounakis, "Weaving Relations for Cache Performance"
(VLDB 2001). PDF fetched: https://research.cs.wisc.edu/multifacet/papers/vldb01_pax.pdf
(153KB, PDF v1.2, 10 pages, 200 OK; pdftotext returned empty — scanned image, [UNVERIFIED from text]).
- PAX is a compromise: preserves NSM's page-level I/O granularity (no random per-column reads
  across files), but within a page lays out attributes of each column together for cache locality.
- Disadvantage vs DSM: still reads entire pages; better suited as an in-memory format than a
  pure on-disk column store.

**Why the split matters:**
OLTP: NSM. OLAP: DSM or PAX. Hybrid systems (HTAP) use different layouts per query type or per
table — this is the core tradeoff HyPer/Umbra paper motivates for compiled execution.

---

## 2. Foundational Sources

| Claim | Source | URL / Location |
|---|---|---|
| PostgreSQL optimizer DP algorithm, RelOptInfo, PathKey | `src/backend/optimizer/README` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/README |
| PostgreSQL cost constants (seq=1.0, rand=4.0, cpu=0.01) | `src/include/optimizer/cost.h` | https://raw.githubusercontent.com/postgres/postgres/master/src/include/optimizer/cost.h |
| PostgreSQL sort/hash join cost formulas | `src/backend/optimizer/path/costsize.c` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/path/costsize.c |
| PostgreSQL PathKey/EquivalenceClass implementation | `src/backend/optimizer/path/pathkeys.c` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/path/pathkeys.c |
| STD_FUZZ_FACTOR=1.01, path comparison | `src/backend/optimizer/util/pathnode.c` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/util/pathnode.c |
| selfuncs.c selectivity estimators (oprrest/oprjoin) | `src/backend/utils/adt/selfuncs.c` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/utils/adt/selfuncs.c |
| pg_statistic, pg_stats, CREATE STATISTICS (extended) | PostgreSQL docs | https://www.postgresql.org/docs/current/planner-stats.html |
| GEQO threshold=12, join/from_collapse_limit=8 | PostgreSQL docs | https://www.postgresql.org/docs/current/runtime-config-query.html |
| PostgreSQL tuplesort: balanced k-way merge, states, MINORDER=6, MAXORDER=500 | `src/backend/utils/sort/tuplesort.c` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/utils/sort/tuplesort.c |
| PostgreSQL hybrid hash join, Zeller & Gray 1990 attribution, state machine | `src/backend/executor/nodeHashjoin.c` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/executor/nodeHashjoin.c |
| DuckDB STANDARD_VECTOR_SIZE=2048 | `duckdb/common/vector_size.hpp` | https://raw.githubusercontent.com/duckdb/duckdb/main/src/include/duckdb/common/vector_size.hpp |
| DuckDB DataChunk as unit of vectorized execution | `duckdb/common/types/data_chunk.hpp` | https://raw.githubusercontent.com/duckdb/duckdb/main/src/include/duckdb/common/types/data_chunk.hpp |
| DuckDB attribution to MonetDB/X100, DP Strikes Back, morsel-driven | DuckDB official website | https://duckdb.org/why_duckdb |
| PostgreSQL LLVM JIT, jit_provider GUC, scope, targets | `src/backend/jit/README` | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/jit/README |
| Selinger 1979 (PDF confirmed 16-page scanned image, claims [UNVERIFIED from text]) | Duke CS mirrors | https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf |
| HyPer LLVM compilation paper (PDF confirmed 6-page, CMU 15-721, [UNVERIFIED from text]) | CMU 15-721 | https://15721.courses.cs.cmu.edu/spring2016/papers/p539-neumann.pdf |
| PAX paper "Weaving Relations for Cache Performance" (PDF confirmed, [UNVERIFIED from text]) | UW-Madison | https://research.cs.wisc.edu/multifacet/papers/vldb01_pax.pdf |
| BusTub optimizer rules (NLJ→HashJoin, SortLimit→TopN, etc.) | `src/include/optimizer/optimizer.h` | https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/optimizer/optimizer.h |

---

## 3. Why It's This Way — Constraints That Forced Each Design

**DP join enumeration:**
Finding the globally optimal join plan is NP-hard (equivalent to finding a minimum-cost
binary tree over n leaves). DP over subsets is O(n·2^n) — exponential but exact. At n=12,
~50K subsets, tractable. At n>12, even DP budget is prohibitive → GEQO or greedy heuristics.
The "interesting order" trick keeps DP sound without having to enumerate all orderings explicitly.

**Catalog statistics + cost model:**
Reading actual data per query to pick a plan would defeat the purpose (a full scan to choose
between a scan and an index scan). Catalog statistics let the optimizer make decisions without
touching the data. The tradeoff: stale or skewed statistics cause bad plans (the classic
"row count explosion" or "row count underestimate" bugs). ANALYZE/autovacuum keep statistics
fresh, but they're still samples.

**External sort balanced k-way merge (over polyphase):**
Polyphase optimized for when you have more runs than tapes. In software, a "tape" costs only
memory buffers for pre-reading; so you can have as many tapes as runs. When tapes ≥ runs,
a single merge pass is possible, eliminating all I/O. Replacement selection (hot-cold heap)
was elegant but the average run length benefit (2× work_mem in random input) is marginal vs
the complexity it adds. Quicksort/radix sort is simpler and produces one run per fill.

**Hash join hybrid over grace:**
Pure grace hash join reads/writes every tuple at least twice (partition phase + probe phase).
Hybrid avoids the second read of the first partition by keeping it in memory during partitioning.
The "double" (batch-size doubles on overflow) strategy means the number of batches is always a
power of 2, which lets hash bit addressing remain simple (shift + mask).

**Vectorized over Volcano:**
The bottleneck for analytical queries is not I/O but CPU throughput, specifically instruction
cache pressure and branch mispredictions from generic expression interpreters.
Processing arrays of 2048 values eliminates:
- Per-tuple virtual dispatch (~3-5 indirect branches per operator boundary)
- Per-tuple null checking (check a selection vector once per batch)
- Prevents register spilling (tight loop over contiguous array fits in registers)
A vector of 2048 int64 values = 16KB, fitting in L1 cache (typically 32–64KB).

**Compiled execution over vectorized:**
Vectorized still has inter-operator function calls at batch boundaries. Compiled execution fuses
entire pipelines into one native function. Tradeoffs: compile latency (only worth it for queries
running ≥ seconds); complexity of code generation; portability (LLVM dependency).

**NSM vs DSM choice:**
A page is the unit of I/O. With NSM, each page fetch gets all columns but wastes bandwidth for
column-sparse queries. With DSM, each page fetch gets exactly one column but reconstruction
requires joining N column arrays. PAX splits the difference: within-page column grouping reduces
cache waste without cross-file I/O. The right choice depends entirely on the query mix.

---

## 4. Common Misconceptions to Preempt

1. **"Dynamic programming finds the globally optimal join plan."**
   No. DP finds the optimal plan *within the search space*. PostgreSQL considers only plans
   with at most left-deep+bushy structure (not all bushy), and uses heuristics (join clauses)
   to prune many pairings. Selinger's DP is optimal over what it considers, but the search
   space is pruned.

2. **"GEQO finds an optimal plan for large joins."**
   No. GEQO is a genetic (stochastic) search — it finds *a* plan quickly. The plan quality
   degrades vs DP but the runtime is acceptable. Above 12 tables, DP is too slow.

3. **"Replacement selection always generates 2× memory-sized runs."**
   Only on average for random input. It generates runs of exactly work_mem for sorted input
   (best case = 1 run) and 1-tuple runs for reverse-sorted input. Modern PostgreSQL abandoned
   it in favor of quicksort, which always produces work_mem-sized runs regardless of input order.

4. **"PostgreSQL hash join spills the whole relation when it overflows."**
   No. PostgreSQL uses a lazy doubling strategy. It spills the current hashtable and repartitions
   tuples to batch files as overflow is detected. Only tuples assigned to the current batch are
   in memory at any time.

5. **"Vectorized execution is the same as SIMD."**
   Vectorized execution means processing arrays (vectors) of values per operator call. SIMD is
   a CPU instruction feature that operates on multiple values per instruction. Vectorized execution
   *enables* SIMD but doesn't require it — a vectorized engine without explicit SIMD intrinsics
   still gets auto-vectorization benefits from the compiler for tight loops over arrays.

6. **"Compiled execution (HyPer/Umbra) is always faster than vectorized (DuckDB)."**
   Benchmarks are mixed. Compiled avoids inter-pipeline calls but adds JIT compile latency.
   For short queries, vectorized (no compile cost) wins. For long analytical queries, compiled
   can win on CPU-bound workloads. DuckDB chose vectorized explicitly to avoid JIT complexity.

7. **"Column stores (DSM) are always better for analytics."**
   Only if: (a) queries touch few columns, (b) tuples don't need reconstruction, (c) data volumes
   are large enough that I/O bandwidth is the bottleneck. For small tables or queries that need
   many columns, NSM is competitive. PAX closes the gap for in-memory workloads.

8. **"PostgreSQL's statistics are always up-to-date."**
   No. `pg_class.reltuples/relpages` are updated only by VACUUM/ANALYZE and some DDL. A table
   with 10M rows that was ANALYZED when it had 100K rows will report reltuples=100000 to the
   planner, potentially causing catastrophic plan choices (underestimate → nested-loop join
   over a huge relation).

---

## 5. Best Build-Your-Own Targets

**1. Minimal cost-based optimizer (strongly recommended):**
BusTub's optimizer (`src/include/optimizer/optimizer.h`) implements:
- `OptimizeMergeProjection` — eliminate redundant projections
- `OptimizeMergeFilterNLJ` — push filter into nested-loop join
- `OptimizeNLJAsHashJoin` — rewrite NLJ with equality predicate as HashJoin
- `OptimizeOrderByAsIndexScan` — ORDER BY → index scan if index covers sort key
- `OptimizeSortLimitAsTopN` — Sort(Limit(n)) → TopN heap
- `OptimizeSeqScanAsIndexScan` — point lookup → index scan
- `OptimizeColumnPruning` — prune unneeded columns
Build target: implement these rules in any simple SQL engine. They teach rule-based optimization
without requiring a full cost model.

**2. Two-pass external merge sort:**
Write: generate sorted runs of size M (quicksort in memory); merge-sort runs using priority queue.
Teaches: why merge order matters, buffer management, final-merge-on-the-fly optimization.
Builds on `tuplesort.c` conceptual model; see Knuth vol.3 for theory.

**3. Hash join with overflow:**
Start with in-memory hash join. Add: detect overflow at insert time; dump current hashtable to
temp file; partition remaining tuples; process partitions sequentially.
Teaches: grace/hybrid distinction, power-of-2 batch sizing, why hash bits = batch routing.

**4. Minimal statistics + selectivity estimator:**
Implement `pg_statistic`-style: store MCV list + histogram per column. Write selectivity
estimator for equality/range predicates. Feed into a join cost estimator. Demonstrates the
estimator→cost→plan loop without full optimizer complexity.

**5. Simple vectorized expression evaluator:**
Replace tuple-at-a-time expression eval with array-at-a-time. Implement: comparison operators
working on arrays of int64; selection vector for filtering (mask instead of copying).
Shows: branch elimination, potential for SIMD, why function call overhead matters.

---

## 6. Open Questions / Source Gaps

**6.1 Selinger 1979 paper text:**
The Selinger 1979 SIGMOD paper PDF at the Duke mirror (`selinger-etal-1979.pdf`) is a scanned
image (PDF v1.3, 16 pages). `pdftotext` and `strings` extraction produced no readable text.
The exact formulas for selectivity factors (SF for equi-join, SF for BETWEEN) and the precise
statement of "interesting order" can only be confirmed by reading the scanned image directly.
All Selinger claims in this brief are attributed `[UNVERIFIED from text]` and sourced from
secondary literature (PostgreSQL README, DuckDB docs, CMU 15-445 lecture notes as proxies).

**6.2 MonetDB/X100 CIDR 2005 paper:**
The canonical URL (`www.monetdb.org/Assets/MonetDB-X100-cidr05.pdf`) returned 404. The CS.OU
and MIT/CSAIL mirrors also returned 404. Could not directly fetch and confirm vector-size or
L1-cache claims from primary source. DuckDB's official attribution at `https://duckdb.org/why_duckdb`
is the closest primary-source citation available. Paper DOI: [UNVERIFIED — paper not directly
accessed from any reachable mirror.]

**6.3 HyPer/Neumann 2011 "Efficiently Compiling" paper:**
PDF fetched from CMU 15-721 (200 OK, 6 pages, PDF v1.5) but pdftotext returned empty (likely
Cairo-rendered vector graphics, not selectable text). The produce/consume model and pipeline
fusing mechanism are widely documented in secondary sources but text-level verification from
this PDF failed. Specific claims (e.g., exact IR generation strategy) are `[UNVERIFIED from text]`.

**6.4 PAX paper text:**
`research.cs.wisc.edu/multifacet/papers/vldb01_pax.pdf` returned 200 OK (153KB, PDF v1.2, 10
pages) but is a scanned CCITT fax image. No text extraction possible. The "minipage" layout
within pages is attributed to Ailamaki et al. 2001, consistent across all DB textbooks, but
exact page layout formulas remain `[UNVERIFIED from text]`.

**6.5 DuckDB VLDB 2019 paper:**
`duckdb.org/duckdb-vldb2019.pdf` and CMU mirrors returned 404. Could not verify VLDB 2019
paper claims (exact design decisions, benchmark numbers) directly. DuckDB source code and
official `why_duckdb` page are the primary verification sources used here.

**6.6 Cardinality estimation for multi-join queries:**
This brief covers single-table and one-join selectivity estimation. Multi-join cardinality
estimation (especially for chains/stars) is known to have problems (independent-columns
assumption compounds errors multiplicatively). PostgreSQL's approach beyond extended statistics
(e.g., Bayesian networks, sampling-based estimation for complex joins) is not covered here.
See: Leis et al. "How Good Are Query Optimizers, Really?" (PVLDB 2015) for a benchmark of
this problem — not yet fetched.

**6.7 Umbra vs HyPer architecture differences:**
HyPer uses LLVM for compiled execution. Umbra (its successor at TU Munich) reportedly uses
a different backend (Umbra IR, a custom intermediate representation for faster JIT). The Umbra
paper/design is not covered here. This is relevant for the "compiled execution" cluster.

**6.8 BusTub cardinality estimation:**
BusTub's `EstimatedCardinality()` method signature is present in optimizer.h but the source
was not fetched to verify what statistics it actually uses (table-level reltuples equivalent,
or per-column histograms). Mark as gap.

---

*Brief covers: Selinger/System R DP + interesting orders; PostgreSQL optimizer (README, pathkeys, costsize, pathnode); PostgreSQL statistics (selfuncs, pg_statistic, CREATE STATISTICS); PostgreSQL tuplesort (external sort evolution, state machine, constants); PostgreSQL nodeHashjoin (hybrid hash join, Zeller/Gray, parallel phases); DuckDB vectorized (DataChunk, STANDARD_VECTOR_SIZE=2048, selection vectors); PostgreSQL LLVM JIT (README, targets, design); NSM/DSM/PAX storage models; BusTub optimizer rules. All verified claims link directly to primary source URLs.*
