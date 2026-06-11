# 02 — Terminal, Shell, and Dev Environment · _structure.md

**Identity:** the reader's daily cockpit AND their first real encounter with the OS process
model — taught as one thing, because everything you see in the shell IS the process model
in disguise.

**Bespoke shape — "outside-in then inside-out, meeting at one hinge."** Two movements:
**Part A (Outside)** the shell as a programming environment you USE; **Part B (Inside)** the
shell as a program built on OS primitives you IMPLEMENT. They meet at the hinge insight that
recurs in both clusters: *why `cd` must be a builtin* — child processes cannot mutate the
parent's state. The arc is deliberately reflective: each USE behavior in Part A gets its
MECHANISM revealed in Part B at the same altitude. (Grounded in the two reconciled
clusters: Missing-Semester/TLCL usage + shell-internals/xv6-sh build.)

## Dependency position
- **Depends on:** 01 (program/CPU mental model — light). Best read before 04 because it
  motivates fork/exec/wait experientially before 04 formalizes them.
- **Feeds into:** 04 (process model — 02 is the gentle on-ramp), 03 (sockets are fds, like
  pipes), 05 (REPL/eval loop echoes a shell loop), and every later lab (you live here).
- **Appendix link DOWN:** B-linux-internals (signals, process groups, the kernel side of
  fork/clone/COW that 02 only touches).

## Chapter specs (3–5 lines each)
### Part A — the shell you use
1. **The REPL and expansion order** — what the shell does to a line before running it:
   tokenize → expansions (brace/tilde/param/command/arith) → word-splitting → globbing →
   quoting. Why order matters; the zsh divergence (no default word-split of unquoted
   `$var`). The mental model: the shell is a tiny language interpreter.
2. **Streams, redirection, and pipelines** — stdin/stdout/stderr as fds 0/1/2; `>`/`>>`/
   `<`/`2>&1` and why `2>&1 >file` ≠ `>file 2>&1`; pipelines as concurrent processes
   streaming bytes. `sudo echo > file` fails because the SHELL opens the file, not sudo.
3. **Exit status, conditionals, and text tools** — `$?`, `&&`/`||`, test/`[[ ]]`, then
   the streaming toolkit: `grep`/`sed -E`/`awk`/`sort`/`uniq -c` as composable filters.
   Globbing vs regex (different languages). Bash-only vs `#!/bin/sh` (dash) portability.
4. **Job control & environment** — foreground/background, Ctrl-C/Ctrl-Z, `&`/`fg`/`bg`/
   `jobs`; SIGINT/SIGTSTP/SIGTERM/SIGKILL (uncatchable). Env vars inherit copy-on-exec,
   one-way down the tree — which is WHY `source`/`export` behave as they do.

### Part B — the shell you build (each maps to a Part-A behavior)
5. **fork / exec / wait — the engine** — the core loop: `fork()` a child, `exec()` the
   program, parent `wait()`s and reads status into `$?`. xv6 `sh.c` as the clean reference.
   Why a process replaces (exec) vs creates. THE hinge: builtins like `cd`/`export` must
   run in the parent because a child can't propagate state back.
6. **Plumbing: redirection & pipes by hand** — the post-fork/pre-exec window: `open`+`dup2`
   +`close` for redirection; `pipe()`+fork-per-stage+`dup2` with disciplined closing of all
   ends so EOF propagates. Re-derives ch.2's semantics from mechanism.
7. **Job control internals** — process groups (`setpgid`), terminal hand-off (`tcsetpgrp`),
   `SIGCHLD` reaping + zombies. Re-derives ch.4 from mechanism. Note glibc `posix_spawn`
   uses `clone(CLONE_VM|CLONE_VFORK)`/`clone3` fast paths, not literal fork+exec.

## Paired build lab (/build → own-shell)
Milestone ladder = the five hinge mechanisms, mirroring Part B:
REPL + argv tokenization/quoting → fork/exec/wait + `$?` → builtins (cd/exit/export) →
redirection (fd manipulation) → pipes (pipe+dup2) → job control (process groups + signal
forwarding). Capstone exercise: a data-wrangling pipeline
(`grep | sed -E | awk | sort | uniq -c | sort -nr`) proving composability/streaming.
Backed by brennan.io, xv6 `sh.c`, CodeCrafters "Build your own shell" (8 core stages).

## Diagrams needed
- Expansion pipeline (line → tokens → expansions → words → glob → exec) as an ordered flow.
- fd table before/after `dup2` redirection (the picture that makes redirection click).
- Two-stage pipeline: two processes + pipe + which fds each closes (EOF propagation).
- fork/exec/wait sequence diagram (parent/child timelines + SIGCHLD).
- Process-group / terminal foreground hand-off diagram.

## Sources / gaps to honor (from _research.md)
- Confirmed by factcheck: Bash §3.7.4 env inheritance; zsh `SH_WORD_SPLIT` is ksh/sh-emul
  only; CodeCrafters 8 core stages; POSIX recommends `printf` over `echo` for portability;
  Julia Evans "turns into ls" phrasing live in the 2016/10/04 post.
- Teach `posix_spawn` as conceptually spawn-like with OS/libc-specific implementation.
- DECISION for drafting: setuid/special permission bits are out of TLCL ch.9 scope — keep
  OUT of 02 (belongs in B) unless an ADR adds them.
