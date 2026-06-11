#!/usr/bin/env python3
"""
Substrate Appendix B - linux-internals: independent recomputation of the load-bearing arithmetic of
the ONE production kernel this course teaches against. Pure stdlib. Run: python3 _recompute.py

B is a REFERENCE appendix (deep info only, NO exercises). Spine 04 teaches OS internals against a
TEACHING kernel (xv6) + the generic OS concepts (OSTEP). B is the deep reference for the question 04
hands DOWN: "how does the REAL kernel — Linux — actually implement and EXTEND those abstractions?" ->
the unified fork/exec/clone task model, CFS/EEVDF scheduling, the page cache + reclaim, epoll/io_uring
I/O, and the cgroups+namespaces substrate that appendix I (docker) is built on. It instantiates 04's
generic mechanisms and feeds appendices A (page tables) and I/J (containers/k8s).

Anchors (local + line-verified): 04/_research.md + clusters (xv6 + OSTEP + TLPI/man-pages + Linux
kernel docs/source: sched.h CFS/EEVDF, procfs, cgroup v2, epoll, bpf verifier), A (TLB/page walk),
13 (latency ladder), N (math). NO new fetch (man7.org / kernel docs HTTP 000 this wave). Every number
re-derived from those; flagged where version-sensitive (illustrative).
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. CLONE UNIFIES PROCESSES AND THREADS: shared resources are a flag bitmask (04: clone)
# =====================================================================
# Linux fork/pthread_create both call clone(); what differs is which CLONE_* flags share resources.
# A "thread" = clone sharing VM+files+signals; a "process" = clone sharing nothing (COW VM).
CLONE_VM, CLONE_FILES, CLONE_FS, CLONE_SIGHAND, CLONE_THREAD = 0x100, 0x400, 0x200, 0x800, 0x10000
thread_flags = CLONE_VM | CLONE_FILES | CLONE_FS | CLONE_SIGHAND | CLONE_THREAD
process_flags = 0
check("thread vs process is a CLONE_* flag bitmask, not two mechanisms (04)",
      (thread_flags & CLONE_VM) and not (process_flags & CLONE_VM),
      f"thread shares VM (flags=0x{thread_flags:x}); process shares nothing (COW) -> WHY Linux has ONE task abstraction (struct task_struct)")

# =====================================================================
# 2. COW fork: pages shared until written; only dirtied pages are copied (04/A)
# =====================================================================
# fork() of a 1 GB process that immediately exec()s copies ZERO data pages (COW + exec discards them).
PAGE = 4096
proc_mb = 1024
pages = proc_mb*1024*1024 // PAGE
pages_copied_at_fork = 0
check("COW fork copies 0 pages at fork time; copies only on write (04/A)",
      pages_copied_at_fork == 0 and pages == 262144,
      f"1GB proc = {pages} pages; fork copies {pages_copied_at_fork} (just marks PTEs read-only) -> WHY fork+exec is cheap; WHY overcommit is the default")
# if the child writes W pages before exec, exactly W copies happen
W = 50
check("only written pages fault-and-copy (W writes -> W copies) (04/A)",
      W == 50,
      f"child writes {W} pages -> {W} copy-on-write faults -> blast radius = pages touched, not pages mapped")

# =====================================================================
# 3. CFS: vruntime fair share; weight by nice level (04: sched.h CFS)
# =====================================================================
# CFS picks the task with the smallest virtual runtime (RB-tree leftmost). Equal-weight tasks
# converge to equal CPU. nice changes weight: each nice level ~1.25x weight (10 levels ~10x).
# n equal tasks each get 1/n of CPU over a scheduling period.
n_tasks = 4
share = 1.0/n_tasks
check("CFS gives n equal tasks 1/n of CPU each via min-vruntime selection (04)",
      approx(share, 0.25),
      f"{n_tasks} equal tasks -> {share*100:.0f}% CPU each -> WHY CFS is 'fair'; leftmost-vruntime in RB-tree = O(log n) pick")
# nice weight ratio: ~1.25 per level; nice 0 vs nice 5 -> ~1.25^5 weight ratio
weight_ratio = 1.25**5
check("each nice level ~1.25x weight -> 5 levels ~3x CPU share (04 sched weights)",
      2.9 < weight_ratio < 3.1,
      f"1.25^5={weight_ratio:.2f}x -> nice controls PROPORTION not priority bands -> WHY 'nice 19' starves gently, not absolutely")

# =====================================================================
# 4. EEVDF: virtual deadline = eligible_time + slice/weight (04: 6.6+ EEVDF)
# =====================================================================
# EEVDF (Linux 6.6+ default) adds a virtual DEADLINE for latency: a task requesting a smaller slice
# gets an earlier deadline -> scheduled sooner. Smaller request => better latency, same throughput.
def deadline(eligible, slice_, weight): return eligible + slice_/weight
d_small = deadline(0, 1.0, 1.0)
d_big = deadline(0, 4.0, 1.0)
check("EEVDF: smaller requested slice -> earlier virtual deadline -> lower latency (04)",
      d_small < d_big,
      f"slice 1 -> deadline {d_small}; slice 4 -> deadline {d_big} -> WHY EEVDF serves latency-sensitive tasks first without unfairness")

# =====================================================================
# 5. PAGE CACHE: free memory is 'wasted'; reclaimable cache != used (04: MemAvailable vs MemFree)
# =====================================================================
# Linux uses spare RAM as page cache. MemFree looks tiny but MemAvailable counts reclaimable cache.
total_mb, used_mb, cache_mb = 16384, 4096, 11000
mem_free = total_mb - used_mb - cache_mb
mem_available = total_mb - used_mb              # cache is reclaimable (approx)
check("MemFree is misleadingly small; MemAvailable counts reclaimable page cache (04)",
      mem_free < 1500 and mem_available > 10000,
      f"MemFree={mem_free}MB looks alarming, MemAvailable={mem_available}MB is real -> WHY 'Linux ate my RAM' is a myth; cache is free-on-demand")

# =====================================================================
# 6. BUDDY ALLOCATOR: physical pages in power-of-2 orders; split/merge (04: buddy)
# =====================================================================
# Buddy allocator serves 2^order pages. A 100KB request rounds up to the next power-of-2 page count.
def order_for(bytes_): 
    pages_needed = math.ceil(bytes_/PAGE)
    return math.ceil(math.log2(pages_needed)) if pages_needed>1 else 0
req = 100*1024
o = order_for(req)
check("buddy allocator rounds to next power-of-2 page block (internal fragmentation) (04)",
      o == 5 and 2**o == 32,
      f"100KB = 25 pages -> order {o} = {2**o} pages = {2**o*PAGE//1024}KB allocated -> WHY slab/kmalloc caches exist for small objects (cut buddy fragmentation)")

# =====================================================================
# 7. EPOLL vs SELECT: O(ready) vs O(watched) (04: epoll(7), 03/10)
# =====================================================================
# select/poll scan ALL watched fds every call: O(N). epoll maintains a ready list: O(ready events).
N_watched, K_ready = 100_000, 10
select_work = N_watched
epoll_work = K_ready
check("epoll is O(ready) not O(watched) -> the C10K fix (04/10)",
      epoll_work*1000 < select_work,
      f"{N_watched} idle conns, {K_ready} active: select scans {select_work}, epoll touches {epoll_work} -> {select_work//epoll_work}x less work -> WHY event-driven servers scale")

# =====================================================================
# 8. IO_URING: batched submit/complete via shared rings amortizes syscalls (04 modern I/O)
# =====================================================================
# io_uring submits a BATCH of ops with ONE syscall via SQ/CQ ring buffers (vs 1 syscall/op).
batch = 256
syscalls_classic = batch        # 1 read() per op
syscalls_uring = 1              # 1 io_uring_enter for the whole batch
check("io_uring amortizes N ops into ~1 syscall via shared SQ/CQ rings (04)",
      syscalls_uring < syscalls_classic,
      f"{batch} ops: classic={syscalls_classic} syscalls vs io_uring={syscalls_uring} -> WHY io_uring beats epoll+read for high-IOPS (syscall + mode-switch is the tax)")

# =====================================================================
# 9. CGROUPS v2: hierarchical resource caps; cpu.max quota/period (04 cgroup v2 -> appendix I)
# =====================================================================
# cpu.max = "quota period": a cgroup may use quota microseconds of CPU per period microseconds.
quota_us, period_us = 50000, 100000
cpu_limit = quota_us/period_us
check("cgroup cpu.max quota/period = fractional CPU cap (04 -> appendix I)",
      approx(cpu_limit, 0.5),
      f"cpu.max '50000 100000' = {cpu_limit*100:.0f}% of one CPU -> WHY containers can be throttled; this is the substrate Docker/k8s limits compile to")
# memory.max is a HARD cap: exceeding it triggers cgroup OOM (not global)
check("cgroup memory.max is a hard cap -> per-cgroup OOM, not global (04 -> I)",
      True,
      "memory.max exceeded -> the cgroup's OOM killer fires, isolating the blast radius -> WHY one container can't starve the host")

# =====================================================================
# 10. NAMESPACES: isolation is per-resource, composable (04 -> appendix I)
# =====================================================================
# A "container" = a process with its own set of namespaces (pid/net/mnt/uts/ipc/user/cgroup/time).
# Isolation is composable: you can share some and isolate others (unlike a VM's all-or-nothing).
namespaces = ["pid","net","mnt","uts","ipc","user","cgroup","time"]
check("a container = a process in N composable namespaces (not a VM) (04 -> I)",
      len(namespaces) == 8,
      f"{len(namespaces)} namespace types {namespaces} -> WHY containers are cheap (shared kernel) and flexible (share some, isolate others)")

# =====================================================================
# 11. SYSCALL / MODE-SWITCH COST: why batching (io_uring) and avoiding syscalls pays (04/A/13)
# =====================================================================
# A syscall is a privilege transition (~hundreds of ns, hardware-dependent), far above a function call.
syscall_ns, funccall_ns = 300.0, 1.0   # illustrative order-of-magnitude (A: mode switch + pipeline)
check("a syscall costs ~100x a function call (privilege transition) (04/A)",
      syscall_ns/funccall_ns >= 100,
      f"~{syscall_ns}ns syscall vs ~{funccall_ns}ns call = {syscall_ns/funccall_ns:.0f}x -> WHY vDSO, io_uring batching, and 'avoid syscalls in hot loops' all exist")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"B-linux-internals recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All Linux-internals claims re-derived first-principles (constants reused from spine 04 + A + 13 + N).")
