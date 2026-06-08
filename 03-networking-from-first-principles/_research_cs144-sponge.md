# 03 — Research brief: Stanford CS144 + TCP labs (Sponge/Minnow)

> Scope: the CS144 lab ladder where students hand-build a working TCP from the
> byte-stream abstraction up, plus the consolidated TCP spec (RFC 9293) and the
> RTO algorithm (RFC 6298) the labs simplify. Primary sources read in full:
> CS144 check1/check2/check3 lab PDFs (Fall 2025, Minnow), RFC 9293, RFC 6298.
> All algorithm details below are quoted/paraphrased from those primaries.

---

## SUMMARY (orientation)

CS144 ("Introduction to Computer Networking", Stanford) pairs lectures with a
lab ladder in which students implement TCP in modern C++, one testable module at
a time, against an unreliable datagram network. The current framework is
**Minnow** (a rewrite of the older **Sponge**); the lab progression is:
**ByteStream (check0) → Reassembler (check1) → TCPReceiver (check2) →
TCPSender + retransmission timer (check3)**, after which provided framework code
(`TCPPeer` / `TCPMinnowSocket`) wires the sender+receiver into a real TCP peer
that interoperates with Linux's kernel TCP and real Internet servers. The pivot
of the whole course is representing each byte's place in the stream three ways —
**stream index** (0-based, no SYN/FIN), **absolute seqno** (0-based, includes
SYN/FIN), and **seqno** (32-bit, wraps, offset by a random ISN) — and converting
among them (`Wrap32::wrap`/`unwrap`). The receiver turns segments into an
in-order byte stream and advertises an **ackno** (next byte needed) + **window
size** (flow control); the sender fills that window, tracks outstanding
segments, and retransmits on a timer with **exponential backoff**. The "why" is
forced from below: IP delivers best-effort datagrams that can be lost,
reordered, duplicated, or altered, so reliable in-order byte streams must be
synthesized via sequence numbers, cumulative ACKs, a sliding window, and timers.

---

## 1. KEY MECHANISMS (deep & precise; each with its forcing constraint)

### 1a. Byte-stream abstraction over packets (ByteStream)
A finite, flow-controlled in-memory FIFO with a fixed `capacity`. Writer pushes
bytes in; Reader pulls bytes out; can convey a stream of arbitrary length even
with tiny capacity. Two of these are conveyed across the network per connection:
an *outbound* stream (local app → peer) and an *inbound* stream (peer → local
app). [check1 §0; check2 §0]
- **Forcing constraint:** applications want an ordered, reliable, infinite byte
  pipe; the network only offers bounded, lossy packets. Capacity bounds memory
  so the abstraction works regardless of how data arrives.

### 1b. Stream reassembly using sequence/stream indices (Reassembler)
`insert(first_index, data, is_last_substring)` accepts substrings each tagged
with the **stream index** of their first byte (every byte has a unique index
starting at 0). The Reassembler has exactly three categories of knowledge:
(1) bytes that are the *next* bytes in the stream → push to `output.writer()`
**as soon as known**; (2) bytes that fit within available capacity but can't yet
be written because earlier bytes are unknown → buffer internally; (3) bytes
beyond available capacity → **discard**. Substrings **may overlap** and may
arrive in any order; the reassembler must **not** store overlapping/redundant
bytes twice (only one copy per index), so that `capacity` remains a true memory
bound. `capacity` upper-bounds *both* bytes buffered in the reassembled
ByteStream *and* bytes held as unassembled substrings. `is_last_substring`
marks where the stream ends (→ ByteStream EOF). [check1 §3, §3.1, §3.2 FAQs]
- **Forcing constraint:** datagrams arrive out of order / duplicated, so the
  receiver must stitch arbitrary index-tagged slices back into one stream while
  capping memory — robustness against reordering/duplication is the whole point.

### 1c. Three indexing spaces + Wrap32 (the conceptual crux)
TCP headers carry a **32-bit seqno**, not a 64-bit index, introducing three
complications and three index spaces [check2 §2.1]:
| Space | Starts at | Includes SYN/FIN | Width | Wraps? |
|---|---|---|---|---|
| seqno | ISN (random) | yes | 32-bit | yes (mod 2³²) |
| absolute seqno | 0 | yes | 64-bit | no |
| stream index | 0 | no | 64-bit | no |
- absolute seqno ↔ stream index: just ±1 (the SYN's seqno occupies absolute 0).
- seqno ↔ absolute seqno: `Wrap32::wrap(n, zero_point)` (absolute→seqno, ~1
  line) and `unwrap(zero_point, checkpoint)` (seqno→absolute, <10 lines). Unwrap
  needs a **checkpoint** because a 32-bit seqno maps to infinitely many absolute
  seqnos (17, 2³²+17, 2³³+17, …); pick the absolute seqno **closest to the
  checkpoint**. In the receiver the checkpoint is the first unassembled index.
  Wrap/unwrap **preserve offsets**: two seqnos differing by 17 map to absolute
  seqnos differing by 17. [check2 §2.1]
- **Forcing constraint:** header space is precious (32 bits = only 4 GiB before
  wrap; ~⅓ sec at 100 Gb/s) and ISNs are randomized, so the implementation must
  reconcile a wrapping, randomly-offset header field with an unbounded stream.

### 1d. SYN/FIN consume sequence numbers (logical begin/end)
SYN (beginning-of-stream) and FIN (end-of-stream) are **control flags that each
occupy exactly one sequence number**; they are *not* bytes in the stream.
The SYN's seqno *is* the ISN. `TCPSenderMessage::sequence_length() =
SYN + payload.size() + FIN`. [check2 §2.1; sender message struct]
- **Forcing constraint:** the start and end of the stream must be delivered
  reliably too, so they need positions in sequence space that can be ACKed/lost
  /retransmitted like data.

### 1e. Receiver: ackno + advertised window (cumulative ACK & flow control)
`TCPReceiver::receive(TCPSenderMessage)` sets the ISN on the first SYN-bearing
segment, unwraps seqnos to stream indices, and pushes payload (and FIN→EOF) into
the Reassembler. `send()` returns a `TCPReceiverMessage { optional<Wrap32>
ackno; uint16_t window_size; bool RST }`:
- **ackno** = the **next** seqno the receiver needs = first unassembled index
  (mapped back to a seqno). It is **empty/optional until the ISN is known**.
  This is the "left edge" of the receiver's window. (Cumulative: ackno X means
  all octets up to but **not including** X have been received and reassembled.)
- **window_size** = available capacity in the output ByteStream, max
  **65,535** (`UINT16_MAX`). `ackno + window_size` = right edge.
[check2 §2, §2.2, §2.2.1; receiver message struct]
- **Forcing constraint:** the sender must learn what to (re)send next and how
  much the receiver can absorb; one cumulative ackno + one window does both with
  minimal header state.

### 1f. Sender: fill the window, track outstanding, retransmit (ARQ)
`TCPSender` responsibilities [check3 §2]: track the receiver's window
(ackno + window size from `receive`); **fill** the window from the outbound
ByteStream (`push(transmit)`) emitting segments each ≤ `MAX_PAYLOAD_SIZE` and
fitting fully inside the window, adding SYN at stream start and FIN at end;
track **outstanding** (sent-but-unACKed, data-bearing) segments; retransmit on
timeout. Detailed rules:
- **Initial window assumption:** before any `receive`, assume window size **1**.
- **Zero-window probe:** if advertised window is 0, `push` **pretends it is 1**
  (sends one byte) to provoke a fresh ACK that may reopen the window — otherwise
  the sender would never learn it may resume. This pretend-1 lives *only* inside
  `push`; the sender must not store a false window of 1. A "full" window ≠ a
  "zero" window. [check3 §2.2]
- **Outstanding tracking:** only segments occupying ≥1 seqno (SYN/payload/FIN)
  are tracked/retransmitted; empty (zero-length) segments are never tracked.
  Partial ACKs are not clipped — a segment stays fully outstanding until the
  ackno exceeds **all** its seqnos. [check3 §2.2, §2.3 FAQs]
- **`make_empty_message()`**: zero-length segment with correct seqno, used to
  carry a bare ACK; never tracked as outstanding.
- **Forcing constraint:** the receiver can rebuild the stream as long as each
  index-tagged byte arrives *at least once* in *any* order, so the sender's only
  job is "send what the window allows, keep resending until ACKed" (ARQ).

### 1g. Retransmission timer, RTO, exponential backoff (check3 §2.1)
The only clock is `tick(ms_since_last_tick, transmit)` — **no OS/wall-clock
calls** (keeps it deterministic/testable). Exact rules:
1. Constructor gets `initial_RTO_ms`; current RTO varies but the initial value
   is fixed.
2. When a **data-bearing** segment is sent (first time *or* retransmit), if the
   timer isn't running, start it to expire after the **current** RTO.
3. When **all** outstanding data is ACKed, **stop** the timer.
4. On `tick` if the timer **expired**:
   (a) retransmit the **earliest** (lowest-seqno) unACKed segment;
   (b) **if window size is nonzero**: (i) increment the consecutive-retransmit
       count (used by the connection layer to give up); (ii) **double RTO**
       (exponential backoff — slows retransmits on lossy networks);
   (c) reset/restart the timer for (the possibly doubled) RTO.
5. On a **new** ackno (absolute seqno larger than any prior ackno): (a) reset
   RTO to its initial value; (b) if data still outstanding, restart the timer;
   (c) reset the consecutive-retransmit count to 0.
   *(Note: when window==0, backoff is intentionally skipped so zero-window probes
   don't blow up RTO.)*
- **CS144 simplifies RFC 6298** (check3 footnote): it implements recs 5.1–5.6
  (fixed initial RTO, backoff, timer start/stop) but **omits adaptive RTO
  estimation** — no SRTT/RTTVAR sampling. The "real" algorithm (for context,
  not implemented in the lab) is RFC 6298: initial RTO 1 s; on first sample R,
  `SRTT=R`, `RTTVAR=R/2`; thereafter `RTTVAR=(1−β)·RTTVAR+β·|SRTT−R'|`,
  `SRTT=(1−α)·SRTT+α·R'` with **α=1/8, β=1/4**; `RTO=SRTT+max(G, K·RTTVAR)`,
  **K=4**; min RTO 1 s; backoff `RTO=RTO×2`; max RTO ≥60 s. [RFC 6298 §2.1–2.5,
  §5.5]
- **Forcing constraint:** must detect loss "in a timely manner" without wasting
  network capacity on premature resends; backoff prevents congestive collapse on
  bad links.

### 1h. Three-way handshake & ISN (RFC 9293 §3.4.1)
SYN(seq=X) → SYN+ACK(seq=Y, ack=X+1) → ACK(ack=Y+1). The handshake exchanges and
confirms both ISNs. ISN is **clock-driven** (a counter incrementing ~every 4 µs,
MUST-8) and SHOULD be randomized as `ISN = M + F(localIP,localPort,remoteIP,
remotePort,secretkey)` (SHLD-1). [RFC 9293 §3.4.1; Fig 6]

### 1i. Connection teardown & TIME-WAIT (RFC 9293 §3.5–3.6)
Each direction's FIN is ACKed independently (half-close allowed). The **active
closer** lingers in **TIME-WAIT for 2×MSL** before CLOSED (MUST-13); MSL is
taken to be **2 minutes** (so TIME-WAIT ≈ 4 min). [RFC 9293 §3.4.2, §3.6.1]
In CS144 this manifests as the `tcp_ipv4` peer "lingering" after both streams
finish to avoid the two-generals problem. [check3 §4.1]

### 1j. Full TCP state machine (RFC 9293 §3.3.2, Fig 5)
Eleven states: **CLOSED, LISTEN, SYN-SENT, SYN-RECEIVED, ESTABLISHED,
FIN-WAIT-1, FIN-WAIT-2, CLOSE-WAIT, CLOSING, LAST-ACK, TIME-WAIT**. Window state
variables: `RCV.NXT` (left edge / next expected), `RCV.WND` (size);
`SND.UNA` (oldest unACKed) < valid `SEG.ACK` ≤ `SND.NXT`. [RFC 9293 §3.3.1]
In the **old Sponge** framework this was a hand-written `TCPConnection` lab
("Lab 4: the summit / TCP in full") with `linger_after_streams_finish` and clean
shutdown; **Minnow** instead provides the peer wiring (`TCPPeer`) so students do
not hand-author the full state machine (see §6).
- **Forcing constraint:** establishment, bidirectional independent teardown, and
  drain-the-network safety each need distinct states with distinct transitions.

---

## 2. FOUNDATIONAL SOURCES (one canonical link per claim)

CS144 course site & labs (Fall 2025, Minnow framework; mirror at
cs144.keithw.org has a cert-name mismatch — use github.io):
- Course site / assignment index: https://cs144.github.io/ (lists check0–check7,
  lecture topics; PDFs also at cs144.keithw.org/assignments/checkN.pdf).
- **check1 — ByteStream + Reassembler:**
  https://cs144.github.io/assignments/check1.pdf  (§3 reassembler interface,
  §3.1 three knowledge categories, §3.2 overlap/capacity FAQs).
- **check2 — TCPReceiver:** https://cs144.github.io/assignments/check2.pdf
  (§2.1 three index spaces + Wrap32 wrap/unwrap; §2.2 ackno + window; message
  structs `TCPSenderMessage`/`TCPReceiverMessage`).
- **check3 — TCPSender + retransmission:**
  https://cs144.github.io/assignments/check3.pdf  (§2.1 timer/RTO/backoff rules
  1–7; §2.2 fill_window + zero-window probe; §2.3 outstanding-segment FAQs; §4
  hands-on interop with Linux TCP / one-megabyte challenge).
- check0 — networking warmup (webget + in-memory ByteStream):
  https://cs144.github.io/assignments/check0.pdf
- Lab FAQ: https://cs144.github.io/lab_faq.html
- Minnow repo (current framework): https://github.com/CS144/minnow
- Doxygen for receiver/sender/state (Sponge-era, still illustrative):
  https://cs144.github.io/doc/lab2/class_t_c_p_receiver.html

RFCs (specification & "why"):
- **RFC 9293** (TCP, consolidated; supersedes RFC 793):
  https://www.rfc-editor.org/rfc/rfc9293.html — §3.3.1 (window vars),
  §3.3.2/Fig 5 (state machine), §3.4 (cumulative ACK semantics), §3.4.1
  (three-way handshake + ISN/clock + randomization rationale), §3.4.2 (MSL=2
  min, quiet time), §3.6.1 (TIME-WAIT 2×MSL, MUST-13), §3.8 (retransmission).
- **RFC 6298** (Computing TCP's RTO): https://www.rfc-editor.org/rfc/rfc6298 —
  §2.1 (initial RTO 1 s), §2.2–2.3 (SRTT/RTTVAR, α=1/8 β=1/4 K=4), §2.4 (min
  1 s), §2.5 (max ≥60 s), §5.5 (backoff ×2). *(CS144 implements a simplified
  subset; full estimator is out of lab scope.)*
- Cited one hop for "why" inside the labs: RFC 791 (IP datagram, check1 §2.1),
  RFC 768 (UDP, check1 §2.2) — used in the hands-on raw-datagram exercises.

**Distinct primary sources: 9** — (1) cs144.github.io course index, (2) check0,
(3) check1, (4) check2, (5) check3 PDFs, (6) CS144 lab FAQ, (7) Minnow repo,
(8) RFC 9293, (9) RFC 6298. (Plus secondary: RFC 791, RFC 768 referenced by the
labs.)

---

## 3. "WHY IT'S THIS WAY" (forcing constraints, traced to a source)

- **Unreliable IP below ⇒ seq/ack/retransmit/window exist at all.** IP delivers
  best-effort datagrams that can be "lost, reordered, altered, or duplicated"
  [check1 §0]. Reliability is a *constructed* service: sequence numbers give
  every byte a position so duplicates/reorders are harmless; cumulative ACKs
  tell the sender what's missing; a timer + retransmit recover losses; a window
  bounds in-flight data. The receiver only needs each byte *at least once, in
  any order* [check3 §2].
- **Why a window for flow control.** The receiver's buffer is finite; the
  advertised window (= available ByteStream capacity, ≤65535) caps how much the
  sender may have in flight so a fast sender can't overrun a slow receiver
  [check2 §2; RFC 9293 §3.3.1]. (Distinct from congestion control — see §6.)
- **Why ISN randomization.** A fixed/zero ISN lets old duplicate segments from a
  previous incarnation of the same 4-tuple be mistaken for current data, and
  lets off-path attackers predict seqnos to inject/spoof. Clock-driven +
  hashed-secret ISN makes seqnos unguessable and unlikely to repeat [check2
  §2.1 reason 2; RFC 9293 §3.4.1, SHLD-1].
- **Why TIME-WAIT = 2×MSL.** A segment can live up to one MSL in the network;
  the active closer waits 2×MSL so that (a) its final ACK can reach the peer and
  (b) any straggling duplicate segments from this connection fully drain before
  the 4-tuple is reused — otherwise a new connection could accept stale data.
  MSL = 2 min ⇒ TIME-WAIT ≈ 4 min [RFC 9293 §3.4.2 "quiet time", §3.6.1
  MUST-13]. CS144's peer "lingers" for exactly this two-generals reason
  [check3 §4.1].
- **Why exponential backoff.** Retransmitting aggressively on a lossy/congested
  path "gums up the works"; doubling RTO each timeout slows resends to avoid
  congestive collapse [check3 §2.1 rule 6(b)ii; RFC 6298 §5.5].
- **Why SYN/FIN occupy seqnos.** Stream start/end must be delivered as reliably
  as data, so they need ACKable/retransmittable positions in sequence space
  [check2 §2.1 reason 3].
- **Why capacity bounds both buffered and unassembled bytes.** So memory stays
  bounded no matter the arrival pattern, and storing overlapping copies is
  forbidden because it would break that bound [check1 §3.1, §3.2].

---

## 4. COMMON MISCONCEPTIONS TO PREEMPT

- **"A TCP connection is a thing on the wire."** No — IP is stateless datagrams.
  A "connection" is purely an abstraction synthesized at the two endpoints from
  seqnos, ACKs, windows, timers, and a state machine [check1 §0; RFC 9293 §3.3].
- **"ACK n means segment n was received."** No — cumulative ACK: ackno = the
  **next** byte needed; "ack X" means *all* octets *up to but not including* X
  arrived and were reassembled in order. A single ACK can acknowledge many
  segments; gaps past the ackno aren't conveyed by the basic ackno [check2 §2.2;
  RFC 9293 §3.4].
- **"SYN/FIN are bytes in the stream."** No — they are control flags occupying
  one seqno each; they are *not* part of the byte stream and don't appear in the
  stream index [check2 §2.1].
- **"seqno == stream index."** No — three distinct spaces; seqno wraps at 2³² and
  is offset by a random ISN; conversions need `Wrap32` + a checkpoint to
  disambiguate [check2 §2.1].
- **"Zero window means the sender stops forever."** No — the sender sends a
  one-byte probe (treating window as 1) to elicit a fresh window advertisement
  [check3 §2.2].
- **"Flow control and congestion control are the same."** No — the advertised
  window is *receiver* buffer protection (flow control); congestion control
  (cwnd, AIMD, slow start) reacts to *network* state and is a separate mechanism
  largely outside the labs [check2 §2; see §6].
- **Head-of-line blocking.** Because TCP delivers a single in-order byte stream,
  one lost segment stalls delivery of all *later, already-arrived* bytes until
  the gap is filled — visible directly in the Reassembler (bytes in category 2
  wait behind an unknown earlier byte) [check1 §3.1]. [Framing note: the term
  "head-of-line blocking" is standard networking vocabulary; it is the behavior
  the Reassembler's category-2 buffering exhibits — UNVERIFIED that CS144 PDFs
  use the exact phrase.]

---

## 5. BEST BUILD-YOUR-OWN TARGET(S): the CS144 lab ladder

This *is* the canonical "build your own TCP/IP" lab. Recommended own-TCP ladder
mirrors CS144 Minnow, each rung independently unit-tested
(`cmake --build build --target checkN`):

1. **ByteStream (check0)** — finite, flow-controlled byte FIFO with capacity;
   Reader/Writer halves. Foundation for both stream directions.
2. **Reassembler (check1)** — `insert(first_index, data, is_last_substring)`;
   push contiguous bytes immediately, buffer in-capacity gaps, discard
   beyond-capacity, dedupe overlaps, signal EOF. Benchmark ≥0.1 Gb/s.
3. **Wrap32 + TCPReceiver (check2)** — implement `wrap`/`unwrap` (offset-
   preserving, checkpoint-disambiguated), set ISN on first SYN, drive the
   Reassembler, emit `{ackno, window_size}`.
4. **TCPSender + retransmission timer (check3)** — fill window, SYN/FIN, track
   outstanding, zero-window probe, timer with start/stop/backoff per rules 1–7;
   `make_empty_message` for bare ACKs.
5. **Integration / interop** — provided `TCPPeer`/`tcp_ipv4` glues sender+
   receiver into a real peer; validate by talking to **Linux's kernel TCP**
   (`tcp_native`) and a lab partner, and by the **one-megabyte challenge**
   (SHA-256-match a 10⁶-byte transfer). Then rewire `webget` onto your own stack
   (`CS144TCPSocket`) and fetch from a real webserver. [check3 §4]
6. **(Optional, down the stack)** check5 network interface (ARP), check6 IP
   router, check7 "make an Internet" — extends the lab to links/IP so the full
   "links→IP→TCP" story is hands-on. [course index]

Pedagogical strengths: strict module boundaries with unit tests at each rung;
the same code interoperates with *real* TCP (a strong correctness signal);
deterministic time via `tick` (no wall clock) makes retransmission testable.

---

## 6. OPEN QUESTIONS / WHERE SOURCES DISAGREE

- **Sponge vs Minnow (naming + scope drift).** The original framework was
  **Sponge** (`libsponge`, classes `StreamReassembler`, `TCPReceiver`,
  `TCPSender`, and a hand-written **`TCPConnection`** state-machine lab — "Lab 4:
  the summit / TCP in full," with `linger_after_streams_finish` and clean
  shutdown). The current framework is **Minnow** (rewrite; `Reassembler` dropped
  the `Stream` prefix; same receiver/sender ladder). **Key difference for a
  course:** Minnow's **check4 is "Measuring the real world"**, not a hand-written
  TCPConnection — Minnow *provides* the peer wiring (`TCPPeer`/`TCPMinnowSocket`,
  background-thread networking) so students no longer author the full 11-state
  machine by hand. If the course wants students to implement the **state machine
  + teardown** themselves, the **Sponge Lab 4** spec is the model; if it wants
  modern, interoperable, well-tested modules, use **Minnow check0–3**. [check1–3
  reference "the Minnow library" explicitly; Sponge Lab 4 / TCPConnection is
  attested via the Sponge doxygen + archived "the summit" handout — exact
  current Sponge-Lab-4 PDF not re-fetched here → **[UNVERIFIED]** beyond
  secondary corroboration.]
- **Congestion control is largely OUT OF SCOPE of the labs.** The labs implement
  *flow control* (receiver advertised window) and ARQ retransmission with
  backoff, but **not** congestion control (cwnd, slow start, AIMD, Reno/CUBIC) —
  that is lecture material (course "Week 4: congestion control") and not part of
  the TCPSender students build. Worth stating explicitly so learners don't
  conflate the advertised window with cwnd. [check2/check3 contain no cwnd;
  course index Week 4 lectures cover it.]
- **RTO estimation simplified.** CS144 deliberately uses a **fixed initial RTO +
  doubling backoff** and omits RFC 6298's adaptive SRTT/RTTVAR estimator
  (check3 footnote cites RFC 6298 recs 5.1–5.6 only). A faithful "own TCP" could
  add the estimator; the lab's simplification still interoperates with real
  servers. [check3 §2.1 footnote 2 vs RFC 6298 §2]
- **Minnow README not retrievable** via WebFetch/raw/GitHub API (404 at
  `main/README.md` — likely a non-`main` default branch or moved file) → the
  explicit "Minnow is a rewrite of Sponge" wording is corroborated by the lab
  PDFs ("the same Minnow library") and community sources but the **repo README
  statement itself is [UNVERIFIED]**.
- **cs144.keithw.org cert mismatch** (`ERR_TLS_CERT_ALTNAME_INVALID`): the
  primary PDFs are reliably reachable via `cs144.github.io/assignments/checkN.pdf`
  (same content); note this if linking the keithw mirror.

---

### GAPS / [UNVERIFIED] flags (consolidated)
1. Current **Sponge Lab 4 / TCPConnection** PDF not directly re-fetched; state-
   machine details cross-checked against RFC 9293 + Sponge doxygen/community,
   not the original handout text. [UNVERIFIED at handout level]
2. **Minnow repo README** "rewrite of Sponge" statement not retrievable (404).
   [UNVERIFIED at repo level; corroborated indirectly]
3. Whether CS144 PDFs use the literal phrase **"head-of-line blocking"** — the
   *behavior* is in check1 §3.1; the term is standard but not quote-verified.
4. check5/6/7 (network interface, router, "make an Internet") summarized from
   the course index, not full-PDF-read (outside the TCP core of this cluster).
