# Verified primaries — Agentic System Design (Part III batch 3), 2026-06-10

Network healed this session for arxiv.org / kafka.apache.org / postgresql.org (all HTTP 200),
plus modelcontextprotocol.io (307 redirect, resolvable). Fetched + extracted with a throwaway
uv venv (`/tmp/pdfx-venv`, pypdf 6.13.2 from the Walmart external-pypi index) — venv removed after;
`/Users/m0t0hu6/.code-puppy-venv` was NEVER touched.

| source | file | what it anchors |
|--------|------|-----------------|
| Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", ICLR 2023 (arXiv 2210.03629) | `react-2210.03629.{pdf,txt}` (33 pp) | 22 the-agent-loop: interleaved reasoning-trace + action; thought→act→observe; overcomes CoT hallucination/error-propagation by interacting with an external API; +34% (ALFWorld) / +10% (WebShop) absolute success over imitation/RL with 1–2 in-context examples |
| Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools", NeurIPS 2023 (arXiv 2302.04761) | `toolformer-2302.04761.{pdf,txt}` (17 pp) | 23 tools-and-tool-contracts: a model trained to decide WHICH API to call, WHEN, WHAT arguments, and HOW to incorporate results; self-supervised (sample→execute→filter-by-loss-reduction); tools = calculator, Q&A, search, translation, calendar |

## Verbatim load-bearing quotes

### ReAct (2210.03629)
- Title: "REACT: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS" (Yao, Zhao, Yu, Du,
  Shafran, Narasimhan, Cao; Princeton + Google Research; ICLR 2023).
- Abstract: "we explore the use of LLMs to generate both reasoning traces and task-specific
  actions in an interleaved manner, allowing for greater synergy between the two: reasoning
  traces help the model induce, track, and update action plans as well as handle exceptions,
  while actions allow it to interface with and gather additional information from external
  sources such as knowledge bases or environments."
- "ReAct overcomes prevalent issues of hallucination and error propagation in chain-of-thought
  reasoning by interacting with a simple Wikipedia API".
- "ReAct outperforms imitation and reinforcement learning methods by an absolute success rate
  of 34% and 10% respectively, while being prompted with only one or two in-context examples."
  (ALFWorld and WebShop.)

### Toolformer (2302.04761)
- Title: "Toolformer: Language Models Can Teach Themselves to Use Tools" (Schick et al., Meta AI;
  NeurIPS 2023).
- Abstract: "We introduce Toolformer, a model trained to decide which APIs to call, when to call
  them, what arguments to pass, and how to best incorporate the results into future token
  prediction. This is done in a self-supervised way, requiring nothing more than a handful of
  demonstrations for each API. We incorporate a range of tools, including a calculator, a Q&A
  system, a search engine, a translation system, and a calendar."
- Method (§2): "Sample API Calls → Execute API Calls → Filter API Calls" — "filter out all calls
  which do not reduce the loss Li over the next tokens. All remaining API calls are interleaved"
  back into the dataset, then the LM is finetuned on it.

## Carry-forward / still to fetch next session
- **MCP spec** (modelcontextprotocol.io, 307) — deep-fetch the spec text for 29 (mcp-skills-and-
  connectors); this session only confirmed it resolves.
- **RAG** (Lewis et al. 2020, arXiv 2005.11401) — fetch for 30 (rag-retrieval-and-grounding).
- **Kafka paper / KIPs** (kafka.apache.org now 200) — opportunistic upgrade for 09/17 carried
  `[UNVERIFIED]`; deferred (time-boxed to land a clean 22/23 checkpoint first).
- **Postgres WAL/replication docs** (postgresql.org now 200) — opportunistic upgrade for 07/15;
  deferred.
- Still blocked: queue.acm.org 403 (CoDel), raft.github.io 000, dl.acm.org 403 (DOI landing).
