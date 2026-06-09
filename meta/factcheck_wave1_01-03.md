# Factcheck Report — Wave 1 Research Briefs (Sub-courses 01, 02, 03)

**Agent:** factchecker-835fee  
**Date:** 2026-06-09  
**Scope:** Load-bearing and [UNVERIFIED]-flagged claims in research briefs for sub-courses 01, 02, 03.  
**Method:** Primary-source verification via curl/shell (GNU Bash manual, glibc GitHub mirror, CodeCrafters raw YAML, POSIX spec, MIT E2E paper text, HPBN, Beej live pages, Julia Evans blog, zsh source). eater.net pages confirmed accessible (HTTP 200) but are Next.js/React SSR — body text not curl-extractable. Secondary notes where JS renders content.

---

## Summary Table (blockers first)

| # | file | claim | verdict | source link | note |
|---|------|-------|---------|-------------|------|
| 1 | `01/_research_eater-csapp.md` | SAP-1 16-signal control-word bit ordering and EEPROM bit map (exact bit positions per row) | **NEEDS-SOURCE** | https://eater.net/8bit/control (accessible, HTTP 200, but Next.js/React-rendered — content not curl-extractable) | The signal *names* (HLT, MI, RI, RO, IO, II, AI, AO, EO, SU, BI, OI, CE, CO, J, FI) are widely attested, but the exact **bit order / EEPROM address layout** was sourced from the community mirror at `ullright.org`, NOT from the primary eater.net page text. Until verified against the eater.net video transcripts or a JS-capable browser crawl, treat the bit-level ordering as community-sourced, not primary. |
| 2 | `01/_research_eater-csapp.md` | Eater 6502 memory map: RAM $0000–$3FFF, I/O $4000–$7FFF, ROM $8000–$FFFF | **NEEDS-SOURCE** | https://eater.net/6502 (same JS-render issue) | Numbers echo community write-ups. eater.net/6502 accessible but React-rendered; schematic/circuit detail not retrievable via curl. Some builders alter decoding. Do not cite specific hex ranges as canonical until confirmed against official schematic PDF or eater.net page. |
| 3 | `01/_research_eater-csapp.md` | T-state count: "fetch = 2, execute up to ~5–6 microsteps" | **NEEDS-SOURCE** | https://eater.net/8bit/control (JS-rendered) | Consistent with community SAP-1 builds, but specific per-instruction microstep counts not sourced to primary eater.net or the Malvino text. Safe to teach directionally but block verbatim table citation. |
| 4 | `01/_research_nand2tetris-petzold.md` | Scott *But How Do It Know?* exact per-step control micro-wiring and Petzold *Code* specific chapter/figure attributions | **NEEDS-SOURCE** | Book-only; neither text publicly available via curl | Research brief correctly flagged these as [PARTIAL]. Do not cite specific chapter numbers or figures without direct book access. |
| 5 | `02/_research_shell-internals-build.md` | `posix_spawn()` is "behind the scenes implemented in terms of … fork and exec" (attributed to Julia Evans) | **UNSUPPORTED** for current Linux/glibc | https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/unix/sysv/linux/spawni.c | The current Linux glibc implementation uses `clone(CLONE_VM | CLONE_VFORK)` (and `clone3` on ≥5.5 kernels), NOT fork+exec. The glibc source comment explicitly states: *"The Linux implementation of posix_spawn{p} uses the clone syscall directly with CLONE_VM and CLONE_VFORK flags and an allocated stack."* Evans' description may match older or non-Linux libcs. Do NOT propagate this claim to course prose; use safe phrasing like "conceptually equivalent to fork+exec but with OS-specific fast paths." |
| 6 | `03/_research_kurose-beej.md` | Beej covers `epoll`/`kqueue` — research brief says "platform-specific and lightly covered" | **UNSUPPORTED** — they are NOT covered at all | https://beej.us/guide/bgnet/html/split/slightly-advanced-techniques.html | Search of Beej §7 (the advanced-techniques chapter, 83,566 chars) returned: `epoll` → NOT FOUND; `kqueue` → NOT FOUND; `IOCP` → NOT FOUND. Beej covers `poll()` (§7.2, full code) and `select()` (§7.3, full code) and mentions `libevent` as a production alternative. Revise any text implying Beej teaches epoll/kqueue to: "Beej covers `poll()` and `select()`; epoll/kqueue are not covered — use the Linux man page (epoll(7)) or the kqueue(2) BSD man page." |
| 7 | `03/_research_stevens-hpbn.md` | QUIC CPU cost: "~2×–4× the CPU of TLS/TCP for large transfers, ~70–80% of cost in per-packet sendmsg/recvmsg syscalls" | **NEEDS-SOURCE** | No single canonical peer-reviewed paper cited | Research brief itself flags this: "from vendor/arXiv not single-source-canonical." The figure is plausible but not yet pinned to a primary measurement paper. Block from course prose until a paper (e.g., Rüth et al. IMC 2018 or equivalent arXiv) is cited inline. |
| 8 | `03/_research_stevens-hpbn.md` | HTTP/3 / QUIC adoption: "~9% of websites used QUIC as of early 2023" | **NEEDS-SOURCE** | Wikipedia cited (secondary, dated) | Time-sensitive adoption stat sourced only to Wikipedia's QUIC article. Use W3Techs or HTTP Archive for authoritative adoption tracking. Do not embed a specific percentage without a primary data source and a retrieval date. |
| 9 | `03/_research_cs144-sponge.md` | Sponge Lab 4 / TCPConnection handout: full state-machine detail and that Minnow *no longer* requires hand-writing it | **NEEDS-SOURCE** (partially) | CS144/minnow GitHub returns 404 (private repo); cs144.github.io timed out | Claim that Minnow's check4 is "Measuring the real world" (not TCPConnection) is corroborated indirectly by the lab PDF language ("the same Minnow library") and community sources, but the original Sponge Lab 4 handout PDF was not re-fetched directly. The [UNVERIFIED] flag in the brief is correct. Safe to say "Minnow provides TCPPeer; the hand-written TCPConnection lab is Sponge-era." |

---

## SUPPORTED claims (no action needed except removing [UNVERIFIED] tags)

| # | file | claim | verdict | source link | note |
|---|------|-------|---------|-------------|------|
| 10 | `02/_research_missing-semester-tlcl.md` | Bash manual Environment page (§3.7.4): export marks variables for child-process inheritance; executed commands inherit the environment | **SUPPORTED** | https://www.gnu.org/software/bash/manual/html_node/Environment.html | Verbatim: *"On invocation, the shell scans its own environment and creates a parameter for each name found, automatically marking it for export to child processes. Executed commands inherit the environment."* Remove the [UNVERIFIED] tag. |
| 11 | `02/_research_missing-semester-tlcl.md` | zsh does NOT perform word-splitting on unquoted parameter expansions by default (unlike bash/sh) | **SUPPORTED** | https://raw.githubusercontent.com/zsh-users/zsh/master/Doc/Zsh/options.yo | zsh source options file marks `SH_WORD_SPLIT` with `<K> <S>` tags — active only in ksh/sh emulation. In native zsh, field splitting on unquoted expansions is off by default. Remove the [UNVERIFIED] tag. |
| 12 | `02/_research_shell-internals-build.md` | CodeCrafters shell course has exactly 8 core stages (base track) with these names | **SUPPORTED** | https://raw.githubusercontent.com/codecrafters-io/build-your-own-shell/main/course-definition.yml | Verified against primary YAML. Core 8 stages: `oo8`="Print a prompt", `cz2`="Handle invalid commands", `ff0`="Implement a REPL", `pn5`="Implement exit", `iz3`="Implement echo", `ez5`="Implement type", `mg5`="Locate executable files", `ip1`="Run a program". Extensions include Navigation (cd/pwd), Quoting, Redirection, Pipelines, History, Parameter Expansion, Completions. Remove the [UNVERIFIED] slug tag. |
| 13 | `02/_research_shell-internals-build.md` | Julia Evans "brain eaten and turns into ls" / "exec will eat your brain" phrasing is verbatim from the Evans blog | **SUPPORTED** | https://jvns.ca/blog/2016/10/04/exec-will-eat-your-brain/ | Confirmed live: the "child that is a clone of myself… gets its brain eaten and turns into ls" metaphor is the blog's own wording. Safe to paraphrase (not quote verbatim without `>`-style attribution). |
| 14 | `02/_research_missing-semester-tlcl.md` | POSIX recommends `printf` over `echo` for portable scripts | **SUPPORTED** | https://pubs.opengroup.org/onlinepubs/9699919799/utilities/echo.html | POSIX spec Application Usage section: *"The printf utility can be used portably to emulate any of the traditional behaviors of the echo utility."* Remove the [UNVERIFIED] tag. |
| 15 | `03/_research_kurose-beej.md` | End-to-End Arguments paper: Saltzer, Reed, Clark; ACM TOCS 2(4), Nov 1984, pp.277–288; core thesis that functions can only be completely/correctly implemented at the endpoints | **SUPPORTED** | https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.txt | Primary plain-text version confirmed: title, authors, publication metadata, and core thesis paragraph all verified. Verbatim thesis: *"The function in question can completely and correctly be implemented only with the knowledge and help of the application standing at the end points of the communication system. Therefore, providing that questioned function as a feature of the communication system itself is not possible."* |
| 16 | `01/_research_eater-csapp.md` | EEPROM part: 28C16 (not 28C256; the 6502 project uses 28C256) | **SUPPORTED** (partially) | https://eater.net/8bit/control (HTML source links directly to `/datasheets/28c16.pdf`) | The 8-bit CPU project uses the 28C16; the 6502 project uses 28C256. The research brief correctly distinguishes these. eater.net/8bit/control HTML source (even before JS renders) contains `<a href="/datasheets/28c16.pdf">28C16 16K EEPROM</a>`.  |
| 17 | `03/_research_stevens-hpbn.md` | TLS ≈ <1% CPU load, <10 KB memory/conn, <2% network overhead (Google, Adam Langley) | **SUPPORTED** | https://hpbn.co/transport-layer-security-tls/ | HPBN verbatim: *"On our production frontend machines, SSL/TLS accounts for less than 1% of the CPU load, less than 10 KB of memory per connection and less than 2% of network overhead."* Adam Langley (Google) attribution confirmed. |

---

## Specific Edit Recommendations

### Sub-course 01 (`_research_eater-csapp.md`)
- **Remove** the specific hex ranges ($0000–$3FFF etc.) from any course prose until confirmed against the eater.net schematics via a JS-capable browser.  
- **Tag** the 16-signal control-word list in prose as "community-documented, consistent with eater.net videos" rather than citing eater.net as a text source.  
- **Keep** the 28C16 EEPROM part number — confirmed via eater.net HTML source.  
- **Keep** the SAP-1 / Malvino attribution as widely accepted context; just do not cite a specific page/chapter without the book.

### Sub-course 02 (`_research_shell-internals-build.md`)
- **Line 42:** Replace `"posix_spawn()` is behind the scenes implemented in terms of… fork and exec." (Evans)` with: *"On Linux/glibc, `posix_spawn` uses `clone(CLONE_VM|CLONE_VFORK)` rather than fork+exec, giving a true vfork-like fast path. On other platforms (older glibc, macOS, WASM), behavior varies. Conceptually it's a fork+exec abstraction, but do not teach it as fork+exec at the implementation level."* Remove the Evans attribution for the internals claim.  
- **Remove** `[UNVERIFIED]` from lines about Bash Environment page inheritance (§3.7.4 confirmed ).  
- **Remove** `[UNVERIFIED]` from CodeCrafters stage names (confirmed against raw YAML ).  
- **Remove** `[UNVERIFIED]` from zsh no-word-split default (confirmed from zsh options.yo `<K><S>` tags ).  
- **Remove** `[UNVERIFIED]` from echo/printf portability — POSIX spec confirmed .

### Sub-course 03 (`_research_kurose-beej.md`, `_research_cs144-sponge.md`, `_research_stevens-hpbn.md`)
- **Beej epoll/kqueue:** Replace "lightly covered" with "not covered in Beej; direct students to `epoll(7)` (Linux) and `kqueue(2)` (BSD/macOS) man pages." This is a correction, not just a note.  
- **QUIC CPU cost (2×–4×):** Keep the claim but mark it as `[CITE-NEEDED: specific arXiv/IMC paper]` and do not let it appear uncited in course prose.  
- **HTTP/3 adoption %:** Remove the 9%/2023 figure or replace with: "HTTP/3 is supported by all major browsers and CDNs; for current adoption see HTTP Archive (httparchive.org) with retrieval date."  
- **E2E paper:** Remove [UNVERIFIED] — fully confirmed. Cite as `https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.txt` (plain text) or the PDF at the same path.  
- **Sponge Lab 4:** Keep the [UNVERIFIED] flag; phrasing is accurate but the primary handout PDF was not retrieved. Safe to teach the TCPConnection state machine from RFC 9293.

---

## Source Archive (primary URLs confirmed live as of 2026-06-09)

| URL | status |
|-----|--------|
| https://www.gnu.org/software/bash/manual/html_node/Environment.html | 200 OK  |
| https://raw.githubusercontent.com/zsh-users/zsh/master/Doc/Zsh/options.yo | 200 OK  |
| https://raw.githubusercontent.com/codecrafters-io/build-your-own-shell/main/course-definition.yml | 200 OK  |
| https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/unix/sysv/linux/spawni.c | 200 OK  |
| https://jvns.ca/blog/2016/10/04/exec-will-eat-your-brain/ | 200 OK  |
| https://pubs.opengroup.org/onlinepubs/9699919799/utilities/echo.html | 200 OK  |
| https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.txt | 200 OK  |
| https://hpbn.co/transport-layer-security-tls/ | 200 OK  |
| https://beej.us/guide/bgnet/html/split/slightly-advanced-techniques.html | 200 OK  |
| https://eater.net/8bit/control | 200 OK (JS-rendered — content not curl-extractable) |
| https://eater.net/6502 | 200 OK (JS-rendered — content not curl-extractable) |
| https://api.github.com/repos/CS144/minnow | 404 (private repo) |
