# 29 · Phase-1 factcheck — mcp-skills-and-connectors

> Method (same discipline as 13-28): every load-bearing claim is (a) VERIFIED verbatim against the
> fetched MCP architecture spec, (b) RECOMPUTED in `_recompute.py` (18/18 pass), (c) REUSED from a
> line-verified Part I/II + 22-28 anchor, or (d) flagged `[UNVERIFIED]` carry-forward. 0 blockers.

## Bespoke structure note
29 is a **PROTOCOL / CONNECTOR WALKTHROUGH** (host/client/server → layers → data layer → primitives
→ transport → lifecycle → discovery → economics → failure), NOT abstract clusters and NOT the 13-20
four-cluster shape. It promotes 23's in-process tool *contract* to a wire *protocol*. Plan-sanctioned
("FETCH the MCP spec; ↔ 23 tool contracts + 03 transport").

## Primary fetched + verified THIS session
| source | file | what it anchors |
|--------|------|-----------------|
| Model Context Protocol — Architecture overview (modelcontextprotocol.io, spec 2025-11-25; examples protocolVersion 2025-06-18) | `mcp-arch.txt` | host/client/server topology; two layers; JSON-RPC 2.0 data layer; tools/resources/prompts + sampling/elicitation/logging + Tasks; stdio vs Streamable-HTTP; lifecycle/capability negotiation; `*/list` + `list_changed` |

Receipt: `meta/fetched_primaries/_VERIFIED_2026-06-10_mcp.md` (verbatim quotes logged there).

### Verified claims (MCP arch doc — verbatim)
- Client-server: "MCP follows a client-server architecture where an MCP host ... establishes
  connections to one or more MCP servers ... by creating one MCP client for each MCP server." Host/
  Client/Server role definitions VERIFIED verbatim. (Anchors §2.1; one-client-per-server = bulkhead.)
- Two layers: "MCP consists of two layers: Data layer ... Transport layer"; "the data layer is the
  inner layer, while the transport layer is the outer layer." VERIFIED. (Anchors §2.2; 03 layering.)
- Data layer = JSON-RPC 2.0: "The data layer implements a JSON-RPC 2.0 based exchange protocol";
  "Notifications can be used when no response is required." VERIFIED. (Anchors §2.3; 17 async.)
- Three server primitives Tools/Resources/Prompts with the exact gloss VERIFIED; tool object fields
  `name`/`title`/`description`/`inputSchema` (a JSON Schema) VERIFIED from the example. (Anchors §2.4
  — the contract surface is IDENTICAL to 23/07 schema-on-write.)
- Client primitives Sampling (`sampling/createMessage`), Elicitation (`elicitation/create`),
  Logging VERIFIED; Tasks (Experimental) "Durable execution wrappers ... deferred result retrieval
  and status tracking" VERIFIED. (Anchors §2.4 — Tasks ↔ 26 durable execution; Elicitation ↔ 33 HITL.)
- Two transports: Stdio "no network overhead" (local), Streamable HTTP "HTTP POST ... optional
  Server-Sent Events ... bearer tokens, API keys ... MCP recommends using OAuth" VERIFIED. (§2.5; 03.)
- Stateful + lifecycle: "MCP is a stateful protocol that requires lifecycle management ... negotiate
  the capabilities"; handshake initialize→response→`notifications/initialized`; "If a mutually
  compatible version is not negotiated, the connection should be terminated." VERIFIED. (§2.6; 11/26.)
- Discovery + notifications: `*/list` "allows listings to be dynamic"; `"listChanged":true` →
  `notifications/tools/list_changed` (no `id`); "Clients don't need to poll ... they're notified".
  VERIFIED. (§2.7; 17 push>poll.)
- Scope boundary: "MCP focuses solely on the protocol for context exchange—it does not dictate how
  AI applications use LLMs or manage the provided context." VERIFIED. (§1 — MCP is plumbing only.)

## Recomputed claims (`_recompute.py`, 18/18)
- **N×M → N+M collapse** (400→40 at M=N=20; ratio = N/2; grows with scale) — the reason a protocol
  exists. PASS.
- **Union-toolbox tax** K=s·t, K·S tokens/turn (5 servers → 8000 tok = 6.25% of window) — 23's tax
  over the union, motivates tool-retrieval (30). PASS.
- **Selection compounding** 1-(1-q)^N over the union (9.6%/18.3%/63.6% at N=5/10/50) — 23/13/20/21
  identity. PASS.
- **Remote-dependency tail** 1-(1-p)^s (9.6%@s=10, 63.4%@s=100) + step-latency inflation
  (local+remote_p99=320ms) — 18/20 over connectors. PASS.
- **Version negotiation** = nonempty version-set intersection (connect) / empty (terminate); schema
  evolution: optional add compatible, new required field breaks callers — 11/17. PASS.

## Reused (line-verified Part I/II + 22-28)
02 (pipes/subprocess for stdio); 03 (transport/RPC/layering); 07 (schema-on-write); 11 (versioning/
compat/negotiate); 17 (async notifications, schema evolution, push>poll, outbox); 18 (timeout/retry/
breaker); 19 (logging); 20 (bulkhead/fan-out tail); 22 (loop); 23 (tool contract, toolbox tax,
selection compounding); 24 (resources/prompts into context); 26 (stateful session/Tasks durability);
28 (the harness MCP plugs into).

## `[UNVERIFIED]` — carry-forward (do NOT harden into prose)
- Formal `/specification/2025-11-25` (TypeScript/JSON-Schema definitions) — client-rendered SPA
  shell, not server-rendered; the architecture doc covers load-bearing semantics; field-level schema
  deferred to Phase 2.
- "Agent Skills" as a distinct MCP concept — listed in docs nav, not extracted in depth this session.
- OAuth/authorization spec details; Streamable-HTTP session resumption; Registry/SEP governance.
- JSON-RPC 2.0 base spec (jsonrpc.org) + JSON Schema spec — referenced, not separately fetched
  (carried from 23); provider function-calling formats (23).
- Injection-via-MCP-server + supply-chain server-vetting → 33.

## Verdict
29 is honest and protocol-appropriate: the architecture (host/client/server, two layers, JSON-RPC
2.0, the three+three primitives, two transports, lifecycle/capability negotiation, dynamic
discovery) is VERIFIED verbatim against the MCP spec; the economics (N×M collapse, union-toolbox
tax, selection compounding, remote-dependency tail, version/schema compat) are RECOMPUTED; every
hard part REUSES a line-verified 03/11/17/18/20/23/26 law. Residual `[UNVERIFIED]` are the formal
schema + Skills + auth details, none load-bearing for the connector model. Reconcile into
`_research.md`.