# 13 scaling-fundamentals — Cluster A: back-of-envelope, latency, and the queueing math

> Phase 1 research brief (NO course prose). Standard six sections. Primary sources first;
> anything not fetched-and-verified this session is flagged `[UNVERIFIED from fetched source]`.
>
> **Network reality this session (4th consecutive):** only `lamport.azurewebsites.net` and
> Walmart artifactory (PyPI / github-*releases*) resolve. Dean "Latency Numbers", Drepper
> "What Every Programmer Should Know About Memory", the jboner latency gist, Little (1961),
> Kleinrock, Amdahl (1967), and Gunther's USL primaries all returned **HTTP 000**. The
> github-releases artifactory remote 404s for gists. Consequence: this cluster's **math is
> verified by derivation** (theorem-grade, needs no fetch); its **empirical numbers and
> historical attributions are flagged** and carried forward.
>
> **Scope of this cluster:** the *method and mathematics* of capacity reasoning —
> Little's Law, the utilization wall (queueing), Amdahl's Law, the Universal Scalability
> Law (USL), tail-latency arithmetic, and the back-of-envelope discipline. The concrete
> latency *table* (Pillar 2) is deliberately treated as a separate, flagged input, not the
> load-bearing content.

---

## 1. Key mechanisms (how the thing actually works, deeply)

### 1.1 Little's Law — the master identity of capacity reasoning

**Statement.** For any stable system observed over a long interval,

```
L = λ · W
```

where `L` = long-run average number of items *in the system*, `λ` = long-run average
*arrival rate* (= throughput, since stable ⇒ arrivals = departures), and `W` = long-run
average *time an item spends in the system*.

**Why it is astonishingly general.** Little's Law makes **no assumption** about the arrival
process, the service-time distribution, the number of servers, or the queueing discipline.
It is a conservation identity, not a model. The standard area/accounting argument:

- Let `A(t)` = cumulative arrivals, `D(t)` = cumulative departures by time `t`.
- `N(t) = A(t) − D(t)` = number in system. The integral `∫₀ᵀ N(t) dt` equals the total
  "item-seconds" accumulated, which also equals `Σ (time each item spent in system)`.
- Divide by `T`: time-average of `N` = (number of arrivals/`T`) × (average time-in-system).
  As `T→∞` with stability, that is exactly `L = λ·W`. ∎ (derivation verified this session)

**Three forms you actually use:**

1. **Concurrency form** (the back-of-envelope workhorse):
   `concurrency = throughput × latency`. A service doing `X` req/s where each request is
   in-flight for `W` seconds has, on average, `X·W` requests in flight *simultaneously*.
   Example (dimensional check only, not a benchmarked claim): 10,000 req/s × 0.020 s =
   200 concurrent requests in flight ⇒ you need ≥200 units of whatever resource a request
   holds (threads, connections, file descriptors) to not queue.

2. **Utilization (server) form:** `U = X · S`, utilization = throughput × *service time*.
   For a single server, `ρ = λ/μ = λ·S` where `S = 1/μ` is mean service time. `ρ` must be
   `< 1` for stability.

3. **Sub-system form:** applies independently to *any* boundary you draw (the thread pool,
   the connection pool, the DB, the disk queue). This is why Little's Law is the unifying
   lens: every bottleneck is "a box with arrivals and a residence time."

### 1.2 The utilization wall — why systems fall over *before* 100% busy

Little's Law tells you occupancy; it does **not** by itself tell you *latency under load*.
For that you need a queueing model. The canonical teaching model is **M/M/1** (Poisson
arrivals, exponential service, 1 server, FIFO, infinite buffer). Its standard results
(derivable from the birth–death balance equations `λ·pₙ = μ·pₙ₊₁ ⇒ pₙ = (1−ρ)ρⁿ`):

```
Number in system        L  = ρ / (1 − ρ)
Mean response time      W  = S / (1 − ρ)            (service + waiting)
Mean waiting time       Wq = ρ·S / (1 − ρ)
Latency amplification   W / S = 1 / (1 − ρ)
```

**The wall (verified arithmetic):** `W/S = 1/(1−ρ)`:

| utilization ρ | latency vs. unloaded (1/(1−ρ)) |
|---------------|--------------------------------|
| 0.50          | 2×                             |
| 0.80          | 5×                             |
| 0.90          | 10×                            |
| 0.95          | 20×                            |
| 0.99          | 100×                           |

This is the single most important shape in capacity planning: **response time is hyperbolic
in utilization and diverges as ρ→1.** You do not run hot servers at 95% "to be efficient";
you run them with headroom because the last few percent of utilization cost you
order-of-magnitude latency. (All values recomputed from `1/(1−ρ)` this session.)

**Caveats worth teaching (mechanism honesty):**
- M/M/1 is a *teaching* model. Real service times are rarely exponential; the
  Pollaczek–Khinchine (M/G/1) result shows waiting time scales with the *variance* of
  service time, not just the mean — `Wq = ρ·S·(1 + C²ₛ)/(2(1−ρ))` where `C²ₛ` is the squared
  coefficient of variation of service time. High variance (e.g. a few slow queries) inflates
  the queue even at modest ρ. [P-K formula stated from standard queueing theory;
  Pollaczek/Khinchine and Kleinrock primaries `[UNVERIFIED from fetched source]`.]
- Multiple servers (M/M/c) push the knee right but do not remove it; the shape persists.

### 1.3 Amdahl's Law — the ceiling on speedup from parallelism

If fraction `p` of work is parallelizable and `(1−p)` is inherently serial, then with `N`
workers:

```
Speedup(N) = 1 / ( (1 − p) + p/N )
Max speedup (N → ∞) = 1 / (1 − p)
```

**Consequence (verified):** even `p = 0.95` caps you at `1/0.05 = 20×` no matter how many
cores you throw at it. The serial fraction, not the core count, is the ceiling. This is the
"why throwing machines at it stops helping" law. [Formula derived/verified this session;
Amdahl 1967 AFIPS primary `[UNVERIFIED from fetched source]`.]

### 1.4 Universal Scalability Law (USL) — why throughput can go *backwards*

Amdahl explains diminishing returns but predicts throughput *plateaus*. Real systems often
get *slower* past a point (retrograde scaling) because of **coherency/crosstalk** (cache
coherence, lock handoff, gossip, coordination). Gunther's USL adds that second penalty:

```
C(N) = N / ( 1 + α(N − 1) + β·N(N − 1) )
```

- `α` = **contention** (serialization; the Amdahl-like term).
- `β` = **coherency** (pairwise crosstalk; grows as `N²`).
- With `β = 0`, USL reduces to an Amdahl-shaped curve.
- With `β > 0`, `C(N)` rises, peaks, then **declines** — the empirically observed retrograde
  region. The peak (optimal concurrency) is at:

```
N* = sqrt( (1 − α) / β )
```

**Teaching value:** USL is the bridge from "scaling math" to "real distributed systems":
the `β·N²` term *is* coordination cost, which is exactly what consensus/replication
(sub-course 11) tries to bound. [USL form and `N*` derived/verified this session; Gunther
"Guerrilla Capacity Planning" primary `[UNVERIFIED from fetched source]`.]

### 1.5 Tail latency arithmetic — why averages lie and fan-out hurts

- **Averages hide the tail.** Users experience p99/p99.9, not the mean. A bimodal mix (most
  fast, a few slow) can have a fine mean and a terrible p99.
- **Fan-out amplifies the tail (verified arithmetic).** If a single user request fans out to
  `N` independent backend calls and *waits for all of them*, and each backend exceeds its
  latency budget with probability `q`, then:
  `P(request is slow) = 1 − (1 − q)^N`.
  With `q = 0.01` (1% of calls slow) and `N = 100` fan-out:
  `1 − 0.99¹⁰⁰ ≈ 1 − 0.366 = 0.634` ⇒ **~63% of user requests hit at least one slow
  backend.** A 1-in-100 backend tail becomes a near-certainty at the user. (Recomputed this
  session: `0.99¹⁰⁰ ≈ 0.3660`.)
- This is the quantitative core of **"The Tail at Scale" (Dean & Barroso, CACM 2013)** and
  motivates hedged/tied requests, which is sub-course 20's territory. [The paper itself is in
  12's canon and remains `[UNVERIFIED from fetched source]` — network-blocked; the
  *arithmetic* above is self-contained.]

### 1.6 The latency hierarchy (Pillar 2 — the part that needs primaries)

The famous "Latency Numbers Every Programmer Should Know" (Jeff Dean; popularized via the
jboner gist and Colin Scott's interactive page) gives orders of magnitude: register/L1 →
L2 → main memory → SSD → spinning disk seek → same-DC round trip → cross-continent round
trip, spanning roughly **sub-nanosecond to hundreds of milliseconds (~9 orders of
magnitude).** The *relative ordering and order-of-magnitude gaps* are the durable teaching
point.

**The specific numeric values (e.g. L1 ≈ 0.5 ns, main memory ≈ 100 ns, SSD random read,
disk seek ≈ ms, same-DC RTT, CA↔Netherlands RTT) are `[UNVERIFIED from fetched source]`
this session — every host hosting that table returned HTTP 000.** Do NOT harden any exact
ns/ms figure into course prose until the primary is fetched. What IS verified from source
(reused canon, see §2): the *structure* of the memory hierarchy and the 64-byte cache line.

---

## 2. Foundational sources

### Verified this session (by derivation — theorem-grade, no fetch required)
- **Little's Law** `L = λW` — area/accounting derivation reproduced in §1.1.
- **M/M/1 results** `L=ρ/(1−ρ)`, `W=S/(1−ρ)`, `W/S=1/(1−ρ)` — from birth–death balance;
  amplification table recomputed in §1.2.
- **Amdahl's Law** `1/((1−p)+p/N)`, ceiling `1/(1−p)` — §1.3.
- **USL** `C(N)=N/(1+α(N−1)+βN(N−1))`, knee `N*=√((1−α)/β)` — §1.4.
- **Fan-out tail** `1−(1−q)^N`; `0.99¹⁰⁰≈0.366` — §1.5.

### Reused verified canon (already line-checked in earlier sub-courses — do NOT re-fetch)
- **Memory hierarchy / SRAM-vs-DRAM / locality / the memory mountain** — verified in
  `01-computers-from-first-principles/_research_eater-csapp.md` §J (CS:APP ch.6).
- **64-byte cache line; false sharing; cache-local layout** — verified from source in
  `06-data-structures-for-systems/_research_probabilistic-distributed-queues.md` (LMAX
  Disruptor `Sequence` padding) and `_research_indexes-lsm-bloom.md` (RocksDB
  `util/bloom_impl.h` cache-local Bloom, 64-byte line).
- **Cache-line waste on wide tuples** — `07-database-internals/_research_optimizer-external-exec.md`.
- **Tail-latency-driven refresh** (cache stampede / stale-while-revalidate) —
  `08-caches-and-storage-systems/_research_admission-dogpile-consistency.md`.

### Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals)
- Jeff Dean, **"Latency Numbers Every Programmer Should Know"** (Stanford 295 talk / jboner
  gist `2841832` / Colin Scott interactive page) — the exact ns/ms table.
- Ulrich Drepper, **"What Every Programmer Should Know About Memory"** (LWN 2007 series /
  akkadia.org PDF) — cache mechanics, access-pattern measurements.
- **Little (1961)**, "A Proof for the Queuing Formula L = λW" (Operations Research) —
  historical attribution of §1.1.
- **Kleinrock**, *Queueing Systems Vol. 1* — M/M/1, M/G/1, Pollaczek–Khinchine primary.
- **Amdahl (1967)**, AFIPS — historical attribution of §1.3.
- **Gunther**, *Guerrilla Capacity Planning* — USL primary.
- **Dean & Barroso, "The Tail at Scale" (CACM 2013)** — also tracked in 12's canon.

---

## 3. "Why it's this way" — the forcing functions

- **Little's Law is a conservation law, so it cannot be cheated.** If throughput and latency
  are both fixed, concurrency is determined; you cannot wish away the in-flight count. This
  is *why* connection/thread-pool sizing is arithmetic, not taste.
- **The utilization wall exists because queues integrate variability.** Any time arrivals
  occasionally exceed instantaneous service capacity, work accumulates; the closer mean load
  is to capacity, the longer it takes to drain, and the integral (`1/(1−ρ)`) diverges. You
  buy latency headroom with idle capacity — there is no free lunch.
- **Amdahl/USL exist because coordination is not free.** Serial sections and pairwise
  coherency traffic are physical costs (a lock is a serialization point; cache coherence is
  real bus/interconnect traffic). The `N²` term is the mathematical shadow of "everyone has
  to agree."
- **Tails dominate at scale because independent rare events compose.** Fan-out turns a
  per-backend 1% tail into a per-request near-certainty; this is pure probability, not bad
  engineering — which is why the *architectural* responses (hedging, replication, budgets)
  are the only fix.
- **The latency hierarchy is set by physics + economics.** Speed-of-light bounds RTT (≈ the
  CA↔Europe floor); the SRAM/DRAM/flash/disk gaps are density-vs-speed-vs-cost tradeoffs
  (the CS:APP "why a hierarchy" argument, verified in 01). The numbers move with hardware
  generations; the *ratios and ordering* are stable.

---

## 4. Common misconceptions to preempt

- **"Run servers near 100% to be efficient."** False — §1.2: latency is `1/(1−ρ)`. Past the
  knee, utilization "efficiency" is bought with catastrophic latency. Plan to a target ρ
  (often 0.5–0.7 for latency-sensitive services), not to saturation.
- **"More cores ⇒ proportional speedup."** False — Amdahl caps at `1/(1−p)`; USL can go
  *retrograde*. There is an optimal concurrency `N*`, beyond which throughput *drops*.
- **"Average latency is the SLO."** False — users live in the tail; the mean is nearly
  useless under fan-out (§1.5). Specify and measure p99/p99.9.
- **"Little's Law needs Poisson/exponential assumptions."** False — it is distribution-free.
  (M/M/1 needs them; Little's Law does not. Don't conflate the two — a frequent student error.)
- **"The latency numbers are exact constants."** False — they are order-of-magnitude
  intuition that drifts with hardware; teach ratios, not memorized nanoseconds. (And this
  session they are `[UNVERIFIED]` anyway.)
- **"Back-of-envelope means guessing."** False — it is disciplined arithmetic: pick the
  dominant cost, apply Little's Law / the latency hierarchy, sanity-check units and orders of
  magnitude. The discipline is the skill.

---

## 5. Best build-your-own target(s)

- **A queueing-wall simulator / notebook.** Implement an M/M/1 (and M/M/c) discrete-event
  simulator; plot measured mean response time vs. ρ and overlay the analytic `S/(1−ρ)`. The
  student *sees* the wall and confirms the theory empirically. Extend with high-variance
  (M/G/1) service times to watch the P-K variance term inflate the queue. (Pairs with
  appendix **N-math-for-systems**.)
- **A back-of-envelope drill kit.** A set of "size this" prompts (QPS for a feed, storage for
  N years of events, bandwidth for a video tier, concurrency for a thread pool) solved purely
  via Little's Law + the latency hierarchy, with a worked rubric. Feeds directly into
  **21-design-case-studies**.
- **A USL fitter.** Given (N, throughput) measurements, fit α and β (least squares) and
  predict `N*`. Connects scaling math to real benchmark data.

---

## 6. Open questions / where sources disagree / gaps to close

- **Pillar 2 is entirely blocked.** Every exact latency-hierarchy number (Dean) and Drepper's
  measurements are `[UNVERIFIED from fetched source]`. Until fetched, the brief teaches the
  *method* rigorously and the *numbers* only as flagged orders of magnitude. **This is the
  reason Cluster A is a clean checkpoint and 13 is NOT reconciled yet.**
- **Historical attributions unverified:** Little (1961), Kleinrock, Amdahl (1967), Gunther
  USL, Pollaczek–Khinchine. The *math* is verified by derivation; the *citations* need
  primaries.
- **Disagreement to resolve with sources:** Amdahl vs. **Gustafson's Law** (weak vs. strong
  scaling — Gustafson argues problem size grows with N, softening Amdahl's ceiling). Worth a
  paragraph once both primaries are fetched.
- **Planned future clusters for 13 (not started):**
  - *Cluster B — bottleneck identification & the USE method* (Gregg USE: Utilization /
    Saturation / Errors; resource-vs-workload; profiling/flame graphs). Note Gregg's site was
    HTTP 000 this session.
  - *Cluster C — horizontal vs. vertical scaling, statelessness, the scaling cube* (AKF
    cube: X/Y/Z-axis splits) and where each axis pushes you toward sub-courses 14/15/16.
  - *Cluster D — load testing & capacity planning method* (closed vs. open models, coordinated
    omission — Tene; how to measure the wall you derived here).
- **Reuse boundary:** 13 should cross-link *down* into appendix **N-math-for-systems** for the
  full queueing/probability derivations rather than duplicating them, per the two-tier design.
