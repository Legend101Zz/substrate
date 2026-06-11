# Appendix O · cloud-infra-basics — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). O is a **reference appendix**: deep info
> ONLY, **NO exercises** (CONSTITUTION #5). It is the single deep home for **the cloud's primitives —
> what a public cloud actually rents you and why each primitive exists** — the managed/rented
> instantiation of concepts the spine already teaches from first principles (compute = appendices
> A/B/I/J; storage = 06/07/08/F/G; network = 03/10; consistency/replication = 11/14/15/L; resilience &
> capacity = 13/20; latency hierarchy = 13). Spine 13/14/15/20 + appendices I/J cross-link DOWN into O
> for "how this looks as a cloud service." **Bespoke structure: the cloud as five planes you rent** —
> *compute*, *storage*, *network*, *identity*, and the *control plane* that ties them together — each
> plane a managed version of a primitive the reader already built. This is a **cloud-primitives
> reference map**, NOT a vendor tutorial, NOT a four-cluster shape, NOT a build progression. It is
> vendor-neutral: name the primitive, then note the AWS/GCP/Azure instances as `[UNVERIFIED]`
> illustrations (vendor docs all unreachable). Math: `_recompute.py` (14/14). Factcheck:
> `_factcheck_phase1.md` (0 blockers). Network: aws.amazon.com / cloud.google.com / azure docs HTTP
> **000** this wave → every load-bearing claim reused from line-verified spine math + appendices,
> never from vendor marketing. Nothing new hardened.

## 1. Thesis
The cloud sells nothing new — it sells the **primitives this course builds, as rented, metered,
API-driven services with someone else's operations team.** "Serverless," "managed," "elastic" are not
new mechanisms; they are the spine's mechanisms (a Linux process in a container = appendix I; a
replicated log = appendix H; a B-tree on a disk = appendix F; consensus = appendix L) with the
*operational burden and the failure domains* moved across an API boundary. The one genuinely new
forcing function is the **economic + control-plane** one: because you pay per-unit-time and call an
API to provision, the cloud makes **elasticity** (scale with load) and **failure-domain isolation**
(regions / availability zones) first-class — which is exactly the resilience & capacity math of spine
13 & 20, now expressed as buttons. One sentence: *the cloud is a credit card wrapped around the
primitives you already understand; the only truly new things are the meter and the blast-radius map.*

## 2. The cloud as five planes you rent (the bespoke spine)

### Plane 1 — Compute: rented execution, sliced finer and finer (appendices A/B/I/J; 20)
- **The ladder of abstraction (each a thinner slice of the same CPU+OS):**
  - **VM / IaaS** — a whole virtualized machine (hypervisor over appendix A's hardware; guest is
    appendix B's Linux). You rent a kernel + cores + RAM.
  - **Container / CaaS** — appendix I's "process + namespaces + cgroups + overlayfs," scheduled by
    appendix J's reconciliation loops. You rent a process slot; the kernel is shared.
  - **Function / FaaS ("serverless")** — a single handler invoked per-event; the platform manages the
    container lifecycle. You rent a *function call*. RECOMPUTED: cold start = container spin-up latency
    (ms–s, appendix I's VM-vs-container ~100× start-time gap) amortized only when invocations are
    frequent → WHY FaaS suits spiky/low-QPS work and warm pools exist.
- **Elasticity = autoscaling = spine 13/20 made automatic:** add instances when a signal (CPU, queue
  depth, RPS) crosses a threshold. RECOMPUTED (reuse 13 Little's Law): to serve offered load L at
  per-instance capacity μ you need ⌈L/μ⌉ instances, +1 for f=1 redundancy → the autoscaler is just
  this formula on a timer. Plan to target utilization ρ≈0.5–0.7, not saturation (13: latency =
  1/(1−ρ) blows up at the knee).

### Plane 2 — Storage: durability you rent, in three shapes (06/07/08; F/G; 11/15)
- **Object storage (S3-class)** — a flat key→blob store: cheap, massively durable, **eventually/strong
  read-after-write** per object, NOT a filesystem (no cheap rename/append). It is the cloud's
  durability primitive; everything else (backups, data lakes, static sites) layers on it. The "11
  nines durability" marketing = parallel-redundancy math from spine 20 (`A = 1−(1−a)^n` across
  replicas/AZs) → RECOMPUTED below.
- **Block storage (EBS-class)** — a virtual disk attached to one VM: this is appendix F/B's block
  device, replicated under the hood. Single-attach by default (a disk has one writer) → the cloud
  version of "one writer per page."
- **Managed databases / caches (RDS, managed Postgres/Redis, DynamoDB-class)** — appendices F & G run
  by the vendor: you rent the storage engine + replication + backups + failover, and inherit its
  CAP/PACELC posture (spine 11/15/L). RECOMPUTED (reuse 15): a read replica is asynchronous → bounded
  staleness; a multi-region strongly-consistent store pays the consensus/commit-wait latency of
  appendix L. The cloud cannot repeal CAP — it only hides the operators.
- **The storage hierarchy is the latency hierarchy (13):** local NVMe < attached block < object store
  < cross-region — each tier ~order(s) of magnitude slower, mirroring 13's memory/disk/network ladder.

### Plane 3 — Network: a software-defined version of appendix 03/10 (03; 10; 16)
- **VPC / software-defined network** — your own private IP space (03's IP/subnets), with route tables,
  security groups (stateful firewall = packet filter from appendix B), and NAT. The cloud gives you
  appendix 03's network as an API.
- **Load balancers (managed)** — appendix 10's reverse proxy / LB algorithms, run as a service (L4
  network LB ≈ connection-level; L7 application LB ≈ HTTP-aware, the nginx of appendix 10). Health
  checks + draining = spine 20's failure detection.
- **CDN / edge (16)** — geographically distributed caches in front of object/origin storage; this is
  spine 16's caching-and-CDN chapter as a rented global cache. RECOMPUTED (reuse 13 latency
  hierarchy): an edge hit avoids the cross-region RTT → the entire economic case for a CDN is the
  speed-of-light bound from 13.
- **Egress economics:** data *into* the cloud is usually free; data *out* (egress) is metered — the
  network meter that shapes architecture (keep traffic in-region/in-VPC).

### Plane 4 — Identity & isolation: who can call what, and blast-radius (11/20; B; J)
- **IAM (identity & access management)** — principals, roles, policies; the cloud's authorization
  substrate. Least privilege = the capability/permission model of appendix B and appendix J's RBAC,
  scaled to an org.
- **Failure-domain hierarchy (the genuinely cloud-native idea):** **Region** (independent geography) ⊃
  **Availability Zone** (independent power/network/cooling within a region) ⊃ instance. This is spine
  20's *correlated-failure* math made physical: spread replicas across **independent** AZs/regions so
  failures are uncorrelated. RECOMPUTED (reuse 20): single-AZ redundancy with correlation c collapses
  6-nines toward ~3-nines (`A ≈ 1−c(1−a)` dominates) → WHY "multi-AZ" exists; cross-region is for
  region-level disasters. The cloud's whole reliability story is spine 20's `A = 1−(1−a)^n` *plus the
  warning that correlation is the enemy*.

### Plane 5 — The control plane: the API that provisions it all (J; 11; 19)
- **Control plane vs data plane** — the API/orchestrator that *creates and reconciles* resources
  (control plane; appendix J's reconciliation loops generalized to the whole cloud) vs the path that
  serves user traffic (data plane). RECOMPUTED (reuse J): provisioning is **declarative +
  level-triggered** — you declare desired state (IaC: Terraform/CloudFormation), the control plane
  drives actual→desired, like a Kubernetes controller. WHY infra-as-code is idempotent.
- **Metering & quotas** — every primitive is counted (the meter) and capped (quotas / service limits);
  this is the economic forcing function that makes elasticity and FaaS exist at all.
- **Observability (19)** — managed metrics/traces/logs (spine 19's Dapper-style tracing + SLOs) as a
  service; the control plane is also where you watch the data plane.

## 3. The "rented primitives + a meter + a blast-radius map" reconciliation (appendix payload)
| plane | rented primitive | spine/appendix it instantiates | the only new forcing function |
|---|---|---|---|
| compute | VM / container / function | A,B / I / J; 13,20 | pay-per-time → elasticity (autoscale) |
| storage | object / block / managed DB | 06,07,08 / F,G; 11,15,L | durability SLA = 20's parallel-redundancy math |
| network | VPC / LB / CDN | 03 / 10 / 16; 13 | egress meter; edge = 13 latency bound |
| identity | IAM / region+AZ | B,J / 20 | failure-domain isolation (correlation is the enemy) |
| control | API / IaC / quotas / obs | J / 11 / 19 | declarative reconciliation + metering |

## 4. Common misconceptions to preempt
- "Serverless means no servers." It means *you* don't manage them; it's appendix I's container with a
  per-invocation lifecycle and a cold-start cost.
- "The cloud repeals CAP." It hides the operators, not the theorem — a multi-region strong store still
  pays consensus/commit-wait latency (appendix L); read replicas are still stale (spine 15).
- "Object storage is a filesystem." It's a flat key→blob store — no cheap rename/append, different
  consistency than POSIX.
- "Multi-AZ guarantees availability." Only if failures are *uncorrelated*; correlated failure collapses
  the nines (spine 20). Independence is the whole point of AZs/regions.
- "Autoscaling is magic." It's ⌈L/μ⌉+redundancy on a timer (spine 13 Little's Law); it can't beat the
  utilization-vs-latency knee (1/(1−ρ)).
- "A CDN makes things fast for free." Its value is bounded by the speed-of-light RTT it saves (spine
  13); a low cache-hit ratio erases the win.
- "Cloud = unlimited." Every primitive is metered and quota-capped; egress is billed; that meter is
  the reason elasticity/FaaS exist.
- "IaC is a script." It's *declarative, level-triggered reconciliation* (appendix J), which is why it's
  idempotent — not an imperative provisioning script.

## 5. Provenance summary
- **REUSED (line-verified spine + appendices):** compute ladder — appendix I (container = process+ns+
  cgroups+overlayfs; VM-vs-container ~100× start gap), appendix J (reconciliation/scheduling), A/B
  (hardware/kernel); storage — 06/07/08 + F (B-tree/WAL/page) + G (in-memory) + 11/15/L (replication,
  CAP/PACELC, consensus latency); network — 03 (IP/subnets/firewall) + 10 (reverse proxy/LB) + 16
  (CDN/caching); resilience/availability — 20 (`A=1−(1−a)^n`, serial `∏a_i`, correlated-failure
  collapse) + 13 (Little's Law capacity, 1/(1−ρ) utilization knee, latency hierarchy); control plane —
  J (declarative level-triggered reconciliation) + 19 (tracing/SLOs).
- **RECOMPUTED:** `_recompute.py` (14/14) — FaaS cold-start amortization; autoscale ⌈L/μ⌉+1; object
  durability via parallel redundancy; read-replica staleness vs strong-consistency commit-wait; CDN
  edge-vs-cross-region latency saving; multi-AZ correlated-failure nines collapse; serial dependency
  availability; utilization knee for autoscale target; egress-asymmetry direction; declarative
  reconciliation idempotence; storage latency hierarchy ordering; region⊃AZ⊃instance domain nesting.
- **`[UNVERIFIED]` carry-forward (none load-bearing — all reused from spine math, not vendor docs):**
  ALL vendor-specific names/numbers (S3 "11 nines," EBS IOPS tiers, Lambda limits, specific instance
  types, exact AZ counts per region, pricing) — aws.amazon.com / cloud.google.com / Azure docs HTTP
  **000** this wave; cited as *illustrations* of the vendor-neutral primitive, never as load-bearing
  facts. The *mechanisms and math* are all spine-derived and recomputed.

---
**Appendix O reconciled.** Reference-grade, exercise-free, 14/14 recomputed, all load-bearing claims
reused from line-verified spine math + appendices (vendor specifics flagged `[UNVERIFIED]`). No
chapters yet.