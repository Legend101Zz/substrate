# 29 · mcp-skills-and-connectors — RECONCILED research (`_research.md`)

> Phase-1 reconciliation (NO course prose; briefs only). 29 promotes **23's in-process tool
> CONTRACT to a wire PROTOCOL**: the standard that makes a tool a portable, discoverable,
> network-spanning **connector**. Bespoke structure: a protocol/connector walkthrough. Primary:
> **MCP architecture spec (FETCHED+VERIFIED)**. Full depth: `_research_mcp-skills-and-connectors.md`.
> Math: `_recompute.py` (18/18). Factcheck: `_factcheck_phase1.md` (0 blockers).

## 1. The one idea
**MCP is 23's tool contract promoted to a network protocol.** 23's contract lived inside the harness
process; 29 asks "what if the deterministic code lives in another process / team / company?" The
answer is a *standard* for the contract — same surface (name + JSON-Schema `inputSchema` + structured
result), plus the three things you only need once a tool crosses a boundary: a **transport** (03),
**dynamic discovery** (`*/list`), and **lifecycle/capability negotiation** (a distributed handshake).
Everything MCP adds beyond 23 is a *distributed-systems* concern → governed by Part I/II laws, not by
anything new about LLMs. VERIFIED scope: MCP "does not dictate how AI applications use LLMs or manage
the provided context" — it's plumbing; the loop/budget/selection stay the host's job.

## 2. The architecture, walked (VERIFIED verbatim)
- **Participants (03):** Host (the 28 harness) creates one **Client** per **Server**; one-client-
  per-server = a **bulkhead** (20). Servers run local (stdio) or remote (HTTP).
- **Two layers:** inner **data layer** (JSON-RPC 2.0) rides any outer **transport** — 03 layering;
  same message format over every transport.
- **Data layer = JSON-RPC 2.0:** request (`id` for correlation) / response / **notification** (no
  `id`, no response — 17's one-way async message). A `tools/call` is literally an RPC.
- **Primitives = the contract surface, IDENTICAL to 23:** server exposes **Tools** (act —
  `name`/`title`/`description`/**`inputSchema` JSON Schema**, the 23/07 schema-on-write surface),
  **Resources** (read-only context → 24/30), **Prompts** (templates → 24). Server can call *back*:
  **Sampling** (`sampling/createMessage`, model-independent), **Elicitation** (`elicitation/create`,
  built-in human-in-the-loop → 33), **Logging** (→19). Experimental **Tasks** = "durable execution
  wrappers ... deferred result retrieval and status tracking" = 26's durable jobs in the protocol.
- **Transports (03):** **Stdio** (local subprocess, "no network overhead", 02 pipes) vs **Streamable
  HTTP** (remote, HTTP POST + optional SSE, bearer/API-key/OAuth — "MCP recommends OAuth").
- **Lifecycle (11/26):** stateful; `initialize` (protocolVersion + capabilities + clientInfo) →
  server caps (e.g. `"tools":{"listChanged":true}`) → `notifications/initialized`. Version mismatch
  ⇒ "connection should be terminated" (11 compat). Statefulness is why 26 session-resume applies.
- **Discovery + notifications (17):** `*/list` makes listings dynamic; `list_changed` notifications
  push updates so clients don't poll (push>poll; saves the 19 poll cost).

## 3. The economics + the laws (RECOMPUTED — the headlines)
- **Why a protocol exists — N×M → N+M:** bespoke integrations = M·N; with one protocol = M+N
  (400→40 at M=N=20; ratio = N/2; grows with scale). The integration collapse IS the justification.
- **Union-toolbox tax (23):** connecting s servers gives K=s·t tools → K·S tokens/turn (5 servers →
  8000 tok = 6.25% of window). More connectors = more 22-quadratic cost + more **selection
  compounding** `1-(1-q)^N` over the union → motivates tool-retrieval (30) + per-task subsetting.
- **A remote server is a networked dependency (18/20):** `1-(1-p)^s` chance ≥1 is slow/down per turn
  (63.4%@s=100); remote p99 adds to the per-step budget → wrap in timeout/retry/breaker (18) +
  bulkhead (20).
- **Compatibility is a law (11/17):** negotiate-or-terminate (version-set intersection); schema
  evolution — optional add safe, new required field breaks callers (17 additive-only rule on
  `inputSchema`).

## 4. Connectors beyond tools
An MCP server is a **typed, discoverable, versioned plugin** for the harness, exposing tools (act) /
resources (read → 24/30) / prompts (templates → 24), reachable over stdio or HTTP. "Skills" layer
reusable capability bundles on top (`[UNVERIFIED]` depth this session).

## 5. Failure modes (all 03/11/17/18/20, not LLM failures)
Server unreachable/slow (18/20) · version mismatch (11) · schema drift breaks callers (17) · toolbox
bloat from too many connectors (23/24 → 30 retrieval) · stale tool list (17 `list_changed`) ·
session lost on reconnect (26) · **untrusted/compromised server = supply-chain + injection-via-tool-
result + ACE** (33 + 23 security: vet servers, sandbox, least-privilege OAuth scopes) · over-broad
scope. **Every failure decomposes to a Part I/II law.**

## 6. Build-your-own
Give the 28 harness an **MCP client**: stdio transport (subprocess + JSON-RPC framing, 02/03) →
`initialize` handshake + capability negotiation (11) → `tools/list` into the tool registry (23) →
route LLM tool calls to `tools/call` (22/23) → handle `list_changed` (17) → wrap remote calls in
timeout/retry/breaker (18) + per-server bulkhead (20). Break it: kill server mid-call → breaker
opens, graceful degrade; mount 5 servers → combined toolbox blows 23's budget → motivates 30.
Seventh harness upgrade (loop→tools→context→memory→persistence→orchestration→**connectors**).

## 7. Provenance summary
- **PRIMARY (FETCHED+VERIFIED):** MCP architecture spec — `meta/fetched_primaries/mcp-arch.txt`,
  receipt `_VERIFIED_2026-06-10_mcp.md`.
- **RECOMPUTED:** `_recompute.py` (18/18) — N×M→N+M, union-toolbox tax, selection compounding,
  remote-dependency tail, version/schema compat.
- **REUSED:** 02, 03, 07, 11, 17, 18, 19, 20, 22, 23, 24, 26, 28.
- **`[UNVERIFIED]` carry-forward (none load-bearing):** formal `/specification/2025-11-25` JSON-
  Schema/TS defs (SPA shell); "Agent Skills" depth; OAuth/auth + Streamable-HTTP resumption;
  Registry/SEP governance; JSON-RPC 2.0 base spec + JSON Schema spec (from 23); provider
  function-calling formats (23); injection-via-MCP-server + supply-chain vetting (→33).

---
**29 reconciled.** Part III "Phase 1 batch 3" now stands at **22-29 reconciled** (8 of 13 agentic
sub-courses). Next in dependency order: **30-rag-retrieval-and-grounding** (FETCH RAG, Lewis et al.
2020, arXiv 2005.11401; ↔ 06 structures + 08/16 caching + 24/25 retrieval-into-context + 14
partitioning), then 31 eval, as far as one clean checkpoint allows.
