## Why

The GUI API's per-record CRUD endpoints (under `airembr_api/endpoint/gui/v1/routes/meta/`) grew organically: some use `/v2/<segment>`, some have no version prefix, some nest path segments in inconsistent order, and handler function names mix `get_`/`load_`, `save_`/`add_`/`upsert_`/`edit_`, and `delete_`/`del_` conventions. One file (`embedding_setting`) even has handlers still literally named `get_segment`/`save_segment`/`delete_segment`, a copy-paste artifact from the `segment` domain. This makes the API harder to document, generate clients for, and reason about consistently. We want every domain's single-record CRUD to live at a predictable `/v1/<domain-object>` path with a predictable function name, without changing any existing behavior or removing existing routes.

## What Changes

- Add a `/v1/<domain-object>` route (and, where the same handler serves both, additional decorators) alongside every existing route in the 17 `routes/meta/*/crud_endpoint.py` files, so old and new paths both resolve to the same handler.
- Standardize handler function names to: `get_<domain>_by_id` (GET), `save_<domain>` (POST create or upsert), `update_<domain>` (POST edit-by-id, only where a domain already has a separate edit-only handler distinct from create), `delete_<domain>_by_id` (DELETE). No PATCH is introduced — POST remains the sole write verb, matching current behavior (no domain currently has real partial-update semantics).
- Fix the `embedding_setting` handlers' copy-pasted names (`get_segment`/`save_segment`/`delete_segment` -> `get_embedding_setting_by_id`/`save_embedding_setting`/`delete_embedding_setting_by_id`).
- Treat self-scoped or independently-keyed sub-resources (`user` preference, `canonical_entity` property GET/DELETE) as their own flat `/v1/<domain-object>` paths rather than nesting them under a parent id, since their handlers don't accept a parent id parameter today and we are not changing signatures.
- Nest sub-resources that do carry a parent id in their existing signature (e.g. `canonical_entity` property POST, which already takes `entity_id`) under the parent path: `/v1/canonical-entity/{entity_id}/property`.
- Existing `/v2/...` and unversioned routes are left in place, untouched, on the same handlers.
- Document the full old-path -> new-path and old-function -> new-function mapping in `ENDPOINT_MAPPING.md` at the `sdk/` root.
- **BREAKING**: none. This is purely additive at the routing layer (new decorators on existing handlers); no existing route, request/response shape, or command logic changes. Renaming handler functions is a Python-internal rename, not a wire-level change — decorators still bind by reference, not by name.

## Capabilities

### New Capabilities
- `gui-api/canonical-v1-crud`: every meta-domain single-record CRUD endpoint (get/save/update/delete) is exposed at a canonical `/v1/<domain-object>` path with a standardized handler function name, alongside its existing legacy path(s).

### Modified Capabilities
(none — no existing spec covers this API surface today)

## Impact

- Code: 17 files under `sdk/airembr_api/endpoint/gui/v1/routes/meta/*/crud_endpoint.py` (bridge, canonical_entity, configuration, destination, embedding_setting, entity_object, ontology, payload_mapping, reshaping_schema, resource, segment, source, task, timer, user, user_account, validator).
- Docs: new `sdk/ENDPOINT_MAPPING.md`.
- No changes to `airembr.system.command.v1.meta.*` command modules, request/response models, or the "list/search" endpoint files (`routes/<domain>_endpoint.py`) — those are out of scope.
- No changes to any code outside `airembr_api/endpoint/gui/v1/routes/` (per explicit scope confirmation).
