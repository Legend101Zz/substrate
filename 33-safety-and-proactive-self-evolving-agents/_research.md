# 33 · safety-and-proactive-self-evolving-agents — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 33 is the **THREAT + EVOLUTION layer**: how
> an agent gets attacked (prompt injection), how you contain the blast (defence-in-depth +
> sandboxing + oversight), and how it safely improves itself (Reflexion gated by 31 eval). Bespoke
> structure: a **threat-model → defence-in-depth → controlled-evolution walkthrough** (NOT four
> clusters, NOT a copy of 19/31). NEW primary fetched+verified: **Greshake et al. Indirect Prompt
> Injection (arXiv 2302.12173)**; evolution primary REUSED (local+VERIFIED): **Reflexion
> (2303.11366)**. Full depth: `_research_safety-and-proactive-self-evolving-agents.md`. Math:
> `_recompute.py` (15/15). Factcheck: `_factcheck_phase1.md` (0 blockers).

## 1. The one idea (VERIFIED — Greshake 2302.12173)
**An LLM blurs the line between data and instructions** (VERBATIM L33-34) — so every channel that
injects *data* into context is also an *instruction* channel an attacker can write to: a **tool
result** (23), a **memory note** (25), a **retrieved passage** (29/30). The injection pointers that
22-32 kept FORWARD-marking `[UNVERIFIED]` all land here on ONE root cause. **Indirect** injection is
remote control "without a direct interface" (L35-37), and a poisoned passage "can act as **arbitrary
code execution** … control how and if other APIs are called" (L44-46) — it hijacks the agent's 23
actuators, not just its answer.

## 2. The walkthrough (the bespoke spine)
- **Threat model (Greshake §3):** *methods* = Passive (by retrieval — poisoned web/code/docs),
  Active (delivered, e.g. emails), User-driven (paste), Hidden/multi-stage (fetch-bigger-payload,
  encoded, in-image); *threats* = data-theft / fraud / intrusion / malware / manipulation /
  availability / **worming** ("prompts as worms"); *persistence* = copy the injection into memory
  (25) → re-read across sessions. This is the 20 blast-radius catalog for a stochastic actuator.
- **Defence-in-depth (no silver bullet — the paper is explicit: mitigations "lacking",
  "Whack-A-Mole", alignment "impossib[le]" to fully defend, L50-51/L1271/L1273-4):**
  (1) **trust boundary on data** — tag provenance, treat tool-result/memory/passage as UNTRUSTED,
  sanitize/delimit at the write (25) and read (30) boundaries [root fix];
  (2) **capability confinement / sandboxing / ACE** — least privilege + per-agent sandbox cells +
  containers/cgroups/seccomp (18/20 over capabilities → App I);
  (3) **inline guardrails** — input-sanitize + tool-arg schema (23) + output-screen + safety
  classifier, measured for escape AND over-refusal (31);
  (4) **oversight** — risk-based human/critic approval gate on high-capability actions; the 27
  critic/voting ensemble as the LLM-supervisor the paper names (L1287-1300) (18/27);
  (5) **detection & response** — trace every tool call (19 Dapper), alert on anomalous capability
  use, turn caught attacks into 31 golden regression tests.
- **Controlled evolution (Reflexion 25, gated by 31):** "proactive self-evolving" = a closed
  self-eval → reflect → improve loop (episodic reflection improves the next attempt WITHOUT weight
  updates). It is SAFE only when the signal is a trustworthy 31 eval oracle and a gate (18/27) sits
  before any self-modification; ungated, it reward-hacks a proxy. Gains converge to a ceiling and are
  budgeted by eval cost — bounded, not runaway.

## 3. The economics (RECOMPUTED — headlines, `_recompute.py` 15/15)
Blast radius = 1-write-many-reads (transient 12 vs persisted-to-memory 62 reads; attacker pays 1
write, victim pays R reads → sanitize the boundary) · least-privilege 8→2 caps (4× smaller surface)
+ per-agent cell = 20× fleet containment (20) · defence-in-depth 3×80% screens → 0.8% escape vs
single-filter 20% leak (Whack-A-Mole), at a 5.9% over-refusal tax (31) · self-improvement converges
to a ceiling and is gated by eval cost; ungated → reward-hacking · risk-based approval gate 20×
cheaper than gate-all and catches 100% of damage (18/27) · prompt-worm R₀=2.0>1 unsanitized vs 0.5<1
sanitized (lever = per-hop re-inject prob, not agent count) · composed screen×confine×gate <
any single layer.

## 4. Where 33 sits
33 is the agentic **security + capacity-of-trust** layer: it takes 18 (admission/shedding → gating &
confinement), 20 (cells/blast-radius/tail → sandboxing), 19 (tracing → detection), and the Part III
carriers 23/25/29/30 (the injection channels), and composes them into a defence-in-depth
architecture, then closes the 31 eval loop into a controlled self-improvement cycle (25 memory + 26
persistence). 31↔32↔33 are the agentic *trust* triad: 31 = "is it correct?", 32 = "what does it
cost?", 33 = "can it be attacked / can it safely improve?". Feeds 34 (every untrusted-data channel
must carry a budgeted safety layer).

## 5. Failure modes (safety-specific)
Treating tool-result/memory/passage as trusted instructions (the root bug) · single-filter defence
(Whack-A-Mole; bypassed by encoding/obfuscation) · over-confinement (over-refusal tax, 31) ·
unsanitized shared memory (prompt worm R₀>1, fleet contamination) · over-broad capabilities (huge
blast radius on compromise, 20) · gate-everything (cost/false-reject blowout) vs gate-nothing
(unsupervised dangerous actions) · **ungated self-improvement (reward-hacking a proxy — needs 31)** ·
no attack tracing (silent compromise, 19). Most are 18/19/20/31 problems re-aimed at an adversary.

## 6. Build-your-own (eleventh harness upgrade, after 32 cost)
Wrap the 28 harness in a safety layer: tag untrusted channels + plant a real indirect injection in a
retrieved passage (30) and watch it hijack a tool, then defend it — least-privilege capability
allow-list + sandbox (→App I); stacked input/arg-schema(23)/output guardrails measured for escape AND
over-refusal (31); a risk-based approval gate (18/27); a Reflexion self-improve loop (25) gated by
`run_evals()` (31), shown to converge — and shown to reward-hack when ungated; trace every tool call
(19) and turn a caught attack into a new golden test (31).

## 7. Provenance summary
- **PRIMARY (NEW, FETCHED+VERIFIED):** Greshake et al., Indirect Prompt Injection (AISec '23,
  arXiv 2302.12173) — `meta/fetched_primaries/greshake-injection-2302.12173.{pdf,txt}`, receipt
  `_VERIFIED_2026-06-10_injection.md`.
- **PRIMARY (REUSED, local+VERIFIED):** Reflexion (2303.11366, verified in 25) for the
  self-evolving loop.
- **RECOMPUTED:** `_recompute.py` (15/15).
- **REUSED:** 18, 19, 20, 23, 25, 27, 29, 30, 31, 32.
- **Carried `[UNVERIFIED]` pointers RESOLVED here** (forward links land; originals not erased):
  23 (tool-result), 25 (memory + persistence), 29 (server), 30 (passage) → all the same root cause.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** dual-LLM/CaMeL capability-defense + Willison
  essays; Constitutional AI (2212.08073) + RLHF/InstructGPT (2203.02155) for alignment; formal
  sandboxing (seccomp/gVisor/Firecracker → App I); Greshake's internal impossibility citation [80];
  agent red-team/injection benchmarks (AgentDojo); Greshake empirical success-rate tables (read
  qualitatively, per-number extraction not done — non-load-bearing).

---
**33 reconciled.** Part III "Phase 1 batch 3" now stands at **22-33 reconciled** (12 of 13 agentic
sub-courses). **BONUS:** the Greshake fetch lands the carried injection `[UNVERIFIED]` pointers from
23/25/29/30 → VERIFIED root cause. Last remaining: **34-design-your-own-agentic-system** (the Part
III CAPSTONE DESIGN CANVAS, applying all of 22-33 the way 21 applied 13-20; NO new primary).
