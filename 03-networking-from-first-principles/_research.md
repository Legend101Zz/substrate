# 03 — networking-from-first-principles · reconciled research brief

Status: Wave 1 research complete (3 of 3 clusters). Formal `factchecker` pass DEFERRED
(blocked by spend limit — see meta/SESSION_LOG.md and ADR-002).

Per-cluster briefs (read for full depth):
- `_research_cs144-sponge.md` — building a working TCP from the byte-stream up (Stanford CS144
  labs, now the **Minnow** framework, rewrite of the older **Sponge**; RFC 9293 TCP, RFC 6298 RTO).
  9 primary sources. Key build ladder: ByteStream → Reassembler → Wrap32+TCPReceiver → TCPSender.
- `_research_kurose-beej.md` — the layered model end-to-end + the sockets API that exposes it
  (Kurose & Ross *Top-Down*, free companion gaia.cs.umass.edu; Beej's Guide; End-to-End Arguments
  paper). 18 primary sources.
- `_research_stevens-hpbn.md` — wire-level IP/TCP headers + TLS/HTTP performance framing (Stevens
  *TCP/IP Illustrated v1*; Grigorik *HPBN*, free at hpbn.co; RFC 8446 TLS 1.3; QUIC/HTTP-3 RFCs).
  8 primary sources.

## Cross-cluster synthesis (the layer-by-layer spine)
Three altitudes that compose into the links→IP→TCP→TLS→HTTP arc:
- **Layering & the end-to-end argument** (Kurose §1 + Saltzer/Reed/Clark 1984) is the organizing
  principle: best-effort dumb IP core ⇒ reliability/ordering/security reconstructed at endpoints.
  This is WHY TCP exists and WHY congestion control is end-host (no central scheduler).
- **TCP mechanism, three views that reinforce:** (a) CS144 = the *algorithms you implement*
  (seq/ack reassembly, sliding window, retransmission timer w/ doubling RTO, TIME-WAIT=2·MSL,
  the 11-state machine); (b) Kurose = the *principles* (rdt building blocks, Go-Back-N/Selective
  Repeat, slow-start/AIMD/fast-retransmit congestion control); (c) Stevens = the *bytes on the wire*
  (header fields, options: MSS/window-scaling/SACK/timestamps, packet-level handshake/teardown).
- **Sockets API** (Beej) is the seam between kernel transport and user code:
  getaddrinfo→socket→bind→listen→accept (server) / →connect (client); byte-stream ⇒ short
  send/recv must loop; blocking vs non-blocking ⇒ select/poll ⇒ (epoll/kqueue) — the motivation
  for event-driven servers that sub-course 10 (nginx) and the own-http-server lab build on.
- **Performance forcing-function** (HPBN): speed of light fixes a latency floor ⇒ "eliminate round
  trips" explains slow start, keep-alive, TLS 1.3 1-RTT/0-RTT, HTTP/2 multiplexing/HPACK, and
  HTTP/3-over-QUIC (moved to UDP to escape TCP head-of-line blocking).

## Reconciliation notes / disagreements to resolve in Phase 2
- **CS144 framework naming:** the current labs are **Minnow** (modules only: sender/receiver);
  the hand-authored `TCPConnection` state-machine lab existed in the older **Sponge** ("Lab 4: the
  summit") and was dropped in Minnow (check4 is now "Measuring the real world"). DECISION NEEDED:
  if we want students to author the 11-state machine + teardown by hand, model it on Sponge Lab 4;
  Minnow alone won't cover it. (Logged context for Phase 2; not yet an ADR.)
- **Congestion control variant:** Kurose teaches Classic/Reno AIMD as the canonical mental model,
  but production Linux defaults to **CUBIC** and Google ships **BBR** (rate/loss-agnostic). Teach
  AIMD-as-principle and *name* CUBIC/BBR as reality. Congestion control is OUT of CS144 lab scope.
- **Layer-count framing:** K&R 5-layer vs OSI 7 vs TCP/IP 4. Pick K&R 5-layer as the spine and
  reconcile the others explicitly.
- **HTTP/3 + QUIC are NOT in the named clusters** (HPBN's TLS chapter predates/omits QUIC; Stevens
  predates it) — sourced from RFCs 9000/9001/9002/9114. This is the one real structural gap; add a
  QUIC/HTTP-3 source to RESEARCH_INDEX (done).

## Best build-your-own targets
- Keystone: **CS144 TCP lab ladder** (ByteStream→Reassembler→Receiver→Sender) = the own-tcp-ip lab.
- Bridge: **Beej sockets echo client/server → select/poll concurrent server → minimal HTTP/1.0
  server** (sets up sub-course 10 + own-http-server).
- Inspection: **tcpdump/Wireshark** packet reading against Stevens' header maps. (Minimal TLS
  client = advanced/optional.)

## Consolidated open questions / gaps (verify before drafting)
- [UNVERIFIED] Sponge Lab-4 `TCPConnection` handout not re-fetched directly (cross-checked via RFC
  9293 + doxygen/community). Minnow README "rewrite of Sponge" line 404'd — corroborated indirectly.
- End-to-End Arguments core thesis and bibliographic metadata factchecked against MIT plain-text
  primary source; safe citation: https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.txt.
- Beej exact `epoll`/`kqueue` coverage corrected: Beej §7 covers `select()` and `poll()` thoroughly
  but does **not** cover `epoll`/`kqueue`; use Linux `epoll(7)` / BSD `kqueue(2)` if teaching them.
- Date-sensitive numbers to re-check before teaching: HTTP/3 adoption %, HTTP/2 server-push
  deprecation status, QUIC CPU-cost figures (~2–4× TCP, narrows with GSO/GRO) remain citation-needed
  unless pinned to a specific measurement paper/data source with retrieval date.
- K&R full prose paywalled (claims verified against free companion slides/videos, not running text);
  Stevens 2nd-ed (Fall & Stevens) chapter renumbering not re-verified — cite by chapter TITLE.
- CS144 mirror cs144.keithw.org has a TLS cert-name mismatch — use the github.io PDFs.
- Verify per-OS congestion-control default if the course makes a factual claim.
