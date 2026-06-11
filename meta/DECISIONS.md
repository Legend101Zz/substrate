# Decisions (ADR log)

Every scope / ordering / cut decision, with its reasoning. Format:

## ADR-NNN <title>
- context:
- decision:
- consequences:

## ADR-001 Per-cluster research files reconciled by brain (avoid parallel-write clobber)
- context: RESEARCH_PROTOCOL says each researcher returns into `<subcourse>/_research.md`. Running
  N researchers per sub-course in parallel against one file races/clobbers it.
- decision: Each researcher writes a cluster-scoped file `_research_<cluster>.md`; the brain
  reconciles them into `<subcourse>/_research.md` (synthesis + cross-cluster reconciliation +
  consolidated sources/gaps, pointing at the cluster files for full depth).
- consequences: Faithful to the protocol's deliverable (a `_research.md` per sub-course) with no
  data loss from concurrent writes. Purely operational; no scope change.

## ADR-002 Spend limit hit mid-Wave-1 → forced partial stop; factchecker DEFERRED
- context: During Wave 1 fan-out the account hit its monthly spend limit ("You've hit your monthly
  spend limit"). 4 of 7 researchers returned self-reports; the other 3 had already written complete,
  validated briefs but failed on their final summary turn. Any further subagent dispatch
  (more researchers, AND the `factchecker`) fails until the limit is raised.
- decision: Stop fanning out. Consolidate the already-paid-for Wave 1 corpus (reconcile, expand
  RESEARCH_INDEX, commit) on the main thread. Defer the formal `factchecker` pass on load-bearing
  claims to the next session. Wave 1 briefs are marked research-complete but NOT factcheck-verified;
  every load-bearing claim that needs confirmation is flagged [UNVERIFIED] in the briefs.
- consequences: Phase 1 is ~3/50 sub-courses deep (foundations 01–03). This is a forced external
  blocker, not a "corpus is done" stop. Resume = raise limit → run `factchecker` on Wave 1 →
  Wave 2 (04,05,06). No quality gate was bypassed silently; the deferral is recorded here.

## ADR-003 Appendices are reference-only and carry NO `_structure.md`
- context: Phase 2 says "for each sub-course write `<subcourse>/_structure.md`." The appendices
  (A–O) are a different artifact class from the spine: CONSTITUTION #5 makes them reference-grade,
  info-only deep dives with NO exercises, NO build labs, and NO teaching arc — spine chapters
  cross-link DOWN into them. Each appendix's bespoke shape was already fixed during Phase 1 and
  lives in `<appendix>/_research.md` (e.g. F = "life of a row", G = "single-threaded in-memory
  machine", I = "there is no container", K = "3-stage + JIT pipeline", O = "five rented planes").
  A separate `_structure.md` would either duplicate that or invent pedagogy the appendices are
  defined NOT to have.
- decision: Phase 2 `_structure.md` files cover the 35 SPINE units (00–34) ONLY. Appendices A–O
  stay reference-only; their `_research.md` is the authoritative shape + content plan. PROGRESS.md
  marks A–O as RECONCILED (terminal for the appendix class), not PLANNED. COURSE_MAP.md records
  this scope note next to the appendix list.
- consequences: No appendix loses depth (it was never going to get a teaching structure). The
  Phase-2 deliverable count is 35 spine `_structure.md` files (batches 2a–2e), which is complete.
  If a future decision wants to add reference sub-sections or a navigation index per appendix, that
  is a new ADR. Candidate appendices P/Q/R remain proposals, add only via ADR. Purely a
  scope-clarification; no content change.

## ADR-004 03 own-tcp-ip lab = CS144 Minnow ladder + a hand-authored Sponge-Lab-4-style state machine
- context: 03's keystone build lab is "write a working TCP." Stanford CS144's CURRENT framework is
  **Minnow**, whose checks build the modules only: ByteStream → Reassembler → TCPReceiver →
  TCPSender, then check4 "Measuring the real world" (no hand-authored connection object — Minnow
  provides the `TCPPeer`/`TCPMinnowSocket` wiring). The older **Sponge** framework HAD a
  hand-written `TCPConnection` lab ("Lab 4: the summit") where students authored the full 11-state
  machine + handshake/teardown/TIME-WAIT themselves. That lab was DROPPED in Minnow. 03 wants
  learners to internalize the TCP state machine BY BUILDING IT, which Minnow alone does not cover.
  The Sponge Lab-4 handout is `[UNVERIFIED]` (404 on direct fetch; cross-checked via RFC 9293
  §3.3.2 Fig 5 + community/doxygen). Logged as "decision needed" in 03's `_research.md` and
  `_structure.md`; owed as an ADR at Phase-2 finalize.
- decision: The own-tcp-ip-stack lab = the **CS144 Minnow module ladder** (ByteStream → Reassembler
  → Receiver → Sender, cited from the github.io check1–check3 PDFs) PLUS a **hand-authored
  connection state-machine capstone modeled on Sponge Lab 4**, but specified from the RFC 9293
  §3.3.2 state diagram as the primary (not from the unfetched Sponge handout). RTO follows RFC 6298
  (CS144's simplified recs 5.1–5.6). Congestion control stays OUT of the lab (AIMD taught as mental
  model; CUBIC/BBR named only) — matching CS144 scope. Cite CS144 via `cs144.github.io` PDFs
  (the `cs144.keithw.org` mirror has a TLS cert-name mismatch).
- consequences: Learners build TCP end to end including the state machine, without depending on a
  framework that no longer ships that lab. The state-machine chapter is grounded in a VERIFIED
  primary (RFC 9293) rather than the `[UNVERIFIED]` Sponge handout — that flag stays logged and is
  upgraded only if the handout is later fetched. If we re-fetch Sponge Lab 4 and it diverges from
  our RFC-derived spec, that is a follow-up note here, not a silent change. Scope of 03's lab is now
  fixed for Phase 3 drafting.
