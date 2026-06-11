# Appendix J · kubernetes-internals — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). Verifies the load-bearing
> claims of J against **just-reconciled appendix I** (the container unit) + **B** (cgroups
> requests/limits) and **line-verified spine canon** — **11** (consensus/quorum/partial-failure/
> happened-before), **15** (replication/lag), **20** (failure model, fan-out tail, headroom), **L**
> (Raft/quorum), **10/03** (Service LB / TCP), **13/N** (latency/math). **NO new primary fetched this
> wave** — kubernetes.io / etcd docs HTTP **000** (re-checked Wave 18); the orchestrator is described
> entirely via 11/15/20 + L + I canon. Every quantitative claim re-derived in `_recompute.py` (13/13).
> Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | K8s core = **reconciliation loop**: observe(actual) vs desired → act; converges, self-heals | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #1; 20 (control loop), 19 (sense/act) |
| 2 | Controllers are **level-triggered** (re-read full state) → survive missed events; edge would not | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #1; 11 (no reliable delivery / partial failure) |
| 3 | **etcd = Raft**; control-plane writes need a **majority quorum**; 3 tolerate 1, 5 tolerate 2; odd sizes | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #2; 11 §1 consensus, L (Raft/quorum) |
| 4 | Even cluster sizes give no extra fault tolerance (4 ≈ 3) → WHY 3/5 etcd members | RECOMPUTED | `_recompute.py` #2; 11/L quorum math |
| 5 | **Scheduler** places a pod iff Σ(requests)+pod ≤ node allocatable → Pending/autoscale otherwise | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #3; B/I (cgroup requests), 13/20 (bin-packing/headroom) |
| 6 | **requests** = scheduling reservation; **limits** = cgroup cap (throttle/OOM) → QoS class drives eviction | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #3; I §2 (cpu.max/memory.max), B |
| 7 | A **pod** = co-located containers sharing net+ipc ns (localhost/volumes); pause holds the ns | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #4; I (namespaces; container as unit) |
| 8 | A **Service** = stable VIP over Ready endpoints; kube-proxy LB spreads ~1/N; pods are ephemeral | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #5; 10 (LB), 03 (TCP/VIP) |
| 9 | **Liveness** fail → restart; **readiness** fail → pull from endpoints (no restart) — distinct responses | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #6; 20 (failure handling), 19 (health signals) |
| 10 | **Rolling update**: maxSurge/maxUnavailable bound capacity; ≥ desired−maxUnavailable always serving | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #7; 20 (headroom/capacity), 13 |
| 11 | The apiserver is a **fan-out hub**: N kubelets watch it → P(≥1 slow) = 1−(1−p)^N → needs rate limits/APF | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #8; 20 (fan-out tail 63.4%) |
| 12 | K8s is **declarative + eventually consistent**: apply acks on etcd write; convergence is async (reconcile lag) | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #9; 15 (replication/propagation lag), 11 |
| 13 | **Node failure** = silent ≈ slow (11) → eviction waits a grace window (~300s); failover not instant | RECOMPUTED + VERIFIED (reuse) | `_recompute.py` #10; 11 (no perfect failure detector), 20 |

## `[UNVERIFIED]` carry-forward (none load-bearing — recomputed or reused from I/11/15/20/L)
- **kubernetes.io docs / k8s + etcd source / Borg paper (Verma 2015) / OCI CRI spec** — hosts HTTP
  **000** this wave. The *mechanisms* (controller pattern, Raft quorum, scheduler predicates, Service
  VIP, probes) are reused from spine 11/15/20 + L + appendix I; k8s-specific API/object naming
  (Deployment/ReplicaSet/StatefulSet/DaemonSet semantics, exact predicate/priority plugins, APF
  config) is structural until a fetch heals.
- **Default constants** (node-not-ready toleration ~300 s, kubelet eviction thresholds, default
  maxSurge/maxUnavailable 25%, scheduler scoring weights) are **version/config-dependent** — taught as
  *mechanism with arithmetic*, not fixed numbers.
- **CNI / kube-proxy modes (iptables vs IPVS vs eBPF/Cilium), CSI storage, admission webhooks,
  operators/CRDs depth, HPA/VPA/cluster-autoscaler control theory** — flagged as appendix-J depth;
  described conceptually, exact mechanics not fetched.
- **etcd internals** (MVCC revisions, compaction, watch streams, lease/TTL) reuse the Raft/quorum +
  MVCC canon from 11/L/F; etcd-specific layout `[UNVERIFIED]`.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 13/13); the
orchestrator is explained as the distributed-systems laws of spine 11/15/20 + L applied to appendix I's
container unit. Closes the B → I → J arc.
