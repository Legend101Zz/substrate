# Research Brief — Sub-course 10: NGINX Event-Driven Reverse Proxy Architecture
## Source cluster: master/worker model, event loop, nonblocking request/upstream path
## Researcher: researcher + brain validation | Date: 2026-06-10

Status: **starter cluster only**. Not yet factchecked by the dedicated factchecker agent, and not reconciled into
`_research.md`.

---

## 1. Key Mechanisms

### 1.1 Master/worker split: control plane vs. data plane

NGINX runs a master process plus worker processes. The master reads configuration, manages workers, handles
signals, reopens logs, reloads config, and performs binary upgrade flows. Workers accept, handle, and process
connections.

Primary anchors:
- AOSA NGINX chapter describes a single master and several workers/cache processes, with workers handling
  connections. Source: `https://raw.githubusercontent.com/aosabook/aosabook/master/aosabook.org/en/nginx.html`.
- `ngx_master_process_cycle()` and `ngx_start_worker_processes()` in
  `https://raw.githubusercontent.com/nginx/nginx/master/src/os/unix/ngx_process_cycle.c`.
- `ngx_worker_process_cycle()` loops around `ngx_process_events_and_timers(cycle)`.

Why it matters: the master can reload/restart workers without owning client request state; workers can be killed
and respawned without corrupting another worker's in-memory event state.

### 1.2 Worker event loop: one worker multiplexes many sockets

Within a worker, NGINX follows an event-driven, asynchronous, nonblocking architecture. AOSA explicitly frames
NGINX as C10K-driven and says workers process thousands of connections in a run loop rather than spawning one
process/thread per connection.

`ngx_process_events_and_timers()` in `src/event/ngx_event.c` is the core loop:
1. compute the next timer timeout,
2. possibly acquire the accept mutex,
3. call platform event processing (`ngx_process_events`, e.g. epoll),
4. process posted accept events,
5. release accept mutex,
6. expire timers,
7. process other posted events.

This design turns readiness notifications into callbacks instead of blocking one thread/process per connection.
Do not attach exact context-switch or per-thread-memory numbers without a direct source; those are currently
`[UNVERIFIED]`.

### 1.3 Event objects carry callback state

NGINX represents readiness as `ngx_event_t` objects and sockets as `ngx_connection_t` objects:
- `ngx_event_t` has a `handler` function pointer, timer node, queue node, and flags like active/ready/timedout.
- `ngx_connection_t` holds fd, read/write event pointers, send/recv function pointers, pool, sockaddr, and a
  generic `data` pointer.

Sources:
- `https://raw.githubusercontent.com/nginx/nginx/master/src/event/ngx_event.h`
- `https://raw.githubusercontent.com/nginx/nginx/master/src/core/ngx_connection.h`

The generic pattern is: install the next handler on the event, register interest with the event module, return to
the loop, and resume when the fd is ready. This is the NGINX state-machine style.

### 1.4 Epoll module: readiness delivery and stale-event protection

On Linux, `ngx_epoll_process_events()` calls `epoll_wait(...)`, then dispatches read/write events. NGINX stores a
connection pointer plus an instance bit in `epoll_event.data.ptr`; if the connection has been closed/reused and
an old event arrives, the instance bit detects the stale event and drops it.

Source: `https://raw.githubusercontent.com/nginx/nginx/master/src/event/modules/ngx_epoll_module.c`.

The event module is abstracted behind `ngx_event_module_t`; other platforms use kqueue/event ports/etc. The HTTP
layer should not need to know which kernel readiness primitive delivered the event.

### 1.5 Accept path and accept mutex

Multiple workers may wait on the same listening sockets. NGINX includes an accept mutex path to reduce thundering
herd effects. `ngx_process_events_and_timers()` attempts `ngx_trylock_accept_mutex(cycle)` when accept mutex is in
use; accept events are posted separately and processed while the mutex is held.

`ngx_event_accept.c` also maintains `ngx_accept_disabled`, computed from connection capacity and free
connections, so a worker near its connection limit temporarily backs off accepting more connections.

Sources:
- `https://raw.githubusercontent.com/nginx/nginx/master/src/event/ngx_event.c`
- `https://raw.githubusercontent.com/nginx/nginx/master/src/event/ngx_event_accept.c`

Modern deployments may use `SO_REUSEPORT`; exact defaults and interaction with `EPOLLEXCLUSIVE` need a separate
pass before teaching operational guidance.

### 1.6 HTTP request path: connection handler → request phases → content handler

After accept, HTTP initialization wires the connection read event to an HTTP wait/request handler. Request parsing
and processing are incremental: if more bytes are needed, the handler returns to the event loop and resumes when
readable again.

The HTTP request then moves through phase handlers such as rewrite, find-config/location, access, content, and log.
The exact phase names and module hooks are in the HTTP core/request source; this starter cluster only verifies the
existence of the phased state-machine model, not every phase edge case.

Sources:
- `https://raw.githubusercontent.com/nginx/nginx/master/src/http/ngx_http_request.c`
- `https://raw.githubusercontent.com/nginx/nginx/master/src/http/ngx_http_request.h`

### 1.7 Reverse proxy/upstream path is also nonblocking state-machine work

For proxied requests, the content handler initializes an upstream object and uses nonblocking connect/send/read
handlers:

- `ngx_http_upstream_init_request(r)` creates or prepares the upstream request.
- `ngx_http_upstream_connect(r, u)` calls `ngx_event_connect_peer(&u->peer)`. If the connection is in progress,
  it installs handlers/timers and returns to the event loop.
- `ngx_http_upstream_send_request(...)` sends buffered request data to the upstream and returns on partial writes.
- `ngx_http_upstream_process_header(...)` reads/parses upstream response headers incrementally.
- Response body handling streams through NGINX's output/filter machinery rather than requiring one blocking
  upstream round trip per client request.

Sources:
- `https://raw.githubusercontent.com/nginx/nginx/master/src/http/ngx_http_upstream.c`
- `https://raw.githubusercontent.com/nginx/nginx/master/src/http/modules/ngx_http_proxy_module.c`

### 1.8 Upstream keepalive avoids connection setup per request

The upstream keepalive module caches idle upstream connections per worker. It wraps upstream peer `get` and `free`
callbacks: `get` tries to reuse a matching cached connection; `free` saves a healthy connection back into the
cache, subject to configuration limits.

Source: `https://raw.githubusercontent.com/nginx/nginx/master/src/http/modules/ngx_http_upstream_keepalive_module.c`.

Do not state "proxy_pass always reuses upstream connections". Reuse depends on upstream keepalive configuration
and protocol/header behavior.

---

## 2. Foundational Sources

| Area | Primary source | Status |
|---|---|---|
| Architecture overview, C10K motivation, master/workers, event-driven design, memory model | AOSA Vol. 2 NGINX chapter by Andrew Alexeev: `https://raw.githubusercontent.com/aosabook/aosabook/master/aosabook.org/en/nginx.html` | VERIFIED snippets |
| Master/worker lifecycle | `https://raw.githubusercontent.com/nginx/nginx/master/src/os/unix/ngx_process_cycle.c` | VERIFIED snippets |
| Event loop and accept mutex | `https://raw.githubusercontent.com/nginx/nginx/master/src/event/ngx_event.c` | VERIFIED snippets |
| epoll implementation | `https://raw.githubusercontent.com/nginx/nginx/master/src/event/modules/ngx_epoll_module.c` | VERIFIED snippets |
| Accept/backoff path | `https://raw.githubusercontent.com/nginx/nginx/master/src/event/ngx_event_accept.c` | VERIFIED snippets |
| Event/connection structs | `ngx_event.h`, `ngx_connection.h` on NGINX master | VERIFIED reachable |
| HTTP request handling | `ngx_http_request.c`, `ngx_http_request.h` on NGINX master | VERIFIED reachable |
| Upstream/reverse proxy path | `ngx_http_upstream.c`, `ngx_http_proxy_module.c` on NGINX master | VERIFIED snippets |
| Upstream keepalive | `ngx_http_upstream_keepalive_module.c` on NGINX master | VERIFIED snippets |
| C10K primary page | `http://www.kegel.com/c10k.html` | NOT fetched directly; AOSA cites it |

Release-pin caveat: this brief uses NGINX `master` source URLs. Before final prose, pin to a release tag or commit.

---

## 3. Why It’s This Way — Forcing Constraints

- **Thread/process-per-connection wastes resources for mostly-idle sockets.** C10K-era servers needed to hold many
  keepalive/slow clients without one OS scheduling entity per client.
- **Readiness events let work follow data.** A worker only runs callbacks for sockets that can make progress.
- **Nonblocking upstream connect prevents one slow backend from freezing a worker.** `EINPROGRESS` plus write-ready
  event/timer turns connect into a resumable state.
- **Master/worker isolates failure and reload control.** The master can supervise workers and reload config while
  workers keep serving or gracefully drain.
- **Preallocated connection/event arrays bound memory.** `worker_connections` becomes both a capacity and budget
  knob; per-accept allocation is avoided.
- **Posted event queues shorten critical sections.** Accept events can be handled while holding accept mutex; slower
  ordinary handlers run after release.
- **Buffer chains and filters avoid needless copies where possible.** AOSA emphasizes avoiding copying; exact
  zero-copy behavior depends on the path (`sendfile`, proxy buffering, filters, TLS).

---

## 4. Common Misconceptions

1. **“NGINX is one single-threaded process.”** It is typically multiple worker processes; each worker's event loop is
   single-threaded in the common model.
2. **“Event-driven means never blocks.”** AOSA explicitly notes disk I/O can still block a worker; thread pools/AIO
   mitigate specific cases.
3. **“Accept mutex perfectly balances workers.”** It reduces herd effects; it is not a per-connection fair scheduler.
4. **“`proxy_pass` always opens a new backend connection.”** Upstream keepalive can reuse connections when configured.
5. **“`proxy_pass` always reuses backend connections.”** Also false; reuse depends on keepalive config and conditions.
6. **“NGINX buffers whole upstream responses before sending clients anything.”** Proxy buffering and streaming behavior
   depend on configuration and response path; do not oversimplify.
7. **“epoll magically makes all operations O(1).”** Epoll avoids scanning all fds for readiness; application handlers
   can still do expensive work.
8. **“Follower source paths or master branch paths are stable forever.”** Use release-pinned NGINX sources before
   final course prose.

---

## 5. Build-Your-Own Targets

1. **Minimal event loop:** nonblocking listening socket, `epoll_wait`, connection pool, read/write handler pointers.
2. **Echo server with EAGAIN loops:** read until `EAGAIN`, write partial buffers, resume via write readiness.
3. **Timer integration:** keep a nearest-timeout timer structure and use it to bound `epoll_wait` timeout.
4. **Accept mutex/backoff simulation:** multiple workers competing for one listener; add near-capacity accept backoff.
5. **Incremental HTTP parser:** parse request line/headers across multiple reads, returning to event loop when incomplete.
6. **Nonblocking reverse proxy:** client connection + upstream connection, nonblocking connect, partial write handling,
   upstream response header parser.
7. **Upstream keepalive pool:** per-worker queue of idle upstream connections, health/timeout/request-count limits.
8. **Filter chain toy:** represent response as buffer-chain nodes; add a header/body transform without copying
   untouched buffers.

---

## 6. Open Questions / Gaps

- Factchecker has not yet reviewed this 10 starter brief.
- Pin NGINX source URLs to a release tag/commit instead of `master`.
- Verify current `accept_mutex`, `reuseport`, and `EPOLLEXCLUSIVE` defaults/selection in source.
- Trace `ngx_event_core_init_conf` for default event config values.
- Trace `ngx_thread_pool.c` and epoll eventfd notification before teaching AIO/thread-pool integration.
- Trace full HTTP phase engine source (`ngx_http_core_module.c`) before listing every phase as canonical course content.
- Trace load-balancing peer selection algorithms (`round_robin`, `least_conn`, `hash`, `ip_hash`) in the next 10 cluster.
- Trace proxy buffering vs. streaming in detail before teaching body flow.
- HTTP/2, HTTP/3/QUIC, TLS handshake/session resumption, and OpenResty/Lua are out of scope for this starter cluster.
