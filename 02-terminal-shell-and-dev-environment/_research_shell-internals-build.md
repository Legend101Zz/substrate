# 02 — Research brief: shell internals + build-your-own-shell

Source cluster: how a shell is actually implemented on top of OS primitives (fork/exec/wait, pipes, redirection, job control). Primary sources: POSIX/Linux man pages, Stephen Brennan "Write a Shell in C", GNU libc "Implementing a Shell" job-control sample, xv6 `sh.c`, Julia Evans, CodeCrafters track. Every load-bearing syscall claim below is tied to a man page or canonical source. The brief is structured for the paired "build your own shell" lab: it gives the exact syscall sequence for the four core operations (run a command, pipeline, redirection, backgrounded job) so the lab can be built as a milestone ladder.

---

## 1. Key mechanisms (deep + precise, each with its forcing constraint)

### 1.1 The REPL: read → parse → execute loop
A shell is a read-eval-print loop. Brennan's `lsh_loop()` is the canonical minimal form:
```c
do {
  printf("> ");
  line   = lsh_read_line();      // read a line from stdin
  args   = lsh_split_line(line); // tokenize into argv[]
  status = lsh_execute(args);    // builtin dispatch OR fork+exec
  free(line); free(args);
} while (status);
```
**Forcing constraint:** the prompt is printed by the shell process itself, and the shell must read from its *own* stdin (fd 0). After running a foreground child it must regain the terminal before printing the next prompt — otherwise prompt and child output interleave. (Brennan, brennan.io)

### 1.2 fork() + execve() + waitpid() — running ONE external command
Exact sequence (Brennan `lsh_launch()`):
```c
pid = fork();                       // 1. duplicate the shell process
if (pid == 0) {                     //    --- child ---
    execvp(args[0], args);          // 2. replace memory image with the program
    perror("lsh"); exit(EXIT_FAILURE); // only reached if execvp fails
} else {                            //    --- parent (shell) ---
    do {
      waitpid(pid, &status, WUNTRACED);   // 3. block until child exits/stops
    } while (!WIFEXITED(status) && !WIFSIGNALED(status));
}
```
- `fork()` returns twice: 0 in the child, child PID in the parent. The child is a near-exact clone (memory, open fds, signal dispositions inherited). (fork(2))
- `execve()`/`execvp()` does NOT create a process — it *replaces* the calling process's program image in place. "all of your memory and registers and the program... change, but almost everything stays the same" re: env vars, signal handlers, open files. exec only returns on failure. (Evans, jvns.ca/blog/2016/10/04; execve(2))
- `waitpid()` collects the child's termination status; `WIFEXITED(status)` → normal exit, `WIFSIGNALED(status)` → killed by signal, `WIFSTOPPED(status)` → stopped (needs `WUNTRACED`). (wait(2))

**Forcing constraint:** the gap *between* fork and exec is the only place where the child is "yourself but not yet the new program" — this is where the shell rewires fds (redirection/pipes) and process groups before the new program ever runs. Without the fork/exec *separation*, there is no such window.

### 1.3 Why fork-then-exec rather than one spawn call
`posix_spawn()` exists, but current Linux/glibc does **not** literally implement it as `fork()+exec`: factcheck confirmed `spawni.c` uses `clone(CLONE_VM|CLONE_VFORK)` / `clone3` fast paths. Treat `posix_spawn` as a higher-level spawn abstraction whose implementation varies by OS/libc. The fork/exec teaching model remains useful because the gap *between* fork and exec is where the shell can run setup code (dup2, close, setpgid, signal reset, chdir) in the child's context before handing it to the new program. **Forcing constraint:** redirection, pipe plumbing, and job-control group placement are all naturally expressed as "things done by the child to itself before exec"; spawn APIs must encode those setup operations up front as file actions/attributes.

### 1.4 Pipelines `a | b` — pipe() + fork() ×2 + dup2()
`pipe(pipefd)` returns two fds: `pipefd[0]` = read end, `pipefd[1]` = write end; "Data written to the write end... is buffered by the kernel until it is read from the read end." (pipe(2)) Both ends are inherited across fork. xv6 `sh.c` PIPE case is the canonical pattern:
```c
pipe(p);
if (fork1() == 0) {            // left process: writes
    close(1); dup(p[1]);       // make fd 1 (stdout) = pipe write end
    close(p[0]); close(p[1]);  // close BOTH original pipe fds
    runcmd(left);              // exec
}
if (fork1() == 0) {            // right process: reads
    close(0); dup(p[0]);       // make fd 0 (stdin) = pipe read end
    close(p[0]); close(p[1]);
    runcmd(right);
}
close(p[0]); close(p[1]);      // PARENT must close both ends too
wait(0); wait(0);              // reap both children
```
Modern code uses `dup2(p[1], 1)` instead of the `close(1); dup(p[1])` idiom; `dup2(oldfd, newfd)` atomically makes `newfd` refer to the same file as `oldfd`. (dup2(2))
**Forcing constraint:** *every* process holding a write-end open prevents the reader from seeing EOF. The shell/parent and the non-writing child MUST close unused ends, or `b` hangs forever waiting for input. This is the single most common pipeline bug.

### 1.5 Redirection `cmd > f`, `cmd < f`, `cmd 2> f` — fd manipulation before exec
xv6 REDIR case:
```c
close(rcmd->fd);                       // close target fd (1 for >, 0 for <)
open(rcmd->file, rcmd->mode);          // open() returns LOWEST free fd = the one just closed
runcmd(rcmd->cmd);                     // exec; new program sees redirected fd
```
The trick: `open()` always returns the lowest-numbered free descriptor, so closing fd 1 then `open()`ing the file installs the file as fd 1. Robust real shells use `fd = open(...); dup2(fd, 1); close(fd);`. Append (`>>`) uses `O_APPEND`; `2>` redirects fd 2. **Forcing constraint:** redirection must happen in the *child, after fork, before exec* — if done in the shell it would clobber the shell's own stdout/stdin permanently.

### 1.6 Process groups, sessions, controlling terminal, job control
A session has one controlling terminal; the terminal has exactly one *foreground process group* at a time. Keyboard signals (Ctrl-C→SIGINT, Ctrl-Z→SIGTSTP) are delivered by the kernel to the foreground process group. (GNU libc "Job Control") The shell's responsibilities (GNU libc `init_shell`):
1. Loop on `tcgetpgrp(term)` until the shell IS the foreground group; if not, it receives/sends `SIGTTIN` to itself and waits.
2. Ignore the job-control signals so they don't kill the shell: `SIGINT, SIGQUIT, SIGTSTP, SIGTTIN, SIGTTOU` (and handle `SIGCHLD`).
3. `setpgid(0,0)` — put the shell in its own process group.
4. `tcsetpgrp(term, shell_pgid)` — make the shell the foreground group; save terminal modes with `tcgetattr`.

Launching a job (`launch_process`): in the child, `setpgid(pid, pgid)` (first process of the job becomes group leader); if foreground, `tcsetpgrp(term, pgid)` hands the terminal to the job; reset all signals to `SIG_DFL`; then `execvp`. The parent ALSO calls `setpgid(pid, pgid)` to avoid a race (set in both parent and child). Foreground (`put_job_in_foreground`): `tcsetpgrp` to the job, `waitpid(..., WUNTRACED)` until it exits or stops, then `tcsetpgrp` the terminal *back* to the shell and restore terminal modes with `tcsetattr`. Background job: skip the wait, leave terminal with the shell. (GNU libc "Implementing a Shell")
**Forcing constraint:** signals are delivered per *process group*, not per process; so each job needs its own pgrp, and ownership of the terminal must be explicitly handed back and forth via `tcsetpgrp` or Ctrl-C would hit the wrong processes (or the shell itself).

### 1.7 SIGCHLD reaping & zombies
"A child that terminates, but has not been waited for becomes a 'zombie.' The kernel maintains a minimal set of information (PID, termination status, resource usage)... to allow the parent to later perform a wait." (wait(2)) The shell reaps children to (a) get exit status and (b) free the kernel process-table slot. For background jobs the shell can't block on `waitpid`; it installs a `SIGCHLD` handler and reaps with `waitpid(-1, &st, WNOHANG | WUNTRACED)` in a loop. `WNOHANG` = return immediately if nothing changed; `WUNTRACED` = also report stopped children; `WCONTINUED` = report SIGCONT-resumed children. If the parent dies first, orphaned children are re-parented to init/subreaper which reaps them. (wait(2))
**Forcing constraint:** a shell that forks background jobs and never reaps leaks zombies until the process table fills. `WNOHANG` is mandatory so reaping doesn't block the interactive prompt.

### 1.8 Builtins vs external commands — and why `cd` MUST be a builtin
Dispatch (Brennan `lsh_execute`): linear-search argv[0] against the builtin table; if matched call the builtin function *in the shell process*; else `lsh_launch` (fork+exec). xv6 special-cases `cd` in `main()` *before* forking. **`cd` cannot be external:** "the current directory is a property of a process. So, if you wrote a program called `cd` that changed directory, it would just change its own current directory, and then terminate. Its parent process's current directory would be unchanged." (Brennan) The shell must call `chdir()` in *itself*. Same logic forces `exit`, `export`/env-setting, `jobs`/`fg`/`bg`, and `declare`/variable-setting to be builtins — they all mutate shell-process state that a forked child could not propagate back.

---

## 2. Foundational sources — exact links (one canonical per claim)

- **fork(2):** https://man7.org/linux/man-pages/man2/fork.2.html — fork returns twice; child inherits memory/fds/signal dispositions.
- **execve(2):** https://man7.org/linux/man-pages/man2/execve.2.html — replaces process image; only returns on error.
- **wait(2) / waitpid(2):** https://man7.org/linux/man-pages/man2/wait.2.html — zombie definition, WIFEXITED/WIFSIGNALED/WIFSTOPPED, WNOHANG/WUNTRACED/WCONTINUED, SIGCHLD, orphan re-parenting.
- **pipe(2):** https://man7.org/linux/man-pages/man2/pipe.2.html — pipefd[0]=read, pipefd[1]=write; kernel buffering; close unused ends for EOF.
- **dup2(2):** https://man7.org/linux/man-pages/man2/dup.2.html — `dup2(oldfd,newfd)` atomically aliases newfd to oldfd (fd-plumbing primitive for redirection/pipes).
- **Stephen Brennan, "Write a Shell in C":** https://brennan.io/2015/01/16/write-a-shell-in-c/ — canonical read→parse→fork→exec→wait loop, builtin table, why `cd` is a builtin.
- **GNU libc manual, "Implementing a Shell" / Job Control:** https://sourceware.org/glibc/manual/latest/html_node/Implementing-a-Shell.html (canonical mirror; the old gnu.org/software/libc URL 302-redirects to sourceware) — init_shell, launch_process, setpgid race, tcsetpgrp hand-off, put_job_in_foreground/background, WUNTRACED reaping. Job-control concept page: https://sourceware.org/glibc/manual/latest/html_node/Job-Control.html
- **xv6 `sh.c`:** https://github.com/mit-pdos/xv6-public/blob/master/sh.c — tiny real shell: getcmd/runcmd, EXEC/REDIR/PIPE/LIST/BACK command tree, exact pipe and redirect syscall sequences, cd special-case in main.
- **Julia Evans, "What happens when you start a process on Linux?":** https://jvns.ca/blog/2016/10/04/exec-will-eat-your-brain/ — fork-then-exec mental model ("a child that is a clone of myself... gets its brain eaten and turns into ls"), exec replaces image, zombies, signal/fd inheritance gotcha. Do **not** reuse the post's `posix_spawn = fork+exec` implementation shortcut for current Linux/glibc; factcheck confirmed glibc uses clone/vfork-style fast paths.
- **CodeCrafters "Build your own Shell":** https://app.codecrafters.io/courses/shell/overview ; course definition (exact stage list): https://github.com/codecrafters-io/build-your-own-shell/blob/main/course-definition.yml
- **build-your-own-x (shell entries):** https://github.com/codecrafters-io/build-your-own-x#build-your-own-shell — index of shell tutorials.

Distinct primary sources: **11** (5 man pages + Brennan + GNU libc manual [2 pages, counted once] + xv6 sh.c + Julia Evans + CodeCrafters).

---

## 3. "Why it's this way" — forcing constraints

- **Why fork/exec separation (not atomic spawn):** the post-fork/pre-exec window is the ONLY place a process can configure itself (fds, pgrp, signals, cwd) in its own context before becoming the target program. Redirection and pipe plumbing literally depend on this window existing. (Evans; xv6)
- **Why `cd` can't be a child process:** cwd is per-process state; a forked `chdir` dies with the child and never reaches the shell. Same for env vars and shell variables → forces a whole class of builtins. (Brennan)
- **Why zombies exist:** the kernel must retain exit status until the parent reads it; the parent–child wait contract requires the corpse to linger so status isn't lost in a race between child-exit and parent-wait. (wait(2))
- **Why controlling-terminal / process-group machinery:** terminal-generated signals (Ctrl-C/Ctrl-Z) are delivered to *the foreground process group* as a unit, so a pipeline's processes can be signaled together, and the shell can protect itself by living in a different group and handing the terminal to jobs via `tcsetpgrp`. Background processes touching the terminal get SIGTTIN/SIGTTOU. (GNU libc Job Control)
- **Why both parent and child call `setpgid`:** to eliminate a race — whichever runs first establishes the group; the other is a harmless no-op. The job must be in its group *before* the shell calls `tcsetpgrp`. (GNU libc)
- **Why close unused pipe ends:** EOF on a pipe is only signaled when ALL write-end fds are closed; a stray open write end (often in the parent) hangs the reader. (pipe(2))

---

## 4. Common misconceptions to preempt

1. **"exec creates a new process."** No — exec *replaces* the current process's image; the PID is unchanged. fork creates the process. (Evans, execve(2))
2. **"fork copies the whole memory immediately."** Conceptually a clone, but real kernels use copy-on-write; semantically the child gets an independent copy. (fork(2))
3. **"You only need to close the pipe ends in the children."** The PARENT must close both ends too, or readers never see EOF. (pipe(2))
4. **"cd is a program in /bin."** There may be a `/bin/cd` for scripting, but interactive `cd` is necessarily a shell builtin; an external one cannot change the shell's cwd. (Brennan)
5. **"waitpid just gets the exit code."** It also frees the zombie's process-table slot; not reaping background children leaks zombies. (wait(2))
6. **"Ctrl-C kills the foreground program because the shell forwards it."** No — the kernel delivers SIGINT directly to the foreground process *group*; the shell merely sets up who owns the terminal. (GNU libc)
7. **"A pipeline is one process per `|` managed by the shell sequentially."** All stages run *concurrently* as separate processes connected by pipes; the shell forks them all, then waits. (xv6)
8. **"Builtins are just for speed."** Some (cd/exit/export/jobs) are builtins out of *necessity* because they mutate shell state; speed is secondary. (Brennan)
9. **"`>` truncation/creation is the shell opening then handing a stream."** The shell sets the redirection by manipulating the child's fd table (close+open or dup2) before exec; the program is unaware it was redirected. (xv6)

---

## 5. Best build-your-own target(s) — milestone ladder

Recommended ladder (synthesizes Brennan + xv6 + CodeCrafters 8-stage core, ordered by syscall dependency):

- **M0 — REPL skeleton:** print prompt, read a line, tokenize into argv, loop. No exec yet. (Brennan `lsh_loop`; CodeCrafters "Print a prompt" → "Implement a REPL")
- **M1 — Builtins first:** `exit`, `echo`, `type`, then `pwd`/`cd` (chdir). Establishes builtin-table dispatch and the "why cd is a builtin" lesson before any forking. (CodeCrafters stages 4–12)
- **M2 — Run external commands:** PATH search → `fork()` + `execvp()` + `waitpid()`. Handle "command not found." This is the fork/exec/wait core. (Brennan `lsh_launch`; CodeCrafters "Locate executable files" → "Run a program")
- **M3 — Quoting/parsing:** single/double quotes, escapes — so later redirection/pipe tokens parse correctly. (CodeCrafters quoting stages)
- **M4 — Redirection:** `>`, `>>`, `<`, `2>` via `open()` + `dup2()` + `close()` in the child before exec. (xv6 REDIR; CodeCrafters redirect stages)
- **M5 — Pipelines:** `a | b` then N-stage, using `pipe()` + fork-per-stage + `dup2()` + disciplined closing of all ends; parent waits on all. (xv6 PIPE; CodeCrafters pipeline stages)
- **M6 — Job control (stretch):** process groups (`setpgid`), terminal hand-off (`tcsetpgrp`), background `&`, `SIGCHLD` reaping with `WNOHANG|WUNTRACED`, `jobs`/`fg`/`bg`, Ctrl-Z/SIGTSTP. (GNU libc job-control sample; CodeCrafters jobs stages)
- **M7 — Polish (optional):** history, tab completion, variables/expansion. (CodeCrafters history/completion/declare stages)

**Best single anchor for the lab:** Brennan for M0–M2 (cleanest C), xv6 `sh.c` for M4–M5 (smallest correct redirection+pipe code to read end-to-end), GNU libc sample for M6 (the only fully-worked job-control reference). CodeCrafters gives an automatically-graded stage ladder that maps almost 1:1 onto M0–M7.

---

## 6. Open questions / where sources disagree

- **`close+open` (lowest-fd trick) vs explicit `dup2`:** xv6 relies on `open()` returning the lowest free fd after `close(1)`; Brennan-style/modern code prefers explicit `dup2(fd,1); close(fd)`. Both correct; the dup2 form is more robust and portable for teaching. Lab should standardize on dup2.
- **`dup()` vs `dup2()` in xv6:** xv6 uses the older `close(1); dup(p[1])` idiom; equivalent to `dup2(p[1], 1)` but the dup2 atomic form is preferred. Cosmetic, worth flagging to learners reading xv6.
- **SIGCHLD-handler reaping vs synchronous `waitpid`:** for purely foreground shells a blocking `waitpid` suffices; background/job-control shells need an async `SIGCHLD` handler + `WNOHANG` loop. Sources present both; the lab should defer the handler until M6.
- **CodeCrafters exact stage count/order:** factcheck confirmed the raw `course-definition.yml` lists the canonical core 8 stages (`oo8` Print a prompt → `ip1` Run a program) plus extension tracks (navigation, quoting, redirection, pipelines, history, parameter expansion, completions). The "8 stages" figure refers only to the base track.
- **`posix_spawn` internals:** Evans' "fork and exec" shortcut is unsupported for current Linux/glibc. Factcheck confirmed glibc `spawni.c` uses `clone(CLONE_VM|CLONE_VFORK)` / `clone3` fast paths. Safe phrasing: conceptually spawn/fork+exec-like API; implementation is OS/libc-specific.
- **`SIGCHLD = SIG_IGN` behavior:** wait(2) notes that ignoring SIGCHLD (or SA_NOCLDWAIT) makes children not become zombies and wait() eventually fail with ECHILD — a portability nuance (POSIX-permitted, Linux-specific guarantees) worth a footnote, not a core lab requirement.

### Gaps / factcheck notes
- CodeCrafters stage **slugs/exact wording**: confirmed against raw `course-definition.yml`.
- glibc `posix_spawn` current implementation path: confirmed as clone/vfork-style fast path, not literal `fork()+exec`.
- Julia Evans direct "brain eaten / turns into ls" phrasing: confirmed in the live jvns.ca post. Do not quote any other phrasing verbatim unless directly sourced. The originally-cited jvns "how to run a program" 2016/02/20 URL 404s — the correct post is the 2016/10/04 "exec-will-eat-your-brain" one used here.
- xv6: used the classic `xv6-public` (x86) `sh.c`; the newer `xv6-riscv` `sh.c` is near-identical in structure — either is fine as a citation.
