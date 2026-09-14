## Why

The GUI API's CRUD endpoints already live in a clean, versioned layout at `airembr_api/endpoint/gui/v1/routes/{meta,data}/<domain>/crud_endpoint.py`, but the command functions those endpoints call are scattered across `airembr/system/command/<domain>/` with inconsistent naming and no versioning. Mirroring the endpoint layout on the command side makes it obvious, for any given CRUD endpoint, exactly where its backing command file lives, and establishes the versioned `meta`/`data` structure that later work (organizing the non-CRUD "operations" commands) will extend.

## What Changes

- Move the command files backing today's `gui/v1` CRUD endpoints into a new `airembr/system/command/v1/{meta,data}/<domain>/` tree, mirroring the endpoint domain folders exactly (including renaming 4 domains to match the endpoint side: `event_mapping` → `payload_mapping`, `event_reshaping` → `reshaping_schema`, `event_source` → `source`, and splitting `user` into `user` / `user_account` per the endpoint split).
- Move the 5 domain `errors.py` files into a shared `airembr/system/command/v1/errors/` folder, one file per domain (`user_errors.py`, `configuration_errors.py`, `payload_mapping_errors.py`, `reshaping_schema_errors.py`, `validator_errors.py`), since `user_errors.py` is shared across two moving domains and this keeps the pattern consistent.
- File contents are relocated as-is — no functions are added, removed, split, or edited. Files that also contain non-CRUD functions (list/meta/histogram helpers) move in full; those non-CRUD functions are out of scope for reorganization in this change.
- Update the single import statement in each affected `gui/v1/.../crud_endpoint.py` to point at the new location.
- Update the single import statement in each affected legacy (pre-v1) endpoint under `airembr_api/endpoint/gui/routes/...` that still imports the same file, since 15 of the moving files are also used by a legacy endpoint.
- No endpoint routes, request/response behavior, or business logic changes. This is a pure internal file relocation.

## Capabilities

### New Capabilities
None — no user-observable or API behavior changes.

### Modified Capabilities
None — no requirement-level behavior changes; purely an internal module reorganization.

## Impact

- **Affected code**: 29 command-side files move (24 command files + 5 errors files) from `airembr/system/command/<domain>/` into `airembr/system/command/v1/{meta,data}/<domain>/` or `airembr/system/command/v1/errors/`.
- **Affected imports**: ~29 import statements in `gui/v1/.../crud_endpoint.py` files, plus ~15 import statements in legacy `gui/routes/...` endpoint files that share the same underlying command modules.
- **Not affected**: endpoint routing/behavior, command function bodies, non-CRUD commands staying in their current locations (to be organized in a later change), database/service layers the commands call into.
