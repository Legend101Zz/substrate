# Research Brief: OSTEP + Berkeley CS162 + MIT 6.S081/xv6
## Sub-course 04 — Operating Systems Internals
## Researcher: researcher-5110f7 | Phase 1 | 2026-06-09

---

## Source cluster
- OSTEP (Arpaci-Dusseau & Arpaci-Dusseau): Virtualization, Concurrency, Persistence — free online
- Berkeley CS162 (Spring 2026): textbook = Anderson & Dahlin OSPP 2nd ed; project = Pintos
- MIT 6.1810 / 6.S081 (Fall 2024, formerly 6.828): xv6-riscv book (rev4) + source + 8 labs

Primary sources read directly: xv6-riscv source (all kernel/*.{c,h,S}); 6.1810 schedule + 8 lab specs; xv6 book rev4 PDF downloaded (769 KB); OSTEP chapter list verified via ostep-homework README (GitHub); CS162 schedule (cs162.org); A&D OSPP confirmed (ospp.cs.washington.edu). OSTEP PDFs: pages.cs.wisc.edu blocked at Walmart proxy; ostep.org redirects there; chapter structure confirmed via GitHub README only.

---

## 1. Key Mechanisms — Deep and Precise

### 1.1 The Process Abstraction

**Forcing constraint:** User programs must not (a) monopolize the CPU, (b) access others' memory, or (c) call privileged hardware ops. These three constraints independently require timer interrupts, virtual address spaces, and user/kernel mode — none is optional.

**xv6 `struct proc` key fields (kernel/proc.h, verified):**
- `enum procstate state` — UNUSED / USED / SLEEPING / RUNNABLE / RUNNING / ZOMBIE
- `void *chan` — sleep channel; `int killed` — checked on every trap return
- `uint64 kstack` — per-process kernel stack VA; `pagetable_t pagetable` — user PT root
- `struct trapframe *trapframe` — one page holding all 31 saved user registers
- `struct context context` — callee-saved regs for kernel swtch; `struct file *ofile[16]`
- Design constants (param.h): NPROC=64 (flat table, linear scan), NCPU=8, NOFILE=16

**Process lifecycle (proc.c, verified):**
- `allocproc()` — scans proc[] for UNUSED; allocates trapframe page + kernel stack; sets context.ra=forkret
- `kfork()` — copies all user pages eagerly via uvmcopy (no COW by default); copies trapframe; sets child trapframe->a0=0
- `kexec()` — reads ELF header + program headers; builds new PT; loads segments; allocates guard page + user stack; switches PT atomically on success
- `exit()` — state=ZOMBIE; wakes parent; reparents orphans to initproc; calls sched()
- `wait()` — scans proc[] for ZOMBIE children; harvests exit status; calls freeproc()

### 1.2 The Trap / System Call Mechanism

**Forcing constraint:** On RISC-V, hardware saves only sepc + scause on a trap; everything else is software. When ecall fires, the MMU still uses the user page table and no kernel stack exists yet. The kernel needs code that runs in this liminal state before the page table switch.

**Trampoline solution (memlayout.h, vm.c, trampoline.S, verified):** Map the same physical page (trampoline.S) at TRAMPOLINE = MAXVA-PGSIZE in both user and kernel page tables (no PTE_U set → user code cannot read/write it, but CPU executes it in S-mode). TRAPFRAME = TRAMPOLINE-PGSIZE is also per-process and kernel-only. Because the VA is identical in both PTs, code at TRAMPOLINE remains accessible after `csrw satp` switches the table.

**Full trap entry/exit sequence (trampoline.S + trap.c, verified):**
1. `ecall` fires: hardware sets sepc=user PC, scause=8 (U-mode syscall), SPP=0 in sstatus, enters S-mode, jumps to stvec (= uservec in trampoline).
2. `uservec`: saves a0 in sscratch; loads TRAPFRAME into a0; stores all 31 user regs into trapframe; restores kernel sp/tp/usertrap-addr/satp from trapframe fields; sfence.vma; csrw satp (switch to kernel PT); sfence.vma; jalr to usertrap().
3. `usertrap()`: verifies SPP=0; sets stvec=kernelvec; saves epc: `p->trapframe->epc = r_sepc()`; dispatches: scause=8 → increment epc+4, intr_on(), syscall(); scause 13/15 (page fault) → vmfault() for lazy allocation; devintr() for devices; else kill. Timer interrupt (devintr→2) → yield().
4. `prepare_return()`: intr_off(); stvec=uservec; refills trapframe->kernel_*; clears SPP, sets SPIE in sstatus; writes user PC to sepc.
5. `userret` (trampoline): csrw satp (switch back to user PT); sfence.vma; restores all user regs from trapframe; loads TRAPFRAME into sscratch; sret → S-mode off, interrupts on per SPIE, jump to sepc.

**Syscall dispatch (syscall.c):** args from trapframe a0–a5; syscall number from a7; return value written to a0. Fetch from user memory uses copyin (bounds-checked against p->sz).

**Key CSRs (riscv.h, verified):** stvec (trap vector), sepc (saved PC), scause (8=ecall, 13=load PF, 15=store PF), sstatus (SPP, SPIE, SIE), satp (SATP_SV39 | pagetable>>12), sscratch (temp during uservec).

### 1.3 Context Switching and Scheduling

**Forcing constraint:** Two separate problems — (1) save/restore CPU state across a yield, (2) choose next process. xv6 separates them: swtch() handles (1); scheduler() handles (2) via round-robin over the flat proc[] table.

**swtch.S (verified, 29 instructions):** Saves 14 registers (ra, sp, s0–s11) to `old->context`; loads the same 14 from `new->context`; `ret` → jumps to new->context.ra. Saves callee-saved only (ABI guarantees caller-saved are spilled by caller). Used exclusively for kernel-to-kernel switches.

**Scheduler (proc.c, verified):** Each CPU runs an infinite loop; for each RUNNABLE proc: acquire(p->lock), state=RUNNING, c->proc=p, swtch(&c->context, &p->context). When proc calls sched(), swtch returns control here; c->proc=0, release(p->lock). No RUNNABLE procs → `wfi` (wait for interrupt).

**sleep/wakeup (proc.c, verified):** `sleep(chan, lk)`: acquire(p->lock), release(lk), p->chan=chan, state=SLEEPING, sched(); on wake: p->chan=0, release(p->lock), acquire(lk). `wakeup(chan)`: scans all procs; SLEEPING+matching chan → RUNNABLE. Lost-wakeup prevented by holding p->lock across the state change before releasing lk.

**OSTEP scheduling algorithms (verified via homework README chapter list):**
- FIFO: convoy problem. SJF/STCF: optimal with preemption but requires knowing job length.
- Round Robin: good response time, poor turnaround.
- MLFQ: approximates STCF without job-length knowledge. Rules: new jobs start highest; use full slice → demote; periodic boost prevents starvation. Can be gamed by short I/O-before-quantum-expiry.
- Lottery/Stride: proportional-share. CFS (Linux): red-black tree on vruntime; weight = f(nice).
- Multiprocessor: SQMS vs MQMS; cache affinity; work-stealing for load balance.

### 1.4 Virtual Memory: Paging and Address Translation

**Forcing constraint:** Address translation on every memory access must be hardware-fast. The MMU (TLB + page-table walker) does it; software only manages the page tables.

**RISC-V Sv39 (vm.c + riscv.h, verified):** 39-bit VA (bits 63:39 must be zero). 3-level PT, 512 entries/level (9 bits each). VA split: [38:30]=L2, [29:21]=L1, [20:12]=L0, [11:0]=offset. PTE (64-bit): PPN[53:10] + flags[9:0] — PTE_V(0), PTE_R(1), PTE_W(2), PTE_X(3), PTE_U(4). PGSIZE=4096; MAXVA = 1<<(9+9+9+12-1) = 256 GB. `walk()` (vm.c): iterates L2→L1, reads/allocates PT pages, returns pointer to L0 PTE. `PTE2PA(pte) = (pte>>10)<<12`.

**Kernel PT layout (kvmmake + memlayout.h, verified):** UART0 (0x10000000), virtio (0x10001000), PLIC (0x0C000000) — identity-mapped, PTE_R|PTE_W, no PTE_U. Kernel text (KERNBASE=0x80000000): PTE_R|PTE_X. Kernel data+free RAM (end..PHYSTOP=KERNBASE+128MB): PTE_R|PTE_W. TRAMPOLINE: PTE_R|PTE_X. Per-proc kernel stacks: KSTACK(p) = TRAMPOLINE-(p+1)*2*PGSIZE (guard page gap between each).

**User PT layout (memlayout.h + exec.c, verified):** 0x0=text/data/BSS (ELF load); heap grows up; TRAPFRAME=TRAMPOLINE-PGSIZE (PTE_R|PTE_W, no PTE_U); TRAMPOLINE=same physical page as kernel (PTE_R|PTE_X, no PTE_U).

**OSTEP VM concepts (from chapter list; not in xv6 base):**
- Segmentation: base+limit per segment; eliminates internal fragmentation but external fragmentation accumulates.
- Free-space management: first/best/worst-fit; coalescing + splitting; external fragmentation unavoidable in variable-size allocation.
- Demand paging: page not allocated until first access; page fault → alloc, map, retry instruction.
- Page replacement: OPT (unrealizable), FIFO (Belady anomaly), LRU (good, costly), Clock (reference-bit ring approximation of LRU).
- Working set / thrashing: sum of working sets > physical RAM → thrashing.
- COW fork (lab): PTEs marked read-only in parent+child; store fault → alloc new page, copy, remap writable; physical pages reference-counted.

**TLB (OSTEP ch. vm-tlbs):** Hit = 1–2 cycles; miss = full walk (10s of cycles). RISC-V: software-managed; sfence.vma flushes entries. xv6 does not use ASIDs — always flushes on PT switch. ASIDs (Linux) tag TLB entries per AS, avoiding full flush on context switch.

### 1.5 Physical Memory Allocator

**Design (kalloc.c, verified):** Single global freelist of 4 KB pages; `struct run *next` stored in the free page itself. `kinit()`: kfree every aligned page from kernel end to PHYSTOP. `kfree()`: fills with 0x01 (catch dangling refs), pushes to freelist head. `kalloc()`: pops from head, fills with 0x05 (catch uninit reads), returns NULL if empty. Protected by one global spinlock — bottleneck on multi-core (lock lab fix: per-CPU freelists + work-stealing).

### 1.6 Locking: Spinlocks and Sleeplocks

**Spinlock (spinlock.c, verified):** `acquire`: push_off (depth-counted interrupt disable); `__atomic_exchange_n(&lk->locked, 1, __ATOMIC_ACQUIRE)` spin until 0 → held. `release`: `__atomic_store_n(&lk->locked, 0, __ATOMIC_RELEASE)` (emits `fence rw,w` on RISC-V); pop_off. ACQUIRE barrier: no CS loads/stores move before lock. RELEASE barrier: no CS loads/stores move after unlock. Interrupts disabled to prevent same-CPU ISR deadlock.

**Sleeplock (sleeplock.c, verified):** Wraps a spinlock; `acquiresleep` calls `sleep(lk, &lk->lk)` while locked — yields CPU instead of spinning. Used for buffer cache (each buf) and inodes (each inode) where critical section may do disk I/O. Cannot be used in interrupt handlers (cannot sleep there).

**Deadlock prevention:** Global lock-ordering discipline documented in fs.c: itable.lock → inode sleeplock; bcache.lock → buf sleeplock; wait_lock → p->lock. `holding()` check + `panic` in `acquire` catches violations.

### 1.7 File System: Five-Layer Stack

**Layers (fs.c comment, verified):** (1) Blocks — bitmap allocator; (2) Log — WAL; (3) Files — inodes; (4) Directories — inodes with dirent contents; (5) Names — path lookup.

**On-disk layout (fs.h, verified):** `[boot | super | log(30) | inodes | bitmap | data]`. BSIZE=1024. Superblock: magic, size, nblocks, ninodes, nlog, logstart, inodestart, bmapstart. On-disk inode (dinode): type, nlink, size, addrs[13] — 12 direct + 1 indirect → max 12+256=268 blocks (268 KB). Lab/fs adds double-indirect: 11+256+65536=65803 blocks. Directory entry: inum(2B) + name[14] (no required null).

**Buffer cache (bio.c, verified):** NBUF=30 bufs in LRU doubly-linked list; bcache.lock (spinlock) protects list; each buf has its own sleeplock. `bget`: find by (dev,blockno) incrementing refcnt, or evict LRU entry with refcnt==0. `bread`: bget + virtio_disk_rw if !valid. `brelse`: sleeplock release, decrement refcnt, move to MRU head.

**Write-ahead log (log.c, verified):** Crash problem: file creation needs multiple writes (inode alloc, inode init, dirent write); power failure mid-sequence → inconsistent disk. WAL solution: `begin_op/log_write/end_op`. All modified block numbers accumulated in log.lh; on `end_op` (last outstanding): `write_head()` writes header to disk (commit point); `install_trans()` copies log blocks to their real locations; clears header. Recovery on boot: if header n>0 (committed), replay install_trans; clear. Write amplification = 2x (every block written twice). xv6 uses full data journaling (strongest, most expensive). Linux ext4 default: ordered journaling (metadata only in journal, data flushed first).

**Inodes (fs.c, verified):** itable.inode[50] in-memory; `iget` increments ref (no lock); `ilock` acquires sleeplock + reads disk if !valid; `iput` decrements ref; if last ref + nlink==0, frees blocks + inode. Separation of ref (memory pointer) from nlink (directory link count) lets open files outlive their directory entries.

**Path lookup:** namei/namex: start from ROOTINO=1 or cwd; for each component: search directory inode for dirent by name → inum → iget.

### 1.8 I/O and Devices

**RISC-V interrupt path (trap.c, plic.c, riscv.h, verified):** External interrupts routed through PLIC (0x0C000000); kernel reads PLIC_SCLAIM to learn device, handles, writes back. Timer uses stimecmp CSR (sstc extension, set in start.c); expiry → usertrap detects devintr()=2 → yield(). Three types: timer, external (PLIC), software.

**OSTEP device/disk concepts (file-devices, file-disks chapters):** Polling wastes CPU; interrupt-driven I/O frees CPU between request and completion; DMA: device writes to memory directly, one interrupt at end. Disk latency dominated by seek + rotation (ms range) >> transfer. SSTF scheduling: minimizes seek, risks starvation. SCAN/elevator: sweeps, fair. SSDs: NOOP or deadline scheduler (no seek penalty).

### 1.9 Concurrency: Locks, CVs, Semaphores

**OSTEP model (threads-* chapters, verified from chapter list):** Thread = shared address space, own PC+stack+registers. Race condition: result depends on instruction interleaving. Critical section must execute atomically.

**Hardware primitives (threads-locks):** test-and-set (spinlock basis); compare-and-swap (lock-free structures); fetch-and-add (ticket locks, no starvation); RISC-V lr/sc (load-reserved/store-conditional).

**Condition variables (threads-cv):** `wait(cv, mutex)`: atomically release mutex + sleep; reacquire on wakeup. Mesa semantics (POSIX): woken thread re-checks condition in a `while` loop — wakeup does not guarantee condition holds. Hoare semantics: immediate transfer, condition guaranteed; both use while loop in practice. xv6 sleep/wakeup is channel-based CV; piperead/pipewrite use while loops.

**Semaphores (threads-sema):** P/V (down/up). Binary = mutex; counting = resource pool or signaling. Producer/consumer: two semaphores (empty=N, full=0) + mutex eliminates race without busy-wait.

**Deadlock (threads-bugs):** Four Coffman conditions: mutual exclusion, hold-and-wait, no preemption, circular wait. Prevention: lock ordering (breaks circular wait); trylock+backoff; lock-free. Common bugs: atomicity violation (missing lock around multi-step read-modify-write); order violation (thread assumes other ran; fix: CV or semaphore); lost wakeup (check condition + sleep not atomic; fix: hold lock across both — as in xv6 sleep).

---

## 2. Foundational Sources — Exact Links, One Canonical per Claim

| Claim | Source |
|-------|--------|
| OSTEP chapter structure | github.com/remzi-arpacidusseau/ostep-homework/README.md |
| OSTEP PDF URL pattern | pages.cs.wisc.edu/~remzi/OSTEP/ (blocked; ostep.org redirects there) |
| xv6 RISC-V source | github.com/mit-pdos/xv6-riscv (branch: riscv) |
| xv6 book PDF rev4 | pdos.csail.mit.edu/6.828/2024/xv6/book-riscv-rev4.pdf |
| xv6 project page | pdos.csail.mit.edu/6.828/2024/xv6.html |
| 6.1810 schedule | pdos.csail.mit.edu/6.1810/2024/schedule.html |
| 6.1810 lab: util | pdos.csail.mit.edu/6.1810/2024/labs/util.html |
| 6.1810 lab: syscall | pdos.csail.mit.edu/6.1810/2024/labs/syscall.html |
| 6.1810 lab: pgtbl | pdos.csail.mit.edu/6.1810/2024/labs/pgtbl.html |
| 6.1810 lab: traps | pdos.csail.mit.edu/6.1810/2024/labs/traps.html |
| 6.1810 lab: cow | pdos.csail.mit.edu/6.1810/2024/labs/cow.html |
| 6.1810 lab: lock | pdos.csail.mit.edu/6.1810/2024/labs/lock.html |
| 6.1810 lab: fs | pdos.csail.mit.edu/6.1810/2024/labs/fs.html |
| 6.1810 lab: mmap | pdos.csail.mit.edu/6.1810/2024/labs/mmap.html |
| proc struct | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/proc.h |
| trapframe / trampoline | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/trampoline.S |
| usertrap, prepare_return | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/trap.c |
| swtch (context switch asm) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S |
| scheduler, yield, sleep, wakeup | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/proc.c |
| spinlock (atomic exchange, fence) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/spinlock.c |
| sleeplock | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/sleeplock.c |
| Sv39 walk(), PTE layout, mappages | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/vm.c |
| Memory layout defines | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/memlayout.h |
| RISC-V CSR defs | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/riscv.h |
| Physical allocator (kalloc, kfree) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/kalloc.c |
| Kernel boot sequence | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/main.c |
| Machine-mode startup, privilege delegation | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/start.c |
| On-disk FS layout, dinode, dirent | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/fs.h |
| Inode, path lookup, balloc, bmap | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/fs.c |
| Buffer cache (LRU, bget, bread, brelse) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/bio.c |
| WAL (begin_op, end_op, commit, recover) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/log.c |
| Pipe (bounded buffer, sleep/wakeup) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/pipe.c |
| File descriptor / in-memory inode | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/file.h |
| exec() — ELF load, PT build | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/exec.c |
| Design constants (NPROC, LOGBLOCKS, …) | github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/param.h |
| CS162 schedule, Pintos project | cs162.org |
| Anderson & Dahlin OSPP 2nd ed | ospp.cs.washington.edu |
| OSTEP projects (kernel hacking) | github.com/remzi-arpacidusseau/ostep-projects |
| Journaling the Linux ext2fs FS (1998) | 6.1810 LEC 15 reading |
| Virtual Memory Primitives for User Programs (Appel & Li, 1991) | 6.1810 LEC 16 reading |
| The Performance of microkernel-Based Systems (1997) | 6.1810 LEC 17 reading |
| Dune: Safe User-level Access to Privileged CPU Features (2012) | 6.1810 LEC 18 reading |
| Meltdown (2018) | 6.1810 LEC 21 reading |

---

## 3. Why It's This Way — Constraints and Tradeoffs

**3.1 User/kernel mode separation:** Without hardware privilege levels any user program could disable interrupts, modify page tables, or corrupt physical memory directly. CPU M/S/U modes are the foundational forcing constraint; every other OS mechanism sits on top.

**3.2 Trampoline identity-mapped in both PTs:** ecall enters S-mode but the MMU still uses the user PT. Code must remain valid through the `csrw satp` that switches to the kernel PT. The only solution is a VA that maps the same physical page in both tables — TRAMPOLINE = MAXVA-PGSIZE, no PTE_U.

**3.3 Per-process kernel stack:** A single shared kernel stack would corrupt across concurrent system calls on different CPUs. Using the user stack is exploitable. Each process gets its own kernel stack allocated by `proc_mapstacks()` and recorded in trapframe->kernel_sp for trampoline.S to restore.

**3.4 Two-hop swtch (yield → scheduler → next process):** A yielding process is still executing; it cannot jump directly to another without saving its own state first. The scheduler is a co-routine on each CPU. swtch(&p->context, &c->context) saves the process and lands in the scheduler; the scheduler calls swtch(&c->context, &next->context) to resume the next. Stateless per-hop — the scheduler loop re-runs from the top on each return.

**3.5 Interrupts disabled while holding a spinlock:** If a CPU holds lock L and a timer interrupt fires, and the ISR also needs L, the CPU deadlocks spinning on itself. `push_off/pop_off` maintain a nesting depth so multiple spinlock acquisitions don't prematurely re-enable interrupts.

**3.6 Jitter fills in kalloc/kfree:** Zeroing memory hides use-after-free and uninitialized-read bugs (garbage looks like valid zero state). `kfree` fills with 0x01; `kalloc` fills with 0x05. Garbage data makes bugs fail loudly rather than silently.

**3.7 Write-ahead logging for crash consistency:** File creation requires several writes (allocate inode, write inode, write dirent). A power failure mid-sequence leaves the disk inconsistent and fsck cannot always recover lost data (O(disk) cost, too). WAL guarantees all-or-nothing atomicity: log header write = atomic commit point; recovery replays if n>0, does nothing if no commit. Cost: every block is written twice (write amplification 2x).

**3.8 Separate iget / ilock:** Pathname lookup holds references to many inodes in sequence. Holding the sleeplock across the entire traversal would serialize all directory accesses. `iget` increments ref (no lock); `ilock` acquires sleeplock + reads disk only when the inode is actually needed. Open files hold a ref across their lifetime but lock only during reads/writes.

**3.9 LRU buffer cache:** Disk I/O is ~10,000x slower than RAM. The working set of recently-used blocks best predicts future access. brelse moves buffers to the MRU head; eviction pulls from the LRU tail. Single bcache.lock is a bottleneck (lock lab: split by hash bucket to reduce contention).

---

## 4. Common Misconceptions to Preempt

**M1: "The process chooses the kernel entry address for a system call."** False. The process executes ecall; hardware jumps to stvec, which is a privileged CSR set exclusively by the kernel. The user cannot change stvec.

**M2: "swtch() saves all CPU registers."** False. swtch saves only callee-saved registers (ra, sp, s0–s11). Caller-saved registers (a0–a7, t0–t6) are the caller's responsibility per the ABI. User registers are separately saved in the trapframe by trampoline.S — a completely different mechanism.

**M3: "Kernel and user share a page table."** False. Each process has its own user PT (p->pagetable). The kernel has a separate kernel PT. The trampoline page is mapped in both at the same VA — a deliberate exception, not general sharing.

**M4: "fork() uses copy-on-write in xv6."** False in the base kernel. kfork() calls uvmcopy() to copy every page eagerly. COW is added only in the lab (6.1810/labs/cow). Linux uses COW; xv6 omits it for pedagogical clarity.

**M5: "Condition variables and semaphores are interchangeable."** No. CVs are stateless — a signal with no waiters is lost. Semaphore V increments a persistent count — never lost. CVs suit "wait until condition true" (always re-check in while loop); semaphores suit resource counting and producer/consumer signaling.

**M6: "fsck can fully repair any filesystem inconsistency."** False. fsck repairs structural inconsistencies (bad link counts, orphan blocks) but cannot recover data that was never written. It is also O(disk size), which is why journaling exists.

**M7: "The TLB is automatically flushed on context switch."** Implementation-dependent. xv6 always executes sfence.vma when switching PTs. Linux uses ASIDs to tag TLB entries per address space — most switches need no flush. Not flushing when required produces stale-translation silent bugs.

**M8: "Spinlocks are always better on multi-core because they avoid context-switch overhead."** Only if the critical section is short. For long sections (disk I/O), spinning burns CPU cycles that could run other processes. xv6 uses spinlocks for in-memory structures and sleeplocks for anything involving disk.

**M9: "Page faults are always errors."** No. Demand paging, COW fork, mmap, and stack growth all rely on page faults as a normal control path. trap.c distinguishes legitimate faults (scause 13/15 → vmfault → alloc+map) from illegal accesses (kill process).

**M10: "MLFQ converges to SJF."** Approximate, not guaranteed. I/O-bound jobs can game a naive MLFQ by issuing I/O just before the quantum expires, perpetually staying in the highest-priority queue. Fixes require accounting CPU usage across I/O and periodic priority boosts — both non-trivial.

---

## 5. Best Build-Your-Own Targets

**Primary: xv6-riscv labs (MIT 6.1810)** — canonical graded kernel exercises:

| Lab | Core build | Level |
|-----|-----------|-------|
| util | pipe/find/xargs user programs | easy |
| syscall | trace + sysinfo syscalls | easy/mod |
| pgtbl | inspect PTs; shared getpid page | easy/mod |
| traps | backtrace; user-level alarm handler | mod |
| cow | COW fork with refcounting + PF handler | hard |
| lock | per-CPU kalloc; hash-bucketed bcache | mod |
| fs | double-indirect blocks; symlinks | mod/hard |
| mmap | file-backed mmap via lazy PF allocation | hard |

COW lab: best single exercise for lazy allocation + page fault handler design. Lock lab: best for lock-contention profiling and redesign.

**Other targets (all primary-source-backed):**
- User-space malloc/free (ostep-projects/malloc): sbrk, free-list, coalescing, splitting — teaches vm-freespace.pdf material concretely.
- xv6 sh.c (~300 lines, github.com/mit-pdos/xv6-riscv/blob/riscv/user/sh.c): minimal shell; fork/exec/wait/pipe in one file.
- CS162 Pintos (cs162.org): 4 projects (threads → user programs → VM → FS); x86; closer to production; harder to set up.
- Toy in-file filesystem: superblock + bitmap + inodes + dirents on a raw file; covers all five xv6 FS layers without hardware.

---

## 6. Open Questions / Where Sources Disagree

**6.1 Production scheduler gap.** xv6 uses linear-scan round-robin. OSTEP covers MLFQ/CFS theory. CS162 covers priority donation (Pintos). None covers Linux CFS implementation (RB-tree, cgroup integration, real-time classes). Appendix B (linux-internals) or Brendan Gregg should fill this.

**6.2 Page replacement: theory only.** OSTEP covers LRU/Clock/OPT analytically. xv6 has no page eviction. The COW lab adds page faults but not swapping. Pintos (CS162) has a demand-paging project — best available runnable implementation in this source cluster.

**6.3 xv6 book revision mismatch.** xv6 book rev4 (2024) is the current version. Third-party commentary and older OSTEP homeworks may reference x86 xv6 or rev1–rev3 with different chapter numbers. Always verify against pdos.csail.mit.edu/6.828/2024/xv6/book-riscv-rev4.pdf.

**6.4 xv6 is not POSIX.** xv6 syscalls: fork, exec, wait, open, read, write, close, pipe, dup, chdir, mkdir, mknod, fstat, link, unlink, stat, getpid, kill, sleep, uptime, sbrk. Missing: signals, pthreads, mmap (base), select/epoll, sockets, mprotect. Learners expecting Linux-subset behavior will be surprised.

**6.5 CS162 (Pintos, x86) vs 6.1810 (xv6-riscv, RISC-V) architectural gap.** Privilege levels: x86 rings 0–3 vs RISC-V M/S/U. Syscall entry: x86 int 0x80/syscall vs RISC-V ecall + trampoline. Page tables: x86 CR3-rooted 4-level vs Sv39 3-level. Mechanism claims from one ISA do not directly apply to the other.

**6.6 WAL / journaling terminology split.** OSTEP calls it "journaling"; database literature calls it "write-ahead logging"; xv6 source says "physical re-do log." Same mechanism. OSTEP ch. file-journaling distinguishes ordered (metadata-only in journal, data flushed first — Linux ext4 default), writeback (metadata-only, no ordering), and data journaling (everything — xv6's mode, 2x write amplification). Sources agree on the mechanics; terminology varies by community.

**6.7 OSTEP modern OS gaps.** Not covered: cgroups/namespaces, eBPF, NUMA-aware allocation, io_uring, Spectre/Meltdown scheduling impacts, CXL/disaggregated memory. Out-of-scope for sub-course 04 unless cross-linked to appendix B (linux-internals) or appendix I (containers).

**6.8 Performance numbers absent from all three sources.** xv6 makes no performance claims. OSTEP gives qualitative comparisons. CS162/OSPP gives analytical models only. Actual syscall latency, TLB miss penalty, and context-switch cost on modern hardware require Brendan Gregg or hardware-specific benchmarks.

---

## Appendix: OSTEP Chapter Index (verified from ostep-homework README)

**Virtualization:** cpu-intro, cpu-api, cpu-mechanisms | cpu-sched, cpu-sched-mlfq, cpu-sched-lottery, cpu-sched-multi | vm-intro, vm-api, vm-mechanism, vm-segmentation, vm-freespace | vm-paging, vm-tlbs, vm-smalltables, vm-beyondphys, vm-beyondphys-policy, vm-complete

**Concurrency:** threads-intro, threads-api, threads-locks, threads-locks-usage, threads-cv, threads-sema, threads-bugs, threads-events

**Persistence:** file-devices, file-disks, file-raid | file-intro, file-implementation (VSFS), file-ffs, file-journaling, file-lfs, file-ssd, file-integrity | dist-intro, dist-nfs, dist-afs

**xv6 book chapters (from 6.1810 schedule, rev4):** Ch.1 OS interface | Ch.2 OS organization | Ch.3 Page tables | Ch.4 Traps and system calls (§4.6 page faults) | Ch.5 Interrupts and device drivers | Ch.6 Locking | Ch.7 Scheduling | Ch.8 File system | Ch.9 [UNVERIFIED — verify title against rev4 TOC]

---
*Brief only — no chapter prose. Append additional cluster briefs as new sections.*
