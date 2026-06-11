# 04 — Operating Systems Internals · _structure.md

**Identity:** how one machine safely runs many untrusted programs at once. The keystone
foundation — every later system (DB, cache, queue, runtime, container) is an OS concept
specialized.

**Bespoke shape — "one constraint, six abstractions, two altitudes each."** The whole
sub-course descends from ONE forcing function stated up front: *untrusted programs must
share CPU/memory/devices without trusting each other* ⇒ three hardware boundaries (timer
interrupts, virtual memory, privilege modes). Each subsequent chapter takes one OS
abstraction and teaches it at TWO altitudes: the **clean mechanism** (xv6 — small enough to
read whole) THEN the **production reality** (Linux/TLPI + observe it live via /proc, perf,
eBPF). The "see it on a real machine" move is the distinctive close of each chapter.

## Dependency position
- **Depends on:** 01 (CPU/memory/privilege), 02 (process model on-ramp — fork/exec/wait).
- **Feeds into:** 05 (runtimes sit on processes/threads/mmap), 07 (DB = files+WAL+buffer
  cache, mirrors xv6 fs), 08 (page cache), 10 (epoll event-driven servers), 11 (failure),
  17/18 (queues/backpressure echo bounded buffers), 26 (WAL/recovery).
- **Appendix link DOWN:** B-linux-internals (xv6→Linux→isolation diff: CFS/EEVDF detail,
  buddy/slab, io_uring, and the **namespaces+cgroups substrate** that feeds I/J).

## Chapter specs (3–5 lines each)
1. **Why an OS exists** — the sharing-without-trust constraint; the three hardware
   boundaries (timer interrupt, MMU/virtual memory, user/kernel privilege). "Isolation is
   hardware-enforced or it is theater." Frames everything after.
2. **The process abstraction** — `struct proc`, the state machine
   (UNUSED…RUNNABLE/RUNNING/ZOMBIE), fork/exec/exit/wait. xv6 eager-copy vs Linux COW +
   threads-as-clone-tasks sharing VM/files/signals. Connects back to 02's shell.
3. **Traps & system calls** — a syscall is NOT a library call: it's a controlled privilege
   transition. RISC-V trap entry (sepc/scause/stvec), the trampoline page mapped at the
   same VA in both page tables, arg/number registers, `sret`. Observe with strace/bpftrace.
4. **Scheduling & context switch** — distinct concepts. xv6 `swtch.S` saves only
   callee-saved kernel regs (user regs live in the trapframe); per-CPU scheduler coroutine.
   Policy vocabulary (FIFO convoy, SJF/STCF, RR, MLFQ gaming, lottery/stride) → Linux CFS
   (vruntime RB-tree) → EEVDF (6.6+). TASK_RUNNING ≠ on-CPU.
5. **Virtual memory & paging** — translation on every access ⇒ hardware MMU/TLB + OS page
   tables. xv6 Sv39 3-level walk + PTE flags. OSTEP adds demand paging, replacement
   (OPT/FIFO/LRU/Clock), working sets/thrashing, COW. Observe via /proc/maps, smaps,
   meminfo, overcommit. Page fault as control flow, not error.
6. **Memory allocation** — xv6's one-freelist/one-spinlock page allocator → Linux buddy +
   slab/kmem caches + GFP flags + zones + kswapd/reclaim + OOM. Why kernel alloc can't rely
   on ordinary page faults (fault handler may not sleep).
7. **Concurrency: locks, sleep, signals** — spinlocks vs sleeplocks; `sleep(chan,lk)`
   atomic release to avoid lost wakeups. Generalize to CVs/semaphores/Mesa-semantics/
   deadlock. Linux signals: dispositions, masks, SIGKILL/SIGSTOP uncatchable, EINTR/
   SA_RESTART. CV-notify lost ≠ semaphore count persists.
8. **Filesystems, descriptors, I/O** — xv6 layers: blocks→log/WAL→inodes→dirs→pathname;
   buffer-cache LRU; WAL makes multi-block updates atomic (double-write cost). Linux: fd →
   shared open file description (offsets shared after fork/dup); FD_CLOEXEC per-fd; epoll
   interest/ready lists; ET requires non-blocking drain-to-EAGAIN. Bridges to 07/08/10.
9. **Observability — see the OS run** — /proc & /sys as kernel-generated virtual fs;
   MemFree vs MemAvailable; perf_event_open + `perf record -F 99 -g` + FlameGraphs;
   eBPF verified in-kernel programs (bounded-proof tradeoff). The "diagnose it live" capstone.

## Paired build lab (/build → xv6 labs are the spine)
Primary ladder (all xv6, mapped to chapters): **syscall** (trace/sysinfo) → **traps/alarm**
(user-level timer handler) → **COW fork** (best single VM lab: PTE flags/refcounts/fault
handling) → **lock** (per-CPU freelists, hash-bucket buffer cache, contention) →
**fs/mmap** (double-indirect blocks, symlinks, file-backed lazy paging). Complementary:
tiny epoll echo server (non-blocking ET drain), a /proc observer script, perf+FlameGraph
profiling, bpftrace one-liners, "filesystem in a file" (superblock+bitmap+inodes+WAL).

## Diagrams needed
- The three hardware boundaries → three abstractions map.
- Process state machine; fork/exec/exit/wait timeline with COW page sharing.
- Trap entry: user→trampoline→kernel, satp switch, register save (the page that demystifies
  syscalls).
- Context-switch vs schedule (two-hop) diagram; CFS vruntime RB-tree.
- Sv39 3-level page-table walk; TLB hit/miss path; COW fault sequence.
- fd → open-file-description → inode sharing after fork/dup; epoll interest/ready lists.
- A FlameGraph specimen (annotated).

## Sources / gaps to honor (from _research.md)
- OSTEP PDFs were proxy-blocked: chapter structure verified, but quote exact OSTEP text
  only after direct PDF access. xv6 book rev4 Ch.9 title `[UNVERIFIED]`.
- Teach BOTH CFS (documented/deployed) and EEVDF (6.6+ direction); distro adoption is
  date-sensitive. Gregg USE-Method page was blocked — verify checklist vs *Systems
  Performance* before quoting.
- Performance numbers (syscall latency, ctx-switch cost, TLB miss) are hardware-dependent —
  use measured labs, not fixed constants.
- Scope guard: io_uring, NUMA, namespaces/cgroups, Spectre/Meltdown live in appendix B/I,
  not 04 (unless an ADR expands 04).
