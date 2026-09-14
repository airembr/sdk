## 1. Fix the sqlite in-memory bootstrap bug

- [x] 1.1 Remove `await engine.dispose()` from `_create_tables`, `_create_database`, and `_create_view` in `airembr/sdk/storage/metadata/proxy/sqlite/database_service.py`. Verify with a standalone scratch script (not committed): set `META_DATA_ADAPTER=sqlite` and `SQLITE_HOST=""`, call `DatabaseServiceProxy().bootstrap()`, then `save_ontology`/`get_ontology`/`delete_ontology` from `airembr.system.command.v1.meta.ontology.ontology` inside `ServerContext(Context())` — all three must succeed with no `OperationalError`.

## 2. Test infrastructure

- [x] 2.1 Create `airembr_tests/command/conftest.py`: set `os.environ["META_DATA_ADAPTER"] = "sqlite"` and `os.environ["SQLITE_HOST"] = ""` at the very top, before any other import; add a session-scoped autouse fixture that runs `asyncio.run(DatabaseServiceProxy().bootstrap())` once inside `with ServerContext(Context()):`. Verify by running `pytest airembr_tests/command/ -v --collect-only` (no import errors, even with zero test files yet).

## 3. Read-only domain

- [x] 3.1 `airembr_tests/command/test_crud_bridge.py` — read-only coverage of `get_data_bridge_by_id` (found + not-found cases). Verify: `pytest airembr_tests/command/test_crud_bridge.py -v` passes.

## 4. Simple create/read/delete domains

- [x] 4.1 `airembr_tests/command/test_crud_destination.py`
- [x] 4.2 `airembr_tests/command/test_crud_embedding_setting.py`
- [x] 4.3 `airembr_tests/command/test_crud_entity_object.py`
- [x] 4.4 `airembr_tests/command/test_crud_ontology.py`
- [x] 4.5 `airembr_tests/command/test_crud_segment.py`
- [x] 4.6 `airembr_tests/command/test_crud_source.py`

For each: read the domain's model class first (`airembr/model/metadata/` or `airembr/model/system/`) to build a minimal valid instance, then write create+read and delete tests per the shape in TEST_PLAN.md. Verify: `pytest airembr_tests/command/test_crud_<domain>.py -v` passes for each.

## 5. Create/read/delete domains with 404-on-missing-get

- [x] 5.1 `airembr_tests/command/test_crud_configuration.py` — assert `ConfigurationError` from `airembr/system/command/v1/errors/configuration_errors.py` on get-after-delete and get-of-never-existed.
- [x] 5.2 `airembr_tests/command/test_crud_payload_mapping.py` — assert the corresponding error from `payload_mapping_errors.py`.
- [x] 5.3 `airembr_tests/command/test_crud_reshaping_schema.py` — assert the corresponding error from `reshaping_schema_errors.py`.
- [x] 5.4 `airembr_tests/command/test_crud_validator.py` — assert the corresponding error from `validator_errors.py`.

Verify: `pytest airembr_tests/command/test_crud_configuration.py airembr_tests/command/test_crud_payload_mapping.py airembr_tests/command/test_crud_reshaping_schema.py airembr_tests/command/test_crud_validator.py -v` passes.

## 6. Multi-entity / non-standard-verb domains

- [x] 6.1 `airembr_tests/command/test_crud_canonical_entity.py` — create/read/delete for both entity (`entities.py`) and property (`properties.py`). Also fixed a pre-existing production bug found while writing this test: `CanonicalEntityPropertyService.delete_by_id` in `airembr/system/adapter/metadata/mysql/service/canonical_entity_service.py` called `delete_by_id_in_deployment_mode(...)` without the required `mapper` argument, so `delete_entity_property()` raised `TypeError` on every call regardless of backend. Fixed by passing `map_to_canonical_entity_property`.
- [x] 6.2 `airembr_tests/command/test_crud_resource.py` — create/upsert, read, delete (`resource.py`).
- [x] 6.3 `airembr_tests/command/test_crud_task.py` — upsert (create+update via `upsert_task.py`), delete only (`delete_task.py`); no get exists for this domain.

Verify: `pytest airembr_tests/command/test_crud_canonical_entity.py airembr_tests/command/test_crud_resource.py airembr_tests/command/test_crud_task.py -v` passes.

## 7. User domain

- [x] 7.1 `airembr_tests/command/test_crud_user.py` — create, read, update, delete via `add_user.py`/`get_user.py`/`edit_user.py`/`delete_user.py`; assert 409 on duplicate email and 404 on not-found (exact error types from `user_errors.py`). Verify: `pytest airembr_tests/command/test_crud_user.py -v` passes.

## 8. Full verification

- [x] 8.1 Run `pytest airembr_tests/command/ -v` from the repo root and confirm all tests across all 15 files pass.
- [x] 8.2 Run `pytest airembr_tests/ -v` (full existing suite) and confirm no regressions or env-var leakage into `airembr_tests/common/` or `airembr_tests/service/` — import order matters, since `command/conftest.py`'s env vars must not affect modules collected outside `airembr_tests/command/`.
