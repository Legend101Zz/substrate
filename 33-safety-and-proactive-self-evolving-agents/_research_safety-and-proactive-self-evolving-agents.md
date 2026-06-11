# 33 · safety-and-proactive-self-evolving-agents — deep research brief (`_research_*.md`)

> Phase-1 brief (NO course prose). Full-depth cluster file; the brain reconciles this into
> `_research.md`. 33 is the **THREAT + EVOLUTION** layer of Part III. Bespoke structure: a
> **threat-model → defence-in-depth → controlled-evolution walkthrough** (NOT four clusters, NOT a
> copy of 19/31). Primary FETCHED+VERIFIED: **Greshake et al., Indirect Prompt Injection
> (arXiv 2302.12173)**. Self-evolution primary REUSED (local+VERIFIED): **Reflexion (2303.11366)**.
> Math: `_recompute.py` (15/15). Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_injection.md`.

---

## A. The one idea (VERIFIED — Greshake 2302.12173)

**An LLM blurs the line between data and instructions.** VERBATIM: "LLM-Integrated Applications
**blur the line between data and instructions**" (L33-34); "the line between data and code … would
get blurry" (L254-255). Therefore every channel that injects *data* into the context is also an
*instruction* channel an attacker can write to:
- a **tool result** (23's deterministic output is attacker-controllable text) → 23's carried
  injection-via-tool-result `[UNVERIFIED]` lands here;
- a **memory note** (25's long-term store) → 25's carried injection-via-memory `[UNVERIFIED]`;
- a **retrieved passage** (29 connector / 30 RAG corpus) → 29/30's carried
  injection-via-server/passage `[UNVERIFIED]`.

These were all FORWARD-pointed to 33 in earlier sub-courses; 33 is where the single root cause is
named and defended. This is **indirect** prompt injection: "enable adversaries to **remotely
(without a direct interface)** exploit LLM-integrated applications by strategically injecting prompts
into data likely to be retrieved" (L35-37).

**Severity:** "processing retrieved prompts can act as **arbitrary code execution** … control how
and if other APIs are called" (L44-46; L127-128). A poisoned passage is not a wrong answer — it is
remote control of the agent's *actuators* (its tools), i.e. of its 23 capabilities.

---

## B. The attack surface (VERIFIED taxonomy, §3.1–3.2)

### Injection methods (how the payload arrives) — §3.1
- **Passive (by retrieval)** — poisoned public sources (SEO-promoted pages), invisible text on a
  page a sidebar summarizes, poisoned code in imported repos, poisoned docs in a Retrieval-Plugin
  corpus (L314-329). ↔ 30 RAG corpus / 29 connector.
- **Active (delivered)** — emails/messages processed by an assistant or spam-filter LLM (L330-334).
  ↔ 17 event-driven inputs feeding an agent.
- **User-driven** — trick the user into pasting attacker text (clipboard exploit, "try this
  prompt") (L335-344).
- **Hidden / multi-stage** — a small injection instructs the model to fetch a larger payload;
  encoded (Base64) payloads to dodge filters; payloads hidden in images for multi-modal models
  (L345-356). ↔ 25 persistence + 30 retrieval composed.

### Threats (what the payload does) — §3.2 (adapted from a cyber-threat taxonomy)
Information gathering / **data theft** (L40, L396); **Fraud** (L407); **Intrusion** (L420-434, esp.
when the model has API/tool access); **Malware** (L439-442, "prompts themselves can now act as
malware"); **Manipulated content / disinformation** (L122, L230); **Availability** attacks on the
LLM itself (L237, L248); and **spreading injections — "Prompts as worms"** / information-ecosystem
contamination (L40 "worming"; L227-228). This is the agent's **blast-radius catalog** — the 20
failure-domain idea applied to a stochastic actuator.

### Persistence (how long it lasts) — §3
"persistence across sessions by **copying the injection into memory** … a memory shared with other
applications" (L424-448; Fig col "Persistence" L220). Persistence is the **multiplier**: a single
write is re-read across many future sessions (the 25 poisoning identity — see C).

---

## C. The economics of the threat (RECOMPUTED, `_recompute.py` 15/15)

1. **Blast radius = 1-write-many-reads (25 poisoning identity).** A poisoned source re-injects
   every turn it stays resident AND every future session that re-reads it from memory. Transient
   (in-context only) ≈ 12 reads; persisted-to-memory ≈ 62 reads (>4×). **The attacker pays one
   write; the victim pays R reads** → sanitize at the *write/read boundary*, not per-turn.
2. **Sandbox-as-cell (20) bounds the blast radius.** Least-privilege confines a compromise from the
   full toolbox (8 dangerous caps) to what the task needs (2) → 4× smaller exploit surface. A
   per-agent sandbox cell turns "1 compromise hits all 20 agents" into "1 compromise hits 1" (20×
   containment) — the 20 cell-isolation result over **capabilities** instead of traffic.
3. **Defence-in-depth (31 identity) + over-refusal tax.** Three independent 80%-effective screens
   (input-sanitize · capability-gate · output-screen) → injection escape 0.8% (a single 80% filter
   still leaks 20% — the paper's "Whack-A-Mole" point). But 3×2%-FP screens block 5.9% of *good*
   actions → measure the false-positive/over-refusal tax as its own metric (same shape as 31).
4. **Controlled self-evolution (Reflexion 25, gated by 31).** Reflexion's episodic reflection
   improves the next attempt **without weight updates**; modeled with diminishing returns it
   converges toward a ceiling, NOT unboundedly. The loop is **budgeted by 31's eval cost** (stop
   when marginal value ≤ eval price). **Without a 31 eval oracle the loop optimizes a proxy
   (reward-hacking)** → eval is the safety interlock on self-improvement.
5. **Risk-based approval gating (18 admission + 27 critic).** Gating *all* actions for human/critic
   approval catches attacks but costs 1000 reviews; gating only **high-capability** actions (the 5%
   that write/exec/spend/send) costs 50 reviews (20× cheaper) and still catches 100% of the
   damage-causing actions — and lowers the false-reject tax 20×. Confine the gate to dangerous
   capabilities.
6. **Prompt-worm propagation (Greshake "prompts as worms") = an R₀ condition.** A compromised agent
   that writes the injection into sources other agents read is a branching process: R₀ = writes ×
   re-inject-prob. Unsanitized shared memory → R₀ = 2.0 > 1 (epidemic across the fleet); sanitizing
   the write/read boundary → R₀ = 0.5 < 1 (contained). **The lever is per-hop re-inject prob, not
   agent count.**
7. **Composed defences multiply.** screen × confine × gate drives residual damage below any single
   layer — defence-in-depth + confinement + oversight *compose* (the paper's thesis that no single
   mechanism suffices).

---

## D. Defences (VERIFIED stance: no silver bullet; defence-in-depth)

The paper is explicit that **today's mitigations are insufficient**: "effective mitigations …
currently **lacking**" (L50-51); defence is "**Whack-A-Mole**" (L1271); "**impossibility of
defending against all undesired behaviors by alignment or RLHF**" (L1273-4); Bing Chat's
input/output filtering was bypassed because it ignores the model's *external* input (L1281-6). So 33
teaches a **layered architecture**, each layer an already-VERIFIED mechanism re-aimed at safety:

1. **Trust boundary on data (the root fix).** Tag provenance: system/developer text = trusted;
   tool-result / memory / retrieved-passage = **untrusted data, never instructions**. Sanitize /
   delimit / quote at the *write* (into memory, 25) and *read* (from retrieval, 30) boundaries.
   Candidate (named, not solved by the paper): a separate non-instruction-tuned screener; "dual-LLM"
   pattern `[UNVERIFIED]`.
2. **Capability confinement / sandboxing / ACE (18/20 → Appendix I).** Least privilege per task;
   per-agent sandbox cells; containers/cgroups/seccomp for shell/fs/net tools (→ App I docker/
   namespaces). Bounds the blast radius when (not if) a layer is bypassed.
3. **Inline guardrails / defence-in-depth (31/18).** Input sanitizer + tool-arg schema validation
   (23) + output screen + safety classifier — measured for both escape AND over-refusal (C-3).
4. **Oversight / human-in-the-loop (18/27).** Risk-based approval gate on high-capability actions
   (C-5); the 27 critic/voting ensemble as an LLM-supervisor/moderator (the paper's named candidate,
   L1287-1300) — "an LLM supervisor or moderator that … specifically detects the attacks".
5. **Detection & response (19/31).** Trace every tool call (19 Dapper); alert on anomalous
   capability use; turn detected attacks into 31 golden regression tests (close the loop).

---

## E. The EVOLUTION half — proactive / self-improving agents (Reflexion 25, local+VERIFIED)

"Proactive self-evolving" = a closed **self-eval → reflect → improve** loop, NOT weight training:
- **Mechanism (Reflexion, VERIFIED in 25):** the agent writes an episodic *reflection* on a failed
  trajectory into memory; the reflection conditions the next attempt → improvement WITHOUT gradient
  updates. 33 generalizes this from "retry a task" to "improve the agent's own prompts/tools/policy
  over time".
- **The interlock is 31.** Self-improvement is only safe if the *signal* is a trustworthy 31 eval
  oracle; an ungated loop reward-hacks a proxy (C-4). So evolution = 25 memory (store lessons) + 31
  eval (validate gain) + 26 persistence (durable across sessions) + a gate (18/27) before any
  self-modification takes effect.
- **Bounded, not runaway:** gains converge to a ceiling and are budgeted by eval cost (C-4) — the
  honest counter to "the agent improves itself forever" hype. Alignment/oversight (D-4) keeps the
  self-modifying loop human-supervised.

---

## F. Where 33 sits / cross-links
- **Down into Part I/II:** 18 (admission/load-shedding → approval gating & confinement),
  20 (cells/blast-radius → sandbox isolation; tail → worst-case exploit), 19 (Dapper tracing →
  attack detection).
- **Down into earlier Part III:** 23 (tool-result carrier + arg-schema validation), 25 (memory
  carrier + persistence multiplier + Reflexion self-evolution), 27 (critic/voting as supervisor;
  multi-agent worm fleet), 29 (connector/server carrier), 30 (retrieved-passage carrier),
  31 (defence-in-depth identity + eval interlock + golden-test feedback), 32 (availability/cost of
  the screening layers).
- **Up into 34:** the design canvas must budget a safety layer for every untrusted-data channel.
- **Appendix I** (docker/cgroups/namespaces/seccomp) for the sandboxing depth.

## G. Build-your-own (eleventh harness upgrade, after 32 cost)
Wrap the 28 harness in a **safety layer**: (1) tag tool-result / memory / retrieved-passage as
UNTRUSTED and delimit them; plant a real indirect-injection in a retrieved passage (30) and show it
hijack a tool call; (2) add a capability allow-list per task (least privilege) + run shell/fs tools
in a sandbox (→ App I); (3) stack input-sanitize / arg-schema (23) / output-screen guardrails and
MEASURE both escape and over-refusal (31); (4) a risk-based approval gate (18/27) on high-capability
actions; (5) a Reflexion self-improve loop (25) gated by `run_evals()` (31) — show it converge AND
show an ungated version reward-hack; (6) trace every tool call (19) and convert a caught attack into
a new golden test (31).

## H. Open questions / where sources are thin (carry-forward `[UNVERIFIED]`)
- Simon Willison prompt-injection essays + the **dual-LLM / "CaMeL" capability-defense** pattern
  (blog/paper, NOT fetched).
- **Constitutional AI** (Bai et al. 2212.08073), **RLHF/InstructGPT** (Ouyang 2203.02155) — named
  for the alignment/oversight section, NOT fetched.
- Formal **sandboxing** references (seccomp/gVisor/Firecracker) → Appendix I, NOT fetched here.
- The **impossibility-of-alignment** citation [80] inside Greshake — secondary, not independently
  fetched.
- **SWE-bench-style safety evals / red-team benchmarks** (e.g. AgentDojo, injection benchmarks) —
  named, NOT fetched.
- Greshake's empirical success-rate tables against Bing Chat / GPT-4 synthetic apps — read
  qualitatively (attacks demonstrated viable); per-number extraction NOT done (non-load-bearing for
  the model; our quantitative claims are recomputed first-principles, not quoted from the paper).
