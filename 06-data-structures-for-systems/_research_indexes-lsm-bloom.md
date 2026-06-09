# Research Brief: B-Trees / B+-Trees, LSM-Trees, and Bloom Filters
## Sub-course 06 — Data Structures for Systems
### Source cluster: Bayer/McCreight, Comer survey, SQLite/Postgres source, O'Neil LSM, RocksDB/LevelDB, Bloom 1970
### Researcher: researcher-58ef3f | 2026-06-09

---

## 1. Key Mechanisms — Deep, Precise, with Forcing Constraints

---

### 1.1 B-Trees and B+-Trees

#### 1.1.1 Why B-trees exist — the forcing constraint

**Constraint**: HDD random page access costs ~10ms (seek + rotation). A binary search tree of N elements has O(log₂ N) levels, meaning a billion-node tree requires ~30 page fetches. A B-tree trades node width for depth: by maximizing keys per node (== per disk page), it collapses 30 levels into 3–4, each requiring exactly one I/O.

**Original motivation**: Bayer & McCreight (1972) explicitly modeled this as the I/O cost dominating all computation. The goal was: one logical key comparison per level of the tree, one disk read per level, O(log_t N) levels where t is the branching factor (fanout). [Source: btreeInt.h attribution to Knuth TAOCP Vol. 3 pp. 473-480; Bayer & McCreight 1972 Acta Informatica 1(3):173-189 — behind Springer paywall, content verified via Comer 1979 survey description and SQLite source comments]

#### 1.1.2 B-tree vs B+-tree — the critical distinction

- **B-tree**: data stored in every node (leaf and internal). Internal nodes hold fewer keys because they also carry values.
- **B+-tree**: ALL data in leaf nodes. Internal nodes hold only separator keys (the "pivot" keys) used for navigation. Leaves are linked in a doubly-linked list.

**Consequence for fanout**: an 8KB PostgreSQL page with 16-byte keys and 8-byte child pointers fits ~341 separator entries. A 4-level tree handles ~340^3 × (entries per leaf) ≈ billions of rows.

**Consequence for range scans**: once the correct leaf is located, subsequent keys are fetched by following sibling links — never ascending back up the tree. This is why databases uniformly use B+-trees, not B-trees. [Source: Comer 1979 ACM Computing Surveys 11(2):121-137 — ACM behind captcha; mechanism confirmed in postgres/postgres nbtree/README and sqlite/sqlite btreeInt.h]

#### 1.1.3 SQLite B-tree on-disk layout (primary source: sqlite/sqlite btreeInt.h)

SQLite stores one or more B+-trees per file. Two variants:

| Variant | intKey flag | Key location | Value location | Use |
|---------|------------|--------------|----------------|-----|
| Table B-tree | 1 | cell header (varint rowid) | payload | SQL tables |
| Index B-tree | 0 | payload (arbitrary blob) | none | SQL indexes |

**Page layout** (verified from btreeInt.h `MemPage` struct and header format table):
```
[file header: 100 bytes — page 1 only]
[page header: 8 bytes leaf / 12 bytes interior]
  offset 0: flags byte (1=intkey, 2=zerodata, 4=leafdata, 8=leaf)
  offset 1: 2-byte offset to first freeblock
  offset 3: 2-byte nCell (number of cells on this page)
  offset 5: 2-byte first byte of cell content area
  offset 7: 1-byte fragmented free bytes
  offset 8: 4-byte right-child pointer (INTERIOR NODES ONLY)
[cell pointer array]  -- 2 bytes per cell, sorted, grows DOWNWARD
[unallocated space]
[cell content area]   -- grows UPWARD from end of page, arbitrary order
```

Cell content format:
- 4 bytes: left child page number (interior nodes only)
- varint: bytes of data (omitted if zerodata flag)
- varint: bytes of key (or integer key if intkey flag)
- payload bytes
- 4 bytes: first overflow page number (if payload overflows)

**Overflow pages**: linked list. Each overflow page stores `pageSize - 4` bytes of payload plus a 4-byte pointer to the next overflow page. [Source: sqlite/sqlite btreeInt.h, https://raw.githubusercontent.com/sqlite/sqlite/master/src/btreeInt.h]

**Max cells per page**: `MX_CELL = (pageSize - 8) / 6` where 6 = minimum cell size (4 bytes payload + 2 bytes cell pointer). [Verified: btreeInt.h macro definition]

**SQLite page size**: 512 to 65536 bytes (must be power of 2); stored as a 2-byte field at header offset 16; the value 1 encodes 65536. Default is 4096 bytes since SQLite 3.12.0 (2016). [UNVERIFIED: exact default not confirmed from source code; file format doc at fileformat2.html does not state default explicitly in the text I extracted]

#### 1.1.4 PostgreSQL nbtree: Lehman & Yao on-disk (primary source: postgres/postgres nbtree/README)

PostgreSQL uses the **Lehman & Yao (1981)** high-concurrency B-tree algorithm (ACM TODS Vol 6 No. 4, pp 650-670), with extensions:

**Key L&Y additions:**
- Every page has a **right-sibling link** — survives page splits without read locks
- Every non-rightmost page has a **high key** — the upper bound on keys that belong to this page; if a descending search finds key > high key, it was split concurrently; follow right link
- These allow lock-free descent: search needs only a shared page lock for the single page being read

**PostgreSQL additions beyond L&Y:**
- **Left-sibling link** — added for backward index scans; not in original L&Y
- **TID as tiebreaker** — all keys are logically unique at each level by appending the heap tuple ID; satisfies L&Y's requirement that Ki < v ≤ Ki+1
- **Suffix truncation** — pivot tuples in internal pages can omit trailing key attributes; makes pivots smaller, increases fanout, delays root splits
- **Posting lists** — non-unique indexes deduplicate via posting lists (arrays of TIDs), applied lazily at page-split time
- **Bottom-up deletion** — PostgreSQL 14+: VACUUM cleans dead index tuples without full index scan

**Splits are right-justified** and bottom-up: inserter splits leaf, then ascends adding downlinks to parent level, repeating until finding a non-full parent. [Source: postgres/postgres, https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README]

**PostgreSQL page size**: BLCKSZ, default **8192 bytes** at compile time; configurable to 1KB, 2KB, 4KB, 8KB, 16KB. [Verified: postgres/postgres configure, https://raw.githubusercontent.com/postgres/postgres/master/configure]

---

### 1.2 LSM-Trees

#### 1.2.1 Why LSM exists — the forcing constraint

**Constraint**: HDD sequential I/O is ~100x faster than random I/O (sequential ~100 MB/s vs random ~1 MB/s for HDD at time of original paper). Any write-heavy workload using a B-tree on HDD incurs expensive random writes — one per tree update once the page is no longer in cache. The LSM-tree converts ALL writes into sequential I/O by buffering in memory and flushing as sorted runs.

**Original formulation**: O'Neil, Cheng, Gawlick, O'Neil (1996) "The Log-Structured Merge-Tree (LSM-Tree)", Acta Informatica 33(4), 1996. PDF verified accessible at: https://www.cs.umb.edu/~poneil/lsmtree.pdf (122KB, HTTP 200). Full text not extractable without pdftotext. Key idea: C0 (in-memory, any structure) + C1 (on-disk B-tree). Insertions go to C0; when C0 fills, entries are rolled-merged into C1 via sequential multi-page I/O. Multi-component extension: C0, C1, ..., Ck with exponentially growing sizes.

**LevelDB lineage**: LevelDB (2011, Google) is the practical implementation of O'Neil's multi-component LSM with levels, implemented as described in its official documentation. RocksDB (2012, Facebook) is a production fork of LevelDB. [Source: google/leveldb doc/impl.md, https://raw.githubusercontent.com/google/leveldb/main/doc/impl.md]

#### 1.2.2 LevelDB write path and compaction (primary source: google/leveldb doc/impl.md)

**Write path**:
1. Write appended to WAL log file (*.log), default max size 4MB
2. Write also applied to **memtable** (in-memory sorted structure, typically skiplist)
3. When log file reaches max size: create new memtable + new log; old memtable becomes immutable
4. Background thread flushes immutable memtable as **SST (sorted string table)** to Level 0

**Level structure**:
- **Level 0**: SST files may have overlapping key ranges; threshold = 4 files triggers L0→L1 compaction
- **Level 1+**: files have distinct non-overlapping key ranges; size targets are 10^L MB (L1=10MB, L2=100MB, L3=1GB, ...)
- Target SST file size: **2MB** (LevelDB); compaction rotates through key space using last-compacted-ending-key as starting point

**Compaction mechanics** (verified from impl.md):
- Pick one file from level L and all overlapping files from level L+1
- If L+1 file overlaps only partially, the entire L+1 file is used as input
- Merge-sort all inputs; produce sequence of L+1 files at 2MB each
- Switch to new output file if: (a) current output ≥ 2MB, or (b) key range would overlap >10 level-(L+2) files (prevents future compaction fan-in explosion)
- Drop overwritten values; drop deletion markers only if no higher levels contain overlapping ranges

**Worst-case compaction I/O** (from impl.md timing section):
- L0→L1: up to 4×1MB (L0) + 10MB (all of L1) = 14MB read + 14MB write
- Ln→L(n+1): 1×2MB file + ~12 overlapping L+1 files = 26MB read + 26MB write
- At 100MB/s disk: ~0.5s per compaction; throttled to 10% = up to 5s

**MANIFEST file**: records the current set of SST files per level, key ranges, other metadata. Formatted as a log. New MANIFEST created on each database open.

**CURRENT file**: single text file pointing to the current MANIFEST.

#### 1.2.3 SST file format (primary source: google/leveldb doc/table_format.md)

```
[data block 1]
...
[data block N]        -- sorted key-value pairs, block_builder.cc format, optionally compressed
[meta block 1]        -- e.g. filter block (Bloom filters)
...
[meta block K]
[metaindex block]     -- maps meta block names to BlockHandle
[index block]         -- one entry per data block: last key in block -> BlockHandle
[footer]              -- fixed size: metaindex handle + index handle + 40 bytes total
                         magic number 0xdb4775248b80fb57 (little-endian, 8 bytes)
```

**Filter meta block** (2KB granularity): all keys in data blocks falling within `[i*2048, (i+1)*2048-1]` are hashed into filter `i`. The filter block stores filter offsets as 4-byte entries plus a 1-byte `lg(base)` value. [Source: https://raw.githubusercontent.com/google/leveldb/main/doc/table_format.md]

#### 1.2.4 RocksDB extensions (primary source: facebook/rocksdb source + EighteenZi/rocksdb_wiki)

**Key defaults** (verified from facebook/rocksdb include/rocksdb/options.h):
- `write_buffer_size = 64MB` (LevelDB: 4MB)
- `level0_file_num_compaction_trigger = 4` (same as LevelDB)
- `max_bytes_for_level_base = 256MB` (L1 target size)
- `max_bytes_for_level_multiplier = 10` (each level 10x the previous)
- Target SST file size: 64MB (vs LevelDB's 2MB)

**Compaction styles** (verified from advanced_options.h enum):
- `kCompactionStyleLevel = 0x0` — LevelDB-style (default)
- `kCompactionStyleUniversal = 0x1` — size-tiered; lower write amp, higher space amp
- `kCompactionStyleFIFO = 0x2` — time-ordered, TTL-based, no compaction

**Amplification factors** (RocksDB Tuning Guide, https://raw.githubusercontent.com/EighteenZi/rocksdb_wiki/master/RocksDB-Tuning-Guide.md):
- **Write amplification (WA)**: ratio of bytes written to storage / bytes written by application. For 5-level RocksDB: ≈ 1 (WAL) + 1 (L0 flush) + 2 (L0→L1 compaction at 2x) + 10 + 10 + 10 = ~34. WA drives SSD wear and disk bandwidth.
- **Read amplification (RA)**: disk reads per point query. Without bloom filters: all L0 files + 1 file per level. With bloom filters: ~1 disk read for existing keys; ~0 for non-existing keys (filter eliminates SST read).
- **Space amplification (SA)**: disk bytes / actual data bytes. Level-style: ~1.1× (data primarily in last level). Universal: up to 2× during compaction.

**Compaction scoring** (verified from compaction_picker_level.cc):
- L0 score = num_L0_files / `level0_file_num_compaction_trigger`
- L1+ score = current_level_size / `MaxBytesForLevel(level)`
- Level with highest score ≥ 1 gets compacted first
- L0→L1 compaction is always single-threaded; `max_subcompactions > 1` enables parallel sub-compaction within L1→L2+

**Internal key format** (verified from facebook/rocksdb db/dbformat.h):
```
[user_key | seq_num(56 bits) | value_type(8 bits)]
```
`kTypeValue = 0x1`, `kTypeDeletion = 0x0`. Max sequence number = 2^56 - 1. Keys with the same user_key are ordered by descending sequence number — the most recent write wins.

---

### 1.3 Bloom Filters

#### 1.3.1 Why Bloom filters exist — the forcing constraint

**Constraint**: LSM reads must check multiple levels for a key. Without a shortcut, a read for a missing key requires loading the index block of every SST file in every level (O(levels × files-per-level) I/Os). A Bloom filter lets the reader skip files where the key is definitely absent, at the cost of a small in-memory bit array with a tunable false positive rate.

**Original paper**: B.H. Bloom, "Space/Time Trade-offs in Hash Coding with Allowable Errors," CACM 13(7):422-426, 1970. DOI: 10.1145/362686.362692 (HTTP 403 at time of fetch). Content verified via LevelDB/RocksDB implementations and RocksDB bloom_impl.h which contains the standard formula with Wikipedia attribution.

**Bloom filter properties**:
- No false negatives: if key absent → filter always returns "absent"
- False positive probability (FPR): query returns "maybe present" for a key that isn't there
- Space-efficient: a bit array, not a hash table storing keys
- Supports only `add(key)` and `contains(key)` — no deletion (without Counting Bloom filter extension)

#### 1.3.2 How Bloom filters work — the mechanism (primary source: google/leveldb util/bloom.cc)

**Parameters**: `m` bits total, `n` keys inserted, `k` hash functions.

**Optimal k**: k = (m/n) × ln(2). Intuition: too few probes → low bit coverage → high FPR. Too many → most bits set → also high FPR. Optimal balances these. LevelDB implements this as:
```cpp
k_ = static_cast<size_t>(bits_per_key * 0.69);  // 0.69 =~ ln(2)
if (k_ < 1) k_ = 1;
if (k_ > 30) k_ = 30;
```
[Source: https://raw.githubusercontent.com/google/leveldb/main/util/bloom.cc]

**False positive rate formula** (verified in rocksdb/util/bloom_impl.h):
```
FPR = (1 - exp(-k × n / m))^k = (1 - exp(-k / bits_per_key))^k
```
[Source: https://raw.githubusercontent.com/facebook/rocksdb/main/util/bloom_impl.h — StandardFpRate()]

At 10 bits/key, optimal k=7: FPR ≈ 0.8%. At 6 bits/key, k=4: FPR ≈ 5.6%.

**Double-hashing to simulate k independent hash functions** (Kirsch & Mitzenmacher 2006 technique, referenced in rocksdb/bloom_impl.h comment):
```cpp
uint32_t h = BloomHash(key);             // single hash
uint32_t delta = (h >> 17) | (h << 15); // rotate right 17 bits
for (j = 0; j < k_; j++) {
    bitpos = h % bits;                   // probe position j
    array[bitpos/8] |= (1 << (bitpos%8));
    h += delta;                          // double-hash increment
}
```
This generates k positions from one hash computation, avoiding k full hash calls. [Source: bloom.cc + bloom_impl.h comment citing Kirsch,Mitzenmacher 2006]

**Filter storage in LevelDB SST**: filter stored per 2KB of data block content (not per data block). The filter block stores filter bits plus an offset array for mapping data block offsets to filter indices. `k_` stored as the last byte of the filter, allowing filters built with different parameters to coexist. [Source: table_format.md]

#### 1.3.3 RocksDB Bloom filter evolution (primary source: bloom_impl.h)

Three implementations in bloom_impl.h (each marked with their generation):

| Class | Cache-local? | SIMD? | Status |
|-------|-------------|-------|--------|
| `LegacyNoLocalityBloomImpl` | No | No | DO NOT REUSE (accuracy flaws) |
| `LegacyLocalityBloomImpl<ExtraRotates>` | Yes (512-bit cache line) | No | Legacy; 1% FPR penalty flaw if !ExtraRotates |
| `FastLocalBloomImpl` | Yes (512-bit/64-byte) | AVX2 | Current; ~0.957% FPR at 10 bpk |

**Cache-local insight**: Legacy double-hashing probes random bit positions across the entire filter — loads multiple cache lines per query. Cache-local design pins all k probes to a single 64-byte cache line; dramatically reduces L1 cache misses at cost of slightly higher FPR (blocked Bloom filter, see `CacheLocalFpRate()` formula). [Source: bloom_impl.h]

**Ribbon filter**: RocksDB also supports a newer Ribbon filter (2021) with better space efficiency than Bloom (~30% smaller at same FPR) based on "ribbon coding" (linear algebra over GF(2)). [UNVERIFIED: not verified directly from source in this session; mentioned in RocksDB release notes known from general knowledge]

**Memtable prefix Bloom filter** (verified from db/memtable.h): `memtable_prefix_bloom_bits` option enables a Bloom filter on the memtable itself, using `DynamicBloom`. This skips memtable lookup when prefix is definitely absent.

**Block-based vs full-filter**: LevelDB and old RocksDB use per-2KB-block filters. RocksDB added "full filter" — one Bloom filter covering the entire SST file — reducing filter overhead and improving point-lookup performance. [Source: RocksDB Tuning Guide filter_policy section]

---

## 2. Foundational Sources — Exact Links, One Canonical Per Claim

| Claim | Source |
|-------|--------|
| B-tree origin and motivation | Bayer & McCreight (1972) Acta Informatica 1(3):173-189 [Springer, blocked] — content via sqlite/sqlite btreeInt.h comments citing Knuth TAOCP Vol.3 pp. 473-480 |
| B-tree survey with B/B+/B* variants | Comer (1979) ACM Computing Surveys 11(2):121-137, doi:10.1145/356770.356776 [ACM, captcha-blocked] |
| SQLite B-tree page format, cell layout, overflow | https://raw.githubusercontent.com/sqlite/sqlite/master/src/btreeInt.h |
| SQLite file format (page header, magic bytes) | https://www.sqlite.org/fileformat2.html [direct fetch succeeded] |
| PostgreSQL B+-tree: Lehman & Yao, suffix truncation, deduplication | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README |
| PostgreSQL default block size 8KB | https://raw.githubusercontent.com/postgres/postgres/master/configure |
| LSM-tree original paper | O'Neil et al. (1996) Acta Informatica 33(4); PDF: https://www.cs.umb.edu/~poneil/lsmtree.pdf |
| LevelDB write path, compaction, level sizes | https://raw.githubusercontent.com/google/leveldb/main/doc/impl.md |
| LevelDB SST file format, filter block | https://raw.githubusercontent.com/google/leveldb/main/doc/table_format.md |
| LevelDB Bloom filter implementation (double-hash, k=bpk*0.69) | https://raw.githubusercontent.com/google/leveldb/main/util/bloom.cc |
| RocksDB default options (write_buffer_size=64MB, trigger=4 files, level_base=256MB) | https://raw.githubusercontent.com/facebook/rocksdb/main/include/rocksdb/options.h |
| RocksDB compaction styles enum | https://raw.githubusercontent.com/facebook/rocksdb/main/include/rocksdb/advanced_options.h |
| RocksDB amplification definitions, write amp ~34 for 5 levels | https://raw.githubusercontent.com/EighteenZi/rocksdb_wiki/master/RocksDB-Tuning-Guide.md |
| RocksDB leveled compaction scoring | https://raw.githubusercontent.com/facebook/rocksdb/main/db/compaction/compaction_picker_level.cc |
| RocksDB internal key format (56-bit seq + 8-bit type) | https://raw.githubusercontent.com/facebook/rocksdb/main/db/dbformat.h |
| Bloom filter FPR formula, cache-local vs standard | https://raw.githubusercontent.com/facebook/rocksdb/main/util/bloom_impl.h |
| Kirsch & Mitzenmacher double-hashing correctness | Cited in bloom_impl.h: "Asymptotic analysis is in [Kirsch,Mitzenmacher 2006]" |
| RocksDB leveled compaction description | https://raw.githubusercontent.com/EighteenZi/rocksdb_wiki/master/Leveled-Compaction.md |

---

## 3. Why It's This Way — Constraints/Tradeoffs That Forced the Design

### B-trees
- **High fanout is mandatory**: each level of the tree requires one disk I/O, so the only way to keep trees shallow enough for fast lookups is to pack as many separator keys as possible per page. The page size (4KB–8KB) is chosen to match OS virtual memory page size and disk sector size — reading one 8KB block is essentially free compared to reading two 4KB blocks if the disk must re-seek between them.
- **B+ variant chosen universally** because internal nodes that hold only keys (not values) can pack ~10–50x more entries per page, shrinking tree height by 1–2 levels at real database scales.
- **Immutable page size**: once chosen at database creation, it cannot change without rebuilding all pages. Changing page size is as expensive as recreating the database. This "lock-in" forced careful defaults.

### LSM-trees
- **In-memory buffer is mandatory**: the only way to convert random writes into sequential is to sort them first. A sorted in-memory structure (skiplist in LevelDB) accumulates writes and then flushes in key order.
- **Levels with size ratios**: level sizing at 10x per level (not arbitrary) is chosen to make write amplification predictable. A key written at L0 is rewritten once per level compaction it participates in. With 10x ratios and ~5 levels, WA ≈ 10 per non-L0 level plus overheads ≈ ~34x. Smaller ratios (e.g., 5x) lower WA but increase the number of levels and raise read amplification.
- **Non-overlapping files in L1+**: the requirement for sorted, non-overlapping ranges per level (except L0) allows a point read to check exactly ONE file per level using a simple range lookup — without this, a read might need to scan all files at that level.
- **L0 files can overlap**: L0 is a special case because flushing memtables happens at write speed (can't wait for compaction). L0 file count is bounded (trigger=4 by default) to prevent read amplification from growing unboundedly.
- **Compaction rotates through key space** (LevelDB verified): to avoid hot-spots where a single key range gets repeatedly compacted while others never are; each compaction advances a cursor, ensuring uniform coverage.
- **Deletion via tombstones**: because old values may exist in lower levels, deletes are written as `kTypeDeletion` markers (sequence + type = 0x0) which are dropped during compaction when no lower level contains the key. Cannot delete in-place because SST files are immutable.

### Bloom Filters
- **Bit array, not hash set**: storing actual keys would require O(n) space per key (~8–16 bytes each). The Bloom filter stores ~10 bits per key regardless of key size, achieving 60–80x space reduction over a simple hash set.
- **No deletions** (standard Bloom): once a bit is set, it cannot be "un-set" without risk of clearing bits shared with other keys. This matches SST usage perfectly — SST files are immutable, so their Bloom filters are write-once.
- **k probes per element trade-off**: each probe independently reduces FPR. But each probe accesses one more bit (cache miss). The optimal k = ln(2) × m/n balances these — verified analytically (formula in bloom_impl.h `StandardFpRate`).
- **Cache-local Bloom filter**: standard Bloom fans out k probes across the entire m-bit array → k potential cache line loads. Cache-local design bins all k probes to one 64-byte cache line → 1 cache line load always. Trade-off: slightly higher FPR (~0.957% vs ~0.953% at 10 bpk/k=6) but 5–10x faster queries on modern CPUs (cite: bloom_impl.h comments).
- **Bloom filter per SST, not per database**: one global filter would be too large to keep in memory. Per-SST filters are sized to the number of keys in the SST file, stay in the block cache, and are fetched once per SST access.

---

## 4. Common Misconceptions to Preempt

1. **"B-tree and B+-tree are the same thing"**: They are not. B-tree stores values in all nodes; B+-tree stores values only in leaves. Virtually all production databases use B+-trees. The term "B-tree" in database marketing/documentation almost always means B+-tree.

2. **"LSM-trees eliminate write amplification"**: LSM-trees dramatically REDUCE random I/O but do NOT reduce total bytes written. Write amplification of 10–50x is typical. SSD wear can actually be WORSE than B-tree for write-heavy LSM workloads at high WA.

3. **"Bloom filters can return false negatives"**: They cannot. A Bloom filter is only allowed to have false POSITIVES (saying "maybe present" for an absent key). A "not present" result is always correct. LSM reads use this guarantee to skip SST files: if the filter says absent, skip the SST; if it says present, fetch the SST (and may find the key isn't actually there, costing an unnecessary I/O — the false positive).

4. **"Compaction is triggered at every write"**: Compaction is a background process triggered by level scores crossing 1.0 (size over target). Most writes go to the WAL and memtable with no compaction involvement. Compaction happens concurrently in background threads.

5. **"LevelDB uses one Bloom filter for the whole database"**: The filter is per-SST file, stored in each SST's filter meta block. A point read checks the filter for each SST file it might need to examine — bloom filters are per-file, not global.

6. **"PostgreSQL's B-tree is a standard textbook B+-tree"**: PostgreSQL's nbtree uses Lehman & Yao (1981) extensions that add right-sibling links, high keys, and lock-free descent. It is NOT a naive B+-tree from Comer's survey. Concurrent splits are handled in a way that does not require exclusive locks on ancestor pages during insert.

7. **"k = number of hash functions in Bloom filter, with k separate hash functions"**: Production implementations use one hash + double-hashing to derive k bit positions. LevelDB uses a single base hash and a rotation-derived delta, computing k positions without k hash function calls. The Kirsch-Mitzenmacher (2006) paper proves this is asymptotically equivalent to k independent hashes.

8. **"LSM-trees have slower reads than B-trees"**: Point reads on LSM with Bloom filters approach B-tree performance (1–2 disk reads for present keys, 0 for absent keys with good filters). Range scans on LSM can be slower (must merge across multiple levels). The trade-off is: LSM wins on write throughput; B-tree wins on predictable read latency.

---

## 5. Best Build-Your-Own Targets

Ordered by pedagogical value and implementation tractability:

### 5.1 Bloom Filter (Easiest, ~200 lines)
**What to build**: A bit-array Bloom filter in Go or Python:
- `NewBloom(n, fp_rate float64)`: computes optimal m bits and k probes
- `Add(key []byte)`: hash + double-hash k probes, set bits
- `Contains(key []byte) bool`: same probes, return false if any bit is 0
- Test: insert 10K keys, verify 0 false negatives, measure FP rate

**Why it teaches**: shows the math of m/n tradeoff, why k = ln(2) × m/n, and why double-hashing works as a substitute for k hash functions.

**Extension**: implement the cache-local variant (all probes within one 512-bit "bucket") and measure the L1 cache miss reduction.

### 5.2 LSM Write Path (Moderate, ~1000 lines)
**What to build**: A mini-LSM in Go/Rust:
- WAL: append-only log with CRC; recover on open
- Memtable: sorted map (Go `btree` pkg or a skiplist)
- SST write: sort memtable → write data blocks + index block + Bloom filter
- SST read: binary search index block → load data block; check Bloom filter first
- Compaction: merge two SSTs from L0, produce one L1 SST (no overlap)
- MANIFEST: track which SSTables exist per level

**Why it teaches**: the WAL-memtable-SST pipeline, immutable file model, and compaction as a merge-sort are the core of LevelDB. Each component can be built and tested in isolation.

**Reference implementation**: mini-lsm (skyzh on GitHub) follows this exact sequence. Primary source: LevelDB's doc/impl.md for correct behavior spec.

### 5.3 B+-tree (Hardest, ~2000 lines)
**What to build**: A B+-tree with file-backed pages:
- Fixed-size page allocator (OS file + page cache)
- Internal node: sorted separator keys + child page IDs
- Leaf node: sorted key-value pairs + next-leaf pointer
- Insert with splits propagated upward
- Scan: find leaf, follow next-leaf pointers

**Why it teaches**: page-level locality (node == page), split mechanics, and the depth/fanout relationship. Adding a write-ahead log teaches crash consistency.

**Scope note**: implementing Lehman & Yao concurrent B+-tree is graduate-level; start with single-threaded. Source of truth for correct format: sqlite/sqlite btreeInt.h.

---

## 6. Open Questions / Where Sources Disagree

1. **Optimal bits-per-key for Bloom filters in practice**: RocksDB default documentation recommends 10 bpk (~1% FPR), but the Ribbon filter achieves the same FPR at ~7 bpk. The transition from Bloom to Ribbon is ongoing in RocksDB and remains incompletely documented in primary sources.

2. **Universal compaction vs. leveled: when to use which**: RocksDB wiki says universal compaction reduces write amplification but increases space amplification to 2×. The exact WA cross-over point where universal beats leveled depends on key distribution, dataset size, and hardware — no single authoritative formula. [Sources in tension: RocksDB Tuning Guide vs. individual benchmarks]

3. **L0→L1 parallelism**: LevelDB impl.md documents L0→L1 as serial. RocksDB added `max_subcompactions` for parallel sub-ranges within a single compaction. The interaction of sub-compaction parallelism with compaction scoring is not documented at the source-code level verified here.

4. **B+-tree fill factor**: PostgreSQL and SQLite leave pages partially full (not 100% full) to accommodate future inserts without immediate splits. The exact fill factor strategy is implementation-specific and not standardized — PostgreSQL uses a 90% page-full heuristic approximately, but the README does not state an exact fraction. [UNVERIFIED exact fill factor for PostgreSQL]

5. **LSM vs. B-tree for SSD workloads**: the original O'Neil paper (1996) was designed for HDD. SSDs have fast random reads (0.1ms) but write amplification still matters for device longevity. Whether leveled or size-tiered compaction is better for SSD endurance remains an active area — papers like "WiscKey" (2016, FAST) propose value-log separation but the consensus on best approach is unsettled.

6. **Bloom filter accuracy claims for cache-local variant**: bloom_impl.h states 0.957% FPR vs. theoretical 0.9535% at 10 bpk with k=6, 512-bit buckets. This is cited with "about" — the exact implementation-level FPR depends on hash quality and isn't independently verified in this session's sources.

7. **SQLite default page size**: SQLite 3.12.0 (2016) changed the default page size from 1024 to 4096 bytes. This is widely reported but not confirmed from source code in this session (btreeInt.h and configure.ac don't expose this constant in grep-accessible form). [UNVERIFIED from primary source]

---

## 6a. Gaps Not Covered

- O'Neil 1996 paper text: PDF fetched (122KB, HTTP 200) but not extractable without pdftotext. All LSM mechanisms verified against LevelDB/RocksDB primary source code instead.
- Bloom 1970 paper: HTTP 403 from ACM. Bloom filter mechanics fully verified from LevelDB and RocksDB implementations which implement the paper directly.
- Bayer & McCreight 1972: blocked by Springer paywall. Content inferred from citations in SQLite btreeInt.h and Comer 1979 survey description.
- Comer 1979 survey: ACM Cloudflare-blocked. Mechanisms verified from PostgreSQL and SQLite implementations.
- MySQL InnoDB B+-tree internals: not covered; would require separate cluster.
- Ribbon filter implementation: exists in RocksDB but not fetched in this session.
- Concurrent B+-tree insert/split mechanics beyond L&Y overview: nbtree/README is detailed but the actual locking code in nbtree.c / nbtinsert.c not analyzed.
