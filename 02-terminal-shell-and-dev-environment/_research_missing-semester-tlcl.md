# 02 — Research brief: MIT Missing Semester + Shotts TLCL

> Source cluster: MIT "The Missing Semester of Your CS Education" + William Shotts, "The Linux Command Line" (TLCL). Focus: practical command-line mastery and the shell as a programming environment. Method: primary sources first, one canonical link per claim, expansion order verified against the Bash Reference Manual (the spec-level WHY). Briefs only — no course prose.

---

## 1. Key mechanisms (deep & precise, each with a forcing constraint)

### M1. Command parsing: split → resolve → exec
The shell reads a line, **splits it by whitespace into tokens**, treats the first token as the program name and the rest as arguments, resolves the program by searching the `:`-separated directories in `$PATH`, then executes it (Missing Semester, Shell). Builtins (e.g. `cd`) are handled by the shell itself, not via `$PATH`.
- **Forcing constraint:** the shell — not the program — does the splitting and the lookup. A program never sees your spaces; it sees an already-tokenized `argv[]`. This is *why* `My Photos` becomes two arguments unless quoted, and *why* `cd` cannot be an external program (it must change the shell's own working directory).

### M2. Expansion order (the spine of the whole cluster)
Bash performs expansions in a **fixed order**, after tokenization, before exec (Bash Reference Manual, *Shell Expansions*):
1. **Brace expansion** `{a,b}` / `{1..5}`
2. **Tilde expansion** `~` → `$HOME`
3. **Parameter & variable expansion** `$foo`, `${foo}` — *(left-to-right, same pass)*
4. **Arithmetic expansion** `$(( ))`
5. **Command substitution** `$( )` / backticks — *(left-to-right, same pass)*
6. **Word splitting** (on `$IFS`: space, tab, newline by default)
7. **Filename expansion / globbing** `* ? [ ]`
8. **Quote removal** (always last)
*(Process substitution `<( )` happens in the same pass as tilde/parameter/arithmetic/command substitution.)*
- **Forcing constraint:** only **brace expansion, word splitting, and filename expansion can change the number of words**; all others map one word → one word. This single rule explains the classic `for f in $files` bug: the *value* of `$files` is split into words AFTER substitution (step 3 then step 6), so spaces in filenames fragment your loop. The order is *load-bearing* — globbing happens after variable expansion, so a `*` stored in a variable WILL glob unless quoted.

### M3. Quoting: which expansions each form suppresses
(TLCL ch.8 *Expansion*; Bash manual)
- **Single quotes `'…'`** — suppress *all* expansions; everything literal.
- **Double quotes `"…"`** — suppress word-splitting, brace, tilde, and pathname/globbing; **but still allow `$` (parameter), `` ` `` /`$()` (command substitution), and `\` (escape)**. So `"$foo"` interpolates but is NOT word-split.
- **Backslash `\`** — escapes a single following character.
- **Forcing constraint:** quoting is the *only* mechanism to defeat the word-splitting + globbing steps of M2. `"$var"` (double-quoted) is the safe default precisely because it keeps the value as ONE word. `echo "$foo"` → value; `echo '$foo'` → literal `$foo` (Missing Semester, shell-tools).

### M4. Standard streams & file descriptors
Every process starts with three open fds: **0 = stdin, 1 = stdout, 2 = stderr** (TLCL ch.7 *I/O Redirection*).
- `> file` redirect stdout (truncate); `>> file` append; `< file` redirect stdin.
- `2> file` redirect stderr; `2>&1` make fd 2 point where fd 1 currently points; `&>` redirect both (bash). `/dev/null` discards.
- **Forcing constraint:** redirection is set up **by the shell before the program runs**, by manipulating the child's fd table. This is *why* `sudo echo 3 > file` fails to write to a root-owned file — the `>` redirection is opened by your unprivileged shell, not by `sudo` (Missing Semester, Shell). Order matters: `2>&1 >file` ≠ `>file 2>&1` because `2>&1` copies fd1's *current* target.

### M5. Pipelines
`a | b` connects **a's stdout to b's stdin** via an in-kernel pipe; commands run **concurrently** in the same pipeline (TLCL ch.7; Missing Semester data-wrangling). Filters (`sort`, `uniq -c`, `grep`, `wc -l`, `head`, `tail`, `tee`, `sed`, `awk`) read stdin → transform → write stdout, which is what makes them composable.
- **Forcing constraint:** a pipe is a byte stream, not a message bus — no metadata, no return values flow through it; only bytes. Each stage is a separate process. `tee` exists *because* a pipe is otherwise single-consumer (it duplicates the stream to a file + stdout).

### M6. Job control & process groups
The shell groups the processes of a pipeline into a **process group / job** attached to the controlling terminal (Missing Semester, command-line; TLCL ch.10 *Job Control*).
- `Ctrl-C` → **SIGINT (2)** to the foreground group; `Ctrl-Z` → **SIGTSTP** ("terminal's version of SIGSTOP") suspends it.
- `&` runs in background; `jobs` lists jobs for this terminal; `fg`/`bg` resume in fore/background; `kill %n` targets a job.
- `kill [-sig] PID`: default **SIGTERM (15)** = graceful; **SIGKILL (9)** = kernel-forced, *cannot be caught*; **SIGHUP (1)** = terminal closed. `nohup` / `disown` detach a job from SIGHUP so it survives logout.
- **Forcing constraint:** signals are **software interrupts** — asynchronous. SIGKILL/SIGSTOP are *uncatchable* by design so the system always retains a way to stop a runaway process. This is *why* graceful cleanup must hook SIGTERM/SIGINT (via `trap`), not SIGKILL.

### M7. Environment vs shell variables & inheritance
A variable created with `foo=bar` (no spaces — `foo = bar` is parsed as running program `foo`) is a **shell-local variable**. **`export foo`** marks it to be placed in the *environment* that is **copied into every child process** the shell spawns (TLCL ch.4 *Variables*; Bash manual, *Environment*).
- **Forcing constraint:** inheritance is **one-way and copy-on-exec** — a child gets a *copy* of exported vars at fork/exec time; it cannot mutate the parent's environment. This is *why* a script can't change your interactive shell's `cd`/vars unless you `source` it (run in the *current* shell), and *why* unexported vars are invisible to subprocesses. `$PATH`, `$HOME`, `$PWD` work across programs precisely because they're exported.

### M8. Exit status & `$?`
Every command returns an integer exit status: **0 = success, non-zero = failure** (Missing Semester shell-tools; TLCL ch.15). Read it via `$?`.
- `&&` / `||` are **short-circuiting** on exit status; `;` sequences unconditionally.
- `exit N` sets a script's status; `trap 'cmd' SIGINT SIGTERM EXIT` runs cleanup on signal/exit.
- **Forcing constraint:** status is a *single byte channel* separate from stdout — this is what lets pipelines carry data on stdout while control flow (`if cmd; then`) keys off status. `if grep -q x f` works because `if` tests exit status, not output.

### M9. Special variables
`$0` script name; `$1..$9` positional args; `$@` all args; `$#` arg count; `$?` last status; `$$` current PID; `!!` last command; `$_` last arg of last command (Missing Semester shell-tools).

### M10. Globbing vs regex (do not conflate)
**Globbing** = shell pathname expansion against existing filenames: `*` = any run of chars, `?` = one char, `[…]`/`{…}` sets/ranges (TLCL ch.8). **Regex** = a separate matching language used *inside tools* (`grep`, `sed`, `awk`): `.` any char, `*` = zero-or-more of *preceding* atom, `+` one-or-more, `^`/`$` anchors, `[abc]` class, `(…)` capture groups `\1`, greedy by default (Missing Semester data-wrangling).
- **Forcing constraint:** the symbols collide but mean different things — glob `*` ≈ regex `.*`. Globbing is done by the *shell* on *filenames*; regex is done by the *tool* on its *input stream*. `sed` BRE needs `\` before `+`/`(` (or use `-E`) — a different dialect again.

### M11. sed / awk stream model
`sed` is a **stream editor** applying `s/REGEX/REPL/` line by line (Missing Semester data-wrangling). `awk` is field-oriented: per line, `$0`=whole line, `$1..$n`=fields; supports `BEGIN`/`END` and pattern-action blocks.
- **Forcing constraint:** both are *streaming* — they process one record at a time without loading the whole file, which is what makes them scale to large inputs in a pipe.

### M12. Shebang & exec
`#!/usr/bin/env python` on line 1 tells the **kernel** which interpreter to exec the file with (Missing Semester shell-tools). `env` resolves the interpreter via `$PATH` for portability.
- **Forcing constraint:** the shebang is read by the *kernel's exec path*, not the shell — so it works for any executable script regardless of which shell launched it.

---

## 2. Foundational sources (one canonical link per claim)

**MIT Missing Semester (missing.csail.mit.edu, 2020):**
- Shell basics, parsing, `$PATH`, redirection, pipes, root/sudo+redirection: https://missing.csail.mit.edu/2020/course-shell/
- Variables, quoting, special vars, exit codes, `&&`/`||`, `$()`, `<()`, globbing, brace, shebang, shellcheck, find/fd/grep/rg: https://missing.csail.mit.edu/2020/shell-tools/
- Job control, signals, tmux, aliases, dotfiles, SSH: https://missing.csail.mit.edu/2020/command-line/
- Pipes, sed, regex, awk, sort/uniq/wc/paste/bc: https://missing.csail.mit.edu/2020/data-wrangling/
- Git data model (content-addressed DAG — note only; git internals belong elsewhere): https://missing.csail.mit.edu/2020/version-control/

**Shotts, The Linux Command Line (linuxcommand.org, free):**
- Learning the Shell index: https://linuxcommand.org/lc3_learning_the_shell.php
- Working with Commands (type/which/builtins): https://linuxcommand.org/lc3_lts0060.php
- I/O Redirection (fds, `>`/`>>`/`<`, pipelines, filters): https://linuxcommand.org/lc3_lts0070.php
- Expansion (globbing, tilde, arithmetic, brace, parameter, command subst, word-splitting, quoting): https://linuxcommand.org/lc3_lts0080.php
- Permissions (rwx triads, octal 755/644/600, chmod/chown/su/sudo): https://linuxcommand.org/lc3_lts0090.php
- Job Control (`&`, jobs, fg/bg, Ctrl-Z, signals, kill, SIGTERM/KILL/HUP): https://linuxcommand.org/lc3_lts0100.php
- Writing Shell Scripts index: https://linuxcommand.org/lc3_writing_shell_scripts.php
- Variables (shell vars, env vars, naming convention): https://linuxcommand.org/lc3_wss0040.php
- Command Substitution and Constants: https://linuxcommand.org/lc3_wss0050.php
- Positional Parameters: https://linuxcommand.org/lc3_wss0120.php
- Errors, Signals and Traps Pt2 (exit, `$?`, `trap`, SIGKILL uncatchable): https://linuxcommand.org/lc3_wss0150.php

**Spec-level WHY (one citation hop — the canonical definition of expansion order/word-splitting/environment):**
- Bash Reference Manual, *Shell Expansions* (authoritative expansion ORDER): https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html
- Bash Reference Manual, *Word Splitting* (`$IFS` rules): https://www.gnu.org/software/bash/manual/html_node/Word-Splitting.html
- Bash Reference Manual, *Environment* (export → child inheritance): https://www.gnu.org/software/bash/manual/html_node/Environment.html

---

## 3. "Why it's this way" (constraints / design choices)

- **Word-splitting exists** because the shell's job is to build an `argv[]` array for `exec`, and the natural delimiter on a typed line is whitespace. The default `$IFS` (space/tab/newline) is the line→words contract. Downside: filenames with spaces fragment — hence quoting. (Bash *Word Splitting*.)
- **Quoting exists** to give the user explicit control over *which* expansion steps apply, since the same characters (`$ * ~ {}`) are both literal text and metacharacters. Single vs double quotes is a deliberate two-level dial: literal-everything vs interpolate-but-don't-split. (TLCL ch.8.)
- **Fixed expansion order** exists so behavior is deterministic and tools compose predictably; "only brace/word-split/glob add words" keeps reasoning tractable. (Bash manual.)
- **Three fds + redirection in the shell** embody the Unix **"everything is a file"** + **composability** philosophy: programs read fd0, write fd1, error on fd2, and the shell rewires those fds to files/pipes *without the program's cooperation*. That decoupling is exactly what makes arbitrary `prog | prog | prog` chains work and is why redirection is the shell's job, not the program's. (Missing Semester Shell; TLCL ch.7.)
- **Pipes carry bytes only** — minimal interface, maximal composability. Small single-purpose filters + a universal text stream beat monolithic programs ("do one thing well"). (Missing Semester data-wrangling.)
- **Process groups + uncatchable SIGKILL/SIGSTOP** exist so the OS/terminal always retains ultimate control over jobs; catchable signals (SIGINT/SIGTERM/SIGHUP) let programs clean up, the uncatchable pair guarantees the system can't be held hostage. (Missing Semester command-line; TLCL ch.15.)
- **Exported env vars are copied to children** because process isolation forbids shared mutable memory across `fork`/`exec`; copy-on-exec is the cheapest way to propagate config (`$PATH`, `$HOME`) one-way down the tree. (Bash *Environment*.)

---

## 4. Common misconceptions to preempt

1. **"Quotes are decorative / interchangeable."** No — `'…'` kills all expansion; `"…"` still does `$`, `$()`, `\`. `"$x"` is one word; `$x` (unquoted) is split + globbed. (M3.)
2. **"Expansion happens when I type / left-to-right as written."** No — it happens in the **fixed order of M2**, after tokenizing. A `*` or space *inside a variable's value* is acted on AFTER substitution, not when you wrote the assignment.
3. **"`sudo cmd > file` writes the file as root."** No — the shell opens `>` as *you* before `sudo` runs. Use `sudo tee` or `sudo sh -c '… > file'`. (M4.)
4. **"A script can change my shell's directory / variables."** No — it runs in a child shell with a *copy* of the environment. Use `source`/`.` to run in the current shell. (M7.)
5. **"Subshell == current shell."** `(...)`, pipelines stages, and `$()` run in subshells; variable changes there don't persist to the parent.
6. **"Glob `*` and regex `*` are the same."** No — glob `*` ≈ regex `.*`; regex `*` means "zero+ of the previous atom." Globbing is filename matching by the shell; regex is content matching inside tools. (M10.)
7. **"`foo = bar` sets a variable."** No — spaces break it; it tries to run program `foo` with args `=` and `bar`. (M7.)
8. **"`kill` kills; `kill -9` is just a stronger kill."** `kill` sends *SIGTERM* (catchable, lets the program clean up); `-9` is SIGKILL (uncatchable, no cleanup, can leak temp files/locks). Prefer SIGTERM first. (M6/M8.)
9. **"Exit status is the program's output."** No — status is a separate 0–255 byte channel; stdout is the data. `if`/`&&`/`||` test status, not text.
10. **"Pipes return data both ways / preserve types."** No — one-directional byte stream only.

---

## 5. Best build-your-own target(s) (sets up the own-shell lab in cluster 2)

Scripting/tooling exercises that build the exact intuitions a from-scratch shell must implement:
- **A `mini-shell` warm-up script**: parse a line into argv (handle quoting + escapes), resolve via `$PATH`, fork/exec, wait, report `$?`. Directly rehearses M1/M2/M8 before the real own-shell lab.
- **Implement redirection & pipes**: extend the warm-up to honor `<`, `>`, `>>`, `2>`, and one `|` by manipulating fds before exec — the core systems lesson of M4/M5 (this is the spine of the paired "build your own shell" lab).
- **A robust cleanup-on-signal script**: temp-file pattern with `trap 'clean_up' SIGINT SIGTERM EXIT` (TLCL ch.15) — teaches signal handling + why SIGKILL can't be trapped (M6).
- **A data-wrangling pipeline** (Missing Semester data-wrangling): take a log, build `grep | sed -E | awk | sort | uniq -c | sort -nr` to produce a frequency table — proves composability/streaming (M5/M10/M11).
- **A `for`-loop that survives spaces in filenames**: contrast `for f in $x` vs `for f in "$x"`/glob iteration — makes M2/M3 failure modes visceral.
- **Dotfiles + alias bootstrap**: versioned dotfiles symlinked into place (Missing Semester command-line) — environment/inheritance (M7) made concrete.

Hooks for cluster 2's own-shell lab: argv tokenization (M1), fork/exec/wait + `$?` (M8), fd plumbing for redirection/pipes (M4/M5), process groups + signal forwarding for job control (M6), and env inheritance to children (M7) are the five mechanisms the lab will re-implement in C/Rust/etc.

---

## 6. Open questions / where sources disagree (bash vs POSIX sh vs zsh)

- **Word splitting on unquoted expansion — bash vs zsh.** Bash (and POSIX sh) word-split *and* glob the result of an unquoted `$var` (M2). **Zsh does NOT word-split unquoted parameter expansions by default** — a major behavioral divergence that breaks/“fixes” scripts moving between shells. Factcheck confirmed `SH_WORD_SPLIT` is a ksh/sh-emulation option in zsh `Doc/Zsh/options.yo`, so native zsh differs from the bash/POSIX-sh model.
- **`&>` and `2>&1` ordering, `[[ ]]`, arrays, `$(< file)`, brace expansion, process substitution `<()`** are **bash/zsh extensions, NOT POSIX `sh`**. Scripts with `#!/bin/sh` (often dash on Debian/Ubuntu) will fail on these. Course should be explicit about which dialect a given example targets.
- **`echo` portability**: flag/escape handling differs across shells/implementations; POSIX `echo` Application Usage says `printf` can portably emulate any traditional `echo` behavior. Prefer `printf` in portable scripts.
- **Default `$IFS`**: space/tab/newline by both bash manual and POSIX — sources agree.
- **Expansion order**: bash manual is canonical and POSIX matches it closely; treat the Bash Reference Manual order (M2) as the spec.
- **Signal numbers** (2/9/15/1) are conventional and consistent across Linux in both sources, but are *not* guaranteed identical on all Unixes — use names (SIGINT/SIGKILL/SIGTERM/SIGHUP), not numbers, in portable text. Sources here agree on names.

---

### Coverage / gaps
- **Distinct primary sources cited: 19** — 5 Missing Semester lecture URLs + 11 TLCL chapter/index URLs + 3 Bash Reference Manual pages (the one-hop spec for expansion order, word splitting, environment).
- **Verified at spec level:** expansion ORDER and word-splitting (Bash manual, *Shell Expansions* / *Word Splitting*); quoting suppression rules (TLCL ch.8 + Bash manual); fds 0/1/2 and redirection (TLCL ch.7); signals incl. uncatchable SIGKILL (TLCL ch.15 + Missing Semester).
- **Gaps / checked notes:**
  1. TLCL ch.4 *Variables* page did **not** itself spell out `export`/child-inheritance; that claim
     is sourced to the Bash manual *Environment* page, factchecked live at GNU Bash §3.7.4.
  2. zsh no-word-split-by-default is factchecked against `zsh-users/zsh` `Doc/Zsh/options.yo`
     (`SH_WORD_SPLIT` marked for ksh/sh emulation).
  3. `echo` vs `printf` portability is factchecked against POSIX `echo` Application Usage.
  4. TLCL has no dedicated standalone "Environment" chapter in the Learning-the-Shell index pulled;
     env material is split between ch.4 (Variables) and the Bash manual hop. Note for structure cluster.
  5. setuid/special permission bits are **out of scope** of TLCL ch.9 (confirmed absent) — flag if the course wants them.
