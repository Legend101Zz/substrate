# 13 scaling-fundamentals — Cluster B: bottleneck identification & the USE method

> Phase 1 research brief (NO course prose). Standard six sections. Primary sources first;
> anything not fetched-and-verified this session is flagged `[UNVERIFIED from fetched source]`.
>
> **Network reality this session (5th consecutive):** only `lamport.azurewebsites.net` and
> Walmart artifactory resolve. `brendangregg.com/usemethod.html`, the USE-method checklists,
> the flame-graph pages, and the *Systems Performance* errata all returned **HTTP 000**
> (verified by direct `curl` this session). Consequence: the **method's logic** is presented
> from first principles and cross-linked to math already verified in Cluster A; the **exact
> wording, checklists, and Gregg's specific tooling tables are flagged** and carried forward.
>
> **Scope of this cluster:** how to *find* the bottleneck — the resource-oriented USE
> method (Utilization / Saturation / Errors), the resource-vs-workload distinction, the
> difference between a *latency* investigation and a *resource* investigation, and the
> profiling instruments (sampling profilers, flame graphs, off-CPU analysis) that localize
> it. This cluster answers "*where* is the wall Cluster A proved must exist?"

---

## 1. Key mechanisms (how the thing actually works, deeply)

### 1.1 Why you need a *method*, not a hunch

Cluster A proved that a system has a hyperbolic latency wall as some resource approaches
100% utilization (`W/S = 1/(1−ρ)`). But a real system has *many* resources (CPUs, cores,
memory capacity, memory bandwidth, disks, network links, locks, connection pools, file
descriptors). The wall belongs to **whichever resource saturates first** — the bottleneck.
Performance debugging fails when engineers start from tools ("let me run `top`") instead of
from a *complete checklist of resources*. The USE method exists to make the search
**exhaustive and resource-complete** rather than tool-driven and lucky.

### 1.2 The USE method — Utilization, Saturation, Errors, for every resource

The USE method (attributed to Brendan Gregg) is a checklist discipline:

> **For every resource, check Utilization, Saturation, and Errors.**

- **Utilization** — the *average* fraction of time the resource was busy over an interval
  (e.g. CPU 90% busy, disk 80% busy). For *capacity-type* resources (memory, disk space) it
  is instead the proportion *used* (e.g. 95% of RAM allocated). Utilization tells you how
  close you are to the Cluster-A wall.
- **Saturation** — the degree to which the resource has **queued work it cannot service
  yet**: run-queue length, disk I/O queue depth, swap activity, `TCP` accept-queue overflow,
  thread-pool wait count. Saturation is the *direct* observable of the queue that Little's
  Law/M-M-1 model: **non-zero saturation means you are already paying the `1/(1−ρ)` tax.**
- **Errors** — count of error events (failed disk I/O, dropped packets, ECC corrections,
  malloc failures, retransmits). Errors are checked *first* in practice because they are
  usually quick to read and can be the actual cause even at low utilization.

**The mechanism that makes USE powerful:** it inverts the usual workflow. Instead of
"observe a symptom → guess a cause → find a tool," you **enumerate resources → for each,
read U, S, E.** A resource with high utilization *and* non-zero saturation is the
bottleneck; a resource with errors is a fault. This is a *resource-complete* sweep: nothing
gets skipped because you didn't think to look. [The exact per-resource checklist tables and
Gregg's recommended Linux tools (e.g. which counter maps to saturation for each resource)
are `[UNVERIFIED from fetched source]` this session — `brendangregg.com` HTTP 000.]

### 1.3 Resource analysis vs. workload analysis — two directions on the same path

There are two complementary investigation directions, and confusing them wastes hours:

- **Resource analysis (bottom-up):** start at the hardware/OS resources and ask "what is
  saturated?" USE is the canonical resource-analysis method. Good for "the box is slow."
- **Workload analysis (top-down):** start at the *application request* and ask "where does a
  request spend its time / why is *this operation* slow?" Distributed tracing (sub-course 19,
  Dapper), request logs, and on-CPU profiles of the hot path are workload tools. Good for
  "this endpoint is slow."

The two meet in the middle: workload analysis localizes to a subsystem; resource analysis
confirms which physical resource that subsystem is starved on. **Little's Law is the bridge**
— a request's residence time `W` decomposes into service + waiting at each resource box it
passes through, so a slow request (workload view) is always a sum of per-resource waits
(resource view).

### 1.4 Utilization is necessary but not sufficient — the saturation insight

A subtle, load-bearing point: **average utilization can look fine while saturation is
killing you.** Two reasons, both grounded in Cluster A:

1. **Variance (the M/G/1 / Pollaczek–Khinchine effect).** A disk 50% utilized *on average*
   but hit by bursty, high-variance I/O can have a deep queue during bursts. The mean
   utilization hides the burst; the *saturation* metric (queue depth) does not. This is the
   `C²ₛ` variance term from Cluster A §1.2 showing up as an operational signal.
2. **Sampling interval aliasing.** "CPU 60% over 60 s" can be 100% for 36 s and 0% for 24 s.
   The shorter the true bursts, the more averaging lies. Saturation metrics (run-queue,
   `pressure stall information`) capture the instantaneous backlog that averaged utilization
   erases. [PSI/`/proc/pressure` specifics `[UNVERIFIED from fetched source]`.]

This is *why* USE checks Saturation separately from Utilization rather than treating "busy"
as one number.

### 1.5 Profiling instruments — localizing on-CPU and off-CPU time

Once USE points at a resource (say CPU), you localize *within* the software:

- **Sampling profilers.** Periodically interrupt the program (e.g. at a fixed Hz) and record
  the stack. Over many samples, the *fraction of samples* a function appears in approximates
  the *fraction of CPU time* spent there. Statistical, low-overhead, and the basis of
  production profiling. (Contrast with instrumenting every function call, which is
  high-overhead and perturbs the very timing you measure.)
- **Flame graphs (Gregg).** A visualization of *collapsed* sampled stacks: x-axis = the
  population of stacks sorted alphabetically (NOT time), width = proportion of samples
  (≈ proportion of time), y-axis = stack depth. The *widest* boxes at any level are where the
  time goes; you read top-down to find the leaf functions actually on-CPU. Crucially, **width
  = cost**, which makes the bottleneck literally the widest tower. [Flame-graph construction
  details and the original scripts are `[UNVERIFIED from fetched source]` — Gregg pages
  HTTP 000.]
- **On-CPU vs. off-CPU analysis.** On-CPU profiling finds where you burn cycles. But much
  latency is *off-CPU*: blocked on I/O, locks, or scheduler queues — exactly the *saturation*
  that USE flags. **Off-CPU flame graphs** sample blocked threads and their wait stacks,
  attributing time spent *waiting*. The pair (on-CPU + off-CPU) accounts for *all* of a
  thread's wall-clock time, which closes the loop with Little's Law (`W` = busy + waiting).

### 1.6 The bottleneck-shifts-then-reappears principle

Removing the top bottleneck does not "fix performance" — it **moves the wall to the next
resource.** This is a direct corollary of Cluster A: there is always a `1/(1−ρ)` curve for
*some* resource; relieving resource X just means resource Y now saturates first. Capacity
work is therefore iterative: USE-sweep → fix the saturated resource → re-sweep. The job ends
when the bottleneck is the one you *chose* to live with at your target utilization, not when
"there is no bottleneck."

---

## 2. Foundational sources

### Verified this session (by reasoning / reuse — no fetch required)
- **Saturation ⇔ the queue Little's Law/M-M-1 model** — the link between the USE
  "Saturation" signal and `1/(1−ρ)` is the *same math* verified by recomputation in
  Cluster A (`_factcheck_clusterA.md` claims #1–#4). Not a new external claim.
- **Variance inflates queues at modest mean utilization** — the M/G/1 Pollaczek–Khinchine
  reasoning, consistent with Cluster A §1.2 (P-K formula there is flagged; the *direction*
  — higher `C²ₛ` ⇒ deeper queue — is the mechanism used here).

### Reused verified canon (already line-checked in earlier sub-courses — do NOT re-fetch)
- **Memory hierarchy / memory bandwidth as a distinct resource from capacity** — CS:APP ch.6
  via `01-computers-from-first-principles/_research_eater-csapp.md` §J. (USE treats memory
  *capacity* and memory *bandwidth* as separate resources; the hierarchy justifies why.)
- **64-byte cache line / false sharing as a hidden coherency cost** —
  `06-data-structures-for-systems` Disruptor + RocksDB `bloom_impl.h` briefs. (False sharing
  is a USE "saturation/utilization" trap on the cache-coherency interconnect — the `β·N²`
  USL term from Cluster A §1.4 made physical.)
- **Tracing as the workload-analysis counterpart** — to be deepened in 19 (Dapper); flagged
  in 12 canon.

### Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals)
- Brendan Gregg, **"The USE Method"** (`brendangregg.com/usemethod.html`) — the canonical
  definition, the per-resource Linux/USE checklist, and tool mappings.
- Brendan Gregg, **flame-graph pages + FlameGraph scripts** (`brendangregg.com/flamegraphs.html`,
  GitHub `brendangregg/FlameGraph`) — construction, collapsed-stack format, off-CPU variant.
- Brendan Gregg, **_Systems Performance_** (2nd ed.) — USE/RED, resource vs. workload
  analysis, USE checklist tables.
- **RED method** (Tom Wilkie / Weaveworks: Rate, Errors, Duration) — the *service-level*
  counterpart to the *resource-level* USE; pairs with 19's SLO material. `[UNVERIFIED]`.
- **Linux PSI / Pressure Stall Information** docs (kernel.org) — modern saturation signal.
  `[UNVERIFIED]`.

---

## 3. "Why it's this way" — the forcing functions

- **USE is resource-*complete* because the wall belongs to whatever saturates first.** A
  tool-driven search can miss the actual bottleneck simply because nobody ran the right tool;
  enumerating *every* resource × {U,S,E} makes omission structurally impossible. The method's
  shape is dictated by Cluster A's truth that *some* resource hits `1/(1−ρ)` first.
- **Saturation is a first-class signal because averages hide queues.** The Pollaczek–Khinchine
  variance term and sampling-interval aliasing both mean utilization-alone undercounts pain;
  the only honest read of "are we past the knee?" is the *queue length itself*.
- **Sampling profiling is statistical because measuring everything changes the timing.**
  Full instrumentation perturbs the workload (observer effect) and adds overhead that
  *creates* a bottleneck; sampling trades exactness for fidelity-under-load. Width = cost in
  a flame graph is just the law of large numbers applied to stack samples.
- **Off-CPU matters because `W` = busy + waiting.** Little's Law forbids ignoring wait time;
  a profiler that only sees on-CPU work is blind to exactly the saturation USE flags. The two
  views are forced to be complementary by the residence-time decomposition.
- **Bottlenecks shift because the wall is intrinsic.** You never delete the `1/(1−ρ)` curve;
  you only choose which resource owns it and at what target ρ. This is why capacity work is a
  loop, not a one-shot fix.

---

## 4. Common misconceptions to preempt

- **"Low average utilization ⇒ no problem."** False — §1.4: bursty/high-variance load queues
  deeply at modest mean utilization, and averaging intervals alias away the bursts. Read
  *saturation*, not just utilization.
- **"100% CPU means CPU-bound."** Not necessarily — 100% on-CPU can be spin-waiting on a lock
  (a *saturation/coherency* problem), and the real fix is contention, not more cores (Cluster
  A USL `α`/`β`). On-CPU + off-CPU profiling disambiguates.
- **"Fix the top bottleneck and you're done."** False — §1.6: it just moves to the next
  resource. Re-sweep.
- **"Profiling = instrument every function."** False — that perturbs timing and adds overhead;
  statistical sampling is the production-correct instrument.
- **"Flame-graph x-axis is time."** False — it is sorted/merged stacks; **width is proportion
  of samples (≈ time), not chronological order.** A frequent reading error.
- **"USE and RED are the same."** No — USE is *resource*-oriented (find the saturated box);
  RED is *service*-oriented (Rate/Errors/Duration of a request stream). They answer different
  questions and pair up (resource vs. workload, §1.3).

---

## 5. Best build-your-own target(s)

- **A USE-sweep harness.** A script/notebook that, for a target box, reads U/S/E for each
  resource (CPU, memory capacity + bandwidth, disk, net, key locks/pools) and prints a
  resource-complete table flagging the saturated one. Teaches the checklist as code, and
  *demonstrates* that the saturated resource is the one whose `1/(1−ρ)` you're climbing.
- **A flame-graph from scratch.** Collapse sampled stacks (perf or a toy sampler), aggregate
  by stack, render width = sample count. The student sees "width = cost" and finds the hot
  tower themselves; extend to an off-CPU flame graph to visualize *waiting*.
- **A "bottleneck moves" demo.** Take the Cluster-A M/M/1 simulator, add a second resource in
  series, relieve the first, and watch the wall reappear at the second — making §1.6 concrete.
- (Pairs with appendix **B-linux-internals** for the actual counters and **N-math-for-systems**
  for the queueing derivations.)

## 6. Open questions / where sources disagree / gaps to close

- **Gregg's exact USE checklist + tool mappings are blocked.** Until `brendangregg.com` is
  fetchable, the per-resource tables (which counter = saturation for each resource) and the
  flame-graph construction details stay `[UNVERIFIED from fetched source]`. Teach the
  *method's logic* now; pin the exact checklist before Phase-2 prose.
- **RED vs. USE attribution + precise definitions** (Wilkie/Weaveworks) need the primary.
- **PSI / modern saturation signals** (`/proc/pressure`) need kernel.org docs to pin exact
  semantics; cross-link to appendix B.
- **Boundary with 19 (observability):** USE/RED *definitions* live here as the bottleneck-
  finding method; the *SLO/tracing/Dapper* machinery is 19's job. Keep the line clean so we
  don't duplicate.
- **Boundary with 20 (resilience/capacity):** "the wall moves" iterative capacity loop is
  introduced here as method; the *failure/headroom/tail-tolerance* engineering is 20.
