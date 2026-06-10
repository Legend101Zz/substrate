# Factcheck Report -- Sub-course 07: Database Internals (Phase 1 Briefs)
## Factchecker: factchecker-364dac | Date: 2026-06-09
## Input files:
- 07-database-internals/_research_storage-query-exec.md
- 07-database-internals/_research_transactions-recovery.md
- 07-database-internals/_research_optimizer-external-exec.md
## Method: primary-source verification via GitHub raw URLs and PostgreSQL sample config

---

## BLOCKERS (must fix before reconciliation)

| # | claim | verdict | source link | note |
|---|-------|---------|-------------|------|
| B1 | `_research_transactions-recovery.md` Sec 1.5/1.6: BusTub lock_manager.h "specifies locking behavior" for `REPEATABLE_READ` and `READ_COMMITTED` isolation levels | UNSUPPORTED as current-master BusTub behavior | https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/concurrency/transaction.h | The current `IsolationLevel` enum in `transaction.h` is `{ READ_UNCOMMITTED, SNAPSHOT_ISOLATION, SERIALIZABLE }` -- REPEATABLE_READ and READ_COMMITTED do not exist as enum values. The lock_manager.h comments referencing those levels are Project 3 (2PL) scaffolding, not the live Project 4 MVCC system. Brief even acknowledges this in Sec 1.4 ("note: no READ_COMMITTED in current master") then contradicts it in Sec 1.6. A course reader will think BusTub's current design supports 2PL with READ_COMMITTED/REPEATABLE_READ. |
| B2 | `_research_transactions-recovery.md` Sec 1.6: lock_manager.h is an active, functional component of the current BusTub | UNSUPPORTED | https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/common/config.h | `config.h` contains `#define DISABLE_LOCK_MANAGER` which gates the destructor's `UnlockAll()` call and signals that the 2PL lock manager is NOT integrated into the active Project 4 MVCC design. The briefs never disclose this macro or its significance. The distinction between Project 3 (2PL + 2-level locking) and Project 4 (MVCC + undo log, no row-level 2PL) is load-bearing for the course. |
| B3 | `_research_transactions-recovery.md` Sec 1.7: `FindCycle()` "aborts youngest (highest txn_id) in cycle" | NEEDS-SOURCE | https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/concurrency/lock_manager.h | `lock_manager.h` declares `FindCycle(txn_id_t source_txn, ..., txn_id_t *abort_txn_id)` but does NOT document the tie-breaking rule (youngest = highest txn_id). The rule is commonly stated in CMU 15-445 lectures and the .cpp student scaffolding, but it is not sourced from a reachable primary source in this brief. Must cite the .cpp implementation or CMU lab spec directly. |

---

## WARNINGS (log as gaps / caveats before writing chapter prose)

| # | claim | verdict | source link | note |
|---|-------|---------|-------------|------|
| W1 | `_research_transactions-recovery.md` Sec 1.4: `SnapshotData` struct field order `xcnt` before `xip` | UNSUPPORTED (minor, order-only) | https://raw.githubusercontent.com/postgres/postgres/master/src/include/utils/snapshot.h | Brief shows `xcnt` before `xip` (`uint32 xcnt; TransactionId *xip;`). Actual source has `xip` first, `xcnt` second (`TransactionId *xip; uint32 xcnt;`). Field names and types are correct; only presentation order is wrong. Fix before chapter drafts quote the struct layout verbatim. |
| W2 | `_research_transactions-recovery.md` Sec 1.4: InnoDB transaction state list omits `TRX_STATE_FORCED_ROLLBACK` | NEEDS-SOURCE (incomplete) | https://raw.githubusercontent.com/mysql/mysql-server/8.4/storage/innobase/include/trx0trx.h | Source has `TRX_STATE_NOT_STARTED`, `TRX_STATE_FORCED_ROLLBACK`, `TRX_STATE_ACTIVE`, `TRX_STATE_PREPARED`, `TRX_STATE_COMMITTED_IN_MEMORY`. Brief omits `TRX_STATE_FORCED_ROLLBACK`. Acceptable as simplification but should be noted as gap. |
| W3 | `_research_storage-query-exec.md` Sec 1.6: AbstractExecutor comment says "Volcano tuple-at-a-time" but Next() is batch-at-a-time | SUPPORTED with important caveat | https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/execution/executors/abstract_executor.h | Briefs correctly note this contradiction. Confirmed: comment says "Volcano tuple-at-a-time" but signature is `Next(vector<Tuple>*, vector<RID>*, size_t batch_size)`. This is a source inconsistency in BusTub itself, not a research error -- but chapter prose must not call BusTub "Volcano tuple-at-a-time" without the batch qualifier. |
| W4 | `_research_optimizer-external-exec.md` Sec 1.8: PostgreSQL JIT targets "expression evaluation and tuple deforming" | SUPPORTED | https://raw.githubusercontent.com/postgres/postgres/master/src/backend/jit/README | Verified from README. No issue, but note that JIT README also identifies "deformed slot" caching, inlined operators, and NativeFunction-based calls as additional JIT targets beyond the two named in the brief. |
| W5 | Graefe 1994 (IEEE TKDE 6(1):120-135) -- claimed as identity of the Volcano paper | NEEDS-SOURCE | doi:10.1109/69.273032 (blocked) | Cannot confirm exact volume/issue/page numbers from any reachable primary source. Brief correctly marks UNVERIFIED. Leave as-is with explicit [UNVERIFIED] tag; do NOT convert to SUPPORTED until doi is confirmed. |
| W6 | Graefe 1993 ACM Computing Surveys 25(2):73-170 | NEEDS-SOURCE | doi:10.1145/152610.152611 (blocked) | Same status. Brief correctly marks UNVERIFIED. |
| W7 | Selinger 1979 SIGMOD paper -- "interesting orders," SF=1/n_distinct, left-deep DP | NEEDS-SOURCE | Duke mirror PDF (scanned image, no text extraction) | Brief correctly marks all Selinger claims as [UNVERIFIED from text]. Source URL confirmed reachable but unreadable. Do NOT promote to SUPPORTED. |
| W8 | ARIES (Mohan et al. 1992 ACM TODS 17(1)) -- CLR undoNextLSN, DPT/ATT, "repeating history" phrase, steal+no-force | NEEDS-SOURCE | doi:10.1145/128765.128770 (blocked) | Brief correctly marks UNVERIFIED. All ARIES-specific claims (exact CLR format, fuzzy checkpoint definition) must remain caveat-gated until paper text is reachable. |
| W9 | HyPer/Neumann 2011 "Efficiently Compiling" (VLDB 2011) -- produce/consume model, LLVM IR pipeline fusion | NEEDS-SOURCE | CMU 15-721 PDF (200 OK, empty text extraction) | Brief correctly marks UNVERIFIED from text. |
| W10 | MonetDB/X100 (Boncz, Zukowski, Nes -- CIDR 2005) -- vector-size L1 cache rationale | NEEDS-SOURCE | All known mirrors 404 | Brief correctly marks UNVERIFIED. DuckDB "why_duckdb" page is cited as secondary attestation. Acceptable as a caveat note, not as primary confirmation. |
| W11 | PAX paper (Ailamaki et al. VLDB 2001) -- "minipage" layout within pages | NEEDS-SOURCE | UW-Madison PDF (200 OK, scanned CCITT image, no text) | Brief correctly marks UNVERIFIED from text. |
| W12 | Crotty et al. CIDR 2022 "Are You Sure You Want to Use MMAP" -- BPM vs mmap argument | NEEDS-SOURCE | Not fetched | Brief notes "[UNVERIFIED for exact citation -- paper identity well-established]." Acceptable caveat; do not promote to SUPPORTED. |
| W13 | `_research_optimizer-external-exec.md` Sec 1.7: DuckDB STANDARD_VECTOR_SIZE "must be power of 2 by assert" | SUPPORTED with precision fix | https://raw.githubusercontent.com/duckdb/duckdb/main/src/include/duckdb/common/vector_size.hpp | The source has `#if (STANDARD_VECTOR_SIZE & (STANDARD_VECTOR_SIZE - 1) != 0) #error ...` -- this is a compile-time `#error`, not a runtime `assert()`. The constraint is correctly described but the mechanism word "assert" is imprecise. |
| W14 | `_research_transactions-recovery.md` Sec 1.6: "Strict 2PL: All locks held until commit/abort. ... PostgreSQL uses strict 2PL for its table-level locks" | NEEDS-SOURCE | PostgreSQL lock source not verified in this session | Brief does not cite a specific PostgreSQL source for this claim. PostgreSQL's concurrency model is MVCC for rows + coarse-grained table locks, but "strict 2PL for table-level locks" is a simplification that needs a specific source (e.g., `src/backend/storage/lmgr/README`). |

---

## VERIFIED HIGHLIGHTS

All claims below are directly confirmed from primary source code fetched during this session.

### BusTub config.h (https://raw.githubusercontent.com/cmu-db/bustub/master/src/include/common/config.h)
| claim | verdict | note |
|-------|---------|------|
| BUSTUB_PAGE_SIZE = 8192 | SUPPORTED | Exact constant confirmed |
| BUFFER_POOL_SIZE = 128 | SUPPORTED | Exact constant confirmed |
| BUSTUB_BATCH_SIZE = 20 | SUPPORTED | Exact constant confirmed |
| LRUK_REPLACER_K = 10 (with comment "backward k-distance for lru-k") | SUPPORTED | Legacy constant: replacer is now ARC; constant remains. Briefs correctly note this as legacy. |
| TXN_START_ID = 1LL << 62 | SUPPORTED | Exact constant confirmed |
| txn_id_t = int64_t | SUPPORTED | Confirmed; makes HEADER_SIZE=20 caveat valid |
| lsn_t = int32_t | SUPPORTED | Confirmed |
| LOG_BUFFER_SIZE = (BUFFER_POOL_SIZE + 1) * BUSTUB_PAGE_SIZE | SUPPORTED | Formula confirmed = 129 * 8192 ~= 1 MB |
| #define DISABLE_LOCK_MANAGER (present in config.h) | SUPPORTED | Macro confirmed; guards UnlockAll() in destructor -- significance NOT disclosed in briefs (see Blocker B2) |

### BusTub table_page.h + tuple.h
| claim | verdict | note |
|-------|---------|------|
| TABLE_PAGE_HEADER_SIZE = 8 | SUPPORTED | `static constexpr uint64_t TABLE_PAGE_HEADER_SIZE = 8` confirmed |
| Header layout: NextPageId(4) \| NumTuples(2) \| NumDeletedTuples(2) | SUPPORTED | Exact struct confirmed |
| TupleInfo = std::tuple<uint16_t, uint16_t, TupleMeta> | SUPPORTED | Confirmed from class definition |
| TUPLE_INFO_SIZE = 24 with static_assert(sizeof(TupleInfo) == TUPLE_INFO_SIZE) | SUPPORTED | Exact assert confirmed |
| TupleMeta = {timestamp_t ts_ (8B), bool is_deleted_ (1B)} | SUPPORTED | Fields confirmed |
| TUPLE_META_SIZE = 16 with static_assert | SUPPORTED | Exact assert confirmed; 8+1+7pad = 16 |

### BusTub arc_replacer.h
| claim | verdict | note |
|-------|---------|------|
| ArcReplacer implements ARC (not LRU-K) | SUPPORTED | Class declared as `ArcReplacer implements the ARC replacement policy` |
| Four lists: mru_, mfu_, mru_ghost_, mfu_ghost_ | SUPPORTED | All four std::list members confirmed |
| mru_target_size_ (p as in original paper) | SUPPORTED | `[[maybe_unused]] size_t mru_target_size_{0}; /* p as in original paper */` |
| AccessType enum: Unknown, Lookup, Scan, Index | SUPPORTED | Confirmed exactly |

### BusTub abstract_executor.h
| claim | verdict | note |
|-------|---------|------|
| Comment: "Volcano tuple-at-a-time iterator model" | SUPPORTED | Verbatim comment confirmed |
| Next() signature is batch-at-a-time | SUPPORTED | `Next(vector<Tuple>*, vector<RID>*, size_t batch_size)` confirmed |

### BusTub log_record.h
| claim | verdict | note |
|-------|---------|------|
| HEADER_SIZE = 20 bytes (5 fields: size, LSN, transID, prevLSN, LogType) | SUPPORTED | Comment block verbatim confirmed |
| LogRecordType enum: INVALID, INSERT, MARKDELETE, APPLYDELETE, ROLLBACKDELETE, UPDATE, BEGIN, COMMIT, ABORT, NEWPAGE | SUPPORTED | All 10 values confirmed |
| prevLSN chains records per transaction | SUPPORTED | Confirmed from constructor chain |

### BusTub B+ Tree page headers
| claim | verdict | note |
|-------|---------|------|
| BPlusTreePage header: "12 bytes in total: PageType(4) \| CurrentSize(4) \| MaxSize(4)" | SUPPORTED | Source comment verbatim: "Header format (size in byte, 12 bytes in total): PageType (4) \| CurrentSize (4) \| MaxSize (4)" |
| INTERNAL_PAGE_HEADER_SIZE = 12 | SUPPORTED | Exact #define confirmed |
| LEAF_PAGE_HEADER_SIZE = 16 | SUPPORTED | Exact #define confirmed |
| LEAF_PAGE_SLOT_CNT formula includes sizeof(size_t) for tombstone buffer | SUPPORTED | Formula confirmed |
| First key in internal pages is always INVALID | SUPPORTED | Comment confirmed verbatim |

### BusTub lock_manager.h
| claim | verdict | note |
|-------|---------|------|
| 5 lock modes: SHARED, EXCLUSIVE, INTENTION_SHARED, INTENTION_EXCLUSIVE, SHARED_INTENTION_EXCLUSIVE | SUPPORTED | Exact enum values confirmed |
| Upgrade rules: IS->[S,X,IX,SIX]; S->[X,SIX]; IX->[X,SIX]; SIX->[X] | SUPPORTED | Verbatim from LOCK_NOTE comment |
| UPGRADE_CONFLICT abort for multiple concurrent upgrades | SUPPORTED | Exception name confirmed |
| waits_for_: unordered_map<txn_id_t, vector<txn_id_t>> adjacency list | SUPPORTED | Exact member confirmed |
| REPEATABLE_READ, READ_COMMITTED appear as named isolation levels in lock_manager.h comments | SUPPORTED as text in file | These labels exist in comments but ARE NOT in the IsolationLevel enum (see Blocker B1) |

### BusTub transaction.h
| claim | verdict | note |
|-------|---------|------|
| IsolationLevel enum: READ_UNCOMMITTED, SNAPSHOT_ISOLATION, SERIALIZABLE | SUPPORTED | Exactly 3 values; no READ_COMMITTED |
| TransactionState: RUNNING, TAINTED, COMMITTED, ABORTED | SUPPORTED | Exact values confirmed |
| UndoLink: {prev_txn_, prev_log_idx_} | SUPPORTED | Exact struct fields confirmed |
| UndoLog: {is_deleted_, modified_fields_, tuple_, ts_, prev_version_} | SUPPORTED | Exact fields confirmed |
| Default isolation level = SNAPSHOT_ISOLATION | SUPPORTED | Constructor default argument confirmed |

### BusTub transaction_manager.cpp
| claim | verdict | note |
|-------|---------|------|
| VerifyTxn() is a stub returning true | SUPPORTED | `auto TransactionManager::VerifyTxn(Transaction *txn) -> bool { return true; }` confirmed |
| commit_mutex_ serializes validate+write | SUPPORTED | `std::unique_lock<std::mutex> commit_lck(commit_mutex_)` in Commit() confirmed |

### BusTub optimizer.h
| claim | verdict | note |
|-------|---------|------|
| All 10 optimizer rules listed in brief | SUPPORTED | All method names confirmed: OptimizeMergeProjection, OptimizeMergeFilterNLJ, OptimizeNLJAsHashJoin, OptimizeNLJAsIndexJoin, OptimizeEliminateTrueFilter, OptimizeMergeFilterScan, OptimizeOrderByAsIndexScan, OptimizeSeqScanAsIndexScan, OptimizeColumnPruning, OptimizeSortLimitAsTopN |
| Rule-based only, no cost-based DP | SUPPORTED | No dynamic programming planner methods found |

### PostgreSQL bufpage.h + itemid.h
| claim | verdict | note |
|-------|---------|------|
| PageHeaderData 24B: pd_lsn(8)\|pd_checksum(2)\|pd_flags(2)\|pd_lower(2)\|pd_upper(2)\|pd_special(2)\|pd_pagesize_version(2)\|pd_prune_xid(4) | SUPPORTED | All fields confirmed; sum = 24B |
| WAL rule: "A dirty buffer cannot be dumped to disk until xlog has been flushed at least as far as the page's LSN" | SUPPORTED | Verbatim from bufpage.h comment |
| ItemIdData 4B: lp_off:15, lp_flags:2, lp_len:15 | SUPPORTED | Exact bitfield widths confirmed |
| LP_UNUSED=0, LP_NORMAL=1, LP_REDIRECT=2, LP_DEAD=3 | SUPPORTED | All four values confirmed |
| max addressable page size = 32KB (15-bit offset) | SUPPORTED | Implied by lp_off:15; 2^15=32768 |

### PostgreSQL htup_details.h
| claim | verdict | note |
|-------|---------|------|
| HeapTupleHeaderData fixed prefix = 23 bytes before null bitmap | SUPPORTED | Source comment: "^ - 23 bytes - ^" immediately before t_bits[] |
| MaxHeapAttributeNumber = 1600 | SUPPORTED | `#define MaxHeapAttributeNumber 1600 /* 8 * 200 */` |
| HEAP_XMIN_COMMITTED=0x0100, HEAP_XMIN_INVALID=0x0200, HEAP_XMAX_COMMITTED=0x0400, HEAP_XMAX_INVALID=0x0800, HEAP_XMAX_IS_MULTI=0x1000 | SUPPORTED | All 5 values confirmed exactly |
| t_xmin (inserting XID), t_xmax (deleting/locking XID), t_cid (command ID), t_ctid (current TID) | SUPPORTED | All field names and descriptions confirmed |

### PostgreSQL transam.h
| claim | verdict | note |
|-------|---------|------|
| InvalidTransactionId=0, BootstrapTransactionId=1, FrozenTransactionId=2, FirstNormalTransactionId=3, MaxTransactionId=0xFFFFFFFF | SUPPORTED | All 5 constants confirmed exactly |

### PostgreSQL xlogrecord.h
| claim | verdict | note |
|-------|---------|------|
| XLogRecord fields: xl_tot_len (uint32), xl_xid (TransactionId), xl_prev (XLogRecPtr), xl_info (uint8), xl_rmid (RmgrId), xl_crc (pg_crc32c) | SUPPORTED | All fields in exact order confirmed |
| SizeOfXLogRecord = offsetof(XLogRecord, xl_crc) + sizeof(pg_crc32c) | SUPPORTED | Exact macro confirmed |
| XLogRecordMaxSize = 1020 * 1024 * 1024 | SUPPORTED | Exact value confirmed |

### PostgreSQL snapshot.h
| claim | verdict | note |
|-------|---------|------|
| SnapshotData fields: snapshot_type, xmin, xmax, xip (TransactionId*), xcnt (uint32) | SUPPORTED with order caveat | Fields correct; brief shows xcnt before xip but source has xip before xcnt (see Warning W1) |

### PostgreSQL lockdefs.h
| claim | verdict | note |
|-------|---------|------|
| 8 lock modes: AccessShareLock(1)...AccessExclusiveLock(8) | SUPPORTED | All 8 values and names confirmed exactly |
| AccessExclusiveLock also covers "unqualified LOCK TABLE" | GAP | Brief omits this use case. Not wrong but incomplete. |

### PostgreSQL cost.h
| claim | verdict | note |
|-------|---------|------|
| seq_page_cost=1.0, random_page_cost=4.0, cpu_tuple_cost=0.01, cpu_index_tuple_cost=0.005, cpu_operator_cost=0.0025, parallel_tuple_cost=0.1, parallel_setup_cost=1000.0, effective_cache_size=524288 | SUPPORTED | All 8 defaults confirmed exactly from cost.h |

### PostgreSQL pathnode.c
| claim | verdict | note |
|-------|---------|------|
| STD_FUZZ_FACTOR = 1.01 | SUPPORTED | `#define STD_FUZZ_FACTOR 1.01` confirmed |

### PostgreSQL postgresql.conf.sample
| claim | verdict | note |
|-------|---------|------|
| geqo_threshold default = 12 | SUPPORTED | `#geqo_threshold = 12` confirmed |
| join_collapse_limit default = 8 | SUPPORTED | `#join_collapse_limit = 8` confirmed |
| from_collapse_limit default = 8 | SUPPORTED | `#from_collapse_limit = 8` confirmed |

### PostgreSQL tuplesort.c
| claim | verdict | note |
|-------|---------|------|
| MINORDER=6, MAXORDER=500, MERGE_BUFFER_SIZE=BLCKSZ*32, TAPE_BUFFER_OVERHEAD=BLCKSZ, SLAB_SLOT_SIZE=1024 | SUPPORTED | All 5 constants confirmed |
| States: TSS_INITIAL, TSS_BOUNDED, TSS_BUILDRUNS, TSS_SORTEDINMEM, TSS_SORTEDONTAPE, TSS_FINALMERGE | SUPPORTED | All 6 states confirmed |
| Before PG15: polyphase merge + replacement selection; After PG15: balanced k-way merge + quicksort/radix sort | SUPPORTED | Exact quote in source: "Before PostgreSQL 15, we used the polyphase merge algorithm (Knuth's Algorithm 5.4.2D)... we always use quicksort or radix sort for run generation" |

### PostgreSQL nodeHashjoin.c
| claim | verdict | note |
|-------|---------|------|
| Hybrid hash join attributed to Zeller & Gray (1990), VLDB Brisbane, pp.186-197 | SUPPORTED | Verbatim citation in nodeHashjoin.c confirmed |
| 8 HJ states: HJ_BUILD_HASHTABLE(1), HJ_NEED_NEW_OUTER(2), HJ_SCAN_BUCKET(3), HJ_FILL_OUTER_TUPLE(4), HJ_FILL_INNER_TUPLES(5), HJ_FILL_OUTER_NULL_TUPLES(6), HJ_FILL_INNER_NULL_TUPLES(7), HJ_NEED_NEW_BATCH(8) | SUPPORTED | All 8 #defines confirmed exactly |
| Parallel phases: PHJ_BUILD_ELECT through PHJ_BUILD_FREE, PHJ_BATCH_ELECT through PHJ_BATCH_FREE | SUPPORTED | All parallel phase names confirmed |

### PostgreSQL optimizer/README
| claim | verdict | note |
|-------|---------|------|
| PostgreSQL considers left-deep, right-deep, and bushy plans | SUPPORTED | README confirms "bushy plans (both inner and outer can be [join rels])" and "generate 'bushy plan' joins between joinrels of lower levels" |

### DuckDB vector_size.hpp
| claim | verdict | note |
|-------|---------|------|
| STANDARD_VECTOR_SIZE = 2048 (DEFAULT_STANDARD_VECTOR_SIZE) | SUPPORTED | `#define DEFAULT_STANDARD_VECTOR_SIZE 2048U` confirmed |
| Must be power of 2 | SUPPORTED | Compile-time `#error` (not runtime assert) confirmed |

### InnoDB (mysql-server 8.4)
| claim | verdict | note |
|-------|---------|------|
| TRX_UNDO_INSERT=1, TRX_UNDO_UPDATE=2 | SUPPORTED | Both constants confirmed from trx0undo.h |
| ReadView fields: m_low_limit_id, m_up_limit_id, m_creator_trx_id, m_ids[] | SUPPORTED | All fields confirmed from read0types.h |
| TRX_STATE_NOT_STARTED, TRX_STATE_ACTIVE, TRX_STATE_PREPARED, TRX_STATE_COMMITTED_IN_MEMORY | SUPPORTED | All confirmed; note TRX_STATE_FORCED_ROLLBACK also exists (see Warning W2) |

---

## Action items by file

### _research_storage-query-exec.md
- No blockers. All primary claims verified.
- Warning W3 (Volcano comment vs. batch Next()): brief correctly acknowledges -- maintain caveat in chapter.
- Graefe/Selinger/Crotty unverified claims: correctly marked [UNVERIFIED] -- keep tags; do not promote.

### _research_transactions-recovery.md
**Three blockers require explicit fixes before this brief can be used as a chapter source:**
1. **B1**: Rewrite Sections 1.5-1.6 to clearly label REPEATABLE_READ/READ_COMMITTED behavior as "Project 3 (2PL) design spec, NOT the active Project 4 IsolationLevel enum." The two-project design distinction must be explicit.
2. **B2**: Add a note that `#define DISABLE_LOCK_MANAGER` in config.h gates the lock manager destructor's cleanup, and that the 2PL lock manager (Project 3) and MVCC transaction manager (Project 4) are distinct non-simultaneous designs in BusTub.
3. **B3**: Replace "aborts youngest (highest txn_id)" with [NEEDS-SOURCE] or cite the BusTub Project 3 specification / .cpp implementation file directly.
- **W1 fix**: Swap xcnt/xip order in the SnapshotData struct layout.
- **W2**: Add TRX_STATE_FORCED_ROLLBACK to the InnoDB state list or note its omission.
- **W14**: Source the "PostgreSQL uses strict 2PL for table-level locks" claim.

### _research_optimizer-external-exec.md
- No blockers. All primary source claims verified.
- W13 (assert vs. #error): minor precision fix for chapter prose only.
- All paper-identity claims (Selinger, PAX, MonetDB, HyPer) correctly marked [UNVERIFIED from text] -- maintain tags.
- GEQO threshold, cost constants, tuplesort constants, hash join states, DuckDB vector size all verified.

---

## Brain resolution notes (same session)
- Fixed B1/B2 in `_research_transactions-recovery.md`: BusTub `READ_COMMITTED`/`REPEATABLE_READ`
  lock-manager behavior is now explicitly labeled as Project 3 spec-comment material, not current
  Project 4 MVCC behavior; `DISABLE_LOCK_MANAGER` is now called out.
- Fixed B3 by replacing the unsupported "youngest/highest txn_id" victim rule with `[NEEDS-SOURCE]`.
- Fixed W1 by ordering `SnapshotData` as `xip` then `xcnt`; fixed W2 by adding
  `TRX_STATE_FORCED_ROLLBACK`; softened W14 to source-needed wording.
- Fixed W13 in `_research_optimizer-external-exec.md`: DuckDB vector power-of-two check is now
  described as compile-time `#error`, not runtime assert.
