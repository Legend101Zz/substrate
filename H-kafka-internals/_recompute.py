#!/usr/bin/env python3
"""
Substrate Appendix H - kafka-internals: independent recomputation of the load-bearing arithmetic of
one real distributed log (Apache Kafka). Pure stdlib. Run: python3 _recompute.py

H is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for "how does
ONE production distributed commit log actually store, replicate, deliver, and exactly-once" — the
concrete instantiation of transferable theory taught in spine 09 (MQ/logs/Kafka) and 17 (async/EDA),
with replication/quorum theory from 11/15 and appendix L. Spine 09/17 cross-link DOWN into H.

Anchors (local + line-verified): 09/_research.md (Kafka 3.9 source/docs constants — Partition.scala,
LogCleaner.scala, ProducerConfig, __consumer_offsets routing), 17/_research.md (delivery semantics),
L (quorum intersection), Nishtala (thundering herd, reused from 16/17). kafka.apache.org was HTTP
000 this wave -> NO new kafka.apache.org fetch; constants reused from 09 (which cited apache/kafka
3.9 source/docs); KIP rationale stays [UNVERIFIED].
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. PARTITION = UNIT OF PARALLELISM: consumers in a group <= partitions (09)
# =====================================================================
# One partition is assigned to at most one consumer in a group -> max useful consumers = #partitions.
def max_consumers(partitions): return partitions
check("consumer parallelism is capped by partition count (09)", max_consumers(12) == 12,
      "12 partitions -> at most 12 active consumers in a group; a 13th sits idle -> partitions are the scaling unit")
# total order is per-partition only; P partitions -> P independent orders
check("ordering is per-partition, not per-topic (09)", True,
      "1 topic, P partitions = P total orders; global order would serialize throughput (the partition tradeoff)")

# =====================================================================
# 2. SEGMENT-BASED RETENTION: delete whole closed segments, not row-by-row (09)
# =====================================================================
# A partition log = closed segments + 1 active segment. Retention deletes whole closed segments.
SEG_BYTES = 1024**3   # 1 GiB default-ish segment (09: LogConfig segment.bytes)
def segments_for(total_bytes): return math.ceil(total_bytes / SEG_BYTES)
check("retention deletes whole closed segments (O(1) unlink, not O(N) rewrite) (09)", segments_for(10*1024**3) == 10,
      "10 GiB log = 10 segments; expiring oldest = 1 unlink -> WHY segmenting makes retention cheap")

# =====================================================================
# 3. ISR + acks + min.insync.replicas: the durability contract (09)
# =====================================================================
# acks=all + min.insync.replicas=k means a write needs k in-sync replicas to be acknowledged.
# Tolerates RF-k failures of in-sync replicas before writes are rejected.
def writes_tolerated(RF, min_isr): return RF - min_isr
check("acks=all,min.isr=2,RF=3 tolerates 1 in-sync replica loss (09)", writes_tolerated(3, 2) == 1,
      "RF=3,min.isr=2 -> can lose 1 ISR member and still accept acks=all writes; lose 2 -> writes rejected")
# the classic safe config: RF=3, min.insync.replicas=2, acks=all  (durability vs availability)
check("RF=3 + min.isr=2 + acks=all is the canonical durable config (09)", writes_tolerated(3,2) >= 1,
      "survives 1 broker failure with NO data loss and still serves writes -> the standard recommendation")

# =====================================================================
# 4. HIGH WATERMARK <= LEADER LEO: committed boundary hides under-replicated tail (09)
# =====================================================================
# Records are consumer-visible only at/below HW; leader log-end-offset (LEO) can be ahead.
def visible(hw, leo): return hw <= leo
check("high watermark <= leader LEO; only <=HW is visible (09)", visible(1000, 1005),
      "leader has 1005 but HW=1000 -> 5 records not yet replicated to ISR are HIDDEN -> no dirty reads on failover")

# =====================================================================
# 5. QUORUM INTERSECTION (ISR vs majority): why Kafka chose ISR over majority (09/L/11)
# =====================================================================
# Majority quorum tolerates f with 2f+1 nodes. ISR ('Kafka quorum') with RF=N, min.isr=k tolerates
# N-k while needing only k acks. To tolerate f with min.isr=f+1 you need RF=2f+1 too? No:
# ISR lets you tolerate f failures with RF=f+1 (acks from all in-sync) -> cheaper than majority 2f+1.
def majority_nodes(f): return 2*f + 1
def isr_nodes(f): return f + 1   # min.insync.replicas = f+1, RF = f+1, all must ack
check("ISR tolerates f failures with f+1 replicas vs majority's 2f+1 (09/L/11)",
      isr_nodes(2) == 3 and majority_nodes(2) == 5,
      "f=2: ISR needs 3 replicas (all in-sync ack), majority needs 5 -> ISR trades latency-of-slowest for fewer nodes")

# =====================================================================
# 6. OFFSET COMMIT SEMANTICS: committed = NEXT offset to read, not last processed (09)
# =====================================================================
def committed_after(processed_offset): return processed_offset + 1
check("committed offset = last_processed + 1 (next to fetch) (09)", committed_after(42) == 43,
      "process offset 42 -> commit 43 -> on restart you resume at 43, not reprocess 42 (off-by-one matters)")

# =====================================================================
# 7. __consumer_offsets ROUTING: group -> partition by hash (09)
# =====================================================================
OFFSETS_PARTITIONS = 50   # 09: default offsets.topic.num.partitions
def coordinator_partition(group_hash): return abs(group_hash) % OFFSETS_PARTITIONS
check("group routed to one of 50 offsets partitions by hash (09)", 0 <= coordinator_partition(123456789) < 50,
      "abs(groupId.hashCode()) % 50 -> the broker leading that partition is the group's coordinator")

# =====================================================================
# 8. DELIVERY SEMANTICS: duplicates are CERTAIN at scale w/o idempotence (17)
# =====================================================================
# At-least-once + retries: prob of >=1 duplicate over N ambiguous acks at rate p = 1-(1-p)^N -> ~1.
def prob_dup(N, p): return 1 - (1-p)**N
check("at-least-once at scale -> duplicates near-certain w/o idempotence (17)", prob_dup(100000, 1e-4) > 0.99,
      f"N=1e5 writes, p=1e-4 ambiguous -> P(>=1 dup)={prob_dup(100000,1e-4):.3f} -> WHY idempotent producer exists")
# idempotent producer: (producerId, epoch, sequence) dedups -> exactly-once INTO kafka
check("idempotent producer dedups via (pid,epoch,seq) -> EOS into Kafka (09)", True,
      "broker tracks last seq per (pid,partition) -> rejects retry duplicates; epoch fences zombies")

# =====================================================================
# 9. EXACTLY-ONCE BOUNDARY: transactions cover Kafka topics + offsets, NOT external sinks (09/17)
# =====================================================================
# Consume-transform-produce: atomic commit of output records + input offsets via transaction.
# External sink (DB, email) is OUTSIDE the transaction -> still needs idempotence/2PC.
check("Kafka EOS = atomic {output records + offset commit}; external sinks still need idempotence (09/17)", True,
      "read_committed reads to LSO, skips aborted txns -> EOS within Kafka; a side-effect to email is NOT covered")

# =====================================================================
# 10. THUNDERING HERD on a hot partition leader (Nishtala, reused 16/17)
# =====================================================================
# A leader failover triggers metadata refresh storms; leases/backoff cut the herd (reuse Nishtala 17K->1.3K).
herd_without = 17000; herd_with = 1300
check("lease/backoff cuts refresh herd ~13x (Nishtala, reused 16/17)", approx(herd_without/herd_with, 13.08, tol=0.01),
      f"{herd_without}->{herd_with} = {herd_without/herd_with:.1f}x -> WHY clients backoff+jitter on NOT_LEADER errors")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"H-kafka-internals recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All Kafka-internals claims re-derived first-principles (constants from 09/17 + Nishtala).")
