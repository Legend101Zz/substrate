# Verified primaries — 2026-06-10 (Wave 9, sub-course 20 resilience-failure-and-capacity-planning)

Network heal continued. The following were fetched THIS session for 20 and verified verbatim.
Files live in `meta/fetched_primaries/`.

| source | file(s) | HTTP | what it anchors (20) |
|--------|---------|------|----------------------|
| Dean & Barroso, "The Tail at Scale" (Jeff Dean talk deck, CACM 2013 companion) | `tail-at-scale-cacm2013.{pdf,txt}` (already local, canon haul) | 200 | Cluster B: fan-out tail 1−0.99^100=63%; hedged/backup requests (33ms→14ms avg, 994ms→50ms p99.9 @10ms backup, <5% extra load); tied requests w/ cross-server cancellation (−43%/−38%, ~1% extra reads); micro-partitioning; selective replication; latency-induced probation; canary requests; tainted partial results |
| AWS Builders' Library, "Workload isolation using shuffle-sharding" (Colm MacCárthaigh) | `aws-shuffle-sharding.{html,txt}` | 200 | Cluster C: 8 workers, shard-of-2 → C(8,2)=28 combos → 1/28 blast radius = 7× better than 4 plain shards (1/4); Route 53 = 2048 virtual name servers, shard-of-4 → ~730 billion combos; "scope of impact"; recursive shuffle-sharding; Infima library |
| AWS Builders' Library, "Timeouts, retries, and backoff with jitter" (Marc Brooker) | `aws-timeouts-retries-backoff.{html,txt}` | 200 | Cluster A/C: exponential backoff; jitter to break retry correlation; per-host deterministic jitter for scheduled work; retry amplification across N layers (5-deep × 3 retries); circuit breakers; token-bucket retry budgets; idempotency required to retry; client(4xx) vs server(5xx) retryability |
| Brewer, "Towards Robust Distributed Systems" (PODC 2000 keynote) | `brewer-podc-2000.{pdf,txt}` | 200 | Cluster A/D: CAP — "at most two of these properties" (Consistency, Availability, Partitions); Forfeit Partitions / Forfeit Availability / Forfeit Consistency; BASE = Basically Available, Soft state, Eventual consistency; ACID↔BASE spectrum |
| Kleppmann, "Please stop calling databases CP or AP" (2015) | `kleppmann-cap-2015.{html,txt}` | 200 | Cluster A: CAP is a narrow formal result (Gilbert–Lynch linearizability + total availability + arbitrary partitions); critique of using CAP as a design taxonomy; partitions are a fault you don't choose |
| Netflix, "The Netflix Simian Army" (2011) | `netflix-simian-army.{html,txt}` | 200 | Cluster C: Chaos Monkey (kills instances in prod), Latency Monkey (induces latency/errors → simulates degradation + partial failure), Conformity/Doctor/Janitor/Security/10-18/Chaos Gorilla (kills an entire AWS Availability Zone). Failure injection as continuous verification |

## Still blocked this session (retried)
- CoDel — `queue.acm.org` HTTP **403** (carried forward; SEDA/bounded-queue + deadline-drop
  already covered via 18 + SEDA primary).
- `raft.github.io/raft.pdf` HTTP **000** (Raft already line-verified via Lamport Paxos primaries
  in 11/12; not load-bearing for 20).
- Nygard "Release It!" (book — no free primary; circuit-breaker/bulkhead/stability-pattern
  attributions carried `[UNVERIFIED]`; mechanisms themselves verified via 18 + AWS builders').

## Method note
Brewer PDF text extracted with pypdf in a throwaway uv venv under `/tmp/pdfv`, removed after.
HTML stripped to text with sed/tr. Nothing under `/Users/m0t0hu6/.code-puppy-venv` touched.
