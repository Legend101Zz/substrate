# Reconciled Research Brief — 04 Operating Systems Internals

Cluster briefs reconciled:
- `_research_ostep-cs162-xv6.md` — OSTEP + Berkeley CS162 + MIT 6.1810/xv6.
- `_research_linux-performance-kerrisk-gregg.md` — TLPI/man-pages + Linux kernel docs/source + Brendan Gregg tooling.

Phase 1 artifact only. No chapters. Use cluster briefs for full detail and exact source tables.

---

## 1. Key mechanisms — consolidated spine

### Process abstraction and lifecycle
The OS exists because untrusted programs must share CPU, memory, and devices without trusting each other. That forces three hardware-backed boundaries: timer interrupts prevent CPU monopoly, virtual memory prevents address-space corruption, and privilege modes prevent direct hardware/page-table control.

xv6 gives the clean mechanism: `struct proc` tracks state (UNUSED/USED/SLEEPING/RUNNABLE/RUNNING/ZOMBIE), trapframe, kernel context, user pagetable, kernel stack, open files, cwd, and sleep channel. `fork` copies user pages eagerly in base xv6; `exec` replaces the image after loading ELF into a fresh pagetable; `exit` makes ZOMBIE and wakes the parent; `wait` harvests status and frees the proc. Linux keeps the same user-visible fork/exec/wait model but uses COW in practice, shares open file descriptions after fork, and implements threads as clone-created tasks sharing VM/files/signals.

### Traps, syscalls, and privilege transition
RISC-V trap entry is intentionally minimal: hardware saves `sepc`/`scause`, switches to S-mode, and jumps to `stvec`; software must save registers and switch page tables. xv6's trampoline page is mapped at the same virtual address in user and kernel page tables so code continues executing across `satp` changes. Syscall args live in a0–a5; syscall number in a7; return value is written to a0. The key teaching point: a syscall is not a function call into a library — it is a controlled privilege transition with explicit register save/restore, page-table switching, and `sret` return.

### Scheduling and context switching
Context switching and scheduling are distinct. xv6 `swtch.S` saves only callee-saved kernel registers (ra, sp, s0–s11) into `struct context`; user registers are in the trapframe. The scheduler is a per-CPU coroutine that linearly scans `proc[]`, runs RUNNABLE processes round-robin, and executes `wfi` when idle. OSTEP supplies policy vocabulary (FIFO convoying, SJF/STCF optimality vs unknowable job length, RR response/turnaround tradeoff, MLFQ gaming/starvation, lottery/stride proportional share). Linux uses per-CPU runqueues; CFS orders tasks by virtual runtime in an RB-tree; Linux 6.6+ introduces EEVDF with lag and virtual deadlines for latency-sensitive work.

### Virtual memory and paging
Address translation must be fast on every memory access, so hardware MMU/TLB performs translation while the OS maintains page tables. xv6 Sv39 uses 3 levels of 512 PTEs each; PTE flags include V/R/W/X/U; `walk()` descends L2→L1→L0 and allocates page-table pages as needed. xv6 maps kernel devices/text/data/trampoline and gives each process a separate user page table. OSTEP adds concepts xv6 omits or labs extend: segmentation, demand paging, page replacement (OPT/FIFO/LRU/Clock), working sets/thrashing, COW fork, and TLB/ASID tradeoffs. Linux exposes VM behavior through `mmap`, `/proc/*/maps`, `/proc/*/smaps`, `/proc/meminfo`, overcommit modes, page cache, reclaim, swap, and OOM behavior.

### Memory allocation
xv6 physical allocation is intentionally tiny: one global freelist of 4 KiB pages protected by one spinlock; freed pages are filled with 0x01 and allocated pages with 0x05 to expose bugs. Linux adds buddy allocation for physical pages, slab/kmem caches for object allocation, GFP flags for sleepability/context constraints, memory zones for DMA/highmem, kswapd/direct reclaim, compaction, and OOM selection. Constraint: kernel allocation cannot rely on ordinary page faults because the fault handler is kernel code and may run in contexts where sleeping/reclaim is illegal.

### Synchronization, sleep, and signals
xv6 uses spinlocks for short non-sleeping critical sections and sleeplocks for disk/I/O-backed structures. `sleep(chan, lk)` atomically releases the caller lock after acquiring `p->lock`, preventing lost wakeups; `wakeup(chan)` scans sleepers. OSTEP generalizes this into locks, condition variables, semaphores, Mesa semantics, and deadlock conditions. Linux adds POSIX signals: dispositions, per-thread masks, pending sets, SIGKILL/SIGSTOP uncatchability, real-time queued signals, and EINTR/SA_RESTART subtleties. Crucial correction: a Linux TASK_RUNNING task may merely be runnable on a runqueue, not actively executing.

### Filesystems, descriptors, and I/O
xv6 file system layers: blocks → log/WAL → inodes → directories → pathname lookup. Its on-disk layout is boot/super/log/inodes/bitmap/data; buffer cache uses an LRU list; WAL makes multi-block updates all-or-nothing at the cost of writing blocks twice. `iget` and `ilock` are deliberately split so references can outlive locks. Linux/TLPI extends the interface model: an fd indexes a per-process table entry pointing to a shared open file description (offset/status flags), so fork/dup share offsets; FD_CLOEXEC is per-fd, not per-OFD. `epoll` scales readiness notification by keeping kernel-side interest and ready lists; edge-triggered mode requires non-blocking fds and drain-to-EAGAIN loops.

### Observability and performance tooling
Real OS teaching must connect internals to live diagnosis. `/proc` and `/sys` are virtual filesystems generated by kernel code, not disk files. `/proc/stat` exposes CPU counters; `/proc/meminfo` distinguishes MemFree from MemAvailable; `/proc/<pid>/smaps` exposes RSS/PSS/private/shared dirty pages; pagemap PFNs require privilege due to Rowhammer. `perf_event_open` provides hardware/software counters and sampling; `perf record -F 99 -g` plus FlameGraph's stack-collapse/render pipeline visualizes hot call stacks. eBPF adds verified in-kernel programs attached to kprobes/tracepoints/fentry/uprobe/XDP/etc.; the verifier trades expressiveness for safety by proving bounded memory access and control flow.

---

## 2. Foundational sources — canonical anchors

- xv6 source/book/labs: `github.com/mit-pdos/xv6-riscv`, `pdos.csail.mit.edu/6.828/2024/xv6/book-riscv-rev4.pdf`, `pdos.csail.mit.edu/6.1810/2024/labs/{util,syscall,pgtbl,traps,cow,lock,fs,mmap}.html`.
- OSTEP: free online chapters via `ostep.org` / `pages.cs.wisc.edu/~remzi/OSTEP/`; in this session, PDF access was blocked, so chapter structure was verified via `github.com/remzi-arpacidusseau/ostep-homework` and project list via `ostep-projects`.
- Berkeley CS162 / OSPP / Pintos: `cs162.org`; Anderson & Dahlin OSPP: `ospp.cs.washington.edu`.
- Linux man-pages/TLPI proxy: `github.com/mkerrisk/man-pages` for `fork(2)`, `mmap(2)`, `signal(7)`, `epoll(7)`, `epoll_ctl(2)`, `epoll_wait(2)`, `perf_event_open(2)`, `proc(5)`.
- Linux kernel docs/source: `github.com/torvalds/linux` docs for scheduler CFS/EEVDF, cgroup v2, procfs, memory concepts, vm sysctl, pagemap, bpf verifier, ftrace/events, perf security, and source `include/linux/sched.h`, `include/uapi/linux/bpf.h`, `fs/proc/stat.c`.
- Brendan Gregg tooling: `github.com/brendangregg/FlameGraph`, `perf-tools`, `bpf-perf-tools-book`; `github.com/bpftrace/bpftrace` and `github.com/iovisor/bcc` for BPF tooling.

---

## 3. Why it's this way — forcing constraints

- **Privilege separation:** without hardware user/kernel modes, a program could disable interrupts, mutate page tables, or program devices directly. OS isolation is hardware-enforced or it is theater.
- **Trampoline mapping:** trap entry starts while using the user page table; identical VA mapping lets the code survive the `satp` switch.
- **Per-process kernel stacks:** a shared kernel stack would corrupt concurrent syscalls; using the user stack would trust attacker-controlled memory.
- **Two-hop scheduling:** a yielding process cannot directly become another; it saves into its own context, resumes the per-CPU scheduler, and the scheduler switches to the next context.
- **Interrupts disabled around spinlocks:** otherwise an interrupt handler on the same CPU can spin forever on a lock held by the interrupted code.
- **Journaling/WAL:** multi-block filesystem updates need an atomic commit point; recovery checks the log header and replays or ignores the transaction.
- **epoll ET drain rule:** edge-triggering reports state changes, not persistent readiness; partial reads without non-blocking drain-to-EAGAIN can stall forever.
- **Overcommit:** fork/exec would fail unnecessarily if the kernel reserved full physical memory for the child's inherited address space; overcommit optimizes the common immediate-exec case at OOM-risk cost.
- **eBPF verifier:** in-kernel extensibility without arbitrary kernel code execution requires conservative static proof; valid but unprovable programs are rejected.
- **99 Hz profiling:** FlameGraph examples use `perf record -F 99`; the anti-aliasing rationale is plausible but needs a Gregg blog/book citation before being taught as sourced fact.

---

## 4. Common misconceptions to preempt

- `exec` creates a new process — false; it replaces the current process image.
- `swtch()` saves all registers — false; user registers are trapframe, kernel callee-saved registers are context.
- xv6 `fork` uses COW — false in base xv6; COW is a lab. Linux uses COW in practice.
- A page fault is always an error — false; demand paging, COW, `mmap`, and stack growth depend on faults as control flow.
- TASK_RUNNING means currently on CPU — false; it includes runnable-on-runqueue.
- MemFree is usable memory — misleading; MemAvailable accounts for reclaimable cache and reserves.
- epoll removes all scaling costs — false; it removes O(N) polling cost, not O(events) application handling.
- CVs and semaphores are interchangeable — false; CV notifications can be lost, semaphore counts persist.
- CPU flame graphs show all bottlenecks — false; off-CPU/I/O/lock waits require off-CPU tracing.
- `SA_RESTART` makes signal interruptions invisible — false; many timed waits still return EINTR.

---

## 5. Best build-your-own targets

Primary ladder:
1. **xv6 syscall lab** — add trace/sysinfo; teaches syscall table, arg fetch, proc/kernel data exposure.
2. **xv6 traps/alarm lab** — user-level timer interrupt handler; teaches trapframe manipulation.
3. **xv6 COW fork lab** — best single VM lab: PTE flags, refcounts, page-fault handling, copy-on-write correctness.
4. **xv6 lock lab** — per-CPU freelists and hash-bucket buffer cache; teaches contention measurement and redesign.
5. **xv6 fs/mmap labs** — double-indirect blocks, symlinks, file-backed lazy paging.

Complementary labs:
- tiny epoll echo server with non-blocking ET mode and drain-to-EAGAIN loop.
- `/proc` observer script computing CPU deltas, MemAvailable, Dirty, RSS/PSS from live procfs.
- perf + FlameGraph profiling lab for CPU-bound code.
- bpftrace one-liners for syscall opens, execs, disk latency, and TCP retransmits.
- toy filesystem in a file: superblock + bitmap + inodes + dirents + WAL.

---

## 6. Open questions / gaps

- OSTEP PDFs were blocked through the proxy; chapter structure and project inventory were verified, but exact OSTEP text/quotes need direct PDF access before quoting.
- xv6 book rev4 Chapter 9 title remains `[UNVERIFIED]`; cite chapter topics from the current PDF/schedule, not stale third-party commentary.
- Linux scheduler teaching should explain both CFS (better documented, widely deployed) and EEVDF (6.6+ default direction); exact distro adoption is date-sensitive.
- Gregg USE Method primary page was blocked; formal checklist should be verified against *Systems Performance* or a reachable canonical page before quoting.
- io_uring, NUMA topology, namespaces/containers, Spectre/Meltdown mitigations, and cgroups-as-container substrate are important modern OS topics but probably belong in appendix B/I unless Phase 2 expands 04.
- Page replacement is mostly theory in OSTEP; xv6 has no eviction. Pintos VM project is the best runnable implementation in this source set.
- Performance numbers (syscall latency, context-switch cost, TLB miss penalty) are hardware-dependent and absent from xv6/OSTEP/CS162; use measured labs or Gregg-style tooling rather than fixed constants.
