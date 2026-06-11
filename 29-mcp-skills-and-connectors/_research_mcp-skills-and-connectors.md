# 29 · mcp-skills-and-connectors — research brief (Phase 1, briefs only)

> Bespoke structure: a **PROTOCOL / CONNECTOR WALKTHROUGH** — NOT abstract source clusters and NOT
> the 13-20 four-cluster shape. 29 is where 23's tool *contract* leaves the process and becomes a
> *wire protocol*: it walks the standard that makes a tool a portable, discoverable, network-spanning
> connector (host/client/server → transport → data layer → primitives → lifecycle → discovery →
> failure/security). Primary: the **Model Context Protocol (MCP)** architecture spec
> (FETCHED+VERIFIED). Math: `_recompute.py`. Factcheck: `_factcheck_phase1.md`.

---

## 0. What this sub-course IS

23 defined a tool as an **API contract between a stochastic caller and deterministic code**, living
*inside* the harness process. 29 asks the next question: **what if the deterministic code lives in a
different process, a different team's repo, or a different company's server?** The answer is a
*standard* for the contract — a wire protocol so any host can talk to any tool-provider without
bespoke glue. MCP is that standard (the de-facto one as of 2025), and it is the worked example for
the whole sub-course. The transferable concept is **the connector**: 23's contract + 03's transport
+ a discovery/registry mechanism.

This is the **N×M → N+M** integration argument: M hosts × N tool-providers needs M·N bespoke
integrations without a standard; with one protocol it collapses to M+N (each side implements the
protocol once). That collapse is the entire reason a tool *protocol* exists (recomputed).

---

## 1. The headline idea

**MCP is 23's tool contract promoted to a network protocol.** It standardizes the contract surface
(name + JSON-Schema `inputSchema` + structured result — *identical shape* to 23) and adds the three
things you only need once a tool crosses a boundary: a **transport** (03), **dynamic discovery**
(`*/list`), and **lifecycle/capability negotiation** (a distributed handshake). Everything MCP adds
beyond 23 is a *distributed-systems* concern — which means 29's hard parts are governed by Part I/II
laws (03 transport/RPC, 11 versioning/compat, 17 async notifications, 18/20 failure of a remote
dependency, 26 stateful-session resume), not by anything new about LLMs.

VERIFIED scope boundary (MCP arch doc): "MCP focuses solely on the protocol for context exchange—it
does not dictate how AI applications use LLMs or manage the provided context." So MCP is a *plumbing*
standard; the loop (22), context budget (24), and selection (23) are still the host's job.

---

## 2. The architecture, walked (VERIFIED verbatim against the MCP arch doc)

### 2.1 Participants — a client-server topology (03)
VERIFIED: "MCP follows a client-server architecture where an MCP host ... establishes connections to
one or more MCP servers ... by creating one MCP client for each MCP server."
- **Host** = the AI application (the harness from 28 — "like Claude Code or Claude Desktop");
  coordinates one or many clients.
- **Client** = one connection manager per server; "obtains context from an MCP server".
- **Server** = "A program that provides context to MCP clients" — runs local or remote.
One-client-per-server is a **bulkhead** (20): a flaky server isolates to its own client.

### 2.2 Two layers (the inner/outer split — a clean 03 layering)
VERIFIED: "MCP consists of two layers: Data layer ... JSON-RPC based protocol ... Transport layer ...
communication mechanisms". "the data layer is the inner layer, while the transport layer is the
outer layer." This is exactly 03's layering discipline: the same JSON-RPC 2.0 message format rides
*any* transport (transport abstracts away connection/framing/auth).

### 2.3 Data layer = JSON-RPC 2.0 (a typed RPC, reuse 03)
VERIFIED: "The data layer implements a JSON-RPC 2.0 based exchange protocol". Requests carry an
`id` for request-response correlation; **notifications carry no `id`** ("no response is expected") —
the async one-way message of 17. A tool call is literally an RPC: `tools/call {name, arguments}` →
`{content:[...]}`. This is 23's "a tool call is an RPC" made concrete.

### 2.4 Primitives (the contract surface — IDENTICAL to 23)
VERIFIED, three **server** primitives:
- **Tools** — "Executable functions that AI applications can invoke to perform actions" (the 23
  contract). Each tool object: `name`, `title`, `description`, **`inputSchema` (a JSON Schema)** —
  the *same* schema-on-write validation surface as 23/07.
- **Resources** — "Data sources that provide contextual information" (read-only context → feeds 24;
  the read side of 30's grounding).
- **Prompts** — "Reusable templates that help structure interactions" (24's few-shot/templates,
  now server-provided).

Plus **client** primitives (the server can call *back* into the host): **Sampling**
(`sampling/createMessage` — server asks the host's LLM for a completion, staying model-independent),
**Elicitation** (`elicitation/create` — server asks the *user* for input/confirmation; a built-in
human-in-the-loop hook, ties to 33 safety), **Logging** (→19 observability). And an Experimental
cross-cutting primitive: **Tasks** — "Durable execution wrappers that enable deferred result
retrieval and status tracking" — i.e. 26's durable-execution/long-running-job pattern, in the
protocol itself.

### 2.5 Transports (reuse 03)
VERIFIED, two:
- **Stdio** — "standard input/output streams for direct process communication between local
  processes on the same machine ... no network overhead." Local server = subprocess (02 pipes).
- **Streamable HTTP** — "HTTP POST for client-to-server messages with optional Server-Sent Events
  for streaming"; remote; "standard HTTP authentication ... bearer tokens, API keys ... MCP
  recommends using OAuth." Remote server = a networked dependency → 18/20 apply in full.
Same data layer over both: transport is swappable (03 layering pays off).

### 2.6 Lifecycle + capability negotiation (a distributed handshake → 11)
VERIFIED: "MCP is a stateful protocol that requires lifecycle management ... to negotiate the
capabilities that both client and server support." Handshake: client `initialize`
(`protocolVersion`, `capabilities`, `clientInfo`) → server response (its capabilities, e.g.
`"tools":{"listChanged":true}`) → client `notifications/initialized`. **Version negotiation:** "If a
mutually compatible version is not negotiated, the connection should be terminated." This is 11's
schema/version-compatibility problem (and 17's schema evolution) as a startup protocol —
**statefulness** is what makes 26 (session resume) relevant to MCP.

### 2.7 Dynamic discovery + notifications (the registry, reuse 17)
VERIFIED: discovery via `*/list` ("client can first list all available tools (`tools/list`) and then
execute them. This design allows listings to be dynamic"). Change propagation via JSON-RPC
notifications: a server with `"listChanged":true` sends `notifications/tools/list_changed` (no `id`)
→ client re-requests `tools/list`. VERIFIED rationale: "Clients don't need to poll for changes;
they're notified when updates occur" — push over poll, the 17 event-driven pattern; avoids the 19
cardinality/poll cost.

---

## 3. The economics + the laws (RECOMPUTED)
- **N×M → N+M integration collapse:** M hosts, N servers: bespoke = M·N integrations; protocol =
  M+N. For M=N=20: 400 → 40 (**10× fewer**); the saving grows quadratically. *This is why a
  protocol exists.* (recomputed)
- **Dynamic discovery feeds 23/24's budget problem:** a host connected to many servers can mount a
  huge combined toolbox → 23's toolbox tax `K·S` tokens/turn and selection compounding
  `1-(1-q)^N` apply to the *union* of all servers' tools. More connectors = more context cost +
  more mis-selection → motivates tool-retrieval (→30) and per-task tool subsetting. (recomputed)
- **A remote MCP server is a networked dependency (18/20):** add its tail latency to the loop's
  per-step budget; wrap calls in timeout + retry + breaker (18); the one-client-per-server topology
  is a bulkhead (20); `1-(1-p)^N` says more servers raise the chance ≥1 is slow/down per turn.
  (recomputed)
- **Capability/version mismatch is a compatibility law (11/17):** negotiate-or-terminate; tool
  schemas evolve → additive/optional changes are safe, required-field changes break callers (the
  17 schema-evolution rule applied to `inputSchema`). (recomputed)

---

## 4. Connectors beyond tools (the full picture)
A connector exposes any of: **tools** (act), **resources** (read context → 24/30), **prompts**
(templates → 24). "Skills" (the docs' "Build with Agent Skills") layer reusable capability bundles
on top — `[UNVERIFIED]` in depth this session. The mental model: an MCP server is a *typed,
discoverable, versioned plugin* for the harness (28), reachable over stdio or HTTP.

## 5. Failure modes (all are 03/11/17/18/20 failures, not LLM failures)
Server unreachable/slow (18 timeout/retry/breaker, 20 bulkhead) · version mismatch (11 negotiate-or-
terminate) · schema drift breaks callers (17 evolution rules) · toolbox bloat from too many
connectors (23/24 budget → 30 retrieval) · stale tool list (17 `list_changed` notification) ·
session lost on remote reconnect (26 stateful resume) · **untrusted server = supply-chain + prompt-
injection-via-tool-result + ACE** (33 + 23 security: a malicious/compromised MCP server can return
poisoned content or dangerous tool definitions — vet servers, sandbox, least-privilege OAuth scopes)
· over-broad OAuth scope (least privilege). **Every failure decomposes to a Part I/II law.**

## 6. Build-your-own
Give the 28 harness an **MCP client**: implement the stdio transport (subprocess + JSON-RPC framing,
02/03), do the `initialize` handshake + capability negotiation (11), `tools/list` into the harness's
tool registry (23), route the LLM's tool calls to `tools/call` (23/22), handle `list_changed`
notifications (17), wrap every remote call in timeout/retry/breaker (18) and a per-server bulkhead
(20). Break it: kill the server mid-call → breaker opens, harness degrades gracefully; mount 5
servers → watch the combined toolbox blow 23's budget → motivates tool-retrieval (30). Seventh
harness upgrade (loop→tools→context→memory→persistence→orchestration→**connectors**).

## 7. Provenance + `[UNVERIFIED]`
- **PRIMARY (FETCHED+VERIFIED):** MCP architecture spec — `meta/fetched_primaries/mcp-arch.txt`,
  receipt `_VERIFIED_2026-06-10_mcp.md` (host/client/server; two layers; JSON-RPC 2.0; tools/
  resources/prompts + sampling/elicitation/logging + Tasks; stdio vs Streamable-HTTP; lifecycle/
  capability negotiation; `*/list` + `list_changed`).
- **RECOMPUTED:** `_recompute.py` — N×M→N+M collapse, union-toolbox tax + selection compounding,
  remote-dependency tail (18/20), version/schema compat.
- **REUSED:** 02 (pipes/subprocess), 03 (transport/RPC/layering), 07 (schema-on-write), 11
  (versioning/compat), 17 (async notifications, schema evolution, push>poll), 18 (timeout/retry/
  breaker), 19 (logging), 20 (bulkhead/tail), 22 (the loop), 23 (the tool contract), 24 (resources/
  prompts into context), 26 (stateful session/Tasks durability), 28 (the harness this plugs into).
- **`[UNVERIFIED]` carry-forward (none load-bearing):** formal `/specification/2025-11-25` JSON-
  Schema/TS definitions (SPA shell, not server-rendered); "Agent Skills" concept depth; OAuth/auth
  spec + Streamable-HTTP session resumption; Registry/SEP governance; JSON-RPC 2.0 base spec
  (jsonrpc.org) + JSON Schema spec (carried from 23); provider function-calling formats (23).
  Injection-via-MCP-server + supply-chain vetting → 33.
