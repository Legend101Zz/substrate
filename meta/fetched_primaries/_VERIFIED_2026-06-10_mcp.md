# VERIFIED — 2026-06-10 — MCP (Model Context Protocol) spec/architecture

Opportunistic + plan-mandated fetch for **29-mcp-skills-and-connectors**. Network healed:
modelcontextprotocol.io reachable (307→200). Saved to `meta/fetched_primaries/`.

## Source fetched
- **MCP Architecture overview** — https://modelcontextprotocol.io/docs/learn/architecture
  (current docs; references protocol spec version **2025-11-25**, examples use protocolVersion
  "2025-06-18"). File: `mcp-arch.txt` (21.6 KB, HTML→text; raw HTML + the JS-only `/specification`
  shell removed after extraction). The `/specification/2025-11-25` page is a client-rendered SPA
  shell (no server-side text) — the architecture doc is the authoritative prose for the
  load-bearing concepts.

## Verified VERBATIM claims (anchor 29)
- **Client-server architecture / participants:** "MCP follows a client-server architecture where an
  MCP host — an AI application like Claude Code or Claude Desktop — establishes connections to one or
  more MCP servers. The MCP host accomplishes this by creating one MCP client for each MCP server."
  - **MCP Host** = "The AI application that coordinates and manages one or multiple MCP clients";
  - **MCP Client** = "A component that maintains a connection to an MCP server and obtains context";
  - **MCP Server** = "A program that provides context to MCP clients".
- **Two layers:** "MCP consists of two layers: Data layer ... JSON-RPC based protocol ... and core
  primitives ... Transport layer : Defines the communication mechanisms and channels ...". "the
  data layer is the inner layer, while the transport layer is the outer layer."
- **Data layer = JSON-RPC 2.0:** "The data layer implements a JSON-RPC 2.0 based exchange protocol";
  "MCP uses JSON-RPC 2.0 as its underlying RPC protocol. ... Notifications can be used when no
  response is required."
- **Three server primitives:** "Tools : Executable functions that AI applications can invoke to
  perform actions ... Resources : Data sources that provide contextual information ... Prompts :
  Reusable templates that help structure interactions". Methods: discovery `*/list`, retrieval
  `*/get`, execution `tools/call`.
- **Client primitives:** "Sampling : Allows servers to request language model completions from the
  client's AI application" (`sampling/createMessage`); "Elicitation : Allows servers to request
  additional information from users" (`elicitation/create`); "Logging".
- **Cross-cutting utility primitive (Experimental):** "Tasks (Experimental) : Durable execution
  wrappers that enable deferred result retrieval and status tracking for MCP requests".
- **Two transports:** "Stdio transport : Uses standard input/output streams for direct process
  communication between local processes on the same machine ... no network overhead." "Streamable
  HTTP transport : Uses HTTP POST for client-to-server messages with optional Server-Sent Events
  ... supports standard HTTP authentication methods including bearer tokens, API keys, and custom
  headers. MCP recommends using OAuth".
- **Stateful + lifecycle/capability negotiation:** "MCP is a stateful protocol that requires
  lifecycle management. The purpose of lifecycle management is to negotiate the capabilities that
  both client and server support." Handshake: `initialize` request (with `protocolVersion`,
  `capabilities`, `clientInfo`) → response → `notifications/initialized`.
- **Tool discovery/exec wire format (verbatim from example):** `tools/list` (no params) →
  response `tools` array, each tool has `name`, `title`, `description`, **`inputSchema` (a JSON
  Schema)**; `tools/call` with `{name, arguments}` → response `content` array of typed objects.
- **Dynamic discovery + notifications:** "`listChanged`: true" capability →
  `notifications/tools/list_changed` (no `id`, JSON-RPC notification) → client re-requests
  `tools/list`. "Clients don't need to poll for changes; they're notified when updates occur."
- **Scope boundary:** "MCP focuses solely on the protocol for context exchange—it does not dictate
  how AI applications use LLMs or manage the provided context."

## What this anchors in 29
The whole sub-course: MCP = a **standard tool-contract transport + registry** that externalizes 23's
contract across a process/network boundary (03 RPC/transport). Host/client/server topology;
JSON-RPC 2.0 data layer; tools/resources/prompts primitives; stdio vs Streamable-HTTP transport;
capability negotiation; dynamic discovery via `*/list` + `list_changed` notifications.

## Still NOT fetched (carry-forward `[UNVERIFIED]` for 29)
- The formal `/specification/2025-11-25` schema (TypeScript/JSON-Schema definitions) — SPA shell,
  not server-rendered; the architecture doc covers the load-bearing semantics. Deeper field-level
  schema deferred to Phase 2.
- "Agent Skills" as a distinct MCP concept (the docs nav lists "Build with Agent Skills") — not
  extracted in depth this session.
- OAuth/authorization spec details, Streamable-HTTP session resumption, Registry/SEP governance.
- JSON-RPC 2.0 base spec (jsonrpc.org) + JSON Schema spec — referenced, not separately fetched
  (carried from 23).
