# Session log

Append-only, reverse-chronological. Each entry: shipped / decisions / stopped-at.

## 2026-06-10 — Phase 2 Wave 20: Batch 2e (29–34 structures) + finalize 2f–2i. **PHASE 2 COMPLETE — awaiting sign-off.**
- rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/SESSION_LOG/
  DECISIONS/NEXT_SESSION/STYLE/QUALITY_BAR; `git status --short` clean at start; checkpoint `557a69c`
  (= Batch 2d); Wave-2 milestone `4a1cc71` confirmed (commit). CWD accessible, NO `Path.cwd()`
  PermissionError; `.code-puppy-venv` untouched; no reinstall.
- **Network retried (opportunistic, still owed) — ALL still blocked:** DPR (arXiv 2004.04906) 000,
  arxiv.org/abs 000, kafka.apache.org 000, raft.github.io 000, queue.acm.org (CoDel) 403. Nothing
  healed; every `[UNVERIFIED]` carried forward verbatim, nothing erased. (RAG 2005.11401 already
  local+VERIFIED for 30.)
- **SHIPPED — Batch 2e: bespoke `_structure.md` for 29–34** (commit `402e554`), each a distinct shape:
  29 = protocol/connector walkthrough (every layer an old Part I/II law renamed; MCP-arch VERIFIED);
  30 = retrieval-pipeline (each stage a data-systems chapter re-applied + embedding primitive +
  corpus-poisoning failure; RAG VERIFIED, DPR still `[UNVERIFIED]`); 31 = trust-loop define→measure
  →grade→watch→constrain→close (SWE-bench VERIFIED; reconcile-note: upgrades 28's carried flag, kept);
  32 = cost-lifecycle account→attribute→budget→optimize→operate ("bill IS the O(T²), priced"; no new
  primary); 33 = threat-model→defence-in-depth→controlled-evolution (Greshake VERIFIED; resolves
  23/25/29/30 injection pointers to one root cause, originals kept); 34 = grand capstone design
  canvas + forced-moves decision tree + budget ledger (no new primary). Each carries dependency
  position, 3–5-line section specs, paired harness upgrade (7th–11th + capstone), diagrams-needed,
  and a sources/gaps section preserving every `[UNVERIFIED]` verbatim.
- **SHIPPED — finalize 2f–2i:**
  - **2f** COURSE_MAP.md rewritten into a FINALIZED dependency DAG (adjacency list + Mermaid +
    appendix back-edges + three reading orders; verified the number line is a valid topological sort).
  - **2g** PROGRESS.md: added authoritative Phase-2 per-chapter table (35 spine units → PLANNED with
    section counts + paired lab; 264 total section specs = the Phase-3 backlog; appendices A–O →
    RECONCILED, reference-only). Detailed Phase-1 provenance archive preserved below it (not pruned).
  - **2h** README.md refreshed: Phase 0 → "Phase 1 complete + Phase 2 spine structures complete; Phase 3
    drafting after sign-off."
  - **2i** DECISIONS.md: wrote **ADR-003** (appendices are reference-only, NO `_structure.md` by
    design — shape lives in their `_research.md`) and **ADR-004** (03 own-tcp-ip lab = CS144 Minnow
    module ladder + a hand-authored Sponge-Lab-4-style state machine specified from RFC 9293 §3.3.2,
    not the `[UNVERIFIED]` Sponge handout; congestion control out of lab scope).
- **DECISIONS:** ADR-003, ADR-004 (above). The owed CS144 Minnow-vs-Sponge decision is now resolved.
- **State preserved:** all 50 `_research.md` intact; prior Phase-2 batches 2a `c8f5e66` / 2b `7354c2d`
  / 2c `c33d627` / 2d `557a69c` untouched. NO chapters/prose written (Phase 2 gate honored).
- **MILESTONE:** **Phase 2 COMPLETE** — 35 spine `_structure.md` files (batches 2a–2e) + finalized
  COURSE_MAP DAG + per-chapter PROGRESS + README + the two owed ADRs. Next gate is **sign-off**;
  only after the user annotates and says go does Phase 3 (one chapter at a time) begin.
- **STOPPED-AT:** presented the full Phase-2 package; awaiting annotation + "go." No drafting until then.

## 2026-06-11 — Phase 1 Wave 19: APPENDICES batch 4 COMPLETE — C + D + E + O reconciled. **ALL 15 APPENDICES DONE → ENTIRE PHASE 1 CORPUS COMPLETE.**
- rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/SESSION_LOG/
  DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint at start `e2487ff`; Wave-2 milestone
  `4a1cc71` confirmed; CWD accessible, NO `os.getcwd()`/`Path.cwd()` PermissionError; `.code-puppy-venv`
  untouched; no reinstall.
- **Network retried — ALL still blocked (reuse-only wave):** kafka.apache.org / arxiv.org /
  raft.github.io / docs.python.org / llvm.org / man7.org all **000**; queue.acm.org **403**. So NO new
  primary fetched; every appendix reused line-verified spine canon (esp. 05 + appendix K) + spine math.
  Opportunistic owed fetches (Kafka paper/KIPs, DPR 2004.04906, Raft, CoDel) retried → STILL BLOCKED,
  carried `[UNVERIFIED]`, nothing hardened, nothing erased.
- **SHIPPED — 4 reference appendices (deep info only, NO exercises, bespoke shapes, CONSTITUTION #5):**
  - **C python-internals** — bespoke "life of a PyObject" (header → refcount death → the GIL that
    protects the count → self-adapting stack-VM eval loop (PEP 659) → cyclic GC). Reuses 05's
    line-verified CPython source reads + appendix K. `_recompute.py` **15/15**. 0 blockers.
  - **D javascript-v8-nodejs-internals** — bespoke "one JS value through V8, one tick through the loop"
    (hidden class → IC + Ignition→Maglev→TurboFan → scavenger/mark-compact → libuv phases + microtasks).
    Reuses 05's line-verified V8+libuv reads + appendix K. `_recompute.py` **13/13**. 0 blockers.
  - **E java-jvm-internals** — bespoke "life of a class through the JVM" (load → verify (StackMapTable
    single pass) → init <clinit>-once → interp→C1→C2+deopt → safepoints + G1/ZGC). Reuses 05's
    line-verified HotSpot reads + appendix K. `_recompute.py` **13/13**. 0 blockers.
  - **O cloud-infra-basics** — bespoke "cloud = five rented planes" (compute/storage/network/identity/
    control-plane); vendor-neutral, NO vendor number load-bearing. Reuses spine 13/20/15 + appendices
    I/J/L. `_recompute.py` **14/14**. 0 blockers.
- **C/D/E are the three concrete instances of appendix K's generic compiler/JIT pipeline + spine 05's
  runtime canon, each with a bespoke (non-K, non-four-cluster) shape; O is the cloud-primitives
  reference that maps every cloud plane DOWN to a spine primitive + the one new forcing function
  (meter + blast-radius).**
- Extraction: no PDF this wave; no venv created; `.code-puppy-venv` untouched.
- **DECISIONS:** none new (followed the Wave-16/17/18 appendix pattern: bespoke per-appendix shape,
  recompute+factcheck+reconcile, reuse-only since network blocked, carry-forward all gaps). No ADR.
- **State preserved:** SPINE 01-34 reconciled; appendices N/L/M/F/G/H/K/A/B/I/J untouched and intact.
- **MILESTONE:** Appendices now **15/15**. Combined with SPINE 01-34, **the entire Phase 1 research
  corpus is COMPLETE.** Next gate is **Phase 2** (per-sub-course `_structure.md` proposals) — which
  **requires sign-off before any drafting** (CONSTITUTION / START_HERE Phase 2). No chapters written.
- **STOPPED-AT:** one clean factchecked checkpoint after C+D+E+O; Phase 1 done; awaiting Phase 2 go.


- rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/SESSION_LOG/
  DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint at start `84d2638`; CWD accessible,
  NO `os.getcwd()`/`Path.cwd()` PermissionError; `.code-puppy-venv` untouched; no reinstall.
- **Network retried — ALL still blocked (reuse-only wave):** kafka.apache.org / arxiv.org /
  raft.github.io / llvm.org / gcc.gnu.org / man7.org / docs.python.org all **000**; queue.acm.org
  **403**. So NO new primary fetched this wave; every appendix reused line-verified spine canon +
  local primaries. Opportunistic owed fetches (Kafka paper/KIPs, DPR 2004.04906, Raft, CoDel) retried
  → STILL BLOCKED, carried `[UNVERIFIED]`, nothing hardened.
- **SHIPPED — 5 reference appendices (deep info only, NO exercises, bespoke shapes, CONSTITUTION #5):**
  - **K compilers-interpreters-and-jit** — bespoke 3-stage+JIT pipeline (front-end → stack/register VM
    → SSA middle-end → codegen/regalloc → JIT profile/specialize/guard/deopt). Reuses 05's line-verified
    CPython/V8/HotSpot/Crafting-Interpreters reads + 06. `_recompute.py` **15/15**. 0 blockers. Commit `41aa4aa`.
  - **A computer-architecture** — bespoke performance ladder (the correct-but-slow CPU 01 built → cache/
    AMAT → pipelining/hazards → branch prediction → superscalar/OOO/ILP → VM/TLB → coherence). Reuses
    01's nand2tetris+CS:APP+Eater reads + 06/13. `_recompute.py` **15/15**. 0 blockers. Commit `2f3020a`.
  - **B linux-internals** — bespoke xv6→Linux→isolation diff (clone/COW → CFS/EEVDF → buddy/slab/page-
    cache → epoll/io_uring → **namespaces+cgroups substrate**). Reuses 04's xv6+TLPI+kernel-source reads
    + A. `_recompute.py` **14/14**. 0 blockers. **Establishes the ns+cgroups substrate for I/J.** Commit `ecebe1e`.
  - **I docker-containers-cgroups-namespaces** — bespoke "there is no container" teardown (process + ns
    + cgroups + overlayfs + caps/seccomp; reassemble in ~4 syscalls). Reuses just-reconciled B + 04/A/03.
    `_recompute.py` **12/12**. 0 blockers. Commit `26ffa0d`.
  - **J kubernetes-internals** — bespoke "loops all the way down" (reconciliation loops over I's container
    unit: store→schedule→run→expose→heal→roll; etcd=Raft). Reuses appendix I + spine 11/15/20 + L.
    `_recompute.py` **13/13**. 0 blockers. **Closes the B→I→J arc.** Commit `4edc1b4`.
- Extraction: no PDF this wave; no venv created; `.code-puppy-venv` untouched.
- **DECISIONS:** none new (followed Wave-16/17 appendix pattern: bespoke per-appendix shape, recompute+
  factcheck+reconcile, reuse-only since network blocked, carry-forward all gaps). No ADR needed.
- **State preserved:** SPINE 01-34 reconciled; appendices N/L/M/F/G/H untouched and intact.
- **STOPPED-AT:** one clean factchecked checkpoint after K+A+B+I+J (preferred a clean checkpoint over
  starting shallow C/D/E/O). Remaining appendices TODO: **C, D, E, O (4/15)**. Next batch recommended:
  C-python-internals + D-v8-node-internals + E-jvm-internals (all reuse 05/K), then O-cloud-infra-basics.

## 2026-06-11 — Phase 1 Wave 17: APPENDICES batch 4 CONTINUED — F-postgres-internals + G-redis-internals + H-kafka-internals reconciled (redis.io eviction+persistence fetched/verified). Appendices now 6/15.
- rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/SESSION_LOG/
  DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint at start `a11be7b`; CWD accessible,
  NO `os.getcwd()`/`Path.cwd()` PermissionError; `.code-puppy-venv` untouched; no reinstall.
- **Network retried:** redis.io HTTP **200** (reachable!) → fetched eviction + persistence docs.
  postgresql.org / kafka.apache.org / raft.github.io / arxiv.org all **000**; queue.acm.org **403**
  (all still blocked, matching Wave 16). So F reused 07's line-verified pg source + WAL intro; H
  reused 09's line-verified Kafka 3.9 source + 17 + Nishtala; only G got NEW primaries this wave.
- **SHIPPED — 3 reference appendices (deep info only, NO exercises, bespoke shapes, CONSTITUTION #5):**
  - **F postgres-internals** — bespoke "life of a row" pipeline (page→tuple→nbtree→cost-planner→
    executor→WAL→checkpoint→REDO→MVCC→VACUUM/wraparound). WAL roll-forward/REDO + sequential-log-
    flush VERIFIED verbatim against local `postgres-wal-intro.txt`; page/planner/MVCC constants reused
    from 07's line-verified PostgreSQL master source. `_recompute.py` **14/14** (fixed page-density
    claim 66→64 after recompute caught it). `_factcheck_phase1.md` 0 blockers. Reuses 06/07/15/26/L.
  - **G redis-internals** — bespoke "single-threaded in-memory machine" tier walkthrough (event loop→
    encodings→expiration→eviction→persistence→replication→cluster). **NEW primaries FETCHED+VERIFIED**
    (redis.io 200): eviction ("Approximated LRU", `maxmemory-samples 5`) + persistence (RDB
    point-in-time; AOF everysec=1s/always=0/no=30s) — receipt `_VERIFIED_2026-06-11_redis-docs.md`.
    `_recompute.py` **14/14**. 0 blockers. Reuses 06/08/16/L/15.
  - **H kafka-internals** — bespoke "distributed-log machine" layer walkthrough (log→segments→ISR→
    HW/epochs→groups/offsets→delivery→EOS/txns→KRaft). NO new primary (kafka.apache.org 000);
    constants reused from 09's line-verified Kafka 3.9 source + 17 delivery math + Nishtala herd.
    `_recompute.py` **13/13**. 0 blockers. Reuses 09/17/11/15/L+Nishtala.
- **Opportunistic primaries (still owed) — retried, STILL BLOCKED:** Kafka paper/KIPs
  (kafka.apache.org 000), DPR arXiv 2004.04906 (arxiv 000), Raft (raft.github.io 000), CoDel
  (queue.acm.org 403). All carried `[UNVERIFIED]`, nothing hardened. Receipt for the ONE new fetch
  (redis docs) saved to `meta/fetched_primaries/`.
- Extraction: plain `curl` + stdlib HTML strip (no PDF this wave); NO venv created;
  `.code-puppy-venv` untouched.
- **DECISIONS:** none new (followed Wave-16 appendix pattern: bespoke per-appendix shape, recompute+
  factcheck+reconcile, fetch only reachable primaries, carry-forward all gaps). No ADR needed.
- **State preserved:** SPINE 01-34 reconciled; appendices N/L/M untouched and intact.
- **STOPPED-AT:** one clean factchecked checkpoint after F+G+H. Remaining appendices TODO:
  A,B,C,D,E,I,J,K,O (9/15). Next batch recommended: K-compilers-and-jit (reuse 05),
  A-computer-architecture (reuse 01), B-linux-internals (reuse 04), then I/J/C/D/E/O.

## 2026-06-11 — Phase 1 Wave 16: APPENDICES batch 4 OPENED — N-math-for-systems + L-consensus-replication-and-transactions + M-ai-agent-memory-tools-and-evaluation reconciled (Lamport Paxos + Byzantine Generals fetched/verified).
- rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/SESSION_LOG/
  DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint was `c640d59`; CWD accessible, no
  `os.getcwd()`/`Path.cwd()` PermissionError; `.code-puppy-venv` untouched.
- **DISCREPANCY HANDLED (again):** the launch prompt described the Wave-13 baseline ("22-30
  reconciled; 31 NEXT untouched; run 31→34"), but disk/PROGRESS/NEXT_SESSION showed Waves 14-15 had
  ALREADY reconciled 31, 32, 33, 34 (commits `31b7377`, `c640d59`). Per the constitution ("never
  guess — rehydrate from PROGRESS.md") I STOPPED before touching 31, reported the conflict, and asked
  the user. User chose **(A) start Appendices batch 4** — the true next work per NEXT_SESSION Wave 16.
  No committed factchecked work was overwritten.
- shipped: **THREE reference appendices reconciled** (deep info only, NO exercises per CONSTITUTION
  #5; bespoke per-appendix structures, NOT the four-cluster/canvas shapes):
  - **N-math-for-systems** — formula compendium by question (queueing/capacity → hashing/
    probabilistic → tail/availability → statistics). `_recompute.py` **20/20** (Little's Law; M/M/1;
    utilization wall 1/(1−ρ); birthday/collision; consistent hashing K/N; Bloom k*=(m/n)ln2 fp 0.82%;
    HLL 1.04/√m; fan-out tail 63.4%; serial/parallel availability; Amdahl/USL; eval CI ~1068). NO new
    primary (standard results, re-derived not asserted; Tail-at-Scale reused for fan-out). Reuses
    06/07/08/13/14/15/17/18/19/20/27/31.
  - **L-consensus-replication-and-transactions** — fault-model ladder (crash n≥2f+1 → Byzantine
    n≥3f+1 → quorum W+R>N → CAP/PACELC → 2PC/commit-wait → isolation). **NEW primaries
    FETCHED+VERIFIED: Lamport Paxos (`lamport-paxos.txt`) + Byzantine Generals (`lamport-byz.txt`)**
    from lamport.azurewebsites.net (HTTP 200) — receipt `_VERIFIED_2026-06-11_consensus.md`;
    extracted via throwaway `/tmp/pdfx-venv-l` (pypdf), `.code-puppy-venv` untouched. Verified
    verbatim: BFT "3m+1"/"more than two-thirds" (byz L10/156/234-5); Paxos majority+quorum+state-
    machine (paxos L18/108/131/189-193). Spanner TrueTime ε≈1-7ms + commit-wait reused
    (spanner-osdi2012 L105/448/580-588). `_recompute.py` **22/22**. **Upgrades 12's carried
    Byzantine/Paxos `[UNVERIFIED]` → LOCAL+VERIFIED.** Reuses 07/11/14/15 + Dynamo/Spanner/Gilbert-
    Lynch/Brewer/Kleppmann/Abadi.
  - **M-ai-agent-memory-tools-and-evaluation** — primitive-by-primary catalogue (memory→tools→
    reasoning→retrieval→evaluation→safety); the reference-grade companion to the Part III spine
    (22-34). **NO new primary** — all seven primaries already LOCAL+VERIFIED (MemGPT/Reflexion/
    Toolformer/ReAct/RAG/SWE-bench/Greshake). `_recompute.py` **17/17** (AMAT over tokens; resident
    0.1%; tool selection compounding; ANN ~430,043×; SWE-bench CI; pass@k vs pass^k; Condorcet judge;
    injection blast radius + defence-in-depth). Reuses 22/23/25/27/30/31/33 + 06/N.
- opportunistic primaries: Lamport Paxos+Byz fetched (host reachable). Still blocked: raft.github.io
  (000, retried) → Raft `[UNVERIFIED]` carried in L; queue.acm.org (403, CoDel) carried in 18/20.
  Did NOT fetch DPR/FAISS this session (kept the checkpoint clean; M's gaps inherited not load-bearing).
- decisions: stopped at THREE clean factchecked appendices rather than risk a thin fourth
  (F-postgres would need postgresql.org docs not yet verified this session). Prefer one clean
  checkpoint over shallow briefs (per the standing instruction).
- stopped-at: N/L/M reconciled + committed. Next batch = remaining appendices, recommended order
  **F-postgres-internals** (local Postgres-WAL + 07/15/26), **H-kafka-internals** (09/17 + Nishtala;
  retry kafka.apache.org), then A/B/C/D/E/G/I/J/K/O as material + reachable primaries allow.

## 2026-06-10 — Phase 1 Wave 15: Part III batch 3 COMPLETE — 33 safety-and-proactive-self-evolving-agents + 34 design-your-own-agentic-system reconciled (Greshake indirect-prompt-injection fetched/verified). PART III (22-34) DONE.
- rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/SESSION_LOG/
  DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint was `31b7377`; no `os.getcwd()`/
  `Path.cwd()` PermissionError (CWD accessible via OneDrive physical path).
- **DISCREPANCY HANDLED:** the launch prompt described the Wave-13 baseline ("22-30 reconciled,
  31 NEXT untouched"), but disk/PROGRESS showed Wave 14 had ALREADY reconciled 31 + 32. Per the
  constitution ("never guess — rehydrate from PROGRESS.md") + NEXT_SESSION.md, proceeded with the
  TRUE next untouched sub-course **33**, then **34**. Reported the discrepancy up front.
- shipped: **33 safety-and-proactive-self-evolving-agents RECONCILED** (the THREAT + EVOLUTION
  layer). Bespoke **threat-model → defence-in-depth → controlled-evolution walkthrough**. NEW
  primary **Greshake et al. "Not what you've signed up for: ... Indirect Prompt Injection" (AISec
  '23, arXiv 2302.12173) FETCHED+VERIFIED** — root cause "blur the line between data and
  instructions" (L33-34); retrieved prompts = arbitrary code / API control (L44-46); injection-
  method taxonomy (Passive/Active/User-driven/Hidden-multistage §3.1) + threat taxonomy (data-theft/
  fraud/intrusion/malware/manipulation/availability/**worming** §3.2) + persistence-via-memory
  (L424-448) + no-silver-bullet/"Whack-A-Mole"/alignment-insufficient stance (L1271/1273-4). The
  carried FORWARD injection `[UNVERIFIED]` pointers from **23 (tool-result) / 25 (memory) / 29
  (server) / 30 (passage)** all land here on ONE verified root cause. Self-evolution half REUSES
  local+VERIFIED **Reflexion (2303.11366)**. `_recompute.py` **15/15** (injection blast-radius
  1-write-many-reads 12→62; sandbox-as-cell 20× containment + least-privilege 4×; defence-in-depth
  0.8% escape vs 5.9% over-refusal tax; self-improve converges+gated-by-31-eval / ungated reward-
  hacks; risk-based approval gate 20× cheaper catches 100% damage; prompt-worm R0=2.0>1 vs
  0.5<1 sanitized; composed defences multiply). `_factcheck_phase1.md` 0 blockers. Reuses
  18/19/20/23/25/27/29/30/31/32.
- shipped: **34 design-your-own-agentic-system RECONCILED** (PART III CAPSTONE DESIGN CANVAS, the
  agentic 21). Bespoke **forced-moves decision-tree / design canvas**. **NO new primary** (capstone
  application, like 21). Thesis: a design is a SEQUENCE OF FORCED MOVES — task shape + arithmetic
  pick the primitives (small task forces {22}; big task forces {22,24,33,26,27,31,32}).
  `_recompute.py` **13/13** re-deriving the cross-cutting budget ledger: 22 O(T²), 24 compaction
  (per-call window vs cumulative cost kept distinct), 25 AMAT, 26 checkpoint knee I*=√(2N·c),
  27 Amdahl/join-tail/YAGNI, 31 eval CI ≈1068 tasks, 32 $, 33 defence-per-channel. `_factcheck_
  phase1.md` 0 blockers; no NEW `[UNVERIFIED]` (inherits home-course gaps). Reuses 22-33.
- PRIMARY fetched+verified to `meta/fetched_primaries/`: `greshake-injection-2302.12173.{pdf,txt}`
  (33 pp, 116,724 chars; receipt `_VERIFIED_2026-06-10_injection.md`). Extracted via throwaway
  `/tmp/pdfx-venv` (uv+pypdf from Walmart external-pypi); `~/.code-puppy-venv` NEVER touched.
- **PART III (Agentic System Design, 22-34) is COMPLETE.** With 01-12 + 13-21 complete, the entire
  **Phase-1 spine corpus (01-34) is DONE**.
- opportunistic: Kafka (kafka.apache.org 200) attempted — `/documentation/#design` returns a thin
  19KB JS-rendered shell (only 4 keyword hits), NOT a usable primary; discarded (no misleading
  receipt). Kafka paper/KIPs for 09/17 remain effectively blocked (JS-rendered). CoDel
  (queue.acm.org 403) + raft.github.io (000) retried, STILL blocked. DPR (2004.04906→30) not
  fetched (time-boxed; non-load-bearing, 30 already anchored by RAG 2005.11401).
- decisions: none structural (ADR log unchanged). Proceeded on true PROGRESS state over the stale
  launch-prompt baseline, per constitution.
- stopped-at: clean checkpoint after 33 + 34 reconciled + committed. Next batch = **Phase 1 batch 4
  (Appendices A-O)** OR Phase 2 (`_structure.md`, which STOPS for sign-off). No chapters. No
  Phase 2 started this session.

## 2026-06-10 — Phase 1 Wave 14: Part III batch 3 continued — 31 evaluation-tracing-and-guardrails + 32 cost-observability-and-ops reconciled (SWE-bench fetched/verified; 28 upgraded)
- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/PROGRESS/
  SESSION_LOG/DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint was `302f6c5`; no
  `os.getcwd()`/`Path.cwd()` PermissionError. Confirmed Wave 2 milestone `4a1cc71`, 01-12 + Part II
  13-21 COMPLETE, Part III open with 22-30 reconciled (9/13); 31 NEXT untouched.
- shipped: **31 evaluation-tracing-and-guardrails RECONCILED** (the TRUST layer). Bespoke
  **trust-loop walkthrough** (Define correct → Measure offline → Grade the un-gradeable → Watch
  live → Constrain inline → feed failures back). **SWE-bench (Jimenez/Yang et al., ICLR 2024,
  arXiv 2310.06770) FETCHED+VERIFIED** — the execution-based "is it useful" definition owed from
  28/30: "apply the generated patch ... execute the unit and system tests ... If the patch applies
  successfully and all of these tests pass we consider the proposed solution to have successfully
  resolved the issue"; "the percentage of task instances that are resolved"; tests-as-oracle
  (fail-to-pass + pass-to-pass); Claude-2 1.96%; lexical≠correctness; saturation motivation.
  Tracing REUSES the local Dapper primary (19); LLM-as-judge REUSES 27's Condorcet majority-of-3;
  guardrails REUSE 18's defence-in-depth. `_recompute.py` **19/19** (binomial CI ~1067 tasks for
  ±3%; pass@k 0.936 vs pass^k 0.216; majority-of-3 judges 1.9–3.6× fewer errors, backfires <0.5;
  49 spans/run + Dapper sampling RSE; defence-in-depth 0.8% escape vs 5.9% over-refusal FP tax;
  lexical≠correct + %resolved; suite cost 837M tok = S·O(T²)). `_factcheck_phase1.md` 0 blockers.
  Reuses 13/18/19/20/22/23/24/25/27/28/30.
- shipped: **32 cost-observability-and-ops RECONCILED** (the 22 O(T²) economics made OPERATIONAL).
  Bespoke **cost-lifecycle walkthrough** (Account → Attribute → Budget/Cap → Optimize → Operate) =
  19 observability + 18 control + 20 capacity denominated in $/tokens, on top of 22's quadratic.
  **NO new primary** (operational synthesis like 21; prices already-VERIFIED mechanisms).
  `_recompute.py` **14/14** (cost O(T²) — doubling turns >2× the bill, input/quadratic term
  dominates; compaction O(T²)→O(T) saves ~$18.8/run@T=100 and grows unbounded; prefix-cache 10×
  cheaper prefix but leaves the quadratic transcript [caching≠compaction]; per-tenant quota = 18
  token-bucket over $; cost tail mean 20× median, per-run turn cap cuts total 10×; cost =
  attributable signal [LLM 80% of bill]; model routing 70/30 → blended $1.04/M vs $3/M).
  `_factcheck_phase1.md` 0 blockers. Reuses 18/19/20/22/24/26/30/31.
- shipped (opportunistic): **SWE-bench (arXiv 2310.06770) FETCHED+VERIFIED** to
  `meta/fetched_primaries/swe-bench-2310.06770.{pdf,txt}` (52 pp, 153k chars), receipt
  `_VERIFIED_2026-06-10_swe-bench.md`. Extraction via throwaway `/tmp/pdfx-venv` (uv+pypdf from
  Walmart external-pypi), REMOVED after; `.code-puppy-venv` never touched. **BONUS:** cleared 28's
  carried `[UNVERIFIED]` SWE-bench note → VERIFIED (annotated in `28-.../_factcheck_phase1.md`;
  nothing erased).
- decisions: NO new ADR — 31 introduces one VERIFIED primary (SWE-bench) + reuses; 32 is an
  operational synthesis with no new primary (capstone-style, like 21). Both bespoke structures per
  the constitution's "do not template" rule. Prefer-one-clean-checkpoint honored: stopped after 31+32
  rather than rushing 33/34.
- stopped-at: **22-32 reconciled (Part III 11/13).** 33-34 untouched. 33 likely wants its own
  fetched primary (prompt-injection / sandboxing / alignment-oversight); 34 is the Part-III capstone
  design canvas (no new primary). Network: arxiv/kafka/postgres 200; queue.acm.org 403 (CoDel) +
  raft.github.io 000 still blocked (retried). Opportunistic Kafka(09/17) upgrade NOT done (SWE-bench
  was the load-bearing budget). Next: **33-safety-and-proactive-self-evolving-agents**, then
  **34-design-your-own-agentic-system** → completes Part III (22-34).


## 2026-06-10 — Phase 1 Wave 13: Part III batch 3 continued — 28 build-your-own-coding-harness, 29 mcp-skills-and-connectors, 30 rag-retrieval-and-grounding reconciled (MCP spec + RAG fetched/verified)
- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/RESEARCH_INDEX/
  PROGRESS/SESSION_LOG/DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint was `f5dc2a8`;
  no `os.getcwd()`/`Path.cwd()` PermissionError. Confirmed Wave 2 milestone `4a1cc71`, 01-12 + Part II
  13-21 COMPLETE, Part III open with 22-27 reconciled (6/13); 28 NEXT untouched.
- shipped: **28 build-your-own-coding-harness RECONCILED** (Part III CAPSTONE LAB). Bespoke **BUILD
  PROGRESSION**: the "40-line agent" grown stage-by-stage, **broken on purpose** at each stage so the
  next primitive is motivated by an observed failure (loop22→tools23→budget(22/18/32)→compaction24→
  memory25→persistence26→orchestration27). NO new primary (capstone application, like 21 — every
  mechanism cross-links to an already-VERIFIED anchor: ReAct/Toolformer/CoT/MemGPT/Reflexion/
  Postgres-WAL + recomputed 27 math). `_recompute.py` **31/31** — all 7 stage walls RE-DERIVED in the
  CODING regime (p=4000,g=1500): O(T²) overflows SOONER for code (T*=83 vs chat 253); selection
  compounding; 1MB-file result overflow; budget caps≠cures; **compaction O(T²)→O(T) win grows
  unbounded**; AMAT 4× (matches 25); poisoning 1→15; checkpoint knee I*=20; idempotent replay;
  Amdahl/join-tail/**YAGNI** (multi-agent LOSES on small tasks). `_factcheck_phase1.md` 0 blockers.
  Reuses 09/17/18/20/21/22/23/24/25/26/27.
- shipped: **29 mcp-skills-and-connectors RECONCILED** (23's tool CONTRACT promoted to a wire
  PROTOCOL). Bespoke protocol/connector walkthrough. **MCP architecture spec FETCHED+VERIFIED**
  verbatim: client-server host/client/server; two layers (data=JSON-RPC 2.0 / transport); three
  server primitives tools/resources/prompts + client sampling/elicitation/logging + experimental
  Tasks(durable exec); stdio vs Streamable-HTTP; stateful lifecycle/capability negotiation
  (negotiate-or-terminate); `*/list` discovery + `list_changed` notifications (push>poll).
  `_recompute.py` **18/18** — **N×M→N+M integration collapse** (why a protocol exists; 400→40),
  union-toolbox tax K·S, selection compounding over the union, remote-dependency tail 1-(1-p)^s,
  version/schema compat (11/17). `_factcheck_phase1.md` 0 blockers. Reuses 02/03/07/11/17/18/19/20/
  22/23/24/26/28.
- shipped: **30 rag-retrieval-and-grounding RECONCILED** (the retrieval mechanism for 25's
  non-parametric memory tier). Bespoke retrieval-pipeline walkthrough (corpus→chunk→embed→index→
  retrieve→rank→inject/ground). **RAG (Lewis et al. 2020, arXiv 2005.11401) FETCHED+VERIFIED**
  verbatim: parametric vs non-parametric memory; DPR bi-encoder; MIPS top-K "solved in sub-linear
  time"; FAISS+HNSW; latent-doc marginalize (RAG-Sequence/RAG-Token); cures hallucination + supplies
  provenance + updatable knowledge; "more specific, diverse and factual". `_recompute.py` **15/15** —
  ANN-vs-scan ~430,000× at 10M chunks; retrieve-vs-stuff 24 budget; **K precision/recall/cost knob**
  (don't max K → distractors); embedding cache 1000×; **index staleness/lag** (grounding only as
  fresh as the index, 15/16). `_factcheck_phase1.md` 0 blockers. Reuses 06/07/08/14/15/16/22/23/24/
  25/28/29.
- shipped: PRIMARIES fetched+verified to `meta/fetched_primaries/` — `mcp-arch.txt` (receipt
  `_VERIFIED_2026-06-10_mcp.md`) + `rag-2005.11401.{pdf,txt}` (receipt `_VERIFIED_2026-06-10_rag.md`).
  Updated PROGRESS (28/29/30 rows RECONCILED + Wave 13 note), NEXT_SESSION. Three clean commits
  (`3e623df`, `f1fdb72`, `2d594ce`) — one per sub-course.
- decisions: (1) 28 needed NO new primary — it is the ASSEMBLY of already-VERIFIED 22-27 primitives
  into a coding harness via a build progression; all walls RECOMPUTED in the coding regime (same
  discipline as 21's Part-II capstone). (2) MCP's formal `/specification/2025-11-25` page is a
  client-rendered SPA shell (no server-side text) — used the authoritative `/docs/learn/architecture`
  prose instead; verbatim load-bearing semantics captured, field-level JSON-Schema deferred to Phase
  2 (`[UNVERIFIED]`). (3) RAG PDF extracted via the throwaway `/tmp/pdfx-venv` (uv+pypdf 6.13.2 from
  Walmart external-pypi), removed after; `.code-puppy-venv` never touched. (4) Each sub-course got a
  BESPOKE structure (28=build progression, 29=protocol/connector walkthrough, 30=retrieval pipeline)
  — NOT the 13-20 four-cluster shape. (5) Time-boxed to THREE deep sub-courses + two plan-mandated
  primary fetches; opportunistic Kafka(09/17) upgrade DEFERRED to keep clean per-sub-course
  checkpoints over shallow briefs.
- stopped-at: 28+29+30 reconciled (Part III at 22-30 = 9/13). Clean checkpoint; all committed. Next:
  **31-evaluation-tracing-and-guardrails** (↔ 19 observability/Dapper + 27 voting/critic + 18
  guardrails), then 32 cost, 33 safety, 34 design-your-own. Still blocked: queue.acm.org 403 (CoDel),
  raft.github.io 000. No chapters. No Phase 2.

- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/RESEARCH_INDEX/
  PROGRESS/SESSION_LOG/DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint was `48a5b5e`;
  no `os.getcwd()`/`Path.cwd()` PermissionError (CWD resolves through OneDrive, reads fine). Confirmed
  Wave 2 milestone `4a1cc71`, that 01-12 + Part II 13-21 are COMPLETE, and Part III open w/ 22+23.
- shipped: **24 prompts-and-context-engineering RECONCILED** (bespoke budget/allocation walkthrough;
  refines the 22 "assemble context" box). Primary **CoT (Wei et al., NeurIPS 2022, arXiv 2201.11903)
  FETCHED+VERIFIED** verbatim: prompts = programming-by-example (Brown lineage); "additional
  computation can be allocated to problems that require more reasoning steps"; permuting few-shot
  exemplars swings GPT-3 SST-2 **54.3%→93.4%** (ORDER is load-bearing); emergent ~100B; style-robust.
  `_recompute.py` 18/18 — HEADLINE: **compaction converts 22's O(T²)→O(T)** (cap transcript at C,
  summarize); + window-as-budget, few-shot cost, compaction ratio/payoff, prefix-cache discount
  (helps prefix NOT the quadratic), placement band. `_factcheck_phase1.md` 0 blockers. Reuses
  06/08/16/13/18/22/23.
- shipped: **25 memory-short-term-long-term-and-safety RECONCILED** (bespoke memory-hierarchy
  walkthrough; what 24's compactor externalizes to). Primaries **MemGPT (arXiv 2310.08560) +
  Reflexion (arXiv 2303.11366) FETCHED+VERIFIED** verbatim: "virtual context management ... paging
  between physical memory and disk"; main vs external context; main=system+working+FIFO; function-
  call pagers; "episodic memory buffer" learning w/o weight updates; 91% vs 80% HumanEval.
  `_recompute.py` 13/13 — **AMAT over tokens** (hit 0.80→0.95 = 4× cheaper), 0.1% resident,
  consolidation O(T) on disk, **poisoning blast radius** (1 write → ~15 reads → validate writes).
  `_factcheck_phase1.md` 0 blockers. Reuses 04/06/08/16/09/15/22/23/24.
- shipped: **26 state-persistence-and-resume RECONCILED** (bespoke durability/recovery walkthrough).
  Insight: the agent transcript is a **Write-Ahead Log** → resume IS DB crash recovery. **PostgreSQL
  WAL docs FETCHED+VERIFIED** verbatim (log-before-data; "only the WAL file needs to be flushed ...
  to guarantee that a transaction is committed"; "roll-forward ... REDO"). `_recompute.py` 12/12 —
  write-ahead loss ≤1 step, **checkpoint knee I*=√(2N·c_ckpt)**, RTO, idempotent replay (17/21),
  fsync/group-commit, replication quorum (15). `_factcheck_phase1.md` 0 blockers. Reuses
  07/09/15/17/20/22/24/25.
- shipped: **27 planning-and-multi-agent-orchestration RECONCILED** (bespoke coordination
  walkthrough). Strong claim: **a multi-agent system is a distributed system whose nodes are LLM
  loops** (laws = 11/13/17/20). No new load-bearing primary (applies the toolkit, like 21).
  `_recompute.py` 16/16 — plan size W^D, **Amdahl over agents** (ceiling 1/s), **join tail
  1-(1-p)^N=63.4%@N=100**, aggregation tax N·r (compact → 6.7× less), **error compounding +
  majority-of-3 voting 6.9× better**, payoff/YAGNI condition (multi-agent LOSES on small tasks),
  C(N,2) conflict pairs. `_factcheck_phase1.md` 0 blockers. Reuses 09/11/13/14/15/17/18/20/22/24/25/26.
- shipped: PRIMARIES fetched+verified to `meta/fetched_primaries/` (cot-2201.11903.{pdf,txt},
  memgpt-2310.08560.{pdf,txt}, reflexion-2303.11366.{pdf,txt}, postgres-wal-intro.txt); receipts
  appended to `_VERIFIED_2026-06-10_agentic.md` + new `_VERIFIED_2026-06-10_postgres-wal.md`.
  Updated PROGRESS (24-27 rows RECONCILED + Wave 12 note), NEXT_SESSION.
- decisions: (1) Reused the throwaway `/tmp/pdfx-venv` (uv+pypdf) for PDF text; `.code-puppy-venv`
  never touched. (2) Each Part III sub-course got a BESPOKE structure (24=budget/allocation,
  25=memory-hierarchy, 26=durability/recovery, 27=coordination) — NOT the 13-20 four-cluster shape.
  (3) 27 needed NO new load-bearing primary — its content is the APPLICATION of line-verified
  11/13/17/20 to loops (same discipline as 21's capstone); planning papers + MA frameworks carried
  `[UNVERIFIED]`. (4) Opportunistic Postgres-WAL fetch done (corroborates 07/15, already source-
  verified in 07); Kafka(09/17) upgrade DEFERRED to keep one clean 4-sub-course checkpoint.
- stopped-at: 24+25+26+27 reconciled (Part III at 22-27 = 6/13). Clean checkpoint; committed. Next:
  **28-build-your-own-coding-harness** (capstone lab: loop→tools→context→memory→persistence→
  orchestration→budgets/compaction), then 29 MCP (fetch spec), 30 RAG (fetch Lewis 2020, arXiv
  2005.11401), 31 eval, 32 cost, 33 safety, 34 design-your-own. Still blocked: queue.acm.org 403
  (CoDel), raft.github.io 000. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 11: OPEN Part III Agentic System Design — 22 the-agent-loop + 23 tools-and-tool-contracts reconciled (ReAct + Toolformer fetched/verified)
- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/RESEARCH_INDEX/
  PROGRESS/SESSION_LOG/DECISIONS/NEXT_SESSION; `git status --short` clean; checkpoint was `384d6dd`;
  no `os.getcwd()`/`Path.cwd()` PermissionError. Confirmed Wave 2 milestone `4a1cc71` and that ALL of
  01-21 are reconciled/factchecked (foundations 01-12 + Part II 13-21 COMPLETE).
- shipped: **22 the-agent-loop RECONCILED** (Part III FOUNDATIONAL primitive; bespoke single-control-
  loop walkthrough, NOT four clusters). An agent = a control loop around an LLM
  (assemble→call→parse→act→observe→append→decide); each loop box maps to a downstream Part III
  sub-course (the dependency spine). Primary **ReAct (Yao et al., ICLR 2023, arXiv 2210.03629)
  FETCHED + VERIFIED** verbatim: interleaved Thought/Action/Observation; acting grounds reasoning,
  curing CoT hallucination via an external API; +34%/+10% (ALFWorld/WebShop) with 1-2 exemplars.
  `_recompute.py` 18/18 — headline: agent input tokens are **O(T²)** (`T*p + g*T*(T-1)/2`, transcript
  re-sent + grows every turn) → motivates 24/25/32; also cost, step/cost/time budgets, window-
  exhaustion `T*=floor((W-p)/g)+1`, per-step retry. `_factcheck_phase1.md` 0 blockers. Reuses
  04/09/13/17/18/20/11.
- shipped: **23 tools-and-tool-contracts RECONCILED** (bespoke contract walkthrough). A tool = an
  **API contract between a stochastic caller and deterministic code**; the hard part is the stochastic
  caller, so the contract must be advertised + validated/repaired. Primary **Toolformer (Schick et al.,
  NeurIPS 2023, arXiv 2302.04761) FETCHED + VERIFIED** verbatim: the four decisions (which API / when /
  what args / how to incorporate results); tools offload arithmetic/lookup; self-supervised baking
  (sample→execute→filter-by-loss→finetune) vs in-context use. `_recompute.py` 15/15 — toolbox tax K·S
  (feeds 22's quadratic), retrieval-over-tools break-even (→30), tool-result size budget, repair-retry
  bound, selection-error compounding `1-(1-q)^N` (the 13/20/21 identity over loop steps), idempotency
  retention (17/21). `_factcheck_phase1.md` 0 blockers. Reuses 03/07/08/16/17/18/22.
- shipped: PRIMARIES fetched+verified to `meta/fetched_primaries/` (react-2210.03629.{pdf,txt},
  toolformer-2302.04761.{pdf,txt}); receipt `_VERIFIED_2026-06-10_agentic.md`. Updated PROGRESS
  (22/23 rows RECONCILED + Wave 11 note), RESEARCH_INDEX (Part III batch 3 section), NEXT_SESSION.
- decisions: (1) Used a throwaway `/tmp/pdfx-venv` (uv + pypdf 6.13.2 from Walmart external-pypi) to
  extract arxiv PDF text, REMOVED after; `/Users/m0t0hu6/.code-puppy-venv` never touched. (2) Each
  Part III sub-course gets a BESPOKE structure (22 = loop walkthrough, 23 = contract walkthrough), per
  the plan — NOT the 13-20 four-cluster shape. (3) **Stopped at 2 clean sub-courses rather than
  starting 24** — prefer one clean factchecked checkpoint over multiple shallow briefs; 24 (context
  engineering) leans on community idiom and deserves its own focused session. (4) Spent the arxiv
  budget on the load-bearing 22/23 primaries; DEFERRED opportunistic Kafka(09/17)/Postgres(07/15)
  upgrades + RAG/MCP/CoT fetches to next session (all confirmed reachable).
- stopped-at: 22 + 23 reconciled (Part III opened, 2/13 done). Committed. Next: **24-prompts-and-
  context-engineering** (refines the "assemble context" box; forced by 22's quadratic + 23's toolbox
  tax), then 25→34. Still blocked: queue.acm.org 403 (CoDel), raft.github.io 000, dl.acm.org 403.

## 2026-06-10 — Phase 1 Wave 10: START + RECONCILE Part II 21 design-case-studies (CAPSTONE) — PART II (13-21) COMPLETE; Gilbert-Lynch formal CAP + Abadi PACELC unblocked + upgraded into 11 & 15
- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/RESEARCH_INDEX/
  PROGRESS/SESSION_LOG/DECISIONS/NEXT_SESSION; `os.getcwd()`/`Path.cwd()` worked (no PermissionError);
  `git status --short` clean; checkpoint was `f382551`. Confirmed Wave 2 milestone `4a1cc71` ("Phase 1
  Wave 2 research and factcheck fixes") and that ALL of 01-20 were reconciled/factchecked.
- shipped: **21 design-case-studies RECONCILED** (Part II CAPSTONE; the application course — NO new
  primitives, applies the 13-20 toolkit to six concrete designs via a bespoke per-case-study
  structure):
  - `_case_url-shortener.md` — write-once/read-heavy (100:1); KGS vs hash key-gen; base62^7 floor;
    cache/CDN is the whole design (16/14); origin-load=(1-h).
  - `_case_news-feed.md` — fan-out-on-write vs read; celebrity = 14 hot key (1e8 single-post
    fan-out); hybrid push/pull; async fan-out (17); read-your-writes (15).
  - `_case_chat-messaging.md` — 1000 connection gateways; per-conversation sequencer (11/17);
    at-least-once+dedup = exactly-once-effect; presence shedding (18); reconnect+resync (20).
  - `_case_search-typeahead.md` — inverted index (06/12); document-partition 100 shards;
    scatter-gather tail 1-(1-p)^100=63.4%; hedged/tied requests + partial results (20).
  - `_case_payments-ledger.md` — double-entry append-only ledger; idempotency=exactly-once-effect
    (17); 2PC vs saga (11/14); sync quorum W+R>N (15); CAP forfeit-A + PACELC PC/EC (VERIFIED).
  - `_case_rate-limiter.md` — direct 18 application; token bucket; cell counters; distributed
    over-admit (M-1)*B=35; shard by key (14); fail-open vs SPOF (20).
  - `_recompute.py` (32/32 back-of-envelope estimates PASS — every QPS/storage/keyspace/cache/shard/
    fan-out-tail recomputed); `_factcheck_phase1.md` (0 blockers); `_research.md` (RECONCILED:
    design-method 6-step spine + toolkit-usage matrix + cross-case reconciliations + gap ledger).
- shipped: **CAP/PACELC primaries UNBLOCKED + verified** (Wave 10 network heal). `groups.csail.mit.edu`
  (Gilbert-Lynch "Perspectives on the CAP Theorem" 2012) + `cs.umd.edu/~abadi` (Abadi PACELC 2012)
  returned HTTP 200 after many blocked sessions. Fetched + text-extracted (throwaway uv venv + pypdf,
  removed after) + verified verbatim to `meta/fetched_primaries/` (`gilbert-lynch-2002.{pdf,txt}`,
  `abadi-pacelc-2012.{pdf,txt}`; receipt `_VERIFIED_2026-06-10_cap-pacelc.md`). Upgraded carry-forward
  `[UNVERIFIED]` -> VERIFIED in 11 (`_factcheck_cluster4.md`: formal CAP = safety-vs-liveness
  impossibility on an atomic register, CAP⇒no-consensus-under-partition) and 15 (`_factcheck_phase1.md`:
  PACELC "if P: A-vs-C; else: L-vs-C", PA/EL vs PC/EC vs PC/EL). Nothing erased.
- decisions: 21 uses a BESPOKE per-case-study structure (not the four-cluster shape of 13-20) because
  it is an application/capstone course — plan-sanctioned; consistent with ADR-001's spirit (cluster/
  case files reconciled by brain into `_research.md`). The design-method spine + toolkit-usage matrix
  in `_research.md` is the actual teachable capstone payload.
- decisions: 21 needed exactly ONE genuinely new primary (CAP/PACELC for the payments case); fetched +
  verified this session. All other claims are RECOMPUTED math or REUSE of line-verified 06/09/11/12/13-20.
  Community design idioms (KGS, push/pull feed, vendor chat/search/payment designs, GCRA) flagged
  `[UNVERIFIED]` as idioms — mechanisms grounded in the line-verified primitives; none load-bearing.
- stopped-at: clean checkpoint after 21 reconciled + Part II complete. `git status --short` then commit.
  **PART II (System Design, 13-21) IS COMPLETE.** Next batch = Part III Agentic System Design
  (22-the-agent-loop onward) per COURSE_MAP "Phase 1 batch 3". Opportunistic note for next session:
  arxiv.org / kafka.apache.org / postgresql.org are now HTTP 200 (deferred, time-boxed); still blocked
  queue.acm.org 403 (CoDel), raft.github.io 000, dl.acm.org 403. Do NOT start chapters or Phase 2.

## 2026-06-10 — Phase 1 Wave 9: START + RECONCILE Part II 20 resilience-failure-and-capacity-planning (The Tail at Scale) (A-D); CAP primaries (Brewer/Kleppmann) unblocked + upgraded into 11 & 15
- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/RESEARCH_INDEX/
  PROGRESS/SESSION_LOG/DECISIONS/NEXT_SESSION; `os.getcwd()`/`Path.cwd()` worked (no PermissionError);
  `git status --short` clean; checkpoint was `60115a5`.
- shipped: **20 resilience-failure-and-capacity-planning RECONCILED** (Part II EIGHTH sub-course, the
  synthesis course; four clusters A-D):
  - `_research_failure-models-and-partial-failure.md` (A): fault->error->failure chain; partial failure
    as the defining property (slow node indistinguishable from dead, FLP reuse 11); taxonomy crash/
    omission/timing(=tail)/Byzantine; independent-vs-correlated failure; fallacies of distributed
    computing; blast radius; cascade vs single fault (reuse 18); CAP as a failure-model statement.
  - `_research_the-tail-at-scale.md` (B): fan-out 1-0.99^100=63%; faults-vs-variability; hedged/backup
    requests (Dean table 994->50ms p99.9, <5% extra) + tied requests w/ cross-server cancellation
    (-43%/-38% p99, ~1% extra); micro-partitioning; selective replication; latency-induced probation;
    canary requests; tainted partial results; synchronized disruption.
  - `_research_resilience-patterns-and-redundancy.md` (C): the 18 toolkit (timeouts/retries+jitter/
    breakers/bulkheads/shedding/degradation/hedging) + redundancy N+1/N+2/2N + failover (reuse 15) +
    cells & shuffle-sharding (C(8,2)=28->1/28->7x; Route 53 2048-choose-4~730B; recursive) + chaos
    engineering (Netflix Chaos/Latency/Gorilla monkeys) as failure-injection verification.
  - `_research_capacity-planning-and-reliability-math.md` (D): capacity loop; utilization wall; headroom
    C=D/rho*; M/G/1 variance; USL knee; serial availability prod(a_i) (erodes); parallel 1-(1-a)^n; the
    correlated-failure correction; headroom-to-survive-f = f/n; capacity as an SLO input (reuse 19).
  - `_recompute.py` (38/38 pass) + `_factcheck_phase1.md` (0 blockers) + RECONCILED `_research.md`.
- shipped: **38/38 load-bearing math claims VERIFIED by recomputation.** Headline: the correlated-failure
  correction collapses naive six-nines parallel redundancy to ~three nines (1001x worse unavailability)
  — correlation, not replica count, sets real availability.
- shipped: **PRIMARIES fetched + verified** to `meta/fetched_primaries/` (receipt
  `_VERIFIED_2026-06-10_resilience.md`): Dean Tail-at-Scale (already local); AWS Builders' shuffle-sharding
  + timeouts/retries/backoff-with-jitter; Brewer PODC 2000 CAP keynote; Kleppmann CAP blog 2015; Netflix
  Simian Army. Brewer PDF extracted via throwaway uv venv at /tmp/pdfv (removed after); nothing under
  /Users/m0t0hu6/.code-puppy-venv touched.
- shipped: **CAP UPGRADE (opportunistic):** Brewer PODC 2000 + Kleppmann 2015 returned HTTP 200 (blocked
  8+ sessions). Upgraded carry-forward CAP `[UNVERIFIED]` -> VERIFIED in 11 (`_factcheck_cluster4.md`)
  and 15 (`_factcheck_phase1.md`): "at most two" of {C,A,P}, Forfeit C/A/P, BASE, CAP-as-narrow-theorem.
  Gilbert-Lynch 2002 formal proof + Abadi 2012 PACELC remain blocked/carried forward; nothing erased.
- decisions: followed the standing per-cluster->reconcile pattern (ADR-001). Kept all `[UNVERIFIED]`
  (Nygard "Release It!", Avizienis fault/error/failure taxonomy, Deutsch/Gosling fallacies, CoDel,
  Gilbert-Lynch formal proof, PACELC) as carry-forward; mechanisms verified via 18 + AWS builders'
  where the book primaries are unavailable. CoDel (queue.acm.org 403) + raft.github.io (000) still
  blocked but not load-bearing for 20.
- stopped-at: clean factchecked checkpoint after 20 fully reconciled + CAP upgrades applied. **ALL of
  01-20 reconciled; only 21 (design-case-studies) remains to finish Part II.** Next session: START 21.

## 2026-06-10 — Phase 1 Wave 8: START + RECONCILE Part II 19 observability-tracing-and-slos (Dapper) (A-D); SEDA finally unblocked + upgraded into 18
- shipped: rehydrated from AGENTS/START_HERE/CONSTITUTION/RESEARCH_PROTOCOL/COURSE_MAP/RESEARCH_INDEX/
  PROGRESS/SESSION_LOG/DECISIONS/NEXT_SESSION; `os.getcwd()`/`Path.cwd()` worked (no PermissionError);
  `git status --short` clean; checkpoint was `e006265`.
- shipped: **19 observability-tracing-and-slos RECONCILED** (Part II SEVENTH sub-course, four clusters):
  - `_research_metrics-and-signal-taxonomy.md` (A): counter/gauge/histogram; Four Golden Signals vs RED vs
    USE; black-box/white-box; cardinality (60->60M); percentiles>means; bucket-additivity.
  - `_research_distributed-tracing-dapper.md` (B): Dapper trace-tree/spans/context-propagation/clock-skew/
    sampling/overhead; head vs tail sampling; reconstructs 13 fan-out tail + 17 async flow.
  - `_research_logs-events-three-pillars.md` (C): structured logging; three pillars cost/cardinality;
    exemplars metric->trace->log; sampling/retention (reuse 09/16/17).
  - `_research_sli-slo-error-budgets.md` (D): SLI/SLO/SLA; error budget=(1-SLO)*window; burn rate;
    multiwindow multi-burn-rate alerting; SRE iterations 1->6.
  - `_recompute.py` (28/28 pass); `_factcheck_phase1.md` (0 blockers); `_research.md` (six sections).
- shipped: **PRIMARIES fetched + verified** to `meta/fetched_primaries/` (network healed): Dapper-2010
  (research.google mirror) + SRE Book Ch.4 SLO + Ch.6 Monitoring + SRE Workbook Ch.5 Alerting (sre.google).
  Receipt `_VERIFIED_2026-06-10_observability.md`. Throwaway uv venv used for pypdf, removed after.
- shipped: **SEDA (Welsh SOSP'01) finally unblocked** via `www.sosp.org/2001/papers/welsh.pdf` (HTTP 200
  after 8+ sessions of 000/404). Fetched + verified `seda-sosp01.{pdf,txt}`; upgraded the carry-forward
  `[UNVERIFIED]` in 18 Cluster B -> VERIFIED (UPGRADE section appended to `18-.../_factcheck_phase1.md`;
  nothing erased). Updated RESEARCH_INDEX + PROGRESS.
- decisions: ADR-001 (per-cluster files reconciled by brain) reused. No new ADR. Prefer one clean
  factchecked checkpoint over breadth (per the prompt) — stopped after 19 + SEDA, did NOT start 20.
- decisions: opportunistic retries — still blocked: CoDel (queue.acm.org 403), raft.github.io (000),
  arxiv/dl.acm/postgresql.org/kafka.apache.org, aws.amazon.com builders', eecs.harvard.edu (use sosp.org).
  Kleppmann CAP blog now HTTP 200 (fetch+verify deferred; not load-bearing for 19).
- stopped-at: **ALL of 01-19 reconciled/factchecked.** Clean checkpoint. Next = 20 resilience-failure-
  and-capacity-planning (The Tail at Scale — already fetched), then 21 design-case-studies. No chapters,
  no Phase 2. All logged `[UNVERIFIED]`/residual gaps preserved.

## 2026-06-10 — Phase 1 Wave 7: START + RECONCILE Part II 18 rate-limiting-backpressure-and-load-shedding (SEDA) (A-D); BIG opportunistic canon fetch (network heal)
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` clean; checkpoint
  at session start `5eff696`; no `os.getcwd()`/`Path.cwd()` PermissionError; `.code-puppy-venv` NOT touched;
  Code Puppy NOT reinstalled. Confirmed Wave 2 milestone `4a1cc71` and ALL of 01-17 reconciled; 18-21 untouched.
- shipped: 18 FOUR cluster briefs — `_research_rate-limiting-algorithms.md` (A: token/leaky bucket; fixed/
  sliding window log+counter; distributed counters; fairness/burst; enforce at edge/LB/task; 429+Retry-After),
  `_research_backpressure-and-seda.md` (B: bounded queues; block-vs-drop; credit/flow control = TCP window/
  request(n)/pull-lag; end-to-end vs hop-by-hop; SEDA stage/queue/controller), `_research_load-shedding-and-
  retry-storms.md` (C: fail-early-503; CPU-not-QPS; criticality 4 tiers + per-customer limits; brownout/degrade;
  FIFO/LIFO/CoDel + deadline-drop; retry amplification 1/(1-r) -> storm -> goodput collapse; budgets 3/10%),
  `_research_timeouts-breakers-bulkheads-hedging.md` (D: timeouts+deadline-propagation; circuit breakers;
  bulkheads; hedged/tied requests; adaptive concurrency AIMD + Google adaptive throttling).
- shipped: `_recompute.py` (pure stdlib, 9/9 pass, exit 0) verifying 9 load-bearing math claims — token bucket
  admit=min(arrival,refill)/burst<=B; leaky bucket smoothing+drop; fixed-window 2x boundary burst; sliding-log
  exact (O(limit)) vs sliding-counter est=curr+prev*(1-frac) worst over-admit prev*frac (O(1)); distributed
  over-admit (cells-1)*batch; bounded-queue latency Q/drain (SRE 10x-pool 1.0s / 0.5x-pool 0.05s); retry
  amplification 1/(1-r) (.9->10x,.99->100x) + 3/10% caps; goodput plateau-vs-collapse; adaptive throttle
  p=max(0,(req-K*acc)/(req+1)).
- shipped: `_factcheck_phase1.md` (recompute/primary/reuse buckets; 0 blockers) and RECONCILED `_research.md`
  (standard six sections + cross-cluster thesis: input->buffer->drop->client). Mechanisms reused from line-
  verified 03/11/13/14/15/16/17/10; no canon re-derived.
- shipped (PRIMARY, fetched this session): RFC 6585 §4 (429 + Retry-After + per-resource/server/fleet counting)
  and Google SRE *Handling Overload* + *Addressing Cascading Failures* — VERIFIED: QPS-pitfall/CPU-signal,
  per-customer limits, adaptive throttling formula+K, criticality 4 tiers+reject-lower-first, graceful
  degradation, retry budgets 3/10%/"don't retry", queue<=50%pool/reject-early/503, FIFO->LIFO/CoDel[Nichols12],
  10K-QPS retry-storm, "capacity planning necessary not sufficient". Saved to `meta/fetched_primaries/`.
- shipped (BIG OPPORTUNISTIC HAUL — network heal: research.google mirrors + usenix.org/legacy +
  allthingsdistributed.com + sre.google all HTTP 200): fetched + extracted (pypdf in a throwaway uv venv,
  removed after) and VERIFIED to `meta/fetched_primaries/` (receipt `_VERIFIED_2026-06-10_canon.md`):
  **Tail at Scale** CACM 2013 (fan-out 63% / backup=hedged + cancellation=tied / Backup Effects 994ms->50ms),
  **Dynamo** SOSP 2007 ("R + W > N" verbatim + consistent-hashing/vnodes/vector-clocks/sloppy-quorum/hinted-
  handoff/Merkle/read-repair/gossip), **MapReduce** OSDI 2004 (straggler+backup tasks), **Bigtable** OSDI 2006
  (SSTable/tablet/Chubby/compaction), **GFS** SOSP 2003 (chunk/64MB/lease/primary), **Spanner** OSDI 2012
  (TrueTime/commit-wait/Paxos/external-consistency). Upgraded carry-forward `[UNVERIFIED]` -> VERIFIED in the
  factcheck files of 18D, 15, 14, 13, and 12 (appended UPGRADE sections).
- decisions: (ADR-001) per-cluster files reconciled by brain — followed. Used a disposable uv venv (Walmart
  Artifactory mirror) for pypdf text extraction since no pdftotext; removed it; system Python untouched.
  Recorded the canon haul as a single receipt file rather than re-running full per-paper factchecks (terms +
  the one load-bearing quote per paper verified verbatim; deep per-paper factcheck deferred to when those
  sub-courses reach Phase 2).
- stopped-at: 18 reconciled; 0 factcheck blockers. NOT started: 19-21 (Phase 1), any chapters, any Phase 2.
  Remaining 18 gaps = vendor/paper attributions (SEDA SOSP'01 [still blocked: Harvard+usenix non-legacy 000],
  CoDel ACM Queue'12 [queue.acm.org 403], Hystrix/concurrency-limits/resilience4j/Envoy, GCRA, AWS builders'
  library [000]) — all `[UNVERIFIED]`, none load-bearing. Next batch: 19 (observability-tracing-and-slos/Dapper).

## 2026-06-10 — Phase 1 Wave 6: START Part II 17 async-queues-and-event-driven-architecture (A/B/C/D) + RECONCILE 17; opportunistic 16/08 RFC+Nishtala upgrade
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean; current
  checkpoint at session start was `59dc7c5`; no `os.getcwd()`/`Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was NOT modified; Code Puppy was NOT reinstalled. Confirmed Wave 2 milestone
  `4a1cc71` in history and ALL of 01-16 reconciled/factchecked at session start; 17-21 untouched.
- shipped: 17 FOUR cluster briefs — `_research_messaging-models-delivery-semantics.md` (A: queue/log/pub-sub;
  at-most/at-least/effectively-once; idempotency+dedup-window; per-partition ordering; outbox+CDC),
  `_research_event-driven-architecture-patterns.md` (B: events vs commands; choreography vs orchestration; sagas+
  compensation; event sourcing+CQRS; materialized-view maintenance; backpressure handoff to 18),
  `_research_producer-consumer-mechanics-failure.md` (C: consumer groups/rebalancing; commit/ack timing; redelivery/
  backoff; DLQ/poison; exactly-once-effect; replay), `_research_delivery-infrastructure-tradeoffs.md` (D: broker
  durability/replication; partitioning for throughput; fan-out; retention vs compaction; batching).
- shipped: `_recompute.py` (pure stdlib, 0 errors) verifying 6 load-bearing math claims — at-least-once duplicate
  certainty E[dups]=N*p / P(>=1)=1-(1-p)^N; dedup-window = redelivery horizon (cap-exp-backoff sum + visibility =
  213 s ex.) and store size rate*window*bytes; batching throughput 1/(c/B+m) asymptote 1/m; retention disk
  rate*bytes*ret*RF vs compaction floor keys*bytes (history-independent); parallelism ceiling consumers<=partitions,
  need=ceil(target/per); dual-write failure window window*crash_rate (~38/1e9 ops at 100 ms -> leaks).
- shipped: `_factcheck_phase1.md` (recompute/reuse/primary buckets; 0 blockers) and RECONCILED `_research.md`
  (standard six sections + cross-cluster thesis). All mechanisms reused from line-verified 09/11/13/14/15/16/06/08/03;
  no canon re-derived.
- shipped (OPPORTUNISTIC, network partially healed: rfc-editor.org + usenix.org HTTP 200 after 8 sessions of 000):
  fetched + saved to `meta/fetched_primaries/` — RFC 9111/5861/7234/4786 and Nishtala et al. NSDI '13
  (`nishtala-nsdi13.pdf` + extracted `.txt`). VERIFIED verbatim: RFC 9111 s-maxage/Vary/Age/must-revalidate; RFC
  5861 SWR+stale-if-error; RFC 4786 anycast BCP; Nishtala demand-filled look-aside cache, leases (64-bit token, <=1
  token/10s/key), peak DB query 17K/s -> 1.3K/s, mcsqueal CDC delete-stream off the DB commit log cross-region, 4%
  of deletes actually invalidate. Recorded as 16 `_factcheck_phase1.md` §F (also clears matching 08 attributions).
  Nishtala doubles as 17's concrete production EDA/CDC instance (A §1.6, B §1.5).
- decisions: (ADR-001) per-cluster files reconciled by brain — followed. Reused 09's line-verified log/offsets/
  consumer-groups/EOS wholesale rather than re-fetching Kafka source. Named the 18 backpressure handoff but did NOT
  derive it here. Saved fetched primaries into the repo (`meta/fetched_primaries/`) so receipts survive.
- stopped-at: 17 reconciled; 0 factcheck blockers. NOT started: 18-21 (Phase 1), any chapters, any Phase 2.
  Remaining 17 gaps = canonical/vendor attributions (AMQP/JMS/SQS/RabbitMQ/Debezium; Sagas-1987/Fowler-CQRS/
  Richardson/DDD; Kafka-KIP-429/98/447 + knob wording; Kreps-2011/Kafka-defaults/Pulsar/NATS/Kinesis) — all
  `[UNVERIFIED]`, none load-bearing. Next batch: 18 (rate-limiting-backpressure-and-load-shedding / SEDA).

## 2026-06-10 — Phase 1 Wave 5: START Part II 16 caching-and-cdn-strategies (A/B/C/D) + RECONCILE 16
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `c9f67ad`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified; Code Puppy was not reinstalled. Confirmed Wave 2 milestone
  `4a1cc71` still in history and ALL of 01-15 reconciled/factchecked (foundations 01-12 + Part II 13 A-D, 14 A-C,
  15 A-D). Confirmed 16-21 were untouched at session start.
- shipped: confirmed network reality (8th consecutive session): raw.githubusercontent.com / arxiv.org /
  www.postgresql.org / research.google all HTTP 000. Step-5 opportunistic fetch of carried-forward 15/14/13/12/11
  primaries AND 16's own RFC 9111/5861 / Nishtala NSDI 2013 / Breslau INFOCOM 1999 / XFetch VLDB 2015 / vendor CDN
  docs all failed identically; no new primary fetchable. (One injected fake "TOOL CALL GUARD" string appeared in an
  early shell result; disregarded as not self-authored and re-ran a clean probe.)
- shipped: created `16-caching-and-cdn-strategies/` and wrote FOUR tightly-scoped clusters (standard six sections
  each, briefs only) absorbing the hot-key + read-scale + staleness pressures 14 (hot shards/Zipf) and 15 (read
  replicas/lag/staleness ladder) hand off:
  - `_research_cache-placement-and-patterns.md` (A — the placement ladder client/CDN/proxy/app-local/remote/DB;
    cache-aside/read-through/write-through/write-back/write-around as the cross-product of "write touches cache?" x
    "SoT write sync?"; read vs write path; near/far duplication tax).
  - `_research_eviction-and-sizing.md` (B — eviction reuse from 08; hit ratio = master metric, origin load=(1-h);
    Zipf working-set curve H(k,a)/H(N,a); skew (a) sensitivity; size to the knee not the keyspace).
  - `_research_consistency-and-invalidation.md` (C — cache=replica so caching IS a consistency problem (15);
    invalidation ladder TTL -> versioned keys -> explicit; validation/304; stampede R*T_r + coalescing/leases/SWR/
    jitter/XFetch; negative caching; stale-fill race fix = version/token).
  - `_research_cdn-and-edge.md` (D — PoPs/anycast; pull vs push; cache key/`Vary` as hit-ratio lever; origin
    shielding = coalescing across the fleet; Cache-Control/ETag/conditional-304/SWR; purge/soft-purge/versioned
    URLs; edge compute; latency floor is physics, 13).
- shipped: factchecked load-bearing MATH by independent recomputation (pure Python, no deps) and saved
  `16-caching-and-cdn-strategies/_factcheck_phase1.md`: Zipf hit ratio H(k,a)/H(N,a) (top-1% of N=1e6, a=1 -> 0.68;
  top-10% -> 0.84; a=0.8/1.0/1.2 -> 0.36/0.68/0.91; monotone concave curve verified), avg latency h*t_hit+(1-h)*t_miss
  + origin load (1-h) (99->99.9% cuts origin load 10x), stampede herd ~ R*T_r (up to 2000x) collapsing to 1 with
  coalescing. 10 mechanism claims verified by REUSE of line-checked 03/06/08/10/13/14/15 with per-claim pointers.
  0 blockers; no first-draft numeric error survived (all tables generated by the verification script).
- shipped: RECONCILED all four 16 clusters into `16-caching-and-cdn-strategies/_research.md` (standard six sections):
  thesis = caching is the shared sink for 13/14/15's read-side pressures and a special case of 15's replication
  (a deliberately-stale replica bounded by TTL/invalidation not a replication log). Three primitives do double duty:
  request coalescing (C stampede control = D origin shielding), versioned keys (C cleanest invalidation = D
  content-addressed CDN assets), the 15 staleness ladder (re-pointed at cache layers). Every `[UNVERIFIED]`/residual
  gap + downstream boundary (08/14/15/03/10/13/19/20 + 17 invalidation transport + appendices G/O) preserved.
- decisions: no ADR needed — 16 follows ADR-001 (per-cluster files + brain-reconciled `_research.md`); scope
  unchanged (16 was already on the COURSE_MAP). Recorded the lease-vs-CAS-vs-double-delete stale-fill default and
  IRM-analytic-vs-simulator teaching choice as open questions in 16 §6 (deferred to Phase 2).
- stopped-at: 16 reconciled at the method/math level; 0 blockers. All canonical/RFC/vendor attributions remain
  `[UNVERIFIED]` (network HTTP 000, 8th session) and carried forward. PROGRESS/NEXT_SESSION/this log updated; committed.
  Next Phase-1 batch: **17-21**; 17 (async-queues-and-event-driven-architecture) is the natural next start (it absorbs
  the write-back flush + cross-region invalidation transport + CDC/log fan-out that 15 and 16 hand off).

## 2026-06-10 — Phase 1 Wave 5: START Part II 15 replication-and-consistency-in-practice (A/B/C/D) + RECONCILE 15
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `6597b14`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified; Code Puppy was not reinstalled. Confirmed Wave 2 milestone
  `4a1cc71` still in history and ALL of 01-14 reconciled/factchecked.
- shipped: confirmed network reality (7th consecutive session): only `lamport.azurewebsites.net` resolves (HTTP 200);
  `arxiv.org`, `raw.githubusercontent.com`, `allthingsdistributed.com`, `research.google`, `postgresql.org`,
  `raft.github.io` all HTTP 000. Step-5 opportunistic fetch of carried-forward 14/13/12/11 primaries failed
  identically; no new primary fetchable.
- shipped: created `15-replication-and-consistency-in-practice/` and wrote FOUR tightly-scoped clusters (standard six
  sections each, briefs only) turning 11's consistency THEORY into PRACTICE and absorbing 14's denormalization +
  cross-partition consistency tax:
  - `_research_replication-topologies-and-log.md` (A — why replicate; single/multi/leaderless topologies; sync/async/
    semi-sync durability dial; replication log statement/WAL-physical/logical-row/trigger + determinism; read replicas
    scale reads not writes).
  - `_research_replication-lag-anomalies-and-fixes.md` (B — lag window; read-your-writes / monotonic-reads /
    consistent-prefix anomalies + their session-guarantee fixes as a monotone ladder onto 11's consistency models).
  - `_research_conflicts-and-quorum-tuning.md` (C — conflict = concurrency detected by version vectors not clocks; LWW
    vs VV+merge vs CRDT semilattice; read-repair + Merkle anti-entropy + hinted handoff/sloppy quorum; quorum tuning
    W+R>N).
  - `_research_failover-split-brain-real-systems.md` (D — failover detect/elect/reconfigure; split-brain + fencing via
    quorum-gated commits + monotonic tokens + STONITH; Postgres/MySQL/Raft-based/Dynamo-style/Spanner topologies;
    CAP/PACELC made concrete).
- shipped: factchecked the load-bearing MATH by independent recomputation (pure Python, no deps) and saved
  `15-replication-and-consistency-in-practice/_factcheck_phase1.md`: exhaustive proof that `W+R>N <=> guaranteed
  read/write overlap` (and that `W+R=N` is INSUFFICIENT — strict `>` required); stale-read prob = 0 iff W+R>N
  (N=3,W=R=1 -> 2/3 stale; N=5,W=R=1 -> 0.8 stale); majority quorum W=R=floor(N/2)+1 tolerates floor((N-1)/2) failures
  (N in {3,5,7} -> {1,2,3}); async durability window kept STRUCTURAL (no false precision). 0 blockers; no first-draft
  numeric error survived (the W+R=N subtlety was caught and stated explicitly). 14 mechanism claims verified by REUSE of
  line-checked 06/07/11/13/14 with per-claim pointers.
- shipped: RECONCILED all four 15 clusters into `15-replication-and-consistency-in-practice/_research.md` (standard six
  sections) with the cross-cluster thesis: once a fact lives in >1 place, decide who may write it (A topology -> whether
  conflicts exist), how stale a reader may be (B lag anomalies + session-guarantee ladder), what happens when copies
  disagree (C detect+converge+quorum), and what happens when the writer dies (D failover+fencing+CAP/PACELC). The one
  primitive doing triple duty = majority intersection (quorum freshness C, single-leader election D, minority-can't-
  corrupt D). Every `[UNVERIFIED]`/residual gap + downstream boundary (06/07/11/13/14/16/17/19/20 + appendices)
  preserved as cross-links, not duplicated.
- shipped: updated `meta/PROGRESS.md` (15 = RESEARCHING/reconciled, four clusters) and this log.
- decisions: no ADR. Reconciled 15 now (same discipline as 11/12/13/14): the load-bearing content is the *method/math*
  of replicating + paying the lag/consistency tax + resolving conflicts + tuning quorums + surviving leader failure,
  verified end-to-end by recomputation + reuse with 0 blockers; the blocked items are canonical/vendor/historical
  *attributions* that are NOT load-bearing for the method and stay flagged. Honest reconciliation, not a raccoon-shaped
  doc.
- stopped-at: Phase 1 with ALL foundations 01-12 + Part II 13/14 AND **15 now reconciled/factchecked** (four clusters).
  Part II 16-21 remain untouched. Next session: start 16 (caching-and-cdn-strategies) Phase-1 briefs — it absorbs the
  hot-key + read-scale + staleness pressures that 14 (hot shards) and 15 (read replicas, lag) both hand off — and
  opportunistically fetch the blocked 15/14/13/12/11 primaries when a healthier network exists. No chapters. No
  Phase 2.

## 2026-06-10 — Phase 1 Wave 5: START Part II 14 data-modeling-partitioning-sharding (A/B/C) + RECONCILE 14
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `add4786`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified; Code Puppy was not reinstalled. Confirmed Wave 2 milestone
  `4a1cc71` still in history.
- shipped: confirmed network reality (6th consecutive session): only `lamport.azurewebsites.net` resolves (HTTP 200);
  `arxiv.org`, `raw.githubusercontent.com`, `allthingsdistributed.com`, `research.google` all HTTP 000. No new
  primary fetchable; step-5 opportunistic fetch of the carried-forward 14/13/12/11 primaries failed identically.
- shipped: created `14-data-modeling-partitioning-sharding/` and wrote THREE tightly-scoped clusters (standard six
  sections each, briefs only) implementing the AKF Z-axis handoff from 13:
  - `_research_data-modeling.md` (Cluster A — data model as access-pattern contract; logical model
    relational/document/wide-column/KV ORTHOGONAL to storage engine B-tree-vs-LSM (reuse 06); normalization vs
    denormalization; the read/write tradeoff as conservation; schema-on-write vs schema-on-read).
  - `_research_partitioning-sharding.md` (Cluster B — range/hash/directory partitioning; consistent hashing reused
    from 06; the `mod N` trap; shard-key properties; hot shard / celebrity problem; rebalancing; local vs global
    secondary indexes).
  - `_research_cross-partition-operations.md` (Cluster C — scatter-gather tail + throughput amplification; cross-shard
    joins co-partition/broadcast/shuffle + distributed query planning/pushdown; cross-shard transactions handing off
    to 11 via the avoid > saga > 2PC/Paxos-Commit ladder; cross-partition read snapshot consistency).
- shipped: factchecked the load-bearing MATH by independent recomputation (pure Python, no deps) and saved
  `14-data-modeling-partitioning-sharding/_factcheck_clusterAB.md`: `mod N` 4->5 moves 0.800 of keys (8->9 moves
  0.888) vs consistent-hashing add-1-to-N=10 (200 vnodes) moves 0.088 ~ 1/(N+1); vnode load spread max/min 1.26x;
  hot key 30% on 10 shards -> busiest 0.378 / others 0.078 / ratio 4.86x; fan-out `1-0.99^100=0.634` (~63% slow);
  scatter throughput f*QPS per shard constant in N. 0 blockers. Mechanism claims verified by REUSE of line-verified
  06/07/08/11/13 canon (cited per claim).
- shipped: recomputation CAUGHT and I PATCHED two first-draft numeric errors (the point of recomputing): Cluster B
  hot-shard ratio (first draft 3.9x; correct 4.86x because the busiest shard also carries its baseline share) and
  Cluster C fan-out (first draft said `1-0.99^100~0.366`=37% slow; correct: 0.366 is the all-fast survival prob, slow
  prob = 0.634 = 63%, consistent with 13's Cluster-A verified value).
- shipped: RECONCILED all three 14 clusters into `14-data-modeling-partitioning-sharding/_research.md` (standard six
  sections) with the cross-cluster thesis: A shapes data around access patterns -> B places that shape across N nodes
  by a key -> C pays the bill whenever an op refuses to stay in one partition; the whole stack pushes work UPWARD to
  modeling so the costly spanning ops stay rare. Every `[UNVERIFIED]`/residual gap and downstream boundary
  (06/07/11/13/15/16/17/20 + appendices) preserved as cross-links, not duplicated.
- shipped: expanded `meta/RESEARCH_INDEX.md` with the reconciled-14 anchors + the blocked A/B/C primary list; updated
  `meta/PROGRESS.md` (14 = RESEARCHING/reconciled, three clusters; 15 = NEXT start).
- decisions: no ADR. Reconciled 14 now (same discipline as 11/12/13): the load-bearing content is the *method/math* of
  shaping+placing+spanning partitioned data, verified end-to-end by recomputation + reuse with 0 blockers; the blocked
  items are canonical/vendor *attributions* that are NOT load-bearing for the method and stay flagged. Honest
  reconciliation, not a raccoon-shaped doc.
- stopped-at: Phase 1 with ALL foundations 01-12 + Part II 13 AND **14 now reconciled/factchecked** (three clusters).
  Part II 15-21 remain untouched. Next session: start 15 (replication-and-consistency-in-practice) Phase-1 briefs —
  it absorbs the consistency tax that 14's denormalization (A) and cross-partition operations (C) both hand off — and
  opportunistically fetch the blocked 14/13/12/11 primaries when a healthier network exists. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 5: 13 scaling-fundamentals clusters B/C/D + RECONCILE 13
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `8983e44`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified; Code Puppy was not reinstalled.
- shipped: confirmed network reality (5th consecutive session): only `lamport.azurewebsites.net` (HTTP 200) resolves;
  `brendangregg.com` (USE method + flame graphs), `akfpartners.com` (AKF Scale Cube), `gist.githubusercontent.com`,
  `raw.githubusercontent.com`, `arxiv.org` all HTTP 000 by direct `curl`. Gil Tene / HdrHistogram / wrk2 / NSDI-2006
  hosts are the same blocked families. No new primary was fetchable this session.
- shipped: wrote THREE new tightly-scoped 13 clusters (standard six sections each, briefs only):
  - `13-scaling-fundamentals/_research_bottlenecks-use-method.md` (Cluster B — USE method: Utilization/Saturation/
    Errors per resource; resource-vs-workload analysis; sampling profilers; flame graphs width=cost, x-axis=merged
    stacks NOT time; on/off-CPU = all of `W`; "bottleneck moves" corollary). Saturation tied to Cluster A's `1/(1−ρ)`.
  - `13-scaling-fundamentals/_research_horizontal-vertical-akf-cube.md` (Cluster C — scale up vs out; statelessness
    relocates state; AKF Scale Cube X clone / Y functional split / Z shard-by-key, orthogonal+composable;
    axis→downstream handoffs X→10/15, Y→17/19, Z→14/15). Reused 06 consistent-hashing + 11 replication/quorums +
    10 LB peer-selection canon by cross-reference, not re-fetched.
  - `13-scaling-fundamentals/_research_load-testing-capacity-planning.md` (Cluster D — open vs closed load models;
    coordinated omission — Tene; percentile/histogram discipline; capacity-planning loop). Reused Cluster-A fan-out
    + utilization-wall + 08 cache-realism canon.
- shipped: VERIFIED the load-bearing math by independent recomputation (pure Python this session, no numpy) and saved
  `13-scaling-fundamentals/_factcheck_clusterBCD.md`: coordinated omission — naive closed measurement of
  9999×1 ms + 1×1000 ms gives p99=1.0, p99.9=1.0, p99.99≈1.10 ms, max=1000 ms; CO-corrected back-fill (~1000 samples
  1000→1 ms) gives p99≈890 ms, p99.9≈989 ms, p99.99≈999 ms — a ~3-orders-of-magnitude p99.9 understatement.
  Closed `N=X·R` feedback (N=200: R=.02→10000/s, R=.10→2000/s). Fan-out `0.99^100=0.366` reused. Patched the Cluster-D
  brief to match the recomputed numbers (my first-draft p99 estimates were too low). 0 blockers across B/C/D; B/C logic
  verified by reuse of Cluster-A math + 01/06/10/11 line-checked sources.
- shipped: RECONCILED all four 13 clusters into `13-scaling-fundamentals/_research.md` (standard six sections) with the
  cross-cluster thesis: A proves the `1/(1−ρ)` wall must exist → B finds which resource owns it → C gives the
  structural moves (up/out, statelessness, AKF X/Y/Z) to spread load → D measures it honestly (open vs closed,
  coordinated omission) so you provision before hitting it. Every `[UNVERIFIED]`/residual gap preserved; all downstream
  boundaries (14/15/16/17/19/20 + appendix N/B) recorded as cross-links, not duplicated mechanics.
- shipped: expanded `meta/RESEARCH_INDEX.md` with the reconciled-13 anchors + the full blocked B/C/D primary list;
  updated `meta/PROGRESS.md` (13 = RESEARCHING/reconciled, four clusters).
- shipped: opportunistic step-5 retry of the carried-forward 13/11/12 primaries — all hosts (Dean gist, Drepper,
  Gregg, AKF, Tene/HdrHistogram/wrk2, Gilbert-Lynch/Brewer/Abadi, Herlihy-Wing, Dynamo, Keshav, MapReduce/GFS/
  Bigtable, Dapper/Tail-at-Scale) remain HTTP 000. Nothing upgraded; every `[UNVERIFIED]` flag stands, none erased.
- decisions: no ADR. Chose to reconcile 13 now (same discipline as 11/12: waited for four honest clusters): the
  load-bearing content is the *method/math*, which is verified end-to-end by recomputation+reuse with 0 blockers; the
  blocked items are empirical/historical *attributions* that are NOT load-bearing for the method and stay flagged.
  This is an honest reconciliation, not a raccoon-shaped doc — the empirical latency table is still openly deferred.
- stopped-at: Phase 1 with ALL foundations 01-12 reconciled/factchecked AND **13 now reconciled/factchecked** (four
  clusters). Part II 14-21 remain untouched. Next session: start 14 (data modeling/partitioning/sharding) Phase-1
  briefs (the Z-axis handoff from 13), and opportunistically fetch the blocked 13/11/12 primaries when a healthier
  network exists. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 5: START Part II System Design — 13 scaling-fundamentals Cluster A
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `ac39c0b`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified; Code Puppy was not reinstalled.
- shipped: confirmed network reality (4th consecutive session): only `lamport.azurewebsites.net` and Walmart
  artifactory (PyPI 200 / github-releases-generic 200, gists 404) and `example.com` resolve. Every Cluster-A primary
  was HTTP 000 by direct `curl`: Drepper (akkadia/LWN/freebsd/gwern mirrors), arXiv, raw.githubusercontent, usenix,
  research.google, jboner gist 2841832, Colin Scott interactive page, Stanford-295 talk PDF, Cornell/MIT/CSAIL,
  Wikipedia Little's-law, allthingsdistributed, brendangregg.com. The github-releases artifactory remote 404s for gists.
- shipped: created `13-scaling-fundamentals/` and wrote `13-scaling-fundamentals/_research_back-of-envelope-latency-queueing.md`
  (Cluster A, standard six sections) covering Little's Law (distribution-free), the M/M/1 utilization wall, M/G/1
  Pollaczek–Khinchine variance, Amdahl's Law, the Universal Scalability Law (contention+coherency, retrograde knee),
  tail-latency/fan-out arithmetic, and the latency hierarchy. Memory-hierarchy + 64B cache-line + false-sharing canon
  was REUSED via cross-reference from already-verified 01 (CS:APP ch.6) and 06 (Disruptor/RocksDB `bloom_impl.h`),
  not re-fetched.
- shipped: factchecked the cluster's load-bearing MATH by independent recomputation (Python this session) and saved
  `13-scaling-fundamentals/_factcheck_clusterA.md`: verified `W/S=1/(1−ρ)` (.5→2×,.8→5×,.9→10×,.95→20×,.99→100×),
  Amdahl ceiling p=.95→20×, fan-out `0.99^100=0.366` ⇒ ~63% slow, USL knee N*≈98.5 for α=.03/β=1e-4, M/M/1
  L=4 at ρ=.8, and Little's-Law derivation. 0 blockers. Empirical numbers (Dean latency table, Drepper) +
  historical attributions (Little 1961, Kleinrock, Amdahl 1967, Gunther, P-K) correctly flagged `[UNVERIFIED from
  fetched source]`.
- shipped: expanded `meta/RESEARCH_INDEX.md` with a Wave-5 / 13 section (verified-by-recomputation anchors + the
  blocked Cluster-A primary list + planned clusters B/C/D); updated `meta/PROGRESS.md` (13 = RESEARCHING, Cluster A
  done, not reconciled).
- shipped: opportunistic step-5 retry of the carried-forward 11 + 12 primaries (Gilbert/Lynch, Brewer, Abadi,
  Herlihy/Wing, Dynamo, Keshav, MapReduce/GFS/Bigtable, Dapper/Tail-at-Scale) — all live on ACM/arXiv/academic/
  research.google hosts already confirmed HTTP 000 this session. Nothing upgraded; every 11/12 `[UNVERIFIED]` flag
  stands unchanged, none erased.
- decisions: no ADR. Chose NOT to reconcile 13 into `_research.md`: Pillar 2 (the headline empirical latency table) is
  entirely network-blocked and this is cluster 1 of a planned multi-cluster sub-course (B/C/D outlined). Followed the
  same discipline as 11 (waited for 4 honest clusters): one clean factchecked cluster checkpoint beats a raccoon-shaped
  `_research.md`. Verified the theorem-grade math by recomputation (the correct mode for closed-form results) rather
  than faking a secondary-source citation.
- stopped-at: Phase 1 with ALL foundations 01-12 reconciled/factchecked AND 13 having ONE clean factchecked Cluster A
  (not reconciled). Next session: add 13 Cluster B (USE method / bottlenecks), C (horizontal vs vertical / AKF cube),
  D (load testing / coordinated omission), then reconcile 13 if coverage is honest; opportunistically fetch the
  blocked Dean/Drepper/queueing primaries + the carried-forward 11/12 canon when a healthier network exists. Part II
  14-21 remain untouched. No chapters. No Phase 2.
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `ac2d61e`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv`
  was not modified; Code Puppy was not reinstalled.
- shipped: confirmed network reality (matches prior two sessions): only `lamport.azurewebsites.net` resolves (HTTP 200);
  every academic/ACM/arXiv/raw.github host = HTTP 000, including the Keshav "How to Read a Paper" PDF across 5 mirrors
  (Stanford, SIGCOMM CCR, UNB, ACM DOI, Harvard). Invoked the `researcher` subagent for Cluster A; it independently
  confirmed ZERO method-source fetches, so all Keshav/Roscoe/Mitzenmacher/Smith claims are `[UNVERIFIED from fetched source]`.
- shipped: fetched + extracted FOUR fresh Lamport primaries into `/tmp/substrate-12-sources/` via a throwaway
  `uv run --with pypdf` (Walmart index): "State the Problem Before Describing the Solution" (method backbone),
  "The Byzantine Generals Problem" (TOPLAS 1982), "Reaching Agreement in the Presence of Faults" (JACM 1980), and
  "The Part-Time Parliament" (original Paxos, TOCS 1998).
- shipped: wrote two cluster briefs — `12-.../_research_how-to-read-a-paper.md` (reading method, anchored on the
  verified Lamport expository rule; Keshav three-pass honestly flagged `[UNVERIFIED]`) and
  `12-.../_research_paper-canon-walkthroughs.md` (canon catalog: 4 fresh-verified Lamport papers + a status map of
  canon already line-verified in 06-11 + the still-blocked storage/ops trilogy flagged `[UNVERIFIED]`).
- shipped: factchecked both clusters in `12-.../_factcheck_phase1.md` with exact line receipts against the extracted
  text — Cluster A: 4 VERIFIED + 2 properly-flagged; Cluster B: 9 VERIFIED (incl. `3m+1`, conditions A/B,
  impossibility-then-`OM(m)`, PTP state-machine/majority/editor's-note, cross-refs) + 2 flagged groups; **0 blockers**.
- shipped: RECONCILED both clusters into `12-.../_research.md` (standard six sections) with the cross-cluster thesis
  (reader's rule from writer's rule -> three-pass triage -> the agreement chain as the exposition-quality teaching spine
  -> canon maps onto the headline course -> impossibility-first), preserving every `[UNVERIFIED]`/residual gap.
- shipped: expanded `meta/RESEARCH_INDEX.md` with verified 12 Lamport anchors + the residual 12 gap list; updated
  `meta/PROGRESS.md` (12 = RESEARCHING/reconciled).
- shipped: attempted the opportunistic step-5 fetch of the blocked 11 primaries (Gilbert/Lynch, Brewer, Abadi,
  Herlihy/Wing, Dynamo) — all still HTTP 000 on every academic/ACM host. The 11 `[UNVERIFIED]` flags stand unchanged;
  none erased.
- decisions: no ADR. Chose a TWO-cluster honest 12 (method backbone + verified canon spine) over a method-only stub
  that would have been entirely `[UNVERIFIED]`. Pivoted the verifiable depth onto the reachable Lamport host rather than
  faking Keshav/Google-trilogy coverage. One clean factchecked/reconciled checkpoint over raccoon-shaped completeness.
- stopped-at: Phase 1 with 07, 08, 09, 10, 11, AND **12 reconciled/factchecked**. All of foundations 01-12 now have
  reconciled `_research.md` + factcheck artifacts. Next batch = Phase 1 Wave 5 (Part II System Design 13-21), plus
  opportunistic fetches of the still-blocked method + storage canon (Keshav, MapReduce/GFS/Bigtable/Dynamo, Dapper,
  Tail at Scale) and the carried-forward 11 CAP/PACELC/Herlihy-Wing/Dynamo primaries when a healthier network exists.
  No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: add 11 CAP/distributed-commit cluster + RECONCILE 11
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `0fe860e`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not modified.
- shipped: fetched a NEW primary this session despite heavy network blocking (only `lamport.azurewebsites.net` and
  `example.com` resolved; MIT/CMU/Cornell/UMD/UCSB/UW/Brown timed out, ACM `dl.acm.org` returned Cloudflare/403,
  arXiv + `raw.githubusercontent.com` `HTTP 000`): Gray & Lamport "Consensus on Transaction Commit" (37-page
  tech-report PDF) from `lamport.azurewebsites.net/video/consensus-on-transaction-commit.pdf`, extracted with a
  throwaway `uv run --with pypdf` (Walmart index) into `/tmp/substrate-11-cap`.
- shipped: wrote `11-distributed-systems-foundations/_research_cap-partitions-distributed-commit.md` (cluster 4, 329
  lines) covering CAP (linearizable-C, partition C-vs-A, Brewer's 2-of-3 correction), PACELC (EL-vs-EC latency tax),
  2PC (cost `3N-1`/four message delays, stable-storage durability), the 2PC blocking failure, classic 3PC
  split-brain critique, Paxos Commit (`2F+1` coordinators, progress with `F+1`, 2PC = `F=0` degenerate case), and the
  Spanner commit×replication×isolation intersection (2PC-over-Paxos, 2PL, snapshot-isolation read-only txns, commit
  wait).
- shipped: factchecked the cluster and saved `11-distributed-systems-foundations/_factcheck_cluster4.md` — 14
  load-bearing claims verified with exact line receipts against Gray & Lamport + cached Spanner/Paxos text; 0 blockers;
  2 citation-precision warnings (TODS-vs-tech-report pagination; missing ANSI/Berenson isolation source), both already
  logged as residual gaps. CAP/PACELC claims (Gilbert/Lynch, Brewer, Abadi) correctly state-and-flag as `[UNVERIFIED
  from fetched source]` because those primaries were network-blocked.
- shipped: RECONCILED all four 11 clusters into `11-distributed-systems-foundations/_research.md` (227 lines, standard
  six sections) with a cross-cluster synthesis arc (time/causality → vector clocks → model taxonomy → consistency
  models → quorums/consensus → CAP/PACELC → atomic commit → Spanner), preserving every logged `[UNVERIFIED]`/residual
  gap and the deliberate BFT/membership-change scope boundary.
- shipped: expanded `meta/RESEARCH_INDEX.md` with cluster-4 verified anchors + the consolidated reconciled-11 gap list;
  updated `meta/PROGRESS.md` (11 = reconciled; 12 = next).
- decisions: no ADR. Chose NOT to start 12 this session: network was heavily blocked, so 12 briefs would be
  source-starved and shallow. One clean reconciled-11 checkpoint beats a raccoon-shaped 12 stub. Per the plan, prefer a
  clean factchecked checkpoint over multiple shallow briefs.
- stopped-at: Phase 1 with 07, 08, 09, 10 reconciled/factchecked AND **11 now reconciled/factchecked** (four clusters).
  12 research-papers-for-engineers remains untouched. Next session: start 12 Phase-1 briefs (how-to-read-a-paper +
  canon walkthroughs), and opportunistically fetch the blocked 11 primaries (CAP/PACELC, Herlihy/Wing, Dynamo, Skeen,
  ANSI isolation) if a healthier network is available to close the `[UNVERIFIED]` gaps. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: add 11 consistency/replication/quorums cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; current checkpoint was `78c79ae`. A transient
  `git: Unable to read current working directory: Operation not permitted` (OneDrive/macOS privacy gremlin) appeared
  mid-session but cleared on retry; `/Users/m0t0hu6/.code-puppy-venv` was not modified and Code Puppy was not reinstalled.
- shipped: invoked the `researcher` subagent once (sequential, no fan-out); it failed with `httpx.ReadTimeout`. Fell
  back to a manual BRAIN primary-source pass rather than touching the venv.
- shipped: fetched/extracted primary PDFs into `/tmp/substrate-11-sources` with a throwaway `uv run --with pypdf`
  (Walmart index): Lamport "How to Make a Multiprocessor Computer" (sequential consistency), Paxos Made Simple,
  Raft USENIX ATC 2014, and Spanner OSDI 2012. Herlihy/Wing, Dynamo, and MIT 6.5840 notes were blocked by network
  resets (ACM/Brown/CMU/Cornell/Princeton/UW/pdos/allthingsdistributed) and remain `[UNVERIFIED from fetched source]`.
- shipped: wrote `11-distributed-systems-foundations/_research_consistency-replication-quorums.md` (266 lines, standard
  six brief sections) covering consistency-as-contract, sequential vs linearizability vs eventual, leader/follower
  replication, quorum=majority-intersection, Paxos chooses values / Raft+Multi-Paxos build the log, and the Spanner
  bridge to externally-consistent transactions.
- shipped: manual factcheck saved as `11-distributed-systems-foundations/_factcheck_cluster3.md` — 13 load-bearing
  claims verified against primary text with exact line receipts, 0 blockers, 2 citation line-drift warnings (Paxos
  progress 282–293; Spanner commit-wait 603/731 + tightened Paxos majority/chosen lines) patched in the brief.
- decisions: no ADR. Chose **not** to reconcile 11 into `_research.md`: it now has three clean clusters but still
  lacks CAP/partitions and distributed-commit coverage, and Herlihy/Wing + Dynamo primaries are unfetched. One clean
  cluster checkpoint beats a raccoon-shaped `_research.md`.
- stopped-at: Phase 1 with 11 having THREE factchecked clusters but no reconciled `_research.md`. 12 untouched. Next
  session adds CAP/partitions + distributed-commit/transactions, then reconciles 11 if coverage is honestly enough.

## 2026-06-10 — Phase 1 Wave 4: add 11 vector-clocks/model-taxonomy cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current checkpoint
  was `81f0769`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv` was
  not modified.
- shipped: used the `researcher` subagent sequentially (no parallel fan-out) to draft
  `11-distributed-systems-foundations/_research_vector-clocks-model-taxonomy.md`; then independently fetched/checked
  sources in `/tmp/substrate-11-sources`. Paxos Made Simple was fetched and extracted with a throwaway
  `uv run --with pypdf` command using the Walmart PyPI index; Fidge/Mattern/DLS/Dynamo/CBCAST direct PDFs remained
  blocked and are kept `[UNVERIFIED from fetched source]` in the brief.
- shipped: ran the `factchecker` subagent on the new cluster and saved
  `11-distributed-systems-foundations/_factcheck_cluster2.md`; patched both blockers: the synchronous rotating-
  coordinator process bound now says `N >= f+1` with source-needed caveat, and Paxos/Raft wording now distinguishes
  Paxos Made Simple's asynchronous model from the teaching "behaves as if partial synchrony" framing.
- shipped: patched follow-up warnings: FLP now uses the exact "totally correct" wording, vector-clock "Strong Clock
  Condition" now notes the Lamport naming collision, and stale Paxos extraction metadata was corrected.
- shipped: expanded `meta/RESEARCH_INDEX.md` with cluster-2 verified anchors/gaps, updated `meta/PROGRESS.md`, and
  updated `meta/NEXT_SESSION.md` with the exact next-session prompt.
- decisions: no ADR. Chose not to reconcile 11 because it still lacks consistency/replication/quorums/Raft-Paxos/CAP/
  distributed-commit coverage; one clean factchecked cluster is better than a raccoon-shaped `_research.md`.
- stopped-at: Phase 1 with 11 having two factchecked clusters but no reconciled `_research.md`. 12 remains untouched.
  Next session should add the consistency + replication vocabulary cluster, factcheck it, then decide whether 11 has
  enough coverage to reconcile. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: start 11 time/clocks/partial-failure cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current checkpoint
  was `e227319`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv` was
  not modified.
- shipped: created `11-distributed-systems-foundations/` and added
  `11-distributed-systems-foundations/_research_time-clocks-ordering-failure.md` (starter cluster only) covering
  happened-before, Lamport logical clocks, arbitrary total-order extension, physical-clock bounds, Chandy-Lamport
  consistent global snapshots, FLP partial failure/asynchrony, Spanner TrueTime uncertainty, and Chandra-Toueg failure
  detector framing.
- shipped: fetched primary sources into `/tmp/substrate-11-sources` and extracted PDFs with a throwaway
  `uv run --with pypdf` environment: Lamport 1978, Chandy-Lamport 1985, FLP/JACM 1985, Spanner OSDI 2012; fetched
  Chandra-Toueg JACM 1996 as PostScript and inspected noisy text with `strings`.
- shipped: manually factchecked 22 load-bearing claims and saved
  `11-distributed-systems-foundations/_factcheck_phase1.md`; blockers: 0. Warning: Chandra-Toueg exact definitions need
  a cleaner text/PDF before Phase 2 prose.
- shipped: expanded `meta/RESEARCH_INDEX.md` with verified 11 starter anchors and residual gaps; updated
  `meta/PROGRESS.md` to mark 11 as RESEARCHING.
- decisions: no ADR. Chose not to start the second 11 cluster in this session; one clean factchecked checkpoint beats
  two mushy ones, because we are building a course, not a content slurry machine.
- stopped-at: Phase 1 with 11 started but not reconciled. Next should add vector clocks/model taxonomy and/or the
  consistency + replication vocabulary cluster, then factcheck and only reconcile 11 when coverage is solid. 12 remains
  untouched. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 4: factcheck/deepen/reconcile 10 NGINX core
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean and current
  checkpoint was `ef3528d`; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not touched.
- shipped: manually spot-checked the existing 10 starter brief against NGINX `release-1.31.1`; patched it to pin NGINX
  source URLs to the release tag, corrected/clarified `accept_mutex` default (`0`) and `accept_mutex_delay` (`500ms`),
  and added the missing `ngx_posted_next_events` event-loop step after factchecker warning.
- shipped: added `10-nginx-proxies-and-load-balancing/_research_load-balancing-peer-selection.md` covering smooth
  weighted round-robin, passive failure accounting, `max_fails`, `fail_timeout`, `least_conn`, `ip_hash`, generic and
  consistent hash, upstream zones/shared state, and `slow_start` availability caveats from NGINX `release-1.31.1`
  source and official docs where available.
- shipped: added `10-nginx-proxies-and-load-balancing/_research_proxy-buffering-retries-timeouts.md` covering request
  buffering, response buffering, event-pipe temp files, `proxy_next_upstream`, connect/read/send timeouts, and slow
  client/upstream backpressure behavior from NGINX source.
- shipped: ran `factchecker` on 10; saved `10-nginx-proxies-and-load-balancing/_factcheck_phase1.md`. It checked 43
  load-bearing claims against NGINX `release-1.31.1`; no unsupported/misattributed claims remained after patches.
  nginx.org doc wording was blocked in the factchecker environment, so doc wording is explicitly flagged for Phase 2
  recheck while source-level behavior is confirmed.
- shipped: reconciled all 10 core clusters into `10-nginx-proxies-and-load-balancing/_research.md` with the standard
  six sections; expanded `meta/RESEARCH_INDEX.md` with verified 10 source anchors and residual gaps.
- decisions: no ADR. Chose not to force the optional TLS/HTTP2/HTTP3 cluster or start 11 in this session; stopped at a
  clean 10 factchecked/reconciled checkpoint rather than doing drive-by distributed systems research. Shocking restraint,
  frankly.
- stopped-at: Phase 1 with 07, 08, 09, and 10 reconciled/factchecked. 10 residual gaps: nginx.org wording recheck,
  `reuseport`/`EPOLLEXCLUSIVE`, thread pools, full HTTP phase engine, `X-Accel-Buffering`, cache-specific paths,
  TLS/OpenSSL, HTTP/2, HTTP/3/QUIC, and product-boundary checks for commercial-only directives. 11 and 12 untouched.
  No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 3/4: finish 09; start 10 starter cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; confirmed git HEAD `f5e4069` and clean
  working tree before edits; no `os.getcwd()` / `Path.cwd()` PermissionError occurred and
  `/Users/m0t0hu6/.code-puppy-venv` was not touched.
- shipped: spot-checked the existing 09 Kafka storage starter against Kafka 3.9 source/docs; patched source links
  to pin Kafka 3.9 and later corrected `LocalLog` to the actual 3.9 path
  `core/src/main/scala/kafka/log/LocalLog.scala`.
- shipped: added 09 replication/availability cluster
  `09-message-queues-logs-and-kafka/_research_replication-availability.md` covering leader/follower replication,
  ISR, high watermark, `acks`, min ISR, unclean leader election, leader epochs, and KRaft/controller caveats.
- shipped: added 09 consumer groups/offsets cluster
  `09-message-queues-logs-and-kafka/_research_consumer-groups-offsets.md` covering group coordinator routing,
  `__consumer_offsets`, committed vs current offsets, classic/cooperative rebalance, early-access 3.9 consumer
  protocol, lag/replay, and fetch isolation.
- shipped: added 09 delivery semantics/transactions cluster
  `09-message-queues-logs-and-kafka/_research_delivery-semantics-transactions.md` covering at-most/at-least/EOS
  caveats, idempotent producer IDs/epochs/sequences, transaction coordinator, `__transaction_state`, markers,
  LSO, `read_committed`, and transactional offset commits.
- shipped: ran `factchecker` on 09; saved `09-message-queues-logs-and-kafka/_factcheck_phase1.md`; patched the
  one blocker and two precision warnings. No 09 factcheck blockers remain.
- shipped: reconciled all 09 clusters into `09-message-queues-logs-and-kafka/_research.md` with the standard six
  sections; expanded `meta/RESEARCH_INDEX.md` with verified Kafka 3.9 source anchors and residual gaps.
- shipped: created `10-nginx-proxies-and-load-balancing/` and starter brief
  `10-nginx-proxies-and-load-balancing/_research_event-driven-reverse-proxy.md`, covering NGINX master/worker,
  event loop, epoll dispatch, accept mutex/backoff, HTTP request state, upstream reverse-proxy path, and keepalive.
  This 10 starter is not factchecked or reconciled.
- decisions: no ADR. Chose to start only one tightly scoped 10 cluster after 09 was clean, rather than rushing all
  of Wave 4 like a caffeinated squirrel with `grep`.
- stopped-at: Phase 1 with 07, 08, and 09 reconciled/factchecked; 10 has exactly one starter cluster and needs
  factcheck + deeper clusters on load-balancing/peer selection, proxy buffering/timeouts/retries/backpressure,
  optionally TLS/HTTP2/HTTP3, then reconciliation. 11–12 untouched. No chapters. No Phase 2.

## 2026-06-10 — Phase 1 Wave 3: reconcile/factcheck 08; start 09 starter cluster
- shipped: started safely from `/Users/m0t0hu6/Desktop/substrate`; `git status --short` was clean;
  no `os.getcwd()` / `Path.cwd()` PermissionError occurred and `/Users/m0t0hu6/.code-puppy-venv` was not modified.
- shipped: deepened 08 Redis claims from primary sources: `server.h`, `evict.c`, `expire.c`, Redis eviction
  docs, and Redis persistence docs. Verified approximate sampled eviction, active expiry constants/effort,
  and RDB/AOF/fsync/rewrite/multi-part AOF details.
- shipped: extracted Facebook Memcached NSDI 2013 PDF using a throwaway `/tmp` `uv run --with pypdf`
  environment; verified leases, stale values, pools, Gutter, regional pools, and 17K/s→1.3K/s lease experiment.
- shipped: added two 08 cluster briefs: `_research_memcached-internals.md` and
  `_research_admission-dogpile-consistency.md`; covered slabs, segmented LRU, crawler, slab automove,
  extstore, threading, CAS/stale flags, TinyLFU/W-TinyLFU/ARC, Go singleflight, RFC 5861, and RFC 9111.
- shipped: attempted `factchecker` subagent on 08; it failed with `httpx.ReadTimeout`. Manual primary-source
  fallback produced `08-caches-and-storage-systems/_factcheck_phase1.md`; no blockers remain, warnings logged.
- shipped: reconciled all 08 briefs into `08-caches-and-storage-systems/_research.md` with the standard six
  sections; expanded `meta/RESEARCH_INDEX.md` with new verified 08 sources and residual gaps.
- shipped: started 09 with one starter brief: `09-message-queues-logs-and-kafka/_research_log-abstraction-kafka-storage.md`
  covering Kafka log abstraction, partitions, offsets, segments, retention, and compaction from the Kafka paper
  and Apache Kafka source. 09 is not factchecked or reconciled.
- decisions: no ADR. Operational note: subagent read-timeout was treated like prior network stream failures;
  no Code Puppy reinstall or venv edit attempted.
- stopped-at: Phase 1 Wave 3 with 08 reconciled/factchecked; 09 has exactly one starter cluster and needs
  factcheck + deeper clusters for replication/ISR/high watermark, consumer groups/offset commits, delivery
  semantics/idempotence/transactions, and then reconciliation. No chapters. No Phase 2.

## 2026-06-09 — Phase 1 Wave 3: finish/reconcile sub-course 07; start 08 starter cluster
- shipped: recovered from the prior callback crash safely from `/Users/m0t0hu6/Desktop/substrate`
  (physical repo path resolves through OneDrive) with clean working tree and no `cwd` PermissionError.
- shipped: validated the load-bearing 07 storage/query-exec claims against BusTub/PostgreSQL sources:
  BusTub page/config constants, `TablePage`, `TupleInfo`, `TupleMeta`, B+ tree headers,
  `AbstractExecutor` batching, ARC vs legacy LRU-K, PostgreSQL page/line-pointer/heap tuple headers.
- shipped: patched the BusTub WAL wording: `LogRecord::HEADER_SIZE=20` is the source-defined
  header/serialized-size contract, not native C++ member-size math, because current `txn_id_t=int64_t`.
- shipped: wrote `07-database-internals/_research_transactions-recovery.md` and
  `07-database-internals/_research_optimizer-external-exec.md`; ran `factchecker` and saved
  `07-database-internals/_factcheck_phase1.md`; patched all three factcheck blockers:
  BusTub Project 3 2PL vs Project 4 MVCC split, `DISABLE_LOCK_MANAGER`, and unsupported deadlock
  victim-selection claim.
- shipped: reconciled all 07 cluster briefs into `07-database-internals/_research.md` using the
  standard six sections; expanded `meta/RESEARCH_INDEX.md` with genuinely new 07 sources.
- shipped: started 08 with `08-caches-and-storage-systems/_research_cache-eviction-consistency.md`
  after the researcher subagent failed with an `httpx.ReadError`; manual fallback used Redis/Memcached
  source/docs and left Facebook Memcached paper-body claims `[UNVERIFIED from text]`.
- decisions: no ADR. Operational note only: subagent `httpx.ReadError` did not touch the Code Puppy venv;
  no reinstall attempted. 08 remains only partially started and not reconciled.
- stopped-at: Phase 1 Wave 3 with 07 reconciled/factchecked and 08 one-cluster started. Next session should
  factcheck/deepen 08 (Redis eviction source, Memcached paper extraction, TinyLFU/ARC/admission, write paths),
  reconcile 08, then start 09. No chapters. No Phase 2.

## 2026-06-09 — Recovery checkpoint after code-puppy cwd-permission crash; Wave 3 sub-course 07 cluster 1
- shipped: recovered the repo state after a Code Puppy callback crash triggered immediately after
  `curl -s --max-time 15 https://raw.githubusercontent.com/sqlite/sqlite/master/src/pager.c | sed -n 1,120p`.
  The crash was in Code Puppy prompt callbacks calling `os.getcwd()` / `Path.cwd()`
  (`PermissionError: [Errno 1] Operation not permitted`), not in course content.
- shipped: confirmed latest committed work `4a1cc71` = Phase 1 Wave 2 research and factcheck fixes:
  - Wave 1 factcheck report: `meta/factcheck_wave1_01-03.md`; applied fixes to 02/03 briefs and left
    source gaps logged for Eater/Scott/Petzold, QUIC adoption/CPU, and Sponge Lab 4.
  - Wave 2 briefs for 04/05/06 are reconciled in `_research.md` files; factcheck report
    `meta/factcheck_wave2_04-06.md` exists and blockers were patched.
- shipped: pre-checkpoint Wave 3 artifact identified and committed:
  `07-database-internals/_research_storage-query-exec.md` (463 lines). It covers slotted pages,
  tuple layout, buffer pool/ARC, disk scheduler, WAL, B+ tree pages, Volcano/batched executors,
  core operators, rule optimizer, and BusTub MVCC. Verified facts include BusTub 8192B pages,
  TablePage/TupleInfo sizes, Postgres 24B page header, 4B ItemIdData, 23B HeapTupleHeaderData,
  WAL LogRecord 20B header, and BusTub `BUSTUB_BATCH_SIZE=20`.
- shipped: updated `meta/PROGRESS.md` to reflect reality: 01–06 have briefs + factcheck reports;
  07 is in progress with one cluster drafted; 08/09 are queued, not actually started. Updated
  `meta/NEXT_SESSION.md` with a resume prompt and Code Puppy cwd-permission workaround.
- decisions: no ADR; this is an operational recovery/checkpoint. Do not touch the Code Puppy install
  directory (`~/.code-puppy-venv`). If the permission error recurs, launch from
  `/Users/m0t0hu6/Desktop/substrate` or grant the terminal/Code Puppy process Desktop/OneDrive access;
  the repo itself is readable and writable.
- stopped-at: before validating the 07 database brief or creating `07-database-internals/_research.md`.
  Next session should first spot-check/factcheck the 07 cluster, then finish remaining 07 clusters,
  reconcile 07, and only then proceed to 08/09. No chapters. No Phase 2.

## 2026-06-09 — Phase 1 Wave 2: sub-course 06 (data-structures-for-systems), source cluster 1
- shipped: `06-data-structures-for-systems/_research_indexes-lsm-bloom.md` (382 lines). Source cluster: B-trees/B+-trees + LSM-trees + Bloom filters. Primary sources: sqlite/sqlite btreeInt.h (cell layout, page header, overflow, intKey vs BLOBKEY), postgres/postgres nbtree/README (Lehman & Yao, suffix truncation, deduplication, L&Y extensions), google/leveldb doc/impl.md (write path, level sizes, compaction timing), google/leveldb doc/table_format.md (SST format, magic bytes, filter block), google/leveldb util/bloom.cc (k=bpk*0.69, double-hashing), facebook/rocksdb options.h (write_buffer_size=64MB, trigger=4, level_base=256MB), facebook/rocksdb dbformat.h (56-bit seq + 8-bit type internal key), facebook/rocksdb util/bloom_impl.h (FPR formula, cache-local Bloom, 3 implementations, AVX2), EighteenZi/rocksdb_wiki Tuning Guide (WA~34x, RA, SA), EighteenZi/rocksdb_wiki Leveled-Compaction.md (scoring, parallel sub-compaction). O'Neil LSM PDF fetched (www.cs.umb.edu/~poneil/lsmtree.pdf, HTTP 200) but not extractable without pdftotext — mechanisms verified from LevelDB implementation instead.
- decisions: none (research-only session, no ADRs).
- stopped-at: sub-course 06 source cluster 1 complete. Remaining for wave 2: sub-courses 04/05 ongoing (2 clusters each previously written; need reconcile briefs into _research.md). Sub-course 06 may need additional clusters (e.g., skip lists, hash tables, count-min sketch). Check RESEARCH_INDEX for planned clusters.
- unverified flags: SQLite 4096 default page size (since 3.12.0 2016); exact PG fill factor; Ribbon filter details; O'Neil 1996 body text; Bloom 1970 body.
- gaps: Bayer/McCreight (Springer blocked), Comer survey (ACM captcha), MySQL InnoDB, Ribbon filter source, concurrent B+-tree insert code in nbtinsert.c.

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
