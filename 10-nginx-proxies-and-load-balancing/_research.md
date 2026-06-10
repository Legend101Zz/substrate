# Reconciled Research — Sub-course 10: NGINX, Proxies, and Load Balancing
## Phase 1 synthesis from 10 cluster briefs
## Date: 2026-06-10

Coverage status: **factchecked and reconciled for the core NGINX reverse-proxy/load-balancing path**. Optional TLS,
HTTP/2, and HTTP/3 multiplexing caveats remain open for a later source cluster if Phase 2 needs them.

Cluster inputs:
- `_research_event-driven-reverse-proxy.md`
- `_research_load-balancing-peer-selection.md`
- `_research_proxy-buffering-retries-timeouts.md`
- `_factcheck_phase1.md`

Factcheck status: `10-nginx-proxies-and-load-balancing/_factcheck_phase1.md` checked 43 load-bearing claims against
NGINX `release-1.31.1` source. No unsupported/misattributed claims remained after BRAIN patches. nginx.org doc wording
was blocked in the factchecker environment; source-level behavior was confirmed where possible, and doc-only wording is
flagged below for Phase 2 recheck.

---

## 1. Key Mechanisms

### 1.1 Master/worker architecture separates control from request processing

NGINX uses a master process to read config, supervise workers, handle signals, reload configuration, reopen logs, and
perform upgrade flows. Workers run the request/event handling data plane. In `release-1.31.1`,
`ngx_worker_process_cycle()` loops around `ngx_process_events_and_timers(cycle)`.

Primary anchors:
- AOSA Vol. 2 NGINX chapter by Andrew Alexeev for architecture/C10K background:
  `https://raw.githubusercontent.com/aosabook/aosabook/master/aosabook.org/en/nginx.html`
- NGINX `release-1.31.1` `src/os/unix/ngx_process_cycle.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/os/unix/ngx_process_cycle.c`

### 1.2 The worker is an event-driven state-machine executor

`ngx_process_events_and_timers()` is the worker loop center. The factchecked order is:

1. compute the next timer timeout,
2. if accept mutex is enabled, handle `ngx_accept_disabled` and possibly acquire accept mutex,
3. if `ngx_posted_next_events` is non-empty, move it to the posted-events queue and clamp timeout to `0`,
4. call platform event processing (`ngx_process_events`, e.g. epoll),
5. process posted accept events,
6. release accept mutex,
7. expire timers,
8. process normal posted events.

Primary anchors:
- `src/event/ngx_event.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event.c`
- `src/event/ngx_event.h` and `src/core/ngx_connection.h` for event/connection structs.

The deep mechanism: sockets are wrapped in `ngx_connection_t`; readiness, timers, queues, and callback handlers live
on `ngx_event_t`. A handler installs the next handler/interest, returns to the loop, and resumes when the fd/timer can
make progress.

### 1.3 Linux epoll delivery includes stale-event protection

On Linux, `ngx_epoll_process_events()` calls `epoll_wait`, pulls connection pointers from `event.data.ptr`, and uses
an instance bit to detect stale readiness events for closed/reused connections. If the fd was closed or the event
instance no longer matches, NGINX drops the stale event.

Primary source:
- `src/event/modules/ngx_epoll_module.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/modules/ngx_epoll_module.c`

### 1.4 Accept behavior is capacity-aware and mutex-gated only when configured

NGINX has an accept mutex path to reduce thundering herd effects, but in `release-1.31.1` the default
`accept_mutex` is `0` and `accept_mutex_delay` defaults to `500ms`. `ngx_use_accept_mutex` becomes true only when
master mode, more than one worker, and configured accept mutex are all true.

`ngx_event_accept.c` computes `ngx_accept_disabled = connection_n / 8 - free_connection_n`; if positive, a worker
backs off accepting until capacity improves. Accept events are posted and processed while the mutex is held, then the
mutex is released before ordinary posted events run.

Primary sources:
- `src/event/ngx_event.c`
- `src/event/ngx_event_accept.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_accept.c`

### 1.5 HTTP request processing is incremental and phased

After accept, HTTP initialization assigns a read event handler such as `ngx_http_wait_request_handler`; parsing moves
to `ngx_http_process_request_line` and header processing. When more bytes are needed, the handler returns to the event
loop and resumes on readiness. Later, request processing enters the HTTP phase engine/content handler path.

Primary sources:
- `src/http/ngx_http_request.c`
- `src/http/ngx_http_request.h`
- `src/http/ngx_http_core_module.c` for full phase-engine details before Phase 2 prose.

### 1.6 Reverse proxying is a nonblocking upstream state machine

For proxied requests, the content handler prepares an upstream object. `ngx_http_upstream_connect()` calls
`ngx_event_connect_peer(&u->peer)`; if the connection is in progress, NGINX installs handlers/timers and returns to
the loop. Then NGINX sends the request, reads upstream headers incrementally, and moves the response through output
filters, non-buffered handlers, or an event pipe.

Primary sources:
- `src/http/ngx_http_upstream.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`
- `src/http/modules/ngx_http_proxy_module.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_proxy_module.c`

### 1.7 Upstream keepalive is explicit and per upstream configuration

The upstream keepalive module wraps peer `get` and `free` callbacks. `get` can reuse a matching cached upstream
connection; `free` can save a healthy connection back into the per-worker cache subject to limits. `proxy_pass` does
not automatically imply upstream connection reuse in every configuration.

Primary source:
- `src/http/modules/ngx_http_upstream_keepalive_module.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_keepalive_module.c`

### 1.8 Default upstream selection is smooth weighted round-robin

Round-robin peers carry `weight`, `effective_weight`, `current_weight`, connection counters, failure counters, and
availability fields. Selection skips down/recently failed/full peers, adds `effective_weight` into `current_weight`,
slowly recovers `effective_weight` toward `weight`, chooses the highest `current_weight`, then subtracts total
weight from the winner. Failures reduce `effective_weight` by `weight / max_fails` when `max_fails` is nonzero.

Primary sources:
- `src/http/ngx_http_upstream_round_robin.h`
- `src/http/ngx_http_upstream_round_robin.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream_round_robin.c`

### 1.9 Failure accounting is passive unless active health checks are specifically available

The open-source source path confirms default `max_fails = 1`, `fail_timeout = 10`, and `max_conns = 0` in upstream
server parsing. The skip condition is gated by `peer->max_fails && peer->fails >= peer->max_fails && now - checked <=
fail_timeout`; source behavior also confirms `max_fails=0` disables skip/penalty accounting by skipping those gated
conditions. For a single-peer group, the free path clears `fails` and returns early.

NGINX docs describe active periodic health checks as commercial; reverify exact nginx.org wording before Phase 2 prose
because the factchecker environment could not fetch nginx.org.

### 1.10 Alternate peer selection methods choose different tradeoffs

- `least_conn`: chooses the peer with the lowest active-connection ratio, comparing without floats via
  `peer->conns * best->weight < best->conns * peer->weight`; ties use weighted round-robin mechanics.
- `ip_hash`: hashes client address; source uses first 3 bytes for IPv4, 16 bytes for IPv6, starts hash at `89`, and
  falls back after too many tries or fewer than two peers.
- `hash`: uses a configured key expression; non-consistent mode uses CRC32/rehash over the key.
- `hash ... consistent`: builds a point ring with `peer->weight * 160` virtual points per peer, sorts/de-duplicates,
  and looks up first point >= key hash.

Primary sources:
- `src/http/modules/ngx_http_upstream_least_conn_module.c`
- `src/http/modules/ngx_http_upstream_ip_hash_module.c`
- `src/http/modules/ngx_http_upstream_hash_module.c`

### 1.11 Upstream zones put runtime peer state in shared memory

The `zone` module creates named shared memory with `ngx_shared_memory_add`, initializes a slab pool, and copies peers
into shared memory. Zone-specific fields in round-robin peer structs support shared peer configuration/state and locks.
Without a shared zone, workers can hold independent process-local counters.

Primary source:
- `src/http/modules/ngx_http_upstream_zone_module.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_zone_module.c`

### 1.12 Proxy buffering and retryability are linked

`proxy_request_buffering` defaults to on in source. With request buffering off and a request body already sent,
`ngx_http_upstream_next()` refuses retry (`u->request_sent && r->request_body_no_buffering`). This is the key
replayability constraint: buffering the whole request body gives NGINX something it can safely replay; streaming a
body to an upstream can make retries unsafe or impossible.

`proxy_buffering` also defaults to on. Source defaults include `proxy_buffer_size = ngx_pagesize`,
`proxy_buffers = 8 * ngx_pagesize`, `proxy_busy_buffers_size = 2 * max(buffer_size, buffer-slot-size)`, and
`proxy_max_temp_file_size = 1 GiB` with `0` disabling temp-file usage.

Primary source:
- `src/http/modules/ngx_http_proxy_module.c`

### 1.13 The event pipe implements response buffering, temp files, and backpressure

Buffered response handling uses `ngx_event_pipe_t`: chains of free/in/out/busy buffers, upstream/downstream fds,
temp-file metadata, busy-size limits, read/send timeouts, and flags for upstream/downstream done/error. It can read
from upstream, write chains to the downstream output filter, and spill chains into temp files when memory buffers fill
and temp-file policy allows.

Primary sources:
- `src/event/ngx_event_pipe.c`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_pipe.c`
- `src/event/ngx_event_pipe.h`:
  `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_pipe.h`

### 1.14 Retry and timeout policy is gated, not blind

Source default `proxy_next_upstream` is `error timeout`; `proxy_next_upstream_tries` and
`proxy_next_upstream_timeout` default to `0`. Retry gates check configured failure bits, remaining tries, timeout,
request-body streaming state, and non-idempotent method handling.

`proxy_connect_timeout`, `proxy_send_timeout`, and `proxy_read_timeout` all default to `60000ms` in source. Timers are
installed on event callbacks, so source behavior supports the “progress timeout” model rather than a single whole
response deadline.

---

## 2. Foundational Sources

- AOSA Vol. 2 NGINX chapter by Andrew Alexeev — C10K motivation, event-driven design, master/workers:
  `https://raw.githubusercontent.com/aosabook/aosabook/master/aosabook.org/en/nginx.html`
- NGINX `release-1.31.1` source tree:
  `src/os/unix/ngx_process_cycle.c`, `src/event/ngx_event.c`, `src/event/modules/ngx_epoll_module.c`,
  `src/event/ngx_event_accept.c`, `src/event/ngx_event_pipe.c`, `src/http/ngx_http_request.c`,
  `src/http/ngx_http_upstream.c`, `src/http/modules/ngx_http_proxy_module.c`,
  `src/http/modules/ngx_http_upstream_keepalive_module.c`, `src/http/ngx_http_upstream_round_robin.c/.h`,
  `src/http/modules/ngx_http_upstream_least_conn_module.c`, `src/http/modules/ngx_http_upstream_ip_hash_module.c`,
  `src/http/modules/ngx_http_upstream_hash_module.c`, `src/http/modules/ngx_http_upstream_zone_module.c`.
- Official NGINX docs needing Phase 2 wording recheck because factchecker was blocked from nginx.org:
  `https://nginx.org/en/docs/http/ngx_http_upstream_module.html`,
  `https://nginx.org/en/docs/http/ngx_http_proxy_module.html`,
  `https://nginx.org/en/docs/http/load_balancing.html`.

---

## 3. Why It’s This Way — Constraints

- **C10K / many idle clients:** one process/thread per connection wastes scheduler and memory resources; readiness
  events let workers run only sockets that can make progress.
- **Independent worker processes:** process isolation supports robustness and reloads, but runtime upstream counters
  fragment unless moved into shared memory zones.
- **Backend heterogeneity:** weights express unequal capacity; `effective_weight` lets failures temporarily reduce
  traffic to a peer without permanently deleting it.
- **Uneven request duration:** `least_conn` exists because round-robin ignores how long prior requests stay active.
- **Locality/affinity:** `ip_hash` and generic hash route similar keys to the same peers for cache/session locality,
  while still needing fallback for unavailable peers.
- **Replay safety:** retries require the request body to be replayable; streaming an already-sent body to another peer
  risks duplicate side effects.
- **Slow clients vs. upstream utilization:** response buffering drains upstreams faster but consumes memory/disk;
  streaming reduces buffering but couples upstream progress to downstream client speed.
- **Finite memory:** buffer chains and temp files bound memory while preserving event-driven progress.

---

## 4. Misconceptions

1. **“NGINX is one single-threaded process.”** It is typically a master plus multiple workers; each worker commonly runs
   an event loop.
2. **“Event-driven means nothing ever blocks.”** Disk I/O, filters, and OS behavior can still block; thread pools/AIO are
   separate mitigations.
3. **“Accept mutex is always on.”** In `release-1.31.1`, default `accept_mutex` is off.
4. **“Round-robin means equal traffic.”** NGINX default is smooth weighted round-robin.
5. **“`least_conn` is globally perfect.”** It depends on state visible to workers; shared zones change that visibility.
6. **“`ip_hash` is session storage.”** It is deterministic routing, not durable session state.
7. **“Open-source NGINX has active health checks by default.”** Source confirms passive failure accounting; active
   health-check availability must be version/product verified.
8. **“Proxy buffering means buffer the whole response before sending.”** Event pipe can simultaneously buffer, spill,
   and flush chains.
9. **“Turning request buffering off is always better.”** It can reduce upload latency but reduces safe retryability.
10. **“Read timeout is total response time.”** Source timers support per-progress-event timeout behavior.

---

## 5. Build-Your-Own Targets

1. **Minimal epoll HTTP server:** connection structs, read/write handlers, timers, posted events.
2. **Accept backoff simulator:** multiple workers sharing a listening socket; add accept mutex and capacity backoff.
3. **Incremental HTTP parser:** parse request line/headers across partial reads.
4. **Nonblocking reverse proxy:** client fd + upstream fd, nonblocking connect, partial writes, header parser, response
   forwarding.
5. **Upstream keepalive pool:** per-worker cached upstream connections with get/free callback wrapping.
6. **Smooth weighted round-robin:** `weight`, `effective_weight`, `current_weight`, passive failure penalty/recovery.
7. **Least-connection balancer:** weighted active-connection comparison via cross multiplication.
8. **Affinity/consistent-hash balancer:** client-key hash and `weight * 160` virtual point ring; measure remapping.
9. **Request-buffering retry lab:** compare buffered vs. streaming POST retry behavior.
10. **Response event pipe:** memory buffers, busy chains, temp-file spill, and slow-client backpressure.
11. **Progress timeout lab:** connect/read/send timers that reset on progress rather than whole-transfer deadlines.

---

## 6. Open Questions / Gaps

- Reverify exact nginx.org documentation wording before Phase 2 prose; factchecker environment could not fetch nginx.org,
  though source-level behavior passed.
- Pin exact source line numbers or commit hash if Phase 2 wants line-level citations rather than `release-1.31.1` tag URLs.
- Trace `reuseport` and `EPOLLEXCLUSIVE` selection/default interaction before teaching operational accept guidance.
- Trace full HTTP phase engine (`ngx_http_core_module.c`) before listing every phase as canonical teaching content.
- Trace `X-Accel-Buffering` / `ngx_http_upstream_process_buffering` before teaching app-controlled buffering overrides.
- Trace cache-specific proxy paths separately; proxy buffering is not full HTTP cache semantics.
- Optional cluster not done: TLS termination, OpenSSL callbacks/session resumption, HTTP/2 stream multiplexing/flow control,
  and HTTP/3/QUIC caveats.
- Verify commercial/open-source boundaries for `slow_start`, active health checks, sticky, queue, random, least_time, and
  dynamic membership in the exact target NGINX version before operational configuration prose.
- Compare NGINX consistent hashing with original ketama/memcached if historical lineage is needed.
