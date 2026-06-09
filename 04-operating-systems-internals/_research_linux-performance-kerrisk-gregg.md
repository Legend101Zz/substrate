# Research Brief: TLPI + Love LKD + Brendan Gregg Systems Performance
## Sub-course 04 — Operating Systems Internals
## Researcher: researcher-9d6be7 | Phase 1 | 2026-06-09

---

## Source cluster
- Kerrisk, *The Linux Programming Interface* (TLPI, 2010, No Starch) — the canonical POSIX/Linux
  syscall reference; man-pages project (mkerrisk/man-pages GitHub) as primary-source proxy.
- Robert Love, *Linux Kernel Development* 3rd ed (2010, Addison-Wesley) — Linux scheduler,
  memory management, VFS, block layer internals. Cross-checked against Linux kernel source
  (github.com/torvalds/linux) and Documentation/.
- Brendan Gregg, *Systems Performance* 2nd ed (2020) + *BPF Performance Tools* (2019) +
  FlameGraph (github.com/brendangregg/FlameGraph) + perf-tools (github.com/brendangregg/perf-tools).

Primary sources read directly: mkerrisk/man-pages — epoll_wait.2, epoll_ctl.2, epoll.7,
mmap.2, fork.2, signal.7, perf_event_open.2, proc.5; linux/torvalds — sched-design-CFS.rst,
sched-eevdf.rst, filesystems/proc.rst, admin-guide/mm/concepts.rst, admin-guide/mm/pagemap.rst,
admin-guide/sysctl/vm.rst, admin-guide/cgroup-v2.rst, trace/ftrace.rst, trace/events.rst,
bpf/verifier.rst, core-api/memory-allocation.rst, perf-security.rst, sched.h;
brendangregg — FlameGraph/README.md, flamegraph.pl, perf-tools/README.md,
bpf-perf-tools-book/README.md; bpftrace/docs/language.md; iovisor/bcc/README.md.
brendangregg.com blocked at Walmart proxy; all Gregg mechanisms verified via GitHub
repos and kernel docs instead.

---

## 1. Key Mechanisms — Deep and Precise

### 1.1 The Linux Process Model and POSIX Interface (TLPI)

**Forcing constraint:** POSIX standardizes the observable process interface, not the
kernel's implementation. xv6 is not POSIX-compliant; Linux's interface adds ~200 additional
syscalls and semantics that real software depends on.

**fork() semantics (man-pages fork.2, verified):** Creates child that is an exact duplicate
of parent except: own PID; parent PID = parent's PID; child gets its own copy of parent's
*memory spaces* — COW in practice (not a guarantee of the interface, but de-facto on Linux);
child does NOT inherit parent's memory locks (mlock); file descriptors are duplicated (shared
underlying open-file descriptions, NOT independent copies — crucial for offset sharing);
signal handlers inherited but pending signals cleared; timer (setitimer) not inherited.

**execve() semantics:** Replaces process image. All text/data/stack replaced. File descriptors
with FD_CLOEXEC set are closed; others remain open. Signal handlers reset to default (disposition
cannot survive exec since handler code is gone); blocked mask is preserved.

**Linux process states (include/linux/sched.h, verified):**
- TASK_RUNNING = 0x0 — on runqueue OR actively running (not same as userland "running")
- TASK_INTERRUPTIBLE = 0x1 — sleeping, wake on signal or event
- TASK_UNINTERRUPTIBLE = 0x2 — sleeping, wake on event only (not signal — the D-state in top)
- TASK_KILLABLE = TASK_WAKEKILL | TASK_UNINTERRUPTIBLE — wakes on fatal signals only
- EXIT_ZOMBIE = 0x20 — exited, not yet reaped (parent hasn't called wait())
- TASK_DEAD = 0x80 — reaping complete

The critical distinction: a process in TASK_RUNNING may be *waiting on the runqueue* (not
executing). "R" in ps/top means runnable, not necessarily burning CPU.

**Threads (clone2, pthreads):** Linux implements threads as tasks sharing resources via
CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND flags. No separate "thread" concept in the
kernel — all scheduling entities are tasks. POSIX thread ID (tid) != kernel PID (tid from
gettid()). Threads within a process share the same TGID (Thread Group ID) = the PID seen by
userland.

### 1.2 Signals — POSIX Delivery Model (TLPI/man-pages signal.7)

**Forcing constraint:** Hardware exceptions (SIGSEGV, SIGBUS, SIGFPE) must be delivered to
the faulting process; software events (SIGCHLD, SIGPIPE, SIGTERM) need an asynchronous
delivery mechanism. Both share the signal machinery but have very different sources.

**Signal disposition:** per-process (not per-thread) attribute. Three choices: default action
(Term/Core/Stop/Cont/Ign per signal); SIG_IGN; or custom handler installed via sigaction(2).
SIGKILL and SIGSTOP cannot be caught, blocked, or ignored — they are the kernel's
unconditional override (verified: signal.7).

**Signal mask and pending signals (signal.7, verified):** Each thread has its own signal mask
(sigprocmask/pthread_sigmask). A blocked signal is *pending* (queued at most once for standard
signals; real-time signals queue multiple). On every transition from kernel to user mode, the
kernel checks for pending unblocked signals and delivers them before returning. This is WHY
slow system calls (read, select, epoll_wait) can be interrupted by signals — the kernel checks
before completing the return.

**SA_RESTART flag (signal.7, verified):** Without it, slow syscalls return EINTR on signal.
With SA_RESTART, many (but not all) syscalls are automatically restarted by glibc. Not all
syscalls support restart (epoll_wait does; nanosleep does not — it returns EINTR with remaining
time). EINTR handling is a common portability pitfall.

**Real-time signals (SIGRTMIN..SIGRTMAX):** Queue multiple instances (unlike standard signals
which merge). Ordered by signal number on delivery. Carry a payload (siginfo_t with si_value).

### 1.3 Virtual Memory: mmap, Anonymous Memory, Overcommit (TLPI/kernel docs)

**Forcing constraint:** Physical RAM is finite and shared. Virtual address spaces must be lazy
(pages allocated only on access), shared where possible (file mappings, COW), and protected
from each other. mmap is the unified interface for all of this.

**mmap() interface (mmap.2, verified):**
`void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);`
Prot: PROT_READ/WRITE/EXEC/NONE. Key flags: MAP_SHARED (writes propagate to file + other
mappers), MAP_PRIVATE (COW — writes go to private copy), MAP_ANONYMOUS (no fd, zeroed pages).
MAP_PRIVATE|MAP_ANONYMOUS = malloc backing. MAP_SHARED|fd = file-backed page cache sharing.
After mmap() returns, fd can be closed — mapping outlives it. Offset must be page-aligned.

**Anonymous memory (kernel mm/concepts.rst, verified):** Not backed by filesystem. Implicitly
created for stack + heap, or via MAP_ANONYMOUS mmap. Read access → zero page (shared
physical zero page, no allocation). Write → real physical page allocated (the "demand
allocation" moment). Dirty anonymous pages must be swapped out under pressure.

**Overcommit (vm.rst sysctl, verified):**
- overcommit_memory=0 (default): kernel checks but allows some overcommit (heuristic)
- overcommit_memory=1: always succeeds (never OOM until actually needed)
- overcommit_memory=2: hard limit = swap + overcommit_ratio% of RAM

**Page cache (mm/concepts.rst, verified):** File reads → data placed in page cache; subsequent
reads hit cache. Writes → go to page cache (dirty), written back by kswapd or pdflush on
dirty_background_ratio threshold or direct reclaim at dirty_ratio. vm.swappiness controls
relative cost weighting of swap vs file-cache eviction (0-200 scale; 100=equal cost).

**procfs vm observability (/proc/meminfo, verified):**
- MemTotal, MemFree, MemAvailable (estimate for new allocations without swapping — not same as MemFree)
- Buffers (block device cache, separate from Cached), Cached (page cache), Active/Inactive(file/anon)
- AnonPages (anonymous in RAM), Mapped (currently mapped), Slab (kernel slab allocator usage)
- Dirty, Writeback — pending I/O budget
- **MemAvailable is NOT MemFree.** Includes reclaimable cache (SReclaimable) and reserves.

**smaps and pagemap (/proc/pid/smaps, pagemap.rst, verified):**
- /proc/pid/maps: VMA list (address range, permissions, file backing)
- /proc/pid/smaps: per-VMA RSS, PSS (Proportional Set Size = RSS/share_count), private/shared dirty/clean
- /proc/pid/pagemap: 64-bit entry per virtual page; bit 63 = present, bits 0-54 = PFN (requires
  CAP_SYS_ADMIN since Linux 4.0 to get actual PFN due to Rowhammer concerns)

### 1.4 File Descriptors, epoll, and I/O Multiplexing (TLPI)

**Forcing constraint:** A process serving 10,000 connections cannot call read() on each in
turn (O(N) per event). Polling (select/poll) scans all fds (O(N) per call). epoll maintains
a kernel-side interest list and a ready list — O(1) per event regardless of total fd count.

**epoll internals (epoll.7, epoll_ctl.2, epoll_wait.2, all verified):**
Three syscalls:
1. `epoll_create1(0)` → returns epoll fd (an in-kernel object with interest + ready lists)
2. `epoll_ctl(epfd, EPOLL_CTL_ADD/MOD/DEL, fd, &event)` → registers fd in interest list
3. `epoll_wait(epfd, events, maxevents, timeout)` → blocks until ready; returns ready events

Internal structure: interest list backed by a red-black tree (O(log N) add/remove); ready
list built as events fire (interrupt-driven); epoll_wait drains the ready list (O(1) amortized).

**Level-triggered (LT, default) vs edge-triggered (ET, EPOLLET) — epoll.7, verified:**
- LT: epoll_wait returns as long as the fd has unread data (safe for partial reads)
- ET: epoll_wait returns only when new data *arrives* (state change). If reader consumes
  partial data and returns to epoll_wait, the next wait blocks until more data arrives — even
  if data is still buffered. ET requires draining fd to EAGAIN/EWOULDBLOCK (non-blocking fd
  mandatory) to avoid missing data. Advantage: fewer syscalls in high-throughput cases.

**FD semantics (TLPI):** Each fd is an index into the per-process fd table. fd table entry
points to a shared *open file description* (OFD) in the kernel. OFD holds: file offset,
status flags, reference count. fork() duplicates the fd table — parent and child share OFDs,
so a write in one advances the offset seen by the other. dup()/dup2() also creates new fds
pointing to the same OFD. FD_CLOEXEC (O_CLOEXEC) flag is per-fd-table-entry, not per-OFD.

### 1.5 Linux Scheduler: CFS and EEVDF (Love LKD + kernel docs)

**Forcing constraint:** xv6 uses O(N) round-robin with a flat array. Linux serves millions
of tasks with nanosecond accounting and must not starve any task class (interactive, batch,
real-time) regardless of workload.

**CFS (sched-design-CFS.rst, verified, merged Linux 2.6.23):**
- Model: ideal multi-tasking CPU (all N tasks run simultaneously at 1/N speed). CFS
  approximates this with a red-black tree of tasks sorted by `p->se.vruntime` (nanoseconds).
- Always picks leftmost task (smallest vruntime = least CPU time consumed).
- Weighted by nice level: vruntime accumulates slower for high-priority tasks (they run longer
  before being preempted). Weight is `sched_prio_to_weight[nice+20]` — each nice level is ~1.25x.
- One tunable: `/sys/kernel/debug/sched/base_slice_ns` (was `sched_min_granularity_ns`)
- No explicit time-slice concept — preemption fires when vruntime of current task exceeds
  leftmost task's vruntime by more than the granularity.
- Scheduling classes: SCHED_NORMAL (CFS), SCHED_BATCH, SCHED_IDLE, SCHED_FIFO, SCHED_RR (RT).

**EEVDF (sched-eevdf.rst, verified, Linux 6.6):**
- "Earliest Eligible Virtual Deadline First" — replaces CFS as default in 6.6+.
- Adds a "lag" concept: tasks owed CPU time have positive lag, tasks that exceeded their share
  have negative lag. Task eligible if lag >= 0. Among eligible tasks, picks earliest virtual
  deadline. Sleeping tasks: lag *decays* over virtual runtime (preventing gaming by brief sleeps).
- Allows latency-sensitive tasks to request shorter time slices via sched_setattr().
- Still uses a red-black tree; CFS documentation still valid for mechanism context.

**runqueue structure (Love LKD, cross-checked sched.h):** Per-CPU runqueue (`struct rq`). Each
CPU has its own CFS run queue (`cfs_rq`), RT runqueue, deadline queue. Load balancer (for SMP)
migrates tasks between CPUs respecting cache affinity.

### 1.6 Kernel Memory Allocation (Love LKD / kernel docs)

**Forcing constraint:** Kernel cannot use page faults for its own allocations (would deadlock —
the page fault handler IS the kernel). Kernel needs both contiguous physical pages (for DMA)
and arbitrary-size slabs (for frequent allocs of same-size objects).

**Buddy allocator (free page management):** Organizes free pages into power-of-2 size blocks.
Allocate 2^n pages → split larger block if needed; free → coalesce with buddy to form larger
block. Fragmentation: over time large contiguous allocations fail even with ample total free
RAM → compaction (kcompactd) migrates pages to form larger contiguous regions.

**Slab allocator (kmem_cache_alloc, kmalloc):**
- kmalloc(size, flags): for arbitrary small allocations; backed by size-class slab caches.
- kmem_cache_alloc(): allocate from a dedicated per-type slab cache (e.g., task_struct, inode).
- Slab caches pre-initialize objects, keep them warm in CPU-local caches → very fast alloc/free.
- GFP flags (core-api/memory-allocation.rst, verified): GFP_KERNEL (may sleep, may reclaim);
  GFP_NOWAIT (atomic context, no sleep, likely fails under pressure); GFP_ATOMIC (interrupt context).

**Memory zones (mm/concepts.rst, verified):**
- ZONE_DMA, ZONE_DMA32: for hardware with limited address ranges
- ZONE_NORMAL: standard kernel/user pages
- ZONE_HIGHMEM (32-bit only): beyond kernel direct-map, requires kmap to access
- kswapd: background reclaim when free < low watermark
- Direct reclaim: synchronous, triggered at min watermark (allocation stalls)
- OOM killer: last resort — selects victim by oom_score (sum of RSS, swap, children, etc.)

### 1.7 /proc and /sys Observability (TLPI/kernel docs)

**Forcing constraint:** The kernel's internal state must be readable from userland without
privileged kernel modules. procfs and sysfs provide a virtual filesystem interface — reading
a file executes a kernel function that formats live kernel data.

**Key /proc/pid/ files (filesystems/proc.rst, verified):**
- `cmdline` — null-separated argv
- `environ` — null-separated environment
- `fd/` — symlinks to open file descriptions
- `maps` — VMA list (address, perms, offset, device, inode, path)
- `smaps` — per-VMA memory stats (RSS, PSS, private/shared dirty/clean)
- `stat` — process state string (fields: PID, comm, state letter, PPID, pgrp, utime, stime ...)
- `statm` — page counts: VmSize, VmRSS, shared, text, data
- `status` — human-readable VmRSS, VmSize, threads, capabilities
- `pagemap` — PFN per virtual page (CAP_SYS_ADMIN for actual PFN since Linux 4.0)
- `io` — read/write bytes (rchar/wchar = logical, read_bytes/write_bytes = actual I/O)
- `wchan` — kernel function the task is blocked in (requires CONFIG_KALLSYMS)

**Key /proc/ system-wide files (filesystems/proc.rst, verified):**
- `/proc/stat` — per-CPU time: user, nice, system, idle, iowait, irq, softirq, steal, guest
  (fs/proc/stat.c, verified). iowait is counted per-CPU when CPU is idle AND I/O is outstanding.
- `/proc/meminfo` — MemTotal, MemFree, MemAvailable, Buffers, Cached, Dirty, Slab, etc.
- `/proc/loadavg` — 1/5/15min load averages (exponentially weighted moving average of runqueue length)
- `/proc/interrupts` — per-CPU interrupt counts by IRQ number
- `/proc/net/dev` — per-interface TX/RX bytes, packets, errors, drops

### 1.8 perf_events: Hardware and Software Counters (man-pages + kernel)

**Forcing constraint:** Instrumenting every instruction is too slow. PMU (Performance Monitoring
Unit) counters in hardware count events with near-zero overhead. Overflow interrupts sample at
configurable rate, attributing execution to code addresses.

**perf_event_open() (man-pages perf_event_open.2, verified):**
```
int syscall(SYS_perf_event_open, struct perf_event_attr *attr, pid_t pid, int cpu, int group_fd, unsigned long flags);
```
Returns an fd. Event types (verified from man-pages):
- PERF_TYPE_HARDWARE: PERF_COUNT_HW_CPU_CYCLES, INSTRUCTIONS, CACHE_REFERENCES,
  CACHE_MISSES, BRANCH_INSTRUCTIONS, BRANCH_MISSES, BUS_CYCLES, STALLED_CYCLES_FRONTEND/BACKEND
- PERF_TYPE_SOFTWARE: PERF_COUNT_SW_CPU_CLOCK, TASK_CLOCK, PAGE_FAULTS, CONTEXT_SWITCHES,
  CPU_MIGRATIONS, PAGE_FAULTS_MIN, PAGE_FAULTS_MAJ
- PERF_TYPE_TRACEPOINT: kernel static tracepoints
- PERF_TYPE_HW_CACHE: L1D, L1I, LL (last-level), DTLB, ITLB, BPU cache events

Two event modes: *counting* (read() returns count) and *sampling* (overflows write to ring
buffer mmap'd to userspace). `perf record -F 99 -ag` = sample at 99 Hz, all CPUs, with stacks.

**perf CLI (tools/perf/Documentation, verified):**
`perf stat` counts events over a command; reports IPC, cache miss rate, branch miss rate.
`perf record -F 99 -ag` samples at 99 Hz all CPUs with call stacks into perf.data.
`perf report` shows hierarchical hotspot breakdown. `perf script` emits raw stack traces
(input to flamegraph.pl). `perf top` shows live hot functions.

**Security (admin-guide/perf-security.rst, verified):** Full PMU access requires CAP_PERFMON
(or CAP_SYS_ADMIN for compat). Unprivileged access controlled by
`/proc/sys/kernel/perf_event_paranoid` (0=all, 1=kernel stacks no, 2=no kernel counters, 3+
varies by distro).

### 1.9 eBPF: Verified Safe In-Kernel Programs (kernel bpf/ + bpftrace/bcc)

**Forcing constraint:** kprobes/uprobes alone enable arbitrary kernel code execution — unsafe.
eBPF adds a verifier that statically proves safety (no loops, bounded memory access, no bad
pointers) before loading. Safety without privilege escalation.

**eBPF execution model (bpf/verifier.rst, verified):**
1. User writes BPF bytecode (or uses bpftrace/BCC to compile C→BPF via LLVM)
2. `bpf(BPF_PROG_LOAD, ...)` syscall → verifier runs:
   - DAG check: no unsafe/unbounded control flow; classic BPF forbids loops, while modern eBPF
     can allow bounded loops when the verifier can prove loop limits [NEEDS-SOURCE: exact kernel version]
   - Type inference: tracks register types (PTR_TO_CTX, PTR_TO_MAP, SCALAR_VALUE, etc.);
     rejects unsafe dereferences; uninitialized registers unreadable
   - Memory bounds: stack access only within [-MAX_BPF_STACK, 0); pointer arithmetic tightly controlled
3. JIT compilation to native code (x86_64, aarch64, etc.)
4. Attached to a hook; fires when hook triggers; result (pass/drop/return value) fed back

**Program types (include/uapi/linux/bpf.h, verified):**
SOCKET_FILTER, KPROBE (dynamic kernel function entry/return), TRACEPOINT (static kernel
tracepoints), XDP (express data path, pre-NIC-stack), PERF_EVENT, CGROUP_SKB, TRACING (fentry/fexit
via BTF-based CO-RE), SYSCALL, LSM (security hooks), and more (33 types enumerated in current bpf.h as of the factcheck pass; version-sensitive).

**bpftrace language (bpftrace/docs/language.md, verified):**
D-inspired: `probe { /predicate/ action }`. Probe types: `kprobe:fn` (kernel function entry),
`kretprobe:fn` (return), `tracepoint:subsys:event` (static, stable ABI), `uprobe:/bin:fn`
(userspace), `fentry/fexit` (BTF-based, faster than kprobes). Example:
`tracepoint:syscalls:sys_enter_open { printf("%s %s\n", comm, str(args.filename)); }`

**BCC (iovisor/bcc, verified):** Python/Lua frontend for eBPF in C, compiled via LLVM at load
time. Key tools: opensnoop, execsnoop, tcpretrans, biolatency, funccount, klockstat, deadlock
detection. bpf-perf-tools-book repo contains 150+ bpftrace scripts from Gregg's book.

### 1.10 Flame Graphs and the USE Method (Brendan Gregg)

**Forcing constraint:** A profile showing per-function CPU time is a flat list — hard to see
call chains. A flame graph visualizes the full call stack weighted by sample count, making the
"hot path" visually obvious.

**Flame graph generation (FlameGraph/README.md + flamegraph.pl, verified):**
Three steps:
1. Capture stacks: `perf record -F 99 -a -g -- sleep 60; perf script > out.perf`
2. Fold stacks: `stackcollapse-perf.pl out.perf > out.folded`
   (format: semicolon-separated stack frames + space + count per line)
3. Render SVG: `flamegraph.pl out.folded > flame.svg`
Result: interactive SVG (click to zoom, Ctrl-F search, hover for info). Each box = function,
width = time spent in that function + its callees. Sorted alphabetically within a level to
allow visual merging of identical stacks. Kernel frames annotated with `_[k]`.

**Reading a flame graph:** Wide boxes at any level = hot code. Flat top = CPU-bound (function
itself is the bottleneck). Tall narrow towers with no wide top = deep call chains, hot leaf.
Gaps (no boxes at top of a tall tower) = CPU idle or off-CPU (need off-CPU flame graph for that).

**USE Method [UNVERIFIED — brendangregg.com blocked; sourced from GitHub readme context]:**
For every resource (CPU, memory, network, disk, bus), check:
- **Utilization**: time resource is busy (saturation begins > ~70% for queue-forming resources)
- **Saturation**: length of wait queue; tasks waiting for the resource
- **Errors**: error events (retransmits, ECC errors, disk errors)
Methodology: enumerate ALL resources → check U/S/E for each → bottleneck identified
before deep investigation. Complements Linux perf tools: vmstat, iostat, sar, netstat,
perf stat, /proc/stat.

### 1.11 cgroups and Linux Process Resource Control (kernel docs)

**Forcing constraint:** A multi-tenant system cannot let one group of processes monopolize
CPU, memory, or I/O. cgroups provide hierarchical resource accounting and limits without
process isolation (that requires namespaces + containers).

**cgroup v2 (admin-guide/cgroup-v2.rst, verified):**
"cgroup is a mechanism to organize processes hierarchically and distribute system resources
along the hierarchy in a controlled and configurable manner."
Mounted at /sys/fs/cgroup (unified v2 hierarchy). Controllers: cpu, memory, io, pid, cpuset.
Key files: `cgroup.procs` (move process), `cpu.weight` (proportional share), `memory.max`
(hard OOM limit), `memory.high` (soft limit), `io.max` (bandwidth cap).
Resource models: Weights, Limits, Protections (guaranteed min), Allocations (exclusive).

---

## 2. Foundational Sources — Exact Links, One Canonical per Claim

| Claim | Source |
|-------|--------|
| fork() semantics (COW, fd inheritance, signal clearing) | github.com/mkerrisk/man-pages blob/master/man2/fork.2 |
| Linux task states (TASK_RUNNING=0, TASK_INTERRUPTIBLE=1, EXIT_ZOMBIE=0x20) | github.com/torvalds/linux blob/master/include/linux/sched.h |
| Signal dispositions, mask, SA_RESTART, SIGKILL uncatchable | github.com/mkerrisk/man-pages blob/master/man7/signal.7 |
| mmap() flags (MAP_SHARED, MAP_PRIVATE, MAP_ANONYMOUS, PROT_*) | github.com/mkerrisk/man-pages blob/master/man2/mmap.2 |
| epoll interest list/ready list, LT vs ET, EPOLLET mechanics | github.com/mkerrisk/man-pages blob/master/man7/epoll.7 |
| epoll_ctl EPOLL_CTL_ADD/MOD/DEL; epoll_wait timeout semantics | github.com/mkerrisk/man-pages blobs man2/epoll_ctl.2 + man2/epoll_wait.2 |
| /proc/pid/ files (maps, smaps, stat, io, pagemap, wchan) | github.com/torvalds/linux blob/master/Documentation/filesystems/proc.rst |
| /proc/meminfo (MemAvailable != MemFree, Dirty, Slab, AnonPages) | github.com/torvalds/linux blob/master/Documentation/filesystems/proc.rst |
| pagemap bit layout; PFN restricted since Linux 4.0 (Rowhammer) | github.com/torvalds/linux blob/master/Documentation/admin-guide/mm/pagemap.rst |
| Anonymous memory, zero page, demand allocation, page cache, OOM | github.com/torvalds/linux blob/master/Documentation/admin-guide/mm/concepts.rst |
| overcommit_memory modes 0/1/2; vm.swappiness 0-200 | github.com/torvalds/linux blob/master/Documentation/admin-guide/sysctl/vm.rst |
| CFS vruntime, red-black tree, base_slice_ns, SCHED_* classes | github.com/torvalds/linux blob/master/Documentation/scheduler/sched-design-CFS.rst |
| EEVDF lag, virtual deadline, sched_setattr, Linux 6.6+ | github.com/torvalds/linux blob/master/Documentation/scheduler/sched-eevdf.rst |
| Buddy allocator, slab, GFP_KERNEL/ATOMIC/NOWAIT flags | github.com/torvalds/linux blob/master/Documentation/core-api/memory-allocation.rst |
| Memory zones ZONE_DMA/NORMAL/HIGHMEM; kswapd; direct reclaim | github.com/torvalds/linux blob/master/Documentation/admin-guide/mm/concepts.rst |
| perf_event_open() signature; PERF_TYPE_*; PERF_COUNT_HW/SW_* | github.com/mkerrisk/man-pages blob/master/man2/perf_event_open.2 |
| perf_event_paranoid; CAP_PERFMON access control | github.com/torvalds/linux blob/master/Documentation/admin-guide/perf-security.rst |
| perf record/stat/top/report/script CLI | github.com/torvalds/linux blob/master/tools/perf/Documentation/ |
| eBPF verifier (DAG, type inference, bounds checking) | github.com/torvalds/linux blob/master/Documentation/bpf/verifier.rst |
| BPF prog types (enum bpf_prog_type, 33 current entries; version-sensitive) | github.com/torvalds/linux blob/master/include/uapi/linux/bpf.h |
| ftrace/tracefs; static tracepoints via set_event | github.com/torvalds/linux blobs Documentation/trace/ftrace.rst + events.rst |
| bpftrace probe types (kprobe, tracepoint, uprobe, fentry, fexit) | github.com/bpftrace/bpftrace blob/master/docs/language.md |
| BCC toolkit; key tools (opensnoop, biolatency, execsnoop) | github.com/iovisor/bcc blob/master/README.md |
| Flame graph 3-step pipeline; stackcollapse format | github.com/brendangregg/FlameGraph blobs README.md + flamegraph.pl |
| perf-tools (iosnoop, execsnoop, cachestat, tcpretrans) | github.com/brendangregg/perf-tools blob/master/README.md |
| BPF Performance Tools book — 150+ bpftrace scripts | github.com/brendangregg/bpf-perf-tools-book blob/master/README.md |
| cgroup v2: hierarchy, controllers, resource models | github.com/torvalds/linux blob/master/Documentation/admin-guide/cgroup-v2.rst |
| /proc/stat iowait semantics (fs/proc/stat.c) | github.com/torvalds/linux blob/master/fs/proc/stat.c |
| Flame graph paper (ACMQ 2016, canonical citation) | queue.acm.org/detail.cfm?id=2927301 |

---

## 3. Why It's This Way — Constraints and Tradeoffs

**3.1 ET epoll requires non-blocking fds:** In ET mode, a single event fires per state
change. If the reader uses a blocking fd and only reads partial data, it returns to epoll_wait.
No new data arrives → no new event fires → reads stall forever. Non-blocking + drain-to-EAGAIN
is not optional in ET mode. The tradeoff: ET is faster (fewer epoll_wait wakeups) at the cost
of more complex read loops.

**3.2 TASK_UNINTERRUPTIBLE exists for kernel correctness:** Some kernel operations (disk I/O
completion, NFS locks) cannot safely be interrupted mid-sequence. If a signal could wake such
a task, it might leave kernel data structures inconsistent. D-state processes are therefore
unkillable (not even SIGKILL) until the operation completes. This is correct behavior but
creates operational pain when NFS hangs — the process is stuck until the remote replies.
TASK_KILLABLE was added as a middle ground (wakes on fatal signals only).

**3.3 Overcommit by default (mode=0) reflects real-world fork/exec patterns:** fork()
conceptually doubles the process's VA space, but in a fork-then-exec pattern, the child
immediately replaces its image. If the kernel rejected the fork() due to insufficient physical
RAM, correct programs would fail even when they'd never actually use that memory. Overcommit
allows the fork-exec idiom at scale; the risk is that OOM killer fires if the commit is actually
exercised under memory pressure.

**3.4 eBPF verifier trades expressiveness for safety:** Classic BPF: simple, no loops, safe.
Extended BPF: 11 64-bit registers, helper functions, maps, JIT — expressive enough to require
verifier-bounded control flow in modern kernels. Verifier must statically bound every execution
path — undecidable in general, so verifier uses conservative approximations: reject any program
it cannot prove safe. Practical implication: some correct programs are rejected; workarounds require restructuring.

**3.5 CFS is being replaced by EEVDF because CFS misfires on latency:** CFS's preemption is
granularity-based (don't preempt unless current task is "far ahead" of next). For short-lived
latency-sensitive tasks, CFS may delay them by a full granularity even when they have the
highest priority. EEVDF assigns virtual deadlines — tasks must complete their slice by their
deadline, enabling earlier preemption for latency-sensitive workloads.

**3.6 Flame graphs commonly use 99 Hz, not 100 Hz:** Gregg's FlameGraph README examples use
`perf record -F 99 -ag`. The practical rationale is to avoid synchronizing with common 10ms/100Hz
periodic work; 99 is not prime, but it is co-prime to 100 (`gcd(99,100)=1`). [NEEDS-SOURCE:
README confirms 99 Hz usage; aliasing rationale needs Gregg blog/book citation before quoting as primary.]

**3.7 procfs is NOT a real filesystem:** procfs/sysfs files have no size (zero as reported
by stat); they generate content on each read by calling a kernel function. This means:
- `cat /proc/stat` is a syscall that computes statistics in the kernel
- Files cannot be seek-read atomically across multiple reads (race conditions in snapshot)
- `wc -l /proc/pid/maps` changes the map while wc reads it (not a file on disk)

---

## 4. Common Misconceptions to Preempt

**M1: "TASK_RUNNING means the process is using CPU."** False. TASK_RUNNING = on the runqueue,
which includes tasks waiting for CPU. A process can be in TASK_RUNNING for seconds before being
scheduled. "Currently executing" = TASK_RUNNING AND is the `current` task on a CPU.

**M2: "%iowait in top/vmstat is per-process I/O wait."** False. %iowait is a per-CPU counter
that increments when the CPU is *idle* AND at least one I/O is outstanding from that CPU. It
is not a measure of how long any specific process waited for I/O.

**M3: "MemFree in /proc/meminfo is the available memory for new applications."** False. MemFree
is truly free pages with nothing in them. MemAvailable accounts for reclaimable cache and is
a better estimate. On a healthy system, MemFree can be near zero while MemAvailable is large.

**M4: "epoll scales to any number of file descriptors."** Partially true. The epoll instance
itself scales O(1) per event. But the application still needs to handle each ready fd, so
10,000 simultaneous ready events still require 10,000 dispatch iterations. epoll solves the
*polling cost*, not the *handling cost*.

**M5: "SA_RESTART makes signals transparent to all system calls."** False. Many syscalls restart
automatically with SA_RESTART, but nanosleep, ppoll, pselect, and clock_nanosleep return EINTR
even with SA_RESTART. Any call that "waits a specified time" generally does not restart — the
man page for each syscall specifies its behavior.

**M6: "eBPF programs can be loaded by any user."** Gated by perf_event_paranoid and capability
checks. Most eBPF program types require CAP_BPF (Linux 5.8+, or older CAP_SYS_ADMIN). The
verifier prevents kernel corruption but not privilege escalation — loading is itself privileged.

**M7: "A flame graph shows where time is spent in the CPU."** Only for CPU flame graphs (perf
record -F ...). Off-CPU time (blocking on I/O, locks, sleep) is invisible in a CPU flame graph.
Off-CPU flame graphs (using scheduling tracepoints) are needed for I/O or lock contention analysis.

**M8: "The page cache wastes memory."** It is the design intent. The Linux memory manager uses
all RAM for page cache when not needed for processes (the "free memory is wasted memory"
principle). The kernel reclaims it as needed. MemFree near zero on a busy server is healthy.

---

## 5. Best Build-Your-Own Targets

**5.1 Tiny epoll echo server (core TLPI exercise):**
Build a single-threaded server handling N concurrent TCP connections using epoll. Implement
accept, add to epoll interest list (EPOLLIN, EPOLLET), non-blocking read-to-EAGAIN, echo write,
graceful close. Target: understand ET vs LT, EAGAIN, why non-blocking is mandatory in ET mode.
Source pattern: TLPI Ch. 63 (not freely available, but syscalls are in man-pages on GitHub).

**5.2 procfs observer script (pure shell + /proc):**
Write a script using only /proc reads (no external tools) to report: per-CPU busy%, memory
pressure (Dirty/MemAvailable), top-RSS processes (scan /proc/*/statm). Forces understanding
of /proc/stat field semantics, VmRSS vs VmSize, and delta computation.

**5.3 perf + flamegraph profiling lab:**
Profile a CPU-bound program (matrix multiply or sort), generate a flame graph. Then add an
artificial hotspot, re-profile, and identify it in the flame graph. Pipeline:
`perf record -F 99 -g` -> `perf script` -> `stackcollapse-perf.pl` -> `flamegraph.pl`.
Teaches: sampling mechanics, stack unwinding, SVG interactivity.

**5.4 bpftrace one-liners lab (kernel docs tracepoints):**
- `bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s\n", str(args.filename)); }'`
  — trace all open() calls with filename
- `bpftrace -e 'kprobe:do_sys_open { @[comm] = count(); }'` — count opens per process
- Histogram of read latencies: fentry + fexit with timestamp delta
Source: bpftrace/docs/language.md (verified); exercises from brendangregg/bpf-perf-tools-book.

**5.5 mmap file-backed reader/writer:**
Use MAP_SHARED to map a file; have two processes write/read through the mapping. Observe via
/proc/pid/smaps the private/shared dirty page counts. Add msync() for durability. Teaches:
page cache sharing, dirty tracking, msync vs fsync, VMA layout.

---

## 6. Open Questions / Where Sources Disagree

**6.1 Gregg USE method: primary source inaccessible.** brendangregg.com blocked at Walmart
proxy. USE Method details sourced from secondary context in GitHub tool descriptions and kernel
docs. The formal USE Method checklist (resource categories, saturation definitions) is in
*Systems Performance* 2nd ed Ch. 2 — book paywalled; specific checklist items marked [UNVERIFIED]
until the book text or an accessible mirror is confirmed.

**6.2 CFS vs EEVDF: transition still in progress.** Kernel docs (sched-eevdf.rst, verified)
state EEVDF was introduced in Linux 6.6 and "making room for EEVDF." Distributions shipping
older kernels still use CFS. The xv6 brief uses CFS as the Linux scheduler reference — accurate
for most current production systems, but leading-edge 6.6+ kernels use EEVDF. Briefs should
note both, with CFS as the primary teaching vehicle (better documented, more sources).

**6.3 eBPF bounded loops: version dependency.** Verifier-bounded loop support is kernel-version
specific; this pass did not pin the exact introducing commit. Tools written for older kernels
(e.g., 4.x fleets) cannot assume bounded loops, and bpftrace/fentry availability is also kernel-version dependent.
Production kernel version fragmentation is a real source of tool incompatibility.

**6.4 iowait accounting is notoriously unreliable.** /proc/stat iowait field is only incremented
when the CPU is *idle* and I/O is outstanding — it can undercount under CPU saturation and
overcount under workloads with many tiny I/Os. Multiple sources (Gregg, kernel docs) flag this.
Prefer iostat -x %util (device saturation) for I/O bottleneck diagnosis.

**6.5 TLPI (2010) predates many modern syscalls.** Kerrisk's book predates: io_uring (5.1),
pidfd (5.3), bpf() fully mature APIs, cgroup v2 stable. TLPI is canonical for the fundamentals
(fork/exec/signals/epoll/mmap) but not the current observability stack. Man-pages project
(github.com/mkerrisk/man-pages) is the maintained primary source for current syscall specs.

**6.6 Love LKD (2010) predates CFS maturity and is pre-EEVDF.** 3rd edition covers the O(1)
scheduler transition to CFS (2.6.23) but EEVDF, cgroup v2, eBPF, and NUMA-aware allocation
developments postdate it. Use Linux kernel Documentation/ as the authoritative supplement for
anything post-2010.

**6.7 Gap: io_uring not covered.** io_uring (Linux 5.1) provides a ring-buffer submission/
completion queue interface avoiding per-operation syscall overhead — relevant for high-IOPS
workloads. Not in TLPI, not in Love LKD. Covered in liburing documentation and
kernel/Documentation. If sub-course 04 covers modern I/O, this is a needed addition.

**6.8 Gap: NUMA and scheduler topology.** NUMA-aware memory allocation, per-NUMA-node freelists,
and scheduler topology (socket vs core vs SMT) are important at scale but absent from this
cluster's primary sources. Robert Love's coverage is pre-NUMA-mature. Add Gregg's *Systems
Performance* Ch. 6 (CPUs) and Ch. 7 (Memory) for this if accessible.

---

*Brief only — no chapter prose. Complements _research_ostep-cs162-xv6.md. Append additional cluster briefs as new sections.*
