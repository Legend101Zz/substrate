# 00 · How to Use This Course

> *"What I cannot create, I do not understand."*
> — Richard Feynman, found written on his blackboard at the time of his death

Every other chapter in Substrate is something you study. This one is something you *consult*. It's
the map bolted to the wall by the entrance — the kind with a reassuring **YOU ARE HERE** dot — not a
lecture. Six short sections: what this is, how it's laid out, how to read a chapter, how to study it
with your coding agent, three ways through, and the house rules. Read it once, get your bearings,
then come back whenever the corridors start to look the same.

---

## 1. What this is & who it's for

Substrate is **one resource that goes all the way down.** That's the whole thesis, and it's a
deliberately greedy one: a serious learner should be able to understand how real systems work — and
how to design new ones — without reaching for another book, course, or tab. The name is the promise.
We don't stop at the surface where most material politely ends; we keep digging until we hit the
substrate, the bedrock of *why it has to be this way.*

So every concept here is taught from first principles, with **zero hand-waving.** When something is
built the way it is, we name the constraint, the paper, or the source file that forced its hand — and
we cite it. We never stop at "here's the API." We go down to "here's the physics, the math, or the
historical accident that gave the API its shape." There's a reason for the rigor:

> *"All non-trivial abstractions, to some degree, are leaky."*
> — Joel Spolsky, *The Law of Leaky Abstractions*

Every abstraction you use will eventually leak on you — usually at 3 a.m., usually in production. The
only durable defense is knowing what's underneath. That's what the second layer is for, because
every concept here is taught in **two layers, and the second is never skipped:**

1. an **intuitive mental model** you can hold in your head, then
2. the **deep mechanism** underneath it — the real data structures, the real protocol, the real
   tradeoff, the part that leaks.

If a skeptical senior engineer would find something glossed over, it isn't finished. That sentence is
the entire quality bar, and it is applied to every page — including this one.

**Who this is for.** A developer — often early in their career — who lives with AI coding agents all
day and is quietly tired of prompting blindly and hoping. You can read a little code. You can survive
in a terminal long enough to run a command. And, crucially, you're willing to *build* things, not
just read about them. That's the entire prerequisite list. You do **not** need a CS degree, and
nothing here has been dumbed down to spare you one — jargon gets defined the first time it appears,
and then we go straight down.

**The honest anti-promise.** This is long, and it is deep, and both of those are on purpose. It is
not a cheat sheet. It is not "Top 10 System Design Questions You'll Be Asked." It is not a weekend
skim you can claim on your résumé by Monday. What it offers instead is understanding that survives
contact with a real incident — the kind you cannot fake when the dashboards are red and everyone is
looking at you. If you came for a quick reference, this is, with great respect, the wrong door. If
you came to actually *get it* — welcome. Pour a coffee. This takes a while, and it's worth it.

---

## 2. The two-tier map: spine vs. appendices

Substrate has exactly two kinds of content, and the very first navigational skill — the thing that
keeps you from getting lost — is knowing which kind you're standing in. Read the wrong kind the wrong
way and you'll either drown a reference manual in exercises it doesn't have, or skim a lesson that
was meant to be built.

**The spine (units 00–34)** teaches **transferable concepts** — the ideas that show up in *every*
system, no matter which database, language, or cloud you happen to be cursing at this quarter. Spine
units are meant to be *worked through*, and wherever the material supports it, each one is paired with
a **build-your-own-X lab** in `/build`. You learn the log abstraction in unit 09, then you build a
small message queue. You learn TCP in unit 03, then you build a working TCP stack. This is the
Feynman doctrine from the epigraph, turned into a curriculum: concepts you've implemented are
concepts you actually own. The rest you're just renting.

**The appendices (A–O)** go **infinitely deep on ONE real system each** — Postgres, Redis, the JVM,
V8, Kafka, the Linux kernel, Kubernetes, and the rest of the usual suspects. They are
**reference-grade and information-only: no exercises, no tests, no labs.** Nobody reads an appendix
cover to cover, and you shouldn't either. Instead, the spine *cross-links down* into them: when unit
07 says "we shard here," it hands you a link to appendix F for how Postgres *actually* implements
MVCC and the WAL. Think of the appendices as the manuals on the bottom shelf — you pull one down,
open it to the exact page you need, and put it back.

The spine is organized into four parts:

| Part | Units | What it covers |
|------|-------|----------------|
| **Part 0 — Orientation** | 00 | This chapter: the map, the contract, the method. |
| **Part I — Foundations** | 01–12 | Computers, the shell, networking, OS internals, language runtimes, data structures, databases, caches, message queues, proxies/LBs, distributed-systems theory, reading papers. |
| **Part II — System Design** *(headline 1)* | 13–21 | Scaling math, partitioning, replication & consistency, caching/CDN, async/event-driven, rate limiting & backpressure, observability, resilience, and a capstone of design case studies. |
| **Part III — Agentic System Design** *(headline 2)* | 22–34 | The agent loop, tools, context engineering, memory, persistence, multi-agent orchestration, a build-your-own-harness track, MCP/connectors, RAG, evaluation, cost/ops, safety, and a capstone design canvas. |

The two **headlines** — *System Design* (13–21) and *Agentic System Design* (22–34) — are the
destination; they're why most people show up. Everything in Part I is the foundation they quietly
stand on. And the appendices (A–O) sit underneath all of it like the bedrock the whole structure is
driven into.

[DIAGRAM: D1 — the course map. A Mermaid graph showing Part 0 (00) → Part I (01–12) → Part II
(13–21) → Part III (22–34) as a left-to-right flow, with the two headline blocks (Part II, Part III)
visually highlighted, and the appendix shelf A–O drawn underneath as a reference layer that the
spine points down into. CONDENSED — parts + headlines + appendix shelf, NOT the full 34-node DAG
(the full dependency DAG lives in `meta/COURSE_MAP.md` and is linked from here). This is the single
most important visual in the repo.]

---

## 3. How to read a chapter

> *"The purpose of computing is insight, not numbers."*
> — Richard Hamming, *Numerical Methods for Scientists and Engineers*

Hamming was talking about arithmetic, but the principle is the whole house style: you're not here to
memorize facts, you're here to walk away with insight. To that end, most spine chapters follow the
same **default arc**, so once you've internalized the rhythm of one, you can feel the shape of all of
them coming:

> **theory → intuition → diagram(s) → implementation/walkthrough → tradeoffs → real-world case
> study**

Some units bend this arc to fit their material — computer architecture builds up from a single logic
gate, networking marches layer by layer, the papers unit is a series of guided paper-walkthroughs.
When a unit deviates, it tells you so up front in its own structure, because surprising the reader is
a cost, not a feature. But the spine of the spine never changes: **the intuitive model first, then
the deep mechanism — and the deep mechanism is never skipped.** Anyone can give you layer one. The
whole reason this course exists is layer two.

A handful of conventions appear on nearly every page. Learn to read them once, here, and they'll
fade into the background everywhere else:

- **Citations.** Every non-obvious claim is tethered to a source, and we strongly prefer **primary
  sources** — papers, source code, official docs — over blog posts about papers about source code. If
  a claim matters, there's one canonical link sitting next to it. Follow them; the citations are the
  receipts, and you are entirely within your rights to audit the till.
- **`[UNVERIFIED]` flags.** Honesty beats polish, every time.

  > *"The first principle is that you must not fool yourself — and you are the easiest person to
  > fool."*
  > — Richard Feynman, Caltech commencement address, 1974

  When we make a load-bearing claim we couldn't confirm against a primary source — the paper 404'd,
  the spec hid behind a paywall, the exact bit pattern simply wasn't fetchable — we stamp it
  **`[UNVERIFIED]`** rather than smile and assert it anyway (you'll see it inline, e.g. "the RTO
  doubles on each retransmit `[UNVERIFIED]`"). It's the academic equivalent of showing
  up to the exam and writing "I'm fairly sure, but don't quote me." Treat flagged claims with extra
  skepticism. And if you go verify one yourself, that's one of the most valuable contributions you
  can make (see §6).
- **Image prompts.** We never fabricate a screenshot or a photograph, because a confidently fake
  diagram is worse than no diagram. Where a *real* image would genuinely beat prose, you'll find an
  HTML comment like `<!-- IMAGE PROMPT: ... -->` describing the image we'd want generated, plus a
  one-line caption. Every last one is logged in
  [`assets/diagrams/image-prompts.md`](../assets/diagrams/image-prompts.md). Diagrams are a different
  animal — those we draw directly (Mermaid or ASCII) and render inline.
- **Cross-links down.** Whenever a spine chapter brushes up against a real system, it links *down*
  into the matching appendix (e.g. "see appendix G for how Redis actually implements eviction").
  Follow the link when you want the real-system depth; ignore it to stay on the concept. The trapdoor
  is always optional.
- **Build labs.** Most Part I and Part III spine chapters come with a `/build` lab that grows the
  very thing you just read about. The chapter teaches the concept; the lab makes you implement it, at
  which point it stops being trivia and becomes a thing you *know.* Do the labs. That's where renting
  turns into owning.

[DIAGRAM: D2 — anatomy of a chapter. An annotated callout/diagram of a single chapter showing where
each piece sits: the intuitive-layer block, the deep-mechanism block, an inline diagram, a cited
claim (with the citation called out), a cross-link arrow pointing DOWN into an appendix, and a link
out to the paired `/build` lab. Purpose: teach the reader to recognize these six recurring elements
on any page.]

---

## 4. The agent-paired learning method

> *"Talk is cheap. Show me the code."*
> — Linus Torvalds, Linux Kernel Mailing List

This is the part that makes Substrate different, and it's built for exactly the reader described in
§1: someone who already has a coding agent open in another window. Here's the reframe. **Use that
agent as a tutor and a lab partner — not as an answer key.** Reading a concept explains it to you;
being *interrogated* about it, and *building* with it, is what fuses it into your brain. Your agent is
the most patient Socratic tutor in human history and it never sighs, never checks the clock, and never
runs out of follow-up questions. It would be a small tragedy to use all that on "write my function."
Point it at the chapter you just finished and put it to work.

Below are reusable prompt templates. Copy one, swap in the chapter or lab, and run it with your own
agent.

**(a) Quiz me at the senior bar.**
```
You are a skeptical senior engineer. I just read Substrate chapter <N> on <topic>.
Ask me 5 questions, one at a time, escalating from "do you know the mechanism" to
"can you reason about the tradeoff under load." After each answer, tell me what I got
wrong or hand-waved, and cite the precise idea I missed. Do NOT give me the answers up front.
```

**(b) Extend the build lab with one feature + tests.**
```
Here is my current code for the /build/<lab> lab from chapter <N>: <paste or point to files>.
Propose ONE realistic next feature that the chapter implies but doesn't yet cover.
Explain why it matters, then guide me to implement it myself with a failing test first.
Don't write the implementation for me — review mine and push back where it's weak.
```

**(c) Explain this diagram / re-derive it from scratch.**
```
Here is diagram <D?> from Substrate chapter <N>: <paste the Mermaid or describe it>.
First explain what it shows in plain language. Then make me re-derive it from first
principles: ask me to reconstruct the boxes and arrows from the underlying mechanism,
and correct me where my version is wrong or missing a constraint.
```

**(d) Check my mental model — find the hand-wave.**
```
I'm going to explain <concept from chapter N> back to you in my own words: <your explanation>.
Act as the skeptical senior engineer from the chapter. Find every place I hand-waved,
oversimplified, or stated something I can't actually justify. Ask me to ground each one
in a constraint, a paper, or a source. Don't be polite about gaps.
```

**A worked example of (a).** Say you've just finished unit 09 (message queues & the log abstraction).
You paste template (a) with `<N> = 09` and `<topic> = the log abstraction and consumer offsets`. A
good agent eases you in — *"What is a partition, and why is it the unit of parallelism?"* — and then,
once you've answered, twists the knife in the most educational way: *"You said consumers track their
own offset. Walk me through what happens to delivery guarantees if a consumer crashes after
processing a message but before committing its offset. Is that at-least-once or at-most-once, and
why?"* That second question is the senior bar in the flesh. If you can't answer it cleanly, you've
just discovered — for free, with no manager watching — exactly which paragraph to go re-read. Which
was the entire point.

> The method in one line: **read it, get quizzed on it, build with it, then explain it back and let
> the agent hunt your hand-waves.** Four passes, and the concept stops being something you read and
> becomes something you know.

---

## 5. Three reading paths

Nobody's checking whether you went cover to cover, so pick the path that matches why you actually came
here. These three orders are the **single source of truth in
[`meta/COURSE_MAP.md`](../meta/COURSE_MAP.md)** — if this table and the map ever drift apart, the map
wins and this chapter is the one that's wrong. (Self-awareness is also a first principle.)

| Path | Who it's for | The order |
|------|--------------|-----------|
| **Linear (cover-to-cover)** | You want the whole thing, properly. | `00 → 01 → 02 → … → 34` (the number line is a verified topological sort of the dependency DAG). |
| **"I just need System Design"** | You want Part II and the foundations it leans on. | `00 → skim 01, 03, 04, 06 → 11 → 13 → 14–21` |
| **"I just need Agentic"** | You want Part III and already have the foundations. | `00 → (assume fluency in 04, 09, 13, 17, 18, 19, 20) → 22 → 23 → 24 → 25 → 26 → 27 → 28 → 29 → 30 → 31 → 32 → 33 → 34`, dipping into appendix M on demand. |

Three notes on those paths:

- The **number line itself is a valid topological sort** — verified against the dependency DAG's
  adjacency list — so the linear path will never ask you to use a concept before it's been taught.
  The chapters are numbered in an honest order, which is rarer than it should be.
- The **Agentic path assumes** you're already fluent in a handful of foundation units (OS internals,
  message queues/logs, scaling math, async architecture, rate limiting, observability, resilience).
  Unit 22 explicitly bridges from those foundations into the agent loop, so if any of them are rusty,
  that bridge is your on-ramp — no shame in doubling back across it.
- **Appendices A–O are never on a path.** You pull them in on demand from spine cross-links, like
  reference manuals. Reading an appendix front to back is the studying equivalent of reading the
  dictionary: technically possible, rarely advisable.

[DIAGRAM: D3 — the three reading paths. A Mermaid swimlane / path diagram with three lanes (Linear,
System-Design-only, Agentic-only), each lane showing its unit sequence as a chain of nodes, so the
reader can see at a glance how the two shortcut paths skip and re-merge relative to the full number
line. Must stay identical to the orders in COURSE_MAP.]

---

## 6. Conventions & contributing

> *"Programs must be written for people to read, and only incidentally for machines to execute."*
> — Harold Abelson & Gerald Jay Sussman, *Structure and Interpretation of Computer Programs*

A course is just a very long program whose runtime is your attention, so we hold the prose to the
same standard. A few house rules make that possible.

**Citation style.** Primary sources first: papers, RFCs, source code, official/vendor docs — in that
order of preference, always over blogs. One canonical link per claim. **Books are cited by chapter
title rather than page or edition number**, because page numbers rot between editions but "the chapter
on write-ahead logging" will still find the right pages in whatever edition you happen to own.

**The `[UNVERIFIED]` flag** (a deliberate echo of §3, because it's that important): a load-bearing
claim we couldn't confirm against a primary source. It is never silently dropped and never quietly
laundered into fact. If a primary source later becomes reachable and confirms it, the flag is upgraded
to verified with a reconcile note and a saved receipt — nothing is ever erased. We'd rather show our
working and be caught being uncertain than be caught being wrong.

**The `/build` directory** holds every build-your-own-X lab, and each spine chapter that has one links
straight to it. The labs are stacked: later stages stand on earlier ones (the agentic capstone
harness, for instance, is grown across the whole of Part III as eleven stacked upgrades — it ends up
genuinely impressive, and you will have built every layer). Start any lab from the chapter that
introduces it, not from the middle.

**The image-prompt manifest** lives at
[`assets/diagrams/image-prompts.md`](../assets/diagrams/image-prompts.md). Every `<!-- IMAGE PROMPT
-->` placeholder anywhere in the course is logged there with its path, prompt, and caption — so the
complete set of "real images we'd want" is auditable in exactly one place, instead of scattered like
loose receipts.

**Contributing.** Substrate is public and contribution-friendly — it was written to help everyone who
stumbles onto it later, possibly including future you. The most valuable contributions, in order:

- **Verify an `[UNVERIFIED]` claim** against a primary source and include that source. This directly
  raises the floor of the entire course, and there is no contribution we love more.
- **Fix an error or a hand-wave.** If a skeptical senior engineer would object to something, that's
  not a nitpick — that's a bug. File it.
- **Improve a diagram or a lab.** Clearer Mermaid, a sharper worked example, one more lab stage.

To contribute: **file an issue** describing the gap, error, or improvement (and link the primary
source if you're verifying a claim), then open a pull request. Contributions are held to the **same
quality bar as the original material** — both layers present (intuition *and* deep mechanism), the
*why* grounded in a real constraint or source, claims cited to primaries, and absolutely no
hand-waving. The bar does not bend for contributors, and that refusal to bend is precisely what makes
the course worth trusting in the first place.

---

> That's the whole orientation. You now know what Substrate is, how it's shaped, how to read a
> chapter, how to study it with your agent, which path is yours, and what the house rules are. The map
> has done its job; the rest is territory. **Head to unit 01 — or jump to your path's first stop — and
> let's start going all the way down to the substrate.**
