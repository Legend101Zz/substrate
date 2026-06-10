# 14 — data-modeling-partitioning-sharding — Cluster A: Data modeling

> **Phase 1 research brief (NO course prose).** Standard six sections. This cluster covers the
> *logical* layer: how you shape data before you decide where to put it. Partitioning/sharding
> (Cluster B) and cross-partition operations (Cluster C) are downstream of the choices made here.
>
> **Verification posture (network 6th-session reality):** only `lamport.azurewebsites.net` +
> Walmart artifactory resolve; arXiv/raw.github/research.google/ACM/allthingsdistributed =
> HTTP 000. So canonical/empirical *attributions* in this cluster are flagged
> `[UNVERIFIED from fetched source]`. The *mechanisms* are anchored by **reuse of already
> line-verified canon** from sub-courses 06 (B-trees/B+-trees, LSM, consistent hashing) and 11
> (replication, consistency models, atomic commit) — not re-fetched, cited as reuse.

---

## 1. Key mechanisms (how the thing actually works, deeply)

### 1.1 The data model is a contract between *access pattern* and *storage engine*

A data model is not "how the data looks" — it is the set of read/write operations you have
promised to make cheap. Every model is a bet about which queries dominate. The forcing function
underneath everything in this cluster:

> **You cannot optimize for all access patterns at once. A model that makes one query O(1) makes
> some other query O(n) or O(joins). Modeling is choosing which queries to privilege.**

The storage engine (verified in 06/07) sets the physics this bet plays out on:
- **B+-tree-backed engines** (06 `_research_indexes-lsm-bloom.md`; SQLite `btreeInt.h`, Postgres
  `nbtree/README`): read-optimized, in-place updates, sorted leaves → cheap range scans and
  ordered access; writes pay page splits + write amplification from random I/O.
- **LSM-tree-backed engines** (06; LevelDB `doc/impl.md`, RocksDB `options.h`/`dbformat.h`):
  write-optimized (sequential appends to memtable → SSTs), reads pay merge across levels +
  Bloom-filter probes; high write throughput, compaction-driven space/read amplification.

So "relational vs document vs wide-column vs KV" is partly a **data-model** question (logical
shape) and partly a **storage-engine** question (B-tree vs LSM). The two axes are independent:
e.g. a wide-column store (Cassandra) is LSM under the hood; a document store (Mongo/WiredTiger)
can be B-tree under the hood. **Teach the two axes separately** so learners stop conflating
"document database" with "fast writes."

### 1.2 The four logical models (what they make cheap)

**(a) Key–Value (KV).** The model is a dictionary: `get(k)`, `put(k,v)`, `delete(k)`. The value
is opaque to the store (no server-side query inside it). Cheap: point lookups by exact key,
horizontal partitioning (the key *is* the shard key — see Cluster B). Expensive/impossible:
querying by anything other than the key, range scans unless keys are ordered, server-side joins.
This is the substrate the other models are often built on. *(Redis/DynamoDB-style; reuse 08
cache canon for KV-as-cache.)*

**(b) Document.** The model is a collection of self-contained, nested, schema-flexible records
(JSON/BSON-ish). One document = one aggregate = (ideally) one read. Cheap: read/write a whole
entity in one I/O *when your access pattern matches the document boundary*; schema evolution
(fields vary per document). Expensive: queries that cut *across* documents (many-to-many,
"all orders containing product X"), and updates to data duplicated across many documents.
The central design act is **choosing the aggregate boundary** — what goes inside one document
vs. what is referenced by id.

**(c) Wide-column (column-family / "Bigtable-style").** The model is a sparse, distributed,
sorted map: `(row key, column family, column qualifier, timestamp) → value`. Rows are
partitioned by row key; *within* a row, columns are stored sorted and contiguously by column
family. Cheap: huge tables, writes (LSM), range scans over row keys, reading a column family.
The model deliberately fuses logical shape with the physical partition+sort order — you model
**by query**, laying out the row key and clustering columns so the answer is a single
contiguous slice. `[UNVERIFIED from fetched source]` Bigtable (Chang et al., OSDI 2006),
Cassandra data model — network-blocked; see 12 carried-forward storage-trilogy gap.

**(d) Relational.** The model is sets of tuples (relations) with a declared schema, related by
*values* (foreign keys), queried by a declarative algebra (the relational algebra / SQL). The
engine — not the application — chooses how to satisfy a query (the optimizer; see 07
`_research_optimizer-external-exec.md`). Cheap: ad-hoc queries you *didn't* anticipate, joins
across normalized entities, integrity constraints. Expensive: scaling writes horizontally once
joins/constraints span shards (the whole reason Cluster C and sub-course 15 exist).
`[UNVERIFIED from fetched source]` Codd "A Relational Model of Data for Large Shared Data Banks"
(CACM 1970) — network-blocked.

> **The unifying lens:** relational normalizes so facts live once and are *joined* at read time;
> the other three tend to **pre-join by embedding/duplication** so a read is a single fetch.
> That is the read/write tradeoff (§1.4) restated as a modeling choice.

### 1.3 Normalization vs denormalization

**Normalization** = store every fact exactly once; relate by key. The classic forcing function
is eliminating **update/insert/delete anomalies**: if a fact is duplicated in N rows, an update
must touch all N atomically or the data lies. Normal forms (1NF→2NF→3NF→BCNF) are progressively
stronger statements of "every non-key attribute depends on *the key, the whole key, and nothing
but the key*." `[UNVERIFIED from fetched source]` Codd's normal-form papers + Kent "A Simple
Guide to Five Normal Forms" (CACM 1983) — network-blocked.

- **Benefit:** writes are cheap and safe (one place to change), storage is minimal, integrity is
  structural.
- **Cost:** reads must *reassemble* the entity by joining — and joins are exactly what does not
  scale across shards (Cluster C / 15).

**Denormalization** = deliberately duplicate facts (or pre-compute joins / materialized views)
to make a hot read a single fetch.

- **Benefit:** the dominant read becomes O(1) fetch, no join, partition-local.
- **Cost:** every duplicated copy is now a *consistency obligation* on write — you must fan out
  the update (sync or async), and between fan-out steps the copies disagree. **Denormalization
  converts a read-time join cost into a write-time consistency cost** — which is why it hands off
  directly to replication/consistency (11, 15) and async fan-out (17).

This is not "normalize good / denormalize bad." It is: **normalize until reads hurt, then
denormalize the specific hot path, and pay the write-side consistency tax with eyes open.**

### 1.4 Access-pattern-driven modeling and the read/write tradeoff

The discipline that ties §1.2–1.3 together, especially for non-relational stores:

1. **Enumerate access patterns first** (the queries + their rates + their latency SLOs), *then*
   design the schema to serve them — the inverse of the relational habit of modeling entities
   first and querying later. In KV/wide-column/single-table designs the schema is literally
   "what shape makes my known queries a single partition-local fetch."
2. **The read/write tradeoff is conservation, not preference.** Work doesn't vanish; it moves in
   time. You either:
   - **pay at read time** (normalized: join/aggregate on every read), or
   - **pay at write time** (denormalized/materialized: do the join/aggregate once on write and
     store the result), or
   - **pay at a third time** (async/batch: precompute via a stream/job — handoff to 17/19).
   Choose where to pay based on the **read:write ratio** and the **latency SLO** of each side.
   A 1000:1 read-heavy feed wants the cost on the rare write; a write-heavy ledger does not.

This is the *same* "where do you pay" reasoning as 13's capacity loop — just applied to a single
record's cost instead of a whole tier's throughput.

### 1.5 Schema-on-write vs schema-on-read

- **Schema-on-write** (relational, and document stores with validators): the schema is enforced
  when data goes in; readers can assume structure. Cost: migrations are explicit events.
- **Schema-on-read** (document by default, KV, raw event logs): writers store whatever; readers
  interpret. Cost: every reader must tolerate every historical shape; "the schema" is an
  emergent property of all the code that reads. Useful for heterogeneous/evolving data; dangerous
  as the only contract. Relevant to evolvability (handoff to 17's event schemas, and to
  forward/backward-compatible encodings — Avro/Protobuf/Thrift). `[UNVERIFIED from fetched
  source]` exact encoding-evolution rules — network-blocked.

## 2. Foundational sources

**Verified by reuse (line-checked in earlier sub-courses — NOT re-fetched this session):**
- B+-tree / B-tree mechanics, sorted leaves, range scans, page splits, write amplification —
  06 `_research_indexes-lsm-bloom.md` (SQLite `btreeInt.h`, Postgres `nbtree/README`).
- LSM mechanics (memtable→SST, level compaction, Bloom-filter read path, write/read/space
  amplification) — 06 `_research_indexes-lsm-bloom.md` (LevelDB `doc/impl.md`,
  `doc/table_format.md`, `util/bloom.cc`; RocksDB `options.h`, `dbformat.h`, `util/bloom_impl.h`).
- Relational query execution + the optimizer choosing access paths (so "the engine decides how
  to join," not the app) — 07 `_research_storage-query-exec.md`, `_research_optimizer-external-exec.md`.
- KV-as-cache semantics, eviction, stampede — 08 `_research.md`.

**Blocked primaries — `[UNVERIFIED from fetched source]`, carried forward (fetch when network heals):**
- Codd, "A Relational Model of Data for Large Shared Data Banks" (CACM 1970); Codd normal-form
  papers; Kent, "A Simple Guide to Five Normal Forms" (CACM 1983).
- Chang et al., "Bigtable: A Distributed Storage System for Structured Data" (OSDI 2006) — the
  wide-column / sparse-sorted-map model (also on 12's carried-forward storage-trilogy list).
- DeCandia et al., "Dynamo" (SOSP 2007) — KV model + the consistency side (shared with 11/Cluster C).
- Encoding-evolution canon: Protocol Buffers / Apache Avro / Thrift schema-evolution docs;
  Kleppmann *Designing Data-Intensive Applications* ch.2–3 (models) for the synthesis framing.

## 3. "Why it's this way" — the forcing functions

- **No model is free across all queries** because storage is laid out one way at a time; sorting
  for one access order de-sorts another. Modeling is allocating that single layout to the
  dominant query.
- **Normalization exists to make a fact have one home** so a write is atomic by construction;
  the moment you duplicate, atomicity becomes a distributed-write problem (11/15).
- **Denormalization exists because joins don't partition** — a read-time join across shards is a
  scatter-gather (Cluster C); pre-joining on write keeps the hot read partition-local.
- **Access-pattern-first modeling exists because non-relational stores have no optimizer** to
  rescue an un-anticipated query — if you didn't lay out the data for it, it's a full scan.
- **The read/write tradeoff is conservation:** the join/aggregate work is invariant; you only
  choose *when* to pay it (read time, write time, or async precompute).

## 4. Common misconceptions to preempt

- "Document/NoSQL = no schema." No — it's schema-on-read; the schema moved into every reader.
- "NoSQL is faster than SQL." Category error: the storage engine (B-tree vs LSM) drives
  write/read speed, not the logical model; many "NoSQL" stores are LSM and many SQL stores can be.
- "Normalize fully, always (or denormalize, always)." Neither — normalize for write integrity,
  denormalize the specific hot read, and pay the consistency tax deliberately.
- "Denormalization just costs disk." No — it costs **write-time consistency**: every copy is an
  update-fan-out obligation, and copies disagree between steps.
- "Joins are a relational feature you lose in NoSQL." You don't lose the *need* to join; you
  relocate it — either pre-join on write (embed/duplicate) or do it in the app (scatter-gather).
- "Pick the data model first." Pick the **access patterns** first; the model falls out of them.
- "Wide-column is just relational with flexible columns." No — its row key *is* the partition +
  sort order; you model physically by query, not logically by entity.

## 5. Best build-your-own target(s)

- **Model-the-same-domain-four-ways lab:** take one domain (e.g. an orders system) and express
  it as relational (normalized), document (aggregate-embedded), wide-column (query-first row
  keys), and KV; enumerate the access patterns and show which query each model makes O(1) vs
  O(scan). The connective tissue into Cluster B (where do these keys shard) and 21 (case studies).
- **Read/write-tradeoff simulator:** same workload, normalized vs denormalized; measure read
  cost (joins) vs write cost (fan-out + inconsistency window). Pairs with 13's capacity loop.
- **Normal-form anomaly demo:** construct an un-normalized table, trigger an update anomaly, show
  3NF/BCNF removing it; then denormalize one hot read and show the re-introduced write obligation.

## 6. Open questions / gaps to close (preserved verbatim in intent)

- **All canonical model attributions are network-blocked** `[UNVERIFIED]`: Codd 1970 + normal
  forms, Kent 1983, Bigtable OSDI 2006, Dynamo SOSP 2007, Avro/Protobuf/Thrift evolution rules,
  Kleppmann DDIA ch.2–3. Teach mechanisms now (anchored by reused 06/07/08 canon); do NOT harden
  exact historical wording/dates into Phase-2 prose until fetched.
- **Disagreement to resolve with sources:** "aggregate boundary" framing (DDD/Evans + DDIA)
  vs. classic normalization — they are reconcilable but use different vocabulary; pin both.
- **Boundary discipline (cross-link, do NOT duplicate):**
  - storage-engine physics (B-tree/LSM/Bloom) live in **06**; this cluster *uses* them.
  - relational query execution / the optimizer lives in **07**; this cluster only states "the
    engine chooses the plan."
  - the write-side consistency tax of denormalization hands off to **11/15** (replication,
    consistency) and **17** (async fan-out / CDC / materialized views).
  - *where* a chosen key physically lands is **Cluster B** (partitioning/sharding); *operations
    that span those partitions* are **Cluster C**.
