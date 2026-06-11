# 29 — MCP, Skills & Connectors · _structure.md

**Identity:** the Part III chapter that promotes **23's in-process tool CONTRACT to a wire PROTOCOL**.
23 made a tool a typed function the loop can call inside the harness process; 29 asks "what if the
deterministic code lives in another process / team / company?" The answer is a *standard* for that
contract plus the three things you only need once a tool crosses a boundary: a **transport** (03),
**dynamic discovery** (`*/list`), and **lifecycle/capability negotiation** (a distributed handshake).
Everything MCP adds beyond 23 is a *distributed-systems* concern governed by Part I/II laws — not by
anything new about LLMs.

**Bespoke shape — "a protocol/connector walkthrough where every layer is an OLD law wearing a new
name."** NOT four clusters, NOT a feature tour of one vendor's SDK. Walk the live MCP architecture
(host/client/server, two layers, JSON-RPC, primitives, transports, lifecycle, discovery) and at each
stop name the Part I/II law that already explains it: JSON-RPC = 03 RPC; notification = 17 one-way
async; `inputSchema` = 23/07 schema-on-write; one-client-per-server = 20 bulkhead; `initialize` =
11 capability negotiation; `list_changed` = 17 push>poll; remote server = 18/20 networked dependency.
The thesis: **MCP is plumbing; the loop/budget/selection stay the host's job.** Primary is
FETCHED+VERIFIED (MCP architecture spec). Math recomputed (18/18). The `/build` deliverable: give the
28 harness an **MCP client** — the seventh harness upgrade.

## Dependency position
- **Depends on:** 23 (the in-process contract this generalizes) + 28 (the harness that hosts the
  client) + 03 (transport/RPC/layering) + 11 (capability negotiation, version compat) + 17 (async
  notifications, additive-only schema evolution) + 18 (timeout/retry/breaker for a remote dependency)
  + 20 (bulkhead, tail of a networked call) + 02 (stdio pipes) + 07 (schema-on-write) + 19 (logging)
  + 24 (resources/prompts feed the window) + 26 (stateful session resume).
- **Feeds into:** 30 (a RAG server is an MCP **resource** `search_corpus`; toolbox bloat motivates
  tool-retrieval) + 31 (logging/tracing the cross-process call) + 32 (the union-toolbox token tax,
  priced) + 33 (an untrusted/compromised server = supply-chain + injection-via-tool-result + ACE) +
  34 ("+ external tool ecosystem → add 29" is one branch of the design tree).
- **Appendix links DOWN:** I-docker (sandbox an untrusted server) · L-consensus (the stateful-session
  / version-compat reasoning) · M-agentic-papers (the MCP spec anchor). 29 owns ONLY the
  contract→protocol promotion; tool *design* stays in 23, retrieval in 30, threats in 33.

## Section specs (3–5 lines each)
1. **The one idea: a tool that crosses a process boundary needs a protocol** — 23's contract lived
   inside one process; the moment the deterministic code is remote you need a transport, discovery,
   and a handshake. MCP standardizes exactly that and nothing more: VERIFIED, it "does not dictate how
   AI applications use LLMs or manage the provided context." The loop, budget, and tool-selection stay
   the host's responsibility — MCP is the wire, not the brain.
2. **The architecture, walked (VERIFIED verbatim)** — Host creates one Client per Server
   (one-client-per-server = a 20 bulkhead); servers run local (stdio) or remote (HTTP). Two layers: an
   inner **data layer** (JSON-RPC 2.0) rides any outer **transport** (the 03 layering split). A
   `tools/call` is literally an RPC; a `notification` (no `id`, no response) is 17's one-way async
   message. Map each MCP noun to its Part I law as you go.
3. **The primitive surface is IDENTICAL to 23** — server exposes **Tools** (act: `name`/`title`/
   `description`/**`inputSchema` JSON Schema** — the 23/07 schema-on-write surface), **Resources**
   (read-only context → 24/30), **Prompts** (templates → 24). Server-initiated callbacks: **Sampling**
   (model-independent), **Elicitation** (built-in human-in-the-loop → 33), **Logging** (→19).
   Experimental **Tasks** = 26's durable jobs lifted into the protocol (deferred result + status).
4. **Transports + lifecycle + discovery (03/11/17/26)** — **Stdio** (local subprocess, no network
   overhead, 02 pipes) vs **Streamable HTTP** (remote, POST + optional SSE, bearer/API-key/OAuth).
   Lifecycle is stateful: `initialize` (protocolVersion + capabilities) → server caps → `initialized`;
   version mismatch ⇒ terminate (11 compat). `*/list` makes listings dynamic; `list_changed`
   notifications push updates so clients don't poll (17 push>poll). Statefulness is why 26 resume applies.
5. **The economics + the laws (RECOMPUTED)** — **N×M → N+M:** bespoke integrations cost M·N; one
   protocol costs M+N (400→40 at M=N=20; ratio N/2, grows with scale) — the integration collapse IS
   the justification. **Union-toolbox tax (23):** s servers → K=s·t tools → K·S tokens/turn (5 servers
   → 8000 tok = 6.25% of window) → more 22-quadratic cost + selection compounding `1-(1-q)^N` →
   motivates 30 retrieval + per-task subsetting. A remote server is a 18/20 networked dependency
   (`1-(1-p)^s` ≥1 slow/down per turn = 63.4%@s=100). Compatibility is a law (11/17 negotiate-or-
   terminate; additive-only schema evolution).
6. **Connectors & "skills" beyond tools** — an MCP server is a typed, discoverable, versioned plugin
   exposing tools/resources/prompts over stdio or HTTP; "skills" layer reusable capability bundles on
   top (`[UNVERIFIED]` depth — teach the connector model now, don't harden the skills spec yet).
7. **Failure modes (all 03/11/17/18/20 — not LLM failures)** — server unreachable/slow (18/20) ·
   version mismatch (11) · schema drift breaks callers (17) · toolbox bloat (23/24 → 30) · stale tool
   list (17 `list_changed`) · session lost on reconnect (26) · **untrusted/compromised server =
   supply-chain + injection-via-tool-result + ACE** (→33: vet servers, sandbox, least-privilege OAuth
   scopes). Every failure decomposes to a Part I/II law.

## Paired build lab (/build → own-coding-agent-harness, seventh upgrade)
Give the 28 harness an **MCP client**: stdio transport (subprocess + JSON-RPC framing, 02/03) →
`initialize` handshake + capability negotiation (11) → `tools/list` into the 23 tool registry → route
LLM tool calls to `tools/call` (22/23) → handle `list_changed` (17) → wrap remote calls in
timeout/retry/breaker (18) + per-server bulkhead (20). Acceptance = DEMONSTRATE THE WALL THEN THE FIX:
kill the server mid-call → breaker opens, graceful degrade; mount 5 servers → the combined toolbox
blows 23's token budget → motivates 30.

## Diagrams needed
- Host ↔ Client ↔ Server topology (one-client-per-server = bulkhead boundary).
- The two-layer stack: JSON-RPC data layer over stdio / Streamable-HTTP transports (03 layering).
- The MCP-noun → Part-I/II-law map (RPC, notification, inputSchema, initialize, list_changed…).
- N×M bespoke integrations vs N+M with a protocol (the integration-collapse payoff).
- The `initialize` capability-negotiation handshake (sequence diagram, 11).
- Union-toolbox token tax: s servers → K tools → K·S tokens/turn vs the window.
- Failure-mode map: each MCP failure → the Part I/II law that explains/fixes it.

## Sources / gaps to honor (from _research.md — DO NOT erase)
- **PRIMARY (FETCHED+VERIFIED):** MCP architecture spec — `meta/fetched_primaries/mcp-arch.txt`,
  receipt `_VERIFIED_2026-06-10_mcp.md`.
- **RECOMPUTED:** `_recompute.py` (18/18) — N×M→N+M, union-toolbox tax, selection compounding,
  remote-dependency tail, version/schema compat.
- **REUSED:** 02, 03, 07, 11, 17, 18, 19, 20, 22, 23, 24, 26, 28.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** formal `/specification/2025-11-25` JSON-Schema/
  TS defs; "Agent Skills" depth; OAuth/auth + Streamable-HTTP resumption; Registry/SEP governance;
  JSON-RPC 2.0 base spec + JSON Schema spec (from 23); provider function-calling formats (23);
  injection-via-MCP-server + supply-chain vetting (→33). Teach the protocol now; do NOT harden the
  formal spec/auth/governance specifics until fetched.
- **Boundary discipline:** tool *design* stays in 23; tool *retrieval* in 30; threats/vetting in 33;
  sandbox in appendix I. 29 owns ONLY the contract→protocol promotion + the "it's all Part I/II laws"
  proof.
