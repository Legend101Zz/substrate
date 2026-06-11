# 25 · memory-short-term-long-term-and-safety — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 25 is what 24's compactor **externalizes
> to**: the memory tier that holds evicted content and pages it back on demand. Bespoke structure:
> a **memory-hierarchy walkthrough** (tiers → paging → retrieval economics → consolidation →
> safety). Full depth: `_research_memory-short-term-long-term-and-safety.md`. Math: `_recompute.py`
> (13/13). Primaries: MemGPT (arXiv 2310.08560) + Reflexion (arXiv 2303.11366). Factcheck:
> `_factcheck_phase1.md` (0 blockers).

## 1. The one idea
**Agent memory is a storage hierarchy, not a database feature.** The window is fast/tiny/volatile
(RAM); everything else is slow/large/persistent (disk). The job is deciding what's resident now,
what spills, and what pages back — the same paging/AMAT math as 04/06/08, over tokens. 25 adds what
24 lacked: a **persistent** tier (sets up 26) and **safety** (persistent memory is a long-lived
attack surface → 33).

## 2. The taxonomy (structure-bearing)
**Working/short-term** = in-window scratchpad + self-editable working block (volatile, 24-budgeted).
**Episodic** = append-only log of past trials/experiences (reuse 09; Reflexion's reflection buffer).
**Long-term/semantic** = distilled facts in a vector store, similarity-retrieved (→30). **Procedural**
= learned skills (→29). Hierarchy map: working=L1; episodic+long-term=disk; retrieval=the page fault.

## 3. Primaries
- **MemGPT (VERIFIED) — memory as an OS pager.** "virtual context management ... drawing inspiration
  from hierarchical memory systems in traditional operating systems ... paging between physical
  memory and disk." **Main context** (prompt tokens, in-context) vs **external context** ("analogous
  to disk"); external data "must always be explicitly moved into main context." Main splits into
  "system instructions, working context, and a FIFO queue." The pager is **function calls** (reuse
  23). → an agent's memory subsystem *is* an OS pager (04) with tools as load/store.
- **Reflexion (VERIFIED) — memory as learning.** Reinforce agents "not by updating weights, but ...
  through linguistic feedback": verbally reflect on feedback, store reflective text in an "episodic
  memory buffer" to improve "subsequent trials." 91% vs 80% HumanEval. → the closed-loop sibling of
  22/24: persist a self-critique between episodes; reading it back is the learning step.

## 4. The hierarchy economics (RECOMPUTED — headline)
Memory = **AMAT (04/06) over tokens.** Main context is a fixed sub-budget (MemGPT 8k = 1k sys + 2k
working + 5k FIFO). Resident set is **0.1%** of everything stored (100 of 100,000) → paging is
mandatory. Retrieval costs k·c tokens pulled and re-billed every turn (22). **Effective cost =
miss_rate × miss_penalty**; raising the hit rate 0.80→0.95 cuts effective memory cost **4×** — a
good eviction/retrieval policy is worth as much as a bigger window. Consolidation writes a
10×-smaller summary so the long-term store grows **O(T) on disk, not O(T²) in-window**. Eviction
sizing is 06/08 verbatim (max resident = ⌊W_w/c⌋).

## 5. Safety: persistence changes the threat model (RECOMPUTED — motivates 33)
A **context** error is transient (gone at next compaction); a **memory** error is **persistent and
re-amplified on every future retrieval**. Recomputed: one poisoned long-term item is re-used ~15×
over 50 queries — **one write, many reads.** Therefore: validate memory writes at write-time
(provenance/trust boundary, like 03/23 input validation); treat injected/retrieved content as
untrusted before it's consolidated (23 §3 → 33); apply TTL/invalidation to stale memory (memory is
a cache of the world, 08/16); govern PII/right-to-be-forgotten on the persistent tier (07/15).

## 6. Failure modes
Overflow→paging · thrash (working set ≫ budget, 06/08) · poisoned/stale memory (→§5, 33) · retrieval
miss (→30 ranking) · consolidation loss (→24 over-compaction) · cross-session contamination
(→isolation, 33). **All storage-system failures, not model failures.**

## 7. Build-your-own
Add a **memory manager** to the 24 loop: tiers (working block + episodic log (09) + long-term
vector store), function-call pagers (`memory.search/write`, reuse 23), eviction policy (06/08),
consolidation (24 compactor → summaries/reflections to long-term), write-time validation (33).
Break it: no validation → poison persists; no eviction → thrash; no consolidation → O(T²) returns.
Fourth harness upgrade (loop → tools → context → **memory** → subagents → budgets).

## 8. Provenance summary
- **VERIFIED primaries:** MemGPT (arXiv 2310.08560), Reflexion (arXiv 2303.11366) —
  `meta/fetched_primaries/`, receipt `_VERIFIED_2026-06-10_agentic.md`.
- **RECOMPUTED:** `_recompute.py` (13/13) — tier partition, resident fraction, recall cost, AMAT,
  consolidation/disk growth, poisoning blast radius, eviction sizing.
- **REUSED:** 04, 06, 08/16, 09, 07/15, 22, 23, 24.
- **`[UNVERIFIED]` carry-forward:** vector/embedding retrieval (→30); memory vendor frameworks;
  cognitive-science memory taxonomy; injection-via-memory + privacy defenses (→33); deeper
  MemGPT/Reflexion benchmark tables. None load-bearing for the hierarchy model.

---
**25 reconciled.** Next in dependency order: **26-state-persistence-and-resume** (the persistent
tier from §1 made durable + replayable; ↔ 15 replication/durability + 09 the log + the 22
transcript-as-log).
