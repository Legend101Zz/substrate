# Session log

Append-only, reverse-chronological. Each entry: shipped / decisions / stopped-at.

## 2026-06-08 — Phase 1 deep research (Wave 1; FORCED PARTIAL STOP — spend limit)
- shipped: Wave 1 research for foundations 01–03. Fanned out 7 `researcher` subagents in parallel
  (general-purpose + researcher persona — the only available agent type with web tools), one per
  source cluster:
  - 01: nand2tetris+Petzold+Scott (13 srcs) · Ben Eater SAP-1 + CS:APP (10 srcs)
  - 02: Missing Semester+TLCL+Bash manual (19 srcs) · shell internals+brennan+xv6+CodeCrafters (11 srcs)
  - 03: CS144/Minnow+RFC9293/6298 (9 srcs) · Kurose+Beej+E2E paper (18 srcs) · Stevens+HPBN+TLS1.3 (8 srcs)
  Validated all 7 against RESEARCH_PROTOCOL (6 sections, primary-sources-first, [UNVERIFIED] flags) —
  all pass. Reconciled each sub-course's clusters into `<subcourse>/_research.md`. Expanded
  RESEARCH_INDEX.md (Minnow-vs-Sponge, RFC 9293/6298/8446/9000/9114, brennan.io, GNU libc job-control,
  SAP-1/Malvino, gaia.cs.umass free companion, hpbn.co free, End-to-End paper, CUBIC/BBR, XarkLabs VHDL).
- decisions: ADR-001 (per-cluster files reconciled by brain to avoid parallel-write clobber);
  ADR-002 (spend limit hit mid-wave → forced stop, `factchecker` DEFERRED to next session).
- stopped-at: END OF WAVE 1, blocked by monthly spend limit ("You've hit your monthly spend limit").
  Phase 1 is ~3 of ~50 sub-courses deep. NOT a "corpus done" stop — an external blocker. No chapters
  written. Resume needs the spend limit raised (claude.ai/settings/usage), then:
  (1) run `factchecker` on Wave 1 load-bearing claims, (2) Wave 2 = sub-courses 04, 05, 06.
  Awaiting user: raise limit + sign-off on the resume plan before continuing.

## 2026-06-08 — Phase 0 bootstrap
- shipped: scaffolded the project — meta constitution files, subagent definitions,
  living-state files, README; initialized git and committed as "scaffold".
- decisions: none beyond following START_HERE.md Phase 0 verbatim.
- stopped-at: end of Phase 0. Awaiting "go" to begin Phase 1 (deep research). No research
  or course content written yet.
