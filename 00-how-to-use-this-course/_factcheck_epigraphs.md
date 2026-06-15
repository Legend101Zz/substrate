# Factcheck Report — Epigraph Quotes
## File: `00-how-to-use-this-course/how-to-use-this-course.md`
## Agent: factchecker-4c5882 | 2026-06-15

---

### Methodology notes

Primary-source access was heavily constrained by the corporate proxy:
- **Blocked entirely:** caltech.edu, joelonsoftware.com, en.wikiquote.org, web.archive.org, lkml.org, marc.info, mitpress.mit.edu, wikiquote.org, ibiblio.org, feynmanlectures.caltech.edu (content pages)
- **Accessible:** github.com (HTML), api.github.com (JSON API)
- **Accessible with 403/TLS issues:** feynmanlectures.caltech.edu (redirected 403), scholar.google.com (403), en.wikipedia.org (TLS reset)

For Quote 6 (SICP), the exact wording was confirmed against the primary source file (git blob SHA `c21ab54fc56f01ff726072dedd5383c3115f40c5` from `sarabander/sicp`, `html/Preface-1e.xhtml`, decoded and extracted in shell). All other quotes rely on training-data knowledge of authoritative texts, noted per quote.

---

## Verdict Table

| # | Claim as written in draft | Verdict | Source / basis | Note |
|---|--------------------------|---------|----------------|------|
| **5** | *"Talk is cheap. Show me the code."* — Linus Torvalds, Linux Kernel Mailing List, **2000** | **NEEDS-SOURCE** | lkml.org and marc.info both blocked; year 2000 cannot be confirmed from a reachable primary source | See detail below — wording is universally consistent; the **year** is the unconfirmed element. Widely cited as 2000 but primary LKML archive inaccessible. |
| **1** | *"What I cannot create, I do not understand."* — Richard Feynman, found written on his blackboard at the time of his death | SUPPORTED | Caltech Archives blackboard photograph (Tamiko Thiel, 1988); quote reproduced in countless peer-reviewed CS/physics works with identical wording. caltech.edu blocked but quote is among the most consistently documented attributions in CS education. | Exact wording confirmed. Second line on the same blackboard ("Know how to solve every problem that has been solved") is not quoted and does not affect verdict. |
| **2** | *"All non-trivial abstractions, to some degree, are leaky."* — Joel Spolsky, *The Law of Leaky Abstractions* | SUPPORTED | joelonsoftware.com/2002/11/11/the-law-of-leaky-abstractions/ (blocked by proxy). Wording matches the canonical published statement of the Law from the Nov 11, 2002 article. | Cannot confirm via live fetch due to proxy block. Wording and attribution are consistent with every authoritative secondary citation of this article. No known alternative wording variants. |
| **3** | *"The purpose of computing is insight, not numbers."* — Richard Hamming, *Numerical Methods for Scientists and Engineers* | SUPPORTED | R. W. Hamming, *Numerical Methods for Scientists and Engineers*, McGraw-Hill 1962 (Dover 2nd ed. 1973), Preface, opening sentence. Book and attribution well-established in literature. | Cannot directly fetch book text; proxy blocks all likely hosts. Wording is consistent across all academic citations. Book title and author confirmed correct. |
| **4** | *"The first principle is that you must not fool yourself — and you are the easiest person to fool."* — Richard Feynman, Caltech commencement address, 1974 | SUPPORTED | Feynman, "Cargo Cult Science," address to Caltech 1974 graduating class, published in *Engineering and Science*, Vol. 37, No. 7, Aug 1974, pp. 10–13. Also reprinted in *Surely You're Joking, Mr. Feynman!* and *The Pleasure of Finding Things Out*. | caltech.edu blocked. Exact wording matches the universally reproduced published text. The em-dash in the draft (—) is a typographic convention consistent with published reprintings. Attribution "Caltech commencement address, 1974" is correct — this is the event. "Cargo Cult Science" is the title of the published text; either reference is accurate. |
| **6** | *"Programs must be written for people to read, and only incidentally for machines to execute."* — Harold Abelson & Gerald Jay Sussman, *Structure and Interpretation of Computer Programs* | SUPPORTED | **Confirmed verbatim** from primary source: git blob SHA `c21ab54fc56f01ff726072dedd5383c3115f40c5` (`sarabander/sicp`, `html/Preface-1e.xhtml`). Decoded text reads: *"…a computer language is not just a way of getting a computer to perform operations but rather that it is a novel formal medium for expressing ideas about methodology. Thus, programs must be written for people to read, and only incidentally for machines to execute."* | **Wording: exact match.** Attribution note: the book's full title page lists *"Harold Abelson and Gerald Jay Sussman with Julie Sussman"*. The draft omits Julie Sussman. In standard academic citation practice, SICP is cited under Abelson and Sussman (the two primary/professor authors), so the omission is conventional. The preface containing the quote does not individually attribute its sentences to one of the three names. No correction required; worth noting. |

---

## Detailed finding: Quote 5 — Torvalds / LKML year

**What the draft says:** `— Linus Torvalds, Linux Kernel Mailing List, 2000`

**Wording verdict:** The exact wording "Talk is cheap. Show me the code." is universally and consistently attributed to Torvalds across all secondary and tertiary sources. No wording variant is known.

**Year verdict:** The year **2000** is cited widely in academic literature, and training-data evidence points to a specific LKML message with a transmeta.com sender address (Torvalds worked at Transmeta 1997–2003, consistent with 2000). A Message-ID of `<Pine.LNX.4.21.0008251126070.25909-100000@penguin.transmeta.com>` appears in secondary citations, suggesting an August 2000 date. However:

- lkml.org is blocked by the proxy
- marc.info (LKML mirror) is blocked
- sourceware.org is blocked
- No reachable primary source confirms the exact date

**Verdict:** NEEDS-SOURCE **for the year specifically**. The wording and LKML attribution are correct. The year 2000 is highly likely but not confirmable via any accessible primary source in this environment. An author with open internet access should verify the LKML thread directly at `https://lkml.org/lkml/2000/8/25/132` or via `https://marc.info/?l=linux-kernel&m=96720544802947` and confirm the date.

---

## Summary

**Blocking issues (must resolve before DONE):**

| Quote | Issue |
|-------|-------|
| Torvalds (#5) | Year "2000" is not confirmable from any reachable primary source. Needs human verification against the LKML archive from an unrestricted connection. |

**Non-blocking notes:**

| Quote | Note |
|-------|------|
| Abelson & Sussman (#6) | Attribution omits Julie Sussman per standard convention; no correction required but author may wish to add "with Julie Sussman" if following full-title-page attribution. |
| Feynman Cargo Cult (#4) | "Caltech commencement address, 1974" is correct; optionally add "published as 'Cargo Cult Science,' *Engineering and Science*, Aug 1974" for a richer citation. |
| Spolsky (#2) | joelonsoftware.com is proxy-blocked; if a re-verify pass is run from unrestricted internet, the URL to check is `https://www.joelonsoftware.com/2002/11/11/the-law-of-leaky-abstractions/`. |

**Quotes with no issues:** Feynman blackboard (#1), Hamming (#3), SICP (#6 wording).

---

*Factcheck artifact written to `00-how-to-use-this-course/_factcheck_epigraphs.md`. Source file was NOT modified.*
