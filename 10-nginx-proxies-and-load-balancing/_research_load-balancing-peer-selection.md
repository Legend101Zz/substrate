# Research Brief — Sub-course 10: NGINX Load Balancing and Peer Selection
## Source cluster: upstream peer algorithms, shared state, passive failure accounting
## Researcher: brain manual primary-source pass | Date: 2026-06-10

Status: drafted from NGINX `release-1.31.1` source and official NGINX docs. Factchecker spot-check found no
unsupported algorithmic/source claims; nginx.org doc wording was blocked in the factchecker environment, so doc-only
wording must be reverified before Phase 2 prose.

---

## 1. Key Mechanisms

### 1.1 The default upstream balancer is weighted round-robin, not naive modulo

When no explicit upstream method such as `least_conn`, `ip_hash`, or `hash` is configured, NGINX initializes the
round-robin upstream peer machinery. Each upstream peer carries:

- `weight` — configured static weight,
- `effective_weight` — mutable penalty/recovery weight,
- `current_weight` — accumulator used to choose the next peer,
- `conns`, `max_conns`,
- `fails`, `max_fails`, `checked`, `fail_timeout`,
- `down`, plus optional shared-zone fields.

Primary source: NGINX `release-1.31.1`
`src/http/ngx_http_upstream_round_robin.h` and `src/http/ngx_http_upstream_round_robin.c`.

The selection loop in `ngx_http_upstream_get_peer()` skips peers that are administratively down, recently exceeded
`max_fails` within `fail_timeout`, or exceed `max_conns`. For eligible peers, it adds `effective_weight` into
`current_weight`, accumulates total effective weight, slowly increments `effective_weight` back toward `weight`, and
selects the peer with highest `current_weight`; the winner then subtracts the total. That is the classic smooth
weighted round-robin shape.

Why this matters: weighted round-robin gives proportional distribution without a huge pre-expanded list of server
entries. The mutable `effective_weight` lets failures reduce a peer's share and then recover gradually.

### 1.2 Failure accounting is passive by default: peer state changes on request outcomes

The `server` parser in `src/http/ngx_http_upstream.c` defaults `max_fails` to `1` and `fail_timeout` to `10` seconds
for upstream servers, unless overridden. Official NGINX docs describe `max_fails` as the number of unsuccessful
attempts during `fail_timeout`, and `fail_timeout` as both the failure-count window and the period the server is
considered unavailable. Factchecker note: nginx.org wording was blocked in the factchecker environment; source-level
behavior was confirmed in `release-1.31.1`.

When an upstream attempt fails, `ngx_http_upstream_next()` calls the peer `free` callback with a failed state.
Round-robin free logic increments `peer->fails`, updates `peer->checked`, and reduces `effective_weight` by roughly
`weight / max_fails` when `max_fails` is nonzero. Later selection skips that peer while
`fails >= max_fails && now - checked <= fail_timeout`.

Important caveats:
- `max_fails=0` disables this attempt accounting at source level: the skip and penalty conditions are gated by
  `peer->max_fails`. The equivalent nginx.org wording needs recheck before Phase 2 prose.
- If there is only one server in a group, source confirms the free path clears `peer->fails` and returns early;
  nginx.org doc wording saying `max_fails`, `fail_timeout`, and `slow_start` are ignored needs recheck before Phase 2 prose.
- Active periodic health checks are not the same mechanism; official NGINX docs mark dynamic groups with periodic
  health checks as part of the commercial subscription.

Primary sources:
- `https://nginx.org/en/docs/http/ngx_http_upstream_module.html`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream_round_robin.c`

### 1.3 `least_conn` chooses by active-connection ratio, with weight as a tie/normalizer

The `least_conn` module installs `ngx_http_upstream_get_least_conn_peer()` as the peer getter. It skips the same
classes of unavailable peers as round-robin, but compares active connections normalized by weight:

- candidate is better when `peer->conns * best->weight < best->conns * peer->weight`,
- if the weighted active-connection ratio ties, it uses the same smooth-weight machinery (`current_weight`,
  `effective_weight`) to break ties among peers in that least-connection class.

Primary source: NGINX `release-1.31.1`
`src/http/modules/ngx_http_upstream_least_conn_module.c`.

Why this matters: least-connections targets long-lived or uneven request durations better than pure round-robin.
But it is still local to the state that NGINX can see. Without a shared upstream zone, per-worker counters are not a
global cluster truth; with a zone, runtime peer state can be shared in memory.

### 1.4 `ip_hash` is client-affinity hashing with fallback after too many misses

The `ip_hash` module keys on the client address:

- IPv4 uses the first three bytes of the address (`addrlen = 3`), preserving affinity across old class-C-ish client
  networks; IPv6 uses the full 16 bytes.
- The hash starts at `89` and repeatedly computes `hash = (hash * 113 + addr[i]) % 6271`, then maps into
  `total_weight`.
- It skips down/failed/full peers and, after more than 20 tries or fewer than two peers, falls back to round-robin.

Primary source: NGINX `release-1.31.1`
`src/http/modules/ngx_http_upstream_ip_hash_module.c`.

Misconception to preempt: `ip_hash` is not a session store. It is a deterministic routing heuristic. NAT, proxies,
IPv6 privacy addresses, and server changes can still alter effective affinity.

### 1.5 Generic `hash` and `hash ... consistent` are key-based peer selection

The generic `hash` upstream module computes a hash from a configured key expression. In non-consistent mode, source
comments show it uses `((crc32([REHASH] KEY) >> 16) & 0x7fff) + PREV_HASH`, then maps into total peer weight. It
rehashes to search for an available peer when the first choice is down/failed/full.

With `hash ... consistent`, NGINX builds a point ring:

- number of points is `peers->total_weight * 160`,
- each peer contributes `peer->weight * 160` points,
- points are produced with CRC32 over host/port/previous-hash material,
- points are sorted, de-duplicated, and lookup finds the first point whose hash is >= key hash.

Primary source: NGINX `release-1.31.1`
`src/http/modules/ngx_http_upstream_hash_module.c`; official docs describe the `consistent` parameter as ketama-style
consistent hashing and note it helps reduce key remapping when servers are added/removed.

### 1.6 Shared upstream zones move runtime peer state into shared memory

The `zone` directive is implemented in `src/http/modules/ngx_http_upstream_zone_module.c`. It creates a named shared
memory zone with `ngx_shared_memory_add`, initializes a slab pool, copies upstream peers into shared memory, and uses
zone-specific locks/config counters. The round-robin peer structs also include zone-only fields such as `rwlock`,
`config`, `resolve`, `zone_next`, per-peer locks, refs, and host pointers behind `NGX_HTTP_UPSTREAM_ZONE`.

Official docs say `zone name [size]` defines a shared memory zone that keeps the group's configuration and run-time
state shared between worker processes, and that several groups may share the same zone. Factchecker note: source-level
shared-memory behavior was confirmed; nginx.org wording should be reverified before Phase 2 prose.

Primary sources:
- `https://nginx.org/en/docs/http/ngx_http_upstream_module.html#zone`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_zone_module.c`
- `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream_round_robin.h`

Why this matters: without shared state, workers can independently believe different peers are healthy/busy because
each worker has its own process memory. Shared zones trade shared-memory locking and slab bookkeeping for more
consistent worker-visible upstream state.

### 1.7 `slow_start` is documented, but treat availability carefully

Official upstream docs document `slow_start=time` as gradually recovering a server's weight from zero after it
becomes healthy or after it becomes available following `fail_timeout`; default is zero. The same docs say the
parameter cannot be used with `hash`, `ip_hash`, or `random`, and the docs place `slow_start` among parameters
available as part of the commercial subscription. Factchecker note: nginx.org wording was blocked; the open-source
source-level caveat below was confirmed.

In open-source `release-1.31.1` source, the peer struct contains `slow_start` / `start_time` compatibility fields,
but the open-source `ngx_http_upstream_server()` parser path inspected here does not parse a `slow_start=` server
parameter. Therefore: cite `slow_start` as official/commercial documented behavior unless a specific deployment's
source build proves otherwise. Do not teach it as universally available OSS behavior.

---

## 2. Foundational Sources

| Mechanism | Primary source | Notes |
|---|---|---|
| Default weighted round-robin peer structs and selection | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream_round_robin.h`; `.../ngx_http_upstream_round_robin.c` | `weight`, `effective_weight`, `current_weight`, `fails`, `checked`, `conns` |
| Upstream `server` parsing/defaults | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/ngx_http_upstream.c` | defaults: `max_fails=1`, `fail_timeout=10`, `max_conns=0` |
| Official upstream directives | `https://nginx.org/en/docs/http/ngx_http_upstream_module.html` | directive semantics and commercial notes |
| Basic load-balancing guide | `https://nginx.org/en/docs/http/load_balancing.html` | high-level descriptions; use source for exact mechanics |
| `least_conn` | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_least_conn_module.c` | weighted connection ratio + WRR tie break |
| `ip_hash` | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_ip_hash_module.c` | IPv4 3-byte / IPv6 16-byte address hash |
| `hash` / consistent hash | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_hash_module.c` | CRC32, `weight * 160` points for consistent ring |
| Shared upstream zones | `https://raw.githubusercontent.com/nginx/nginx/release-1.31.1/src/http/modules/ngx_http_upstream_zone_module.c` | shared memory/slab copy of peer state |

---

## 3. Why It’s This Way — Forcing Constraints

- **Backend capacity is heterogeneous.** Weighted algorithms represent different server capacities without duplicating
  server entries into a giant list.
- **Workers are processes, not threads sharing a heap.** Shared upstream zones exist because the default master/worker
  process model otherwise fragments runtime counters across worker address spaces.
- **Failures should reduce traffic before a full outage is declared.** `effective_weight` penalties and
  `max_fails`/`fail_timeout` let failed attempts temporarily reduce or skip a peer.
- **Sticky routing is a cache/session optimization, not a correctness primitive.** `ip_hash`/`hash` can improve cache
  locality or affinity, but server churn and unavailable peers still require fallback.
- **Least-connections needs live counters.** It is useful for uneven request duration, but only as good as the current
  connection state NGINX can observe.

---

## 4. Common Misconceptions

1. **“Round-robin means equal traffic.”** Weighted round-robin is default; equal traffic only follows if weights and
   request durations are equal enough.
2. **“`least_conn` means global least connections.”** Without a shared zone, per-worker process state can diverge.
3. **“`ip_hash` guarantees sessions stick forever.”** It is deterministic routing, not session storage.
4. **“NGINX open source has active health checks by default.”** Passive failure accounting is in OSS source; active
   periodic health checks are documented as commercial.
5. **“`max_fails` permanently marks a server dead.”** It is bounded by `fail_timeout`; source and docs model this as
   temporary unavailability/accounting.
6. **“Consistent hashing means no keys move.”** It reduces remapping; adding/removing/downing peers still moves keys.
7. **“`slow_start` is always available.”** Docs list it, but availability is commercial/source-build sensitive; verify
   the deployed build before teaching operational config.

---

## 5. Build-Your-Own Targets

1. **Smooth weighted round-robin:** implement `weight`, `effective_weight`, `current_weight`, then simulate distribution.
2. **Passive health penalty:** on failed request, increment `fails`, set `checked`, reduce `effective_weight`, and skip
   during `fail_timeout`.
3. **Least-connections balancer:** compare `conns / weight` without floating point using cross multiplication.
4. **Client-affinity hash:** route by client key, add fallback after N failed probes, and observe churn when peers change.
5. **Consistent-hash ring:** create `weight * 160` virtual points per peer, sort, lookup first point >= key hash, and
   measure remapping when adding/removing peers.
6. **Shared-state simulation:** run multiple worker processes with independent counters, then add shared memory/IPC and
   show how behavior changes.

---

## 6. Open Questions / Gaps

- Factchecker passed the source-level algorithmic claims; nginx.org doc wording still needs recheck before Phase 2 prose.
- Trace `random` / `random two least_conn` only if Phase 2 wants broader NGINX upstream algorithm coverage; user plan did
  not require it for this session.
- Verify exact commercial/open-source boundary for `slow_start`, active health checks, sticky, queue, least_time in the
  deployment version before operational prose.
- Verify how dynamic DNS `resolve` interacts with upstream zones before teaching resolver-driven membership changes.
- Compare NGINX's consistent hash behavior against the original ketama/memcached source if the course wants historical
  lineage rather than just NGINX mechanics.
