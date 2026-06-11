# Appendix I · docker-containers-cgroups-namespaces — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). Verifies the load-bearing
> claims of I against **just-reconciled appendix B** (namespaces + cgroups v2 substrate) plus **04**
> (clone, COW, page cache, PID/signals), **A** (shared kernel / no guest OS), **03** (TCP/IP for the
> network namespace), **13** (latency), **N** (math). **NO new primary fetched this wave** —
> docs.docker.com / kernel hosts HTTP **000** (re-checked Wave 18); the runtime is described entirely
> in terms of B's line-verified kernel primitives. Every quantitative claim re-derived in
> `_recompute.py` (12/12). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | Container shares the host kernel → no per-guest OS → ~100× less memory + ms (not s) start vs a VM | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #1,#2; B/A (shared kernel; container = process) |
| 2 | A container is a **composition** of 4 primitives (namespaces + cgroups + overlayfs + caps/seccomp), not one kernel object | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #2; B §2 layer 5 |
| 3 | **overlayfs** = N read-only image layers + 1 writable upper; reads fall through; file-granularity COW on write | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #3,#4; 04 COW + B page cache (overlay copy-up is the file-level analogue) |
| 4 | Content-addressed **layer sharing** dedups the common base across images (stable base first = cache hits) | RECOMPUTED | `_recompute.py` #5; 04 page-cache/content-addressing concept |
| 5 | **cgroup cpu.max** throttles a CPU-bound container to quota/period → throttle-induced latency spikes | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #6; B §2 layer 5 (cpu.max quota/period) |
| 6 | **cgroup memory.max** → per-container OOM kill (host survives) — the isolation/reliability story | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #7; B §2 (memory.max hard cap → per-cgroup OOM) |
| 7 | **Network namespace** + veth pair + bridge + NAT → each container gets its own TCP/IP stack & can bind :80 | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #8; B (net namespace) + 03 (TCP/IP) |
| 8 | **Capabilities + seccomp** drop privilege + shrink syscall attack surface; `--privileged` removes it (footgun) | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #9; B (eBPF/verifier + user ns); seccomp count illustrative |
| 9 | A hand-rolled container ≈ **4 syscalls** (clone NEW* + pivot_root + cgroup write + execve); Docker orchestrates | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #10; 04 clone + B namespaces/cgroups |
| 10 | Container entrypoint is **PID 1** → must reap zombies + handle signals → WHY `--init`/tini exists | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #11; 04 §1 PID/signal semantics (SIGKILL/SIGSTOP, reaping) |
| 11 | Runtime stack: image (OCI) → runc (spawns the namespaced process) → containerd → dockerd/CLI | VERIFIED (reuse, structural) | B kernel primitives + 04 process model; OCI/runc *spec text* `[UNVERIFIED]` (docs not fetched) |
| 12 | This is exactly the unit appendix **J** (Kubernetes) schedules: pod = co-located containers sharing namespaces | VERIFIED (reuse, forward-link) | B → I → J chain; J detail deferred to its own appendix |

## `[UNVERIFIED]` carry-forward (none load-bearing — recomputed or reused from B/04's line-cited reads)
- **docs.docker.com / OCI runtime+image spec / runc + containerd source** — hosts HTTP **000** this
  wave. The *mechanisms* are reused from B's line-verified namespaces+cgroups reads; Docker/OCI-specific
  naming (storage drivers, exact CLI→cgroup mapping, OCI JSON schema) is structural until a fetch heals.
- **Docker default seccomp profile exact denylist size** — order-of-magnitude only; exact count
  version-specific.
- **VM-vs-container absolute overhead/boot numbers** — illustrative order-of-magnitude (the *ratio*
  "shared kernel ⇒ far cheaper" is the load-bearing claim, recomputed).
- **overlayfs internals** (whiteouts, opaque dirs, metacopy, page-cache sharing across containers) —
  structural description; exact driver behavior `[UNVERIFIED]`.
- **rootless containers / cgroup-v1-vs-v2 differences / gVisor-Kata stronger isolation** — flagged as
  appendix-I depth; described conceptually, exact mechanics not fetched.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 12/12); the
entire runtime is explained in terms of appendix B's line-verified kernel primitives. Forward-links
cleanly into appendix J (kubernetes).
