# 25 · memory-short-term-long-term-and-safety — research brief (full depth)

> Phase-1 research brief (NO course prose; briefs only). 25 is what 24's compactor **externalizes
> to**. 24 proved compaction converts 22's **O(T²) → O(T)** by capping the in-window transcript;
> but evicted content can't just be deleted — it is **paged out** to a memory tier and **paged back
> in** on demand. That is the OS virtual-memory / cache hierarchy (04/06/08) over tokens. Bespoke
> structure: a **memory-hierarchy walkthrough** (tiers → paging → retrieval economics → consolidation
> → safety), NOT abstract clusters. Math: `_recompute.py` (13/13). Primaries: MemGPT (Packer et al.,
> 2023, arXiv 2310.08560) + Reflexion (Shinn et al., NeurIPS 2023, arXiv 2303.11366). Factcheck:
> `_factcheck_phase1.md`.

---

## 0. Scope and the one-sentence thesis
**Agent memory is a storage hierarchy, not a database feature.** The in-context window is fast,
tiny, and volatile (RAM); everything else is slow, large, and persistent (disk). The whole job is
deciding *what lives in the fast tier right now*, *what spills to the slow tier*, and *what gets
paged back* — under the same budget pressure as 24 and with the same paging math as 04/06/08. 25
adds two things 24 didn't: (1) a **persistent** tier that survives across loops/sessions (sets up
26), and (2) **safety**, because persistent memory is a long-lived attack surface (sets up 33).

Two layers:
- **Intuitive:** the model only "remembers" what's on the desk (window). Memory is the filing
  cabinet behind the desk: you file things you'll need later and fetch them back when relevant.
- **Mechanism:** main context = prompt tokens (RAM); external context = vector/recall/archival
  store (disk); a controller (function calls) moves data between them. Reading costs tokens
  (re-billed every turn, 22); the resident set is a tiny fraction of everything stored → paging is
  mandatory.

---

## 1. The taxonomy of agent memory (structure-bearing)
- **Working / short-term memory** — the scratchpad inside the window: the current Thought/Action/
  Observation transcript (22) + an editable working-context block. Volatile; bounded by 24's
  budget. MemGPT's "working context" is *self-editable* (the model writes its own notes).
- **Episodic memory** — a log of past *experiences/trials* (what happened, what worked). Reflexion's
  "episodic memory buffer" of self-reflections lives here. Append-only → reuse 09 (the log).
- **Long-term / semantic memory** — distilled facts/knowledge persisted across sessions, usually in
  a vector store, retrieved by similarity (handoff to 30 RAG for the retrieval mechanism).
- **Procedural memory** — learned skills/routines (handoff to 29 skills).
Mapping to the hierarchy: working = registers/L1; episodic+long-term = disk; retrieval = the page
fault that pulls a line back into the fast tier.

---

## 2. Primary 1: MemGPT — virtual context management (VERIFIED)
MemGPT is the load-bearing primary because it *names the design as an OS*. VERIFIED verbatim from
`meta/fetched_primaries/memgpt-2310.08560.txt`:
- The thesis: "**virtual context management, a technique drawing inspiration from hierarchical
  memory systems in traditional operating systems which provide the illusion of an extended virtual
  memory via paging between physical memory and disk**." → memory = paging, full stop.
- The two tiers: "**Main context** consists of the LLM prompt tokens—anything in main context is
  considered in-context" vs "**external context** (analogous to disk memory/disk storage)"; external
  data "**must always be explicitly moved into main context in order**" to be used. → the resident/
  non-resident split (recompute §2).
- Main context is itself partitioned: "**system instructions, working context, and a FIFO queue**"
  (recompute §1).
- The controller is **function calls**: "MemGPT uses functions to move data between main context and
  external context (the archival and recall storage databases)" — i.e. the agent pages its own
  memory via tools (reuse 23). It can chain calls with `request_heartbeat=true` (immediate
  follow-up inference).
- Motivation matches 24: "limited fixed-length context"; "long-context models struggle to utilize
  additional context effectively" (the position/"lost-in-the-middle" pressure from 24 §6) — so the
  fix is *better management*, not just a bigger window.

Teaching takeaway: an agent's memory subsystem is literally an OS pager (04) with an LLM as the CPU
and tools (23) as the load/store instructions.

---

## 3. Primary 2: Reflexion — memory as learning signal (VERIFIED)
Reflexion is the second primary because it shows memory isn't just storage — it's *how an agent
improves without weight updates*. VERIFIED verbatim from
`meta/fetched_primaries/reflexion-2303.11366.txt`:
- "reinforce language agents **not by updating weights, but instead through linguistic feedback**.
  ... agents **verbally reflect on task feedback signals, then maintain their own reflective text in
  an episodic memory buffer** to induce better decision-making in subsequent trials." → learning =
  writing the right thing to episodic memory and reading it back next trial.
- It is the closed-loop sibling of 22/24: ReAct grounds reasoning with observations; Reflexion
  grounds *future* reasoning with a persisted *self-critique* (a memory write between episodes).
- Result anchor: "91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previous
  state-of-the-art GPT-4 that achieves 80%." → memory hygiene buys real capability.
Connection: Reflexion's reflections are exactly the kind of distilled summary 24's compactor writes
to the long-term tier (recompute §5) — except their *content* is a lesson, not a transcript digest.

---

## 4. The hierarchy economics (RECOMPUTED — the headline math)
Memory is the **memory-hierarchy AMAT (04/06) over tokens**:
- **Main context is a fixed budget, sub-partitioned** (recompute §1): MemGPT's 8k splits into
  system (1k) + working (2k) + FIFO (5k); tiers must sum ≤ budget.
- **Resident set is tiny** (recompute §2): 5000-tok FIFO holds 100 items of 50 tok out of 100,000
  stored = **0.1% resident** → paging is mandatory, not optional.
- **Retrieval has a token cost** (recompute §3): a recall of k=5 items × 50 = 250 tok pulled into
  main context — re-billed every subsequent turn (22) — and must fit headroom or evict (06/08).
- **Effective cost = miss_rate × miss_penalty** (recompute §4 — AMAT shape): at 80% hit rate,
  ~70 tok/access avg; raising the hit rate 0.80→0.95 cuts effective memory cost **4×** → a good
  eviction/retrieval policy is worth as much as a bigger window.
- **Consolidation keeps disk O(T), not in-window O(T²)** (recompute §5): the compactor writes a
  10×-smaller summary to long-term store; over 200 turns the disk store grows linearly (9600 tok,
  off the critical path) while the resident set stays bounded.
- **Eviction sizing reuses 06/08 directly** (recompute §7): max resident working items =
  ⌊W_w/c⌋ = 40; access #41 misses → recall.

---

## 5. Safety: memory is a persistent attack surface (RECOMPUTED §6 — motivates 33)
The defining difference from 24: a context error is **transient** (gone at next compaction); a
**memory** error is **persistent** and **re-amplified on every future retrieval**. Recomputed: one
poisoned long-term item with a 30% per-query recall probability is re-used ~15× over 50 future
queries — *one write, many reads.* Consequences (handoff to 33):
- **Memory writes need validation + provenance** (who/what wrote this, is it trusted) — write-time
  is the cheap place to stop poisoning, exactly like input validation at a trust boundary (03/23).
- **Prompt injection can plant memories** — untrusted tool/retrieved content (23 §3) that gets
  summarized into long-term memory persists the attack.
- **Privacy / PII retention** — persistent memory is a data-governance surface (right-to-be-
  forgotten, encryption at rest — reuse 07/15 durability + the project's PII rules).
- **Stale memory** — a once-true fact that's now wrong; needs TTL/invalidation (reuse 08/16 cache
  invalidation — memory is a cache of the world).

---

## 6. Failure modes (tie-back to 22 table)
Context overflow handled by paging (→§4) · cache thrash (retrieval churn when working set ≫ budget,
06/08) · poisoned/stale memory (→§5, 33) · retrieval miss (relevant memory not surfaced → 30
ranking) · consolidation loss (summary drops the needed fact → 24 over-compaction) · cross-session
contamination (one user's memory leaks to another → isolation, 33). **All are storage-system
failures, not model failures.**

---

## 7. Build-your-own (toward the 28 capstone)
Add a **memory manager** to the 24 loop: tiers (working block + episodic log (09) + long-term
vector store), function-call pagers (`memory.search`, `memory.write` — reuse 23), an eviction policy
(LRU/LFU on working items, 06/08), a consolidation step (24 compactor writes summaries/reflections
to long-term), and write-time validation (33). Break it: drop validation → poison persists; drop
eviction → thrash; drop consolidation → O(T²) returns. Fourth harness upgrade (loop → tools →
context → **memory** → subagents → budgets).

---

## 8. Sources & provenance
- **VERIFIED primaries:** MemGPT (arXiv 2310.08560) — `memgpt-2310.08560.{pdf,txt}`; Reflexion
  (arXiv 2303.11366) — `reflexion-2303.11366.{pdf,txt}`. Both in `meta/fetched_primaries/`; receipt
  in `_factcheck_phase1.md`.
- **RECOMPUTED:** `_recompute.py` (13/13) — tier partition, resident fraction, recall cost, AMAT,
  consolidation/disk growth, poisoning blast radius, eviction sizing.
- **REUSED (line-verified Part I/II):** 04 (virtual memory/paging, AMAT), 06 (cache structures,
  eviction), 08/16 (caching, eviction, invalidation, TTL), 09 (the log → episodic memory), 07/15
  (durability/persistence → sets up 26), 22 (the quadratic, transcript), 23 (function-call pagers),
  24 (compaction/consolidation).
- **`[UNVERIFIED]` carry-forward (do NOT harden into prose):**
  - Vector-store/embedding retrieval mechanics (ANN, cosine sim) — deferred to 30 (RAG).
  - Specific memory frameworks (LangGraph/LangMem, Letta/MemGPT product, mem0) — vendor, not primary.
  - Cognitive-science memory taxonomy (working/episodic/semantic/procedural as used here) — standard
    framing, not separately primary-sourced beyond MemGPT/Reflexion usage.
  - Prompt-injection-via-memory defenses — deferred to 33.
  - MemGPT/Reflexion deeper benchmark tables — not fully transcribed (headline numbers only).
