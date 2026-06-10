#!/usr/bin/env python3
"""17 async-queues + EDA — load-bearing math, verified by independent recomputation.
Pure stdlib. Run: python3 _recompute.py   (no deps, no network)

Anchors the numeric claims in the cluster briefs so none harden on vibes:
  1. delivery-semantics duplicate probability under at-least-once retry
  2. dedup-window sizing (how long must a dedup store remember a key?)
  3. batching throughput vs latency (Little's Law + per-batch fixed cost)
  4. retention sizing (bytes = rate * retention) and compaction floor
  5. consumer-group rebalance / partition-count parallelism ceiling
  6. outbox vs dual-write failure-window reasoning (probabilistic)
"""
import math

def section(t): print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)

# ---------------------------------------------------------------------------
section("1. DELIVERY SEMANTICS: duplicate probability under at-least-once")
# At-least-once = ack-after-process. If the ack is lost (prob p_ack_loss) after
# a successful process, the broker redelivers -> a duplicate. Over a stream of
# N messages each independently at risk, expected duplicates = N * p_ack_loss.
# Probability of >=1 duplicate in the stream = 1 - (1 - p)^N.
for p in (1e-3, 1e-4, 1e-6):
    for N in (1, 1_000, 1_000_000):
        exp_dups = N * p
        p_any = 1 - (1 - p) ** N
        print(f"  p_ack_loss={p:<7} N={N:>9}  E[dups]={exp_dups:>10.3f}  P(>=1 dup)={p_any:.4f}")
print("  => at-least-once makes duplicates a CERTAINTY at scale (E[dups]=N*p);")
print("     'effectively-once' must be built by the CONSUMER via idempotency/dedup,")
print("     not assumed from the broker. At p=1e-4, 1e6 msgs => ~100 dups expected.")

# ---------------------------------------------------------------------------
section("2. DEDUP-WINDOW SIZING: how long must the dedup store remember a key?")
# A dedup store rejects a key seen before. It only needs to remember a key for
# as long as a duplicate of it could still arrive = the maximum redelivery
# horizon = retry_backoff_ceiling * max_retries + in-flight/visibility timeout.
# Window must cover the WORST-CASE redelivery gap, else a late dup slips through.
def dedup_window_seconds(max_retries, base_backoff, backoff_cap, visibility_timeout):
    # exponential backoff capped, summed across retries, plus one visibility timeout
    total = 0.0
    for k in range(max_retries):
        total += min(base_backoff * (2 ** k), backoff_cap)
    return total + visibility_timeout
W = dedup_window_seconds(max_retries=8, base_backoff=1.0, backoff_cap=60.0, visibility_timeout=30.0)
print(f"  retries=8, base=1s, cap=60s, vis=30s  => dedup window must be >= {W:.0f}s ({W/60:.1f} min)")
# Storage cost of that window = unique keys/sec * window * bytes/key
for kps in (1_000, 50_000):
    for bpk in (16, 64):
        bytes_needed = kps * W * bpk
        print(f"    keys/s={kps:>6} bytes/key={bpk:>3}  store size ~ {bytes_needed/1e6:8.1f} MB for the window")
print("  => dedup is NOT free: window is bounded by redelivery horizon, and store")
print("     size = key_rate * window * bytes/key. Too-short window => silent dups.")

# ---------------------------------------------------------------------------
section("3. BATCHING: throughput vs latency tradeoff")
# Per-batch fixed cost c (syscall/RTT/fsync) amortizes over B messages.
# Effective per-msg cost = c/B + m (marginal per-msg work).
# Throughput = 1 / (c/B + m). Latency added by batching ~ B / arrival_rate (wait
# to fill) OR linger time, whichever caps first.
c = 1e-3   # 1 ms fixed cost per batch (e.g. one fsync / one RTT)
m = 5e-6   # 5 us marginal per message
print(f"  fixed cost c={c*1e3:.1f} ms/batch, marginal m={m*1e6:.1f} us/msg")
for B in (1, 10, 100, 1000, 10000):
    per_msg = c / B + m
    tput = 1 / per_msg
    print(f"    B={B:>6}  per-msg={per_msg*1e6:9.3f} us  throughput={tput/1e6:7.3f} M msg/s")
print("  => throughput is concave in batch size: huge gains 1->100, then the c/B")
print("     term vanishes and you asymptote at 1/m (here 200k... wait, 1/5e-6=200k? no:")
print("     1/m = 1/5e-6 = 200,000? recheck:")
print(f"     1/m = {1/m:,.0f} msg/s ceiling. Batching buys throughput, costs linger latency.")

# ---------------------------------------------------------------------------
section("4. RETENTION SIZING: disk = rate * retention; compaction floor")
# Time retention: bytes on disk per partition = write_rate(bytes/s) * retention(s).
def retention_bytes(msg_rate, avg_msg_bytes, retention_hours, replication=3):
    raw = msg_rate * avg_msg_bytes * retention_hours * 3600
    return raw, raw * replication
for rate, sz, hrs in ((100_000, 1024, 24), (1_000_000, 256, 72)):
    one, repl = retention_bytes(rate, sz, hrs)
    print(f"  rate={rate:>9}/s msg={sz:>5}B ret={hrs:>3}h  1-replica={one/1e12:7.3f} TB  x3={repl/1e12:7.3f} TB")
# Compaction floor: a compacted (keyed) log shrinks to one record per live key.
def compacted_floor(unique_keys, avg_record_bytes):
    return unique_keys * avg_record_bytes
for keys, rb in ((10_000_000, 200), (100_000_000, 64)):
    fl = compacted_floor(keys, rb)
    print(f"  compaction floor: {keys:>11} live keys * {rb}B = {fl/1e9:7.2f} GB (independent of write history)")
print("  => time retention grows with TRAFFIC; compaction floor grows with KEYSPACE.")
print("     Pick time-retention for event streams, compaction for changelog/CDC state.")

# ---------------------------------------------------------------------------
section("5. PARALLELISM CEILING: consumers per group <= partitions")
# In a log (Kafka-style), a partition is consumed by at most one consumer in a
# group => max useful consumers in a group = partition count. Extra consumers
# idle. Required partitions = ceil(target_throughput / per_consumer_throughput).
def required_partitions(target_tput, per_consumer_tput):
    return math.ceil(target_tput / per_consumer_tput)
for target, per in ((500_000, 20_000), (2_000_000, 50_000)):
    p = required_partitions(target, per)
    print(f"  target={target:>9}/s, per-consumer={per:>7}/s => need >= {p} partitions (and <= {p} useful consumers)")
print("  => partition count is the parallelism unit AND the ordering unit: you can")
print("     only have per-partition order, and only as many parallel consumers as partitions.")

# ---------------------------------------------------------------------------
section("6. OUTBOX vs DUAL-WRITE: the failure window")
# Dual write = write DB then publish to broker as two non-atomic ops. If the
# process crashes between them, you get an inconsistency (DB changed, no event,
# or event with no DB change). The window is the time between the two ops.
# Probability of a crash landing in the window over a long run:
# P(inconsistency per op) ~ window_seconds * crash_rate_per_second.
crash_mtbf_hours = 720  # crash every 30 days per instance
crash_rate = 1 / (crash_mtbf_hours * 3600)
for window_ms in (1, 10, 100):
    w = window_ms / 1000
    p_bad = w * crash_rate
    # over 1e9 operations:
    exp_bad = p_bad * 1e9
    print(f"  dual-write window={window_ms:>4}ms => P(bad/op)={p_bad:.2e}  E[bad over 1e9 ops]={exp_bad:8.3f}")
print("  => dual-write leaks at scale (nonzero E[bad]). The OUTBOX pattern removes the")
print("     window entirely: event is written in the SAME DB txn as the state change,")
print("     then a relay/CDC tails the outbox -> at-least-once delivery, ZERO dual-write gap.")
print("     Cost moves from 'lost/Phantom events' to 'duplicate events' (handled by #1/#2).")

print("\nALL RECOMPUTED. No external sources required for the math itself.")
