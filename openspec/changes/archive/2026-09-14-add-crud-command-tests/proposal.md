## Why

The CRUD command functions under `airembr/system/command/v1/meta/` (17 domains) have zero automated test coverage, and the repo has no storage-backed test infrastructure at all. While investigating how to add that infrastructure, an empirical smoke test surfaced a real bug: `SqliteDatabaseService._create_tables()` (and its `_create_database`/`_create_view` siblings) call `await engine.dispose()` after bootstrapping the schema. For an in-memory SQLite database (`sqlite+aiosqlite://` via `SQLITE_HOST=""`), the aiosqlite dialect binds the engine to a `StaticPool` holding a single shared connection; disposing it destroys that connection, and the next query opens a fresh, empty in-memory database. The result: every CRUD command call after `bootstrap()` fails with `sqlite3.OperationalError: no such table: ...`. This is a latent bug that nothing in the repo currently exercises, because nothing else uses `SQLITE_HOST=""`. It must be fixed before any in-memory-SQLite-backed test can run.

## What Changes

- Fix `airembr/sdk/storage/metadata/proxy/sqlite/database_service.py`: remove the `await engine.dispose()` calls from `_create_tables`, `_create_database`, and `_create_view`. Confirmed safe: the mysql counterpart's equivalent `dispose()` calls are harmless there because a fresh connection reopens the same server-backed database; for sqlite specifically, disposing the `StaticPool`'s sole connection destroys an in-memory database's contents. No behavioral change for file-backed sqlite or mysql usage.
- Add `airembr_tests/command/conftest.py`: sets `META_DATA_ADAPTER=sqlite` and `SQLITE_HOST=""` before any `airembr.*` import, and a session-scoped autouse fixture that bootstraps the in-memory schema once (inside `ServerContext(Context())`).
- Add 15 new test modules under `airembr_tests/command/test_crud_<domain>.py`, one per domain folder under `airembr/system/command/v1/meta/`, exercising each domain's actual CRUD command functions (create/read/delete, or the subset that domain actually exposes) directly against the real command functions and the in-memory SQLite backend — no mocking. Full domain-by-operation breakdown and file list are in the existing `TEST_PLAN.md` at the repo root, which this change formalizes and will supersede.
- Fix `airembr/system/adapter/metadata/mysql/service/canonical_entity_service.py`: `CanonicalEntityPropertyService.delete_by_id` called `delete_by_id_in_deployment_mode(...)` without the required `mapper` argument, so `delete_entity_property()` (the canonical-entity-property delete command) raised `TypeError` on every call — against any backend, not just sqlite. Discovered while writing `test_crud_canonical_entity.py`. Fixed by passing `map_to_canonical_entity_property`, mirroring the sibling `CanonicalEntityService.delete_by_id`, which already did this correctly.

## Capabilities

### New Capabilities
(none — this change adds test coverage and fixes an internal bug; it introduces no new externally-observable behavior)

### Modified Capabilities
(none — the sqlite `dispose()` removal only fixes a code path that currently cannot work at all for in-memory use; it does not change any documented/spec'd behavior for file-backed sqlite or mysql, which are the only backends exercised in production today)

## Impact

- **Code**: `airembr/sdk/storage/metadata/proxy/sqlite/database_service.py` (bugfix, 3 methods); `airembr/system/adapter/metadata/mysql/service/canonical_entity_service.py` (bugfix, 1 method); new `airembr_tests/command/` package (conftest + 15 test files).
- **Tests**: `pytest airembr_tests/command/ -v` must pass; `pytest airembr_tests/ -v` must show no regressions in `airembr_tests/common/` or `airembr_tests/service/` (import-order/env-leakage check).
- **No dependency changes**: no new test framework (`pytest-asyncio` intentionally not added — follows the existing `asyncio.run()`-inside-`def test_...()` pattern from `airembr_tests/service/test_llm_adapter.py`).
- **Out of scope**: `airembr/system/command/v1/list/` commands, the HTTP endpoint layer, `timer` and `user_account` domains (see TEST_PLAN.md for exclusion rationale).
