# 17 — async-queues-and-event-driven-architecture — Phase 1 factcheck

> Scope: verify the **load-bearing** claims of the four clusters. Method per claim: **RECOMPUTE**
> (math in `_recompute.py`, pure stdlib, 0 errors), **REUSE** (line-verified in an earlier
> sub-course; cite it; do NOT re-derive), or **PRIMARY** (confirmed against a fetched source this
> session). Anything not in those three buckets stays `[UNVERIFIED from fetched source]`.
> Verdict: **0 blockers.**

## A. Recomputed math (`_recompute.py`, run clean)
| # | Claim | Result | Verdict |
|---|-------|--------|---------|
| 1 | At-least-once duplicates: `E[dups]=N·p`, `P(≥1)=1−(1−p)^N` | p=1e-4,N=1e6 → E≈100, P=1.0 |  RECOMPUTE |
| 2 | Dedup window = redelivery horizon = `Σcapped-exp-backoff + visibility` | retries8/base1/cap60/vis30 → **213 s**; store=`rate·window·bytes` (50K/s·213·64B≈682 MB) |  RECOMPUTE |
| 3 | Batching: per-msg=`c/B+m`, tput=`1/(c/B+m)` → asymptote `1/m` | c=1ms,m=5µs: B=100→67K, B=10K→196K, ceiling 200K msg/s |  RECOMPUTE |
| 4 | Retention disk=`rate·bytes·ret·RF`; compaction floor=`keys·bytes` (history-independent) | 1e6/s·256B·72h·RF3≈199 TB; 1e8 keys·64B≈6.4 GB |  RECOMPUTE |
| 5 | Parallelism ceiling: consumers/group ≤ partitions; need=`ceil(target/per)` | 500K/s÷20K/s→25 partitions |  RECOMPUTE |
| 6 | Dual-write failure window: `P(bad/op)≈window·crash_rate` | 100 ms window, 30-day MTBF → ~38 bad/1e9 ops (nonzero → leaks) |  RECOMPUTE |
| — | Fan-out tail `1−(1−q)^N` (Cluster D §1.3) | reuses 13's already-verified result |  REUSE 13 |

## B. Reused, line-verified mechanisms (NOT re-derived)
| Claim | Source (line-verified earlier) | Verdict |
|-------|--------------------------------|---------|
| Log = ordered append-only partition addressed by offsets; retention/compaction; consumer groups + coordinator; position≠committed; HW≤LEO; idempotent producer (PID+epoch+seq); transactional offset commit / LSO / `read_committed` | **09** `_research.md` (Kafka source: `LocalLog.scala`, `LogSegment.java`, `LogCleaner.scala`, `GroupCoordinatorService`, `__consumer_offsets`) |  REUSE 09 |
| Per-partition (partial) order; total order needs consensus; exactly-once delivery impossible (Two Generals); 2PC blocking | **11** `_research.md` |  REUSE 11 |
| Shard/partition key = ordering+parallelism+placement unit; hot shard / celebrity key; repartition cost; consistent hashing/vnodes; cross-shard txn → saga; denormalized read copies | **14** (+**06** consistent hashing) |  REUSE 14/06 |
| Logical/row replication log = CDC source; durability dial sync/async/semi-sync; quorum overlap `W+R>N`, majority tolerates `floor((N−1)/2)`; semilattice/idempotent merge; materialized view = stale replica + staleness ladder | **15** (+**11**) |  REUSE 15 |
| Cache/projection = deliberately-stale replica; backoff+jitter; coalescing | **16** (+**08** Redis/TTL dedup store) |  REUSE 16/08 |
| Little's Law / amortization; queueing latency wall (ρ→1); fan-out tail `1−(1−q)^N`; retry discipline | **13** (+**03**) |  REUSE 13/03 |

## C. Verified from a fetched primary THIS session (network partially healed)
| Claim | Source | Receipt | Verdict |
|-------|--------|---------|---------|
| Cache-aside = "demand-filled look-aside cache"; deletes (not updates) on write | Nishtala et al., *Scaling Memcache at Facebook*, NSDI '13 | `/tmp/nishtala.txt` L98–118, Fig.1 |  PRIMARY |
| Leases (64-bit token) regulate the **thundering herd**; server returns a token ≤ once / 10 s / key | same, §3.2.1 | L371–406 |  PRIMARY |
| Herd cut: peak DB query rate **17K/s → 1.3K/s** with leases | same, §3.2.1 | L406–410 (verbatim) |  PRIMARY |
| **mcsqueal**: CDC daemon reads DB **commit log**, extracts deletes, broadcasts cross-region; **only 4% of deletes actually invalidate** | same, §4.1 Regional Invalidations + Fig.6 | L565–604 |  PRIMARY |
| (Upgrades 16/08 carry-forward) RFC 9111/5861/7234/4786 fetched (text on disk for 16's verification, see 16 factcheck update) | rfc-editor.org (HTTP 200) | `/tmp/rfc9111.txt` etc. |  PRIMARY (16) |

> Note: the Nishtala + RFC fetches are *opportunistic upgrades to 16/08's carry-forward gaps*, applied
> here because the network healed mid-session. For 17 itself, Nishtala is the concrete EDA/CDC instance
> (Cluster A §1.6, Cluster B §1.5) — a production "CDC off the commit log drives async invalidation."

## D. Still `[UNVERIFIED from fetched source]` (carry forward; HTTP 000 this session)
- **Cluster A:** AMQP 0-9-1 / JMS ack semantics; SQS visibility-timeout/FIFO dedup-window; RabbitMQ
  publisher-confirms/consumer-acks; Debezium CDC docs; Kafka EOS KIPs (KIP-98/129/447) text.
- **Cluster B:** Garcia-Molina & Salem "Sagas" SIGMOD 1987; Fowler Event-Sourcing/CQRS/EDA articles;
  Young/Dahan CQRS; Richardson microservices.io saga/outbox; Vernon/Evans DDD.
- **Cluster C:** Kafka KIP-429 (cooperative rebalance); exact `session.timeout.ms`/
  `max.poll.interval.ms`/`auto.offset.reset` doc wording; SQS redrive/DLQ + RabbitMQ DLX docs.
- **Cluster D:** Kreps et al. "Kafka: a Distributed Messaging System for Log Processing" NetDB 2011;
  Kafka exact defaults (`acks`/`min.insync.replicas`/`linger.ms`/`batch.size`/unclean-election/codecs);
  Pulsar/BookKeeper, NATS JetStream, Kinesis durability docs.
- All are **named-attribution / vendor-exact-wording** gaps. Every underlying *mechanism* is verified
  by reuse(09/11/13/14/15/16) or recomputation. None is load-bearing for the method. Do NOT harden
  these specifics into Phase-2 prose until fetched.

## Verdict
**0 blockers.** 17's load-bearing content is verified end-to-end: 6 math claims by recomputation, all
mechanisms by reuse of line-checked 09/11/13/14/15/16/06/08/03, and a fresh production EDA/CDC primary
(Nishtala NSDI '13). Remaining gaps are canonical/vendor attributions, uniformly carried forward.
