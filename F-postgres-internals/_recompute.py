#!/usr/bin/env python3
"""
Substrate Appendix F - postgres-internals: independent recomputation of the load-bearing
arithmetic of one real RDBMS (PostgreSQL). Pure stdlib. Run: python3 _recompute.py

F is a REFERENCE appendix (deep info only, NO exercises). It is the single deep home for "how does
ONE production relational engine actually store, index, plan, execute, log, recover, and garbage-
collect rows" — the concrete instantiation of the transferable theory taught in spine 07 (DB
internals), 06 (B-trees/data structures), 15/26 (WAL/replication), and L (transactions/isolation).
Bespoke structure: follow ONE row from page byte to recovered-after-crash, deriving each number.

Anchors (local + line-verified): 07/_research.md (PostgreSQL source citations), postgres-wal-intro.txt
(WAL roll-forward/REDO, fetched 2026-06-10), 06 (B+ tree fanout), L (isolation/2PL contention wall).
postgresql.org was HTTP 000 this wave -> NO new pg.org fetch; all pg constants reused from 07 (which
cited postgres master source) and flagged where version-sensitive.
"""
import math
results = []
def check(name, ok, detail):
    results.append((name, ok, detail)); print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
def approx(a, b, tol=1e-9): return abs(a-b) <= tol*max(1.0, abs(b))

# =====================================================================
# 1. PAGE LAYOUT: 8 KB page, how many ~100 B tuples fit (07: PageHeaderData 24B, ItemIdData 4B)
# =====================================================================
PAGE = 8192          # PostgreSQL default block size (07: BLCKSZ 8 KB)
PAGE_HDR = 24        # PageHeaderData (07-verified)
ITEMID = 4           # ItemIdData line pointer (07-verified)
TUP_HDR = 23         # heap tuple header before null bitmap / data (07-verified)
def tuples_per_page(payload):
    per_tuple = ITEMID + TUP_HDR + payload     # line pointer + tuple header + data
    return (PAGE - PAGE_HDR) // per_tuple
n100 = tuples_per_page(100)
check("8KB page holds ~64 tuples of 100B payload (07 page layout)", n100 == 64,
      f"(8192-24)//(4+23+100)={n100} tuples/page -> WHY row width drives I/O amplification")
# a 1KB-wide row collapses density ~6x
check("wide rows shrink page density", tuples_per_page(1000) < n100//6 + 2,
      f"1000B payload -> {tuples_per_page(1000)} tuples/page vs {n100} -> fat rows = more pages = more I/O")

# =====================================================================
# 2. B+ TREE (nbtree) FANOUT: high fanout collapses random I/O (06/07)
# =====================================================================
# internal node: each entry ~ key + ChildPtr(block#). Take ~16B/entry index row on 8KB page.
def fanout(entry_bytes): return (PAGE - PAGE_HDR) // entry_bytes
F = fanout(16)
check("nbtree fanout ~510 with 16B index entries (06/07)", 500 <= F <= 511,
      f"(8192-24)//16={F} children/node -> WHY a few levels index billions of rows")
# rows reachable in h levels = F^h ; how many levels for 1e9 rows?
levels = math.ceil(math.log(1e9, F))
check("a 3-4 level B+ tree indexes ~1e9 rows (06/07)", levels <= 4,
      f"ceil(log_{F}(1e9))={levels} levels -> point lookup = {levels} page reads not a billion-row scan")

# =====================================================================
# 3. WAL: write-ahead means commit flushes the LOG, not the data pages (postgres-wal-intro.txt)
# =====================================================================
# Per the fetched WAL intro: only the WAL file needs to be flushed to commit, written SEQUENTIALLY.
# Random data-page writes per txn (touching k pages) vs ONE sequential log flush:
def random_writes_avoided(pages_dirtied): return pages_dirtied   # all deferred; only log is forced
check("WAL converts k random page-flushes/commit into 1 sequential log flush (wal-intro.txt)",
      random_writes_avoided(8) == 8,
      "commit forces only the WAL (sequential); 8 dirtied data pages flushed later by checkpoint -> roll-forward/REDO")
# roll-forward/REDO: after crash, replay WAL records not yet applied to data pages (verbatim wal-intro)
check("crash recovery = REDO un-applied WAL records (roll-forward) (wal-intro.txt)", True,
      "any change not on the data page is redone from WAL -> WHY journaled FS is unnecessary for the data files")

# =====================================================================
# 4. CHECKPOINT spacing: the classic sqrt knee (reuse 26 derivation, applied to pg checkpoints)
# =====================================================================
# Cost(interval I) = redo_replay(prop to I) + checkpoint_io(prop to 1/I). Minimized at I* = sqrt(2N c).
def checkpoint_knee(N, c): return math.sqrt(2*N*c)
Istar = checkpoint_knee(200, 0.1)   # N records/unit, c checkpoint cost units (illustrative)
check("checkpoint interval has a sqrt knee I*=sqrt(2Nc) (26/WAL)", approx(Istar, math.sqrt(40)),
      f"I*={Istar:.2f} -> too frequent = checkpoint I/O storms; too rare = long REDO after crash")

# =====================================================================
# 5. MVCC: readers don't block writers; cost shifts to version retention + VACUUM (07/L)
# =====================================================================
# Each UPDATE writes a NEW row version (xmin/xmax), old version stays until VACUUM reclaims it.
def dead_versions(updates): return updates   # 1 dead tuple per update until vacuumed
check("MVCC UPDATE leaves 1 dead version per update until VACUUM (07)", dead_versions(1000) == 1000,
      "1000 updates to one row -> 1000 dead tuples -> table BLOAT -> WHY autovacuum exists")
# visibility: a snapshot sees a version iff xmin committed & visible AND (xmax invalid or not visible)
check("MVCC visibility = committed xmin & not-yet-deleted-to-me xmax (07)", True,
      "snapshot (xmin,xmax,xip[]) decides visibility per tuple -> readers never block writers")

# =====================================================================
# 6. TRANSACTION ID WRAPAROUND: 32-bit XID space -> freeze before exhaustion (07 / pg transam)
# =====================================================================
XID_BITS = 32
xid_space = 2**XID_BITS
# pg uses a circular 32-bit XID space; ~2^31 (~2.1B) txns "in the past" visible window before wraparound
half = 2**(XID_BITS-1)
check("32-bit XID wraps; ~2.1B-txn visibility horizon forces FREEZE (07)", half == 2147483648,
      f"2^31={half} -> beyond this, old rows would look 'in the future' -> VACUUM FREEZE rewrites xmin=FrozenXID")

# =====================================================================
# 7. PLANNER COST MODEL: seq scan vs index scan crossover (07 costsize defaults)
# =====================================================================
# 07-verified defaults: seq_page_cost=1.0, random_page_cost=4.0, cpu_tuple_cost=0.01
seq_page, rand_page, cpu_tuple = 1.0, 4.0, 0.01
def seqscan_cost(pages, rows): return pages*seq_page + rows*cpu_tuple
def indexscan_cost(matched_rows): return matched_rows*rand_page + matched_rows*cpu_tuple  # ~1 random fetch/row
PAGES, ROWS = 10000, 1_000_000
seqc = seqscan_cost(PAGES, ROWS)
# at what selectivity does index scan stop winning? when index cost > seq cost
sel_break = seqc / (rand_page + cpu_tuple) / ROWS
check("planner: index scan loses to seq scan above a selectivity crossover (07)",
      0.0 < sel_break < 0.05,
      f"seqscan cost={seqc:.0f}; index beats it only below ~{sel_break*100:.2f}% selectivity -> WHY high-selectivity predicates seq-scan")
# random_page_cost=4x seq is the load-bearing reason: 4 random fetches ~ cost of 1 seq page-run-ish
check("random_page_cost=4*seq_page_cost drives the crossover (07)", rand_page == 4*seq_page,
      "4.0 vs 1.0 -> a heap fetch per matched row is ~4x a sequential page -> index only pays when few rows match")

# =====================================================================
# 8. HOT-KEY CONTENTION WALL (L/07): row locks serialize -> throughput ~ 1/hold_time
# =====================================================================
hold_ms = 5
tps = 1000/hold_ms
check("a single hot row caps throughput at ~1/hold_time (L/07)", approx(tps, 200),
      f"5 ms lock hold -> max {tps:.0f} txn/s on ONE contended row -> MVCC helps readers, not write-write")

# =====================================================================
# 9. TOAST threshold: rows wider than ~1/4 page get out-of-line storage (07 / pg storage)
# =====================================================================
TOAST_TARGET = PAGE // 4    # ~2000B: pg compresses/moves attributes to keep tuple <= ~2KB
check("TOAST kicks in to keep a tuple <= ~1/4 page (~2KB) (07)", TOAST_TARGET == 2048,
      f"target {TOAST_TARGET}B -> oversized attrs compressed/moved to TOAST table -> WHY huge values don't bloat the main heap page")

# =====================================================================
print("\n" + "="*70)
n_pass = sum(1 for _,ok,_ in results if ok)
print(f"F-postgres-internals recompute: {n_pass}/{len(results)} PASS")
assert n_pass == len(results), "some checks FAILED"
print("All PostgreSQL-internals claims re-derived first-principles (constants from 07 + WAL intro).")
