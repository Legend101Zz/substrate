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
