# 33 — Safety & Proactive Self-Evolving Agents · _structure.md

**Identity:** the **THREAT + EVOLUTION layer** of an agentic system — how an agent gets attacked
(prompt injection), how you contain the blast (defence-in-depth + sandboxing + oversight), and how it
safely improves itself (Reflexion gated by a 31 eval oracle). 33 is where every injection pointer that
22–32 kept FORWARD-marking `[UNVERIFIED]` lands on ONE root cause — and where the carried pointers
from 23/25/29/30 are RESOLVED.

**Bespoke shape — "threat-model → defence-in-depth → controlled-evolution walkthrough."** NOT four
clusters, NOT a copy of 19/31. The one idea is VERIFIED from Greshake: **an LLM blurs the line between
data and instructions** — so every channel that injects *data* into context is also an *instruction*
channel an attacker can write to (a tool result 23, a memory note 25, a retrieved passage 29/30).
**Indirect** injection is remote control "without a direct interface," and a poisoned passage "can act
as arbitrary code execution ... control how and if other APIs are called" — it hijacks the agent's 23
actuators, not just its answer. The defence is honest: the paper itself says mitigations are
"lacking," it's "Whack-A-Mole," full alignment is "impossib[le]" — so the chapter teaches
defence-in-depth, never a silver bullet. NEW primary FETCHED+VERIFIED (Greshake et al., Indirect
Prompt Injection, arXiv 2302.12173); evolution primary REUSED local+VERIFIED (Reflexion, 2303.11366).
Math recomputed (15/15). The `/build` deliverable: wrap the 28 harness in a safety layer — the
eleventh harness upgrade.

## Dependency position
- **Depends on:** 23 (tool-result channel + tool-arg schema) + 25 (memory channel + poisoning blast
  radius + persistence of an injection) + 29 (untrusted server channel) + 30 (retrieved-passage
  channel) + 18 (admission/shedding → gating & confinement) + 20 (cells/blast-radius/tail →
  sandboxing) + 19 (Dapper tracing → attack detection) + 27 (critic/voting ensemble = the
  LLM-supervisor oversight gate) + 31 (eval oracle that gates self-improvement; guardrail escape/
  over-refusal metrics) + 32 (gating has a price; runaway = cost-availability attack) + 26 (persisted
  reflections/memory) + 28 (the harness wrapped).
- **Feeds into:** 34 ("every untrusted-data channel must carry a budgeted safety layer" — 33 supplies
  the safety column of the design ledger; one open channel = 100% compromise). Completes the agentic
  trust triad 31/32/33: correct? / affordable? / **attackable & safely-improving?**
- **Appendix links DOWN:** I-docker (formal sandboxing — seccomp/gVisor/Firecracker; the ACE
  containment cell) · L-consensus (oversight quorum) · M-agentic-papers (Greshake, Reflexion,
  Constitutional-AI anchors) · N-math (R₀ worm arithmetic, blast-radius). 33 owns the threat model +
  defence composition + the controlled-evolution gate.

## Section specs (3–5 lines each)
1. **The one idea: an LLM blurs data and instructions (VERIFIED — Greshake)** — VERBATIM L33-34. So
   every data-injection channel is also an instruction channel: tool result (23), memory note (25),
   retrieved passage (29/30). The forward-marked injection `[UNVERIFIED]`s from 22–32 all collapse onto
   this single root cause. Indirect injection (L35-37) = remote control "without a direct interface";
   a poisoned passage = ACE over the agent's actuators (L44-46).
2. **Threat model (Greshake §3)** — *methods*: Passive (by retrieval — poisoned web/code/docs), Active
   (delivered, e.g. emails), User-driven (paste), Hidden/multi-stage (fetch-bigger-payload, encoded,
   in-image). *threats*: data-theft / fraud / intrusion / malware / manipulation / availability /
   **worming** ("prompts as worms"). *persistence*: copy the injection into memory (25) → re-read
   across sessions. This is the 20 blast-radius catalog for a stochastic actuator.
3. **Defence-in-depth (no silver bullet — VERIFIED the paper is explicit)** — five composed layers,
   none sufficient alone: (1) **trust boundary on data** — tag provenance, treat tool-result/memory/
   passage as UNTRUSTED, sanitize/delimit at the write (25) and read (30) boundaries [the root fix];
   (2) **capability confinement / sandboxing / ACE** — least privilege + per-agent sandbox cells +
   containers/cgroups/seccomp (18/20 over capabilities → App I); (3) **inline guardrails** —
   input-sanitize + tool-arg schema (23) + output-screen + safety classifier, measured for escape AND
   over-refusal (31); (4) **oversight** — risk-based human/critic approval gate on high-capability
   actions (the 27 critic/voting ensemble = the LLM-supervisor the paper names); (5) **detection &
   response** — trace every tool call (19 Dapper), alert on anomalous capability use, turn caught
   attacks into 31 golden regression tests.
4. **Controlled evolution (Reflexion 25, gated by 31)** — "proactive self-evolving" = a closed
   self-eval → reflect → improve loop (episodic reflection improves the next attempt WITHOUT weight
   updates). It is SAFE only when the signal is a trustworthy 31 eval oracle and a gate (18/27) sits
   before any self-modification; ungated, it reward-hacks a proxy. Gains converge to a ceiling and are
   budgeted by eval cost — bounded, not runaway.
5. **The economics (RECOMPUTED, `_recompute.py` 15/15)** — blast radius = 1-write-many-reads
   (transient 12 vs persisted-to-memory 62 reads; attacker pays 1 write, victim pays R reads →
   sanitize the boundary) · least-privilege 8→2 caps (4× smaller surface) + per-agent cell = 20× fleet
   containment (20) · defence-in-depth 3×80% screens → 0.8% escape vs single-filter 20% leak, at a
   5.9% over-refusal tax (31) · risk-based approval gate 20× cheaper than gate-all, catches 100% of
   damage (18/27) · prompt-worm R₀=2.0>1 unsanitized vs 0.5<1 sanitized (lever = per-hop re-inject
   prob, NOT agent count) · self-improvement converges to a ceiling; ungated → reward-hacking.
6. **Where 33 sits + failure modes** — 33 = the agentic security + capacity-of-trust layer: 18
   (gating/confinement) + 20 (cells/blast-radius) + 19 (detection) + the 23/25/29/30 injection
   carriers, composed into defence-in-depth, then closed into a 31-gated self-improvement cycle.
   Failures: treating tool-result/memory/passage as trusted instructions (root bug) · single-filter
   defence (Whack-A-Mole) · over-confinement (over-refusal tax, 31) · unsanitized shared memory
   (prompt worm R₀>1) · over-broad capabilities (huge blast radius, 20) · gate-everything (cost
   blowout) vs gate-nothing (unsupervised dangerous actions) · **ungated self-improvement
   (reward-hacking a proxy — needs 31)** · no attack tracing (silent compromise, 19).

## Paired build lab (/build → own-coding-agent-harness, eleventh upgrade)
Wrap the 28 harness in a safety layer: tag untrusted channels + plant a real indirect injection in a
retrieved passage (30) and watch it hijack a tool — THEN defend it: least-privilege capability
allow-list + sandbox (→App I); stacked input/arg-schema(23)/output guardrails measured for escape AND
over-refusal (31); a risk-based approval gate (18/27); a Reflexion self-improve loop (25) gated by
`run_evals()` (31), SHOWN to converge — and SHOWN to reward-hack when ungated; trace every tool call
(19) and turn a caught attack into a new golden test (31).

## Diagrams needed
- The data/instruction blur: one channel carries both → attacker writes to the data side (Greshake).
- The injection-channel map: tool result (23) · memory (25) · MCP server (29) · passage (30) → one
  root cause.
- The threat taxonomy: methods × threats × persistence (the blast-radius catalog).
- Defence-in-depth as five composed layers; escape rate as layers stack vs single-filter leak.
- Blast radius 1-write-many-reads (transient vs persisted-to-memory; attacker pays 1, victim pays R).
- The prompt-worm R₀ model (>1 unsanitized vs <1 sanitized; lever = per-hop re-inject prob).
- The controlled-evolution loop: self-eval → reflect → improve, with the 31/18/27 gate before any
  self-modification (and the ungated reward-hacking failure path).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **PRIMARY (NEW, FETCHED+VERIFIED):** Greshake et al., Indirect Prompt Injection (AISec '23, arXiv
  2302.12173) — `meta/fetched_primaries/greshake-injection-2302.12173.{pdf,txt}`, receipt
  `_VERIFIED_2026-06-10_injection.md`.
- **PRIMARY (REUSED, local+VERIFIED):** Reflexion (2303.11366, verified in 25) for the self-evolving
  loop.
- **RECOMPUTED:** `_recompute.py` (15/15).
- **REUSED:** 18, 19, 20, 23, 25, 27, 29, 30, 31, 32.
- **Carried `[UNVERIFIED]` pointers RESOLVED here (reconcile-note — originals NOT erased):** the
  injection pointers forward-marked in 23 (tool-result), 25 (memory + persistence), 29 (server), 30
  (passage) all land on the Greshake data/instruction-blur root cause and are upgraded → VERIFIED at
  this convergence point; each home chapter keeps its original flag with a pointer to here.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** dual-LLM/CaMeL capability-defense + Willison
  essays; Constitutional AI (2212.08073) + RLHF/InstructGPT (2203.02155) for alignment; formal
  sandboxing (seccomp/gVisor/Firecracker → App I); Greshake's internal impossibility citation [80];
  agent red-team/injection benchmarks (AgentDojo); Greshake empirical success-rate tables (read
  qualitatively — per-number extraction NOT done, non-load-bearing).
- **Boundary discipline:** formal sandboxing depth → appendix I; alignment training (CAI/RLHF) is
  flagged, not taught here; eval mechanics stay in 31; cost of gating in 32. 33 owns the threat model,
  the defence-in-depth composition, and the controlled-evolution gate.
