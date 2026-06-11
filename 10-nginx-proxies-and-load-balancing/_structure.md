# 10 — NGINX, Proxies, and Load Balancing · _structure.md

**Identity:** how one box fronts many backends — reverse proxying, load balancing, and the
event-driven architecture that makes serving tens of thousands of connections on a handful
of workers possible. Where 03's sockets+epoll grow up into a production server.

**Bespoke shape — "follow one request through the proxy, then turn each knob."** Two
movements. **Part A — the event-driven engine (trace it):** follow a single request from
accept → event loop → incremental parse → upstream connect → response, building the mental
model of *why* nothing blocks. **Part B — the balancing & safety knobs (choose them):** once
the engine is clear, each chapter is one decision the proxy must make — which backend?
what on failure? buffer or stream? retry or not? Reference is NGINX `release-1.31.1` source
(factchecked); the C10K forcing function frames the whole thing. Heavy source-reading
sub-course — concrete, not abstract.

## Dependency position
- **Depends on:** 03 (sockets, epoll, HTTP — the seam 10 builds on), 04 (epoll, processes,
  shared memory), 06 (consistent hashing for `hash consistent`), 18 (backpressure preview).
- **Feeds into:** 13 (scaling), 16 (CDN/edge), 18 (load shedding/timeouts/retries — 10 is
  the concrete instance), 20 (resilience), own-http-server lab feeds the agentic tool layer.
- **Appendix links DOWN:** B-linux (epoll, shared memory, accept), I/J (proxies in
  containers/k8s ingress). No dedicated NGINX appendix — 10 IS the deep reference; cross-link
  up from 16/18.

## Chapter specs (3–5 lines each)
### Part A — the event-driven engine
1. **Why event-driven: the C10K problem** — process/thread-per-connection wastes scheduler +
   memory on mostly-idle connections; readiness events let a worker run only sockets that can
   progress. Master (control: config/reload/signals) + workers (data plane). `ngx_worker_
   process_cycle` → `ngx_process_events_and_timers`. (AOSA NGINX chapter.)
2. **The worker loop & epoll** — the loop center: compute timer timeout → accept-mutex
   handling → posted-next-events → `ngx_process_events` (epoll) → posted accept events →
   release mutex → expire timers → posted events. Connections wrapped in `ngx_connection_t`;
   readiness/timers/handlers on `ngx_event_t`; epoll instance-bit drops stale events for
   reused fds. A handler installs the next handler and returns to the loop.
3. **Accept & incremental HTTP parsing** — accept is capacity-aware: `ngx_accept_disabled =
   connection_n/8 − free_connection_n` backs off; accept_mutex is OFF by default in 1.31.1
   (correct a common myth). HTTP parsing is incremental across partial reads
   (`ngx_http_wait_request_handler` → request line → headers), returning to the loop when
   more bytes are needed.
4. **Reverse proxying as a nonblocking upstream state machine** — content handler prepares
   an upstream; `ngx_http_upstream_connect` → `ngx_event_connect_peer`; if in-progress,
   install handlers/timers and return. Send request → read upstream headers incrementally →
   move response through filters / non-buffered / event pipe. Upstream keepalive pool is
   explicit per-upstream (proxy_pass ≠ automatic reuse).

### Part B — the balancing & safety knobs
5. **Load balancing algorithms** — default is smooth weighted round-robin
   (weight/effective_weight/current_weight; failures cut effective_weight by weight/max_fails,
   recover slowly). `least_conn` (float-free cross-multiply) for uneven request duration;
   `ip_hash` / `hash` / `hash consistent` (weight×160 virtual points) for affinity/locality.
   Each is a different tradeoff, not a ranking.
6. **Failure accounting & health** — passive by default: max_fails=1, fail_timeout=10s,
   max_conns=0; skip gate = `max_fails && fails≥max_fails && now−checked≤fail_timeout`;
   max_fails=0 disables penalty. Active periodic health checks are commercial — verify
   nginx.org wording. Upstream **zones** put peer state in shared memory (else per-worker
   counters fragment).
7. **Buffering, retries & replay safety** — the linked constraint: with request buffering
   off and body already sent, retry is REFUSED (`u->request_sent && request_body_no_
   buffering`). Buffering a body gives NGINX something safe to replay. proxy_buffering on by
   default; the event pipe (`ngx_event_pipe_t`) does memory buffers + temp-file spill +
   slow-client backpressure simultaneously.
8. **Timeouts & gated retries** — `proxy_next_upstream` default `error timeout`; retries
   gated by failure bits + remaining tries + timeout + body-streaming state + idempotency.
   connect/send/read timeouts default 60s and are PER-PROGRESS-EVENT, not whole-response
   deadlines. (Direct concrete instance of 18's patterns.)

## Paired build lab (/build → own-http-server-and-load-balancer)
Minimal epoll HTTP server (connection structs, read/write handlers, timers, posted events)
→ accept-backoff simulator (shared listen socket, accept mutex, capacity backoff) →
incremental HTTP parser (partial reads) → nonblocking reverse proxy (client+upstream fd,
nonblocking connect, partial writes, forward response) → upstream keepalive pool → smooth
weighted round-robin (effective_weight penalty/recovery) → least-conn (cross-multiply) →
affinity/consistent-hash balancer (weight×160 ring; measure remapping) → request-buffering
retry lab (buffered vs streaming POST) → response event pipe (temp-file spill, backpressure)
→ progress-timeout lab (timers reset on progress).

## Diagrams needed
- Process-per-connection vs event-driven (C10K): scheduler/memory cost contrast.
- Master/worker layout; the worker loop step order (the 8-step sequence as a cycle).
- `ngx_connection_t`/`ngx_event_t` + epoll readiness → handler → install-next → return.
- Upstream state machine: nonblocking connect → send → read headers → response path.
- Smooth weighted round-robin walk (current_weight updates over several picks).
- least_conn cross-multiply; consistent-hash ring (weight×160) remap on peer change.
- Event pipe: free/in/out/busy buffer chains + temp-file spill + downstream backpressure.
- Per-progress timeout vs whole-response deadline timeline.

## Sources / gaps to honor (from _research.md)
- 43 load-bearing claims factchecked vs NGINX `release-1.31.1` source (0 unsupported after
  patches). nginx.org DOC WORDING was blocked in factcheck — reverify exact nginx.org wording
  before prose (upstream/proxy/load_balancing module docs). Pin line numbers/commit SHA if
  line-level citations wanted.
- Trace before teaching as canonical: reuseport/EPOLLEXCLUSIVE, full HTTP phase engine
  (`ngx_http_core_module.c`), X-Accel-Buffering override, cache-specific proxy paths.
- Verify commercial vs OSS boundary per target version: slow_start, active health checks,
  sticky, queue, random, least_time, dynamic membership.
- Optional cluster NOT done (decide in Phase 3 if needed): TLS termination/OpenSSL session
  resumption, HTTP/2 stream multiplexing/flow control, HTTP/3/QUIC caveats. Compare NGINX
  consistent hashing to ketama/memcached if lineage wanted.
