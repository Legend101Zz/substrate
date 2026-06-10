# Research Brief — Sub-course 10: NGINX Proxy Buffering, Retries, Timeouts, and Backpressure
## Source cluster: request/response buffering, temp files, retry limits, timeout state machines
## Researcher: brain manual primary-source pass | Date: 2026-06-10

Status: drafted from NGINX `release-1.31.1` source and official NGINX docs. Factchecker spot-check found no
unsupported numeric/source claims; nginx.org doc wording was blocked in the factchecker environment, so doc-only
wording must be reverified before Phase 2 prose.

---

## 1. Key Mechanisms

### 1.1 Proxying is two coupled streams: downstream client and upstream server

In NGINX proxying, a request has a downstream client connection and an upstream peer connection. The upstream code
moves through nonblocking states: connect, send request, read headers, then move response bytes through filters,
output chains, or an event pipe. This is not a single blocking function call from client to backend.

Primary source: NGINX `release-1.31.1`
`src/http/ngx_http_upstream.c`, especially `ngx_http_upstream_connect()`,
`ngx_http_upstream_send_request()`, `ngx_http_upstream_process_header()`, and the buffered/non-buffered response
paths.

### 1.2 Request buffering protects retries and isolates upstreams from slow clients

Official proxy docs say `proxy_request_buffering on` is the default. With request buffering enabled, NGINX reads the
whole client request body before sending it to the proxied server. If disabled, the request body is sent immediately
as it is received; the docs warn that in that case the request cannot be passed to the next server if NGINX already
started sending the request body. Factchecker note: nginx.org wording was blocked in the factchecker environment;
the default and retry gate were confirmed in `release-1.31.1` source.

The source backs this up:

- proxy module merge defaults set `upstream.request_buffering` to `1`.
- `ngx_http_proxy_handler()` sets `r->request_body_no_buffering = 1` only when `proxy_request_buffering` is off,
  there is no scripted request body, the request body is passed, and chunking/version conditions allow it.
- `ngx_http_upstream_next()` refuses retry when `u->request_sent && r->request_body_no_buffering`.

Primary sources:
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_request_buffering`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_proxy_module.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`

Why it matters: request buffering is a replayability boundary. If NGINX has the full body, it can retry some upstream
failures before exposing them to the client. If bytes have already been streamed to an upstream, retrying can duplicate
side effects or become impossible.

### 1.3 Response buffering decouples fast upstreams from slow clients

Official docs say `proxy_buffering on` is the default. With buffering enabled, NGINX receives the response from the
proxied server as soon as possible and saves it in buffers controlled by `proxy_buffer_size` and `proxy_buffers`; if
the response exceeds memory buffers, part can be saved to a temporary file. With buffering disabled, the response is
passed synchronously/as-soon-as-possible to the client as it is received. Factchecker note: nginx.org wording was
blocked; defaults and event-pipe/temp-file behavior were confirmed in source.

The source backs the defaults:

- `conf->upstream.buffering` merges to `1`.
- `proxy_buffer_size` defaults to `ngx_pagesize`.
- `proxy_buffers` defaults to `8` buffers of `ngx_pagesize`.
- `proxy_busy_buffers_size` defaults to `2 * max(proxy_buffer_size, proxy_buffers.size)`.
- `proxy_max_temp_file_size` defaults to `1024 * 1024 * 1024`, with `0` disabling temp files.

Primary sources:
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering`
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_max_temp_file_size`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_proxy_module.c`

Why it matters: buffering lets NGINX free the upstream connection faster when clients are slow, but it consumes memory
and may spill to disk. Turning it off reduces buffering latency/memory for streaming, but couples upstream read pace to
client write pace more tightly.

### 1.4 Temp files are part of the event pipe, not a separate “download everything first” phase

Buffered response handling uses `ngx_event_pipe_t`. `ngx_http_upstream.c` allocates a temp file structure, points it
at the configured temp path, sets `max_temp_file_size` and `temp_file_write_size`, then drives reads and writes through
`ngx_event_pipe()`.

`src/event/ngx_event_pipe.c` shows the mechanics:

- it reads from upstream into raw buffers when upstream read readiness and buffer availability allow;
- if downstream is ready and buffering/caching constraints allow, it passes chains to the output filter;
- if there are buffered input chains and temp-file limits allow, it writes chains to a temporary file and creates file
  buffers pointing at temp-file offsets;
- it respects `busy_size`, `free_raw_bufs`, `busy`, `out`, and downstream write readiness/delays.

Primary sources:
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_pipe.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_pipe.h`

Misconception to preempt: buffering does not necessarily mean “read the entire response before sending the first byte.”
It means NGINX may read ahead from upstream into memory/disk while independently flushing to the client subject to
buffer, temp-file, filter, and downstream readiness limits.

### 1.5 `proxy_next_upstream` is a controlled retry policy, not blind retry forever

Official docs default `proxy_next_upstream` to `error timeout`. The directive controls which conditions cause NGINX
to pass a request to the next server; docs also provide `proxy_next_upstream_tries` and
`proxy_next_upstream_timeout`, both defaulting to `0` (unlimited by that knob, but still bounded by available peers and
other conditions). Factchecker note: nginx.org wording was blocked; bitmask/default behavior was confirmed in source.

Source-level gates in `ngx_http_upstream_test_next()` and `ngx_http_upstream_next()` include:

- the response status/error must match the configured bitmask,
- there must be more peer tries available,
- the request must not already have been sent with `request_body_no_buffering`,
- `next_upstream_timeout`, if nonzero, must not be exceeded,
- non-idempotent methods such as POST/LOCK/PATCH are treated specially by adding the `non_idempotent` failure bit.

Primary sources:
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream`
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream_tries`
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream_timeout`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`

Why it matters: retries improve availability for connect failures/timeouts before side effects, but unsafe retries can
multiply writes. NGINX's retry gates are an encoded version of that distributed-systems constraint.

### 1.6 Connect, send, and read timeouts bound gaps between progress events

Official docs default `proxy_connect_timeout`, `proxy_send_timeout`, and `proxy_read_timeout` to `60s`. The source
merge defaults are also `60000` milliseconds for connect/send/read. Factchecker note: nginx.org wording was blocked;
source defaults and timer installation were confirmed. The upstream code installs timers on the relevant
events:

- connect path adds a write timer with `connect_timeout` while the nonblocking connect is in progress;
- sending request data adds a write timer with `send_timeout` when upstream writes would block;
- reading response headers/body adds read timers with `read_timeout`.

Docs are explicit that `proxy_read_timeout` is set between two successive read operations, not for the whole response;
if the proxied server transmits nothing within the timeout, the connection is closed. `proxy_send_timeout` is similarly
between successive write operations, not the whole request transmission. Factchecker note: the per-operation behavior
was source-confirmed through event-timer callbacks; reverify exact nginx.org wording before Phase 2 prose.

Primary sources:
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_connect_timeout`
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout`
- `https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_send_timeout`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_proxy_module.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`

### 1.7 Slow client vs. slow upstream behavior is asymmetric

- **Slow client, fast upstream, response buffering on:** NGINX can read ahead from upstream into buffers/temp files,
  freeing or at least draining the upstream faster while the downstream client drains slowly.
- **Slow client, buffering off / streaming:** downstream write readiness and busy output chains can throttle upstream
  reading; source paths use non-buffered upstream/downstream handlers and output chains.
- **Slow upstream:** read timers and upstream event readiness govern progress; NGINX cannot synthesize missing backend
  bytes, only time out, retry if safe/configured, or relay partial data.
- **Slow request upload:** with request buffering on, NGINX absorbs upload before upstream; with buffering off, upstream
  connection occupancy can be tied to client upload pace, and retries after body streaming are constrained.

Primary source: `ngx_http_upstream_process_non_buffered_request()` and event-pipe paths in NGINX `release-1.31.1`
`src/http/ngx_http_upstream.c` plus `src/event/ngx_event_pipe.c`.

---

## 2. Foundational Sources

| Mechanism | Primary source | Notes |
|---|---|---|
| Proxy directive docs | `https://nginx.org/en/docs/http/ngx_http_proxy_module.html` | buffering, temp files, retries, timeouts |
| Proxy module config/defaults | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_proxy_module.c` | defaults for buffering/timeouts/buffers/temp sizes |
| Upstream state machine | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c` | connect/send/read/retry/non-buffered paths |
| Event pipe | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_pipe.c`; `.../ngx_event_pipe.h` | buffered body movement, temp file writes, backpressure chains |

---

## 3. Why It’s This Way — Forcing Constraints

- **Retries require replayable input.** If a request body was streamed to an upstream, NGINX may not be able to safely
  replay it to another upstream.
- **Slow clients should not monopolize upstream sockets.** Response buffering lets NGINX drain upstream responses and
  then serve slow clients from local buffers/disk.
- **Memory is finite.** Buffers are bounded; temp files are the spillway when response data outruns client drain rate.
- **Timeouts are progress timers, not total SLA timers.** Event-driven servers need to distinguish “no progress on this
  fd” from “long but active transfer.”
- **Backpressure is implemented with readiness, timers, and chain accounting.** NGINX does not need a single global
  “backpressure” feature flag; it emerges from not reading/writing when buffers, busy chains, or readiness say stop.

---

## 4. Common Misconceptions

1. **“NGINX always streams proxied responses.”** Default `proxy_buffering` is on.
2. **“NGINX always buffers the entire response before sending anything.”** Event pipe can send buffered chains while
   also reading/spilling; buffering is not all-or-nothing whole-response staging.
3. **“Turning request buffering off is free latency reduction.”** It can reduce upload latency to upstream, but it hurts
   retryability and can tie upstream resources to slow clients.
4. **“`proxy_next_upstream` retries all failures.”** It is gated by error type/status, tries, timeout, request-body
   buffering, and non-idempotent method handling.
5. **“Read timeout means the whole response must finish in 60s.”** Docs say it is between successive read operations.
6. **“Temp files mean caching.”** Proxy temp files can be buffering spillover even without cache/store semantics.

---

## 5. Build-Your-Own Targets

1. **Replayable request body buffer:** buffer a POST body to memory/file, then retry a failed upstream connect safely.
2. **Streaming request mode:** send upload bytes directly to upstream and demonstrate why retry after partial send is unsafe.
3. **Response event pipe:** implement `in`, `out`, `busy`, `free` chains and spill to a temp file when memory buffers fill.
4. **Progress timeouts:** implement connect/send/read timers that reset on progress rather than total request lifetime.
5. **Retry policy matrix:** model `error`, `timeout`, HTTP statuses, idempotent vs. non-idempotent methods, max tries, and
   total retry timeout.
6. **Slow-client lab:** upstream writes fast, client reads slowly; compare buffering on/off and observe upstream socket
   occupancy and disk spill.

---

## 6. Open Questions / Gaps

- Factchecker passed the source-level default values and retry caveats; nginx.org doc wording still needs recheck before Phase 2 prose.
- Trace exact interaction with `X-Accel-Buffering` (`ngx_http_upstream_process_buffering`) before teaching app-controlled
  buffering overrides.
- Trace cache-specific paths separately; this cluster covers proxy buffering, not full HTTP cache semantics.
- Trace HTTP/2/HTTP/3 flow-control interaction separately if later course scope includes multiplexing caveats.
- Trace OS-level `sendfile`, AIO/thread pools, and TLS write buffering separately before making zero-copy claims.
