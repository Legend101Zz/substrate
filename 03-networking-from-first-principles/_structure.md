# 03 — Networking From First Principles · _structure.md

**Identity:** how two machines talk, built bottom-up from a dumb best-effort link to a
working browser request — with the reader implementing TCP along the way.

**Bespoke shape — "the layer-climb, with one organizing principle on top."** Strict
bottom-up ascent (link → IP → TCP → TLS → HTTP), but framed throughout by ONE forcing idea
introduced first: the **end-to-end argument** (dumb core, smart endpoints) explains WHY each
upper layer exists. Each transport mechanism is shown at three reinforcing altitudes:
the algorithm you implement (CS144), the principle (Kurose), the bytes on the wire
(Stevens). The keystone build (your own TCP) runs in parallel with the chapters.

## Dependency position
- **Depends on:** 02 (sockets are fds; send/recv loop like pipes), light 01/04.
- **Feeds into:** 09 (the log ships over the network), 10 (proxies/LB/event-driven servers
  build directly on the sockets+epoll seam here), 11 (distributed systems assume this
  network model), 13/16 (latency floor, CDN), 26 (resume = network failure recovery).
- **Appendix links DOWN:** none owned; cross-links UP from 10/11. (No dedicated networking
  appendix — 03 itself is the deep reference; QUIC/HTTP-3 sourced from RFCs.)

## Chapter specs (3–5 lines each)
1. **The end-to-end argument & the layer model** — why a dumb best-effort IP core +
   smart endpoints (Saltzer/Reed/Clark 1984). Pick K&R **5-layer** as the spine; reconcile
   OSI-7 / TCP/IP-4 explicitly. This chapter is the lens for all the rest.
2. **Links and addressing** — frames, MAC, switching; then IP: addressing, routing,
   fragmentation, best-effort delivery (no guarantees — that's the point). Why the core
   stays simple.
3. **TCP I — reliability from unreliability** — the reconstruction job: byte-stream
   abstraction, sequence/ack, the Reassembler, sliding window. Kurose's rdt building
   blocks + Go-Back-N/Selective-Repeat as principle; CS144 ByteStream→Reassembler as
   the algorithm you write.
4. **TCP II — timers, teardown, state machine** — retransmission timer with RTO doubling
   (RFC 6298), the 11-state machine, handshake/teardown, TIME-WAIT = 2·MSL. CS144
   Wrap32+TCPReceiver+TCPSender; Stevens for the bytes (header fields, options:
   MSS/window-scale/SACK/timestamps).
5. **Congestion control** — slow-start / AIMD / fast-retransmit as the *principle* (Kurose);
   then name reality: Linux default **CUBIC**, Google **BBR** (rate/loss-agnostic). Note:
   congestion control is OUT of CS144 lab scope — teach AIMD as the mental model.
6. **The sockets API seam** — getaddrinfo→socket→bind→listen→accept / connect (Beej);
   byte-stream ⇒ short send/recv must loop; blocking vs non-blocking ⇒ select/poll ⇒
   (epoll/kqueue). This is the on-ramp to 10 + the own-http-server lab.
7. **TLS — security at the endpoints** — why crypto lives at the edge (end-to-end again):
   TLS 1.3 1-RTT/0-RTT handshake (RFC 8446), what it guarantees (confidentiality/
   integrity/authentication). Mechanism over math; defer crypto internals.
8. **HTTP and the latency war** — HTTP/1.1 → keep-alive → HTTP/2 multiplexing/HPACK →
   HTTP/3 over QUIC (UDP, escapes TCP head-of-line blocking; RFCs 9000/9001/9002/9114).
   Driven by HPBN's forcing function: speed of light fixes a latency floor ⇒ kill round trips.

## Paired build lab (/build → own-tcp-ip-stack, own-http-server)
**Keystone:** CS144 TCP ladder (ByteStream→Reassembler→Receiver→Sender) = own-tcp-ip-stack,
running alongside ch.3–4. **Bridge:** Beej echo client/server → select/poll concurrent
server → minimal HTTP/1.0 server (sets up 10 + own-http-server). **Inspection:**
tcpdump/Wireshark against Stevens' header maps.

## Diagrams needed
- The 5-layer stack with encapsulation (headers nesting); end-to-end vs hop-by-hop.
- TCP 3-way handshake + 4-way teardown sequence diagram; the 11-state machine.
- Sliding window + cumulative ack animation-style figure; RTO doubling timeline.
- Slow-start/AIMD sawtooth; CUBIC vs Reno shape (named, illustrative).
- TLS 1.3 1-RTT vs 0-RTT handshake; HTTP/1.1 vs /2 multiplexing vs /3-QUIC HOL-blocking.

## Sources / gaps to honor (from _research.md)
- **ADR NEEDED (logged in _research):** CS144 current labs are **Minnow** (modules only);
  the hand-authored 11-state `TCPConnection` lived in the older **Sponge** "Lab 4." If we
  want students to author the state machine, model it on Sponge Lab 4 — Minnow alone won't
  cover it. → I will file this as an ADR in DECISIONS.md at finalize (2i).
- `[UNVERIFIED]` Sponge Lab-4 handout (cross-checked via RFC 9293 + community). End-to-End
  paper verified at MIT plain-text URL. Beej covers select/poll, NOT epoll/kqueue — use
  `epoll(7)`/`kqueue(2)` if teaching them.
- Date-sensitive, re-check before teaching: HTTP/3 adoption %, HTTP/2 server-push
  deprecation, QUIC CPU cost (~2–4× TCP, narrows w/ GSO/GRO) — pin to a dated measurement.
- Cite K&R/Stevens by chapter TITLE (edition drift); use github.io PDFs for CS144
  (cs144.keithw.org cert mismatch).
