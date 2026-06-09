# Factcheck Report: Wave 2 Research Files — Sub-courses 04, 05, 06
**Agent:** factchecker-5bc65c  
**Date:** 2026-06-09  
**Method:** Primary-source verification via curl/shell against official repositories, kernel source, language runtimes, and specs. All verdicts are source-backed or explicitly flagged where no primary source was locatable.

---

## Blockers first (UNSUPPORTED / MISATTRIBUTED)

| file | claim | verdict | source link | note |
|---|---|---|---|---|
| `04/_research_ostep-cs162-xv6.md` line 58 | `swtch.S (verified, 14 instructions)` | UNSUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/swtch.S | **Wrong count.** swtch.S has 29 instructions: 14 `sd` (saves) + 14 `ld` (loads) + 1 `ret` = 29. The number 14 is the register count (ra, sp, s0–s11), not the instruction count. The description that follows is correct (saves callee-saved only), but "14 instructions" is factually wrong and will confuse students. |
| `04/_research_linux-performance-kerrisk-gregg.md` line 293, 373 | `35 types enumerated in bpf.h` | UNSUPPORTED | https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/bpf.h | **Wrong count.** Current kernel `enum bpf_prog_type` has **33** entries (BPF_PROG_TYPE_UNSPEC through BPF_PROG_TYPE_NETFILTER). Not 35. |
| `05/_research_production-runtimes.md` line 132 | CPython GC `threshold (default 700)` for generation 0 | NEEDS-SOURCE (version caveat) | https://raw.githubusercontent.com/python/cpython/main/Include/internal/pycore_interp_structs.h | **Stale for main branch.** CPython `main` branch (Python 3.14+) defines `GC_GENERATION_INIT` with `{ .threshold = 2000, }`. The historical value 700 applies to Python 3.12 and 3.13 stable releases but the research cites main-branch source files without specifying a version. Must add version qualification: `(default 700 in CPython ≤3.13; changed to 2000 in CPython 3.14+ main)`. |
| `04/_research_linux-performance-kerrisk-gregg.md` line 420–423 | `99 Hz is prime-relative to common timer frequencies` | NEEDS-SOURCE | https://raw.githubusercontent.com/brendangregg/FlameGraph/master/README.md | **Two problems.** (1) 99 is **not** prime (99 = 3² × 11); the correct term is "co-prime to 100" (gcd(99,100)=1). (2) The FlameGraph README and `flamegraph.pl` do not explain the rationale at all — this is Gregg's verbal/blog explanation, not in the primary repository. The underlying point (avoids aliasing with 10ms timer loops) is sound, but the "prime-relative" phrasing is technically wrong and needs a citable primary source (Gregg's book or blog post). |
| `04/_research_linux-performance-kerrisk-gregg.md` line 282–283 | eBPF bounded loops `allowed with loop bounds provable at verification time since ~Linux 5.3` | NEEDS-SOURCE | https://raw.githubusercontent.com/torvalds/linux/master/Documentation/bpf/verifier.rst | `verifier.rst` only says "First step does DAG check to disallow loops" — it does NOT confirm the version. The ~5.3 attribution is plausible (bounded loop support via verifier landed in 5.3 as part of the BPF loop detection patches) but is not confirmed by the linked primary document. Needs a specific kernel commit or changelog citation. |
| `04/_research_linux-performance-kerrisk-gregg.md` references | RocksDB write amplification `~34` | NEEDS-SOURCE | https://raw.githubusercontent.com/EighteenZi/rocksdb_wiki/master/RocksDB-Tuning-Guide.md | **Off by one.** The RocksDB Tuning Guide explicit calculation gives `1 + 2 + 10 + 10 + 10 = 33`, not 34. Minor but should match the primary source. |

---

## NEEDS-SOURCE (self-flagged [UNVERIFIED] in the research, confirmed unciteable from primary sources in this session)

| file | claim | verdict | source link | note |
|---|---|---|---|---|
| `06/_research_indexes-lsm-bloom.md` lines 64, 370 | SQLite default page size `4096 since SQLite 3.12.0 (2016)` | NEEDS-SOURCE | https://raw.githubusercontent.com/sqlite/sqlite/master/src/sqliteInt.h | Already self-flagged [UNVERIFIED] in research. SQLite canonical source (`SQLITE_DEFAULT_PAGE_SIZE`) could not be confirmed from these file paths; the claim is widely reported but requires a direct source (SQLite changelog or `btreeInt.h` constant). |
| `06/_research_probabilistic-distributed-queues.md` line 182 | Redis Cluster `gossip message with slot assignment fits in 2KB` | NEEDS-SOURCE | — | Self-flagged [UNVERIFIED exact wording, source: redis.io design doc]. No primary source found in Redis source or docs for this specific sizing rationale. |
| `06/_research_probabilistic-distributed-queues.md` line 126 | Disruptor `~25ns per message vs ~100ns for ArrayBlockingQueue` | NEEDS-SOURCE | — | Self-flagged [UNVERIFIED: exact benchmark numbers; paper not fetchable]. The LMAX tech note PDF is not publicly fetchable; numbers cannot be verified without the paper. |
| `06/_research_probabilistic-distributed-queues.md` line 420 | `exact DynamoDB architecture` re consistent hashing | NEEDS-SOURCE | — | Self-flagged [UNVERIFIED: exact DynamoDB architecture]. |

---

## SUPPORTED (verified against primary sources)

### Sub-course 04: OS Internals

| file | claim | verdict | source link | note |
|---|---|---|---|---|
| `04/_research_ostep-cs162-xv6.md` | `MAXVA = 1L << (9+9+9+12-1)` = 2^38 = 256 GB | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/riscv.h | Exact macro confirmed: `#define MAXVA (1L << (9 + 9 + 9 + 12 - 1))` |
| `04/_research_ostep-cs162-xv6.md` | `NPROC=64, NCPU=8, NOFILE=16` | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/param.h | All confirmed from param.h |
| `04/_research_ostep-cs162-xv6.md` | `NBUF = MAXOPBLOCKS*3 = 30` | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/param.h | `#define NBUF (MAXOPBLOCKS * 3)`, MAXOPBLOCKS=10 → NBUF=30  |
| `04/_research_ostep-cs162-xv6.md` | `kfree() fills with 0x01; kalloc() fills with 0x05` | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/kalloc.c | `memset(pa, 1, PGSIZE)` in kfree; `memset((char *)r, 5, PGSIZE)` in kalloc |
| `04/_research_ostep-cs162-xv6.md` | `KSTACK(p) = TRAMPOLINE - ((p)+1)*2*PGSIZE` | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/memlayout.h | Exact macro confirmed |
| `04/_research_ostep-cs162-xv6.md` | `TRAPFRAME = TRAMPOLINE - PGSIZE` | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/memlayout.h | Confirmed |
| `04/_research_ostep-cs162-xv6.md` | `scause == 8` for U-mode ECALL (syscall) | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/trap.c | `if (r_scause() == 8)` confirmed in usertrap() |
| `04/_research_ostep-cs162-xv6.md` | xv6 fs: `BSIZE=1024`, `NDIRECT=12`, `addrs[NDIRECT+1]` (= addrs[13]), `MAXFILE=268` | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/fs.h | All confirmed: BSIZE=1024, NDIRECT=12, NINDIRECT=BSIZE/sizeof(uint)=256, MAXFILE=268 |
| `04/_research_ostep-cs162-xv6.md` | swtch saves callee-saved only (ra, sp, s0–s11) per ABI | SUPPORTED | https://raw.githubusercontent.com/mit-pdos/xv6-riscv/riscv/kernel/swtch.S | Confirmed — only `sd`/`ld` of ra, sp, s0–s11. **Note: The instruction *count* (incorrectly stated as 14) is a separate blocker above.** |
| `04/_research_linux-performance-kerrisk-gregg.md` | `CFS merged in Linux 2.6.23` | SUPPORTED | https://raw.githubusercontent.com/torvalds/linux/master/Documentation/scheduler/sched-design-CFS.rst | "merged in Linux 2.6.23" — exact quote |
| `04/_research_linux-performance-kerrisk-gregg.md` | `EEVDF transitioning/replacing CFS as default in Linux 6.6` | SUPPORTED | https://raw.githubusercontent.com/torvalds/linux/master/Documentation/scheduler/sched-eevdf.rst | "Linux kernel began transitioning to EEVDF in version 6.6"; CFS docs say "making room for EEVDF"  |
| `04/_research_linux-performance-kerrisk-gregg.md` | `sysctl_sched_base_slice` (was `sched_min_granularity_ns`) | SUPPORTED | https://raw.githubusercontent.com/torvalds/linux/master/kernel/sched/fair.c | `unsigned int sysctl_sched_base_slice = 700000ULL;` confirmed |
| `04/_research_linux-performance-kerrisk-gregg.md` | epoll interest list backed by **red-black tree** | SUPPORTED | https://raw.githubusercontent.com/torvalds/linux/master/fs/eventpoll.c | `#include <linux/rbtree.h>`, `struct rb_root_cached rbr`, `rb_entry` all confirmed |
| `04/_research_linux-performance-kerrisk-gregg.md` | epoll LT vs ET, interest list / ready list terminology | SUPPORTED | https://raw.githubusercontent.com/mkerrisk/man-pages/master/man7/epoll.7 | "interest list" and "ready list" are the exact terms in the man page |
| `04/_research_linux-performance-kerrisk-gregg.md` | FlameGraph uses 99 Hz (not 100 Hz) | SUPPORTED | https://raw.githubusercontent.com/brendangregg/FlameGraph/master/README.md | `perf record -F 99` in README examples  |

### Sub-course 05: Language Runtime Internals

| file | claim | verdict | source link | note |
|---|---|---|---|---|
| `05/_research_production-runtimes.md` | CPython `struct _object`: `ob_refcnt (uint32) + ob_overflow (uint16) + ob_flags (uint16) + ob_type*` (non-GIL, little-endian, 64-bit) | SUPPORTED | https://raw.githubusercontent.com/python/cpython/main/Include/object.h | Exact struct layout confirmed from `#ifndef Py_GIL_DISABLED` branch. Note big-endian reverses flags/overflow order. |
| `05/_research_production-runtimes.md` | CPython free-threaded (Py_GIL_DISABLED) layout: `ob_tid + ob_flags + ob_mutex + ob_gc_bits + ob_ref_local + ob_ref_shared + ob_type` | SUPPORTED | https://raw.githubusercontent.com/python/cpython/main/Include/object.h | Exact struct layout confirmed for `#else` branch. |
| `05/_research_production-runtimes.md` | CPython GIL: `DEFAULT_INTERVAL = 5000` (µs = 5ms) | SUPPORTED | https://raw.githubusercontent.com/python/cpython/main/Python/ceval_gil.c | `#define DEFAULT_INTERVAL 5000` confirmed |
| `05/_research_production-runtimes.md` | CPython GIL: `FORCE_SWITCHING` compile flag exists | SUPPORTED | https://raw.githubusercontent.com/python/cpython/main/Python/ceval_gil.c | `#ifdef FORCE_SWITCHING` present in multiple locations |
| `05/_research_production-runtimes.md` | CPython `eval_breaker` is `uintptr_t` | SUPPORTED | https://raw.githubusercontent.com/python/cpython/main/Python/ceval_gil.c | `copy_eval_breaker_bits(uintptr_t *from, uintptr_t *to, uintptr_t mask)` |
| `05/_research_production-runtimes.md` | CPython GC: `NUM_GENERATIONS = 3` | SUPPORTED | https://raw.githubusercontent.com/python/cpython/main/Include/internal/pycore_interp_structs.h | `#define NUM_GENERATIONS 3` confirmed |
| `05/_research_production-runtimes.md` | CPython GC thresholds: `(700, 10, 10)` for Python ≤3.13 | SUPPORTED (with caveat) | https://docs.python.org/3.13/library/gc.html | Historical default 700,10,10 is consistent with docs for Python ≤3.13. **However**: CPython `main` (3.14+) has changed this to `{ .threshold = 2000, }` — see blocker above. The research must add version qualifier. |
| `05/_research_production-runtimes.md` | V8: every `HeapObject` has a `Map` pointer as first field | SUPPORTED | https://raw.githubusercontent.com/v8/v8/main/src/objects/heap-object-inl.h | `Tagged<Map> HeapObject::map()` method and `MapField::Relaxed_Load_Map_Word` confirm Map is always present; standard V8 architecture. |
| `05/_research_production-runtimes.md` | libuv event loop phase order: timers → pending → io_poll → check → close | SUPPORTED | https://raw.githubusercontent.com/libuv/libuv/v1.x/src/unix/core.c | `uv__run_timers`, `uv__run_pending`, `uv__io_poll`, `uv__run_check`, `uv__run_closing_handles` confirmed in order |
| `05/_research_production-runtimes.md` | HotSpot CompLevel: 0=interpreter, 1=C1 simple, 2=C1+counters, 3=C1+counters+MDO, 4=C2 | SUPPORTED | https://raw.githubusercontent.com/openjdk/jdk/master/src/hotspot/share/compiler/compilerDefinitions.hpp | Exact enum confirmed with comments |
| `05/_research_production-runtimes.md` | HotSpot safepoint polling page mechanism | SUPPORTED | https://raw.githubusercontent.com/openjdk/jdk/master/src/hotspot/share/runtime/safepointMechanism.hpp | `_polling_page`, `_poll_page_armed_value`, `_poll_page_disarmed_value` all confirmed |

### Sub-course 06: Data Structures for Systems

| file | claim | verdict | source link | note |
|---|---|---|---|---|
| `06/_research_indexes-lsm-bloom.md` | LevelDB `write_buffer_size = 4MB` (memtable/log flush threshold) | SUPPORTED | https://raw.githubusercontent.com/google/leveldb/main/include/leveldb/options.h | `size_t write_buffer_size = 4 * 1024 * 1024` |
| `06/_research_indexes-lsm-bloom.md` | LevelDB target SST file size = 2MB | SUPPORTED | https://raw.githubusercontent.com/google/leveldb/main/include/leveldb/options.h | `size_t max_file_size = 2 * 1024 * 1024` |
| `06/_research_indexes-lsm-bloom.md` | LevelDB impl.md: log 4MB, SST 2MB, level 1=10MB | SUPPORTED | https://raw.githubusercontent.com/google/leveldb/main/doc/impl.md | "4MB by default", "a new level-1 file for every 2MB of data", "all the level-1 files (10MB)" |
| `06/_research_indexes-lsm-bloom.md` | LevelDB Bloom `k = bits_per_key * 0.69` (≈ ln 2), clamped 1–30 | SUPPORTED | https://raw.githubusercontent.com/google/leveldb/main/util/bloom.cc | `k_ = static_cast<size_t>(bits_per_key * 0.69); if (k_ < 1) k_ = 1; if (k_ > 30) k_ = 30;` |
| `06/_research_indexes-lsm-bloom.md` | LevelDB Bloom uses double-hashing from [Kirsch, Mitzenmacher 2006] | SUPPORTED | https://raw.githubusercontent.com/google/leveldb/main/util/bloom.cc | Comment: `// See analysis in [Kirsch,Mitzenmacher 2006].` Technique: `delta = (h >> 17) | (h << 15)` |
| `06/_research_indexes-lsm-bloom.md` | RocksDB `write_buffer_size = 64MB` | SUPPORTED | https://raw.githubusercontent.com/facebook/rocksdb/main/include/rocksdb/options.h | `size_t write_buffer_size = 64 << 20;` |
| `06/_research_indexes-lsm-bloom.md` | RocksDB `level0_file_num_compaction_trigger = 4` | SUPPORTED | https://raw.githubusercontent.com/facebook/rocksdb/main/include/rocksdb/options.h | `int level0_file_num_compaction_trigger = 4;` |
| `06/_research_indexes-lsm-bloom.md` | RocksDB `max_bytes_for_level_base = 256MB` | SUPPORTED | https://raw.githubusercontent.com/facebook/rocksdb/main/include/rocksdb/options.h | `uint64_t max_bytes_for_level_base = 256 * 1048576;` |
| `06/_research_indexes-lsm-bloom.md` | RocksDB `target_file_size_base = 64MB` | SUPPORTED | https://raw.githubusercontent.com/facebook/rocksdb/main/include/rocksdb/advanced_options.h | `uint64_t target_file_size_base = 64 * 1048576;` with comment `// Default: 64MB.` |
| `06/_research_indexes-lsm-bloom.md` | PostgreSQL nbtree: L&Y algorithm, right-link, high key | SUPPORTED | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README | "correct implementation of Lehman and Yao's high-concurrency B-tree…", "right-link pointer", "high key" |
| `06/_research_indexes-lsm-bloom.md` | PostgreSQL nbtree: TID as tiebreaker for unique keys | SUPPORTED | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README | "heap TID as a tiebreaker attribute. Logical duplicates are sorted in heap TID order." |
| `06/_research_indexes-lsm-bloom.md` | PostgreSQL nbtree: left-sibling link (extension beyond original L&Y) | SUPPORTED | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README | "we also store a 'left sibling' link" confirmed; left-link used for backward scans |
| `06/_research_indexes-lsm-bloom.md` | PostgreSQL nbtree: suffix truncation | SUPPORTED | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README | "The Postgres implementation of suffix truncation…" confirmed |
| `06/_research_probabilistic-distributed-queues.md` | Redis `ZSKIPLIST_MAXLEVEL=32`, `ZSKIPLIST_P=0.25` | SUPPORTED | https://raw.githubusercontent.com/redis/redis/unstable/src/server.h | Exact defines confirmed |
| `06/_research_probabilistic-distributed-queues.md` | Redis skip list level generation: `while(random() < threshold) level += 1` | SUPPORTED | https://raw.githubusercontent.com/redis/redis/unstable/src/t_zset.c | `static const int threshold = ZSKIPLIST_P*RAND_MAX; while (random() < threshold) level += 1;` |
| `06/_research_probabilistic-distributed-queues.md` | Redis skip list: `span` at `level[0]` repurposed for `zskiplistNodeInfo{sdsoffset, levels}` | SUPPORTED | https://raw.githubusercontent.com/redis/redis/unstable/src/server.h + t_zset.c | struct definition + `zslSetNodeInfo`/`zslGetNodeInfo` using `node->level[0].span` confirmed; static_assert verifies fit |
| `06/_research_probabilistic-distributed-queues.md` | Redis Cluster: 16384 slots, `crc16(key) & 0x3FFF` | SUPPORTED | https://raw.githubusercontent.com/redis/redis/unstable/src/cluster.h | `CLUSTER_SLOTS = (1<<CLUSTER_SLOT_MASK_BITS)` (16384), `crc16(key,keylen) & 0x3FFF` confirmed |
| `06/_research_probabilistic-distributed-queues.md` | Redis HLL: `HLL_P=14`, `HLL_Q=50`, `HLL_REGISTERS=16384`, `HLL_BITS=6`, `HLL_ALPHA_INF=0.72134…` | SUPPORTED | https://raw.githubusercontent.com/redis/redis/unstable/src/hyperloglog.c | All constants confirmed exactly |
| `06/_research_probabilistic-distributed-queues.md` | HLL standard error `1.04/√16384 ≈ 0.81%` | SUPPORTED | Derived from confirmed HLL_REGISTERS=16384 | √16384=128; 1.04/128=0.008125≈0.81%  |
| `06/_research_probabilistic-distributed-queues.md` | Disruptor `Sequence`: 56B pad + 8B `long value` + 56B pad = 120B | SUPPORTED | https://raw.githubusercontent.com/LMAX-Exchange/disruptor/master/src/main/java/com/lmax/disruptor/Sequence.java | 7×8B LhsPadding + 8B value + 7×8B RhsPadding = 120B exactly. `INITIAL_VALUE = -1L`, `VarHandle VALUE_FIELD` all confirmed |
| `06/_research_probabilistic-distributed-queues.md` | Disruptor `RingBuffer`: `BUFFER_PAD=32`, `bufferSize` power-of-2 enforced, `indexMask = bufferSize-1`, slot = `entries[BUFFER_PAD + (seq & indexMask)]` | SUPPORTED | https://raw.githubusercontent.com/LMAX-Exchange/disruptor/master/src/main/java/com/lmax/disruptor/RingBuffer.java | All confirmed; throws if not power-of-2 |
| `06/_research_probabilistic-distributed-queues.md` | Disruptor `MultiProducerSequencer`: `availableBuffer` is `int[]` tracking publication flags | SUPPORTED | https://raw.githubusercontent.com/LMAX-Exchange/disruptor/master/src/main/java/com/lmax/disruptor/MultiProducerSequencer.java | `private final int[] availableBuffer;` + VarHandle ops (setRelease/getAcquire) confirmed |

---

## Recommendations for file edits

### Immediate blockers (must fix before promotion):

**`04/_research_ostep-cs162-xv6.md` line 58:**
```
WRONG:  swtch.S (verified, 14 instructions)
FIX:    swtch.S (verified, 29 instructions: 14 sd saves + 14 ld loads + 1 ret)
```
The "14" should be noted as register count, not instruction count. The description that follows is correct.

**`04/_research_linux-performance-kerrisk-gregg.md` line 293/373:**
```
WRONG:  35 types enumerated in bpf.h
FIX:    33 types enumerated in bpf.h (BPF_PROG_TYPE_UNSPEC through BPF_PROG_TYPE_NETFILTER, as of kernel 6.x)
```
Note: this count can shift with new kernel versions; recommend saying "currently 33 as of kernel 6.x" rather than a bare number.

**`05/_research_production-runtimes.md` line 132:**
```
WRONG:  threshold (default 700)   [without version context]
FIX:    threshold (default 700 in CPython ≤3.13; changed to 2000 in CPython 3.14+ main branch)
```
The research cites `main` branch sources throughout but states the 700 default without acknowledging it was changed in main. Add version caveat.

**`04/_research_linux-performance-kerrisk-gregg.md` lines 420–423:**
```
WRONG:  "99 Hz is prime-relative to common timer frequencies"
FIX:    "99 Hz is co-prime to 100 Hz (gcd(99,100)=1), avoiding aliasing with 10ms timer
        periods. Note: 99 = 3²×11 is not itself prime; the property that matters is 
        that it shares no common factor with 100."
```
Also add a primary citation: if Gregg's blog post or BPF Performance Tools book URL is accessible, cite it. If not, note this as NEEDS-SOURCE.

### Wording softening (NEEDS-SOURCE, not blockers if presented as approximate):

**`04/_research_linux-performance-kerrisk-gregg.md` line 282–283** (eBPF bounded loops ~5.3):  
Acceptable to keep with qualifier: add "[approximate; confirm specific commit]" or find the specific kernel commit sha and link it.

**`04/_research_linux-performance-kerrisk-gregg.md`** (write amplification ~34):  
Change to "~33" to match the RocksDB Tuning Guide's explicit calculation of `1 + 2 + 10 + 10 + 10 = 33`.

### Leave as-is (self-flagged [UNVERIFIED], gap acknowledged):
- SQLite default page size (line 64, 370 in `06/_research_indexes-lsm-bloom.md`) — already flagged; leave as gap
- Redis Cluster gossip 2KB sizing — already flagged; leave as gap
- Disruptor ~25ns benchmark — already flagged; leave as gap
- V8 Maglev threshold numbers — already flagged [UNVERIFIED]; leave as gap

---

## Methodology notes

- All xv6 claims verified against `mit-pdos/xv6-riscv` at branch `riscv` (current HEAD)
- CPython claims verified against `python/cpython` at `main` branch unless otherwise noted
- Redis claims verified against `redis/redis` at `unstable` branch
- RocksDB claims verified against `facebook/rocksdb` at `main` branch
- Linux kernel claims verified against `torvalds/linux` at `master`
- Disruptor claims verified against `LMAX-Exchange/disruptor` at `master`
- V8 claims verified against `v8/v8` at `main`
- LevelDB claims verified against `google/leveldb` at `main`
- PostgreSQL claims verified against `postgres/postgres` at `master`
- libuv claims verified against `libuv/libuv` at `v1.x`
- OpenJDK claims verified against `openjdk/jdk` at `master`
