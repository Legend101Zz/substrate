# 13 scaling-fundamentals — Factcheck: Cluster A (back-of-envelope / latency / queueing)

Method note: this cluster is **theorem-grade math + flagged empirical numbers**. The math is
verified by **independent recomputation** (Python, this session) and by reproducing the
standard derivations, not by fetching a secondary source — that is the correct verification
mode for closed-form results. Every empirical/historical claim that would need a primary is
explicitly flagged, not asserted.

**Network reality (4th consecutive session):** only `lamport.azurewebsites.net` + Walmart
artifactory resolve. Dean latency table, Drepper, jboner gist, Little 1961, Kleinrock,
Amdahl 1967, Gunther USL = **HTTP 000**. Verified by direct `curl` this session.

## VERIFIED (recomputed this session — 0 blockers)

| # | Claim | Check | Verdict |
|---|-------|-------|---------|
| 1 | Little's Law `L = λW`, distribution-free | Area/accounting derivation reproduced (§1.1) | VERIFIED (derivation) |
| 2 | Concurrency = throughput × latency (Little form) | Dimensional identity of #1 | VERIFIED |
| 3 | M/M/1 `L = ρ/(1−ρ)`; at ρ=0.8 ⇒ 4 | Python: `0.8/0.2 = 4.0` | VERIFIED |
| 4 | Utilization wall `W/S = 1/(1−ρ)` | Python: ρ=.5→2×, .8→5×, .9→10×, .95→20×, .99→100× | VERIFIED (exact) |
| 5 | Amdahl ceiling `1/(1−p)`; p=0.95 ⇒ 20× | Python: `1/0.05 = 20` | VERIFIED |
| 6 | USL `C(N)=N/(1+α(N−1)+βN(N−1))`, knee `N*=√((1−α)/β)` | Form reduces to Amdahl at β=0; knee from `dC/dN=0`; sample α=.03,β=1e-4 ⇒ N*≈98.5 | VERIFIED (derivation + sample) |
| 7 | Fan-out tail `1−(1−q)^N`; q=.01,N=100 ⇒ ~63% | Python: `0.99^100=0.3660`, `1−=0.6340` | VERIFIED (exact) |

## VERIFIED BY REUSE (already line-checked in prior sub-courses — not re-fetched)

| # | Claim | Source already verified in | Verdict |
|---|-------|----------------------------|---------|
| 8 | Memory hierarchy / SRAM-vs-DRAM / "why a hierarchy" / memory mountain | 01 `_research_eater-csapp.md` §J (CS:APP ch.6) | VERIFIED (reuse) |
| 9 | 64-byte cache line; false sharing; cache-local layout | 06 Disruptor + RocksDB `bloom_impl.h` briefs | VERIFIED (reuse) |

## FLAGGED — `[UNVERIFIED from fetched source]` (network-blocked, carried forward)

| # | Claim | Why flagged |
|---|-------|-------------|
| F1 | Exact Dean latency numbers (L1≈0.5ns, mem≈100ns, disk seek≈ms, DC/cross-continent RTT) | Every host HTTP 000; only orders-of-magnitude/ordering taught, all exact ns/ms marked UNVERIFIED |
| F2 | Drepper memory-access measurements | akkadia/LWN/mirrors HTTP 000 |
| F3 | Historical attributions: Little 1961, Kleinrock M/M/1·M/G/1, Amdahl 1967, Gunther USL, Pollaczek–Khinchine | Primaries HTTP 000; the *math* is verified by derivation, the *citations* are not |
| F4 | "The Tail at Scale" (Dean & Barroso CACM 2013) as the source of the fan-out argument | Also tracked unverified in 12 canon; the arithmetic (claim #7) is self-contained and verified |

## Warnings / precision notes (no blockers)
- W1: P-K (M/G/1) variance formula `Wq = ρS(1+C²ₛ)/(2(1−ρ))` is stated from standard
  queueing theory; flagged because Kleinrock/Pollaczek primaries are unfetched. Not load-bearing.
- W2: Amdahl vs. Gustafson tension is noted as an open question, not asserted as resolved.
- W3: Do NOT let any exact latency number harden into Phase-2 prose until F1/F2 are fetched.

**Blockers: 0.** Cluster A's load-bearing content (the capacity *method/math*) is fully
verified. The empirical *numbers* are honestly deferred — which is exactly why 13 stays a
clean cluster checkpoint and is NOT reconciled this session.
