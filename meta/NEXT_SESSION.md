# NEXT_SESSION — resume here

Single source of truth for "where we are + what to run next." Update this at the end of every
session alongside PROGRESS.md and SESSION_LOG.md. (Detailed history lives in SESSION_LOG.md;
scope/process decisions in DECISIONS.md.)

Last updated: 2026-06-09 · Phase: 1 (deep research) · Stop reason: spend limit (ADR-002)

---

## ⛔ BLOCKER (clear this first)
Account hit its **monthly spend limit** mid–Wave 1 — any subagent fan-out (`researcher` AND
`factchecker`) fails until it's raised at **claude.ai/settings/usage**. Don't retry dispatches
before then; you'll only burn partial budget. See ADR-002.

---

## ✅ Things DONE
- **Phase 0** — scaffold + constitution files + subagent personas + living-state files; git
  initialized. (commits `ad7dfc8`, `05fd114`)
- **Phase 1 / Wave 1 — foundations 01, 02, 03 researched** (commit `5028386`). 7 `researcher`
  subagents fanned out in parallel (one per source cluster), all validated against
  RESEARCH_PROTOCOL (6 sections, primary-sources-first, `[UNVERIFIED]` flags), all accepted:
  - 01 computers-from-first-principles — `_research_nand2tetris-petzold.md` (13 srcs),
    `_research_eater-csapp.md` (10 srcs) → reconciled `_research.md`.
  - 02 terminal-shell-and-dev-environment — `_research_missing-semester-tlcl.md` (19 srcs),
    `_research_shell-internals-build.md` (11 srcs) → reconciled `_research.md`.
  - 03 networking-from-first-principles — `_research_cs144-sponge.md` (9), `_research_kurose-beej.md`
    (18), `_research_stevens-hpbn.md` (8) → reconciled `_research.md`.
- **RESEARCH_INDEX.md expanded** with Wave 1 finds (Minnow-vs-Sponge, RFC 9293/6298/8446/9000/9114,
  brennan.io, GNU libc job-control, SAP-1/Malvino, gaia.cs.umass free companion, hpbn.co free,
  End-to-End paper, CUBIC/BBR, XarkLabs VHDL).
- **DECISIONS.md** — ADR-001 (per-cluster files reconciled by brain to avoid parallel-write clobber),
  ADR-002 (spend limit → forced stop, factchecker deferred).
- **PROGRESS.md** seeded with all ~50 sub-courses; 01–03 marked RESEARCHING (briefs done).

## ⏳ Things LEFT
- **Factcheck debt (ADR-002):** `factchecker` has NOT run on Wave 1. Briefs self-flag the shaky
  claims as `[UNVERIFIED]` — e.g. exact SAP-1 control-word bit map / T-state tables; Eater 6502
  memory map; Scott/Petzold book figures; zsh no-word-split default; Bash *Environment* verbatim;
  CodeCrafters stage slugs; End-to-End paper page-quotes; Beej epoll depth; date-sensitive HTTP/3
  numbers + per-OS congestion-control default. Resolve these before they harden into chapters.
- **Phase 1 research remaining (~47 sub-courses):** foundations 04–12, System Design 13–21,
  Agentic 22–34, appendices A–O. All TODO in PROGRESS.md.
- **Open design question for Phase 2** (logged, not yet ADR): CS144 Minnow dropped the hand-authored
  `TCPConnection` state-machine lab — decide whether the own-tcp-ip lab models Sponge Lab 4.
- **Not started:** Phase 2 (per-sub-course `_structure.md`), any chapters. Do NOT begin until
  Phase 1 corpus is signed off.

---

## ▶️ PROMPT TO RUN NEXT (paste after raising the spend limit)

```
Rehydrate first: read START_HERE.md, then meta/CONSTITUTION.md, RESEARCH_PROTOCOL.md,
COURSE_MAP.md, RESEARCH_INDEX.md, PROGRESS.md, SESSION_LOG.md, DECISIONS.md (note
ADR-001/002) and meta/NEXT_SESSION.md. Confirm in 3–4 lines: current state, that Wave 1
(01–03) briefs are committed, and the exact plan you're about to run. Then proceed.

Continue Phase 1 deep research per RESEARCH_PROTOCOL.md:
- FIRST clear the ADR-002 debt: run `factchecker` (general-purpose + factchecker persona)
  on the most load-bearing / [UNVERIFIED]-flagged claims in 01–03's _research files.
  Record verdicts; fix or escalate any UNSUPPORTED/MISATTRIBUTED before they harden.
- THEN run Wave 2 = sub-courses 04, 05, 06. Fan out one researcher per source cluster
  in RESEARCH_INDEX, in parallel, writing _research_<cluster>.md; reconcile into each
  _research.md; validate before accepting (reject thin/uncited, re-run); expand
  RESEARCH_INDEX with new finds.
- Note: the Agent tool exposes no `researcher`/`factchecker` type — use `general-purpose`
  with the meta/subagents/*.md persona embedded inline. Each sub-course lives under
  /Users/comreton/Desktop/substrate/<id>/ (mkdir the dir first). Watch for the spend
  limit; if it recurs, consolidate + commit what's paid-for and stop, don't retry.
- Keep PROGRESS.md current (RESEARCHING in-flight). Scope changes → DECISIONS.md as ADRs.
Then continue waves: 3 (07,08,09), 4 (10,11,12). STOP at the end of the foundations
spine, commit, append a SESSION_LOG entry, update meta/NEXT_SESSION.md, and report gaps +
the proposed next batch (System Design 13–21). Do not start System-Design research or any
Phase 2 work until I sign off. No chapters.
```
