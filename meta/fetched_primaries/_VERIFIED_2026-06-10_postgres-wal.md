Source: https://www.postgresql.org/docs/current/wal-intro.html
Fetched: 2026-06-10 (Wave 12). HTTP 200. Network healed for postgresql.org.

VERBATIM load-bearing quotes (Write-Ahead Logging chapter, PostgreSQL current docs):

- "Write-Ahead Logging (WAL) is a standard method for ensuring data integrity."

- "WAL's central concept is that changes to data files (where tables and indexes reside)
   must be written only after those changes have been logged, that is, after WAL records
   describing the changes have been flushed to permanent storage. If we follow this procedure..."
   (the WAL rule: log-before-data; the log is the source of truth for recovery)

- "Because WAL restores database file contents after a crash, journaled file systems are not
   necessary for reliable storage of the data files or WAL files."

- "Using WAL results in a significantly reduced number of disk writes, because only the WAL file
   needs to be flushed to disk to guarantee that a transaction is committed, rather than every
   data file changed by the transaction. The WAL file is written sequential[ly]..."
   (sequential append + flush-on-commit = the durability primitive; the same log abstraction as 09)

- "...roll-forward recovery, also known as REDO."
   (crash recovery = replay the log forward from the last checkpoint)

NOTE: the rendered docs page collapses some paragraphs ("[truncated]" in the text view); the
sentences above were extracted verbatim from the raw HTML, not the collapsed view.

APPLIES TO (upgrade carried [UNVERIFIED] -> VERIFIED where these claims were asserted):
- 07 database-internals: WAL = log-before-data; flush-on-commit; sequential append; REDO recovery.
- 15 replication-and-consistency-in-practice: the WAL/replication log as the durable, replayable
  ordering primitive shipped to replicas.
- 26 state-persistence-and-resume (Part III): the agent transcript-as-WAL durability model.
