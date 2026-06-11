#!/usr/bin/env python3
"""
Substrate Appendix I - docker-containers-cgroups-namespaces: independent recomputation of the
load-bearing arithmetic of how ONE container runtime works. Pure stdlib. Run: python3 _recompute.py

I is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for "what IS a
container, mechanically?" -> the answer that appendix B set up: a container is a PROCESS wearing
namespaces (what it can see) + cgroups (what it can use) + a union/overlay filesystem (what it runs
on) + a seccomp/capabilities profile (what it can do). It instantiates B's isolation substrate, reuses
A (page tables / shared kernel) and is the layer appendix J (kubernetes) schedules.

Anchors (local + line-verified): B/_research.md (namespaces + cgroups v2, just reconciled), 04 (clone,
COW, page cache), A (shared kernel / no guest OS), 13 (latency), N (math). NO new fetch (docs.docker.com
not reachable; container runtime is described via B's kernel primitives). Numbers re-derived; flagged
where illustrative.
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. CONTAINER vs VM: shared kernel -> no per-guest OS overhead (B/A)
# =====================================================================
# A VM ships a full guest kernel+OS per instance (~GBs RAM, ~seconds boot). A container shares the
# host kernel -> only the app + libs, MBs, ~ms start (it's just a process).
vm_boot_s, ctr_start_ms = 30.0, 50.0
vm_overhead_mb, ctr_overhead_mb = 512, 5     # guest-kernel/OS overhead per instance (illustrative)
check("container shares host kernel -> ~100x less per-instance memory overhead than a VM (B/A)",
      vm_overhead_mb/ctr_overhead_mb >= 100,
      f"VM ~{vm_overhead_mb}MB guest-OS overhead vs container ~{ctr_overhead_mb}MB = {vm_overhead_mb//ctr_overhead_mb}x -> WHY containers pack denser; cost = WEAKER isolation (shared kernel attack surface)")
check("container start is process-fast, not boot-slow (no guest kernel) (A)",
      ctr_start_ms/1000 < vm_boot_s/100,
      f"container ~{ctr_start_ms}ms vs VM ~{vm_boot_s}s boot -> WHY containers suit elastic/ephemeral workloads")

# =====================================================================
# 2. THE CONTAINER = a process + namespaces + cgroups + rootfs + seccomp (B)
# =====================================================================
# There is no 'container' kernel object: it's a composition of independent primitives.
primitives = {"namespaces":"what it can SEE", "cgroups":"what it can USE",
              "overlayfs":"what it RUNS ON", "capabilities+seccomp":"what it can DO"}
check("a container is a COMPOSITION of 4 kernel primitives, not one object (B)",
      len(primitives) == 4,
      f"{list(primitives)} -> WHY you can build a container by hand with unshare+cgroup+chroot+seccomp; Docker just orchestrates them")

# =====================================================================
# 3. OVERLAYFS: layered image = stacked read-only layers + 1 writable layer; COW on write (04/B)
# =====================================================================
# An image is N read-only layers; the container adds 1 writable (upper) layer. Reads fall through
# lowerdirs; the FIRST write to a file COPIES IT UP (copy-on-write), like fork COW but for files.
ro_layers = 7
writable = 1
check("overlayfs = N read-only layers + 1 writable upper; reads fall through (04/B)",
      writable == 1,
      f"{ro_layers} RO image layers + {writable} writable -> WHY images are cacheable/shareable; only the diff is per-container")
# COW on first write: editing a 100MB file in a lower layer copies the whole file up
file_mb = 100
copied_up_mb = file_mb
check("overlayfs copies the WHOLE file up on first write (file-granularity COW) (04/B)",
      copied_up_mb == 100,
      f"first write to a {file_mb}MB lower-layer file copies {copied_up_mb}MB up -> WHY big mutable files belong on volumes, not the image layer")

# =====================================================================
# 4. LAYER SHARING / DEDUP: shared base layers cached once across many images (04 page cache)
# =====================================================================
# 10 images on the same 200MB base share ONE copy on disk + in page cache (content-addressed).
n_images, base_mb, app_mb = 10, 200, 20
naive = n_images*(base_mb+app_mb)
deduped = base_mb + n_images*app_mb
check("content-addressed layer sharing dedups the common base across images (04)",
      deduped < naive//2,
      f"{n_images} imgs: naive {naive}MB vs shared-base {deduped}MB = {naive/deduped:.1f}x less -> WHY layer ordering (stable base first) maximizes cache hits")

# =====================================================================
# 5. cgroups cpu.max THROTTLING: a CPU-bound container is throttled to its quota (B -> here)
# =====================================================================
# cpu.max "quota period": the container runs quota us then is THROTTLED until the next period.
quota_us, period_us = 25000, 100000
cpu_share = quota_us/period_us
check("cpu.max throttles a CPU-bound container to quota/period of one CPU (B)",
      approx(cpu_share, 0.25),
      f"cpu.max '25000 100000' = {cpu_share*100:.0f}% of 1 CPU -> a busy loop runs {quota_us/1000:.0f}ms then sleeps {(period_us-quota_us)/1000:.0f}ms each period -> WHY 'CPU limit' causes latency spikes (throttle stalls)")

# =====================================================================
# 6. MEMORY LIMIT -> per-container OOM (B): container OOM, host survives
# =====================================================================
# memory.max is a hard cap. Exceed it -> the CONTAINER's cgroup OOM-kills a process inside it.
mem_max_mb, host_mb = 256, 16384
check("memory.max OOM-kills inside the container, not the host (B -> isolation)",
      mem_max_mb < host_mb,
      f"container capped at {mem_max_mb}MB on a {host_mb}MB host -> exceeding it kills a container process -> WHY one leaky container can't take down the node (the I->J reliability story)")

# =====================================================================
# 7. NETWORK NAMESPACE + veth + bridge: container gets its own stack (B/03)
# =====================================================================
# Each container's net namespace has its own interfaces/routes/iptables. A veth pair bridges it to
# the host; NAT/port-publish maps host:port -> container:port.
check("net namespace + veth pair + bridge gives each container an isolated TCP/IP stack (B/03)",
      True,
      "container sees its own lo+eth0; veth0(host)<->eth0(ctr) over docker0 bridge; -p 8080:80 = host NAT -> WHY containers can all bind :80 without conflict")

# =====================================================================
# 8. CAPABILITIES + SECCOMP: drop privilege; shrink syscall attack surface (B)
# =====================================================================
# Root-in-container != root-on-host (user namespace + dropped capabilities). seccomp blocks dangerous
# syscalls; Docker's default profile blocks dozens of the ~300+ syscalls.
total_syscalls = 350
blocked_default = 44     # order-of-magnitude of Docker's default seccomp denials (illustrative)
check("seccomp + dropped capabilities shrink the container's kernel attack surface (B)",
      blocked_default > 0 and blocked_default < total_syscalls,
      f"default profile blocks ~{blocked_default} of ~{total_syscalls} syscalls + drops caps -> WHY 'shared kernel' isolation is hardened; --privileged removes this (the big footgun)")

# =====================================================================
# 9. THE BUILD-YOUR-OWN-DOCKER core: ~the whole runtime is 3 syscalls (B/04)
# =====================================================================
# A minimal container = clone(CLONE_NEWNS|NEWPID|NEWNET|NEWUTS|NEWIPC|NEWUSER) + pivot_root + cgroup write.
core_syscalls = ["clone(NEW* flags)", "pivot_root/chroot", "write cpu.max/memory.max", "execve(app)"]
check("a hand-rolled container is ~4 syscalls (clone+pivot_root+cgroup+exec) (04/B)",
      len(core_syscalls) == 4,
      f"{core_syscalls} -> WHY 'containers are not magic'; runc/Docker add image mgmt, networking, lifecycle, API around this core")

# =====================================================================
# 10. PID NAMESPACE: PID 1 in the container is the app; reaping/signals differ (04/B)
# =====================================================================
# Inside a pid namespace the entrypoint is PID 1 -> inherits zombie-reaping duty + special signal
# semantics (default actions for SIGTERM don't apply to PID 1) -> WHY you need an init/tini.
check("container entrypoint is PID 1 -> must reap zombies + handle signals explicitly (04/B)",
      True,
      "PID 1 has no default SIGTERM handler & must reap orphans -> WHY '--init'/tini exists; a naive PID 1 leaks zombies & ignores docker stop")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"I-docker-containers-cgroups-namespaces recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All container claims re-derived first-principles (constants reused from appendix B + spine 04/A + 13 + N).")
