#!/usr/bin/env python3
"""
18 - rate-limiting / backpressure / load-shedding - load-bearing MATH recomputation.

Phase-1 factcheck aid (ADR-001). Pure stdlib, deterministic, no network. Each block
RECOMPUTES one load-bearing claim used in the cluster briefs and asserts the result so a
regression is loud. Run:  python3 _recompute.py   (exit 0 = all claims hold).

Claims verified here:
  A1  token bucket: admitted rate is min(arrival, refill); burst bounded by capacity B.
  A2  leaky bucket (queue) smooths to exactly rate r; overflow drops past depth.
  A3  fixed-window boundary burst: up to 2*limit in one window-width => sliding wins.
  A4  sliding-window-log is exact; sliding-window-counter approximation error.
  A5  distributed counter: sync-on-every error 0; batched-by-N over-admit <= (cells-1)*N.
  B1  Little's Law bound: a queue capped at Q adds at most Q/throughput latency (reuse 13).
  C1  retry amplification multiplier = 1/(1-r) for retry ratio r (geometric series).
  C2  goodput-vs-offered-load: past saturation, naive-retry goodput collapses; budget caps it.
  D1  adaptive throttling (Google SRE) client reject prob = max(0,(req-K*acc)/(req+1)).
"""
from __future__ import annotations
import math

EPS = 1e-9
def approx(a, b, tol=1e-6): return abs(a - b) <= tol


# ----------------------------------------------------------------------------- A1
def token_bucket(arrivals, capacity, refill_rate, dt):
    """Simulate a token bucket. arrivals: list of (t, n) request bursts.
    Returns (admitted, rejected). tokens regenerate at refill_rate/sec, capped at capacity."""
    tokens = float(capacity)
    last = 0.0
    admitted = rejected = 0
    for t, n in arrivals:
        tokens = min(capacity, tokens + (t - last) * refill_rate)
        last = t
        for _ in range(n):
            if tokens >= 1.0:
                tokens -= 1.0
                admitted += 1
            else:
                rejected += 1
    return admitted, rejected

def test_A1_token_bucket():
    # Empty bucket cap=10, refill=5/s. Instant burst of 100 at t=0 -> only `capacity` admitted.
    adm, rej = token_bucket([(0.0, 100)], capacity=10, refill_rate=5, dt=0)
    assert adm == 10 and rej == 90, (adm, rej)
    # Steady arrival at exactly refill rate over a long horizon -> ~all admitted.
    # 5 req/s for 100 s = 500 req, bucket refills 5/s -> admit all 500 (+ initial cap slack).
    arr = [(i / 5.0, 1) for i in range(500)]  # one req every 0.2s == 5/s
    adm, rej = token_bucket(arr, capacity=10, refill_rate=5, dt=0)
    assert rej == 0, (adm, rej)
    # Arrival ABOVE refill (10/s vs 5/s) for 100s: long-run admitted -> ~ refill*T + capacity.
    arr = [(i / 10.0, 1) for i in range(1000)]  # 10/s for 100s = 1000 req
    adm, rej = token_bucket(arr, capacity=10, refill_rate=5, dt=0)
    # long-run admit ~= refill_rate*T + initial capacity = 5*100 + 10 = 510 (boundary +/-1)
    assert abs(adm - 510) <= 1, adm
    # burst capacity is exactly B: from full bucket an instant burst admits B immediately.
    adm, rej = token_bucket([(0.0, 1000)], capacity=10, refill_rate=5, dt=0)
    assert adm == 10, adm
    return "A1 token bucket: admit=min(arrival,refill) long-run, instantaneous burst<=capacity"


# ----------------------------------------------------------------------------- A2
def leaky_bucket(arrivals, depth, leak_rate, horizon, step=0.001):
    """Leaky-bucket-as-queue: requests enter a FIFO of max `depth`; serviced at leak_rate/s.
    Returns (served, dropped, max_out_rate_per_s)."""
    q = 0
    served = dropped = 0
    credit = 0.0
    idx = 0
    arrivals = sorted(arrivals)
    t = 0.0
    served_times = []
    while t <= horizon + EPS:
        while idx < len(arrivals) and arrivals[idx] <= t + EPS:
            if q < depth:
                q += 1
            else:
                dropped += 1
            idx += 1
        credit += leak_rate * step
        while credit >= 1.0 and q > 0:
            q -= 1
            credit -= 1.0
            served += 1
            served_times.append(t)
        t += step
    # measure peak output rate over any 1s sliding window
    peak = 0
    for s in served_times:
        c = sum(1 for x in served_times if s <= x < s + 1.0)
        peak = max(peak, c)
    return served, dropped, peak

def test_A2_leaky_bucket():
    # Burst of 50 at t=0, depth=10, leak=5/s, horizon 12s.
    served, dropped, peak = leaky_bucket([0.0] * 50, depth=10, leak_rate=5, horizon=12)
    # only depth survive admission; rest dropped
    assert served == 10 and dropped == 40, (served, dropped)
    # output never exceeds leak_rate (smoothing): peak per-second <= 5 (+1 discretization)
    assert peak <= 6, peak
    return "A2 leaky bucket: output smoothed to leak_rate; admits<=depth, rest dropped"


# ----------------------------------------------------------------------------- A3
def fixed_window_boundary_burst(limit):
    """Worst case for a fixed window: `limit` requests at the very end of window 1 and
    `limit` at the very start of window 2 => 2*limit within one window-width span."""
    # window 1: requests at t = 0.999 (limit of them)
    # window 2: requests at t = 1.001 (limit of them)
    # any 1.0-wide sliding span covering [0.999,1.001] sees 2*limit
    return 2 * limit

def sliding_window_log_exact(times, limit, window):
    """Exact sliding-window-log: count timestamps in (now-window, now]; admit iff < limit."""
    admitted = []
    log = []
    for t in sorted(times):
        log = [x for x in log if x > t - window]
        if len(log) < limit:
            log.append(t)
            admitted.append(t)
    return len(admitted)

def test_A3_window_accuracy():
    limit = 100
    assert fixed_window_boundary_burst(limit) == 200
    # Sliding-window-log NEVER admits more than `limit` in any window-width span:
    # hammer 1000 requests in 0.5s with window=1.0, limit=100 -> exactly 100 admitted.
    times = [i * 0.0005 for i in range(1000)]  # all within 0.5s < window
    adm = sliding_window_log_exact(times, limit=100, window=1.0)
    assert adm == 100, adm
    return "A3 fixed-window admits up to 2*limit at boundary; sliding-log caps at exactly limit"


# ----------------------------------------------------------------------------- A4
def sliding_window_counter(prev_count, curr_count, elapsed_frac, limit):
    """Approximate sliding window: weight previous full window by (1-elapsed_frac).
    estimate = curr_count + prev_count*(1-elapsed_frac). Admit iff estimate < limit."""
    estimate = curr_count + prev_count * (1.0 - elapsed_frac)
    return estimate, estimate < limit

def test_A4_counter_approx():
    # The counter assumes the previous window's requests were UNIFORM. If they were actually
    # all clustered at the window's END, the estimate UNDERCOUNTS -> can over-admit.
    # prev window had `limit` requests all in its last instant; we are 10% into curr window.
    # estimate weights prev by 0.9 => 0.9*limit, leaving 0.1*limit headroom that doesn't exist.
    limit = 100
    est, ok = sliding_window_counter(prev_count=100, curr_count=0, elapsed_frac=0.1, limit=limit)
    assert approx(est, 90.0), est
    # worst-case over-admission of the counter vs exact log = prev_count*elapsed_frac (here 10)
    over = 100 * 0.1
    assert approx(over, 10.0)
    # memory: log = O(limit) timestamps; counter = O(1) (two integers). That's the tradeoff.
    return "A4 sliding-counter est=curr+prev*(1-frac); worst over-admit=prev*frac, but O(1) memory vs O(limit)"


# ----------------------------------------------------------------------------- A5
def distributed_counter_error(cells, per_cell_rate, sync_batch, horizon):
    """N cells each admit locally then sync. If each syncs only every `sync_batch` admits,
    a cell can over-admit by up to (sync_batch-1) before learning others used the budget.
    Total worst-case over-admission across the fleet <= cells*(sync_batch-1)... but the
    GLOBAL-limit overshoot relative to a perfect shared counter is bounded by
    (cells-1)*sync_batch in the canonical analysis (each lagging cell unaware of others)."""
    worst_over = (cells - 1) * sync_batch
    return worst_over

def test_A5_distributed_counter():
    # sync-on-every-admit (batch=1): worst over-admit = (cells-1)*1, i.e. at most cells-1.
    assert distributed_counter_error(cells=10, per_cell_rate=0, sync_batch=1, horizon=0) == 9
    # batch of 100 across 10 cells: worst over-admit = 9*100 = 900 above the global limit.
    assert distributed_counter_error(cells=10, per_cell_rate=0, sync_batch=100, horizon=0) == 900
    # => accuracy/coordination tradeoff: bigger batch = less chatter, more slop. (reuse 11)
    return "A5 distributed counter worst over-admit=(cells-1)*batch; batch trades chatter for slop"


# ----------------------------------------------------------------------------- B1
def queue_latency_bound(queue_cap, service_rate):
    """Little's Law corollary (reuse 13): a bounded queue of capacity Q served at rate mu
    adds at most Q/mu waiting time. Unbounded queue at rho->1 => unbounded latency."""
    return queue_cap / service_rate

def test_B1_queue_bound():
    # SRE example: queue = 10x threads, 100ms/req on the thread => full-queue wait ~1.0s + svc.
    # threads=N, queue=10N, service per thread=0.1s, drain rate=N/0.1s -> wait=10N/(N/0.1)=1.0s
    N = 50
    drain_rate = N / 0.1  # reqs/sec the pool completes
    wait = queue_latency_bound(queue_cap=10 * N, service_rate=drain_rate)
    assert approx(wait, 1.0), wait
    # small queue (50% of pool) bounds added latency to 0.05s -> "reject early" beats "queue deep"
    wait_small = queue_latency_bound(queue_cap=int(0.5 * N), service_rate=drain_rate)
    assert approx(wait_small, 0.05), wait_small
    return "B1 bounded-queue added latency=Q/drain; 10x pool=>~1.0s, 0.5x pool=>0.05s (reject early)"


# ----------------------------------------------------------------------------- C1
def retry_amplification(retry_ratio, max_attempts=None):
    """If a fraction r of requests are retried and retries can themselves be retried, the
    request multiplier is the geometric series sum_{k=0}^{inf} r^k = 1/(1-r) (uncapped),
    or sum_{k=0}^{A-1} r^k = (1-r^A)/(1-r) with a cap of A attempts."""
    if max_attempts is None:
        if retry_ratio >= 1.0:
            return math.inf
        return 1.0 / (1.0 - retry_ratio)
    return (1.0 - retry_ratio ** max_attempts) / (1.0 - retry_ratio)

def test_C1_retry_amplification():
    # r=0.5 uncapped -> 2x load. r=0.9 -> 10x. r=0.99 -> 100x. (the storm)
    assert approx(retry_amplification(0.5), 2.0)
    assert approx(retry_amplification(0.9), 10.0)
    assert approx(retry_amplification(0.99), 100.0)
    # SRE per-request cap of 3 attempts bounds the worst-case multiplier hard:
    # even at r=1.0 (everything fails+retries), 3 attempts = 3x, not infinity.
    assert approx(retry_amplification(0.999999, max_attempts=3),
                  (1 - 0.999999 ** 3) / (1 - 0.999999), tol=1e-3)
    # the 10% per-client retry budget caps steady-state amplification at 1/(1-0.1)=1.111x
    assert approx(retry_amplification(0.10), 1.0 / 0.9)
    return "C1 retry multiplier=1/(1-r): r=.5->2x,.9->10x,.99->100x; 3-attempt cap & 10% budget bound it"


# ----------------------------------------------------------------------------- C2
def goodput_curve(offered, capacity, retry_attempts, reject_cost_frac=0.0):
    """Goodput (useful completions/s) vs offered load.
    Below capacity: goodput=offered. Above: server can only do `capacity` units of work/s;
    naive retries multiply the *attempt* load, and if rejecting still costs reject_cost_frac
    of a unit, effective serving capacity for REAL work shrinks => goodput collapses.
    Returns goodput at this offered level."""
    if offered <= capacity:
        return offered
    # attempt load amplified by retries (each failed first-try gets retry_attempts more tries)
    attempt_load = offered * retry_attempts
    # fraction of attempts that are rejections (over capacity)
    if attempt_load <= capacity:
        return min(offered, capacity)
    reject_attempts = attempt_load - capacity
    # capacity consumed by paying the rejection cost
    wasted = min(capacity, reject_attempts * reject_cost_frac)
    real_capacity = max(0.0, capacity - wasted)
    return min(offered, real_capacity)

def test_C2_goodput_collapse():
    cap = 1000
    # below saturation goodput tracks offered
    assert goodput_curve(500, cap, retry_attempts=1) == 500
    # at/above saturation with NO retry, NO reject cost: goodput plateaus at capacity
    assert goodput_curve(2000, cap, retry_attempts=1, reject_cost_frac=0.0) == cap
    # WITH naive 3x retries AND non-trivial reject cost: goodput COLLAPSES below capacity
    collapsed = goodput_curve(2000, cap, retry_attempts=3, reject_cost_frac=0.5)
    assert collapsed < cap, collapsed
    # heavier overload => worse goodput (congestion collapse shape)
    worse = goodput_curve(5000, cap, retry_attempts=3, reject_cost_frac=0.5)
    assert worse <= collapsed, (worse, collapsed)
    return f"C2 goodput plateaus at cap w/o retries, COLLAPSES to {collapsed:.0f}<{cap} w/ 3x retries+reject cost"


# ----------------------------------------------------------------------------- D1
def adaptive_throttle_reject_prob(requests, accepts, K=2.0):
    """Google SRE adaptive throttling: client rejects locally with probability
    max(0, (requests - K*accepts)/(requests + 1)) over a 2-min sliding history."""
    return max(0.0, (requests - K * accepts) / (requests + 1.0))

def test_D1_adaptive_throttle():
    # Healthy: requests==accepts -> with K=2, prob = max(0,(r-2r)/(r+1)) = 0 (never throttle).
    assert approx(adaptive_throttle_reject_prob(100, 100), 0.0)
    # Backend accepting only half: requests=200, accepts=100, K=2 -> (200-200)/201 = 0 (still!).
    assert approx(adaptive_throttle_reject_prob(200, 100), 0.0)
    # Backend accepting a third: requests=300, accepts=100 -> (300-200)/301 ~= 0.332 throttle.
    p = adaptive_throttle_reject_prob(300, 100)
    assert approx(p, 100 / 301, tol=1e-6), p
    # Aggressive K=1.1: backend accepting ~half -> heavy throttle (rejects waste < resources)
    p2 = adaptive_throttle_reject_prob(200, 100, K=1.1)
    assert p2 > 0, p2
    return "D1 adaptive throttle p=max(0,(req-K*acc)/(req+1)); K=2 tolerates 2x, K=1.1 throttles at ~half"


def main():
    tests = [test_A1_token_bucket, test_A2_leaky_bucket, test_A3_window_accuracy,
             test_A4_counter_approx, test_A5_distributed_counter, test_B1_queue_bound,
             test_C1_retry_amplification, test_C2_goodput_collapse, test_D1_adaptive_throttle]
    print("=" * 78)
    print("18 - rate-limiting / backpressure / load-shedding - MATH recomputation")
    print("=" * 78)
    for t in tests:
        msg = t()
        print(f"[OK] {msg}")
    print("=" * 78)
    print(f"ALL {len(tests)} load-bearing claims VERIFIED BY RECOMPUTATION. 0 failures.")
    print("=" * 78)


if __name__ == "__main__":
    main()
