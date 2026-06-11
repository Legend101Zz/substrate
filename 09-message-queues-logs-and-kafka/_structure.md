# 09 — Message Queues, Logs, and Kafka · _structure.md

**Identity:** the log as a foundational abstraction — and how a retained, partitioned log
becomes a queue, a pub/sub bus, a replication backbone, and a stream processor. The piece
that decouples producers from consumers in time.

**Bespoke shape — "build the log up one guarantee at a time."** NOT a Kafka feature tour.
Start from the simplest possible thing (an append-only file) and add exactly one capability
per chapter, each driven by a constraint the previous version can't meet: storage →
retention/compaction → replication → committed-data semantics → consumer groups/offsets →
delivery semantics → exactly-once. Kafka 3.9 source is the running reference, but the THESIS
is the log abstraction (Kreps), not Kafka trivia. Version caveats are load-bearing —
Kafka has opinions and migrations; preserve them.

## Dependency position
- **Depends on:** 06 (the log = segments + sparse index + ring-buffer ideas), 04 (sequential
  I/O, page cache, fsync), 03 (replication ships over the network), 11 (ISR/HW are quorum/
  consensus ideas — leader epochs ≈ terms), 07/15 (offsets-as-WAL, replication).
- **Feeds into:** 17 (async/event-driven architecture = the system-design application),
  26 (transcript-as-WAL reuses log/offset), 27 (multi-agent = distributed log consumers),
  19 (CDC/delete-streams).
- **Appendix links DOWN:** H-kafka-internals (the distributed-log machine in full: KRaft,
  EOS recovery, ELR, fetch-from-follower), L-consensus (ISR vs majority quorum). 09 teaches
  the log abstraction; H is the Kafka deep-dive.

## Chapter specs (3–5 lines each)
0. **The log: the abstraction under everything** (short opener) — Kreps's inversion: don't
   delete on ack; RETAIN by policy and let consumers track position. This enables replay +
   independent consumers but shifts processing-correctness to offset management. A topic =
   ordered partitions; offsets are per-partition positions, NOT global IDs; ordering is
   per-partition only.
1. **Storage: segments, indexes, retention** — a partition = closed segments + one active
   segment; sparse offset→position index; reads locate segment then scan sequentially.
   Segment boundaries make retention cheap (delete whole closed segments by time/size, not
   rewrite a monolith). Kafka `LocalLog`/`LogSegment`/`LogConfig`.
2. **Compaction: a second retention mode** — for keyed streams, key K at offset O is
   obsolete if a later O′ has K; cleaner builds key→last_offset and recopies segments,
   dropping obsolete records. Tombstones for deletes (with retention rules); active segment
   never cleaned. `LogCleaner`. Background, segment-based — not immediate.
3. **Replication: leader + ISR + high watermark** — one leader orders writes; followers
   fetch and append. ISR = dynamic commit set; HW = consumer-visible boundary (≤ leader LEO).
   `acks` (0/1/all) + `min.insync.replicas` = the durability contract. Defaults: acks=all,
   idempotence on, replica.lag.time.max=30s, unclean election off. ISR can shrink below
   majority — NOT plain majority quorum (→ contrast with 11/L).
4. **Failure repair: leader epochs** — offsets alone don't say which leader wrote which
   range. Leader epochs = a leadership-history coordinate system; followers find safe
   truncation points after reconnecting to a new leader. `LeaderEpochFileCache`. (Bridge:
   epochs ≈ Raft terms.)
5. **Consumer groups & offsets** — a group = logical reader; one partition → ≤1 member per
   group; groups consume independently. `__consumer_offsets` (compacted topic) stores
   offsets + metadata; group routes to coordinator by hash%50. Position (next fetch) ≠
   committed offset (restart checkpoint = process N then commit N+1). records-lag is
   fetch-position lag, not commit lag.
6. **Rebalancing — availability vs assignment correctness** — classic state machine
   (EMPTY…STABLE) + join/sync/heartbeat; client-side assignment. Eager (stop-the-world
   revoke-all) vs cooperative (revoke only moved partitions; multi-round). The modern
   `CONSUMER` protocol (KIP-848, server-side) exists but is early-access in 3.9 — "know it
   exists," not the default.
7. **Delivery semantics — scoped failure contracts** — at-most-once (commit before process),
   at-least-once (process then commit; duplicates), exactly-once-in-Kafka (idempotent
   producer + transactions + read_committed + transactional offset commits). EOS boundary =
   Kafka topics + offsets; EXTERNAL sinks still need idempotence/coordination.
8. **Idempotence & transactions — protocols on the log** — idempotent producer:
   (producerId, epoch, sequence); broker rejects dup/out-of-order; epochs fence zombies.
   Transactions: coordinator + `__transaction_state` state machine; control batches as
   commit/abort markers; aborted data stays in the log; LSO + abort index control
   read_committed visibility (read to LSO, skip aborted). → H.

## Paired build lab (/build → own-message-queue)
Append-only partition log (segments named by base offset) → sparse offset index → retention
cleaner (delete closed segments) → compaction cleaner (key→latest, recopy) → replicated
partition (leader append, follower fetch, HW advance) → ISR/min-ISR simulator (acks=all
purgatory, min-ISR rejection) → leader-epoch truncation lab → group coordinator toy (hash
shard, compacted offsets) → classic + cooperative rebalance → lag calculator (fetch vs
commit) → idempotent producer (pid/epoch/seq) → transaction coordinator + LSO/read-committed
toy → consume-transform-produce (atomic output + offsets).

## Diagrams needed
- The log: append-only partition + offsets; topic = N independent partitions (ordering scope).
- Segment layout (closed + active) + sparse index lookup; retention deleting a closed segment.
- Compaction: dirty section → key→last_offset → recopied segment (+ tombstone).
- Leader/followers + ISR + HW vs LEO; acks/min.insync.replicas durability contract.
- Leader-epoch truncation after failover (divergent logs → safe truncation point).
- Consumer group → partition assignment; coordinator routing by hash%50.
- Position vs committed offset timeline; eager vs cooperative rebalance.
- Transaction markers + LSO: read_committed vs read_uncommitted visibility.

## Sources / gaps to honor (from _research.md)
- **Opportunistic primary still OWED + BLOCKED:** Kafka paper (kafka.apache.org 000) + KIPs
  (98/101/500/848/360) — retry each session; if healed, save receipt + upgrade
  `[UNVERIFIED]`→VERIFIED, erase nothing.
- Pin Kafka source to a release tag/commit SHA before chapter prose (currently 3.9 paths).
  Trace before deep claims: KRaft PartitionChangeBuilder/ELR, fetch-from-follower/rack-aware,
  CoordinatorRuntime threading, sticky assignor/static membership, TransactionMarker retry +
  `__transaction_state` expiration, long-open-txn × compaction.
- Version caveats are LOAD-BEARING: 3.9-specific defaults, KRaft vs ZooKeeper, new consumer
  protocol = early access. Don't pretend Kafka is one unchanging system.
- Many deep gaps are intentionally scoped to appendix H — keep that boundary explicit.
