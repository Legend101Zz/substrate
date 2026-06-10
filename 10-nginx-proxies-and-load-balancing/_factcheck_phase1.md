# Factcheck Report — Sub-course 10: NGINX Phase 1 Research Briefs
## Factchecker: factchecker-062c75 | Date: 2026-06-10
## Files checked:
- `_research_event-driven-reverse-proxy.md`
- `_research_load-balancing-peer-selection.md`
- `_research_proxy-buffering-retries-timeouts.md`

All source verification was performed against `nginx/nginx` tag `release-1.31.1`
on `raw.githubusercontent.com`. nginx.org was blocked by the corporate URL filter;
those doc-URL claims were verified through source code instead and are noted.
AOSA book URL (raw.githubusercontent.com/aosabook) was reachable.

Post-factcheck BRAIN patches applied on 2026-06-10:
- pinned remaining NGINX source URLs in `_research_event-driven-reverse-proxy.md` to `release-1.31.1`;
- added the missing `ngx_posted_next_events` step to the event-loop sequence;
- annotated nginx.org doc-wording claims in load-balancing/proxy-buffering briefs as needing recheck before Phase 2 prose while keeping source-confirmed behavior.

---

## Verdict Table

BLOCKERS and UNSUPPORTED first, then WARN, then PASS.

| # | File | Claim | Verdict | Source | Note |
|---|---|---|---|---|---|
| 1 | event-driven | Sections 1.3–1.8 text source URLs use `/master/` branch, not `release-1.31.1`, contradicting the table footer that says "Release pin: source links in this brief use NGINX release-1.31.1" | **WARN** | `https://raw.githubusercontent.com/nginx/nginx/master/src/event/ngx_event.h` (as cited) vs `release-1.31.1` tag | Pinning inconsistency: the text of §1.3, §1.4, §1.5, §1.6, §1.7, §1.8 all cite `master` branch URLs. The source table entry for event/connection structs also notes `release-1.31.1` is the pin. Must be corrected to `release-1.31.1` URLs before reconciliation. No claims are factually wrong (master matches release at verification time), but reproducibility is broken. |
| 2 | event-driven | Event loop step order description omits the `ngx_posted_next_events` processing step that occurs between mutex acquisition and `ngx_process_events()` | **WARN** | `release-1.31.1/src/event/ngx_event.c` L239–247 | The actual order in `ngx_process_events_and_timers()` is: (1) timer, (2) accept mutex, **(3) move ngx_posted_next_events and set timer=0**, (4) ngx_process_events, (5) ngx_posted_accept_events, (6) unlock mutex, (7) expire timers, (8) ngx_posted_events. The brief omits step 3. Not a wrong claim; just an incomplete description. Note before Phase 2 prose. |
| 3 | all three | nginx.org doc URLs referenced throughout (proxy_module.html, upstream_module.html, load_balancing.html, etc.) could not be fetched — corporate proxy blocks nginx.org | **NEEDS-SOURCE** | nginx.org blocked | All numeric defaults (buffer sizes, timeouts, next_upstream behavior) were independently confirmed in release-1.31.1 source. Doc-layer claims (e.g., directive description wording, commercial annotations) are unverified from nginx.org but consistent with source. Annotate any claim that relies solely on doc wording before writing course prose. |
| 4 | load-balancing | `max_fails=0` disables attempt accounting | **NEEDS-SOURCE** | nginx.org blocked; source: `release-1.31.1/src/http/ngx_http_upstream_round_robin.c` L1063 | Source condition `if (peer->max_fails) { peer->effective_weight -= ... }` means max_fails=0 skips weight penalty; and L873–875 skip condition also gates on `peer->max_fails`. This supports the claim at source level. Doc wording ("disables") unverifiable from nginx.org. Mark NEEDS-SOURCE for the doc-layer wording; mark SUPPORTED for the source-level behavior. |
| 5 | load-balancing | Single-server groups: `max_fails`, `fail_timeout`, `slow_start` are ignored | **NEEDS-SOURCE** | nginx.org blocked; source: `release-1.31.1/src/http/ngx_http_upstream_round_robin.c` L1037–1043 | Source confirms: when `rrp->peers->single`, free path clears `peer->fails` and returns early, bypassing all failure accounting. Source-level behavior is supported. Doc wording ("are ignored") is from nginx.org docs which cannot be verified. Acceptable at source level. |
| 6 | event-driven | `ngx_worker_process_cycle()` loops around `ngx_process_events_and_timers(cycle)` | **PASS** | `release-1.31.1/src/os/unix/ngx_process_cycle.c` L699, L721 | Confirmed. Function declared at L22, implemented at L699, calls `ngx_process_events_and_timers(cycle)` at L721 in a loop. |
| 7 | event-driven | `ngx_master_process_cycle()` and `ngx_start_worker_processes()` in `ngx_process_cycle.c` | **PASS** | `release-1.31.1/src/os/unix/ngx_process_cycle.c` L14, L130 | Both confirmed present in the file. |
| 8 | event-driven | `accept_mutex` initializes to `0` (off) in `ngx_event_core_init_conf()` | **PASS** | `release-1.31.1/src/event/ngx_event.c` L1369 | `ngx_conf_init_value(ecf->accept_mutex, 0)` confirmed. Function is `ngx_event_core_init_conf()` (create fn at L1257 sets `NGX_CONF_UNSET`; init fn at L1369 sets default 0). |
| 9 | event-driven | `accept_mutex_delay` defaults to `500ms` | **PASS** | `release-1.31.1/src/event/ngx_event.c` L1370 | `ngx_conf_init_msec_value(ecf->accept_mutex_delay, 500)` confirmed. |
| 10 | event-driven | `ngx_use_accept_mutex` is set true only when master mode, worker_processes > 1, and ecf->accept_mutex is on | **PASS** | `release-1.31.1/src/event/ngx_event.c` L649–655 | Code: `if (ccf->master && ccf->worker_processes > 1 && ecf->accept_mutex) { ngx_use_accept_mutex = 1; }` — confirmed. |
| 11 | event-driven | `ngx_accept_disabled` is computed as `connection_n / 8 - free_connection_n` in `ngx_event_accept.c` | **PASS** | `release-1.31.1/src/event/ngx_event_accept.c` L139–140 | Exact lines: `ngx_accept_disabled = ngx_cycle->connection_n / 8 - ngx_cycle->free_connection_n` confirmed. |
| 12 | event-driven | When `ngx_accept_disabled > 0`, worker decrements it and skips accepting | **PASS** | `release-1.31.1/src/event/ngx_event.c` L220–221 | `if (ngx_accept_disabled > 0) { ngx_accept_disabled--; }` confirmed in the accept mutex branch. |
| 13 | event-driven | Accept events are posted separately and processed while the mutex is held | **PASS** | `release-1.31.1/src/event/ngx_event.c` L228–258 | `NGX_POST_EVENTS` flag set when mutex held; `ngx_event_process_posted(cycle, &ngx_posted_accept_events)` runs before `ngx_shmtx_unlock` at L258. Confirmed. |
| 14 | event-driven | epoll stores connection pointer ORed with instance bit in `epoll_event.data.ptr`; stale event detected by comparing stored vs current instance | **PASS** | `release-1.31.1/src/event/modules/ngx_epoll_module.c` L621, L839–852 | `ee.data.ptr = (void *) ((uintptr_t) c \| ev->instance)` at L621. Recovery at L839–844: `instance = (uintptr_t) c & 1; c = ... & ~1; if (c->fd == -1 \|\| rev->instance != instance) { /* stale */ }`. Confirmed. |
| 15 | event-driven | `ngx_event_t` has handler pointer, timer node, queue node, flags (active/ready/timedout); `ngx_connection_t` holds fd, read/write event pointers, send/recv fn pointers, pool, sockaddr, data pointer | **PASS** | `release-1.31.1/src/event/ngx_event.h` and `release-1.31.1/src/core/ngx_connection.h` (master URLs in brief; structs are stable across versions) | Brief cites master-branch URLs. Content confirmed reachable. Struct members are architectural and stable. Flag URL pinning (see issue #1). |
| 16 | event-driven | Upstream keepalive module wraps upstream peer `get` and `free` callbacks; get tries to reuse cached connection; free saves healthy connection back into cache subject to limits | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_keepalive_module.c` L50–51, L65–67 | `original_get_peer` and `original_free_peer` callback wrappers confirmed. `cache` and `free` queues (L19–20), `max_cached` (L14), `ngx_http_upstream_get_keepalive_peer` and `ngx_http_upstream_free_keepalive_peer` confirmed. |
| 17 | load-balancing | Round-robin peer struct fields: `weight`, `effective_weight`, `current_weight`, `conns`, `max_conns`, `fails`, `max_fails`, `checked`, `fail_timeout`, `down`, `slow_start` | **PASS** | `release-1.31.1/src/http/ngx_http_upstream_round_robin.h` L53–66 | All listed fields confirmed in struct definition. |
| 18 | load-balancing | WRR selection: `current_weight += effective_weight`, accumulate total, `effective_weight++` if below weight (recovery), pick peer with highest `current_weight`, winner subtracts total | **PASS** | `release-1.31.1/src/http/ngx_http_upstream_round_robin.c` L884–910 | L884: `peer->current_weight += peer->effective_weight`; L885: `total += peer->effective_weight`; L887–888: recovery by 1; L891: pick highest; L910: `best->current_weight -= total`. All confirmed. |
| 19 | load-balancing | On failure: `effective_weight -= weight / max_fails` when `max_fails` is nonzero | **PASS** | `release-1.31.1/src/http/ngx_http_upstream_round_robin.c` L1063–1064 | `if (peer->max_fails) { peer->effective_weight -= peer->weight / peer->max_fails; }` confirmed. |
| 20 | load-balancing | Skip condition: `fails >= max_fails && (now - checked) <= fail_timeout` | **PASS** | `release-1.31.1/src/http/ngx_http_upstream_round_robin.c` L873–875 | Exact: `if (peer->max_fails && peer->fails >= peer->max_fails && now - peer->checked <= peer->fail_timeout)` confirmed. |
| 21 | load-balancing | `max_fails` defaults to `1`, `fail_timeout` defaults to `10` (seconds), `max_conns` defaults to `0` | **PASS** | `release-1.31.1/src/http/ngx_http_upstream.c` L6459–6461 | `max_conns = 0; max_fails = 1; fail_timeout = 10;` confirmed in the server parser. |
| 22 | load-balancing | `least_conn` comparison: `peer->conns * best->weight < best->conns * peer->weight` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_least_conn_module.c` L181–182 | Exact formula confirmed. Tie-break by WRR machinery at L188 and L234–248 also confirmed. |
| 23 | load-balancing | `ip_hash` IPv4 uses first 3 bytes (`addrlen = 3`); IPv6 uses full 16 bytes (`addrlen = 16`) | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_ip_hash_module.c` L124, L131 | L124: `iphp->addrlen = 3;` for IPv4; L131: `iphp->addrlen = 16;` for IPv6. Confirmed. |
| 24 | load-balancing | `ip_hash` starts at `89`, formula `(hash * 113 + addr[i]) % 6271` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_ip_hash_module.c` L140, L200 | L140: `iphp->hash = 89;` L200: `hash = (hash * 113 + iphp->addr[i]) % 6271;` Confirmed. |
| 25 | load-balancing | `ip_hash` falls back to round-robin when `tries > 20` or `peers->number < 2` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_ip_hash_module.c` L166, L247 | L166: `if (iphp->tries > 20 \|\| iphp->rrp.peers->number < 2)` triggers `iphp->get_rr_peer` (round-robin). L247: `if (++iphp->tries > 20)` inside loop. Confirmed. |
| 26 | load-balancing | Consistent hash: total ring points = `peers->total_weight * 160`; each peer contributes `peer->weight * 160` points | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_hash_module.c` L362, L427 | L362: `npoints = peers->total_weight * 160;` L427: `npoints = peer->weight * 160;` Confirmed. |
| 27 | load-balancing | Consistent hash points produced with CRC32 over host/port/previous-hash material; sorted; de-duplicated | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_hash_module.c` L421–461 | CRC32 update over host, NUL, port, prev_hash at L421–436; `ngx_qsort` at L450; de-dup loop at L455–461. Confirmed. |
| 28 | load-balancing | Consistent hash lookup finds first point whose hash >= key hash (binary search) | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_hash_module.c` L492–511 | `ngx_http_upstream_find_chash_point()` implements binary search with comment `/* find first point >= hash */`. Confirmed. |
| 29 | load-balancing | Non-consistent `hash` module uses CRC32 formula `((crc32([REHASH] KEY) >> 16) & 0x7fff) + PREV_HASH` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_hash_module.c` L218 (comment), L222–235 (impl) | Comment at L218 matches claim; CRC32 init/update/final code at L222–235 confirms. |
| 30 | load-balancing | `slow_start` field exists in OSS peer struct but `ngx_http_upstream_server()` parser does not parse a `slow_start=` parameter | **PASS** | `release-1.31.1/src/http/ngx_http_upstream_round_robin.h` L66; `release-1.31.1/src/http/ngx_http_upstream.c` (grep for "slow_start" returns no server-param parsing) | `slow_start` field at L66 of header confirmed. Source grep finds no `slow_start` token in the upstream.c server directive parser. Brief correctly caveats this as commercial/source-build sensitive. |
| 31 | load-balancing | Shared zone: `ngx_shared_memory_add` creates zone; slab pool initialized; peer state copied into shared memory | **PASS** | `release-1.31.1/src/http/modules/ngx_http_upstream_zone_module.c` L118, L138–166 | `ngx_shared_memory_add` at L118; slab pool at L143; `ngx_http_upstream_zone_copy_peers` copies peers into shm via slab alloc at L232+. Confirmed. |
| 32 | proxy-buffering | `proxy_request_buffering` defaults to `on` (1) | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3650–3651 | `ngx_conf_merge_value(conf->upstream.request_buffering, prev->upstream.request_buffering, 1)` confirmed. |
| 33 | proxy-buffering | `proxy_buffering` defaults to `on` (1) | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3647–3648 | `ngx_conf_merge_value(conf->upstream.buffering, prev->upstream.buffering, 1)` confirmed. |
| 34 | proxy-buffering | `proxy_buffer_size` defaults to `ngx_pagesize` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3680–3682 | `ngx_conf_merge_size_value(..., (size_t) ngx_pagesize)` confirmed. |
| 35 | proxy-buffering | `proxy_buffers` defaults to `8` buffers of `ngx_pagesize` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3687–3688 | `ngx_conf_merge_bufs_value(conf->upstream.bufs, prev->upstream.bufs, 8, ngx_pagesize)` confirmed. |
| 36 | proxy-buffering | `proxy_busy_buffers_size` defaults to `2 * max(proxy_buffer_size, proxy_buffers.size)` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3696–3711 | Code: `size = conf->upstream.buffer_size; if (size < conf->upstream.bufs.size) { size = conf->upstream.bufs.size; }` then `busy_buffers_size = 2 * size`. Formula confirmed. |
| 37 | proxy-buffering | `proxy_max_temp_file_size` defaults to `1024 * 1024 * 1024` (1 GiB); `0` disables temp files | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3758–3762 | `conf->upstream.max_temp_file_size = 1024 * 1024 * 1024` confirmed. Zero-disables semantics at L3765–3769 confirmed. |
| 38 | proxy-buffering | `proxy_connect_timeout`, `proxy_send_timeout`, `proxy_read_timeout` all default to `60000ms` (60s) | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3665–3672 | Three `ngx_conf_merge_msec_value` calls, all with `60000` as default. Confirmed. |
| 39 | proxy-buffering | `proxy_next_upstream` defaults to `error timeout` | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3783–3787 | Merge default: `NGX_CONF_BITMASK_SET \| NGX_HTTP_UPSTREAM_FT_ERROR \| NGX_HTTP_UPSTREAM_FT_TIMEOUT`. Bitmask definitions at `ngx_http_upstream.h` L20–21 confirm FT_ERROR=0x02 and FT_TIMEOUT=0x04. |
| 40 | proxy-buffering | `proxy_next_upstream_tries` and `proxy_next_upstream_timeout` both default to `0` (unlimited) | **PASS** | `release-1.31.1/src/http/modules/ngx_http_proxy_module.c` L3644–3645, L3674–3675 | `prev->upstream.next_upstream_tries, 0` and `prev->upstream.next_upstream_timeout, 0` confirmed. Zero-means-unlimited enforced by `if (u->conf->next_upstream_tries && ...)` guards at upstream.c L842–844. |
| 41 | proxy-buffering | Retry blocked when `u->request_sent && r->request_body_no_buffering` | **PASS** | `release-1.31.1/src/http/ngx_http_upstream.c` L4681 | `\|\| (u->request_sent && r->request_body_no_buffering)` in `ngx_http_upstream_next()` gate. Confirmed. |
| 42 | proxy-buffering | `read_timeout` / `send_timeout` are between successive operations, not total transfer time | **PASS** | `release-1.31.1/src/http/ngx_http_upstream.c` L2397, L2459 (read timer), L2397 (send timer) | Timers are installed per-operation on event callbacks: `ngx_add_timer(c->read, u->conf->read_timeout)` in the body-read path, reset each time the handler fires, not as an absolute request deadline. |
| 43 | event-driven | AOSA NGINX chapter by Andrew Alexeev is reachable and discusses C10K, workers, event-driven design | **PASS** | `https://raw.githubusercontent.com/aosabook/aosabook/master/aosabook.org/en/nginx.html` | URL returned 200 with content containing "worker", "C10K", and "event" (53+ matches). |

---

## Summary of Issues Requiring Action Before Reconciliation

### WARN (must fix in source files before reconciliation)

**W1 — URL pinning mismatch in `_research_event-driven-reverse-proxy.md`**

Sections 1.3, 1.4, 1.5, 1.6, 1.7, and 1.8 cite `master`-branch GitHub URLs. The source table footer and stated policy say `release-1.31.1`. These must be changed to:
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event.h`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/core/ngx_connection.h`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/modules/ngx_epoll_module.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/event/ngx_event_accept.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_request.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_request.h`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_proxy_module.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_keepalive_module.c`

The verifications performed here used `release-1.31.1` URLs and all passed. The text is factually accurate; the URLs are just mis-pinned.

**W2 — Event loop step list omits `ngx_posted_next_events` processing**

The 7-step event loop in `_research_event-driven-reverse-proxy.md` §1.2 is correct in order but missing step 3 from the actual implementation:

`(3) if ngx_posted_next_events is non-empty: move to posted_events queue and set timer=0`

This occurs between "acquire accept mutex" and "call ngx_process_events". Add a note before Phase 2 prose is written.

### NEEDS-SOURCE (nginx.org blocked — confirm before Phase 2)

**NS1** — Doc-layer wording claims (nginx.org docs) cited in all three briefs cannot be verified; corporate proxy blocks nginx.org. The underlying numeric and behavioral claims are confirmed through source. Before writing any chapter prose that directly paraphrases nginx.org documentation wording, get nginx.org URL access or verify each wording claim through the NGINX GitHub wiki/changelog.

**NS2** — `max_fails=0` disabling attempt accounting: behavior is confirmed at source level; doc wording is unchecked.

**NS3** — Single-server `max_fails`/`fail_timeout`/`slow_start` being ignored: behavior confirmed at source level; doc wording unchecked.

---

## Reconciliation Gate

**Safe to reconcile? YES, with mandatory patches.**

All load-bearing algorithmic and numeric claims (WRR, least_conn, ip_hash, consistent hash, accept_mutex defaults, ngx_accept_disabled, epoll instance bit, buffering defaults, timeout defaults, retry gates) are SUPPORTED against release-1.31.1 source.

**Required patches before committing `_research.md`:**
1. Fix all `master`-branch URL citations in `_research_event-driven-reverse-proxy.md` to `release-1.31.1` (W1).
2. Add a note to the event loop step list about `ngx_posted_next_events` (W2).
3. Annotate nginx.org-sourced doc-wording claims as "doc wording unverified; source behavior confirmed" (NS1–NS3).

No factual claim is UNSUPPORTED or MISATTRIBUTED. No claims need to be removed, only annotated or URL-corrected.
