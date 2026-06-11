# Opportunistic primary fetches — 2026-06-10 (session: 18 + network heal wave)

Network healed substantially this session (`research.google` mirrors via
`static.googleusercontent.com`, `usenix.org/legacy`, `allthingsdistributed.com`, `sre.google`,
`rfc-editor.org`, `lamport.azurewebsites.net` all HTTP 200). Fetched + extracted (pypdf in a
throwaway `uv` venv, since no `pdftotext`) the long-blocked canon. Receipts saved as
`<name>.pdf` + `<name>.txt` in `meta/fetched_primaries/`. This file records the verbatim
claims confirmed and which carried-forward `[UNVERIFIED]` flags they upgrade.

## New primaries verified this session

### 1. Dean & Barroso, "The Tail at Scale," CACM 2013 (`tail-at-scale-cacm2013.{pdf,txt}`)
*(slide-deck/preprint form of the CACM article; figures + speaker notes)*
- **VERIFIED:** fan-out tail — "Server with 1 ms avg. but 1 sec 99%ile latency – touch 1 of
  these: 1% of requests take ≥1 sec – touch 100 of these: **63% of requests take ≥1 sec**."
  (= `1 − 0.99^100 = 0.634`, already recomputed in 13.)
- **VERIFIED:** **backup requests** (= hedged requests) and **backup requests w/ cancellation**
  (= tied requests) as within-request latency-tolerating techniques; cross-request techniques =
  load balancing, micro-partitioning, selective replication; differentiated service classes +
  prioritized queues; break large requests into small ones to reduce head-of-line blocking.
- **VERIFIED (Backup Requests Effects table):** No backups → 99.9%ile **994 ms**; Backup after
  10 ms → 99.9%ile **50 ms**; Backup after 50 ms → 99.9%ile **68 ms** (i.e. a tiny extra load
  collapses the tail).
- **Upgrades:** **13** tail/fan-out + hedged/tied attribution; **18D** hedged/tied requests;
  **20** (Tail-at-Scale is its headline paper — pre-cleared); **12** canon walkthrough.

### 2. DeCandia et al., "Dynamo: Amazon's Highly Available Key-value Store," SOSP 2007 (`dynamo-sosp2007.{pdf,txt}`)
- **VERIFIED verbatim:** "Setting R and W such that **R + W > N** yields a quorum-like system…
  the latency of a get (or put) is dictated by the slowest of the R (or W) replicas." (= the
  quorum-overlap claim 15 recomputed and carried `[UNVERIFIED]`.)
- **VERIFIED (terms present):** consistent hashing, virtual nodes, vector clocks, sloppy quorum,
  hinted handoff, Merkle trees (anti-entropy), read repair, gossip membership.
- **Upgrades:** **15** (leaderless quorum `W+R>N`, sloppy quorum, hinted handoff, Merkle
  anti-entropy, read repair, sibling vector clocks); **14**/**06** (consistent hashing + virtual
  nodes); **11** (Dynamo as the AP/eventual-consistency exemplar); **12** canon.

### 3. Dean & Ghemawat, "MapReduce," OSDI 2004 (`mapreduce-osdi04.{pdf,txt}`)
- **VERIFIED (terms present):** map/reduce model, master/worker, **re-execution** on failure,
  input **locality** optimization, **straggler** problem + **backup tasks** (the same
  tail-mitigation idea as Tail-at-Scale's backup requests).
- **Upgrades:** **14** (MapReduce attribution, scatter-gather lineage); **12** canon; **13**
  (straggler/backup-task = tail).

### 4. Chang et al., "Bigtable," OSDI 2006 (`bigtable-osdi06.{pdf,txt}`)
- **VERIFIED (terms present):** SSTable, tablet, GFS, Chubby, column family, minor compaction,
  commit log. (= the wide-column + LSM lineage 14/06/08 reuse.)
- **Upgrades:** **14** (wide-column model, Bigtable attribution); **06**/**08** (SSTable/LSM/
  compaction); **12** canon.

### 5. Ghemawat, Gobioff & Leung, "The Google File System," SOSP 2003 (`gfs-sosp2003.{pdf,txt}`)
- **VERIFIED (terms present):** chunk, master, **64 MB** chunk size, replicas, lease, primary
  replica.
- **Upgrades:** **12** canon; supports 14/15 replication-placement context.

### 6. Corbett et al., "Spanner," OSDI 2012 (`spanner-osdi2012.{pdf,txt}`)
- **VERIFIED (terms present):** TrueTime, commit wait, Paxos, external consistency, uncertainty
  interval, `TT.now()`.
- **Upgrades:** **15** (Spanner externally-consistent topology, commit-wait); **11** (TrueTime as
  the bounded-clock-uncertainty answer to ordering); **14** (re-pin Spanner); **12** canon.

## Still blocked this session (carry forward `[UNVERIFIED]`)
- **SEDA** (Welsh SOSP 2001) — Harvard `eecs.harvard.edu` + `usenix.org` (non-legacy) 000.
- **CoDel** (Nichols & Jacobson, ACM Queue 2012) — `queue.acm.org` 403.
- AWS Builders' Library (timeouts/backoff-jitter) — `aws.amazon.com` 000.
- Netflix Hystrix / concurrency-limits, resilience4j, Envoy knobs — not attempted (vendor docs).
- CAP/PACELC primaries (Gilbert-Lynch 2002, Brewer, Abadi 2012), Herlihy-Wing TOPLAS 1990,
  Bayou session guarantees, CRDT papers, Keshav CCR 2007, Codd CACM 1970, Kafka paper/KIPs,
  Postgres/MySQL/Mongo/Cassandra/etc. vendor docs — not attempted this session.

## Method note
Extraction used `pypdf` 6.13.1 in a disposable `uv` venv at `/tmp/pdfvenv` (installed from the
Walmart Artifactory mirror), then removed. The `.txt` files are the extracted text receipts;
the `.pdf` files are the originals. No system Python packages were modified;
`/Users/m0t0hu6/.code-puppy-venv` was not touched.
