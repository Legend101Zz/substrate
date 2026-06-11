# Appendix I · docker-containers-cgroups-namespaces — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). I is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for **"what IS a container,
> mechanically?"** — and the answer is the punchline appendix **B** set up: a container is a *process*
> wearing **namespaces** (what it can see) + **cgroups** (what it can use) + a **union/overlay
> filesystem** (what it runs on) + a **capabilities/seccomp** profile (what it can do). I sits directly
> ON appendix B (which reconciled the namespaces+cgroups substrate) and **A** (shared kernel / no guest
> OS), reuses spine **03** (TCP/IP) for the network namespace and **04** (clone/COW/PID), and is the
> unit appendix **J** (Kubernetes) schedules. Spine chapters (and B) cross-link DOWN into I for the
> concrete runtime. **Bespoke structure: deconstruct a running container into the 4 independent kernel
> primitives that compose it, then reassemble it by hand** — a "there is no container" teardown, NOT
> four clusters, NOT a build progression. Math: `_recompute.py` (12/12). Factcheck:
> `_factcheck_phase1.md` (0 blockers). Network: docs.docker.com / OCI hosts HTTP **000** this wave →
> the runtime is described entirely via B's line-verified kernel primitives; nothing new hardened.

## 1. Thesis
**There is no "container" kernel object.** A container is an *emergent illusion* composed from four
independent Linux primitives, each of which appendix B already explained. The forcing function is the
gap a VM leaves: a VM isolates by shipping a whole guest kernel+OS per instance (strong isolation, but
GBs of RAM and seconds to boot); most workloads only need to *look like* they have their own machine
while *sharing* the host kernel. So Linux lets a single process (a) **see** a private set of resources
(namespaces), (b) **use** a bounded slice of them (cgroups), (c) **run on** a cheap layered filesystem
(overlayfs), and (d) **do** only a safe subset of operations (capabilities + seccomp). Docker is not a
kernel feature — it's an orchestrator that wires those primitives together and adds image distribution,
networking, and lifecycle on top.

## 2. Deconstructing a running container (the bespoke spine)

### Primitive 0 — Why not a VM? (A/B)
- VM = guest kernel + OS per instance → RECOMPUTED ~100× more per-instance memory overhead and
  seconds-vs-milliseconds start (container start is *process*-fast because there's no kernel to boot).
- The trade is **isolation strength**: containers share the host kernel, so a kernel vulnerability is a
  shared attack surface (→ why capabilities/seccomp/user-ns matter, and why gVisor/Kata exist for
  stronger isolation). This is the whole reason the appendix is *honest about the cost*, not a sales
  pitch.

### Primitive 1 — What it can SEE: namespaces (B → here)
- Eight composable namespace types (pid/net/mnt/uts/ipc/user/cgroup/time). Each virtualizes one class
  of kernel-visible identifiers.
- **PID namespace**: the entrypoint becomes **PID 1**. RECOMPUTED consequence: PID 1 has no default
  SIGTERM action and must **reap orphaned zombies** → WHY a naive PID 1 leaks zombies and ignores
  `docker stop`, and WHY `--init`/tini exists.
- **Network namespace**: each container gets its own interfaces/routes/iptables; a **veth pair**
  bridges it to the host over `docker0`, and `-p 8080:80` is host NAT → WHY every container can bind
  `:80` without conflict (reuses spine 03's TCP/IP).
- **Mount namespace** + `pivot_root` give it a private filesystem tree (the image rootfs).

### Primitive 2 — What it can USE: cgroups v2 (B → here)
- **cpu.max "quota period"**: RECOMPUTED `25000 100000` = 25% of one CPU → a busy loop runs 25 ms then
  is **throttled** for 75 ms each period → WHY CPU *limits* cause latency spikes (throttle stalls), a
  subtle production footgun.
- **memory.max**: a hard cap → RECOMPUTED exceeding it triggers the *container's* cgroup OOM kill, not
  the host's → WHY one leaky container can't take down the node (the reliability story that appendix J
  schedules around).

### Primitive 3 — What it RUNS ON: the union/overlay filesystem (04/B)
- An image = N **read-only** layers (content-addressed); the container adds **1 writable upper** layer.
  Reads fall through the lowerdirs. RECOMPUTED layer sharing: 10 images on a 200 MB base cost 400 MB
  (shared) vs 2200 MB (naive) — 5.5× less → WHY stable-base-layer ordering maximizes cache/page-cache
  hits.
- **Copy-up COW**: the first write to a file in a lower layer copies the *whole file* up (file
  granularity, unlike fork's page granularity). RECOMPUTED editing a 100 MB lower-layer file copies
  100 MB up → WHY big mutable data belongs on **volumes**, not the image layer.

### Primitive 4 — What it can DO: capabilities + seccomp (B → here)
- **User namespace** + dropped **capabilities** mean root-in-container ≠ root-on-host. **seccomp**
  filters the syscall surface (Docker's default profile blocks dozens of the ~350 syscalls).
  RECOMPUTED: this hardens the shared-kernel attack surface; `--privileged` removes it (the big
  footgun). This is the same "constrain the kernel interface" idea as B's eBPF verifier, applied to a
  sandbox.

### Reassembly — build a container by hand (04/B)
- RECOMPUTED a hand-rolled container ≈ **4 syscalls**: `clone(CLONE_NEW* flags)` + `pivot_root` +
  write `cpu.max`/`memory.max` + `execve(app)`. Everything Docker/runc adds — image pull/unpack, OCI
  spec, networking, lifecycle, an API — is *orchestration around this 4-call core*. WHY "containers are
  not magic."
- Runtime stack (structural): OCI **image** → **runc** (spawns the namespaced+cgrouped process) →
  **containerd** → **dockerd**/CLI. OCI/runc spec *text* `[UNVERIFIED]` (docs not fetched).

## 3. The "one illusion, four primitives" reconciliation (appendix payload)
| primitive | question it answers | mechanism | load-bearing number | anchor |
|---|---|---|---|---|
| namespaces | what can it SEE? | pid/net/mnt/... isolation | 8 types; PID 1 reaping; veth :80 | B/04/03 |
| cgroups v2 | what can it USE? | cpu.max / memory.max | 25% throttle; per-ctr OOM | B |
| overlayfs | what does it RUN ON? | RO layers + writable upper, copy-up | 5.5× base dedup; 100 MB copy-up | 04/B |
| caps+seccomp | what can it DO? | drop caps + filter syscalls | ~44/350 blocked; --privileged footgun | B |
| (reassembly) | how is it built? | clone+pivot_root+cgroup+exec | ~4 syscalls | 04/B |

## 4. Common misconceptions to preempt
- "A container is a lightweight VM." No guest kernel — it's a process in namespaces+cgroups sharing the
  host kernel; isolation is weaker and composable, not all-or-nothing.
- "Docker is a kernel feature." The kernel provides the primitives; Docker/runc orchestrate them.
- "Containers are fully isolated/secure." Shared kernel = shared attack surface; security comes from
  caps/seccomp/user-ns (and `--privileged` throws it away).
- "Writing to a file in the image is cheap." First write copies the whole file *up* (overlay COW).
- "A CPU limit just slows the container down smoothly." `cpu.max` *throttles* — the container stalls at
  period boundaries, causing latency spikes.
- "PID 1 in a container is normal." It must reap zombies and handle signals itself → use an init.
- "Each container needs its own OS image bloat." Read-only base layers are shared/deduped across
  containers and images.
- "Containers can't all use port 80." Each net namespace has its own stack; host port-publish NATs.

## 5. Provenance summary
- **REUSED (line-verified in appendix B):** namespaces (8 types, composition), cgroups v2 (cpu.max /
  memory.max → per-cgroup OOM), the "container = process + ns + cgroups" framing, the syscall-cost /
  shared-kernel argument.
- **REUSED:** 04 (clone, COW, PID/signal semantics, page cache), A (shared kernel / no guest OS), 03
  (TCP/IP for net namespace), 13 (latency), N (math).
- **RECOMPUTED:** `_recompute.py` (12/12) — VM-vs-container overhead/start, 4-primitive composition,
  overlay RO+writable + copy-up, layer dedup, cpu.max throttle, memory.max per-ctr OOM, net-ns/veth,
  seccomp/caps surface, ~4-syscall hand-roll, PID-1 reaping.
- **`[UNVERIFIED]` carry-forward (not load-bearing):** docs.docker.com / OCI image+runtime spec / runc
  + containerd source (hosts 000); Docker default seccomp denylist exact size; VM/container absolute
  overhead numbers (ratios are the claim); overlayfs internals (whiteouts/metacopy); rootless / cgroup
  v1-vs-v2 / gVisor-Kata depth. All blocked behind unreachable hosts; logged, none hardened.

---
**Appendix I reconciled.** Reference-grade, exercise-free, 12/12 recomputed, the entire runtime
explained via appendix B's line-verified kernel primitives. Forward-links into appendix J (kubernetes).
No chapters yet.
