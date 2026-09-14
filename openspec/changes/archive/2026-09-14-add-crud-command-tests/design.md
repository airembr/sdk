## Context

See proposal.md - Why for the discovery of the sqlite `dispose()` bug. This document covers the two things that need a deliberate technical decision: how to fix that bug, and how the shared in-memory test DB is bootstrapped and used across 16 test files. Per-domain model fields, DAO calls, and the exact list of files to create are already enumerated in `TEST_PLAN.md` (repo root) and are not repeated here — this design references that plan rather than restating it.

## Goals / Non-Goals

**Goals:**
- Make `SQLITE_HOST=""` (in-memory) sqlite usable at all for `DatabaseServiceProxy().bootstrap()` + subsequent DAO calls in the same process.
- Give every domain's CRUD commands direct, mock-free integration coverage against that in-memory backend.

**Non-Goals:**
- Changing MySQL behavior, or any file-backed sqlite behavior — the fix only removes a call that is provably inert for those cases (verified: `_create_tables`/`_create_database`/`_create_view` are symmetric between the mysql and sqlite `DatabaseService` classes; MySQL's `dispose()` is harmless because a new connection reconnects to the same server-backed database).
- Adding `pytest-asyncio`, a DB-reset-between-tests mechanism, or a CRUD base class/dispatcher — none exist today and the plan doesn't need them (see TEST_PLAN.md's "Key findings").
- Testing the `list/` commands or the HTTP endpoint layer (out of scope per proposal).

## Decisions

**1. Fix the bug in production code, not by working around it in test setup.**
Rejected alternatives (both investigated and confirmed technically workable during exploration):
- *Bypass `DatabaseServiceProxy().bootstrap()` in `conftest.py`* (call `Base.metadata.create_all` directly via `AsyncSqliteEngine().get_engine_for_database()`, skip `dispose()`) — works, but means the tests no longer exercise the real bootstrap path, and the underlying bug would remain latent for any future code that does the same thing (e.g. a local dev workflow that sets `SQLITE_HOST=""`).
- *Use a temp-file-backed sqlite DB instead of true in-memory* (`SQLITE_HOST=<tempdir>/test.sqlite`, cleaned up at session teardown) — sidesteps the bug entirely since file-backed connections just reopen the same file after `dispose()`. Rejected because it silently trades away the "in-memory, no files" requirement instead of fixing the actual defect, and the fix (see below) is a 3-line removal with no observed downside.

Chosen: remove `await engine.dispose()` from `_create_tables`, `_create_database`, `_create_view` in `airembr/sdk/storage/metadata/proxy/sqlite/database_service.py`. Verified empirically (scratch smoke test): with the calls removed, `DatabaseServiceProxy().bootstrap()` followed by real `save_ontology()`/`get_ontology()`/`delete_ontology()` calls succeeds end-to-end against `SQLITE_HOST=""`. Without the fix, the same sequence fails immediately with `sqlite3.OperationalError: no such table: sys_ontology`, because the aiosqlite dialect binds in-memory URLs to a `StaticPool` (single shared connection), and `dispose()` closes that connection — the next checkout opens a brand-new, empty in-memory database.

**2. Session-scoped, autouse bootstrap fixture in `airembr_tests/command/conftest.py`.**
Sets `META_DATA_ADAPTER`/`SQLITE_HOST` at module import time (before any `airembr.*` import reaches `db_config.py`'s module-level `os.environ.get(...)` read), then bootstraps the schema once per test session inside `with ServerContext(Context()):`. All 16 test files share this one in-memory database for the process lifetime of the test run — matches TEST_PLAN.md's approach of test-scoped unique IDs (`f"test-{domain}-{uuid4()}"`) rather than resetting state between tests, since there is no reset mechanism and none is being added.

**3. No changes to MySQL code path.** Confirmed `MysqlDatabaseService` bootstrap is structurally identical (`_create_database` then `_create_tables`, both `dispose()`-terminated) but is unaffected by this change since these tests never select `META_DATA_ADAPTER=mysql`.

## Risks / Trade-offs

- **[Risk]** Removing `dispose()` in the sqlite `DatabaseService` leaves engine connections open slightly longer after bootstrap/create_database/create_view calls than before. → **Mitigation**: these are one-time setup operations (bootstrap runs once per process in production per `md_install_manager.py`, and per-call in `list/bridge/list.py` but only for a lightweight existence check), not hot paths; the engine itself is a cached singleton (`AsyncSqliteEngine` via `Singleton` metaclass) for the life of the process either way, so no unbounded connection growth.
- **[Risk]** All 16 test files share one in-memory DB with no reset between tests, relying entirely on unique per-test IDs to avoid collisions. → **Mitigation**: this matches the existing plan and repo convention (no test DB reset infra exists anywhere else in the repo either); each test file uses distinct id prefixes per TEST_PLAN.md.
- **[Trade-off]** Tests are real integration tests against a real (if in-memory) SQLAlchemy/aiosqlite stack rather than unit tests with mocks — slower to write per TEST_PLAN.md's per-domain model research step, but they catch real wiring bugs (as demonstrated by this very investigation) that a mocked DAO layer would hide.
