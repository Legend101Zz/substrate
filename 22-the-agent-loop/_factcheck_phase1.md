# 22 · Phase-1 factcheck — the-agent-loop

> Method (same discipline as 13-21): every load-bearing claim is either (a) RECOMPUTED in
> `_recompute.py` (18/18 pass), (b) VERIFIED verbatim against a primary fetched to
> `meta/fetched_primaries/`, (c) REUSED from a previously line-verified Part I/II sub-course, or
> (d) flagged `[UNVERIFIED]` and carried forward (must not harden into Phase-2 prose). 0 blockers.

## Bespoke structure note
Per the Part III plan: 22 is the FOUNDATIONAL control-loop primitive, so its single brief is a
loop walkthrough (anatomy → iteration → termination → failure → economics), NOT abstract source
clusters and NOT the four-cluster shape of 13-20. Plan-sanctioned departure.

## Primary fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Yao et al., "ReAct: Synergizing Reasoning and Acting in LMs", ICLR 2023 (arXiv 2210.03629) | `react-2210.03629.{pdf,txt}` | §2 the canonical Thought→Action→Observation loop; grounding cures CoT hallucination; +34%/+10% with 1-2 exemplars |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_agentic.md`.

### Verified claims (ReAct)
- "generate both reasoning traces and task-specific actions in an interleaved manner" — VERIFIED
  verbatim (abstract). Anchors the loop definition (§1, §2).
- "overcomes prevalent issues of hallucination and error propagation in chain-of-thought reasoning
  by interacting with a simple Wikipedia API" — VERIFIED verbatim. Anchors WHY tools ground
  reasoning (§2, handoff to 23).
- "an absolute success rate of 34% and 10% respectively, while being prompted with only one or two
  in-context examples" (ALFWorld, WebShop) — VERIFIED verbatim. Anchors "capability is in the loop"
  (§2).

## Recomputed claims (`_recompute.py`, 18/18)
- Per-turn prompt tokens linear: `p+(t-1)*g` (2000 / 4000 / 6500 at t=1/5/10). PASS.
- Cumulative input tokens **quadratic**: `T*p + g*T*(T-1)/2`; closed form == brute sum for
  T=1/5/10/20; g-term grows 4.22x when T doubles 10→20 (super-linear → O(T^2)). PASS. **Headline.**
- Cost-per-call + cumulative $ at example pricing ($3/$15 per 1M in/out); naive flat-prompt
  estimate undercounts 3.38x. PASS.
- Step budget bounds worst-case cost ($0.495 at max_steps=20). PASS.
- Context-window exhaustion turn `T* = floor((W-p)/g)+1` = 253 for W=128k; boundary verified
  (turn 253 fits, 254 overflows → motivates 24 compaction). PASS.
- Per-step retry attempts under a step deadline = floor(30/10)=3 (reuse 18); loop worst-case
  wall-clock = max_steps*step_deadline = 600s. PASS.

## Reused (line-verified Part I/II) — mechanisms, not re-derived
- 04 scheduler / event loop; 10 nginx event loop; 17 consumer poll loop → the loop SHAPE (§1).
- 09 the log → the transcript is an append-only log (§3) → free durability/replay (26) + trace (31).
- 13 capacity/sizing → the economics framing (§6); 18 timeout/retry/deadline/budgets → termination
  + per-step retry (§4, §6); 20 tail/blast radius → step-tail + failure isolation (§5).
- 11 → halting/livelock intuition (§4: termination is bounded externally, not predicted).
- 17 idempotency / exactly-once-effect → side-effecting tool double-apply fix (§5).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Chain-of-Thought (Wei et al., NeurIPS 2022, arXiv 2201.11903) — the open-loop contrast; not
  fetched this session (arxiv now 200 — fetchable next session).
- "sense-decide-act" control-loop lineage (classic control theory; Brooks subsumption; BDI agents)
  — author synthesis grounded in 04/17 + ReAct; not separately primary-sourced.
- Reflexion (Shinn et al., 2023, arXiv 2303.11366) self-reflection loop — deferred to 25/31.
- Provider agent-loop / tool-use docs (OpenAI, Anthropic) — deferred to 23/29.

## Verdict
22 is honest and foundation-appropriate: the loop definition + grounding result are VERIFIED
against ReAct; the loop economics (quadratic token growth, budgets, window exhaustion, per-step
retry) are RECOMPUTED; the loop shape + plumbing are REUSED from line-verified 04/09/13/17/18/20.
Residual `[UNVERIFIED]` are adjacent papers/docs, none load-bearing for the loop itself. Reconcile
into `_research.md`.
