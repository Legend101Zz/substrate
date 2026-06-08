# 03 — Research brief: Stevens TCP/IP Illustrated + Grigorik HPBN

> Cluster: the wire-level reality of IP/TCP (Stevens, by chapter) and the TLS/HTTP layers that ride on top, framed by performance forcing-functions (Grigorik HPBN, free at hpbn.co), with TLS 1.3 handshake confirmed against RFC 8446. Each mechanism is paired with the physical/protocol constraint that forces it. HTTP/3 + QUIC drawn from RFC 9000/9114 + Wikipedia/measurement papers (HPBN predates QUIC; flagged).

---

## 1. Key mechanisms (deep & precise, each with its forcing constraint)

### IP header & fragmentation / MTU — Stevens Ch 3 (IP)
- **IPv4 header**: 20 bytes minimum. Fields: Version (4b), IHL/header-length (4b), Type-of-Service/DSCP (8b), Total Length (16b), Identification (16b), Flags (3b: reserved, **DF** Don't Fragment, **MF** More Fragments), Fragment Offset (13b, in 8-byte units), TTL (8b), Protocol (8b — 6=TCP, 17=UDP, 1=ICMP), Header Checksum (16b), Source Addr (32b), Dest Addr (32b), Options (variable).
- **Fragmentation**: a router splits a datagram larger than the outgoing link's MTU into fragments sharing the same Identification; reassembly happens **only at the final destination**. Offset is in 8-byte units → all fragments except the last must be multiples of 8 bytes.
- **Forcing constraint**: links have a finite **MTU** (Ethernet = 1500 bytes). A datagram larger than the path's smallest MTU must either fragment or be dropped. **DF set** → router drops + returns ICMP "fragmentation needed," the basis of **Path MTU Discovery**. Fragmentation is fragile (loss of one fragment kills the whole datagram; offset/ID fields enable attacks), which is *why* TCP avoids it via MSS negotiation instead.

### TCP header fields & flags — Stevens Ch 17 (TCP intro), Ch 18
- **TCP header**: 20 bytes minimum. Fields: Source Port (16b), Dest Port (16b), Sequence Number (32b), Acknowledgment Number (32b), Data Offset/header-length (4b), Reserved, **Flags** (CWR, ECE, URG, **ACK**, PSH, **RST**, **SYN**, **FIN**), Window Size (16b), Checksum (16b), Urgent Pointer (16b), Options (variable, up to 40 bytes).
- **Forcing constraint**: the 16-bit **Window Size** field hard-caps the un-scaled receive window at 65 535 bytes — the reason window scaling (below) had to be bolted on as an option.

### 3-way handshake & teardown at the packet level — Stevens Ch 18; HPBN "Building Blocks of TCP"
- **Open (3 segments)**: (1) Client → `SYN`, seq=x. (2) Server → `SYN,ACK`, seq=y, ack=x+1. (3) Client → `ACK`, ack=y+1. Data may piggyback on segment 3; SYN/FIN each consume one sequence number.
- **Cost**: a **full round trip of latency before any application byte flows**. HPBN: NY↔London handshake ≥ **56 ms** (28 ms each way).
- **Teardown (4 segments, "half-close")**: each direction sends its own `FIN`, acknowledged separately: `FIN` → `ACK`, `FIN` → `ACK`. Active closer enters **TIME_WAIT** (2×MSL) to absorb stray retransmissions.
- **Forcing constraint**: reliability over an unreliable IP layer requires both sides to synchronize **independent, random initial sequence numbers** before data — and you cannot do that in less than one RTT. This RTT tax is the root cost that TLS False Start, TCP Fast Open, and QUIC's 0-RTT all attack.

### MSS, window scaling, SACK, timestamps (TCP options) — Stevens Ch 18, Ch 24
- **MSS** (Maximum Segment Size): advertised in the SYN; each side states the largest segment it will accept. Tuned to MTU − 40 (=1460 on Ethernet) to **avoid IP fragmentation**. Forcing constraint: keep TCP segments ≤ path MTU.
- **Window scaling** (RFC 1323/7323): a SYN-only option giving a left-shift (0–14) of the 16-bit window → max receive window from 65 535 B up to **~1 GB**. Forcing constraint: on high **bandwidth-delay-product** paths, 64 KB caps throughput far below link capacity (HPBN: 16 KB window over 100 ms RTT ≈ **1.31 Mbps** ceiling regardless of bandwidth).
- **SACK** (Selective ACK, RFC 2018): lets the receiver name non-contiguous received blocks so the sender retransmits only the gaps, not everything after the loss. Forcing constraint: cumulative ACKs alone force wasteful retransmission on multi-loss.
- **Timestamps** (RFC 1323/7323): per-segment TSval/TSecr → accurate RTT sampling (RTTM) and **PAWS** (Protection Against Wrapped Sequence numbers) on fast links where the 32-bit seq space wraps quickly.

### Slow start & congestion-window dynamics — Stevens Ch 20; HPBN "Building Blocks of TCP"
- **cwnd** = sender-side limit on un-ACKed data in flight; actual in-flight = **min(cwnd, rwnd)**.
- **Slow start**: start small, **double cwnd every RTT** (exponential) until ssthresh or loss; then congestion avoidance (linear). Initial window **IW = 10 segments** per RFC 6928 (was 4 in RFC 2581, originally 1).
- **Math (HPBN)**: time to grow to N segments = `RTT × log₂(N / IW)`. Example: 56 ms RTT, IW=10 → reaching ~45 segments / 64 KB takes ~**168 ms** (3 round trips).
- **Forcing constraint**: a new sender has **no knowledge of available path capacity**; blasting at full rate would collapse shared links (congestion collapse, 1986). Slow start probes gently — *why* short connections (most web requests) finish before ever using available bandwidth, making them **RTT-bound, not bandwidth-bound**.

### TCP head-of-line blocking — HPBN "Building Blocks of TCP"
- TCP guarantees **in-order byte delivery**: one lost segment forces **all later segments to wait in the receiver's kernel buffer** until the gap is retransmitted (≥1 RTT stall). The app sees only delay, not the cause.
- **Forcing constraint**: the in-order-byte-stream abstraction itself. This is the defect HTTP/2 multiplexing *cannot* fix (it shares one TCP stream) and that pushed HTTP/3 to QUIC.

### TLS 1.3 handshake, 1-RTT, 0-RTT, resumption — RFC 8446 §2, §2.2, §2.3, §4.2.8; HPBN "TLS"
- **TLS 1.2 baseline (HPBN)**: full handshake = **2 RTT** on top of the TCP handshake (ClientHello → ServerHello/Certificate → key exchange → Finished). Resumption via **Session IDs** (RFC 5246, server-side state) or **Session Tickets** (RFC 5077, stateless) → **1 RTT** abbreviated handshake. **False Start** → ~1 RTT for new connections by sending app data right after the client's Finished.
- **TLS 1.3 (RFC 8446 §2)**: **1-RTT full handshake**. Client puts its ephemeral (EC)DHE **`key_share` in the ClientHello** (§4.2.8). Server replies ServerHello + EncryptedExtensions + Certificate + CertificateVerify + Finished — all after the first flight. *Everything after ServerHello is encrypted.*
- **0-RTT early data (§2.3)**: with a **PSK** from a prior session (§2.2), the client sends app data *in its first flight*, encrypted under a `client_early_traffic_secret` derived from the PSK.
- **Forcing constraint**: TLS 1.2 wasted a round trip because cipher/key params were negotiated *before* keys were exchanged. TLS 1.3 collapses this by speculatively sending key_share up front — *why* it saves exactly one RTT.

### HTTP/1.1 keep-alive & application-layer HOL blocking — HPBN "HTTP/1.x" & "HTTP/2"
- **Persistent connections** (keep-alive) reuse one TCP connection across requests, amortizing handshake + slow-start cost.
- **HOL blocking**: HTTP/1.x delivers **one response at a time per connection** (response queuing). **Pipelining** tried to fix this but failed in practice (broken proxies, no reliable error handling). Browsers worked around it with **~6 parallel connections per origin** + **domain sharding**.
- **Forcing constraint**: HTTP/1's strictly serialized request/response framing on a connection → the only way to get parallelism was more sockets.

### HTTP/2 multiplexing & HPACK — HPBN "HTTP/2"
- **Binary framing layer**: 9-byte frame header (24b length, 8b type, 8b flags, 1b reserved, 31b stream ID). Hierarchy: **stream → message → frame**.
- **Multiplexing**: interleave frames from many streams over **one TCP connection**, reassemble by stream ID → solves HTTP/1's *application-layer* HOL blocking. Removes need for sharding/sprites/concatenation.
- **Prioritization**: per-stream weight (1–256) + dependency tree (advisory, not enforced). **Flow control**: credit-based, per-stream + per-connection WINDOW_UPDATE, default 65 535 B, cannot be disabled. **Server push** via PUSH_PROMISE (now largely deprecated in practice).
- **HPACK**: static Huffman coding + shared static/dynamic indexed header tables → big header-overhead savings (SPDY data: 45–1142 ms PLT reduction on DSL).
- **Forcing constraint / residual flaw**: all streams ride **one TCP byte stream**, so TCP-layer HOL blocking remains — one lost packet stalls *all* HTTP/2 streams. This is the unsolved problem HTTP/3 targets.

### HTTP/3 over QUIC, and why it moved to UDP — RFC 9000 (QUIC), RFC 9001 (QUIC-TLS), RFC 9002 (loss/cc), RFC 9114 (HTTP/3)
- **QUIC = userspace transport over UDP** with TLS 1.3 baked into the handshake, **independent streams**, per-stream flow control, and its own loss recovery + congestion control (reimplements TCP-like reliability).
- **Kills transport HOL blocking**: each stream is an independent ordered byte sequence; a lost packet stalls **only the stream(s) whose bytes it carried**; other streams proceed.
- **Faster setup**: transport + crypto handshake combined → **1-RTT** new connections, **0-RTT** resumed (inherits TLS 1.3 risks). **Connection migration** via connection IDs (survives IP/port change, e.g. Wi-Fi→cellular).
- **Why UDP, not "fix TCP"**: (1) **TCP HOL blocking** is intrinsic to the in-order byte stream and unfixable without changing the transport contract; (2) **protocol ossification** — middleboxes inspect/rewrite cleartext TCP headers (a study found ~1/3 of paths have a TCP-metadata-modifying middlebox, 6.5% harmful), so new TCP options (Fast Open, MPTCP) won't deploy; QUIC encrypts almost the entire transport header so middleboxes can't ossify it; (3) **kernel deployment lag** — TCP lives in the OS kernel, so iteration is slow; QUIC in userspace ships with the app/browser.
- **Forcing constraint**: to get both independent-stream delivery *and* deployability on today's Internet, you must bypass the kernel TCP stack and ossified middleboxes — UDP is the only ubiquitously-passed substrate that allows a fully custom, encrypted transport.

### The latency budget breakdown — HPBN "Primer on Latency and Bandwidth"
Total one-way latency = **propagation + transmission + queuing + processing** delay.
- **Propagation**: distance ÷ signal speed. Light in fiber ≈ **2×10⁸ m/s** (refractive index ~1.5). NY↔SF 21 ms (42 ms RTT); NY↔London 28 ms (56 ms); NY↔Sydney 80 ms (160 ms).
- **Transmission**: packet bits ÷ link data rate.
- **Queuing**: time waiting in router buffers.
- **Processing**: header parse, checksum, routing decision.
- **Last-mile** (FCC, HPBN): fiber 10–20 ms, cable 15–40 ms, DSL 30–65 ms — often the dominant local term.
- **Human thresholds**: lag perceptible at **100–200 ms**, "sluggish" past ~300 ms.
- **Forcing constraint**: propagation is bounded below by the **speed of light** — an irreducible floor no engineering removes. This is the headline thesis: *"Latency, not bandwidth, is the performance bottleneck for most websites."*

---

## 2. Foundational sources — exact links (one canonical per claim)

**Grigorik, *High Performance Browser Networking* (O'Reilly, free, hpbn.co)**
- Latency budget / speed of light / bandwidth-vs-latency: https://hpbn.co/primer-on-latency-and-bandwidth/
- 3-way handshake, slow start, cwnd/rwnd, BDP, window scaling, TCP HOL, TFO: https://hpbn.co/building-blocks-of-tcp/
- TLS 1.2 handshake (2-RTT), session ID/ticket resumption, False Start, ALPN/SNI, chain of trust, TLS-1.3 1-RTT/0-RTT goal note: https://hpbn.co/transport-layer-security-tls/
- HTTP/2 binary framing, multiplexing, HPACK, prioritization, flow control, push; HTTP/1.x keep-alive/pipelining/HOL/sharding: https://hpbn.co/http2/

**W. Richard Stevens, *TCP/IP Illustrated, Vol 1: The Protocols*** (chapter refs; 1st ed. numbering)
- IP header, routing, fragmentation/MTU: **Ch 3 (IP: Internet Protocol)**
- TCP intro & header format: **Ch 17 (TCP: Transmission Control Protocol)**
- 3-way handshake, teardown/half-close, MSS, TIME_WAIT, state diagram, TCP options: **Ch 18 (TCP Connection Establishment and Termination)** — https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/0201633469/ch18.html
- Bulk data flow & **slow start**: **Ch 20 (TCP Bulk Data Flow)**
- Timeout/retransmission, RTT measurement (RTO), Karn's algorithm: **Ch 21 (TCP Timeout and Retransmission)** — https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/0201633469/ch21.html
- TCP futures/options (window scaling, timestamps, PAWS, long fat pipes): **Ch 24 (TCP Futures and Performance)**
- *(Note: 2nd ed. by Fall & Stevens renumbers — IP is Ch 5, TCP connection mgmt Ch 13; cite by title to be edition-safe.)* [UNVERIFIED — 2nd-ed exact numbers not re-checked]

**RFC 8446 — TLS 1.3** (https://www.rfc-editor.org/rfc/rfc8446)
- §2 handshake overview / 1-RTT flow; §2.2 resumption + PSK; §2.3 0-RTT early data + its weaker security; §4.2.8 `key_share`; §4.2.9 `psk_key_exchange_modes`; §8 + Appendix E.5 anti-replay.

**QUIC / HTTP/3** — RFC 9000 (QUIC transport, May 2021), RFC 9001 (using TLS with QUIC), RFC 9002 (loss detection + congestion control), RFC 9114 (HTTP/3, June 2022). Background: https://en.wikipedia.org/wiki/QUIC

**Supplementary RFCs (one-hop, for WHY):** RFC 1323/7323 (window scaling, timestamps, PAWS); RFC 2018 (SACK); RFC 6928 (IW10); RFC 5077 (session tickets); RFC 6298 (RTO computation).

---

## 3. "Why it's this way" — forcing constraints

- **Speed of light ⇒ propagation latency floor.** Signal in fiber ≈ 2×10⁸ m/s; NY↔London RTT can't drop below ~56 ms no matter the bandwidth. *Every* round-trip-bound cost (handshakes, slow start) inherits this irreducible tax — the reason the field obsesses over *eliminating round trips*, not adding Mbps.
- **Why slow start.** A new TCP sender has zero information about path capacity and shares links with everyone else. After the 1986 congestion-collapse episodes, senders must probe gently (exponential-from-small) to avoid overwhelming buffers. Consequence: short transfers finish during the probe and never touch full bandwidth → **RTT-bound**.
- **Why TCP HOL blocking forced HTTP/3 → QUIC/UDP.** TCP's contract is a single in-order byte stream; one lost segment blocks delivery of everything behind it. HTTP/2 multiplexes *above* that single stream, so the stall hits all streams. You cannot fix this without giving the transport stream-awareness — and you cannot deploy a new in-kernel transport past ossified middleboxes. UDP + userspace QUIC is the escape hatch: independent streams, encrypted headers (un-ossifiable), app-shipped (fast iteration).
- **Why TLS 1.3 cut a round trip.** TLS 1.2 negotiated the cipher suite *first*, then exchanged keys — two sequential dependencies = 2 RTT. TLS 1.3 has the client **guess** and send its ephemeral DH `key_share` in the very first ClientHello, so the server can derive keys and finish in one RTT. Resumption via PSK enables 0-RTT by reusing prior secrets.

---

## 4. Common misconceptions to preempt

- **"Bandwidth = speed / latency."** They're orthogonal. Bandwidth = throughput (bits/sec); latency = delay (one packet's travel time). HPBN's thesis: latency dominates most web loads.
- **"More bandwidth fixes slow pages."** For RTT-bound loads (many small objects, handshakes, slow start) extra Mbps barely helps — past ~5 Mbps, page load time flattens; cutting RTT helps almost linearly. Doubling bandwidth ≠ halving load time; halving RTT ~ halves it.
- **"HTTP/2 eliminated head-of-line blocking."** Only at the *application* layer. **TCP-layer HOL blocking persists** — one lost TCP segment stalls every HTTP/2 stream on that connection. Only HTTP/3/QUIC removes it (per-stream loss recovery).
- **"More TCP connections = always faster."** Each connection pays its own handshake + independent slow start and competes for the same congestion control; HTTP/2 deliberately collapses to **one connection per origin** to share congestion state and cut handshakes. Domain sharding can *hurt* under HTTP/2.
- **"0-RTT is free speed, just turn it on."** 0-RTT early data has **weaker security** (RFC 8446 §2.3): **no forward secrecy** (encrypted only under the PSK) and **replayable** (no ServerHello-Random freshness). Safe only for idempotent requests; never for state-changing operations without app-level anti-replay.
- **"TLS is expensive / slow."** Modern symmetric crypto + AES-NI: Google reports TLS ≈ <1% CPU, <10 KB RAM/conn, <2% network overhead (HPBN, Langley). Public-key cost is one-time at setup; resumption avoids even that.
- **"Fragmentation is normal for TCP."** TCP actively avoids it via MSS = MTU−40 and Path MTU Discovery; IP fragmentation is fragile and mostly an IP/UDP-era concern.

---

## 5. Best build-your-own target(s)

- **Primary (beginner→intermediate): packet inspection.** Capture and dissect a real session with `tcpdump`/Wireshark:
  - `tcpdump -n -S 'tcp port 443'` to watch the **SYN / SYN-ACK / ACK** with raw sequence numbers, then **FIN/ACK** teardown and TIME_WAIT.
  - Inspect SYN **options** in Wireshark: MSS, window scale, SACK-permitted, timestamps.
  - Watch the **TLS 1.3 handshake** (ClientHello with key_share/SNI/ALPN → ServerHello → encrypted rest) and compare a fresh handshake vs. a resumed (PSK) one — count the round trips.
  - Compare HTTP/1.1 vs HTTP/2 in DevTools (waterfall, single connection, multiplexing); force HTTP/3 and observe UDP.
- **Stretch: a from-scratch TCP/IP or HTTP exercise.** A raw-socket "send a SYN and parse the SYN-ACK" exercise, or a minimal HTTP/1.1 client over a TCP socket, makes the headers concrete.
- **Advanced — scope carefully: minimal TLS client.** A real TLS 1.3 handshake (X25519 key_share, HKDF key schedule, AEAD records, certificate verification) is a large, security-sensitive build. **Recommend: read & annotate an existing handshake (Wireshark + RFC 8446) rather than implement crypto** at this course level; flag full TLS implementation as out-of-scope / optional capstone only.

---

## 6. Open questions / where sources disagree / dated numbers

- **HPBN is pre-QUIC/HTTP-3 for the deep dives.** The TLS chapter explicitly does **not** cover QUIC/HTTP-3 and only notes TLS 1.3's 1-RTT/0-RTT as a *future goal*. All HTTP/3 + QUIC material here comes from RFC 9000/9001/9002/9114 + Wikipedia + measurement papers, **not** Stevens or HPBN. **Gap:** no single primary source in the named cluster covers HTTP/3 — supplement needed.
- **QUIC CPU cost is genuinely contested.** Measurements report QUIC using **~2×–4× the CPU of TLS/TCP** for large transfers, with **70–80% of cost in per-packet `sendmsg/recvmsg` syscalls** (userspace transport); **UDP GSO/GRO** narrows the gap substantially (one study: GSO coalescing → +45% throughput; GSO+GRO cut IO cost 60.7%→21.3%). Net: the "QUIC is slower" claim is **workload- and tuning-dependent**, not absolute. [partially UNVERIFIED — figures from vendor blogs/arXiv, not yet cross-checked against a single canonical source]
- **HTTP/3 adoption maturity is a moving target.** ~9% of websites used QUIC as of early 2023 (Wikipedia, dated); supported by all major browsers + major CDNs, but server-side library maturity and middlebox UDP-throttling remain real caveats. **Verify current adoption numbers before teaching as fact** (this brief's figures are 2021–2023 vintage).
- **Stevens edition/chapter numbering.** 1st ed (1994, Stevens) vs 2nd ed (2011, Fall & Stevens) renumber chapters; IW default, ECN, and modern congestion-control variants (CUBIC, BBR) are **not** in the 1st edition. Cite Stevens **by chapter title**; pull IW10, modern CC, and SACK/timestamps current behavior from RFCs/HPBN, not 1994 Stevens. [Ch-number mapping for 2nd ed UNVERIFIED]
- **Server push (HTTP/2)** is described as a feature in HPBN but has since been **deprecated/removed by Chrome** — teach it as historical, not current best practice. [date-sensitive]
- **Slow-start example numbers in HPBN** assume IW10 and specific RTTs; they're illustrative, not universal — initial window, ssthresh, and CC algorithm vary by OS/stack.

---

### Summary (read first)
The cluster cleanly splits: **Stevens = the bytes on the wire** (IP/TCP header fields, fragmentation/MTU, the SYN/SYN-ACK/ACK handshake and FIN teardown, retransmission/RTO, the MSS/window-scaling/SACK/timestamps options), and **HPBN = why those bytes cost what they cost** (the latency budget, the speed-of-light propagation floor, the handshake + slow-start round-trip tax, TCP HOL blocking, TLS resumption, HTTP/1→2 multiplexing). The through-line for the whole sub-course is **"eliminate round trips, because the speed of light fixes the floor"**: it explains slow start, keep-alive, TLS False Start/1.3, HTTP/2 single-connection multiplexing, and HTTP/3. **TLS 1.3 1-RTT/0-RTT and its replay/forward-secrecy caveats are confirmed against RFC 8446 §2.3.** The one structural gap is **HTTP/3/QUIC**: neither Stevens nor the HPBN chapters read here cover it, so it's sourced from RFC 9000/9114 + measurement literature and must be supplemented. Strongest hands-on target is **tcpdump/Wireshark packet inspection**; a full minimal-TLS client is real but should be optional/out-of-scope.

**Distinct primary sources w/ links: 8 core** — (1) HPBN Latency primer, (2) HPBN Building Blocks of TCP, (3) HPBN TLS, (4) HPBN HTTP/2 — all hpbn.co; (5) Stevens TCP/IP Illustrated Vol 1 (Ch 3/17/18/20/21/24); (6) RFC 8446 (TLS 1.3); (7) RFC 9000 (QUIC) + siblings 9001/9002; (8) RFC 9114 (HTTP/3). Plus supplementary RFCs (1323/7323, 2018, 6928, 5077, 6298).

**Gaps / [UNVERIFIED] flags:** HTTP/3+QUIC absent from the named cluster (supplement required); QUIC CPU-cost figures (2×–4×) from vendor/arXiv not single-source-canonical; Stevens 2nd-ed chapter numbers not re-verified; HTTP/3 adoption % and HTTP/2 server-push status are date-sensitive — re-check before teaching.
