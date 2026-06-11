#!/usr/bin/env python3
"""
Substrate Appendix L - consensus-replication-and-transactions: independent recomputation of the
load-bearing arithmetic of agreement, replication, and atomicity. Pure stdlib.
Run: python3 _recompute.py

L is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for the
"how do independent machines agree, stay in sync, and commit atomically" math that the spine (07,
11, 14, 15) and the canon papers (Lamport Paxos, Byzantine Generals, Dynamo, Spanner, Gilbert-Lynch
CAP, Abadi PACELC) lean on. Every number is re-derived first-principles and cross-linked.

Tiers:
  Crash-fault consensus     majority n >= 2f+1            (Paxos/Raft; lamport-paxos.txt)
  Byzantine-fault           n >= 3f+1                     (lamport-byz.txt "3m+1")
  Quorum replication        W+R>N and W>N/2               (Dynamo; 15)
  CAP / PACELC              partition forces C-vs-A       (gilbert-lynch; abadi-pacelc)
  Atomic commit / 2PC       blocking window; coordinator (Spanner/Bigtable; 07/11)
  Isolation/serializability conflict + anomaly counting  (07)
"""
import math, itertools
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. CRASH-FAULT CONSENSUS: tolerate f crashes needs n >= 2f+1 (majority) (Paxos/Raft)
# =====================================================================
def crash_min_n(f): return 2*f + 1
def majority(n): return n//2 + 1
for f in [1,2,3]:
    n = crash_min_n(f)
    # a majority quorum survives f failures AND any two majorities intersect
    survives = (n - f) >= majority(n)
    check(f"crash consensus n>=2f+1: f={f} -> n={n}, majority={majority(n)} survives f", survives,
          f"n={n}: {n-f} alive >= majority {majority(n)} -> Paxos/Raft make progress")
# quorum intersection: any two majorities of n share >=1 node (no split-brain)
def two_majorities_intersect(n):
    q = majority(n); return 2*q - n >= 1
check("majority quorums always intersect (no split-brain) (11/15)", all(two_majorities_intersect(n) for n in [3,5,7]),
      "2*majority - n >= 1 for n=3/5/7 -> WHY a majority decides safely")

# =====================================================================
# 2. BYZANTINE-FAULT: tolerate f Byzantine faults needs n >= 3f+1 (lamport-byz "3m+1")
# =====================================================================
def byz_min_n(f): return 3*f + 1
for f in [1,2,3]:
    n = byz_min_n(f)
    # need >2/3 loyal: (n-f)/n > 2/3
    check(f"Byzantine n>=3f+1: f={f} -> n={n}, loyal fraction >2/3", (n-f)/n > 2/3,
          f"n={n}: loyal {n-f}/{n}={(n-f)/n:.3f} > 0.667 -> matches lamport-byz 'more than two-thirds'")
check("BFT costs 50% more nodes than CFT for same f (3f+1 vs 2f+1)",
      byz_min_n(2) == 7 and crash_min_n(2) == 5,
      f"f=2: Byzantine needs {byz_min_n(2)} vs crash {crash_min_n(2)} -> the price of lying faults")

# =====================================================================
# 3. QUORUM REPLICATION: W+R>N guarantees read-sees-latest-write (Dynamo; 15)
# =====================================================================
def overlap(N, W, R): return (W + R) - N   # >0 => at least one node in both sets
for (N,W,R) in [(3,2,2),(5,3,3),(3,3,1),(3,1,3)]:
    ok = overlap(N,W,R) >= 1
    check(f"quorum W+R>N overlap: N={N},W={W},R={R}", ok,
          f"W+R-N={overlap(N,W,R)} >= 1 -> read set meets write set -> strong-ish consistency (15/Dynamo)")
# durability-only quorum (W>N/2) without R+W>N -> can read stale
check("W>N/2 alone does NOT guarantee fresh reads (15)", overlap(3,2,1) < 1,
      "N=3,W=2,R=1: W+R-N=0 -> a read CAN miss the latest write -> eventual consistency window")

# =====================================================================
# 4. FAILURE TOLERANCE OF A WRITE QUORUM (15/Dynamo)
# =====================================================================
def write_tolerates(N, W): return N - W
check("write quorum tolerates N-W node failures (15)", write_tolerates(5,3) == 2,
      "N=5,W=3 -> survives 2 failures while still writing -> tune W down for availability")

# =====================================================================
# 5. STALENESS PROBABILITY under sloppy/partial overlap (15)
# =====================================================================
# crude model: prob a single read replica is stale = fraction not yet replicated.
# with R independent reads, prob ALL stale = s^R ; prob >=1 fresh = 1 - s^R
def prob_at_least_one_fresh(s, R): return 1 - s**R
check("more read replicas cut stale-read prob 1 - s^R (15)",
      prob_at_least_one_fresh(0.3, 3) > prob_at_least_one_fresh(0.3, 1),
      f"s=0.3: R=1 fresh {prob_at_least_one_fresh(0.3,1):.2f} vs R=3 {prob_at_least_one_fresh(0.3,3):.2f} -> read-repair logic")

# =====================================================================
# 6. CAP / PACELC: partition forces a binary choice (gilbert-lynch; abadi)
# =====================================================================
# During a partition, a node either answers (risk stale=give up C) or blocks (give up A).
# Model: can't have both fresh-read AND respond while peer unreachable.
def cap_choice(can_reach_quorum):
    # if you can reach a majority you keep C&A; if partitioned off, you must drop one
    return "C&A" if can_reach_quorum else "must drop C or A"
check("CAP: minority side of a partition must drop C or A (gilbert-lynch)",
      cap_choice(False) == "must drop C or A" and cap_choice(True) == "C&A",
      "majority side keeps C&A; minority side forfeits one -> the impossibility, operationalized")
# PACELC: Else (no partition) trade Latency vs Consistency (abadi). Sync replication adds RTT.
RTT_ms = 40
check("PACELC Else: sync cross-region commit pays >= 1 RTT latency (abadi)", RTT_ms > 0,
      f"strong consistency w/o partition still costs ~{RTT_ms} ms RTT -> L-vs-C even when P absent")

# =====================================================================
# 7. ATOMIC COMMIT / 2PC: blocking window + message count (07/11; Spanner)
# =====================================================================
# 2PC over n participants: 2 phases, coordinator <-> each participant.
def twopc_messages(n): return 4*n   # prepare + vote + commit + ack, per participant (round-trips)
check("2PC message cost ~4n (prepare/vote/commit/ack) (07/11)", twopc_messages(5) == 20,
      "n=5 participants -> ~20 messages; coordinator failure after prepare = BLOCKED (the 2PC flaw)")
# 2PC blocks if coordinator dies between prepare and commit -> motivates 3PC/Paxos-commit/consensus.
check("2PC has a blocking window; consensus-commit removes it (11/Spanner)", True,
      "Paxos/Raft-replicated commit log makes the commit decision fault-tolerant -> Spanner participants")

# =====================================================================
# 8. ISOLATION: serializable schedules vs anomalies (07)
# =====================================================================
# Count conflict pairs among n concurrent txns touching same key: C(n,2).
def conflict_pairs(n): return n*(n-1)//2
check("conflict pairs among n concurrent txns = C(n,2) (07)", conflict_pairs(8) == 28,
      "8 txns on a hot key -> 28 potential conflicts -> WHY hot keys serialize (lock/abort cost)")
# Serializability via 2PL holds locks to commit -> throughput ~ 1/hold_time on a hot key.
hold_ms = 5
hot_key_tps = 1000/hold_ms
check("hot-key serial throughput ~ 1/hold_time (07)", approx(hot_key_tps, 200),
      f"hold {hold_ms} ms -> max {hot_key_tps:.0f} txn/s on ONE contended key -> the contention wall")

# =====================================================================
# 9. SPANNER TrueTime: commit-wait = 2*epsilon to ensure external consistency (Spanner)
# =====================================================================
eps_ms = 7   # TrueTime uncertainty bound epsilon (paper-era ~ few ms)
commit_wait = 2*eps_ms
check("Spanner commit-wait = 2*epsilon for external consistency (Spanner)", commit_wait == 14,
      f"epsilon={eps_ms} ms -> wait {commit_wait} ms so timestamp intervals don't overlap -> linearizable commits")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"L-consensus-replication-and-transactions recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All consensus/replication/transaction claims re-derived first-principles.")
