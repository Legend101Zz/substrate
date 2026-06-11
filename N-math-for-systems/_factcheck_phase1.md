# Appendix N · Phase-1 factcheck — math-for-systems

> Method (same discipline as the spine): every load-bearing number is RECOMPUTED in `_recompute.py`
> (20/20 pass) or REUSED from a line-verified spine anchor. N is a **reference appendix** (deep info
> only, NO exercises) so there is no chapter prose to check — only the formulas. **0 blockers.**

## Bespoke structure note
N is a **formula compendium organized by the question each tool answers** (queueing/capacity →
hashing/probabilistic → tail/availability → statistics), NOT the 13-20 four-cluster shape and NOT a
build progression. Appendix-appropriate per CONSTITUTION #5 (reference-grade, exercise-free).

## NO new primary (why)
Every entry is a STANDARD mathematical result. The honest move for an appendix is not to re-cite a
1960s paper from memory but to **re-derive the result first-principles and show it computing** — which
`_recompute.py` does for all 20 checks. Original-author attributions are noted as carry-forward
`[UNVERIFIED]` (below) but are not load-bearing because the math itself is verified.

## Recomputed claims (`_recompute.py`, 20/20)
- Little's Law `L=λW` (forward sizing + inverted queue-as-latency-budget `Q/μ`). PASS×2.
- M/M/1 `W=1/(μ−λ)`, `L=ρ/(1−ρ)` (and L==λW consistency). PASS×2.
- Utilization wall `1/(1−ρ)` = 2×/5×/10×/20× at ρ=.5/.8/.9/.95; capacity `⌈D/ρ*⌉`=5. PASS×2.
- Birthday 23/365>50%; `√m` rule (~1177 keys for 50% in 1e6). PASS×2.
- Consistent hashing `~K/(N+1)` vs mod-N (~100× less churn on N=100→101). PASS.
- Bloom `k*=(m/n)ln2≈6.93`, fp≈0.82% at 10 b/item, closed-form `0.6185^{m/n}` matches. PASS×3.
- HLL RSE `1.04/√m` at m=1024 (3.25%) and m=16384 (0.81%). PASS×2.
- Fan-out tail `1−(1−p)^N`=63.4% at p=.01,N=100. PASS.
- Availability serial `∏a_i`=99.501%; parallel `1−(1−a)^n`=99.9999% (independence caveat). PASS×2.
- Amdahl ceiling `1/s`=20×; USL throughput peaks (~N=98) then retrogrades. PASS×2.
- Sampling CI ±3% ⇒ ~1068 samples. PASS.

## Reused (line-verified spine + local primaries)
Tail-at-Scale (`tail-at-scale-cacm2013`, local+VERIFIED) for the fan-out identity. The spine anchors
that consume this math are all reconciled: 06 (hashing/bloom/HLL), 07/08 (bloom on LSM read path),
13 (queueing/Little/wall/tail), 14/15 (consistent hashing/resharding), 17/18 (queue-as-budget),
19 (cardinality/sampling), 20 (availability/Amdahl/USL/capacity), 27 (join tail), 31 (eval CI).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Original-paper attributions not separately fetched: Little (1961), Bloom (1970), Flajolet et al.
  HyperLogLog (2007), Karger et al. consistent hashing (STOC 1997), Amdahl (1967), Gunther USL,
  Erlang's original queueing formulae. **Not load-bearing — every result is recomputed**, not relied
  upon by citation. Fetch opportunistically in Phase 2 if a chapter wants the historical quote.

## Verdict
N is honest and appendix-appropriate: no new load-bearing claim; every formula RE-DERIVED
first-principles (20/20) and cross-linked to the spine anchor that uses it, giving the course a
single verified home for its recurring math. Reconcile into `_research.md`. **0 blockers.**
