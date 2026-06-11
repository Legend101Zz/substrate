# 25 · Phase-1 factcheck — memory-short-term-long-term-and-safety

> Method (same discipline as 13-24): every load-bearing claim is either (a) RECOMPUTED in
> `_recompute.py` (13/13 pass), (b) VERIFIED verbatim against a primary fetched to
> `meta/fetched_primaries/`, (c) REUSED from a previously line-verified Part I/II sub-course, or
> (d) flagged `[UNVERIFIED]` and carried forward. 0 blockers.

## Bespoke structure note
Per the Part III plan: 25 is what 24's compactor externalizes to. Its brief is a **memory-hierarchy
walkthrough** (tiers → paging → retrieval economics → consolidation → safety), NOT abstract source
clusters and NOT the 13-20 four-cluster shape. Plan-sanctioned, consistent with 22/23/24.

## Primaries fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Packer et al., "MemGPT: Towards LLMs as Operating Systems", 2023 (arXiv 2310.08560) | `memgpt-2310.08560.{pdf,txt}` (13 pp) | §2/§4: memory = OS virtual-memory paging; main vs external context; main split into system/working/FIFO; function-call pagers |
| Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning", NeurIPS 2023 (arXiv 2303.11366) | `reflexion-2303.11366.{pdf,txt}` (19 pp) | §3: episodic memory buffer of self-reflections; learning without weight updates; 91% vs 80% HumanEval |

Fetch method: `curl https://arxiv.org/pdf/<id>`; text via throwaway `/tmp/pdfx-venv` (uv + pypdf),
`.code-puppy-venv` untouched. Receipt appended to `meta/fetched_primaries/_VERIFIED_2026-06-10_agentic.md`.

### Verified claims (MemGPT)
- "virtual context management, a technique drawing inspiration from hierarchical memory systems in
  traditional operating systems which provide the illusion of an extended virtual memory via paging
  between physical memory and disk" — VERIFIED verbatim (abstract). Anchors: memory = paging (§0, §2, §4).
- "Main context consists of the LLM prompt tokens—anything in main context is considered in-context"
  + external context "(analogous to disk memory/disk storage)" + data "must always be explicitly
  moved into main context" — VERIFIED verbatim (§2.1, l.145-177). Anchors: resident/non-resident
  split (§2; recompute §2-3).
- main context split into "system instructions, working context, and a FIFO queue" — VERIFIED
  verbatim (§2.1, l.182-190). Anchors: tier partition (recompute §1).
- "MemGPT uses functions to move data between main context and external context (the archival and
  recall storage databases)" + `request_heartbeat=true` chaining — VERIFIED verbatim (Fig. caption,
  l.231-234). Anchors: function-call pagers reuse 23 (§2).

### Verified claims (Reflexion)
- "reinforce language agents not by updating weights, but instead through linguistic feedback ...
  agents verbally reflect on task feedback signals, then maintain their own reflective text in an
  episodic memory buffer to induce better decision-making in subsequent trials" — VERIFIED verbatim
  (abstract, l.27-31). Anchors: episodic memory as learning signal (§1, §3).
- "91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previous state-of-the-art
  GPT-4 that achieves 80%" — VERIFIED verbatim (abstract). Anchors: memory hygiene buys capability (§3).

## Recomputed claims (`_recompute.py`, 13/13)
- Main context partitions into system+working+FIFO; tiers ≤ budget (8000=1000+2000+5000). PASS.
- Resident set tiny: 100 of 100,000 items = 0.1% → paging mandatory. PASS.
- Recall cost k·c=250 tok pulled + re-sent (22); must fit or evict (06/08). PASS.
- **Effective cost = miss_rate × miss_penalty (AMAT)**; hit 0.80→0.95 cuts cost 4×. PASS.
- Consolidation writes 10×-smaller summary; long-term store grows O(T) on disk, not O(T²) in-window. PASS.
- **Poisoning blast radius**: one poisoned item re-used ~15× over 50 queries (1 write, many reads). PASS.
- Eviction sizing: max resident = ⌊W_w/c⌋=40; #41 misses → recall (06/08). PASS.

## Reused (line-verified Part I/II)
- 04 virtual memory/paging + AMAT → the entire hierarchy model (§0, §4).
- 06 cache structures + eviction → resident-set + eviction sizing (§4, recompute §7).
- 08/16 caching + eviction + invalidation/TTL → recall economics + stale-memory invalidation (§4, §5).
- 09 the log → episodic memory append-only (§1).
- 07/15 durability/persistence → the persistent tier (sets up 26); PII at-rest (§5).
- 22 the quadratic/transcript; 23 function-call pagers; 24 compaction/consolidation → handoffs.

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Vector-store / embedding-retrieval mechanics (ANN, cosine) — deferred to 30 (RAG).
- Memory product frameworks (Letta/MemGPT product, LangMem, mem0) — vendor, not primary.
- Cognitive-science memory taxonomy (working/episodic/semantic/procedural) — standard framing;
  grounded here only as far as MemGPT/Reflexion use it.
- Prompt-injection-via-memory defenses + privacy/right-to-be-forgotten mechanics — deferred to 33.
- MemGPT/Reflexion deeper benchmark tables — headline numbers only transcribed.

## Verdict
25 is honest and hierarchy-appropriate: the design (memory = OS paging; main vs external; function-
call pagers; episodic memory as learning signal) is VERIFIED against MemGPT + Reflexion; the
economics (tier partition, resident fraction, recall cost, AMAT, consolidation, poisoning blast
radius, eviction sizing) are RECOMPUTED; the mechanisms (paging, AMAT, eviction, invalidation, the
log, durability) are REUSED from line-verified 04/06/08/09/15/22/24. Residual `[UNVERIFIED]` are
retrieval mechanics (→30), vendor frameworks, and injection defenses (→33), none load-bearing for
the hierarchy model. Reconcile into `_research.md`.
