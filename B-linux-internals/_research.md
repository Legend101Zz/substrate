# Appendix B · linux-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). B is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). Spine **04** teaches OS internals against a *teaching*
> kernel (xv6) + generic OS theory (OSTEP). B is the deep reference for the question 04 hands DOWN:
> **"how does the REAL kernel — Linux — implement and EXTEND those abstractions in production?"** Spine
> 04 cross-links DOWN into B; B sits ON appendix **A** (page tables / TLB) and is the SUBSTRATE under
> appendices **I** (docker = namespaces+cgroups) and **J** (kubernetes). **Bespoke structure:
> xv6-abstraction → what Linux actually does → what Linux ADDS that xv6 has no concept of** — a
> generic-to-production diff, NOT four clusters, NOT a build progression. Math: `_recompute.py`
> (14/14). Factcheck: `_factcheck_phase1.md` (0 blockers). Network: man7.org / kernel.org docs HTTP
> **000** this wave → constants reused from 04's line-verified xv6 + TLPI/man-pages + Linux
> source/docs reads; nothing new hardened.

## 1. Thesis
04 teaches *what an OS must do* (isolate, schedule, translate memory, mediate I/O) using xv6 — small,
correct, readable. B teaches *how the one kernel this course actually runs on does it at production
scale*, and the through-line is: **Linux generalizes every xv6 abstraction into a configurable,
hierarchical, observable mechanism — and then adds the resource-isolation primitives (namespaces +
cgroups) that turn a process into a container.** xv6 has processes; Linux has *tasks* unified by
`clone()`. xv6 has round-robin; Linux has CFS→EEVDF proportional-share. xv6 eagerly copies fork
memory; Linux does COW + overcommit + a page cache. And xv6 has no notion of resource caps or
namespacing at all — that gap is exactly where appendix I (Docker) is born.

## 2. xv6-abstraction → Linux-reality → Linux-addition (the bespoke spine)

### Layer 1 — The task model (xv6 `struct proc` → Linux `task_struct` + clone)
- xv6: `fork` eagerly copies user pages; threads don't exist; `exec` swaps the image.
- Linux: ONE abstraction — `task_struct` — created by **clone()**. RECOMPUTED: "thread vs process" is
  just which `CLONE_*` flags share resources (a thread = clone sharing VM+files+signals;
  `pthread_create` and `fork` both bottom out in clone). WHY: a single scheduler/lifecycle path.
- COW fork: RECOMPUTED a 1 GB process forks copying **0** pages (PTEs marked read-only); only the W
  pages the child writes fault-and-copy → blast radius = pages *touched*, not pages *mapped* → WHY
  fork+exec is cheap and **overcommit** is the sane default (04 §3).

### Layer 2 — Scheduling (xv6 round-robin → CFS → EEVDF)
- xv6: linear scan of `proc[]`, round-robin, `wfi` when idle.
- Linux **CFS**: pick smallest **vruntime** (RB-tree leftmost, O(log n)). RECOMPUTED n equal-weight
  tasks converge to 1/n CPU each; **nice** sets weight (~1.25×/level → 5 levels ≈ 3× share) → nice
  controls *proportion*, not absolute priority bands (so nice 19 starves *gently*).
- Linux **EEVDF** (6.6+ default direction): adds a virtual **deadline** = eligible_time +
  slice/weight. RECOMPUTED a task requesting a *smaller* slice gets an *earlier* deadline → scheduled
  sooner → lower latency *without* sacrificing fairness. This is the production answer to OSTEP's
  response-vs-turnaround tradeoff (04 §1).

### Layer 3 — Memory (xv6 freelist → buddy/slab + page cache + reclaim)
- xv6: one global freelist of 4 KiB pages, one spinlock; poison bytes to catch bugs.
- Linux **buddy allocator**: physical pages in power-of-2 **orders** (split/merge). RECOMPUTED a 100 KB
  request rounds up to order 5 = 32 pages = 128 KB (internal fragmentation) → WHY **slab/kmalloc**
  caches exist for small kernel objects. GFP flags encode sleepability/context.
- **Page cache**: Linux uses spare RAM to cache file pages. RECOMPUTED **MemFree** looks alarmingly
  small while **MemAvailable** (reclaimable cache + reserves) is the real headroom → the "Linux ate my
  RAM" myth (04 §1). Reclaim (kswapd/direct), swap, and the OOM killer manage pressure.
- Translation sits on appendix **A**: real x86-64 4/5-level page tables + TLB (RECOMPUTED in A: a TLB
  miss = ~4-access page walk ≈ 400 ns). Page faults are *control flow* (demand paging, COW, mmap,
  stack growth) — not always errors (04 misconception).

### Layer 4 — I/O and events (xv6 blocking syscalls → epoll → io_uring)
- xv6: blocking read/write through the buffer cache + WAL.
- Linux **epoll**: O(ready) readiness notification, not O(watched) scanning. RECOMPUTED 100k idle conns
  + 10 active: select scans 100,000, epoll touches 10 (10,000× less work) — the **C10K** fix (→ spine
  03/10). Edge-triggered requires non-blocking drain-to-EAGAIN (04 §3).
- Linux **io_uring**: a shared **SQ/CQ ring** pair lets one `io_uring_enter` submit a *batch*.
  RECOMPUTED 256 ops = 256 classic syscalls vs ~1 io_uring syscall. WHY it beats epoll+read at high
  IOPS: RECOMPUTED a syscall is a privilege transition ~100× a function call → the syscall + mode
  switch (appendix A) is the tax, and batching amortizes it. (Exact ring byte layout `[UNVERIFIED]`.)

### Layer 5 — What Linux ADDS that xv6 has NO concept of: isolation (→ appendices I/J)
- **Namespaces**: per-resource, **composable** virtualization of kernel-visible identifiers.
  RECOMPUTED 8 types (pid/net/mnt/uts/ipc/user/cgroup/time). A "container" = a process with its own
  set — cheap (shared kernel) and flexible (share some, isolate others), unlike a VM's all-or-nothing.
- **cgroups v2**: hierarchical resource caps. RECOMPUTED `cpu.max "50000 100000"` = 50% of one CPU
  (quota/period); `memory.max` is a **hard cap** → per-cgroup OOM (isolates the blast radius — one
  container can't starve the host).
- Together namespaces (what you can *see*) + cgroups (what you can *use*) **are** the container. This
  is the exact substrate appendix **I** (Docker) compiles its `--cpus`/`--memory`/`--net` flags down
  to, and appendix **J** (Kubernetes) schedules on top of.
- **Observability**: `/proc` + `/sys` are kernel-generated virtual filesystems; `perf_event_open` +
  **eBPF** (verified in-kernel programs; the verifier proves bounded memory/control flow or rejects)
  give live, low-overhead tracing — the production version of "inspect the kernel" that xv6 can't offer.

## 3. The "generalize, then isolate" reconciliation (appendix payload)
| xv6 abstraction | Linux reality | Linux addition | load-bearing number | anchor |
|---|---|---|---|---|
| `struct proc`, eager fork | `task_struct` + clone, COW | unified thread/process model | fork copies 0 pages | 04 |
| round-robin | CFS min-vruntime | EEVDF virtual deadline | n tasks → 1/n; nice^5 ≈ 3× | 04 |
| freelist + spinlock | buddy + slab + page cache | reclaim/overcommit/OOM | order-5 = 128 KB; MemAvailable | 04 |
| blocking syscalls | epoll O(ready) | io_uring batched rings | 10,000× less; 256→1 syscall | 04/03/10 |
| (none) | — | **namespaces + cgroups v2** | cpu.max 50%; 8 ns types | 04 → I/J |
| printf debug | `/proc`+`/sys`, perf | **eBPF** verified tracing | — | 04 |

## 4. Common misconceptions to preempt
- "Threads and processes are different kernel objects." Both are `task_struct` via clone; the
  difference is shared-resource flags.
- "fork copies the whole address space." COW copies nothing up front; only written pages copy.
- "Low MemFree means I'm out of RAM." Page cache is reclaimable; **MemAvailable** is the real number.
- "nice is a priority band." It's a *weight* — proportional share, not absolute precedence.
- "epoll removes all scaling cost." It removes O(watched) polling, not O(events) app handling.
- "io_uring is just async epoll." It's a batched submit/complete ring that amortizes the *syscall*
  itself, not only the wait.
- "A container is a lightweight VM." It's a process in namespaces + cgroups sharing the host kernel —
  no guest kernel, isolation is composable per-resource.
- "cgroup limits are advisory." `memory.max` is a hard cap that triggers a per-cgroup OOM kill.
- "`/proc` files are on disk." They're generated by kernel code on read.

## 5. Provenance summary
- **REUSED (line-verified in 04):** clone/task model, COW + overcommit, CFS vruntime + EEVDF, buddy +
  slab + page cache + reclaim, epoll, cgroup v2, namespaces, `/proc`+`/sys`, eBPF verifier. (04 cited
  xv6 + TLPI/man-pages + the Linux kernel docs/source directly.)
- **REUSED:** A (page tables/TLB), 13 (latency/syscall cost), N (math); 03/10 (C10K/event-driven).
- **RECOMPUTED:** `_recompute.py` (14/14) — clone flag bitmask, COW copy count, CFS 1/n + nice weight,
  EEVDF deadline, MemFree-vs-MemAvailable, buddy order rounding, epoll O(ready), io_uring batching,
  cgroup cpu.max/memory.max, namespace composition, syscall-vs-call cost.
- **`[UNVERIFIED]` carry-forward (not load-bearing):** Linux source/docs + man-pages primary text
  (hosts 000); io_uring ring byte layout; exact CFS/EEVDF + nice→weight constants (version-specific);
  NUMA / Spectre-Meltdown / THP / OOM-score heuristics (appendix-B depth, structural only); plus all
  carried 04 gaps (OSTEP text, Gregg USE page, xv6 Ch.9 title, hardware-dependent absolute timings).
  All blocked behind unreachable hosts; logged, none hardened.

---
**Appendix B reconciled.** Reference-grade, exercise-free, 14/14 recomputed, all mechanisms reused
from 04's line-verified source reads. Establishes the namespaces+cgroups substrate for appendices
I (docker) and J (kubernetes). No chapters yet.
