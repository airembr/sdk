## Why

Command files under `airembr/system/command/v1/{meta,data}/<domain>/` mix single-item CRUD functions (get/save/add/edit/upsert/delete by id) with list, histogram, meta/type-lookup, and other multi-record query functions. This makes it unclear, when looking at a `list_endpoint.py`'s backing command file, which functions actually belong to that CRUD endpoint versus which are only used by legacy list-oriented endpoints. Separating list operations into their own `command/v1/list/<domain>/` tree extends the `v1` reorganization pattern established by the prior CRUD-to-`v1` move and gives list operations a home mirroring the eventual `list_endpoint.py` pattern already scaffolded (but unused) under `gui/v1/routes/meta/bridge/`.

## What Changes

- Move every non-single-item-CRUD function (list_*, histogram, meta/type lookups, by-tag/by-entity queries, and other multi-record or derived-aggregate functions) out of the 17 mixed files under `airembr/system/command/v1/{meta,data}/<domain>/` into a new `airembr/system/command/v1/list/<domain>/list.py` per domain (16 new `list.py` files; `canonical_entity` merges functions from two source files into one `list.py`).
- Functions that are single-item CRUD (get/save/add/edit/upsert/delete/get-by-id) stay in their existing file and location.
- Private helper functions used only by moving list functions (e.g. `_apply_where_filter`, `_shorten_texts` in the event/observation data files) move with them.
- File contents are relocated as-is — no functions are added, removed, or edited beyond moving them and adjusting imports where a moved function's dependency needs to be duplicated/pointed at.
- Update the import statements in the legacy (pre-v1) `gui/routes/...` endpoint files that import the moving functions (16 files) to point at the new `command/v1/list/<domain>/list.py` location.
- No changes needed to any `gui/v1/.../crud_endpoint.py` file — verified that every v1 CRUD endpoint already imports only single-item CRUD functions, none of which are moving.
- Scope is strictly `airembr/system/command/v1/{meta,data}/**`. Legacy (pre-v1) command modules outside `command/v1/` are untouched. Domains with no list-shaped functions (`task`, `timer`, `user_account`, and the `user` domain's `add_user.py`/`delete_user.py`/`edit_user.py`/`get_user.py` files) are untouched.
- No endpoint routes, request/response behavior, or business logic changes. This is a pure internal file/function relocation.

## Capabilities

### New Capabilities
None — no user-observable or API behavior changes.

### Modified Capabilities
None — no requirement-level behavior changes; purely an internal module reorganization. (`skip_specs: true` set in `.openspec.yaml`.)

## Impact

- **Affected code**: 17 source files (16 domains; `canonical_entity` has 2 source files) lose their list-shaped functions; 16 new `command/v1/list/<domain>/list.py` files are created to receive them.
- **Affected imports**: ~16 legacy `gui/routes/...` endpoint files update their import statements to the new list module paths. Zero `gui/v1/.../crud_endpoint.py` files require changes.
- **Not affected**: endpoint routing/behavior, function bodies, single-item CRUD functions and their current file locations, `command/v1/errors/` (unchanged, still imported by absolute path from wherever a function using it now lives), domains/files with no list-shaped functions.
