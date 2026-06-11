# 33 · Phase-1 factcheck — safety-and-proactive-self-evolving-agents

> Method (same discipline as 13-32): every load-bearing claim is (a) RECOMPUTED in `_recompute.py`
> (15/15 pass), (b) backed by a FETCHED+VERIFIED primary, (c) REUSED from a line-verified Part I/II
> + 22-32 anchor, or (d) flagged `[UNVERIFIED]` carry-forward. **NEW PRIMARY fetched+verified:**
> Greshake et al. Indirect Prompt Injection (arXiv 2302.12173). **0 blockers.**

## Bespoke structure note
33 is a **THREAT-MODEL → DEFENCE-IN-DEPTH → CONTROLLED-EVOLUTION walkthrough**, NOT four clusters
and NOT the 13-20 four-cluster shape. Plan-sanctioned ("prompt-injection via tool-result/memory/
retrieved-passage carried from 23/25/29/30; sandboxing/ACE; self-improvement loops Reflexion 25;
alignment/oversight"). It is the layer where the FORWARD `[UNVERIFIED]` injection pointers from
23/25/29/30 finally land on one verified root cause.

## New primary (FETCHED+VERIFIED)
**Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz — "Not what you've signed up for: Compromising
Real-World LLM-Integrated Applications with Indirect Prompt Injection"** (AISec '23 / arXiv
2302.12173). Files `meta/fetched_primaries/greshake-injection-2302.12173.{pdf,txt}`; receipt
`_VERIFIED_2026-06-10_injection.md`. Verbatim load-bearing claims (line refs in receipt):
- **Root cause:** "blur the line between data and instructions" (L33-34, L254-255). ← the one idea.
- **Indirect = remote, no direct interface** (L35-37); **retrieved prompts = arbitrary code / API
  control** (L44-46, L127-128). ← severity = control of 23 actuators.
- **Injection-method taxonomy** (Passive/Active/User-driven/Hidden-multistage, §3.1, L310-356).
- **Threat taxonomy** (info-gathering/fraud/intrusion/malware/manipulation/availability/**worming**,
  §3.2, L219-248, L396-442).
- **Persistence via memory** (L424-448) ← lands 25's injection-via-memory pointer.
- **No reliable fix; "Whack-A-Mole"; alignment provably insufficient** (L50-51, L1271, L1273-4,
  L1281-6). ← defends the defence-in-depth thesis, not a single filter.

## Reused primary (local, already VERIFIED)
**Reflexion (arXiv 2303.11366, verified in 25):** episodic-memory reflection improves the next
attempt WITHOUT weight updates — the mechanism for the "proactive self-evolving" half. Re-aimed, not
re-fetched.

## Recomputed claims (`_recompute.py`, 15/15)
- **Injection blast radius** = 1-write-many-reads (25 poisoning): transient 12 vs persisted 62 reads;
  attacker pays 1 write, victim pays R reads. PASS×2.
- **Sandbox-as-cell (20)**: least-privilege 8→2 caps (4× smaller surface); per-agent cell 20×
  fleet containment. PASS×2.
- **Defence-in-depth (31)**: 3×80% screens → 0.8% escape; 3×2%-FP → 5.9% over-refusal tax; single
  80% filter leaks 20% (Whack-A-Mole). PASS×3.
- **Self-evolution (Reflexion 25, gated by 31)**: converges to ceiling (not unbounded); eval cost
  gates the loop; ungated loop optimizes a proxy (reward-hacking). PASS×3.
- **Risk-based approval gate (18/27)**: gate-high-risk 20× cheaper than gate-all, catches 100% of
  damage; lowers false-reject 20×. PASS×2.
- **Prompt-worm R₀ (Greshake contamination)**: unsanitized R₀=2.0>1 (epidemic) vs sanitized
  R₀=0.5<1 (contained); lever = per-hop re-inject prob. PASS×2.
- **Composed defences multiply**: screen×confine×gate < any single layer. PASS.

## Reused (line-verified Part I/II + 22-32)
18 (admission/load-shedding → approval gating & confinement); 19 (Dapper tracing → attack
detection); 20 (cells/blast-radius/tail → sandboxing); 23 (tool-result carrier + arg-schema
validation); 25 (memory carrier + persistence multiplier + Reflexion); 27 (critic/voting supervisor;
multi-agent worm fleet); 29 (connector carrier); 30 (retrieved-passage carrier); 31 (defence-in-depth
identity + eval interlock + golden-test feedback); 32 (cost of the screening layers).

## Carried `[UNVERIFIED]` pointers RESOLVED here (forward links land; originals NOT erased)
- 23 injection-via-tool-result → root cause named (claim 1).
- 25 injection-via-memory → VERIFIED carrier + persistence multiplier (Greshake L424-448).
- 29 injection-via-server / 30 injection-via-passage → Passive-retrieval method (§3.1).
These earlier files keep their forward-pointer notes; 33 is the destination, as planned.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Simon Willison prompt-injection essays + **dual-LLM / CaMeL** capability-defense pattern (blog/
  paper, not fetched).
- **Constitutional AI** (Bai 2212.08073), **RLHF/InstructGPT** (Ouyang 2203.02155) — alignment/
  oversight, named not fetched.
- Formal **sandboxing** refs (seccomp/gVisor/Firecracker) → Appendix I, not fetched here.
- Greshake's internal **impossibility-of-alignment** citation [80] — secondary, not independently
  fetched.
- Agent **red-team / injection benchmarks** (AgentDojo etc.) — named, not fetched.
- Greshake empirical success-rate tables — read qualitatively (attacks demonstrated viable);
  per-number extraction not done (non-load-bearing; our numbers are recomputed first-principles).

## Verdict
33 is honest and threat-appropriate: one NEW primary (Greshake 2302.12173) settles the root cause
("data IS instructions") and the no-silver-bullet stance; Reflexion (local) anchors the evolution
half; every quantitative claim is RECOMPUTED first-principles (15/15) and every defence cross-links
to a line-verified 18/19/20/23/25/27/30/31 mechanism. The forward injection pointers from
23/25/29/30 land here as designed. Residual `[UNVERIFIED]` are named-not-fetched secondary defenses
and benchmarks — none load-bearing. Reconcile into `_research.md`. **0 blockers.**
