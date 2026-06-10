# Factcheck — Sub-course 11 Phase 1, Cluster 2
## Scope: `_research_vector-clocks-model-taxonomy.md`
## Factchecker: factchecker-393407 | Date: 2026-06-10
## Method: Adversarial claim extraction against cached primary sources in /tmp/substrate-11-sources/
##         and attempted re-fetch of all unverified sources.

Source availability confirmed:
- /tmp/substrate-11-sources/time-clocks.txt (42525 bytes) — Lamport 1978 CACM, extracted text.
- /tmp/substrate-11-sources/flp.txt (28462 bytes) — FLP JACM 1985, extracted text.
- /tmp/substrate-11-sources/paxos-simple.txt (26987 bytes) — Paxos Made Simple, EXTRACTED (see blocker note below).
- /tmp/substrate-11-sources/ct96.txt (660113 bytes) — CT96 PostScript, noisy (prior cluster warning preserved).
- Fidge 1988 / Mattern 1989: NOT fetchable. dls88.pdf = 103 bytes error page; mattern89.pdf = 16 bytes
  Cloudflare block. Charron-Bost 1991 DOI timed out.
- Dynamo 2007 allthingsdistributed.com: BLOCKED by Walmart proxy.
- Birman/Schiper/Stephenson 1991: NOT fetched.

---

## Summary verdict

- Load-bearing claims checked: 22
- BLOCKERS: 2 — must patch before Phase 2 or before reconciliation into _research.md
- WARNINGS: 4 — should patch before Phase 2 prose; do not escalate to hard errors if brief marks claim unverified
- PASSES: 16

---

## Claim table (UNSUPPORTED / MISATTRIBUTED / NEEDS-SOURCE first, then PASS)

| # | Claim (section) | Verdict | Source link / receipt | Note |
|---|----------------|---------|----------------------|------|
| 1 | §1.5: "Requires at most f+1 rounds where f is the number of crash failures, **and N >= 2f+1 processes**" for a simple rotating coordinator protocol in the synchronous crash-fault model. No citation given. Not marked [UNVERIFIED]. | **UNSUPPORTED** | No primary source available; claim contradicts standard crash-fault consensus results | BLOCKER. For crash failures in a synchronous model, N >= f+1 suffices for a rotating-coordinator approach — you only need one non-faulty coordinator to survive and respond. N >= 2f+1 is the majority-quorum threshold for Byzantine fault tolerance (where you need quorum intersections that exclude faulty processes). The simpler f+1-round rotating-coordinator only needs N > f = N >= f+1. The brief's formula is wrong for the protocol as described and would be wrong for Byzantine faults too (Byzantine needs 3f+1, not 2f+1). No source is cited and the claim is not flagged. Must be corrected. |
| 2 | §1.7 (and §4 misconceptions): "Paxos and Raft operate under **partial synchrony** (they assume message delivery is eventually bounded and failure detection is eventually reliable)." Presented as settled characterization of the original protocol. | **NEEDS-SOURCE** | Paxos Made Simple: "We use the customary **asynchronous**, non-Byzantine model." lines 47-52. | BLOCKER (context-dependent). Paxos Made Simple explicitly describes an asynchronous model, not partial synchrony. Lamport delegates liveness to "real time or randomness" mechanisms (line 260-264) while keeping the model asynchronous. The "partial synchrony" framing is a common teaching characterization (consistent with DLS88's theoretical framework) but is not the framing Lamport uses in the primary source. Raft paper is unfetched. As written — stated as settled fact without qualification — this is a misframing relative to the primary source. Recommend patching to: "Paxos and Raft are commonly analyzed under partial synchrony assumptions; Paxos Made Simple itself uses an asynchronous model but requires timing assumptions (randomness or real time) for liveness." Affects both §1.7 and the §4 misconceptions note about FLP/Paxos. |
| 3 | §source-note header: "Paxos Made Simple was fetched from lamport.azurewebsites.net but the PDF is FlateDecode-compressed, so text extraction failed; it is marked accordingly." | **UNSUPPORTED** | /tmp/substrate-11-sources/paxos-simple.txt (26987 bytes, timestamp 10 Jun 16:17) | WARNING. The text was successfully extracted — the file exists and contains all sections through references. This stale note causes the brief to incorrectly label Paxos Made Simple [marked accordingly], understating how much of it is now verifiable. Paxos claims can be directly checked. Recommend removing the extraction-failure note and re-verifying Paxos claims. Does not by itself block; the Paxos claims check out in substance, but the model framing (claim #2) is still a blocker. |
| 4 | §1.2: "Strong Clock Condition (the bidirectional property that scalar clocks cannot satisfy): a → b iff VC(a) < VC(b)." Term presented as if it is standard consensus terminology for vector clocks. | **NEEDS-SOURCE** | Lamport 1978 lines 543-547 defines "Strong Clock Condition" for **physical clocks** only. Fidge 1988 / Mattern 1989 unfetchable. | WARNING. The term "Strong Clock Condition" as applied to vector clocks (bidirectionality) originates in Fidge 1988 and Mattern 1989. Lamport 1978 also uses "Strong Clock Condition" (lines 543-547) but for a completely different thing: an extension of the ordinary Clock Condition to physical-world causal order and physical clocks. The brief applies the term correctly in its context (vector clocks) but the source for the terminology is unverified. Because Fidge/Mattern are already properly marked [UNVERIFIED from fetched source] throughout §1.2, this is a warning rather than a blocker. However, the description "the Strong Clock Condition" implies settled terminology; recommend adding a note that the term comes from the Fidge/Mattern literature pending source confirmation, and note the potential naming overlap with Lamport's distinct physical-clock usage. |
| 5 | §1.6: "No consensus protocol can guarantee termination in this model with even one crash failure. (FLP Theorem 1, fetched text.)" | **SUPPORTED (minor paraphrase gap)** | FLP line 187: "THEOREM 1. No consensus protocol is **totally correct** in spite of one fault." | WARNING. The paraphrase substitutes "guarantee termination" for "totally correct." "Totally correct" in FLP means both safe and live (valid safety + liveness conditions). Paraphrasing as "guarantee termination" captures the liveness failure but silently drops the safety/validity requirement. The FLP proof is more nuanced: it shows the protocol cannot be both safe and live. Imprecision is low-stakes here since the liveness failure is the headline result, but for a precision course this should be: "FLP Theorem 1 shows no consensus protocol can be totally correct (safe AND live) in the fully asynchronous model in spite of one fault." |
| 6 | §1.1: Lamport Clock Condition quote: "For any events a, b: if a --> b then C(a) < C(b). Note that we cannot expect the converse condition to hold as well, since that would imply that any two concurrent events must occur at the same time. In Figure 1, p2 and p3 are both concurrent with q3, so this would mean that they both must occur at the same time as q3, which would contradict the Clock Condition because p2 ---> p3." | **SUPPORTED** | time-clocks.txt lines 238-248: exact match (minor OCR: p.~ = p3 in the source; not a content difference) | PASS. Quote is accurate. The source text says "p.~" where the brief says "p3" — this is an OCR artifact in the extracted PDF, not a brief error. |
| 7 | §1.1: "Lamport explicitly proves the Clock Condition is necessarily asymmetric" and the converse would force concurrent events to have the same timestamp, contradicting the Clock Condition itself. | **SUPPORTED** | time-clocks.txt lines 238-248 | PASS. Correctly describes Lamport's argument. |
| 8 | §1.2: Vector clock Rule 1 (local step: increment before each local event), Rule 2 (send: attach current vector), Rule 3 (receive: max merge then increment). Comparison: VC(a) <= VC(b) iff each component <=; VC(a) < VC(b) iff <= and !=; || iff incomparable. | **NEEDS-SOURCE** (properly flagged) | Fidge 1988 / Mattern 1989: unfetchable. Standard textbook algorithm; brief marks [UNVERIFIED from fetched source]. | PASS (properly flagged). The algorithm is standard and matches every major secondary source (Coulouris, Tanenbaum, Lynch, MIT 6.5840). Flagging is appropriate. No phase-gate risk since the brief does not harden the claim into prose certainty. |
| 9 | §1.2: O(N) lower bound on vector size: "detecting concurrency requires at least O(N) state [UNVERIFIED from fetched source; see Charron-Bost 1991 which proved that N integers are necessary and sufficient]." | **NEEDS-SOURCE** (properly flagged) | Charron-Bost, "Concerning the size of logical clocks in distributed systems," IPL 1991. DOI timed out. | PASS (properly flagged). The Charron-Bost result is well-cited in the field. Flagging is appropriate. |
| 10 | §1.3: Amazon Dynamo (SOSP 2007) uses version vectors to detect conflicts when multiple replicas diverge during a network partition; application must resolve siblings. | **NEEDS-SOURCE** (properly flagged) | Dynamo SOSP 2007: blocked. allthingsdistributed.com blocked by proxy. | PASS (properly flagged). Standard result from Dynamo literature. Brief marks [UNVERIFIED from fetched source]. |
| 11 | §1.3: Riak introduced "dotted version vectors" to fix a bug where concurrent writes from the same client could be incorrectly discarded as dominated. Attribution to Preguica et al. 2010. | **NEEDS-SOURCE** (properly flagged) | Not fetched. | PASS (properly flagged). The dotted version vector refinement is a real and well-documented contribution; the attribution to Preguica et al. is standard in the literature but not confirmed from primary source here. |
| 12 | §1.4: CBCAST (Birman, Schiper, Stephenson 1991, ACM TOCS): causal delivery holds a message from process j until (a) VV_m[j] = VC_local[j] + 1, AND (b) VV_m[k] <= VC_local[k] for all k != j. | **NEEDS-SOURCE** (properly flagged) | Birman/Schiper/Stephenson 1991, DOI: 10.1145/128738.128742. Not fetched. | PASS (properly flagged). The delivery conditions described are standard CBCAST as universally cited. Flagging appropriate. |
| 13 | §1.5: "The FLP paper confirms: 'solutions are known for the synchronous case, the Byzantine Generals problem' (fetched text, line 16)." | **SUPPORTED** | flp.txt line 16: exact match | PASS. Quote is exact. |
| 14 | §1.5: "Byzantine Generals paper (Lamport, Shostak, Pease 1982) works precisely because it assumes a synchronous model with known round bounds." | **SUPPORTED** | FLP line 16 establishes that the synchronous case has known solutions. The Lamport-Shostak-Pease paper is the standard reference for this. Not directly verified from text but well-established and derivable from FLP's own framing. | PASS. Standard attribution; synchrony assumption for Byzantine Generals is universally confirmed. |
| 15 | §1.6: FLP asynchronous model: three-point definition including "no assumptions about relative speeds or delay time," "no access to synchronized clocks / no time-outs," and "impossible to tell whether another has died or is just running slowly." | **SUPPORTED** | flp.txt lines 81-87: exact text confirmed | PASS. All three conditions confirmed. |
| 16 | §1.6: "FLP defines the asynchronous model with three explicit non-assumptions" and "No consensus protocol can guarantee termination in this model with even one crash failure." | **SUPPORTED** | flp.txt lines 80-87 (model) and line 187 (theorem). | PASS (with minor paraphrase caveat — see claim #5). |
| 17 | §1.7: DLS88 (JACM 1988) defines partial synchrony. Paper exists, topic confirmed via FLP's reference 10 at lines 365-368. | **SUPPORTED** | flp.txt lines 365-368: "DWORK, C., LYNCH, N., AND STOCKMEYER, L. Consensus in the presence of partial synchrony. In Proceedings of the 3rd Annual ACM Symposium on Principles of Distributed Computing (Vancouver, B.C., Canada, Aug. 27-29). ACM, New York, 1984, pp. 103-118." | PASS for existence and topic. DOI 10.1145/42282.42283 is the 1988 JACM journal version; FLP cites the 1984 PODC conference version — these are distinct publications. The brief cites both in different places; the DOI in the sources table is correctly the JACM version. |
| 18 | §1.7: DLS88 Model 1 (unknown bounds) and Model 2 (GST) exact definitions, and proof that consensus is solvable in both. | **NEEDS-SOURCE** (properly flagged) | DLS88 not fetched (103-byte error page). | PASS (properly flagged). The two-model taxonomy is the standard description of DLS88 in all secondary literature. The brief correctly marks it [UNVERIFIED from fetched source]. |
| 19 | §1.7: "GST (Global Stabilization Time) is a theoretical construct — an unknown future time after which the synchrony bounds hold. A correct protocol must not require knowing when GST occurs." | **NEEDS-SOURCE** (properly flagged) | DLS88 not fetched. | PASS (properly flagged). Description matches all secondary literature on DLS88. |
| 20 | §1.7: FLP conclusion (lines 325-333) quote motivating partial synchrony and citing DLS88. | **SUPPORTED** | flp.txt lines 325-333: exact match (brief elides the parenthetical "(For example, termination might be required only with probability 1.)" with "[...]" which is acceptable) | PASS. |
| 21 | §1.8: Chandra-Toueg failure detector taxonomy (◇S = eventually strong: strong completeness + eventual accuracy; ◇W = eventually weak; ◇S sufficient for consensus; reduction ◇W to ◇S). | **NEEDS-SOURCE** (properly flagged with prior cluster warning preserved) | CT96 PostScript — noisy extraction. Prior cluster factcheck: PASS WITH WARNING. | PASS (properly flagged). Brief preserves the prior cluster warning about CT96 noisy extraction. |
| 22 | §1.8: "DLS Model 2 and Chandra-Toueg's eventually-accurate failure detectors are 'essentially equivalent'." | **NEEDS-SOURCE** (properly flagged) | Neither DLS88 nor CT96 confirmed from clean text. | PASS (properly flagged). Known result in distributed systems theory but not confirmed from fetched primary sources. The brief correctly marks it [UNVERIFIED exact equivalence from fetched source]. |

---

## BLOCKERS requiring patch before Phase 2

### BLOCKER 1 — N >= 2f+1 claim in §1.5

**Location**: Section 1.5, fourth bullet under "With exact failure detection, consensus becomes solvable."

**Current text**:
```
Requires at most f+1 rounds where f is the number of crash failures, and N >= 2f+1 processes.
```

**Problem**: The N >= 2f+1 bound is unsourced and incorrect for a simple rotating coordinator
in the synchronous crash-fault model. For crash faults, the minimum process count for a
rotating coordinator is N >= f+1 — you need exactly one non-faulty coordinator to survive and
respond within the known timing bound. N >= 2f+1 is the majority-quorum threshold; it applies
when a protocol requires a quorum of correct processes to overlap, which is not what the described
"try coordinator 1, if silent try coordinator 2" protocol does. (For Byzantine faults the threshold
is 3f+1, not 2f+1.) No citation given; not marked [UNVERIFIED].

**Required patch**:
```
Requires at most f+1 rounds where f is the number of crash failures, and N >= f+1 processes
(at least one correct coordinator must survive). Note: quorum-based protocols that additionally
require majority overlap for validity need N >= 2f+1, but the pure rotating-coordinator
timeout scheme only requires N > f. [Source needed for f+1 round lower bound — standard result,
see Lynch 1996 "Distributed Algorithms" or equivalent.]
```

---

### BLOCKER 2 — Paxos model framing in §1.7 and §4

**Location**: Section 1.7 third paragraph; Section 4 misconceptions ("FLP proves Paxos/Raft cannot work").

**Current text §1.7**:
```
This is exactly the behavior of Paxos and Raft: they guarantee safety unconditionally; they
guarantee liveness only when a stable leader can gather a quorum of responding replicas.
```
(This part is fine.)

**Current text §4 misconceptions**:
```
Paxos and Raft operate under partial synchrony (they assume message delivery is eventually
bounded and failure detection is eventually reliable). They are not guaranteed to terminate in
fully asynchronous conditions, but they are safe in all conditions and live when the synchrony
assumption holds.
```

**Problem**: Paxos Made Simple (now fully extracted at /tmp/substrate-11-sources/paxos-simple.txt)
explicitly declares "We use the customary asynchronous, non-Byzantine model" (line 47). Lamport
frames liveness as requiring "either randomness or real time — for example, by using timeouts"
(lines 262-263) but does not call this "partial synchrony." Describing Paxos as "operat[ing]
under partial synchrony" as a settled fact is not what the primary source says; it is a teaching
characterization consistent with DLS88 but not attributed there.

**Required patch** (§4 misconceptions only — the §1.7 prose is acceptable as is):
Replace the partial synchrony claim in §4 with:
```
Paxos and Raft are not guaranteed to terminate in fully asynchronous conditions; that is
what FLP proves. Paxos Made Simple describes the protocol using an asynchronous model but
notes that liveness requires "either randomness or real time — for example, by using timeouts"
(Lamport 2001, line 263). In practice this means Paxos and Raft behave as if operating under
partial synchrony: safe in all conditions, live when message delivery is timely enough for
leader election to succeed.
```

---

### SUPPLEMENTARY NOTE — Paxos Made Simple extraction

The brief's source-availability header says Paxos Made Simple text extraction failed. This is
stale: /tmp/substrate-11-sources/paxos-simple.txt (26987 bytes, 10 Jun 16:17) contains the
full text including the Safety, Progress, and Implementation sections. Future passes should
source Paxos claims directly from this file. No patch to the claim body required, but the
source-note should be updated when the brief is reconciled.

---

## Warnings summary (non-blocking, must address before Phase 2 prose)

| # | Location | Issue | Recommendation |
|---|----------|-------|----------------|
| W1 | §1.2 "Strong Clock Condition" | Term is used for vector clock bidirectionality (from Fidge/Mattern literature), but Lamport 1978 lines 543-547 defines the same term for physical clocks (different meaning). Fidge/Mattern are unverified. | Add: "(in the vector clock literature, following Fidge 1988 and Mattern 1989 [UNVERIFIED from fetched source]; note: Lamport 1978 uses the same term for a distinct physical-clock property in §5 of his paper)" |
| W2 | §1.6 / §4 | Brief paraphrases FLP Theorem 1 as "No consensus protocol can guarantee termination ... with even one crash failure." Actual theorem: "No consensus protocol is **totally correct** in spite of one fault." "Totally correct" means both safe and live. The paraphrase captures the liveness failure but loses the safety dimension. | Add clarification: "FLP Theorem 1 uses the term 'totally correct,' meaning both safe and live; the impossibility is that you cannot guarantee both properties simultaneously in a fully asynchronous model." |
| W3 | §source header | Paxos Made Simple extraction marked as failed; it is actually available in /tmp/substrate-11-sources/paxos-simple.txt. | Update when reconciling into _research.md. |
| W4 | §1.8, §3 | Claim that DLS Model 2 and CT96 eventually-strong failure detectors are "essentially equivalent" is well-known but unconfirmed from fetched primary sources. Not hardened into prose certainty in the brief. | Flag for Phase 2 sourcing; cannot be used as a confident prose claim until CT96 or DLS88 text is confirmed. |

---

## Confirmed PASS claims with source receipts

| Claim | Source | Line(s) |
|-------|--------|---------|
| Clock Condition: if a→b then C(a)<C(b) | time-clocks.txt | 238-239 |
| Converse argument: demanding converse forces concurrent events to same time, contradicting Clock Condition | time-clocks.txt | 240-247 |
| FLP model: no speed assumptions, no synchronized clocks, no death detection | flp.txt | 81-87 |
| FLP Theorem 1 statement | flp.txt | 187 |
| FLP line 16: "solutions are known for the synchronous case, the 'Byzantine Generals' problem" | flp.txt | 16 |
| FLP conclusion motivating partial synchrony research | flp.txt | 325-333 |
| FLP cites DLS88 (PODC 1984 conference version) as reference [10] | flp.txt | 365-368 |
| Paxos safety unconditional | paxos-simple.txt | 264, 391 |
| Paxos liveness requires distinguished proposer + majority quorum | paxos-simple.txt | 252-265 |
| Paxos liveness requires randomness or real-time (timeouts) | paxos-simple.txt | 261-264 |
| Paxos uses asynchronous non-Byzantine model | paxos-simple.txt | 47 |
| All DLS88 / Fidge 1988 / Mattern 1989 / Dynamo / CT96 / CBCAST claims correctly marked [UNVERIFIED from fetched source] | — | — |
| GST non-detectability misconception correctly marked [UNVERIFIED] | — | — |
| O(N) lower bound (Charron-Bost 1991) correctly marked [UNVERIFIED] | — | — |
| Vector clocks vs. version vectors distinction (different problem, not just optimization) | Consistent with Dynamo literature (unverified); correctly distinguished and flagged | — |

---

## Phase gate ruling

**NOT CLEAR for Phase 2 prose.** Two blockers must be patched:

1. §1.5: Replace "N >= 2f+1" with "N >= f+1" for rotating-coordinator crash-fault synchronous
   consensus and add source-needed flag.
2. §4 misconceptions: Reframe "Paxos and Raft operate under partial synchrony" to accurately
   reflect that Paxos Made Simple uses an asynchronous model with timing requirements for liveness,
   not the DLS partial synchrony framing.

After those patches, the brief is clean for Phase 1 use. All other NEEDS-SOURCE claims are
properly flagged in the brief itself and do not introduce false confidence.

---

## Post-patch recheck
## Re-checker: factchecker-69ca1b | Date: 2026-06-10
## Scope: Re-examine only the five prior blockers/warnings; no new claims extracted.

### Source files confirmed still present

| File | Bytes | Note |
|------|-------|------|
| /tmp/substrate-11-sources/flp.txt | 28 462 | FLP JACM 1985, extracted text |
| /tmp/substrate-11-sources/paxos-simple.txt | 26 987 | Paxos Made Simple, extracted text |
| /tmp/substrate-11-sources/time-clocks.txt | 42 525 | Lamport 1978 CACM, extracted text |

---

### Recheck table — prior blockers/warnings only

| Prior item | What the patch changed | Recheck verdict | Source evidence | Residual note |
|---|---|---|---|---|
| **BLOCKER 1** — §1.5 rotating coordinator N bound | Text now reads: `N >= f+1 processes (at least one correct coordinator must survive). Note: quorum-based protocols … need N >= 2f+1, but the pure rotating-coordinator timeout scheme only requires N > f. [Source needed … see Lynch 1996]` | **RESOLVED** | No primary source contradicts the corrected formula; the fix correctly scopes N >= 2f+1 to quorum-only protocols and keeps a [source-needed] flag for the f+1-round lower bound. The original unsourced, unflagged N >= 2f+1 claim is gone. | None. Source-needed flag remains appropriate; must be pinned to Lynch 1996 or equivalent before Phase 2 prose. |
| **BLOCKER 2** — §4 Paxos/Raft partial synchrony framing | Text now reads: "Paxos Made Simple describes Paxos using an asynchronous, non-Byzantine model, but notes that liveness requires 'either randomness or real time — for example, by using timeouts' (Lamport 2001, extracted lines around 260–264). In practice, Paxos and Raft behave **as if** operating under partial synchrony …" | **RESOLVED** | paxos-simple.txt line 47: "We use the customary asynchronous, non-Byzantine model" — exact match. paxos-simple.txt line 263: "either randomness or real time—for example, by using timeouts." Line 265: "safety is ensured regardless of the success or failure of the election." All three verified. | None. The "behave as if" hedge is factually appropriate. |
| **W3** — Stale Paxos extraction note | **NOT patched in the brief.** The sources table (line 352) still reads: `FETCHED (PDF compressed, text not extracted)`. The open-questions §6 (lines 511–514) still says extraction failed and recommends installing pdftotext. The body of §4 now correctly cites extracted lines, creating an internal contradiction. | **STILL OPEN** | paxos-simple.txt (26 987 bytes, dated 10 Jun 16:17) is fully available and is actively used in the §4 patch. The metadata note is factually false. | Non-blocking for Phase 1 cluster checkpoint (the claims themselves are correctly sourced in the body). Must be corrected when reconciling into `_research.md`; the stale note should be replaced with "FETCHED and TEXT EXTRACTED — see /tmp/substrate-11-sources/paxos-simple.txt." |
| **W2** — FLP theorem paraphrase | Text now reads: `FLP Theorem 1 says no consensus protocol can be "totally correct" in this model in spite of one fault. Here "totally correct" means the protocol cannot guarantee both the required safety/validity properties and liveness/termination under the fully asynchronous assumptions.` | **RESOLVED** | flp.txt line 187: "THEOREM 1. No consensus protocol is totally correct in spite of one fault." flp.txt lines 182–186: "A consensus protocol P is totally correct in spite of one fault if it is partially correct, and every admissible run is a deciding run." The brief now quotes "totally correct," explains it covers both validity/safety and liveness, and does not reduce it to "guarantee termination" alone. | None. Minor precision note: FLP proves that given partial correctness (safety) you cannot also guarantee all admissible runs terminate — i.e., liveness fails, not safety. The brief's "cannot guarantee both" phrasing is directionally accurate for Phase 1 purposes. |
| **W1** — Strong Clock Condition naming collision | Text now reads: `Strong Clock Condition in the vector-clock literature (following Fidge/Mattern, still [UNVERIFIED from fetched source]; note Lamport 1978 uses the same phrase for a distinct physical-clock property):` | **RESOLVED** | time-clocks.txt line 543: "Strong Clock Condition. For any events a, b in O°: if a --> b then C(a) < C(b). This is stronger than the ordinary Clock Condition because ~ is a stronger relation than →. It is not in general satisfied by our logical clocks." Confirms Lamport's usage is for physical clocks (the relation involving physical causality in special relativity), completely distinct from vector-clock bidirectionality. The brief now correctly flags the naming collision inline. Fidge/Mattern remain [UNVERIFIED from fetched source], so the full claim cannot be hardened. | None for Phase 1. The collision note is present; Fidge/Mattern primary sources must be obtained before the term is used as settled prose in Phase 2. |

---

### Post-patch summary verdict

| Item | Prior status | Recheck status |
|---|---|---|
| BLOCKER 1 — §1.5 N bound | BLOCKER | **CLEARED** |
| BLOCKER 2 — §4 Paxos framing | BLOCKER | **CLEARED** |
| W3 — stale Paxos extraction note | WARNING (non-blocking) | **STILL OPEN — non-blocking** |
| W2 — FLP "totally correct" paraphrase | WARNING | **CLEARED** |
| W1 — Strong Clock Condition naming | WARNING | **CLEARED** |

**Phase 1 cluster-checkpoint ruling (post-patch):**
**CLEAR for Phase 1 cluster checkpoint use.**

Both blockers are resolved. The three prior warnings are either cleared (W1, W2) or confirmed
non-blocking (W3). The remaining open item — the stale extraction metadata in the sources table
and §6 open-questions — is a documentation inconsistency that does not introduce any false
factual claim into the body text; all Paxos body claims are correctly sourced from the
extracted text. This brief can be used to proceed to reconciliation into
`11-distributed-systems-foundations/_research.md`.

**Required before Phase 2 prose (carry-forward):**
1. Source the f+1-round crash-fault lower bound to Lynch 1996 or equivalent.
2. Obtain Fidge 1988 / Mattern 1989 primary text before hardening vector-clock algorithm
   statements or the Strong Clock Condition into prose certainty.
3. Obtain DLS88 primary text before hardening Model 1 / Model 2 / GST definitions.
4. CT96 PostScript extraction remains noisy; clean text version needed for Chandra-Toueg
   exact theorem statements (carry-forward from cluster 1, unchanged).
5. Historical note: the stale Paxos extraction note was still open at the instant of this factchecker
   recheck, then BRAIN patched it immediately afterward; see the next section.

---

## BRAIN metadata patch after post-patch recheck
## Date: 2026-06-10

After the post-patch recheck above, BRAIN also patched the remaining non-blocking W3 metadata issue in
`_research_vector-clocks-model-taxonomy.md`:

- Sources table now marks Paxos Made Simple as `VERIFIED (fetched + extracted via pypdf to /tmp/substrate-11-sources/paxos-simple.txt)`.
- Open questions now say Paxos Made Simple extraction is available and list the verified anchors:
  asynchronous non-Byzantine model, progress via distinguished proposer/majority, and liveness needing randomness or real time such as timeouts.

Result: W3 is resolved for the cluster brief. Carry-forward gaps remain: Fidge/Mattern primary text,
DLS88 primary text, cleaner CT96 text, Dynamo/version-vector primary text, CBCAST primary text, and a
source pin for the f+1 rotating-coordinator crash-fault result before Phase 2 prose.
