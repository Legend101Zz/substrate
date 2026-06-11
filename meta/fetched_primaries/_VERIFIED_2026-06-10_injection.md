# VERIFIED 2026-06-10 (Wave 15) — Indirect Prompt Injection primary for sub-course 33

Fetched + text-extracted + verified verbatim for **33-safety-and-proactive-self-evolving-agents**.
Extraction used the throwaway `/tmp/pdfx-venv` (uv + pypdf from Walmart external-pypi); the venv was
NOT removed only because `/tmp` is ephemeral — `~/.code-puppy-venv` was never touched.

## Primary

- **Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz — "Not what you've signed up for:
  Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"**
  (AISec '23 / arXiv **2302.12173**).
  - Files: `greshake-injection-2302.12173.pdf` (7.3 MB, 33 pp), `greshake-injection-2302.12173.txt`
    (116,724 chars).
  - Source: `https://arxiv.org/pdf/2302.12173` (HTTP 200, arxiv reachable Wave 15).

## Load-bearing claims VERIFIED verbatim (line refs into the .txt)

1. **Data/instructions are not separated (the root cause).** "We argue that LLM-Integrated
   Applications **blur the line between data and instructions**." (L33-34; restated L96, L254-255:
   "the line between data and code (i.e., instructions in natural language) would get blurry").
   → This is the one idea of 33: a tool result / retrieved passage / memory note is *data* that the
   model can read as *instructions*. Lands the carried `[UNVERIFIED]` injection pointers from
   23 (tool-result), 25 (memory), 29/30 (retrieved-passage).

2. **Indirect injection = remote exploitation without a direct interface.** "enable adversaries to
   **remotely (without a direct interface)** exploit LLM-integrated applications by strategically
   injecting prompts into data likely to be retrieved." (L35-37)

3. **Retrieved prompts act as arbitrary code.** "processing retrieved prompts can act as **arbitrary
   code execution** … control how and if other APIs are called." (L44-46; L127-128 "retrieved
   prompts themselves can act as 'arbitrary code'"). → motivates sandboxing/least-privilege (33 ↔
   18/20 over capabilities, → Appendix I cgroups/seccomp).

4. **Injection-method taxonomy** (§3.1, L310-356): **Passive** (by retrieval — poisoned
   websites/SEO, hidden text on a page, poisoned code repos / Retrieval-Plugin docs, L314-329);
   **Active** (delivered, e.g. emails processed by an assistant, L330-334); **User-Driven** (trick
   the user into pasting, L335-344); **Hidden** (multi-stage: a small injection fetches a larger
   payload; encoded/Base64; hidden in images for multi-modal models, L345-356). → 33's attack-surface
   map; "Hidden/multi-stage" = the 25-persistence + 29/30-retrieval combination.

5. **Threat taxonomy** (§3.2, adapted from a cyber-threat taxonomy [45]): Information Gathering /
   data theft (L40, L396), Fraud (L407-414), Intrusion (L420-434), Malware (L439-442), **Manipulated
   content / disinformation** (L122, L230), **Availability** (L237, L248), and **Spreading injections
   = "Prompts as worms"** (L40 "worming"; L227-228). → the agent's blast-radius catalog (33 ↔ 20).

6. **Persistence + memory carrier.** "persistence across sessions by **copying the injection into
   memory** … a memory that is shared with other applications." (L424-448; Fig column "Persistence"
   L220). → directly lands 25's carried injection-via-memory `[UNVERIFIED]`.

7. **No reliable fix today; defence is "Whack-A-Mole"; alignment alone is insufficient.** "effective
   mitigations of these emerging threats are currently **lacking**" (L50-51); "the defensive approach
   seems to follow a **'Whack-A-Mole' style**" (L1271); "recent theoretical work [80] shows the
   **impossibility of defending against all undesired behaviors by alignment or RLHF**" (L1273-1274);
   Bing Chat's input-output filtering was bypassed because it does not consider the model's external
   input (L1281-1286). → 33's thesis that safety must be **defence-in-depth + confinement +
   oversight** (18/20/27), not a single filter; "a clear-cut defense … is, at least, difficult"
   (L1138). Candidate residual defenses named (not solved): retrieved-input filtering, a less-capable
   non-instruction-tuned screener, an **LLM supervisor/moderator** (L1287-1300) → the 27/18 critic +
   human-in-the-loop gate.

## Cross-references it unlocks
- Carried `[UNVERIFIED]` injection pointers in **23** (tool-result), **25** (memory), **29**
  (server/connector), **30** (retrieved-passage) all land in 33 as the SAME root cause (claim 1).
  Annotate each as → resolved-in-33 (do NOT erase the originals; they note the *forward* pointer).
- Self-evolving loop primary is **Reflexion (2303.11366, already local+VERIFIED in 25)** — reused,
  not re-fetched.

## NOT verified here (carry-forward `[UNVERIFIED]` for 33)
- Simon Willison's prompt-injection essays / the "dual-LLM" pattern (blog, not fetched).
- Google "CaMeL" / capability-based defense papers; constitutional AI (Bai 2212.08073);
  RLHF (Ouyang 2203.02155) — named, not fetched.
- Formal ACE / sandboxing references (seccomp/gVisor/Firecracker specifics → Appendix I).
- The "impossibility" citation [80] inside Greshake — secondary, not independently fetched.
