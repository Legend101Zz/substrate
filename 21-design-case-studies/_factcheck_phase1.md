# 21 · Phase-1 factcheck — design-case-studies

> Method: 21 is the CAPSTONE of Part II — it introduces NO new primitives, so every claim is
> either (a) a back-of-envelope estimate RECOMPUTED in `_recompute.py` (32/32 pass), (b) a
> mechanism REUSED from a previously line-verified sub-course (06/09/11/12/13-20), (c) VERIFIED
> verbatim against a primary fetched to `meta/fetched_primaries/`, or (d) flagged `[UNVERIFIED]`
> and carried forward (must not harden into Phase-2 prose). 0 blockers. No fake completeness.

## Bespoke structure note
Per the next-session plan + ADR-001 spirit: 21 is an APPLICATION course, so its briefs are
per-case-study walkthroughs (`_case_*.md`), NOT abstract source clusters. The reconciliation
(`_research.md`) adds a cross-cutting "design method" spine + consolidated sources/gaps. This is a
deliberate, plan-sanctioned departure from the four-cluster shape used in 13-20.

## Primaries fetched + verified THIS session (network heal, Wave 10)
| source | file | what it anchors |
|--------|------|-----------------|
| Gilbert & Lynch, "Perspectives on the CAP Theorem" (2012) | `gilbert-lynch-2002.{pdf,txt}` | Case 5 payments: formal CAP — can't have both safety(C) + liveness(A) under partition; CAP ⇒ no consensus under partition |
| Abadi, PACELC (2012) | `abadi-pacelc-2012.{pdf,txt}` | Case 5: PC/EC vs PA/EL; the **Else-Latency** limb (strong consistency costs latency even with no partition) |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_cap-pacelc.md`. These ALSO upgrade
carry-forward `[UNVERIFIED]` in 11 (formal CAP) and 15 (PACELC) — applied separately.

## Case 1 — URL shortener
- RECOMPUTED: write 1,157 QPS, read 115,741 QPS (100:1), base62^6=56.8B, base62^7=3.52e12, 5-yr
  records 1.825e11 = 5.2% of 62^7 (62^6 overflows 3.2x), 91.25 TB storage, 5 GB hot cache, origin
  read 11,574 QPS at 90% hit. All PASS.
- REUSED: 13/14/15/16/17/18/19/20/06 (see brief §7). Write-once -> trivial consistency (15);
  origin-load=(1-h) (16). All mechanisms line-verified in their home sub-courses.
- `[UNVERIFIED]`: "KGS" key-gen service is a community idiom (no single primary); flagged as idiom,
  grounded in 11/14.

## Case 2 — News feed / timeline
- RECOMPUTED: feed read 34,722 QPS, post 347 QPS, fan-out-on-write 69,444/s (200x), celebrity 1e8
  single-post fan-out, push/pull cost comparison. All PASS.
- REUSED: 13 (write-amplification), 14 (celebrity = hot key), 15 (eventual + read-your-writes),
  16 (timeline cache), 17 (async fan-out, idempotent append), 18 (fan-out backpressure), 19/20.
- `[UNVERIFIED]`: push/pull/hybrid feed is a community idiom (Twitter/IG eng blogs); mechanisms
  grounded in 14/16/17. No vendor follower-distribution numbers fetched.

## Case 3 — Chat / messaging
- RECOMPUTED: 23,148 msg QPS, 73 TB/yr, 1,000 gateway nodes (50M/50k), 500-member group fan-out.
  All PASS.
- REUSED: 11 (ordering/sequencer, FLP/2-generals -> no exactly-once transport), 13 (connection
  sizing), 14 (conversation partition, hot channel), 15 (single-leader-per-partition order), 16,
  17 (at-least-once+dedup = exactly-once-effect, cursor, replay), 18 (presence shed), 19/20.
- `[UNVERIFIED]`: websocket/XMPP/MQTT specifics + vendor chat designs not fetched; grounded in
  11/17.

## Case 4 — Web search / typeahead
- RECOMPUTED: typeahead 23,148 QPS (20x search), 100 index shards (50B/500M), scatter-gather tail
  N=10 -> 9.6%, N=50 -> 39.5%, N=100 -> 63.4% (= the line-verified 13/20 fan-out identity). All PASS.
- REUSED: 06/12 (inverted index), 13 (fan-out tail), 14 (document-partition sharding), 15 (read
  replicas/eventual index), 16 (query+prefix cache), 17 (async indexing), 18, 19 (trace the
  straggler), 20 (hedged/tied requests + partial results — the tail-at-scale core, line-verified).
- `[UNVERIFIED]`: Google/Lucene/Elasticsearch internals + BM25 mechanics not fetched (Appendix-P
  candidate); grounded in 06/13/20.

## Case 5 — Payments / ledger
- RECOMPUTED: 116 txn QPS, 3.74 TB/yr, W+R>N (2+2=4>3 strict), N-W=1 fault tolerance, idempotency
  retention 86400s. All PASS.
- VERIFIED (primaries this session): Gilbert-Lynch formal CAP (forfeit A under partition) + Abadi
  PACELC (payments = PC/EC; strong consistency costs latency on the EL limb). See receipt.
- REUSED: 11 (2PC/atomic commit, FLP, consensus, no exactly-once transport), 13, 14 (cross-shard
  txn + saga/compensation), 15 (sync quorum W+R>N, no lag anomalies, failover w/o lost writes), 17
  (idempotency + exactly-once-effect + outbox/CDC), 18 (fail-closed), 19/20 (choose C over A).
- `[UNVERIFIED]` carried: Skeen 1981 3PC, Berenson 1995 ANSI isolation (11 gaps), Sagas SIGMOD 1987
  (14 gap), vendor payment designs (Stripe/Square) not fetched.

## Case 6 — Distributed rate limiter
- RECOMPUTED: 1M checks/s, token-bucket steady rate r, distributed over-admit (M-1)*B = 35 (M=8,
  B=5), 64 MB counter store. All PASS.
- REUSED: 18 (CORE — token/leaky bucket, windows, over-admit (M-1)*B, 429+Retry-After,
  fail-open/closed — all line-verified + recomputed in 18), 06 (consistent-hash counter sharding),
  13/14/15 (PA/EL counters)/16/17/19/20, 11 (no global clock -> per-node refill).
- `[UNVERIFIED]` carried: GCRA + Stripe/Cloudflare limiter posts not fetched (from 18); RFC 6585 §4
  (429) already VERIFIED in 18.

## Carry-forward still-blocked primaries (retried this session)
- CoDel — `queue.acm.org` HTTP **403** (covered via 18+SEDA; not load-bearing for 21).
- `raft.github.io/raft.pdf` HTTP **000** (Raft covered via Lamport primaries in 11/12).
- `dl.acm.org` DOI landing HTTP **403** (used alternate mirrors for CAP/PACELC successfully).
- NEWLY 200 but not yet deep-fetched this session (time-boxed): arxiv.org, kafka.apache.org,
  postgresql.org — noted for next session's opportunistic pass.

## Verdict
21 coverage is honest and capstone-appropriate: it APPLIES the 13-20 toolkit to six concrete
designs, every back-of-envelope estimate is RECOMPUTED (32/32), every mechanism is REUSED from a
line-verified home sub-course, and the one genuinely new primary need (CAP/PACELC for payments) was
FETCHED + VERIFIED this session. Residual `[UNVERIFIED]` items are community design idioms + vendor
eng-blog specifics + already-carried canon gaps — none load-bearing for the sizing/mechanism core.
Reconcile into `_research.md`. Part II (13-21) is COMPLETE.
