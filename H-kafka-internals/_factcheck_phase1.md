# Appendix H · Phase-1 factcheck — kafka-internals

> Method (spine discipline): every load-bearing claim is (a) RECOMPUTED in `_recompute.py` (13/13) or
> (b) VERIFIED against a local primary / 09's line-verified Kafka 3.9 source reads. H is a **reference
> appendix** (no exercises). **0 blockers.** Network: kafka.apache.org HTTP **000** this wave (still
> blocked; retried) → NO new kafka.apache.org/arxiv fetch; Kafka constants reused from **09** (which
> cited apache/kafka **3.9** source + docs verbatim). KIP rationale stays `[UNVERIFIED]`.

## Bespoke structure note
H is a **"distributed log machine" layer walkthrough** (partitioned log → segments/retention →
ISR replication → high watermark/epochs → consumer groups/offsets → delivery semantics → EOS/
transactions → KRaft), NOT the 13-20 four-cluster shape and NOT a build progression. Reference-grade,
deep on ONE engine (Apache Kafka 3.9).

## Reused from 09 (line-verified apache/kafka 3.9 source + docs)
- `LocalLog.scala`/`LogSegment.java`/`LogConfig.java`: append-only segmented log; segment sizing,
  retention time/size, compaction → segment-retention recompute.
- `Partition.scala`/`ReplicaFetcherThread.scala`: leader append, ISR shrink/expand, **high watermark**
  advancement, follower HW from fetch → HW≤LEO recompute.
- `ProducerConfig.java` (3.9 defaults): `acks="all"`, `enable.idempotence=true`,
  `min.insync.replicas=1`, `replica.lag.time.max.ms=30000`, unclean leader election disabled →
  durability-contract recompute.
- `__consumer_offsets` routing `Utils.abs(groupId.hashCode()) % numPartitions`, 50 offsets partitions,
  7-day retention → coordinator-routing recompute.
- Idempotent producer `(producerId, epoch, sequence)`; transactions `__transaction_state`, LSO,
  `read_committed`/`read_uncommitted`, control/abort markers → EOS recompute.
- Leader epochs (`LeaderEpochFileCache`, `AbstractFetcherThread`) for divergence/truncation repair.

## Reused from 17 + Nishtala (local primaries)
- 17 delivery-semantics math: dup certainty `1-(1-p)^N` → duplicates-near-certain recompute.
- **Nishtala NSDI 2013** (`nishtala.txt`, local+VERIFIED): thundering-herd 17K→1.3K via leases →
  reused as the leader-failover metadata-refresh herd analogy (backoff+jitter on NOT_LEADER).

## Reused from 11/15/L
- Quorum intersection (majority `2f+1`) vs ISR (`f+1` with all-in-sync ack) → the ISR-vs-majority
  tradeoff recompute.

## Recomputed claims (`_recompute.py`, 13/13)
- Consumer parallelism ≤ partitions; per-partition ordering. PASS×2.
- Segment retention = whole-segment unlink, not row rewrite. PASS.
- `acks=all` + `min.isr=2` + RF=3 tolerates 1 ISR loss (canonical durable config). PASS×2.
- HW ≤ leader LEO hides under-replicated tail. PASS.
- ISR tolerates f with f+1 replicas vs majority 2f+1. PASS.
- Committed offset = last_processed + 1. PASS 1 of 50 offsets partitions by hash. PASS.
- At-least-once → duplicates near-certain w/o idempotence; idempotent producer dedups. PASS×2.
- EOS boundary = {output records + offset commit}; external sinks excluded. PASS.
- Failover herd cut ~13× (Nishtala). PASS.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- **Kafka original paper** (Kreps/Narkhede/Rao) — kafka.apache.org HTTP 000; mirror not re-fetched
  this wave (the PDF-paper/mirror retry is still owed). Design claims stated via 09's source reads.
- **KIPs** (KIP-98 EOS, KIP-101 leader epochs, KIP-500 KRaft, KIP-848 new consumer protocol,
  KIP-360) — rationale `[UNVERIFIED]`; cwiki not fetched.
- **KRaft deep internals** (`QuorumController`/`KafkaRaftClient` metadata quorum, ELR/eligible leader
  replicas) — cited as "separate metadata Raft quorum," details not line-verified beyond 09.
- **Fetch-from-follower / rack-aware** replica selection path — mechanism only.
- **Transaction recovery** (`TransactionMarkerChannelManager` retry, `__transaction_state`
  expiration), sticky/cooperative assignor algorithm — deferred.
- Segment size 1 GiB used as default-ish illustration; exact `segment.bytes` is config-dependent.
All logged, none load-bearing (numbers recomputed or from 09's line-verified 3.9 source).

## Verdict
H is honest and appendix-appropriate: the log/replication/EOS cores come from 09's line-verified
Kafka 3.9 source reads, the delivery-semantics + herd math reuse local 17/Nishtala, and every dived
number is recomputed (13/13). The owed Kafka paper/KIP fetches remain blocked (kafka.apache.org 000)
and are carried `[UNVERIFIED]`. Reconcile into `_research.md`. **0 blockers.**
