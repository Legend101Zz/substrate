# 16 — caching-and-cdn-strategies — Phase 1 factcheck (`_factcheck_phase1.md`)

> Method: load-bearing MATH verified by **independent recomputation** (pure Python 3, no deps).
> Mechanisms verified by **REUSE** of line-checked 03/06/08/10/13/14/15 with per-claim pointers.
> Canonical/vendor/RFC ATTRIBUTIONS network-blocked this session (HTTP 000 on every non-Lamport
> host, 8th consecutive session) → carried `[UNVERIFIED from fetched source]`. **0 blockers.**

Date: 2026-06-10 · Checkpoint at start: `c9f67ad` · `git status` clean at start.

---

## A. Network probe (this session)

`curl -s -o /dev/null -w '%{http_code}' --max-time 8` against:
- `raw.githubusercontent.com` → **000**
- `arxiv.org` → **000**
- `www.postgresql.org` → **000**
- `research.google` → **000**

Conclusion: identical to the prior 7 sessions; no carried-forward primary (15/14/13/12/11 OR 16's
own RFC 9111/5861, Nishtala NSDI 2013, Breslau INFOCOM 1999, VLDB-2015 XFetch) is fetchable.
Step-5 opportunistic upgrade is **impossible this session**; all `[UNVERIFIED]` flags preserved.

## B. Math verified by recomputation (Python, no deps)

All output reproduced exactly from a single script run this session.

### B1. Zipf hit ratio = H(k,α)/H(N,α), H(n,α)=Σ 1/i^α  — Cluster B §1.4

| N | α | top 1% | top 10% | top 20% | verdict |
|-----------|-----|--------|---------|---------|---------|
| 1,000 | 1.0 | 0.3913 | 0.6930 | 0.7853 | VERIFIED (exact) |
| 1,000,000 | 1.0 | 0.6800 | 0.8400 | 0.8882 | VERIFIED (exact) |

Lesson confirmed: small cache, big hit ratio (1% of keys → 68% hits at N=1e6) — caching works
because working set ≪ keyspace.

### B2. Skew sensitivity — cache top 1% of N=1e6 — Cluster B §1.5

| α | hit ratio | verdict |
|-----|-----------|---------|
| 0.8 | 0.3624 | VERIFIED |
| 1.0 | 0.6800 | VERIFIED |
| 1.2 | 0.9096 | VERIFIED |

Lesson: α dominates hit ratio; measure skew before promising a hit ratio.

### B3. Monotone working-set curve (N=1e6, α=1) — Cluster B §1.4

| cache fraction | hit ratio |
|----------------|-----------|
| 0.10% | 0.5201 |
| 1.00% | 0.6800 |
| 10.00% | 0.8400 |
| 50.00% | 0.9518 |
| 100.00% | 1.0000 |

monotone increasing: **True** (verified). Lesson: concave curve → diminishing returns → size to the
knee, not the keyspace. (50× memory, 1%→50%, only 0.68→0.95.)

### B4. Average latency & origin load — Cluster B §1.3

`t_avg = h·t_hit + (1−h)·t_miss`, origin fraction `= (1−h)`. (t_hit=1ms, t_miss=100ms illustrative.)

| h | t_avg (ms) | (1−h) |
|------|-----------|--------|
| 0.90 | 10.900 | 0.1000 |
| 0.95 | 5.950 | 0.0500 |
| 0.99 | 1.990 | 0.0100 |
| 0.999| 1.099 | 0.0010 |

VERIFIED. Lesson: 99→99.9% barely moves latency but cuts origin load 10× — sizing protects the
origin (13 tail), not the mean.

### B5. Stampede load multiplier — Cluster C §1.4

naive herd `≈ R·T_r` concurrent origin calls; coalescing → 1.

| R | T_r (s) | herd | verdict |
|--------|---------|------|---------|
| 1,000 | 0.05 | 50 | VERIFIED |
| 1,000 | 0.20 | 200 | VERIFIED |
| 10,000 | 0.05 | 500 | VERIFIED |
| 10,000 | 0.20 | 2,000 | VERIFIED |

Lesson: hottest + slowest keys stampede worst; the cache can *raise* peak origin load at expiry.

## C. Mechanisms verified by REUSE (line-checked earlier; not re-fetched)

| # | Claim (cluster) | Reused from | Verdict |
|---|-----------------|-------------|---------|
| R1 | Cache = bounded faster memory; TTL=logical-invalidity; cache-aside shape; stale-fill race (A,C) | 08 §§1.1–1.7 (Redis/Memcached/Caffeine line anchors) | VERIFIED (reuse) |
| R2 | LRU/LFU/2Q/ARC/TinyLFU/W-TinyLFU + admission-vs-eviction + slabs (B) | 08 §§1.3–1.5 | VERIFIED (reuse) |
| R3 | Leases / singleflight / stale-while-revalidate / stale-fill fixes (C) | 08 §1.6–1.7 (`singleflight.go`, RFC 5861/9111 mechanisms) | VERIFIED (reuse); RFC names flagged |
| R4 | In-process W-TinyLFU near cache = head/tail (A) | 08 §1.5 (Caffeine `PERCENT_MAIN`) | VERIFIED (reuse) |
| R5 | Reverse-proxy `proxy_cache` / event-driven PoP (A,D) | 10 NGINX `release-1.31.1` | VERIFIED (reuse) |
| R6 | Latency hierarchy / propagation floor / RTT-bound cross-region / read fan-out (A,B,D) | 13 `_research.md` + Cluster A fan-out (verified) | VERIFIED (reuse) |
| R7 | TCP 3-way + TLS 1.2/1.3 handshake RTTs; IP/BGP/DNS substrate (D) | 03 `_research.md` | VERIFIED (reuse) |
| R8 | Hot shards / celebrity keys / Zipf skew the cache absorbs (A,B,C) | 14 `_research.md` | VERIFIED (reuse) |
| R9 | Cache-as-replica staleness ladder (read-your-writes/monotonic/consistent-prefix) (C) | 15 Cluster B + 11 consistency models | VERIFIED (reuse) |
| R10 | Bloom filter for definite-absence (negative-cache pre-filter) (C) | 06 | VERIFIED (reuse) |

## D. Attributions flagged `[UNVERIFIED from fetched source]` (carried forward; HTTP 000)

- RFC 9111 (HTTP caching: `Cache-Control`/`s-maxage`/`Age`/`Vary`/validators/304/invalidation after
  unsafe methods) — carried from 08. Load-bearing for C §1.3 + D §1.7/§1.5.
- RFC 5861 (`stale-while-revalidate` / `stale-if-error`) — carried from 08.
- RFC 7234 (predecessor wording), RFC 4786 (anycast operations).
- Nishtala et al. "Scaling Memcache at Facebook" NSDI 2013 (cache-aside default, leases,
  17K→1.3K herd, cross-region delete stream) — carried from 08.
- Breslau et al. "Web Caching and Zipf-like Distributions" INFOCOM 1999 (empirical web α) — the Zipf
  *model + math* is recomputation-verified; real-world α values are NOT fetched.
- Vattani et al. "Optimal Probabilistic Cache Stampede Prevention" VLDB 2015 (XFetch formula) —
  teach intuition only; equation NOT written.
- Cormode & Muthukrishnan 2005 (Count-Min error bounds), ARC pseudo-code/patent — carried from 08.
- Vendor CDN architecture/purge/edge-compute (Cloudflare/Fastly/Akamai/CloudFront), anycast/BGP +
  DNS-steering specifics — patterns reasoned from 03; vendor APIs/routing behavior NOT fetched.
- RTT/propagation ms figures (D) — illustrative; not a fetched source.

## E. Verdict

- **0 blockers.** Every load-bearing number in 16 is verified by recomputation; every mechanism is
  verified by reuse of a previously line-checked source. The only open items are *attributions/exact
  wording* of canonical sources + RFCs + vendor specifics, all uniformly network-blocked and carried
  forward exactly as in 08/11–15.
- No first-draft numeric error survived: the Zipf hit-ratio tables, latency/origin tables, monotone
  curve, and stampede multiplier were all generated by the verification script, not hand-typed from
  memory.
- 16 is **honestly reconcilable** at the method/math level. The `[UNVERIFIED]` attributions are NOT
  load-bearing for the method and must NOT harden into Phase-2 prose until fetched.
