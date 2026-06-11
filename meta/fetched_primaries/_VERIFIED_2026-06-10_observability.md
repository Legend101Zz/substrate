# Verified primaries — 2026-06-10 (Observability haul for sub-course 19)

Network healed: `static.googleusercontent.com` (research.google mirror) + `sre.google`
returned HTTP 200. Fetched + extracted + verified to `meta/fetched_primaries/`.

## Dapper (Google Technical Report dapper-2010-1, April 2010)
File: `dapper-2010.pdf` (1,551,487 B, PDF 1.4, 14 pages) + `dapper-2010.txt` (63,999 chars,
extracted with pypdf in a throwaway uv venv, removed after).
Authors: Sigelman, Barroso, Burrows, Stephenson, Plakal, Beaver, Jaspan, Shanbhag.

Verified verbatim load-bearing claims (line numbers in the .txt):
- **Design goals** (§1): "Low overhead", "Application-level transparency", "Scalability";
  plus the freshness goal "ideally within a minute".
- **Trace model** (§2.1): "We tend to think of a Dapper trace as a tree of nested RPCs."
  "the tree nodes are basic units of work which we refer to as spans. The edges indicate a
  cas[u]al relationship between a span and its parent span." Spans carry a **span name,
  span id, and parent id**; root spans have no parent id; all spans in a trace share a
  common **trace id**; "All of these ids are probabilistically unique 64-bit integers."
- **Two-host spans + clock skew** (§2.1): "every RPC span contains annotations from both
  the client and server processes, making two-host spans the most common ones." Clock skew
  handled by the ordering invariant "an RPC client always sends a request before a server
  receives it, and vice versa for the server response" → a lower/upper bound on server-side
  timestamps. (Reuses 11 happens-before / no global clock.)
- **Context propagation** (§2.2): trace context in **thread-local storage**; carried across
  async callbacks via the common control-flow library; span+trace ids transmitted client→
  server in the RPC framework. Language-independent (C++ & Java).
- **Sampling for low overhead** (§1.1, §2.4, §4.4): "we have found sampling to be necessary
  for low overhead"; "a sample of just one out of thousands of requests provides sufficient
  information for many common uses". First prod version: **uniform 1/1024** ("one sampled
  trace for every 1024 candidates"); moving to **adaptive sampling** parameterized by a
  desired rate of sampled traces per unit time (low-traffic↑, high-traffic↓).
- **Overhead numbers** (§4.1, Table 2): root span create/destroy **204 ns**, non-root
  **176 ns**; unsampled annotation thread-local lookup **~9 ns**; sampled string annotation
  **40 ns** (2.2 GHz x86). Table 2 latency/throughput penalty vs sampling frequency:
  1/1→16.3% lat / −1.48% tput; 1/16→2.12% / −0.08%; 1/1024→−0.20% / −0.06%
  (experimental error 2.5% lat, 0.15% tput). Span ≈ **426 bytes** avg; trace collection
  < **0.01%** of production network traffic; daemon < **0.3%** of one core (Table 1).
- **Collection** (§2.5): 3-stage (local log → daemon pull → regional Bigtable cell); a trace
  is one Bigtable row, each span a column (sparse). Median collection latency **< 15 s**.
- **Out-of-band / decoupled**: tracing is collected asynchronously, off the request path.

## Google SRE Book — Ch.4 "Service Level Objectives" (sre.google/sre-book)
File: `sre_slo.txt` (25,827 chars, HTML stripped).
Verified: **SLI** = "a carefully defined quantitative measure of some aspect of the level
of service"; **SLO** = "a target value or range of values for a service level that is
measured by an SLI", natural structure "SLI ≤ target, or lower bound ≤ SLI ≤ upper bound";
**SLA** = "an explicit or implicit contract with your users that includes consequences of
meeting (or missing) the SLOs". Availability = fraction of well-formed requests that
succeed (a.k.a. yield). "Most metrics are better thought of as distributions rather than
averages" → use percentiles (50th/99th/99.9th), not means (reuses 13 tail discipline).
"it is better to allow an error budget" — 100% is the wrong target. The Chubby
planned-outage example (don't significad your SLO). "Have as few SLOs as possible."

## Google SRE Book — Ch.6 "Monitoring Distributed Systems" (sre.google/sre-book)
File: `sre_monitoring.txt` (30,822 chars).
Verified: **The Four Golden Signals** = "latency, traffic, errors, and saturation. If you
can only measure four metrics of your user-facing system, focus on these four." Latency:
"distinguish between the latency of successful requests and the latency of failed requests."
Saturation: "how full your service is", + impending-saturation prediction. **White-box
vs black-box** monitoring; black-box = symptom-oriented (active problems now), white-box =
internals/telemetry for debugging. "page a human when one signal is problematic". Mean
hides tails → percentiles. Symptoms-for-paging, causes-for-debugging.

## Google SRE Workbook — Ch.5 "Alerting on SLOs" (sre.google/workbook)
File: `sre_workbook_alerting.txt` (30,617 chars).
Verified the burn-rate canon (all numbers recomputed in `19.../_recompute.py`):
- **Error budget** for a window = (1 − SLO) of total events; alert dimensions =
  precision, recall, detection time, reset time.
- **Burn rate** = "how fast, relative to the SLO, the service consumes the error budget."
  Burn rate 1 ⇒ exactly 0 budget left at end of the SLO window.
- Time-to-fire = (1 − SLO) × window × burn_rate / error_rate; budget consumed at fire =
  burn_rate × (alerting_window / SLO_period).
- "Five percent of a 30-day error budget spend over one hour requires a burn rate of 36."
- **Recommended multi-burn-rate (Table 5-6 / 5-8, for 99.9% SLO):**
  - Page: 2% budget / 1 h window / **burn rate 14.4** (short window 5 m)
  - Page: 5% budget / 6 h window / **burn rate 6** (short window 30 m)
  - Ticket: 10% budget / 3 d window / **burn rate 1** (short window 6 h)
- **Multiwindow, multi-burn-rate**: AND a short window (guideline 1/12 of the long window)
  so the alert stops firing once burning stops (better reset time). PromQL examples verified.

All four are PRIMARY sources fetched this session. Receipts: this file + the .txt/.pdf
artifacts alongside it.

## BONUS UPGRADE: SEDA (Welsh/Culler/Brewer, SOSP 2001) — finally unblocked
File: `seda-sosp01.pdf` (305,499 B, 14 pp) + `seda-sosp01.txt` (93,103 chars).
Fetched from `https://www.sosp.org/2001/papers/welsh.pdf` (HTTP 200) — also live at
`people.eecs.berkeley.edu/~brewer/papers/SEDA-sosp.pdf`. Blocked 8+ sessions; now reachable.
This is the headline primary for **18 Cluster B** (carried `[UNVERIFIED]` since 18 was built).

Verified verbatim (line refs in the .txt):
- Title: "SEDA: An Architecture for Well-Conditioned, [Scalable Internet Services]";
  "we call the staged event-driven architecture (SEDA)."
- **Stage = the fundamental unit** (S3.2): "A stage is a self-contained application component
  consisting of an event handler, an incoming event queue, and a thread pool... Each stage is
  managed by a controller that affects scheduling and thread allocation. Stage threads operate
  by pulling a batch of events off of the incoming event queue and invoking the
  application-supplied event handler... dispatches zero or more events by enqueuing them on the
  event queues of other stages." -> confirms 18B's stage/queue/thread-pool/controller model.
- **Well-conditioned = graceful degradation** (S2): "a service is well-conditioned if it
  behaves like a simple pipeline... As the offered load increases, the delivered throughput
  increases proportionally until the pipeline is full and the throughput saturates; additional
  load should not degrade throughput." "The key property of a well-conditioned service is
  graceful degradation: as offered load exceeds capacity, the service maintains high throughput
  with a linear response-time penalty that impacts all clients equally." -> confirms 18B/18C
  goodput-plateau + 13 queueing-wall reuse.
- **Dynamic resource controllers** (Abstract/S3.1): "a set of dynamic resource controllers to
  keep stages within their operating regime... thread pool sizing, event batching, and [load
  shedding/admission control]." -> confirms 18B self-tuning controllers + 18A batching.
- **Explicit/bounded event queues for load conditioning** (S2/S3): "individually conditioned
  to load by thresholding or filtering its event queue"; "making event queues explicit allows
  applications to make [load-conditioning decisions]." -> confirms 18B bounded-queue thesis.
- **Bounded thread pools** (S2.2) + closed-loop "response time should increase linearly with
  the number of clients" -> ties to 13 Cluster D closed-model + Little's Law.

Applied: UPGRADE section appended to `18-.../_factcheck_phase1.md` (carry-forward SEDA
`[UNVERIFIED]` -> VERIFIED; nothing erased). Deep per-figure factcheck deferred to 18 Phase 2.
