# 25 — Memory: Short-Term, Long-Term, and Safety · _structure.md

**Identity:** what 24's compactor EXTERNALIZES to — the memory tier that holds evicted content and
pages it back on demand. The one idea: **agent memory is a storage hierarchy, not a database feature.**
The window is fast/tiny/volatile (RAM); everything else is slow/large/persistent (disk).

**Bespoke shape — "a memory-hierarchy walkthrough" (tiers → paging → retrieval economics →
consolidation → safety).** NOT a vector-DB tutorial. The job is the same paging/AMAT math as 04/06/08,
now over tokens: decide what's resident, what spills, what pages back. 25 adds what 24 lacked — a
PERSISTENT tier (sets up 26) and SAFETY (persistent memory is a long-lived attack surface → 33). Two
primaries: MemGPT (memory as an OS pager) + Reflexion (memory as learning). The headline is the safety
asymmetry: a context error is transient, a memory error is persistent and re-amplified on every
retrieval (one write, many reads). Math recomputed (13/13). Fourth harness upgrade.

## Dependency position
- **Depends on:** 24 (the compactor that externalizes here), 04 (OS paging / virtual memory), 06 (the
  structures + eviction sizing), 08/16 (AMAT, cache eviction, memory-as-cache-of-the-world TTL), 09
  (episodic = append-only log), 07/15 (PII/right-to-be-forgotten governance), 22 (the quadratic),
  23 (function-call pagers).
- **Feeds into:** 26 (the persistent tier made durable + replayable), 30 (long-term/semantic =
  similarity-retrieved vector store), 29 (procedural = learned skills), 33 (memory as a long-lived
  attack surface — the safety handoff), 31 (consolidation loss shows up in eval).
- **Appendix links DOWN:** N-math (AMAT), M-agentic-papers (MemGPT/Reflexion). 25 owns the hierarchy
  model + the safety asymmetry.

## Chapter specs (3–5 lines each)
1. **The one idea: memory is a storage hierarchy** — window = fast/tiny/volatile (RAM); everything else
   = slow/large/persistent (disk). The job is the same paging/AMAT math as 04/06/08, over tokens. 25
   adds a persistent tier (→26) and a long-lived attack surface (→33).
2. **The taxonomy** — working/short-term = in-window scratchpad + self-editable working block (volatile,
   24-budgeted); episodic = append-only log of past trials (09; Reflexion's reflection buffer);
   long-term/semantic = distilled facts in a vector store, similarity-retrieved (→30); procedural =
   learned skills (→29). Map: working=L1; episodic+long-term=disk; retrieval=the page fault.
3. **MemGPT: memory as an OS pager** — VERIFIED: "virtual context management ... paging between physical
   memory and disk." Main context (in-context: system instructions + working context + a FIFO queue) vs
   external context ("analogous to disk"; must be explicitly moved into main). The pager is FUNCTION
   CALLS (23). → an agent's memory subsystem IS an OS pager (04) with tools as load/store.
4. **Reflexion: memory as learning** — VERIFIED: reinforce agents "not by updating weights, but ...
   through linguistic feedback" — verbally reflect, store reflective text in an episodic buffer to
   improve subsequent trials (91% vs 80% HumanEval). The closed-loop sibling of 22/24: persist a
   self-critique between episodes; reading it back is the learning step.
5. **The hierarchy economics: AMAT over tokens** — main context is a fixed sub-budget (MemGPT 8k = 1k
   sys + 2k working + 5k FIFO); resident set ≈ 0.1% of everything stored → paging is MANDATORY.
   Effective cost = miss_rate × miss_penalty; raising the hit rate 0.80→0.95 cuts effective memory cost
   4× (a good retrieval policy is worth as much as a bigger window). Consolidation writes a 10×-smaller
   summary → long-term grows O(T) on disk, not O(T²) in-window. Eviction sizing = 06/08 verbatim
   (max resident = ⌊W_w/c⌋).
6. **Safety: persistence changes the threat model (motivates 33)** — a context error is transient (gone
   at next compaction); a memory error is PERSISTENT and re-amplified on every future retrieval
   (recomputed: one poisoned item re-used ~15× over 50 queries — ONE WRITE, MANY READS). Therefore:
   validate memory writes at write-time (provenance/trust boundary, like 03/23); treat injected/retrieved
   content as untrusted before consolidation (→33); TTL/invalidate stale memory (memory is a cache of the
   world, 08/16); govern PII/right-to-be-forgotten on the persistent tier (07/15).
7. **Failure modes** — overflow→paging · thrash (working set ≫ budget, 06/08) · poisoned/stale memory
   (→§6, 33) · retrieval miss (→30 ranking) · consolidation loss (→24 over-compaction) · cross-session
   contamination (→isolation, 33). All storage-system failures, not model failures.

## Paired build lab (/build → memory-manager stage of own-coding-agent-harness, 28)
Add a memory manager to the 24 loop: tiers (working block + episodic log (09) + long-term vector store),
function-call pagers (`memory.search/write`, reuse 23), eviction policy (06/08), consolidation (24
compactor → summaries/reflections to long-term), write-time validation (33). Break it: no validation →
poison persists; no eviction → thrash; no consolidation → O(T²) returns. Fourth harness upgrade.

## Diagrams needed
- The memory hierarchy (window=RAM/L1 → episodic+long-term=disk; retrieval=page fault) over tokens.
- The taxonomy (working / episodic / long-term-semantic / procedural) + downstream owners.
- MemGPT pager: main context (sys + working + FIFO) ↔ external context, moved by function calls.
- Reflexion loop: trial → reflect → episodic buffer → improved next trial.
- AMAT over tokens; hit-rate 0.80→0.95 = 4× cheaper; consolidation O(T) disk vs O(T²) in-window.
- The safety asymmetry: transient context error vs persistent memory error (one write → ~15 reads).

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **VERIFIED primaries:** MemGPT (arXiv 2310.08560) + Reflexion (arXiv 2303.11366);
  `meta/fetched_primaries/`, receipt `_VERIFIED_2026-06-10_agentic.md` — pager quotes, FIFO/working
  split, linguistic-feedback learning, 91% vs 80%.
- **RECOMPUTED (13/13):** tier partition, resident fraction, recall cost, AMAT, consolidation/disk
  growth, poisoning blast radius, eviction sizing.
- **`[UNVERIFIED]` carry-forward (none load-bearing for the hierarchy model):** vector/embedding
  retrieval (→30); memory vendor frameworks; cognitive-science memory taxonomy; injection-via-memory +
  privacy defenses (→33); deeper MemGPT/Reflexion benchmark tables. Teach the hierarchy now; do NOT
  harden retrieval internals or vendor framework specifics until 30/33.
- **Boundary discipline:** durability/replay of the persistent tier → 26; vector retrieval/ranking →
  30; procedural skills → 29; memory-poisoning/privacy defenses → 33; cache mechanics → 08/16; OS paging
  → 04; AMAT math → appendix N. 25 owns the hierarchy + the safety asymmetry.
