# Research Brief -- Sub-course 07: Transactions / Concurrency / Recovery
## Source cluster: ARIES/WAL/MVCC/Locking -- BusTub, PostgreSQL, InnoDB, ARIES paper
## Researcher: researcher-c5da59 | Date: 2026-06-09

---

## 1. Key Mechanisms

### 1.1 Write-Ahead Logging (WAL) -- the foundational durability contract

**Forcing constraint:** Disk writes are slow and non-atomic. If a buffer pool page is
flushed before its log is durable, a crash leaves the page modified but unrecoverable.
WAL is the minimal safe contract: *log first, then page.*

**The WAL rule (two parts):**
- The log record for a page modification must reach disk before the modified page itself.
- A transaction's commit log record must reach disk before the commit is acknowledged.

**Consequence 1 -- no-force policy:** Pages do NOT need to be flushed at commit (ARIES style).
Log flush is sufficient. This allows buffer pool pages to stay dirty and be written lazily.

**Consequence 2 -- steal policy:** Dirty pages CAN be written to disk before a transaction
commits. Combined with undo logging, this allows buffer pool eviction under pressure.

These two together define the ARIES design space: steal + no-force. The alternative
(force + no-steal) is simpler but wastes I/O and memory.

**BusTub log_manager.h** (verified):
- `next_lsn_` (atomic<lsn_t>) incremented per record
- `persistent_lsn_` (atomic<lsn_t>) tracks what's on disk
- Double-buffer: `log_buffer_` (in-flight records) + `flush_buffer_` (flushing to disk)
- `LOG_BUFFER_SIZE = (BUFFER_POOL_SIZE + 1) * BUSTUB_PAGE_SIZE` = 129 * 8192 = ~1 MB
- Flush thread woken on buffer full or timeout; signals waiting transactions
- Source: `src/include/recovery/log_manager.h`

**PostgreSQL xlog.c/xlog.h** (verified from GitHub):
- WAL levels: MINIMAL, REPLICA, LOGICAL (`src/include/access/xlog.h`)
- `RedoRecPtr` = current redo start point, checked at each insert
- `XactLastCommitEnd` = LSN of last commit, used to determine WAL-must-be-flushed-to point
- `RecordTransactionCommit()` in `src/backend/access/transam/xact.c` is the commit critical path;
  it writes commit WAL record and can delay checkpoint (`DELAY_CHKPT_IN_COMMIT` flag)
- Source: `src/backend/access/transam/xlog.c`, `src/include/access/xlog.h`

### 1.2 Log Sequence Numbers (LSN) and Log Record Structure

**Why LSN:** Every log record needs a unique, monotonically increasing identifier that also
encodes ordering. Pages store their pageLSN (= LSN of last log record that modified them).
This enables the WAL dirty-page check: "page cannot be written unless log is flushed past pageLSN."

**BusTub LogRecord format** (verified: `src/include/recovery/log_record.h` + `config.h`):
```
HEADER_SIZE = 20 bytes, per source constant/comment:
  | size | LSN | transID | prevLSN | LogType |
INSERT/DELETE body: HEADER + RID(8B) + tuple_size(4B) + tuple_data
UPDATE body: HEADER + RID + old_tuple_size + old_data + new_tuple_size + new_data
NEWPAGE body: HEADER + prev_page_id(4B) + page_id(4B)
```
Nuance: current BusTub defines `txn_id_t = int64_t`, while `HEADER_SIZE` remains `20`.
Therefore cite 20B as BusTub's serialized/header-size contract from the source, not as native
C++ object-layout math. `prev_lsn_` = LSN of previous log record from the same transaction
(backward chain for undo).

**Log record types**: INVALID, INSERT, MARKDELETE, APPLYDELETE, ROLLBACKDELETE,
UPDATE, BEGIN, COMMIT, ABORT, NEWPAGE.

**PostgreSQL XLogRecord** (verified: `src/include/access/xlogrecord.h`):
```c
typedef struct XLogRecord {
  uint32      xl_tot_len;   // total length of entire record
  TransactionId xl_xid;    // transaction XID
  XLogRecPtr  xl_prev;     // LSN of previous record in log
  uint8       xl_info;     // flag bits
  RmgrId      xl_rmid;     // resource manager (heap, btree, seq, ...)
  pg_crc32c   xl_crc;      // CRC of this record
  /* XLogRecordBlockHeaders and data follow */
} XLogRecord;
```
`SizeOfXLogRecord = offsetof(XLogRecord, xl_crc) + sizeof(pg_crc32c)`.
PG WAL is resource-manager (rmgr) partitioned -- each subsystem registers its own redo handler.
`XLogRecordMaxSize = 1020 * 1024 * 1024` (about 1 GB, theoretical ceiling).

### 1.3 ARIES Recovery -- Analysis / Redo / Undo

**Source:** Mohan et al., "ARIES: A Transaction Recovery Method Supporting Fine-Granularity
Locking and Partial Rollbacks Using Write-Ahead Logging," ACM TODS 17(1), 1992.
doi:10.1145/128765.128770 [UNVERIFIED -- direct fetch blocked; identity and structure confirmed
via PostgreSQL and BusTub source comments + CMU 15-445 course references]

**Why three phases:** A crash leaves state inconsistent in three ways simultaneously:
1. Committed transactions may have dirty pages still in buffer pool, not flushed to disk
2. Uncommitted transactions may have flushed some dirty pages to disk (steal policy)
3. We don't know which is which without scanning the log

**Phase 1 -- Analysis:** Scan forward from last checkpoint. Reconstruct the "dirty page table"
(DPT, maps page_id to recLSN = LSN at which page first became dirty) and the transaction
table (maps txn_id to state + lastLSN). Determine REDO start point (min(recLSN) across DPT).
Determine which transactions were active at crash (need undo).

**Phase 2 -- Redo ("repeating history"):** Scan forward from redo start point. For each log
record, check if the affected page is in DPT and the record's LSN > page's pageLSN on disk.
If so, redo the operation UNCONDITIONALLY -- including operations of aborted transactions.
This restores the exact pre-crash buffer pool state. No filtering by transaction status.

**Why repeat history for aborted txns:** Simplicity and correctness. If we skip aborted txn
redo, we must handle complex interactions with CLRs. Repeating history lets undo phase be a
clean pass that only works forward from a known consistent state.

**Phase 3 -- Undo:** Traverse the transaction table's loser set backward (via prevLSN chains),
undoing each operation. For each undo, write a CLR (Compensation Log Record).

**CLR (Compensation Log Record):**
- Written during undo for each operation reversed
- Has an `undoNextLSN` field pointing to the next LSN to undo for that transaction
  (skipping already-undone operations)
- CLRs are REDO-only (never undone) -- if crash during undo, CLRs allow idempotent restart
- This is what makes ARIES safe against crashes during recovery

**PostgreSQL CheckPoint record** (verified: `src/include/catalog/pg_control.h`):
```c
typedef struct CheckPoint {
  XLogRecPtr  redo;         // REDO start point (next LSN available when checkpoint began)
  FullTransactionId nextXid; // next free transaction ID at checkpoint time
  Oid         nextOid;      // next free OID
  // ...
} CheckPoint;
```
PostgreSQL fuzzy checkpoint: dirty pages written in background, checkpoint record stores
redo pointer so recovery knows where to start. Pages older than checkpoint redo pointer are
guaranteed consistent and need no redo.

### 1.4 MVCC -- Multi-Version Concurrency Control

**Why MVCC:** Readers and writers should not block each other. The insight is that we can
keep multiple versions of a row and let each transaction see the version current at its start
time, without locks on the read path.

**Core invariant:** Each read sees a consistent snapshot = the state of committed data as of
some point in time. Writes create new versions, old versions retained for concurrent readers.

#### PostgreSQL MVCC (verified from GitHub source)

**Tuple header fields** (`src/include/access/htup_details.h`):
- `t_xmin`: XID of the transaction that inserted this version
- `t_xmax`: XID of the transaction that deleted/updated this version (0 = live)
- `t_cid`: Command ID -- differentiates updates within the same transaction
- `t_ctid`: "Current TID" -- pointer to newer version (HOT chain following), or self if latest
- `t_infomask` hint bits: `HEAP_XMIN_COMMITTED(0x0100)`, `HEAP_XMIN_INVALID(0x0200)`,
  `HEAP_XMAX_COMMITTED(0x0400)`, `HEAP_XMAX_INVALID(0x0800)`, `HEAP_XMAX_IS_MULTI(0x1000)`
  -- used to cache clog lookups; set lazily, must be set while holding page lock

**Visibility rule:** Tuple version is visible to snapshot S iff:
1. t_xmin is committed AND t_xmin < S.xmax AND t_xmin not in S.xip[] (not in-progress at snapshot)
2. AND (t_xmax is invalid, OR t_xmax is in-progress at snapshot, OR t_xmax > S.xmax)

**Snapshot structure** (`src/include/utils/snapshot.h`):
```c
typedef struct SnapshotData {
  SnapshotType snapshot_type;
  TransactionId xmin;   // all XID < xmin are committed and visible
  TransactionId xmax;   // all XID >= xmax are invisible (started after snapshot)
  TransactionId *xip;   // array of in-progress XIDs (xmin <= xip[i] < xmax)
  uint32    xcnt;       // count of in-progress XIDs
  // ...
} SnapshotData;
```
`HeapTupleSatisfiesMVCC()` in `src/backend/access/heap/heapam_visibility.c` implements
the full visibility check, calling `XidInMVCCSnapshot()` for the xip[] scan.

**Transaction ID (XID):** 32-bit unsigned wrapping counter (`src/include/access/transam.h`):
- `InvalidTransactionId = 0`, `BootstrapTransactionId = 1`, `FrozenTransactionId = 2`
- `FirstNormalTransactionId = 3`, `MaxTransactionId = 0xFFFFFFFF`
- Wraparound: PostgreSQL treats XID space as a circle; tuples more than 2^31 XIDs old are
  "frozen" (their xmin is replaced with FrozenTransactionId=2, always visible)
- This requires periodic VACUUM to advance the freeze horizon

#### InnoDB MVCC (verified from MySQL 8.4 GitHub source)

**ReadView** (`storage/innobase/include/read0types.h`):
```
ReadView {
  m_low_limit_id:  trx_id_t  // IDs >= this are invisible (started after snapshot)
  m_up_limit_id:   trx_id_t  // IDs < this are visible (committed before snapshot)
  m_creator_trx_id: trx_id_t // creator's own writes are always visible
  m_ids[]:          sorted list of in-progress transaction IDs
}
```
Visibility: `id < m_up_limit_id` -> visible; `id >= m_low_limit_id` -> invisible;
else binary search in `m_ids[]` -- if found, invisible; if not found, visible.

**Undo log chain** (`storage/innobase/include/trx0undo.h`):
- `TRX_UNDO_INSERT = 1`: created for INSERT; discarded at commit (not needed for MVCC)
- `TRX_UNDO_UPDATE = 2`: created for UPDATE/DELETE; retained until no ReadView needs old version
- Each record version stores a rollback pointer to previous version in undo log pages
- Undo logs live in "rollback segments" (ibdata or separate undo tablespaces)
- MVCC reads traverse undo chain following rollback pointers until finding a visible version

**Transaction states** (`storage/innobase/include/trx0trx.h`):
`TRX_STATE_NOT_STARTED, TRX_STATE_FORCED_ROLLBACK, TRX_STATE_ACTIVE, TRX_STATE_PREPARED,
TRX_STATE_COMMITTED_IN_MEMORY`.
Isolation levels: `READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ (default), SERIALIZABLE`

#### BusTub MVCC (verified from GitHub source)

**Design:** Timestamp-based MVCC, not XID-based. Each tuple has a `ts_` field (timestamp_t = int64).
During a transaction, `ts_` stores the transaction's `txn_id_` (which has high bit set via
`TXN_START_ID = 1LL << 62`). On commit, all modified tuple timestamps are set to `commit_ts_`.

**Version chain** (`src/include/concurrency/transaction.h`):
```cpp
struct UndoLink {
  txn_id_t prev_txn_;     // which transaction holds the previous version
  int      prev_log_idx_; // index within that transaction's undo_logs_ vector
};

struct UndoLog {
  bool is_deleted_;
  vector<bool> modified_fields_; // which columns changed (delta encoding)
  Tuple tuple_;                  // the delta (partial old values)
  timestamp_t ts_;               // timestamp of this version
  UndoLink prev_version_;        // link to older version
};
```
`TransactionManager::version_info_` maps `page_id_t -> PageVersionInfo -> slot_offset_t -> UndoLink`
-- this is a separate structure from the tuple itself, allowing atomic update of tuple + undo link.

**Watermark** (`src/include/concurrency/watermark.h`):
```cpp
class Watermark {
  timestamp_t commit_ts_;     // last committed timestamp
  timestamp_t watermark_;     // min(read_ts) across all running transactions
  unordered_map<timestamp_t, int> current_reads_; // ref count per read_ts
};
```
The watermark is the GC frontier: undo logs with `ts_ < watermark_` are unreachable by any
running transaction and can be garbage collected.

**Isolation levels** (BusTub `transaction.h`):
`READ_UNCOMMITTED, SNAPSHOT_ISOLATION, SERIALIZABLE` (note: no READ_COMMITTED in current master)
Default is `SNAPSHOT_ISOLATION`.

**Commit serialization:** `commit_mutex_` in `TransactionManager` ensures only one transaction
commits at a time. This is the OCC validation gate for `SERIALIZABLE` level (`VerifyTxn()`).

### 1.5 Isolation Levels and Anomalies

**The anomaly model (SQL standard + research):**
| Anomaly | Definition |
|---------|------------|
| Dirty read | Read uncommitted data that may be rolled back |
| Non-repeatable read | Same row read twice in one txn gives different values |
| Phantom read | Same range query gives different row sets due to concurrent inserts |
| Write skew | Two txns each read, then write based on stale combined read |
| Lost update | Two concurrent updates, one overwrites the other silently |

**Level -> permitted anomalies:**
- READ UNCOMMITTED: dirty reads allowed
- READ COMMITTED: no dirty reads; non-repeatable reads and phantoms possible
- REPEATABLE READ: no dirty reads, no non-repeatable reads; phantoms possible (SQL standard)
  Note: MySQL InnoDB RR prevents phantoms via gap locks -- stricter than SQL standard
- SERIALIZABLE: no anomalies

**BusTub project split caveat (load-bearing):** current `transaction.h` exposes only
`READ_UNCOMMITTED, SNAPSHOT_ISOLATION, SERIALIZABLE`. `lock_manager.h` still contains Project 3
2PL specification comments that mention `REPEATABLE_READ` and `READ_COMMITTED`, but these are
not active enum values in current master. `config.h` also contains `#define DISABLE_LOCK_MANAGER`,
so treat the lock manager as a Project 3 teaching/spec scaffold, not the active Project 4 MVCC
runtime.

**BusTub Project 3 lock_manager.h comments** (verified as spec text, not active Project 4 behavior):
- REPEATABLE_READ: all locks held until commit; no locks in SHRINKING state
- READ_COMMITTED: X locks trigger SHRINKING; S locks can still be acquired in SHRINKING
  (release S locks early, allows non-repeatable reads)
- READ_UNCOMMITTED: only IX/X locks acquired; no S/IS/SIX allowed

### 1.6 Two-Phase Locking (2PL)

**The 2PL theorem:** A schedule is conflict-serializable iff all transactions follow 2PL.
[Source: Bernstein & Goodman, "Concurrency Control in Distributed Database Systems," ACM
Computing Surveys 1981 -- classic theorem, widely cited, not directly fetched; [UNVERIFIED]]

**Two phases:**
- GROWING: acquire locks, never release
- SHRINKING: release locks, never acquire (once first lock is released)

**Strict 2PL:** All locks held until commit/abort. Prevents cascading aborts (no dirty reads).
PostgreSQL's row-level concurrency is MVCC plus row locks; its table-level lock mode names are
verified below, but the stronger claim "PostgreSQL uses strict 2PL for table-level locks" needs
`src/backend/storage/lmgr/README` or equivalent primary-source confirmation before course prose.

**Lock modes in PostgreSQL** (verified: `src/include/storage/lockdefs.h`):
```
AccessShareLock        (1)  -- SELECT
RowShareLock           (2)  -- SELECT FOR UPDATE/SHARE
RowExclusiveLock       (3)  -- INSERT, UPDATE, DELETE
ShareUpdateExclusiveLock(4) -- VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY
ShareLock              (5)  -- CREATE INDEX
ShareRowExclusiveLock  (6)  -- like EXCLUSIVE but allows ROW SHARE
ExclusiveLock          (7)  -- blocks ROW SHARE / SELECT FOR UPDATE
AccessExclusiveLock    (8)  -- ALTER TABLE, DROP TABLE, VACUUM FULL
```
Higher number = more restrictive. Conflicts checked via a compatibility matrix.

**BusTub Project 3 lock_manager.h** (verified as teaching/spec scaffold) -- 5 lock modes:
`SHARED, EXCLUSIVE, INTENTION_SHARED, INTENTION_EXCLUSIVE, SHARED_INTENTION_EXCLUSIVE`
Hierarchical (table then row): to lock a row EXCLUSIVE, must hold X, IX, or SIX on table.
Intention locks = "I plan to lock something below this level."

**Lock upgrade rules** (from lock_manager.h comments, verified):
```
IS -> [S, X, IX, SIX]
S  -> [X, SIX]
IX -> [X, SIX]
SIX -> [X]
```
Only one upgrading transaction allowed per resource simultaneously (UPGRADE_CONFLICT abort).

**Phantom problem:** Even strict 2PL doesn't prevent phantom reads without predicate/gap locks.
Locking individual rows doesn't lock the "gap" where new rows could be inserted.
InnoDB solves this with gap locks (REPEATABLE_READ).

**InnoDB gap locks** (verified: `storage/innobase/include/lock0lock.h`):
- LOCK_GAP: locks a gap between index entries (prevents inserts into that gap)
- LOCK_REC_NOT_GAP: locks a specific record only (not its preceding gap)
- Next-key lock = LOCK_S + LOCK_GAP on the index entry = locks record + gap before it
- INSERT_INTENTION lock: set by inserting transactions; compatible with GAP locks but
  conflicts with other INSERT_INTENTION locks at the same gap position
- Gap locks NOT acquired at READ_COMMITTED (each statement gets fresh snapshot, gap locks not needed)

### 1.7 Deadlocks

**Definition:** Cycle in the waits-for graph: T1 waits for T2, T2 waits for T1 (or longer cycles).

**Detection vs. Prevention:**
- Detection: Periodic cycle detection in waits-for graph; abort the youngest/cheapest txn
- Prevention: Wound-Wait (older txn "wounds" i.e. aborts younger waiting txn) or
  Wait-Die (older txn waits; younger txn dies/aborts rather than waiting)

**BusTub Project 3 deadlock detection** (verified from `src/include/concurrency/lock_manager.h`
for declarations/data structures; tie-break policy still source-needed):
- `waits_for_`: adjacency list `unordered_map<txn_id_t, vector<txn_id_t>>`
- `RunCycleDetection()` thread runs continuously when `enable_cycle_detection_ = true`
- `HasCycle(txn_id_t *txn_id)`: finds a cycle and returns the txn to abort
- `FindCycle(...)`: DFS helper with `on_path` set for cycle detection; exact victim-selection
  rule (e.g., youngest/highest txn_id) is [NEEDS-SOURCE] until `lock_manager.cpp` or the CMU
  Project 3 spec is fetched directly.
- `AddEdge(t1, t2)` = "t1 waits for t2"; removed when lock granted

**PostgreSQL deadlock detection** (`src/backend/storage/lmgr/deadlock.c`):
PostgreSQL uses a similar waits-for graph + DFS cycle detection, run when a lock wait
times out (`deadlock_timeout` GUC, default 1 second). [UNVERIFIED for exact source -- not
directly fetched, but consistent with general PG knowledge and lockdefs.h structure]

### 1.8 Optimistic Concurrency Control (OCC)

**Why OCC:** For low-contention workloads, pessimistic locking wastes overhead on locks that
never conflict. OCC validates at commit time instead of acquiring locks eagerly.

**Three phases:**
1. Read: Execute transaction, track read set and write set
2. Validate: At commit, check no conflicting committed transaction overlaps with our read set
3. Write: If valid, apply writes; else abort

**BusTub SERIALIZABLE implementation** (verified: `transaction_manager.cpp`):
- `VerifyTxn(txn)` called during commit under `commit_mutex_`
- `scan_predicates_` in `Transaction` stores read predicates for validation
- Commit mutex serializes the validate+write phase (one at a time)
- Currently `VerifyTxn` returns `true` -- stub for student implementation

**Snapshot Isolation (SI) vs. Serializable SI:**
- SI: each transaction sees a consistent snapshot at start; write-write conflicts only
- SI does NOT prevent write skew (two transactions each read overlapping sets, write different rows)
- SSI (Serializable Snapshot Isolation): adds anti-dependency tracking on top of SI
  to catch write skew. Used in PostgreSQL >= 9.1 (`SERIALIZABLE` isolation level).

---

## 2. Foundational Sources

| Claim | Primary source |
|-------|---------------|
| BusTub transaction states, isolation levels, UndoLink/UndoLog structure | `src/include/concurrency/transaction.h` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/concurrency/transaction.h |
| BusTub Project 3 lock modes, 5-mode hierarchy, spec-comment isolation rules, deadlock data structures; not active Project 4 MVCC runtime because current config has `DISABLE_LOCK_MANAGER` | `src/include/concurrency/lock_manager.h` + `src/include/common/config.h` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/concurrency/lock_manager.h |
| BusTub TransactionManager: version_info_, commit_mutex_, Watermark, Begin/Commit/Abort | `src/include/concurrency/transaction_manager.h` + `src/concurrency/transaction_manager.cpp` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/concurrency/transaction_manager.cpp |
| BusTub Watermark GC frontier | `src/include/concurrency/watermark.h` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/concurrency/watermark.h |
| BusTub LogRecord HEADER_SIZE=20 source constant/comment, log types, prevLSN chain; caveat: `txn_id_t=int64_t` in current config | `src/include/recovery/log_record.h` + `src/include/common/config.h` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/recovery/log_record.h |
| BusTub LogManager: double-buffer, flush thread, LOG_BUFFER_SIZE | `src/include/recovery/log_manager.h` + `src/include/common/config.h` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/recovery/log_manager.h |
| BusTub constants: TXN_START_ID=1LL<<62, txn_id_t=int64, lsn_t=int32 | `src/include/common/config.h` -- https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/common/config.h |
| PostgreSQL tuple header xmin/xmax/cid/ctid/infomask | `src/include/access/htup_details.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/access/htup_details.h |
| PostgreSQL MVCC snapshot structure (xmin/xmax/xip[]) | `src/include/utils/snapshot.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/utils/snapshot.h |
| PostgreSQL HeapTupleSatisfiesMVCC, XidInMVCCSnapshot | `src/backend/access/heap/heapam_visibility.c` -- https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/heap/heapam_visibility.c |
| PostgreSQL TransactionId constants: FrozenTxnId=2, FirstNormal=3, MaxXid=0xFFFFFFFF | `src/include/access/transam.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/access/transam.h |
| PostgreSQL XLogRecord structure, SizeOfXLogRecord, xl_crc | `src/include/access/xlogrecord.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/access/xlogrecord.h |
| PostgreSQL WAL levels, RedoRecPtr, checkpoint flags | `src/include/access/xlog.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/access/xlog.h |
| PostgreSQL CheckPoint.redo (REDO start LSN), nextXid | `src/include/catalog/pg_control.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/catalog/pg_control.h |
| PostgreSQL 8 lock modes (AccessShare ... AccessExclusive) | `src/include/storage/lockdefs.h` -- https://raw.githubusercontent.com/postgres/postgres/master/src/include/storage/lockdefs.h |
| PostgreSQL RecordTransactionCommit WAL commit path | `src/backend/access/transam/xact.c` -- https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/transam/xact.c |
| InnoDB ReadView structure (m_low_limit_id, m_up_limit_id, m_ids[]) | `storage/innobase/include/read0types.h` -- https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/read0types.h |
| InnoDB isolation levels (READ_UNCOMMITTED ... SERIALIZABLE) | `storage/innobase/include/trx0trx.h` -- https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/trx0trx.h |
| InnoDB lock modes (LOCK_IS, LOCK_IX, LOCK_S, LOCK_X) | `storage/innobase/include/lock0types.h` -- https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/lock0types.h |
| InnoDB TRX_UNDO_INSERT=1, TRX_UNDO_UPDATE=2 | `storage/innobase/include/trx0undo.h` -- https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/trx0undo.h |
| InnoDB gap locks, next-key locks, insert intention locks | `storage/innobase/include/lock0lock.h` -- https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/lock0lock.h |
| InnoDB LSN structure: write_lsn, flushed_to_disk_lsn | `storage/innobase/include/log0sys.h` -- https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/log0sys.h |
| ARIES 3-phase recovery, CLRs, repeating history, steal/no-force | Mohan et al., ACM TODS 17(1), 1992. doi:10.1145/128765.128770 [UNVERIFIED -- domain not accessible] |

---

## 3. Why It's This Way -- Forcing Constraints

**WAL exists because:** Disk I/O is slow and non-atomic. Without WAL, we cannot know post-crash
which page modifications were committed. Force policy (flush page at commit) is prohibitively
slow; steal+no-force with WAL enables high throughput with correctness.

**MVCC exists because:** 2PL readers block writers and vice versa. Under heavy read workloads,
lock contention becomes the bottleneck. MVCC decouples reads from writes at the cost of
storage (multiple versions) and GC complexity (purging old versions).

**Why 32-bit XID in PostgreSQL (and wraparound):** The system was designed in an era when
32-bit was sufficient for "any practical workload." The frozen XID mechanism is the workaround:
VACUUM periodically rewrites xmin to FrozenTransactionId=2 for old tuples, preventing the
2^31-XID visibility cliff. Modern PostgreSQL (14+) has "accelerated aging" and more aggressive
freeze hints to handle this.

**Why InnoDB separates insert undo from update undo:** Insert undo is only needed for rollback,
not MVCC (new inserts invisible to concurrent transactions until commit). Discarding insert undo
at commit immediately frees space. Update undo must be retained until no active ReadView needs
the old version, driving the purge thread design.

**Why 2PL alone doesn't solve phantoms:** 2PL locks existing rows but cannot lock "holes"
where new rows will appear. Gap locking (InnoDB) extends 2PL to predicate-level coverage.
PostgreSQL instead relies on SSI (anti-dependency tracking) at SERIALIZABLE level and MVCC
visibility at lower levels.

**Why ARIES "repeats history" for aborted transactions during redo:** Correctness. CLRs from
incomplete rollbacks must be redone. If redo selectively skips aborted transactions, it must
correctly handle CLRs without knowing their context -- impossible without full history. Repeating
history ensures undo phase starts from a known consistent state identical to pre-crash memory.

**Why BusTub uses TXN_START_ID = 1LL << 62:** Timestamps and transaction IDs share the same
type (`int64_t`). In-progress tuples have `ts_ = txn_id_` which has the high bit set, making
them instantly distinguishable from committed timestamps (which are small monotonic counters).
A reader seeing `ts_ >= TXN_START_ID` knows the row is in-flight.

**Why InnoDB default is REPEATABLE_READ (not SERIALIZABLE):** Serializability via locking
requires predicate locks; SSI requires anti-dependency tracking. Both add significant overhead.
REPEATABLE_READ with gap locks provides practical protection against most anomalies at lower cost.

---

## 4. Common Misconceptions to Preempt

**Misconception 1: "2PL guarantees serializability."**
Correct: 2PL guarantees conflict-serializability only if applied to ALL conflicting operations.
Without predicate locks, phantom reads can violate serializability even under strict 2PL.

**Misconception 2: "MVCC eliminates the need for locks."**
Correct: MVCC eliminates read-write locking. Write-write conflicts still require locking or OCC
validation. PostgreSQL MVCC + table-level locking; InnoDB MVCC + row-level locking coexist.

**Misconception 3: "REPEATABLE_READ in MySQL/InnoDB = SQL standard REPEATABLE_READ."**
Correct: SQL standard REPEATABLE_READ allows phantoms. InnoDB REPEATABLE_READ prevents phantoms
via gap locks -- stronger than the standard. This is a deliberate design choice, not a bug.

**Misconception 4: "Snapshot Isolation is serializable."**
Correct: SI prevents dirty reads, non-repeatable reads, and phantoms, but allows write skew
(two transactions each check a condition, both pass, both write, combined result violates
an integrity constraint). PostgreSQL's SERIALIZABLE level uses SSI to catch this.

**Misconception 5: "WAL means every commit flushes all dirty pages."**
Correct: WAL only requires the log record to be flushed at commit. Dirty pages can stay in
the buffer pool and be written lazily. This is the whole performance point of no-force.

**Misconception 6: "ARIES undo only undoes committed-then-rolled-back transactions."**
Correct: ARIES undo phase undoes ALL transactions that were active (uncommitted) at crash time,
including partially-executed transactions. The redo phase first restored their partial writes,
and undo reverses them using the log.

**Misconception 7: "PostgreSQL XID is monotonically increasing forever."**
Correct: XID is a 32-bit wrapping counter. The frozen XID mechanism and VACUUM are required
to prevent the "XID wraparound catastrophe" where old tuples appear to be in the future.

**Misconception 8: "CLRs are undone during Undo phase."**
Correct: CLRs are REDO-only records. They are never undone. During undo, each CLR's
`undoNextLSN` field causes the undo process to skip past the CLR's own log record directly
to the next operation requiring undo, making recovery idempotent.

---

## 5. Best Build-Your-Own Targets

**Target 1: BusTub Project 4 (Transaction + MVCC)**
- Implement `Begin()`, `Commit()`, `Abort()` in transaction_manager.cpp
- Implement tuple visibility using UndoLink/UndoLog chain
- Implement watermark-based GC
- Implement SERIALIZABLE via `VerifyTxn()` + scan predicate validation
- Direct source scaffolding: full skeleton at github.com/cmu-db/bustub master branch
- Best pedagogical target for MVCC internals because version chain is explicit in code structure

**Target 2: BusTub Project 3 (Lock Manager)**
- Implement LockTable(), UnlockTable(), LockRow(), UnlockRow()
- Implement deadlock detection via DFS on waits_for_ graph
- Full isolation level semantics enforced via lock acquisition rules
- Source: `src/include/concurrency/lock_manager.h` (full spec in comments)

**Target 3: Simple WAL + ARIES recovery (from scratch)**
- Page-level log with LSN, pageLSN, prevLSN chain
- Implement Analysis/Redo/Undo phases
- Test with crash injection (kill process during write workload)
- Good reference starting point: BusTub log_manager.h + log_record.h structure
- Simpler alternative: cstack db_tutorial Part 12+ (SQLite-style single-page WAL) [UNVERIFIED -- cstack WAL section not directly fetched this session]

**Target 4: Minimal MVCC with timestamp ordering**
- Two tables per relation: current version + version chain (linked list)
- Visibility check: timestamp range [xmin_ts, xmax_ts)
- GC: remove versions older than watermark
- BusTub's UndoLink/UndoLog pattern is an excellent reference implementation

---

## 6. Open Questions / Source Gaps

1. **ARIES paper direct content unverified:** doi:10.1145/128765.128770 blocked. Specific
   claims about CLR `undoNextLSN` field format, exact DPT/ATT structure, and "fuzzy checkpoint"
   terminology are widely cited but not directly fetched from the original paper. Verify before
   course prose.

2. **PostgreSQL SSI implementation details:** The Ports/Gruber/Levandoski 2012 paper on
   Serializable Snapshot Isolation is referenced in PG docs but not directly fetched. The
   PostgreSQL predicate locking source (`src/backend/storage/lmgr/predicate.c`) should be
   the primary anchor for SSI details. Not fetched this session.

3. **PostgreSQL deadlock detection source:** `src/backend/storage/lmgr/deadlock.c` not
   directly fetched. Claimed to be DFS-based; verify before teaching it as fact.

4. **InnoDB purge thread mechanics:** How InnoDB decides when an UPDATE undo log segment is
   safe to purge (purge thread vs. ReadView watermark) not directly traced in source this
   session. `storage/innobase/row/row0purge.cc` and `trx0purge.cc` would be primary sources.

5. **PostgreSQL VACUUM freeze threshold configuration:** The exact GUC parameters controlling
   freeze horizon (vacuum_freeze_min_age, vacuum_freeze_table_age) and the accelerated aging
   mechanism in PG14+ were not directly fetched. `src/backend/commands/vacuum.c` would confirm.

6. **BusTub SERIALIZABLE VerifyTxn() is a stub:** The reference implementation is unfinished
   (`VerifyTxn` returns `true`). Student implementations vary. For the course, the build target
   should specify the OCC validation algorithm explicitly.

7. **OCC vs MVCC-SI boundary in BusTub:** BusTub's current master uses `SNAPSHOT_ISOLATION`
   as the default but the `VerifyTxn`+`commit_mutex_` pattern is closer to OCC validation.
   The relationship between the two should be clarified in course material (they are related
   but distinct: SI is a read visibility policy, OCC is a conflict detection method; they can
   coexist).

8. **Wound-Wait vs Wait-Die prevention strategies:** Not implemented in BusTub (which uses
   detection, not prevention). If course covers prevention, primary source would be
   Rosenkrantz et al. 1978, "System Level Concurrency Control for Distributed Database Systems,"
   ACM TODS 3(2). [UNVERIFIED -- not fetched]

9. **cstack db_tutorial WAL coverage:** The cstack tutorial's WAL/recovery section (if any)
   was not fetched this session. The earlier cluster brief verified cstack through B-tree/pager.
   Confirm whether cstack covers WAL before listing it as a build target.
