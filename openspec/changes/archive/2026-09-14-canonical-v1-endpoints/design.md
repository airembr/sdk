## Context

See proposal.md - Why. All 17 target files already share one shape: a FastAPI `router = APIRouter(...)` plus one `@router.<verb>(...)` decorator per handler, no global path prefix applied at `include_router()` time (every path is a literal string in the decorator). This means each new canonical route is just another decorator stacked on the existing handler function (FastAPI supports multiple decorators on one function), and a rename of the function is purely a Python-internal identifier change - decorators bind to the function object, not its name, and no code outside these files imports these handlers by name (verified: `grep -rn "import.*<handler_name>"` across the repo found no external references for the renamed handlers).

Scope is explicitly limited to files under `airembr_api/endpoint/gui/v1/routes/` (confirmed by user) - this covers all 17 `routes/meta/*/crud_endpoint.py` files. The sibling `routes/<domain>_endpoint.py` "list/search" files and the `airembr.system.command.v1.meta.*` command modules are untouched.

## Goals / Non-Goals

**Goals:**
- Every domain gets a canonical `/v1/<domain-object>` route per verb it already supports, stacked onto the existing handler.
- Handler function names become consistent: `get_<domain>_by_id`, `save_<domain>`, `update_<domain>` (only where create/edit are already separate), `delete_<domain>_by_id`.
- Fix the `embedding_setting` copy-paste bug (handlers literally named after `segment`).
- Produce `sdk/ENDPOINT_MAPPING.md` documenting every old path/function -> new path/function.

**Non-Goals:**
- No PATCH endpoints, no new update-only command logic. POST remains the sole write verb (see spec: "Create and update stay distinct where they already are").
- No removal or modification of any existing `/v2/...` or unversioned route.
- No change to command modules, request/response models, or list/search endpoints.
- No change to files outside `airembr_api/endpoint/gui/v1/routes/`.

## Decisions

**Domain-object slug source: folder name under `routes/meta/`.** Considered deriving from the Pydantic model name or preserving the old path segment, but both disagree with each other in several places (e.g. `EntitySegment` model vs `/segment` path vs `segment` folder) with no single consistent rule. The folder name is already the identifier chosen when lists were split from CRUD (see commit "Separated the lists from crud") and lines up with the command module path (`system.command.v1.meta.<folder>`), so it's the most internally consistent anchor. Accepted consequence: `source` (folder name) replaces the more descriptive `event-source` (old path) as the v1 slug - a deliberate one-off naming regression accepted for consistency.

**Self-scoped/independently-keyed sub-resources get flat v1 paths, not nested ones.** `user` preference and `canonical_entity` property GET/DELETE resolve their "parent" from auth context or from a self-sufficient id, not from a path parameter in the existing function signature. Nesting them under a parent id (e.g. `/v1/user/{id}/preference/{key}`) would require adding a parameter the handler doesn't have - a signature/behavior change, which is out of scope for an additive routing-only change. `canonical_entity` property's POST, which already takes `entity_id`, is nested (`/v1/canonical-entity/{entity_id}/property`); its GET/DELETE (property-id only) become the flat `/v1/canonical-entity-property/{id}`.

**Create vs. update naming split preserved even without PATCH.** Only `user` has genuinely separate create-only and edit-only handlers (`add_user` vs `edit_user`). Renaming both to `save_user` would collide in meaning (and, since they're different functions on different paths, isn't a Python identifier collision, but would make it impossible to tell from the name alone which does what). Keeping `save_user` (create) / `update_user` (edit-by-id) preserves the intent signal even though both are POST.

**Renames applied in this same pass, not deferred.** The user's own worked example (`get_destination` -> `get_destination_by_id`) already established that fixing non-canonical names is part of "adding canonical annotation," not a separate step. Applying the `embedding_setting` bug fix and all other renames now avoids a second pass that would touch the same lines again.

## Full endpoint mapping (see also `sdk/ENDPOINT_MAPPING.md`, generated as a task)

| Domain (folder) | Verb | Legacy path | v1 path | Legacy fn | v1 fn |
|---|---|---|---|---|---|
| bridge | GET | `/v2/bridge/{bridge_id}` | `/v1/bridge/{bridge_id}` | `get_data_bridge_by_id` | `get_bridge_by_id` |
| canonical_entity | GET | `/v2/canonical/entity/{id}` | `/v1/canonical-entity/{id}` | `load_canonical_entity_by_id` | `get_canonical_entity_by_id` |
| canonical_entity | POST | `/v2/canonical/entity` | `/v1/canonical-entity` | `save_canonical_entity` | `save_canonical_entity` |
| canonical_entity | DELETE | `/v2/canonical/entity/{id}` | `/v1/canonical-entity/{id}` | `delete_canonical_entity` | `delete_canonical_entity_by_id` |
| canonical_entity (property) | GET | `/v2/canonical/entity/property/{id}` | `/v1/canonical-entity-property/{id}` | `load_entity_property` | `get_canonical_entity_property_by_id` |
| canonical_entity (property) | POST | `/v2/canonical/entity/{entity_id}/property` | `/v1/canonical-entity/{entity_id}/property` | `save_entity_property` | `save_canonical_entity_property` |
| canonical_entity (property) | DELETE | `/v2/canonical/entity/property/{id}` | `/v1/canonical-entity-property/{id}` | `delete_entity_property` | `delete_canonical_entity_property_by_id` |
| configuration | GET | `/configuration/{id}` | `/v1/configuration/{id}` | `get_configuration` | `get_configuration_by_id` |
| configuration | POST | `/configuration` | `/v1/configuration` | `add_configuration` | `save_configuration` |
| configuration | DELETE | `/configuration/{id}` | `/v1/configuration/{id}` | `delete_configuration` | `delete_configuration_by_id` |
| destination | GET | `/destination/{destination_id}` | `/v1/destination/{destination_id}` | `get_destination` | `get_destination_by_id` |
| destination | POST | `/v2/destination` | `/v1/destination` | `save_destination` | `save_destination` |
| destination | DELETE | `/destination/{destination_id}` | `/v1/destination/{destination_id}` | `delete_destination_by_id` | `delete_destination_by_id` |
| embedding_setting | GET | `/v2/embedding/{embedding_id}` | `/v1/embedding-setting/{embedding_id}` | `get_segment` | `get_embedding_setting_by_id` |
| embedding_setting | POST | `/v2/embedding` | `/v1/embedding-setting` | `save_segment` | `save_embedding_setting` |
| embedding_setting | DELETE | `/v2/embedding/{embedding_id}` | `/v1/embedding-setting/{embedding_id}` | `delete_segment` | `delete_embedding_setting_by_id` |
| entity_object | POST | `/v2/entity/object` | `/v1/entity-object` | `save_entity_object` | `save_entity_object` |
| entity_object | GET | `/v2/entity/object/{entity_type_id}` | `/v1/entity-object/{entity_type_id}` | `get_entity_object_payload` | `get_entity_object_by_id` |
| entity_object | DELETE | `/v2/entity/object/{entity_type_id}` | `/v1/entity-object/{entity_type_id}` | `delete_entity_object` | `delete_entity_object_by_id` |
| ontology | GET | `/v2/ontology/{id}` | `/v1/ontology/{id}` | `load_ontology_by_id` | `get_ontology_by_id` |
| ontology | POST | `/v2/ontology` | `/v1/ontology` | `save_ontology` | `save_ontology` |
| ontology | DELETE | `/v2/ontology/{id}` | `/v1/ontology/{id}` | `delete_ontology` | `delete_ontology_by_id` |
| payload_mapping | POST | `/event-type/mapping` | `/v1/payload-mapping` | `add_event_type_mapping` | `save_payload_mapping` |
| payload_mapping | GET | `/event-type/mapping/{event_type_id}` | `/v1/payload-mapping/{event_type_id}` | `get_event_mapping_by_id` | `get_payload_mapping_by_id` |
| payload_mapping | DELETE | `/event-type/mapping/{event_type_id}` | `/v1/payload-mapping/{event_type_id}` | `del_event_type_metadata` | `delete_payload_mapping_by_id` |
| reshaping_schema | POST | `/event-reshape-schema` | `/v1/reshaping-schema` | `add_reshape_schema` | `save_reshaping_schema` |
| reshaping_schema | DELETE | `/event-reshape-schema/{id}` | `/v1/reshaping-schema/{id}` | `delete_reshape_schema` | `delete_reshaping_schema_by_id` |
| reshaping_schema | GET | `/event-reshape-schema/{id}` | `/v1/reshaping-schema/{id}` | `get_reshape_schema` | `get_reshaping_schema_by_id` |
| resource | GET | `/resource/{id}` | `/v1/resource/{id}` | `get_resource_by_id` | `get_resource_by_id` |
| resource | POST | `/resource` | `/v1/resource` | `upsert_resource` | `save_resource` |
| resource | DELETE | `/resource/{id}` | `/v1/resource/{id}` | `delete_resource` | `delete_resource_by_id` |
| segment | POST | `/v2/segment` | `/v1/segment` | `save_segment` | `save_segment` |
| segment | GET | `/v2/segment/{segment_id}` | `/v1/segment/{segment_id}` | `get_segment` | `get_segment_by_id` |
| segment | DELETE | `/segment/{segment_id}` | `/v1/segment/{segment_id}` | `delete_segment` | `delete_segment_by_id` |
| source | GET | `/v2/event-source/{id}` | `/v1/source/{id}` | `load_source_by_id` | `get_source_by_id` |
| source | POST | `/v2/event-source` | `/v1/source` | `save_event_source` | `save_source` |
| source | DELETE | `/v2/event-source/{source_id}` | `/v1/source/{source_id}` | `delete_event_source` | `delete_source_by_id` |
| task | DELETE | `/v2/task/{id}` | `/v1/task/{id}` | `delete_task` | `delete_task_by_id` |
| task | POST | `/v2/task` | `/v1/task` | `upsert_task` | `save_task` |
| timer | GET | `/v2/timer/{timer_id}` | `/v1/timer/{timer_id}` | `load_timer_by_id` | `get_timer_by_id` |
| user_account | GET | `/user-account` | `/v1/user-account` | `get_user_account` | `get_user_account` |
| user_account | POST | `/user-account` | `/v1/user-account` | `edit_user_account` | `update_user_account` |
| user | POST | `/user` | `/v1/user` | `add_user` | `save_user` |
| user | DELETE | `/user/{id}` | `/v1/user/{id}` | `delete_user` | `delete_user_by_id` |
| user | GET | `/user/{id}` | `/v1/user/{id}` | `get_user` | `get_user_by_id` |
| user | POST | `/user/{id}` | `/v1/user/{id}` | `edit_user` | `update_user` |
| user (preference) | GET | `/user/preference/{key}` | `/v1/user-preference/{key}` | `get_user_preference` | `get_user_preference_by_id` |
| user (preference) | POST | `/user/preference/{key}` | `/v1/user-preference/{key}` | `set_user_preference` | `save_user_preference` |
| user (preference) | DELETE | `/user/preference/{key}` | `/v1/user-preference/{key}` | `delete_user_preference` | `delete_user_preference_by_id` |
| validator | POST | `/v2/event-config` | `/v1/validator` | `add_validator` | `save_validator` |
| validator | DELETE | `/v2/event-config/{id}` | `/v1/validator/{id}` | `delete_validator` | `delete_validator_by_id` |
| validator | GET | `/v2/event-config/{id}` | `/v1/validator/{id}` | `get_validator` | `get_validator_by_id` |

## Risks / Trade-offs

- [Stacking a second `@router` decorator changes OpenAPI schema grouping/dedup for tools that render both routes as if they were unrelated operations] -> Mitigation: both routes already carry the same `tags=[...]` and `include_in_schema=sys_config.expose_gui_api`; no schema-generation change needed beyond the new path appearing as its own operation, which is expected and desired.
- [Renaming a handler function could theoretically break something that imports it directly (routers, tests, scripts) even though today's grep found none] -> Mitigation: re-run the same import grep per-file immediately before each rename during implementation, not just once at design time.
- [`source` as the v1 slug is a semantic regression from the descriptive `event-source`] -> Mitigation: accepted deliberately (see Decisions) for consistency; legacy `/v2/event-source` path is unaffected and remains available.
- [17 files touched in one change increases review surface] -> Mitigation: each file's edit is mechanical and independent (add decorator + rename), so tasks.md should list one task per file for isolated, easily-reviewable diffs.

## Migration Plan

Purely additive - no migration or rollback beyond a normal revert, since no existing route or behavior changes. Deploy as a single release; no phased rollout needed. No data migration.
