# 02 — terminal-shell-and-dev-environment · reconciled research brief

Status: Wave 1 research complete (2 of 2 clusters). Formal `factchecker` pass DEFERRED
(blocked by spend limit — see meta/SESSION_LOG.md and ADR-002).

Per-cluster briefs (read for full depth):
- `_research_missing-semester-tlcl.md` — the shell as a programming environment: expansion order,
  quoting, fds/redirection, pipelines, job control, env vars, exit status, globbing vs regex,
  sed/awk (MIT Missing Semester + Shotts TLCL + Bash Reference Manual). 19 primary sources.
- `_research_shell-internals-build.md` — how a shell is implemented on OS primitives: fork/exec/
  wait, pipe/dup2 plumbing, process groups/job control, SIGCHLD/zombies, builtins-vs-external
  (POSIX man pages, brennan.io, GNU libc job-control manual, xv6 sh.c, CodeCrafters, Julia Evans).
  11 primary sources.

## Cross-cluster synthesis (the through-line)
The two clusters are the OUTSIDE and INSIDE of the same machine and they meet at one hinge:
**everything the user observes in the shell is the OS process model in disguise.**
- **Why `cd` must be a builtin** (both clusters independently land here): redirection/pipes/env are
  configured in the child's post-fork/pre-exec window, but `cd`/`export`/shell-var mutation change
  *the shell's own* per-process state — a child cannot propagate them back. This single fact ties
  M1/M7 (usage) to the fork/exec/wait model (internals).
- **Redirection & pipelines:** usage cluster gives the semantics (`>`/`>>`/`<`/`2>&1`, `a|b`
  concurrency, ordering of `2>&1 >file`); internals cluster gives the mechanism (open+dup2+close
  before exec; pipe()+fork-per-stage+dup2 with disciplined closing of all ends so EOF propagates).
- **`sudo echo > file` fails** (usage) ⇔ the shell, not sudo, opens the redirection as the
  unprivileged parent (internals): same lesson, two altitudes.
- **Job control:** usage gives Ctrl-C/Ctrl-Z/&/fg/bg/jobs + SIGINT/SIGTSTP/SIGTERM/SIGKILL(uncatchable);
  internals gives process groups (setpgid), terminal hand-off (tcsetpgrp), SIGCHLD reaping + zombies.
- **Env inheritance** is copy-on-exec, one-way down the tree (both clusters) — why `source` exists.

## Reconciliation notes / no conflicts
Consistent across clusters. The usage cluster is bash/POSIX-centric; flag the **zsh divergence**
(zsh does not word-split unquoted parameter expansions by default) and the bash-only extensions
(`[[ ]]`, arrays, `&>`, `<()`) when prose targets `#!/bin/sh` (dash).

## Best build-your-own target (paired lab: own-shell)
Milestone ladder synthesized from both clusters (the lab re-implements the five hinge mechanisms):
REPL/argv-tokenization+quoting → fork/exec/wait + `$?` → builtins (cd/exit/export) →
redirection (fd manipulation) → pipes (pipe+dup2) → job control (process groups + signal forwarding).
Backed by brennan.io, xv6 sh.c, CodeCrafters "Build your own shell". A data-wrangling pipeline
exercise (`grep|sed -E|awk|sort|uniq -c|sort -nr`) proves composability/streaming.

## Consolidated open questions / gaps (verify before drafting)
- Bash manual *Environment* page (export→child inheritance) confirmed by factcheck:
  GNU Bash §3.7.4 says executed commands inherit the environment.
- zsh native mode does **not** word-split unquoted parameter expansions by default; factcheck
  confirmed `SH_WORD_SPLIT` is marked for ksh/sh emulation in zsh `options.yo`.
- CodeCrafters shell stage slugs/wording confirmed against raw `course-definition.yml`: 8 core
  stages plus extension tracks.
- glibc `posix_spawn` implementation corrected: current Linux/glibc uses `clone(CLONE_VM|CLONE_VFORK)`
  / `clone3` fast paths, not literal `fork()+exec`; teach it as conceptually spawn-like with
  OS/libc-specific implementation details.
- Julia Evans "brain eaten / turns into ls" phrasing confirmed in the live 2016/10/04 post; do not
  quote unrelated phrasings without direct attribution.
- POSIX `echo` portability confirmed: POSIX Application Usage recommends `printf` to emulate
  traditional `echo` behaviors portably.
- setuid/special permission bits are out of scope of TLCL ch.9 — decide if the course wants them.
