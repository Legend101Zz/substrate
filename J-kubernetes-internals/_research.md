# Appendix J · kubernetes-internals — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). J is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for **"what IS Kubernetes,
> mechanically?"** — and the answer reuses everything below it: Kubernetes is a fleet of
> **reconciliation loops** (the controller pattern) driving the container unit from appendix **I**
> toward a *declared desired state*, backed by a strongly-consistent store (**etcd = Raft**), governed
> by the exact distributed-systems laws spine **11** (consensus/time/partial failure), **15**
> (replication/lag) and **20** (resilience/failure/fan-out) already taught. J sits ON appendix I (the
> scheduled unit) and **B** (cgroup requests/limits), and reuses **10/03** (Service LB) + **L**
> (Raft/quorum). **Bespoke structure: Kubernetes as ONE pattern (the reconciliation loop) applied at
> every layer — store → schedule → run → expose → heal → roll** — a "it's loops all the way down"
> walkthrough, NOT four clusters, NOT a build progression. Math: `_recompute.py` (13/13). Factcheck:
> `_factcheck_phase1.md` (0 blockers). Network: kubernetes.io / etcd docs HTTP **000** this wave → the
> orchestrator is described entirely via 11/15/20 + L + I canon; nothing new hardened.

## 1. Thesis
Kubernetes looks like a sprawling product, but it is **one idea repeated**: a **reconciliation loop**
that continuously compares *desired state* (declared specs in etcd) to *actual state* (observed
status) and takes one step to close the gap. Every "feature" — the scheduler, the deployment
controller, the service endpoints controller, the node lifecycle controller — is another instance of
that loop. The forcing function is appendix I's honesty: a container is just a process on a shared
kernel, easy to start and easy to lose; at fleet scale across unreliable machines you need something
to *keep declaring what should be true and relentlessly making it true again* — which is exactly a
control loop over a distributed system, so K8s inherits every law from spine 11/15/20 (no free
"now," majority quorum, no perfect failure detector, fan-out tail, capacity headroom).

## 2. It's loops all the way down (the bespoke spine)

### Layer 0 — The pattern: the reconciliation loop (20)
- A controller repeatedly: read **desired** (spec) → read **actual** (status) → diff → take one step
  toward desired. RECOMPUTED: desired 5 replicas, actual 2 → create 3. Delete a pod and the gap simply
  reopens and the next loop refills it → **self-healing is free**, it's just the loop running again.
- Crucially controllers are **level-triggered** (re-read the *whole* current state), not
  edge-triggered (react to events). RECOMPUTED: lose the "pod died" event and the next loop still
  re-reads actual=0 and acts → WHY K8s is robust to lost/duplicated/reordered events (spine 11: you
  cannot rely on reliable delivery in a distributed system).

### Layer 1 — The store: etcd / Raft (11/L)
- All desired+actual state lives in **etcd**, a **Raft** cluster. A write needs a **majority quorum**.
  RECOMPUTED: 3 nodes → quorum 2, tolerate 1 failure; 5 → tolerate 2; even sizes give no extra
  tolerance (4 ≈ 3, just more latency) → WHY control planes run **3 or 5 (odd)** etcd members. This is
  spine 11/L consensus applied verbatim; the apiserver is the only component that talks to etcd.

### Layer 2 — Place it: the scheduler (B/I/13/20)
- The scheduler binds a Pod to a Node iff the node's remaining **allocatable ≥ Σ(pod requests)**.
  RECOMPUTED: a node with 3500m/9000Mi used can't take a (1000m, 5000Mi) pod (mem 14000 > 16000) →
  **Pending/Unschedulable** → triggers the cluster autoscaler. This is bin-packing (13) over the
  cgroup **requests** from appendix B.
- **requests vs limits** (the I throttle/OOM story made schedulable): *request* = scheduling
  reservation; *limit* = cgroup `cpu.max`/`memory.max` cap. RECOMPUTED their relationship sets the
  **QoS class** (Guaranteed = request==limit; Burstable = request<limit; BestEffort = none), which
  decides eviction order under node pressure.

### Layer 3 — Run it: the pod = the I unit, grouped (I)
- A **Pod** is co-located containers sharing the **net + ipc** namespaces (and optionally pid) → they
  reach each other on **localhost** and share volumes; the **pause** container holds the namespaces so
  app containers can restart without losing the network identity. RECOMPUTED: the pod, not the
  container, is the scheduling unit → WHY sidecars work. Each container inside is exactly appendix I's
  ns+cgroups+overlay+seccomp composition.

### Layer 4 — Expose it: Services & endpoints (10/03)
- Pods are ephemeral (IPs churn). A **Service** is a stable **VIP**; kube-proxy (iptables/IPVS)
  load-balances to the current **Ready** endpoints. RECOMPUTED: 4 ready pods → ~1/N = 25% traffic
  each; a failed pod drops out of endpoints automatically → WHY clients use the Service DNS name,
  never a pod IP. This is spine 10's load balancing over a dynamic backend set.

### Layer 5 — Heal it: probes & node lifecycle (11/20)
- **Liveness** fail → *restart* the container; **readiness** fail → *pull from endpoints* (stop
  routing, don't restart). RECOMPUTED they are distinct responses → WHY a slow-starting app needs
  readiness/startup probes, not a tight liveness probe (which would restart-loop a warming pod).
- **Node failure**: a silent node is indistinguishable from a slow one (spine 11: no perfect failure
  detector). RECOMPUTED K8s waits a **grace window** (~300 s default) before evicting/rescheduling →
  too fast = thrash on a blip, too slow = long outage. Failover is *never* instant — that's the 11 tax,
  not a bug.

### Layer 6 — Change it: rolling updates & the control-plane fan-out (20)
- A **rolling update** bounds capacity with maxSurge/maxUnavailable. RECOMPUTED: desired 10 with
  maxUnavailable=2/maxSurge=2 → always ≥8 Ready, ≤12 total → WHY you need capacity **headroom/quota**
  for surge (maxUnavailable=0 *requires* +maxSurge capacity). This is spine 20's headroom math.
- The **apiserver is a fan-out hub**: every kubelet *watches* it. RECOMPUTED P(≥1 slow watch) =
  1−(1−p)^N = 63.4% at N=100, p=0.01 → WHY the apiserver needs rate limits / API Priority & Fairness;
  a control-plane hiccup is a *correlated* failure across all nodes (spine 20 fan-out tail + correlated
  failure).
- And the whole thing is **declarative + eventually consistent**: RECOMPUTED `kubectl apply` acks on
  the etcd write (~20 ms) but pods become Ready asynchronously (~seconds) — a reconcile-lag window
  exactly like spine 15's replication propagation lag. K8s is not a synchronous RPC; it's a promise the
  loops keep.

## 3. The "one loop, every layer" reconciliation (appendix payload)
| layer | the loop reconciles | inherited law | load-bearing number | anchor |
|---|---|---|---|---|
| store | spec/status durability | majority quorum | 3→tol 1, 5→tol 2, odd | 11/L |
| schedule | pods → nodes | bin-packing/headroom | 14000>16000 = Pending | B/I/13 |
| run | container → pod | shared ns / unit | net+ipc localhost | I |
| expose | VIP → endpoints | load balancing | ~1/N = 25% | 10/03 |
| heal | actual → desired | no perfect detector | ~300 s grace; level-trig | 11/20 |
| roll | old → new safely | capacity headroom + fan-out | ≥8 Ready; 63.4% fan-out | 20 |
| consistency | apply → converge | replication lag | 20 ms ack / 3 s converge | 15/11 |

## 4. Common misconceptions to preempt
- "K8s pushes changes to nodes." It doesn't — controllers/kubelets **pull** desired state and
  reconcile; it's level-triggered, not event-driven RPC.
- "kubectl apply means it's done." Apply only commits desired state to etcd; convergence is async.
- "A pod is a container." A pod is one-or-more containers sharing net+ipc namespaces.
- "Use the pod IP." Pods are ephemeral — address the Service VIP/DNS.
- "Liveness and readiness are interchangeable." Liveness restarts; readiness only de-routes. Confusing
  them causes restart loops or traffic to broken pods.
- "limits == requests." Requests schedule; limits cap (cgroup throttle/OOM). Their relation sets QoS.
- "More etcd nodes = more reliable." Even counts add no tolerance; odd 3/5 is the sweet spot.
- "Failover is instant." A grace window is mandatory because slow ≠ dead (spine 11).
- "The control plane scales for free." The apiserver is a fan-out hub with a correlated-failure /
  tail-latency profile (spine 20).

## 5. Provenance summary
- **REUSED (just-reconciled appendix I):** the container = ns+cgroups+overlay+seccomp unit; pod
  grouping; cgroup requests/limits → throttle/OOM/QoS.
- **REUSED (line-verified spine):** 11 (consensus/quorum, no perfect failure detector, no reliable
  delivery), 15 (replication/propagation lag), 20 (control loop, fan-out tail 63.4%, headroom,
  correlated failure), L (Raft/quorum), 10/03 (Service LB/VIP), B (cgroups), 13/N (bin-packing/math).
- **RECOMPUTED:** `_recompute.py` (13/13) — reconcile convergence + level-triggering, etcd quorum/odd
  sizing, scheduler request-fit, pod shared-ns, Service 1/N, liveness-vs-readiness, rolling-update
  bounds, apiserver fan-out tail, async convergence lag, node-failure grace window.
- **`[UNVERIFIED]` carry-forward (not load-bearing):** kubernetes.io docs / k8s+etcd source / Borg
  paper / CRI spec (hosts 000); k8s object semantics (Deployment/StatefulSet/DaemonSet), scheduler
  plugin set, APF config; version/config-dependent constants (300 s toleration, 25% surge/unavail,
  scoring weights); CNI/kube-proxy modes, CSI, admission webhooks, operators/CRDs, HPA/VPA/autoscaler;
  etcd MVCC/watch internals. All blocked behind unreachable hosts; logged, none hardened.

---
**Appendix J reconciled.** Reference-grade, exercise-free, 13/13 recomputed, the orchestrator explained
as spine 11/15/20 + L laws applied to appendix I's container unit. **Closes the B → I → J arc.** No
chapters yet.
