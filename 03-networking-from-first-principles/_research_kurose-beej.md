# 03 — Research brief: Kurose & Ross Top-Down + Beej's Guide

> Source cluster: Kurose & Ross, *Computer Networking: A Top-Down Approach* (9th ed., companion site gaia.cs.umass.edu) for the layered model end-to-end; Beej's *Guide to Network Programming* (beej.us/guide/bgnet) for the Berkeley sockets API that exposes it. One citation hop on the WHY: Saltzer/Reed/Clark, "End-to-End Arguments in System Design" (1984).
> Method: primary sources first; exact link per claim; [UNVERIFIED] flagged; gaps flagged. The K&R full text is paywalled (Pearson) — verified content is from the authors' free companion site (online lectures index + per-section video pages + downloadable `.pptx` slide decks), which list each section's exact topic coverage. Slide-deck URLs are canonical and stable.

---

## 1. Key mechanisms (deep, precise, with forcing constraint each)

**A. The 5-layer Internet model & encapsulation.** K&R Ch.1 frames the Internet protocol stack as five layers: application, transport, network, link, physical. Each layer takes the upper layer's PDU as payload and prepends its own header (encapsulation): app message → transport *segment* (TCP/UDP header) → network *datagram* (IP header) → link *frame* (e.g., Ethernet header/trailer). Forcing constraint: a layer may only use the service of the layer directly below and only serves the layer directly above — this *abstraction boundary* is what lets each layer change independently (fiber vs wifi at link; TCP vs UDP at transport) without rewriting the others. Source: Ch.1 online lecture (videos/1).

**B. DNS resolution.** K&R §2.4. Hierarchical, distributed database: root servers → TLD servers (`.com`, `.org`) → authoritative servers (the zone's own records). A local/recursive resolver caches results (with TTLs) so most lookups never reach root. Distinguishes *recursive* queries (resolver chases the chain on the client's behalf) from *iterative* queries (each server returns a referral to the next). Forcing constraint: no single server can hold or serve the whole namespace at Internet scale → hierarchy + heavy caching are mandatory, not optional. Source: §2.4 video (youtu.be/6lRcMh5Yphg).

**C. HTTP request/response over TCP.** K&R §2.2. HTTP is a stateless, text-based request/response protocol running over a TCP connection (default port 80; 443 for TLS). Persistent connections reuse one TCP connection for multiple objects (vs non-persistent: one connection per object → extra RTTs + slow-start cost each time). Statelessness is patched at the app layer with cookies. HTTP/2 adds multiplexing over a single connection. Forcing constraint: HTTP assumes a reliable, in-order byte stream → it *requires* TCP's guarantees and does not re-implement them (clean example of layering). Source: §2.2 part 1/2 (youtu.be/S9GEPaQ1lFs, youtu.be/4M39gEPWPYs).

**D. IP addressing, subnets, forwarding vs routing, NAT.** K&R §4.1, §4.3. *Forwarding* = local, per-router, per-packet data-plane action: look up the destination in the forwarding table and move the packet to the right output port (fast, hardware). *Routing* = network-wide, control-plane process that computes the forwarding tables (slower, algorithmic). IPv4 §4.3 covers addressing, NAT, and IPv6. NAT lets a whole private network share one public IP by rewriting (src IP, src port) on the way out and reversing it on the way back, keyed by a translation table. Forcing constraint: forwarding must run at line rate per packet, so it is deliberately separated from the expensive global routing computation — the data-plane/control-plane split. Source: §4.1 slides (videos/4/1/4.1_video_slides.pptx), §4.3 slides (videos/4/3/4.3_video_slides.pptx).

**E. ARP & the link layer.** K&R §6.1, §6.4. The link layer moves *frames* between two nodes on the same link, identified by 48-bit MAC addresses (flat, hardware-burned, not hierarchical like IP). ARP resolves a next-hop *IP address* → *MAC address* on the local subnet by broadcasting a query and caching the reply. Ethernet switches are self-learning (build a MAC-to-port table from observed source addresses) and forward within a LAN without IP. Forcing constraint: IP is logical/routable but the wire only understands MAC, so every hop needs an IP→MAC translation (ARP) to actually put bits on the local link. Source: §6.1 (youtu.be/lMGWJZLTulY), §6.4 slides (videos/6/4/6.4_video_slides.pptx).

**F. Reliable data transfer principles (rdt).** K&R §3.4. Builds reliability on an unreliable channel from primitives: checksums (detect corruption), ACKs/NAKs, sequence numbers (detect duplicates/reorder), timers + retransmission (recover loss). Pipelining + Go-Back-N and Selective Repeat give throughput beyond stop-and-wait. Forcing constraint: the underlying network layer (IP) is best-effort (may drop, dup, reorder), so *all* reliability must be reconstructed at the endpoints from these mechanisms. Source: §3.4 video (youtu.be/nyUHUtmxWg0).

**G. TCP & congestion control: slow start, AIMD, congestion avoidance, fast retransmit.** K&R §3.5–§3.7. TCP adds connection setup (3-way handshake), RTT estimation/timeout, and flow control (receiver-advertised window). Congestion control (§3.7, "Classic TCP"): *slow start* — `cwnd` starts at ~1 MSS and doubles each RTT (exponential) until a threshold or loss; *congestion avoidance* — past `ssthresh`, `cwnd` grows linearly (+1 MSS/RTT); *AIMD* (additive-increase/multiplicative-decrease) — additive linear growth while healthy, halve `cwnd` on a loss signal; *fast retransmit* — 3 duplicate ACKs trigger immediate resend without waiting for timeout (fast recovery avoids dropping back to slow start). §3.7 also covers ECN, delay-based TCP, and fairness. Forcing constraint: there is no central network scheduler, so each sender must *probe* available bandwidth and *back off* on loss; AIMD is the rule that makes independent senders converge to a fair, stable share. Source: §3.5 (youtu.be/UYJP-6mhF6E), §3.6 (youtu.be/Fm92xvIp6JY), §3.7 (youtu.be/cIHiSR4j3g4).

**H. Sockets API lifecycle.** Beej §5–6. The API that exposes transport to user code.
- **TCP server:** `getaddrinfo()` (with `AI_PASSIVE`) → `socket()` → `bind()` → `listen(backlog)` → `accept()` (returns a *new* fd per connection) → `send()`/`recv()` → `close()`.
- **TCP client:** `getaddrinfo()` → `socket()` → `connect()` → `send()`/`recv()` → `close()`.
- Key semantics (Beej §5.7): `send()` returns *bytes actually sent* (may be < requested → must loop); `recv()` returns `0` when the peer has closed; both return `-1`/`errno` on error. `getaddrinfo()` fills a linked list of `struct addrinfo`; cast `ai_addr` to `struct sockaddr*`. `shutdown(how)` (0=recv,1=send,2=both) half-closes vs `close()`.
- **Byte order** (Beej §3.2): `htons/htonl` (host→network) and `ntohs/ntohl` (network→host) convert to big-endian "network byte order" for ports and addresses. `inet_pton`/`inet_ntop` (§3.4) convert string ↔ binary address.
- Forcing constraint: TCP is a *byte stream*, not a message stream → short `send`/`recv` are normal and the app must frame/loop itself.
Sources: Beej "System Calls or Bust" (html/split/system-calls-or-bust.html), client/server skeletons §6.

**I. Blocking vs non-blocking + select/poll motivation.** Beej §7. Sockets block by default: `recv()`/`accept()` sleep until ready. `fcntl(fd, F_SETFL, O_NONBLOCK)` makes calls return immediately with `EAGAIN`/`EWOULDBLOCK` — but naive polling busy-waits and burns CPU. I/O multiplexing solves this: `select()` (fd_set bitsets via `FD_ZERO/FD_SET/FD_ISSET`, `timeval` µs timeout, modifies sets in place, limited fd range) and `poll()` (array of `struct pollfd{fd,events,revents}`, ms timeout, no fd-range limit). One thread watches many sockets; the OS wakes it only when some socket is ready. Forcing constraint: thread-per-connection costs memory + context-switching at thousands of connections → event-driven multiplexing is the bridge to production successors like Linux `epoll` and BSD/macOS `kqueue`. Source: Beej §7 (html/split/slightly-advanced-techniques.html). Factcheck correction: Beej covers `select()`/`poll()` thoroughly but does **not** cover `epoll`/`kqueue`; use `epoll(7)` / `kqueue(2)` primary docs if the course teaches those APIs directly.

---

## 2. Foundational sources — exact links (one canonical per claim)

- K&R companion site (root, 9th ed.): https://gaia.cs.umass.edu/kurose_ross/index.php
- K&R online lectures index (chapter map): https://gaia.cs.umass.edu/kurose_ross/online_lectures.htm
- Ch.1 layering/encapsulation: https://gaia.cs.umass.edu/kurose_ross/videos/1/
- §2.2 Web & HTTP: https://youtu.be/S9GEPaQ1lFs (part 1), https://youtu.be/4M39gEPWPYs (part 2)
- §2.4 DNS: https://youtu.be/6lRcMh5Yphg
- §3.3 UDP: https://youtu.be/VjBDgcNno-Q
- §3.4 Reliable data transfer: https://youtu.be/nyUHUtmxWg0
- §3.5 TCP (handshake, flow control): https://youtu.be/UYJP-6mhF6E
- §3.6 Principles of congestion control: https://youtu.be/Fm92xvIp6JY
- §3.7 TCP congestion control (slow start, AIMD, fast retransmit): https://youtu.be/cIHiSR4j3g4
- §4.1 forwarding vs routing, data/control plane: https://gaia.cs.umass.edu/kurose_ross/videos/4/1/4.1_video_slides.pptx
- §4.3 IP addressing, NAT, IPv6: https://gaia.cs.umass.edu/kurose_ross/videos/4/3/4.3_video_slides.pptx
- §6.1 link layer intro: https://youtu.be/lMGWJZLTulY
- §6.4 ARP, Ethernet, switches, VLANs: https://gaia.cs.umass.edu/kurose_ross/videos/6/4/6.4_video_slides.pptx
- Beej's Guide (root): https://beej.us/guide/bgnet/html/
- Beej §5–6 sockets calls + client/server skeletons: https://beej.us/guide/bgnet/html/split/system-calls-or-bust.html
- Beej §3.2/§3.4 byte order + inet_pton: https://beej.us/guide/bgnet/html/ (sections 3.2 Byte Order, 3.4 IP Addresses)
- Beej §7 blocking, select, poll: https://beej.us/guide/bgnet/html/split/slightly-advanced-techniques.html
- Citation hop (WHY layering / end-to-end): Saltzer, Reed, Clark, "End-to-End Arguments in System Design," ACM TOCS 2(4), Nov 1984, pp.277–288: https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf

---

## 3. "Why it's this way" — forcing constraints

- **Why layering & the end-to-end argument.** Saltzer/Reed/Clark (1984): a function (e.g., reliable delivery, error recovery, encryption) often *cannot be completely or correctly* implemented by the network's lower levels; the endpoints must do it anyway, so doing it in the network is redundant cost. Hence put application-specific guarantees at the edges and keep the core simple/dumb. This is the principled justification for why IP is best-effort and TCP's reliability lives in the end hosts. Factcheck confirmed the thesis against MIT's primary plain-text version: https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.txt.
- **Why congestion control is end-host, not network.** The IP core offers no admission control or central scheduler (consequence of the dumb-core/end-to-end design). With no one to throttle them, senders must self-regulate by probing and backing off → TCP's slow-start + AIMD. K&R §3.6 ("causes and costs of congestion," approaches to congestion control) motivates this directly.
- **Why NAT exists.** IPv4 address exhaustion + the desire to put many private hosts behind one public address. NAT rewrites address/port so a whole LAN multiplexes one global IP. K&R §4.3. (Side effect: breaks strict end-to-end addressability — a tension noted vs the e2e argument.)
- **Why DNS hierarchy & caching.** Scale + availability: no single authority can serve the global namespace, and round-trips to root for every name would be fatal to latency. Delegated hierarchy distributes authority; TTL-based caching at resolvers absorbs the vast majority of queries. K&R §2.4.

---

## 4. Common misconceptions to preempt

- **TCP vs UDP tradeoffs.** TCP ≠ "better"; it adds reliability, ordering, flow + congestion control at the cost of latency (handshake, head-of-line blocking, retransmit waits). UDP is the right tool when the app wants timeliness over completeness or implements its own logic (DNS, real-time media, QUIC-over-UDP). Tie to §3.3 vs §3.5.
- **What a socket actually is.** A socket is *not* a connection or a wire — it is a local file-descriptor handle to a kernel endpoint. `accept()` returns a *new* socket per connection while the listening socket keeps listening. Beej §5–6.
- **NAT is not a firewall.** NAT translates addresses; its "protection" is an incidental side effect of having no inbound mapping. A firewall is a deliberate policy filter. They are independent mechanisms often co-located. K&R §4.3.
- **Layering is not strict in practice.** Real systems leak across layers: NAT (L3) inspects/edits L4 ports; TLS sits awkwardly between L4 and L7; HTTP/3 (QUIC) reimplements transport over UDP. The 5-layer model is a teaching abstraction, not an enforced runtime boundary.
- **"Network byte order = my machine's order."** No — it is fixed big-endian; you must call `htons`/`htonl` even if your host happens to match. Beej §3.2.

---

## 5. Best build-your-own target(s)

- **Primary: a sockets-based TCP echo client + server in C** following Beej §6 skeletons. Server: `getaddrinfo(AI_PASSIVE)` → `socket` → `bind` → `listen` → `accept` loop → `recv`/`send` echo → `close`. Client: `getaddrinfo` → `socket` → `connect` → `send`/`recv` → `close`. Forces the learner to confront partial `send`/`recv` (must loop), byte order, and `addrinfo`. Direct primary-source backing: Beej "System Calls or Bust" + §6.
- **Extension 1: concurrent server via `select()`/`poll()`** (Beej §7) — replace blocking accept-loop with one event loop over many fds; demonstrates the multiplexing motivation firsthand.
- **Extension 2 (sets up "own-http-server" later): a minimal HTTP/1.0 server** layered on the TCP server — parse a `GET` request line, return a status line + headers + body. This makes the layering concrete (HTTP rides the byte stream; the server re-frames messages itself) and is the natural bridge into the TLS → HTTP arc of this sub-course.
- **Optional: raw DNS query over UDP** (`socket(SOCK_DGRAM)`, hand-build a DNS query, send to a resolver) — concrete §2.4 + UDP exercise; smaller scope.

---

## 6. Open questions / where sources disagree

- **Which congestion-control variant to teach.** K&R §3.7 centers on "Classic TCP" (Reno-style AIMD with fast retransmit/recovery) but also covers ECN and delay-based TCP. Modern Linux defaults to CUBIC; Google's BBR is loss-agnostic/rate-based. The textbook AIMD mental model is pedagogically canonical but not what production stacks run by default — decide whether the course teaches AIMD-as-principle and *names* CUBIC/BBR as the real-world reality. [Verify exact default per OS if course makes a factual claim.]
- **OSI 7-layer vs TCP/IP 4-layer vs K&R 5-layer.** K&R deliberately uses a 5-layer model (adds physical below link, drops OSI's session/presentation). OSI is 7; the IETF/TCP-IP model is often drawn as 4 (folding link+physical into "link/network access"). These are framings of the same reality; the course must pick one spine (recommend K&R 5-layer for this cluster) and explicitly reconcile the others to avoid student confusion.
- **epoll/kqueue depth.** Beej teaches `select`/`poll` thoroughly; factcheck found `epoll`, `kqueue`, and `IOCP` are **not covered** in Beej §7. Gap: if the course targets high-concurrency servers, use non-Beej primaries such as Linux `epoll(7)` and BSD/macOS `kqueue(2)` man pages.
- **End-to-end paper page-level quotes.** The MIT PDF did not auto-extract to text in this pass; thesis is captured from the verified ACM citation + abstract. Any verbatim quotation must be re-pulled from the PDF directly. [UNVERIFIED at page level.]
- **K&R full prose is paywalled.** All section-level claims above are verified against the authors' free companion site (lecture index + per-section topic descriptions + downloadable slide decks), which reliably enumerate each section's coverage, but not against the book's running text. Slide decks (.pptx) are the deepest free primary; pull those if exact figures/numbers are needed.
