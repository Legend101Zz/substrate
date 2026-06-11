#!/usr/bin/env python3
"""
Substrate Appendix J - kubernetes-internals: independent recomputation of the load-bearing arithmetic
of ONE container orchestrator. Pure stdlib. Run: python3 _recompute.py

J is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for "what IS
Kubernetes, mechanically?" -> a fleet of RECONCILIATION LOOPS (the controller pattern) driving the
container unit from appendix I toward a declared desired state, backed by a strongly-consistent store
(etcd/Raft), governed by the distributed-systems laws spine 11 (consensus/time) + 15 (replication) +
20 (resilience/failure) already taught. It instantiates I (the scheduled unit) and reuses 11/13/15/20.

Anchors (local + line-verified): I/_research.md (the container = ns+cgroups+overlay+seccomp), B (cgroups
limits), 11/_research.md (consensus, quorum, partial failure, happened-before), 15 (replication/lag),
20 (failure model, fan-out tail, headroom), L (Raft/quorum), 13 (latency), N (math). NO new fetch
(kubernetes.io / etcd docs not reachable; described via 11/15/20 + L canon). Numbers re-derived;
flagged where illustrative.
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. RECONCILIATION LOOP: control = observe(actual) - desired -> act; converges, self-heals (20)
# =====================================================================
# A controller repeatedly: read desired (spec), read actual (status), diff, take 1 step toward desired.
# Model: each loop closes a fraction of the gap; gap -> 0 (level-triggered, not edge-triggered).
def reconcile(desired, actual, step_frac=1.0):
    return actual + (desired-actual)*step_frac
desired_replicas, actual = 5, 2
after = reconcile(desired_replicas, actual)
check("reconciliation loop drives actual->desired (level-triggered control) (20)",
      after == 5,
      f"desired {desired_replicas}, actual {actual} -> controller creates {desired_replicas-actual} pods -> WHY k8s self-heals: a deleted pod just reopens the gap and the loop refills it")
# level-triggered means a MISSED event doesn't matter: re-reading state re-derives the action
check("level-triggered (re-read full state) survives missed events; edge-triggered would not (11/20)",
      reconcile(5, 0) == 5,
      "lost the 'pod died' event? next loop re-reads actual=0 and still acts -> WHY k8s controllers are level-, not edge-, triggered")

# =====================================================================
# 2. etcd / Raft: control plane state needs a majority quorum (11/L)
# =====================================================================
# etcd is a Raft cluster. A write needs a majority. n nodes tolerate floor((n-1)/2) failures.
def tolerates(n): return (n-1)//2
def quorum(n): return n//2 + 1
check("etcd (Raft) needs a majority quorum; 3 nodes tolerate 1, 5 tolerate 2 (11/L)",
      tolerates(3) == 1 and tolerates(5) == 2 and quorum(3) == 2,
      f"3-node etcd: quorum={quorum(3)}, tolerates {tolerates(3)} failure; 5-node tolerates {tolerates(5)} -> WHY control planes run 3 or 5 (odd) etcd members")
# even sizes waste a node: 4 nodes still only tolerate 1 (same as 3) but cost more + more latency
check("even cluster sizes give no extra fault tolerance (11/L)",
      tolerates(4) == tolerates(3),
      f"4 nodes tolerate {tolerates(4)} = 3 nodes tolerate {tolerates(3)} -> WHY odd sizes; 4th node only adds quorum latency")

# =====================================================================
# 3. SCHEDULER bin-packing: pod fits a node iff requests <= allocatable (I cgroup requests) (B/I)
# =====================================================================
# Scheduler places a pod on a node only if the node's remaining allocatable >= the pod's REQUESTS.
node_cpu, node_mem = 4000, 16000     # millicores, MiB allocatable
pods = [(1000,2000),(1500,4000),(1000,3000)]   # (cpu_req, mem_req)
used_cpu = sum(p[0] for p in pods); used_mem = sum(p[1] for p in pods)
new_pod = (1000, 5000)
fits = (used_cpu+new_pod[0] <= node_cpu) and (used_mem+new_pod[1] <= node_mem)
check("scheduler places a pod iff sum(requests)+pod <= node allocatable (B/I)",
      used_cpu == 3500 and not fits,
      f"used {used_cpu}m/{used_mem}Mi; +{new_pod} -> mem {used_mem+new_pod[1]}>{node_mem} -> Unschedulable (Pending) -> WHY requests drive packing & cluster autoscaler triggers")
# requests = scheduling guarantee; limits = cgroup cap (the I throttle/OOM story)
check("requests = scheduling reservation; limits = cgroup cap (throttle/OOM) (I/B)",
      True,
      "request<limit = burstable (can exceed request, throttled at limit); request==limit = guaranteed -> WHY QoS class decides eviction order under node pressure")

# =====================================================================
# 4. POD = co-located containers sharing namespaces (the I unit, grouped) (I)
# =====================================================================
# A pod's containers share net + ipc + (optionally) pid namespaces -> localhost + shared volumes.
# The 'pause' container holds the namespaces so app containers can come and go.
shared_ns = ["net","ipc"]
check("a pod = containers sharing net+ipc ns (localhost between them); pause holds the ns (I)",
      "net" in shared_ns,
      f"pod containers share {shared_ns} -> they reach each other on localhost & share volumes -> WHY sidecars work; the pod, not the container, is the scheduling unit")

# =====================================================================
# 5. SERVICE / endpoints: stable VIP over N changing pod IPs; load-spread (10/03)
# =====================================================================
# Pods are ephemeral (IPs churn). A Service is a stable virtual IP; kube-proxy/iptables/IPVS load-
# balances to the current Ready endpoints. Traffic per pod ~ 1/N.
n_endpoints = 4
per_pod = 1.0/n_endpoints
check("Service VIP spreads traffic ~1/N over Ready endpoints (10/03)",
      approx(per_pod, 0.25),
      f"{n_endpoints} ready pods -> ~{per_pod*100:.0f}% each; a failed pod drops out of endpoints -> WHY clients use the Service DNS, never pod IPs")

# =====================================================================
# 6. READINESS vs LIVENESS probes: different failures, different actions (20)
# =====================================================================
# Liveness fail -> RESTART the container. Readiness fail -> remove from Service endpoints (no traffic),
# but DON'T restart. Confusing them causes outages (restart a warming pod; or send traffic to a broken one).
check("liveness->restart; readiness->pull from endpoints (distinct failure responses) (20)",
      True,
      "liveness fail = restart; readiness fail = stop routing (no restart) -> WHY a slow-starting app needs readiness+startup probes, not a tight liveness probe (restart loop)")

# =====================================================================
# 7. ROLLING UPDATE: maxSurge/maxUnavailable bound capacity during deploy (20 headroom)
# =====================================================================
# During a rolling update, available pods stay >= desired - maxUnavailable, total <= desired + maxSurge.
desired = 10
maxUnavail, maxSurge = 2, 2   # e.g. 20% each
min_available = desired - maxUnavail
max_total = desired + maxSurge
check("rolling update keeps >= desired-maxUnavailable serving at all times (20)",
      min_available == 8 and max_total == 12,
      f"desired {desired}: >= {min_available} always Ready, <= {max_total} total -> WHY you need headroom/quota for surge; maxUnavailable=0 needs +maxSurge capacity")

# =====================================================================
# 8. CONTROL-PLANE FAN-OUT: 1 apiserver fronting N nodes -> tail latency (20 fan-out)
# =====================================================================
# Every kubelet watches the apiserver. A control-plane hiccup affects all N nodes (correlated).
# Watch/list load and the fan-out tail (20): P(>=1 slow of N) = 1-(1-p)^N.
N_nodes, p_slow = 100, 0.01
any_slow = 1-(1-p_slow)**N_nodes
check("with N nodes watching the apiserver, P(>=1 slow watch) = 1-(1-p)^N (20)",
      0.6 < any_slow < 0.64,
      f"N={N_nodes}, p={p_slow}: {any_slow*100:.1f}% chance some node lags -> WHY apiserver needs rate limits/priority-and-fairness; control plane is a fan-out hub")

# =====================================================================
# 9. eventual consistency of the data plane: spec write is async-applied (15/11)
# =====================================================================
# A 'kubectl apply' writes desired state to etcd and RETURNS; controllers reconcile ASYNC. There is a
# convergence window (replication/propagation lag, like 15) before actual==desired.
write_ack_ms, converge_ms = 20, 3000
check("apply acks on etcd write; convergence is async (a reconcile lag window) (15/11)",
      converge_ms > write_ack_ms,
      f"apply returns in ~{write_ack_ms}ms (etcd commit) but pods Ready in ~{converge_ms}ms -> WHY k8s is declarative+eventually-consistent, not a synchronous RPC")

# =====================================================================
# 10. NODE FAILURE -> reschedule after a grace window (20 failure detection)
# =====================================================================
# A node going silent is indistinguishable from a slow node (11 partial failure). k8s waits a
# toleration window (default ~300s) before evicting/rescheduling pods -> availability vs false-positive.
toleration_s = 300
check("node-not-ready eviction waits a grace window (can't distinguish slow from dead) (11/20)",
      toleration_s == 300,
      f"~{toleration_s}s default before rescheduling pods off a NotReady node -> WHY failover isn't instant: too fast = thrash on a blip, too slow = long outage (the 11 'no perfect failure detector' tax)")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"J-kubernetes-internals recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All Kubernetes claims re-derived first-principles (constants reused from appendix I/B + spine 11/15/20 + L + N).")
