# 13 scaling-fundamentals — Cluster C: horizontal vs. vertical scaling, statelessness, the AKF cube

> Phase 1 research brief (NO course prose). Standard six sections. Primary sources first;
> anything not fetched-and-verified this session is flagged `[UNVERIFIED from fetched source]`.
>
> **Network reality this session (5th consecutive):** only `lamport.azurewebsites.net` and
> Walmart artifactory resolve. `akfpartners.com` (the AKF Scale Cube articles) and *The Art
> of Scalability* errata returned **HTTP 000** (verified by direct `curl`). Consequence: the
> **cube's geometry and the scaling logic** are presented from first principles and tied to
> math/canon already verified (Cluster A + sub-courses 06/11); the **exact AKF wording,
> diagrams, and book attributions are flagged** and carried forward.
>
> **Scope of this cluster:** the *strategy layer* of scaling — scale up vs. scale out,
> why statelessness is the precondition for cheap horizontal scaling, and the AKF Scale Cube
> (X/Y/Z axes) as the taxonomy of "how to split." This cluster answers "*given* a bottleneck
> (Cluster B) and the wall (Cluster A), what are my structural moves, and which downstream
> sub-course (14/15/16) does each move hand off to?"

---

## 1. Key mechanisms (how the thing actually works, deeply)

### 1.1 Vertical scaling (scale up) — bigger box

Add resources to a single node: more cores, more RAM, faster disk, bigger NIC.

- **Pros:** no application change, no distribution, no consistency problem — you keep a single
  address space and a single source of truth. Best first move; often the cheapest *until the
  knee*.
- **Limits (forced by Cluster A):** Amdahl's ceiling `1/(1−p)` and the USL retrograde knee
  `N*=√((1−α)/β)` both bound the payoff of adding cores to *one* machine — coherency traffic
  (`β·N²`) eventually makes more cores *slower*. And there is a hard physical/$$ ceiling: the
  biggest box that exists, at superlinear price. Vertical scaling buys time, not infinity.

### 1.2 Horizontal scaling (scale out) — more boxes

Add more nodes and spread load across them (behind a load balancer / partitioner).

- **Pros:** capacity grows ~linearly with node count (in the ideal, contention-free case),
  past any single machine's ceiling; also the substrate for *fault tolerance* (lose a node,
  keep serving).
- **The cost it introduces:** **coordination.** The instant state lives on more than one node
  you inherit replication, partitioning, and consistency problems — exactly sub-course 11's
  material. Horizontal scaling trades a hardware ceiling for a *distributed-systems* problem.
  The USL `β` term is the mathematical warning that this trade is not free: cross-node
  coordination is the `N²` coherency cost.

### 1.3 Statelessness — the precondition that makes scale-out cheap

A service instance is **stateless** when any request can be handled by *any* instance because
the instance holds no client-specific data between requests — all durable/session state lives
*outside* the instance (a database, a cache, a token, the client).

- **Why it matters:** if instances are stateless, horizontal scaling is *embarrassingly
  parallel* — the load balancer can spray requests round-robin, add/remove nodes freely, and
  recover from a node loss with zero session loss. The hard part (state) is concentrated in a
  *few* stateful systems you scale deliberately (DB, cache, log).
- **Where the state goes (the displacement, not deletion, of state):**
  - **Session state → token (client-held) or shared store.** JWT/cookies push session to the
    client; or a shared session cache (Redis) holds it. Either way the *app tier* is stateless.
  - **Durable state → database/partitioned store** (hands off to 14: partitioning/sharding).
  - **Hot read state → cache/CDN** (hands off to 16: caching/CDN).
- **The deep point:** "stateless services" is a slight lie — state is never deleted, it is
  *relocated* to systems designed to be authoritative and scaled on their own terms. Making
  the *compute tier* stateless is what lets you scale it the easy way (X-axis below) so you
  can spend your hard scaling budget on the *data tier*.

### 1.4 The AKF Scale Cube — three orthogonal axes of splitting

The AKF Scale Cube (Abbott & Fisher, AKF Partners / *The Art of Scalability*) frames all
scaling as movement along three **orthogonal** axes. The corner `(0,0,0)` is a single
monolithic, unsplit instance; the far corner is split on all three axes at once.

- **X-axis — horizontal duplication / cloning.** Run *N identical copies* behind a load
  balancer; each copy can serve *any* request and holds the *whole* dataset (or reads a
  shared one). This is "add more clones." Scales **transactions/throughput**, gives
  redundancy, requires **statelessness** (or replicated state) to be cheap. *Does not* reduce
  per-node data size or code complexity. **Hands off to:** load balancing (sub-course 10),
  and read replicas (sub-course 15).
- **Y-axis — functional / service decomposition (split by *what*).** Split the system by
  *verb/noun* — distinct services for distinct responsibilities (auth, search, checkout,
  feed). Each service is independently deployable and scalable; this is the
  microservices/SOA direction. Scales by letting each function get its own resources and
  team, and shrinks each codebase. **Hands off to:** async/event-driven decoupling
  (sub-course 17) and observability across services (19).
- **Z-axis — data partitioning / sharding (split by *who/which*).** Split by a *lookup on the
  data itself* — shard by customer ID, geography, tenant, hash of key. Each shard handles a
  *subset of the data/requests*, ideally with near-identical code to the others. Scales the
  **data size** and isolates load/blast-radius per shard. **Hands off to:** data
  modeling/partitioning/sharding (sub-course 14) and replication/consistency (15).

**Orthogonality is the key insight:** the axes compose. A large system is typically X *and*
Y *and* Z: functionally decomposed services (Y), each sharded by customer (Z), each shard
cloned for throughput/HA (X). Choosing an axis is choosing *which* scaling problem you take
on:

| axis | splits by | scales | shrinks | primary new cost | hands off to |
|------|-----------|--------|---------|------------------|--------------|
| **X** | clone (identical copies) | throughput / availability | nothing (data) | needs statelessness/replication | 10 (LB), 15 (read replicas) |
| **Y** | function (verb/noun) | per-function capacity + team autonomy | each codebase | inter-service calls, distributed txns | 17 (async), 19 (observability) |
| **Z** | data lookup (shard key) | data size + isolates load | per-shard dataset | rebalancing, cross-shard queries, hot shards | 14 (sharding), 15 (consistency) |

### 1.5 Choosing an axis — the decision logic

- **Throughput-bound, data fits, code fine?** → **X** first (cheapest; just clone, behind a
  load balancer, once you're stateless). This is why "make it stateless then autoscale" is
  the default cloud playbook.
- **One team/codebase is the bottleneck; different parts have different scaling profiles?** →
  **Y** (decompose so the hot function scales independently). Beware: Y adds network calls and
  the USL `β` coordination cost between services.
- **Dataset too big for one node, or per-customer isolation needed?** → **Z** (shard). This is
  the hardest axis (rebalancing, cross-shard joins, hot keys) and is exactly sub-course 14.
- **Cluster A connection:** every axis is ultimately an attempt to keep *each* resource below
  its `1/(1−ρ)` knee — X by spreading arrivals, Z by spreading the dataset/arrivals by key,
  Y by giving the hot function its own resource pool. The USL warns that Y and Z add
  coordination (`β`), so you don't split for its own sake.

### 1.6 Linearity is the ideal, not the guarantee

"Horizontal scaling is linear" is the *aspiration*; the USL is the *reality check*. Adding
nodes adds throughput only to the extent that contention (`α`) and coherency (`β`) stay low.
Shared bottlenecks (a single database behind "stateless" app servers, a global lock, a chatty
service mesh) re-introduce the serial fraction and cap scale-out exactly as Amdahl/USL
predict. **Stateless app tier + an unscaled shared DB just relocates the wall to the DB** —
which is precisely why Z-axis sharding (14) and replication (15) exist.

---

## 2. Foundational sources

### Verified this session (by reasoning / reuse — no fetch required)
- **Why X-axis needs statelessness; why Y/Z add coordination cost** — these are direct
  applications of Cluster A's Amdahl/USL math (`_factcheck_clusterA.md` claims #5–#6): the
  `β·N²` coherency term *is* cross-node/cross-service coordination. Not a new external claim.
- **Sharding/partitioning + replication/quorum mechanics that Z and X bottom out in** — already
  line-verified in sub-course 11 (`11-distributed-systems-foundations/_research.md`:
  quorum = majority intersection, leader/follower replication, consistency models) and the
  consistent-hashing/partitioning structures in 06.

### Reused verified canon (already line-checked in earlier sub-courses — do NOT re-fetch)
- **Consistent hashing / partitioning data structures** (the Z-axis substrate) —
  `06-data-structures-for-systems` (consistent hashing) — verified there.
- **Replication, quorums, consistency models** (the X read-replica + Z cross-shard cost) —
  `11-distributed-systems-foundations/_research.md` + its four factcheck files.
- **Load-balancer peer selection / smooth weighted round-robin / `ip_hash`** (the X-axis
  fan-out mechanism) — `10-nginx-proxies-and-load-balancing/_research_load-balancing-peer-selection.md`,
  verified against NGINX `release-1.31.1`.

### Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals)
- **AKF Partners, "The AKF Scale Cube" / "Scalability Cube"** articles (`akfpartners.com`) —
  the canonical X/Y/Z definitions and diagram.
- **Abbott & Fisher, _The Art of Scalability_ (2nd ed.)** — the cube's book-length treatment
  and the "AKF" attribution.
- **Martin Fowler / microservices canon** (`martinfowler.com`) for the Y-axis decomposition
  tradeoffs (independent deployability, the distributed-monolith antipattern). `[UNVERIFIED]`.
- **Twelve-Factor App** (`12factor.net`), factors VI ("processes are stateless") and others —
  the canonical statement of statelessness for the compute tier. `[UNVERIFIED]`.

---

## 3. "Why it's this way" — the forcing functions

- **Vertical scaling ends because of physics + Amdahl/USL.** One box has a largest size, at
  superlinear cost, and even within it the serial fraction and coherency traffic cap the
  payoff of more cores. The ceiling is mathematical, not just budgetary.
- **Horizontal scaling exists to pass that ceiling — and *creates* the distributed-systems
  problem.** The moment state spans nodes you owe replication + consistency (11). There is no
  scale-out without coordination; the only question is how much (`β`) you can keep down.
- **Statelessness is the lever that makes X-axis cheap.** If any instance can serve any
  request, scaling the compute tier is trivial and node loss is survivable. State doesn't
  vanish — it's *relocated* to systems (DB/cache/log) you scale on purpose. That relocation is
  the whole reason 14/15/16 exist as separate sub-courses.
- **The cube has exactly three axes because there are exactly three independent things you
  can split:** the *copies* (X), the *functions* (Y), and the *data/requests by key* (Z).
  They're orthogonal because you can do any combination; real systems do all three.
- **Linearity is conditional.** The USL says scale-out returns are bounded by `α`+`β`; a
  shared, unscaled dependency behind "stateless" servers silently re-imposes the serial
  fraction. You must scale the *bottleneck* (Cluster B), not just clone the easy tier.

---

## 4. Common misconceptions to preempt

- **"Scale up vs. scale out is either/or."** False — you scale up first (cheap, no
  distribution), then out when you hit the box/Amdahl ceiling; real systems do both.
- **"Horizontal scaling is automatically linear."** False — §1.6 + Cluster A: the USL bounds
  it; a shared DB/lock re-imposes Amdahl. Cloning the app tier without scaling the data tier
  just moves the wall.
- **"Stateless means we deleted the state."** False — §1.3: state is *relocated* to DB/cache/
  client, not removed. The point is concentrating it where it can be scaled deliberately.
- **"The AKF axes are alternatives; pick one."** False — they're orthogonal and *compose*;
  big systems are X∧Y∧Z. Picking an axis = picking which scaling problem you take on now.
- **"Y-axis (microservices) is always more scalable."** False — Y adds network calls and
  distributed-transaction/coordination cost (USL `β`); a poorly cut decomposition is a
  *distributed monolith* that scales worse. Decompose along real load/ownership seams.
- **"Z-axis sharding is just X with more machines."** False — X clones the *whole* dataset; Z
  splits the dataset by key, which adds rebalancing, hot-shard, and cross-shard-query problems
  (the hard part — sub-course 14).

## 5. Best build-your-own target(s)

- **A stateless-ify refactor lab.** Take a toy app that keeps session in-process; move session
  to a token + shared cache; then run two instances behind the Cluster-B/own-LB and show that
  requests now survive instance loss and round-robin freely. Makes §1.3 visceral.
- **An AKF-cube decision worksheet → applied to a case study.** Given a workload (e.g. the
  feed/chat/URL-shortener targets from 21), decide X/Y/Z moves with explicit justification and
  the downstream sub-course each move invokes. Direct feeder into 21-design-case-studies.
- **A "shared bottleneck defeats scale-out" demo.** Extend the Cluster-A/B M/M/1 sim: clone
  the app tier (X) but keep one shared DB resource; plot throughput vs. app-node count and
  watch it plateau at the DB's `1/(1−ρ)` — proving §1.6 and motivating 14/15.

## 6. Open questions / where sources disagree / gaps to close

- **AKF cube exact wording + diagram are blocked.** Until `akfpartners.com` / *The Art of
  Scalability* are fetchable, the X/Y/Z definitions and the "AKF" attribution stay
  `[UNVERIFIED from fetched source]`. The *geometry and logic* are first-principles and safe;
  pin the canonical phrasing before Phase-2 prose.
- **Twelve-Factor statelessness statement** needs `12factor.net` to pin exact factor wording.
- **Microservices Y-axis tradeoffs** (Fowler; distributed-monolith antipattern; saga/2PC for
  cross-service transactions) need primaries; cross-link to 11 (atomic commit) and 17 (async).
- **Boundary discipline:** Cluster C is the *strategy/taxonomy* layer only. The *mechanics* of
  each axis live downstream — X→10/15, Y→17/19, Z→14/15. Keep handoffs as cross-links; do NOT
  duplicate sharding/replication mechanics here.
- **Disagreement to resolve with sources:** whether "scale cube" is best attributed to AKF
  (Abbott/Fisher) alone or has antecedents; confirm against the primary before asserting
  attribution in prose.
