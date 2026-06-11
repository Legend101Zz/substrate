# Appendix O · cloud-infra-basics — factcheck (Phase 1)

> Reference appendix (deep info only, NO exercises — CONSTITUTION #5). O is a **cloud-primitives
> reference map**: it deliberately makes **no vendor-specific claim load-bearing.** Every mechanism /
> number that matters is reused from **line-verified spine math + appendices** (13, 20, 15, and
> appendices I, J, L) — never from cloud-vendor documentation (all unreachable). Vendor names/numbers
> (S3 "11 nines," EBS tiers, Lambda limits, AZ counts, prices) appear ONLY as `[UNVERIFIED]`
> illustrations of a vendor-neutral primitive. **NO new primary fetched this wave** — aws.amazon.com /
> cloud.google.com / Azure docs HTTP **000** (consistent with the wave's network state). Every
> quantitative claim is re-derived in `_recompute.py` (14/14). Blockers: **0**.

## Claim ledger

| # | Claim | Status | Source / basis |
|---|-------|--------|----------------|
| 1 | Compute ladder VM → container → function rents progressively thinner slices of the same CPU+OS | VERIFIED (reuse) + RECOMPUTED | appendices A/B/I/J; `_recompute.py` #14 |
| 2 | "Serverless"/FaaS = appendix I's container with a per-invocation lifecycle + cold-start cost | VERIFIED (reuse) + RECOMPUTED | appendix I (VM-vs-container ~100× start gap); `_recompute.py` #1 |
| 3 | Autoscaling = ⌈offered_load / per-instance capacity⌉ + redundancy on a timer | RECOMPUTED | spine 13 (Little's Law); `_recompute.py` #2 |
| 4 | Plan to target utilization ρ≈0.5–0.7; latency = 1/(1−ρ) blows up at the knee | VERIFIED (reuse) + RECOMPUTED | spine 13; `_recompute.py` #3 |
| 5 | Object-store "N nines durability" = spine-20 parallel redundancy `A = 1−(1−a)^n` across replicas/AZs | VERIFIED (reuse) + RECOMPUTED | spine 20; `_recompute.py` #4 |
| 6 | Read replica = fast-but-stale (async lag); multi-region strong store pays consensus/commit-wait | VERIFIED (reuse) + RECOMPUTED | spine 15 + appendix L; `_recompute.py` #5 |
| 7 | The cloud cannot repeal CAP — it hides operators; CAP/PACELC posture is inherited | VERIFIED (reuse) | spine 11/15 + appendix L |
| 8 | CDN edge hit saves the cross-region RTT; value bounded by the speed-of-light latency hierarchy | VERIFIED (reuse) + RECOMPUTED | spine 13 + 16; `_recompute.py` #6 |
| 9 | Multi-AZ only helps if failures are uncorrelated; correlation collapses the nines | VERIFIED (reuse) + RECOMPUTED | spine 20 (correlated-failure model); `_recompute.py` #7 |
| 10 | Serial synchronous dependency chain multiplies unavailability: `A = ∏ a_i` | VERIFIED (reuse) + RECOMPUTED | spine 20; `_recompute.py` #8 |
| 11 | Failure domains nest: region ⊃ AZ ⊃ instance; spread replicas for independence | VERIFIED (reuse) + RECOMPUTED | spine 20; `_recompute.py` #12 |
| 12 | IaC provisioning is declarative + level-triggered reconciliation → idempotent | VERIFIED (reuse) + RECOMPUTED | appendix J; `_recompute.py` #10 |
| 13 | Control plane (provision/reconcile) is separate from data plane (serve); split limits blast radius | VERIFIED (reuse) + RECOMPUTED | appendix J + spine 19; `_recompute.py` #13 |
| 14 | Storage hierarchy (local NVMe < block < object < cross-region) mirrors the spine-13 latency ladder; egress metered, ingress free | VERIFIED (reuse) + RECOMPUTED | spine 13; `_recompute.py` #9, #11 |

## `[UNVERIFIED]` carry-forward (none load-bearing — ALL vendor specifics; every mechanism is spine-derived)
- **ALL vendor-specific names & numbers** — S3 "eleven nines," EBS IOPS/throughput tiers, Lambda
  memory/time/concurrency limits, specific instance families, exact AZ counts per region, all pricing
  (e.g. the illustrative $0.09/GB egress) — aws.amazon.com / cloud.google.com / Azure docs HTTP
  **000** this wave. These are cited as *illustrations* of the vendor-neutral primitive, never as
  load-bearing facts. The *primitive + its math* is reused from spine 13/20/15 + appendices I/J/L and
  recomputed.
- **Egress price direction** is the load-bearing claim (ingress free, egress metered → keep traffic
  in-region); the *number* is illustrative only.
- This appendix intentionally goes deep on **primitives and the math/forcing-functions behind them**,
  not on any one vendor's console — consistent with O being the cloud-*primitives* reference, not a
  vendor tutorial.

**0 blockers.** Reference-grade, exercise-free; all numbers re-derived (`_recompute.py` 14/14); no
vendor number is load-bearing; every mechanism reused from line-verified spine math + appendices.