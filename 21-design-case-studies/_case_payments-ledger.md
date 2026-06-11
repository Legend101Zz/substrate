# 21 · Case study — Payments / ledger (idempotency, exactly-once-effect, strong consistency)

> Phase-1 brief (NO course prose). Bespoke walkthrough. Math RECOMPUTED in `_recompute.py`
> (Case 5). The correctness-over-throughput case: low QPS, zero tolerance for lost/double money.
> Uses idempotency (17), strong consistency (15), and 2PC/saga (11/14), and is the natural home
> for the freshly-verified CAP/PACELC primaries.

## 1. Requirements
- **Functional:** transfer money between accounts; record an immutable **double-entry ledger**
  (every transaction = balanced debit + credit); query balance + statement; refunds/reversals as
  new compensating entries (never edits).
- **Non-functional:** **strong consistency + correctness above all** — no lost writes, no double
  charges, balances never wrong; full **auditability** (append-only, every entry traceable);
  durability (committed = survives any single failure); availability is secondary to correctness
  (better to reject a payment than to double-charge).
- **Scale (RECOMPUTED, Case 5):** 10M txn/day -> **~116 txn QPS** (peak ~231) — *deliberately
  low*; 1 KB/record -> **~3.74 TB/yr** append-only. The challenge is correctness, not volume.

## 2. Data model + API
- **Model:** append-only `ledger_entries {entry_id, txn_id, account, direction(D/C), amount, ts}`
  with the invariant **sum(debits) == sum(credits)** per `txn_id`; `accounts {id, balance}` as a
  derived/materialized view (or computed from entries); `idempotency_keys {key -> txn_id, result}`.
- **API:** `POST /transfers {idempotency_key, from, to, amount} -> {txn_id, status}` (safe to
  retry with the same key); `GET /accounts/{id}/balance`; `GET /accounts/{id}/statement`.
- **Idempotency is mandatory:** the client sends an `idempotency_key`; the first request executes
  and stores `{key -> result}`; retries return the stored result without re-applying ->
  **exactly-once EFFECT** (reuse 17; transport is at-least-once, effect is once).

## 3. Bottleneck analysis
- **Not throughput — correctness under failure.** 116 QPS is trivial. The hard parts:
  1. **No double-apply** on retry (idempotency keys; dedup window >= max retry horizon = 24h,
     RECOMPUTED).
  2. **Atomic multi-account update** — debit and credit must both commit or neither
     (cross-account, possibly cross-shard -> 2PC or saga, reuse 11/14).
  3. **Strong read-after-write** — a balance read after a transfer must reflect it (no replica lag
     anomalies) -> synchronous quorum (reuse 15).

## 4. Design + cross-links to 13-20
- **13:** sizing shows this is a low-QPS / high-correctness regime — spend the complexity budget on
  consistency, not scale-out.
- **14:** accounts partitioned by `account_id`; a transfer between two accounts on different shards
  is a **cross-shard transaction** -> 2PC (strong, blocking) or **saga** (debit + credit as
  separate steps with idempotent compensation on failure) — the exact 14/17 cross-partition trade.
- **15 (CORE):** **synchronous replication + majority quorum** so committed money survives failover
  with no lost write; **W+R>N** (RECOMPUTED: N=3, W=2, R=2 -> 4>3, guaranteed overlap, strict `>`
  required; tolerates N-W=1 node failure). No read-your-writes anomalies allowed -> read at quorum
  / from leader. This is a **PC/EC** system in PACELC terms (below).
- **17:** idempotency + exactly-once-effect is the central pattern; the **outbox/CDC** pattern emits
  ledger events to downstream (analytics, notifications) without dual-write risk (reuse 17).
- **18:** rate-limit per account/API key (fraud/abuse); reject (don't queue) excess — for money,
  fail-closed.
- **19:** txn success/failure rate, commit latency, reconciliation mismatches = golden signals;
  audit log is the durable trace.
- **20:** on partition/failover, **choose Consistency over Availability** (reject rather than risk a
  double-spend) — the CAP/PACELC decision made concrete (see §7 primaries).
- **11:** 2PC/atomic commit, FLP (why a coordinator can block), consensus for the commit decision —
  all reused; a transfer's commit is a tiny consensus problem.

## 5. Failure modes (20)
- **Client retry / network double-send:** idempotency key -> apply once, return stored result.
- **Coordinator crash mid-2PC:** participants block holding locks (2PC's known weakness, 11) ->
  recovery/heuristic resolution, or prefer a **saga** (no global lock; compensate on failure) for
  availability — the classic strong-vs-available trade.
- **Partition during a transfer:** per CAP (Gilbert-Lynch, §7) you cannot have both C and A ->
  **forfeit A** (reject the transfer) to never violate the ledger invariant.
- **Partial saga (debit done, credit failed):** run the idempotent **compensating** debit-reversal
  (14/17 saga); the ledger stays balanced because reversals are new entries, not edits.
- **Replica lag on balance read:** read from leader/quorum, never a stale async replica (15).

## 6. Tradeoffs
- **2PC vs saga:** 2PC = strong atomicity but blocking + coordinator is a failure point + holds
  locks (lower availability); saga = non-blocking + available but only *eventual* atomicity and
  needs carefully designed idempotent compensations. Money systems lean 2PC/strong for the core
  ledger and sagas for orchestration across services.
- **Consistency vs availability (CAP, VERIFIED §7):** payments are **CP / PC** — during a partition
  they sacrifice availability to preserve consistency. Gilbert-Lynch: you provably cannot have both
  in a partitionable async system.
- **Latency vs consistency (PACELC, VERIFIED §7):** even with no partition (the **EL/EC** limb),
  payments pay **latency for consistency** (synchronous quorum commit) — they are **PC/EC**.
  Contrast Dynamo-style stores (PA/EL) used for the feed/cache cases.
- **Append-only ledger vs mutable balances:** append-only = perfect audit + easy reversal +
  recomputable balances, at the cost of storage growth + a materialized-balance view to read fast.

## 7. Sources / gaps
- **PRIMARIES VERIFIED this session** (`meta/fetched_primaries/`, receipt
  `_VERIFIED_2026-06-10_cap-pacelc.md`):
  - **Gilbert & Lynch, "Perspectives on the CAP Theorem" (2012)** — formal CAP: cannot guarantee
    both safety (consistency) and liveness (availability) in a partitionable async system; CAP ⇒
    cannot achieve consensus under partitions. Anchors the "forfeit A under partition" decision.
  - **Abadi, "Consistency Tradeoffs... (PACELC)" (2012)** — "if Partition: trade A vs C; **Else**:
    trade **Latency vs Consistency**." Payments = **PC/EC**; Dynamo-style = PA/EL. Anchors the
    no-partition latency cost of strong consistency.
- **REUSED (line-verified):** 11 (2PC/atomic commit, FLP, consensus, no exactly-once transport),
  13 (low-QPS/high-correctness sizing), 14 (account sharding, cross-shard txn, saga + compensation),
  15 (synchronous quorum W+R>N, no lag anomalies, failover without lost writes, CAP/PACELC made
  concrete), 17 (idempotency, exactly-once-effect, outbox/CDC, dedup window), 18 (fail-closed rate
  limiting), 19 (reconciliation signals/audit), 20 (choose C over A under partition).
- **RECOMPUTED:** txn QPS, storage/yr, W+R>N quorum, fault tolerance, idempotency-key retention.
- **`[UNVERIFIED]` carried:** Skeen 1981 3PC; Berenson 1995 ANSI isolation levels (11 gaps); Sagas
  SIGMOD 1987 (14 gap); specific payment-system designs (Stripe/Square ledger talks) not fetched.
