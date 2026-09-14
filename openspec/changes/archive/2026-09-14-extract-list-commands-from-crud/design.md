## Context

See proposal.md for the "Why". This section covers the boundary rule used to classify every function and the full per-file move list.

**Classification rule** (agreed during exploration): a function stays in its current CRUD file only if it is single-item CRUD — get/save/add/edit/upsert/delete operating on exactly one record identified by an id. Everything else — `list_*`, histograms, meta/type lookups, by-tag/by-entity queries, and multi-record or derived-aggregate reads — moves to `command/v1/list/<domain>/list.py`.

**Import topology** (verified by grepping every importer of `airembr.system.command.v1.*` across the repo): every `gui/v1/.../crud_endpoint.py` already imports only single-item CRUD functions — none of them import a function that is moving. All of the moving functions are imported exclusively by legacy (pre-`v1`) `gui/routes/...` endpoints. This means the `v1` CRUD endpoints require zero changes; only the legacy endpoint imports need repointing.

## Goals / Non-Goals

**Goals:**
- Classify every function in the 17 mixed files under `command/v1/{meta,data}/<domain>/` as CRUD (stays) or list (moves), with the move list below as the source of truth.
- Create `command/v1/list/<domain>/list.py` (one per domain; `canonical_entity`'s two source files merge into one `list.py`) containing every moved function verbatim.
- Update every legacy endpoint import that resolves to a moved function.
- Preserve current behavior exactly — no function bodies, signatures, or logic change.

**Non-Goals:**
- Touching any `gui/v1/.../crud_endpoint.py` file (none import moving functions).
- Renaming functions, changing their signatures, or altering `command/v1/errors/` (unchanged; already an absolute import from every call site, so no path fixup needed even after functions move).
- Building the `gui/v1/.../list_endpoint.py` routes that would eventually call these new list command modules — that is a separate, future endpoint-side change. This change only reorganizes the command layer.
- Touching domains/files with zero list-shaped functions: `task`, `timer`, `user_account`, and the `user` domain's `add_user.py` / `delete_user.py` / `edit_user.py` / `get_user.py`.

## Decisions

**Per-file move table.** CRUD = stays in place. List = moves to `command/v1/list/<domain>/list.py`.

| Domain | Source file(s) | Stays (CRUD) | Moves (list) |
|---|---|---|---|
| bridge | `meta/bridge/bridge.py` | `get_data_bridge_by_id` | `reinstall_bridges`, `get_data_bridges`, `get_data_bridges_meta` |
| canonical_entity | `meta/canonical_entity/entities.py` | `get_canonical_entity`, `save_canonical_entity`, `delete_canonical_entity` | `list_canonical_entities` |
| canonical_entity | `meta/canonical_entity/properties.py` | `get_entity_property`, `save_entity_property`, `delete_entity_property` | `list_entity_properties` |
| configuration | `meta/configuration/configuration.py` | `get_configuration`, `add_configuration`, `delete_configuration` | `list_defined_configuration`, `list_configuration_types` |
| destination | `meta/destination/destination.py` | `save_destination`, `get_destination`, `delete_destination_by_id`, `get_destination_trigger_by_id` | `get_destinations_type_list`, `get_destinations_by_tag`, `get_destinations_meta`, `get_destination_triggers_metadata`, `list_destination_resources` |
| embedding_setting | `meta/embedding_setting/embedding_setting.py` | `get_embedding_setting`, `save_embedding_setting`, `delete_embedding_setting` | `list_embedding_settings` |
| entity_object | `meta/entity_object/entity_object.py` | `save_entity_object`, `get_entity_object_payload`, `delete_entity_object` | `get_entity_observations`, `list_entity_objects`, `get_entity_texts`, `list_entity_tables`, `get_entity_history`, `load_events_by_data_hash`, `get_entity_object_current_state` |
| payload_mapping | `meta/payload_mapping/event_mapping.py` | `add_event_type_mapping`, `get_event_mapping_by_id`, `del_event_type_metadata` | `list_event_mappings`, `list_event_type_mappings_by_tag` |
| reshaping_schema | `meta/reshaping_schema/reshaping_schema.py` | `add_reshape_schema`, `delete_reshape_schema`, `get_reshape_schema` | `get_reshape_schemas_by_event_type`, `load_reshape_schemas` |
| resource | `meta/resource/resource.py` | `get_resource_by_id`, `upsert_resource`, `delete_resource` | `get_resource_types_list`, `list_resources_names_by_tag`, `list_all_resources`, `list_resources`, `list_resources_by_type` |
| segment | `meta/segment/segment.py` | `save_segment`, `get_segment`, `delete_segment` | `list_segments`, `list_segments_meta` |
| source | `meta/source/event_source.py` | `load_source_by_id`, `save_event_source`, `delete_event_source` | `get_event_source_entities`, `list_event_sources`, `list_running_event_sources`, `get_event_source_types`, `list_event_sources_names_and_ids` |
| validator | `meta/validator/validator.py` | `add_validator`, `delete_validator`, `get_validator` | `load_validators` |
| ontology | `meta/ontology/ontology.py` | `get_ontology`, `save_ontology`, `delete_ontology` | `list_ontologies` |
| user | `meta/user/preferences.py` | `get_user_preference`, `set_user_preference`, `delete_user_preference` | `get_all_user_preferences` |
| event | `data/event/event.py` | `get_event`, `delete_event` | `load_event_by_query`, `get_event_histogram`, `get_events_for_actor_entity`, `get_events_for_object_entity`, `get_event_type_data_schema`, plus private helpers `_shorten_texts`, `_apply_where_filter` |
| observation | `data/observation/observation.py` | `get_observation`, `delete_observation` | `get_observation_facts`, `get_observers_from_facts`, `load_observations`, `load_observations_by_query`, `get_observations_histogram`, plus private helper `_apply_where_filter` |

**Edge-case classifications** (functions that don't cleanly fit "single record by id" or "returns a collection", resolved explicitly rather than left ambiguous):
- `reinstall_bridges` (bridge): an action affecting all bridges, not a getter. Classified as "moves" — it operates on the whole collection, not one record, matching the "everything except single-item CRUD" rule.
- `get_destination_trigger_by_id` (destination): a single-item get-by-id, but for a different sub-entity (trigger) than the domain's primary entity (destination). Classified as "stays" — it fits the single-item-by-id shape regardless of which entity it targets.
- `get_entity_object_current_state` (entity_object): takes one `entity_pk` but internally fans out across stitched pks and returns aggregated/derived state, not a single DAO record. Classified as "moves" — it is not a plain single-record read.
- `get_event_type_data_schema` (event): returns one static/derived schema object, not a collection, and isn't a DAO lookup by id at all (it's a lookup in a predefined schema table). Classified as "moves" for consistency (not single-item-by-id CRUD), but flagged here since it's the least "list-like" of the moved functions — reviewer should confirm this placement still makes sense when the file is opened.
- `get_observation_facts` (observation): scoped to one `observation_id` but paginated (`start`, `limit`) and returns a list of facts. Classified as "moves" — the pagination and list return type make it a list operation on a sub-collection, not a single-record read.

**Private helpers travel with their sole callers.** `_shorten_texts` and `_apply_where_filter` (event.py) and `_apply_where_filter` (observation.py) are used exclusively by functions that are moving (verified by grep within each file), so they move into the corresponding `list.py` with no residual reference from the CRUD file left behind.

**`command/v1/errors/` is untouched.** Every error import (e.g. `from airembr.system.command.v1.errors.reshaping_schema_errors import EventReshapingError`) is already an absolute import. Moving a function that raises one of these errors into `command/v1/list/<domain>/list.py` requires no import path change — the new file just adds the same absolute import.

**No new `gui/v1/.../list_endpoint.py` routes in this change.** The empty `list_endpoint.py` scaffold under `gui/v1/routes/meta/bridge/` stays as-is (still unregistered, still empty). Wiring v1 list endpoints to call these new list command modules is deliberately deferred — this change is command-layer-only, matching the proposal's stated scope.

## Migration Plan

1. Create `airembr/system/command/v1/list/<domain>/` (16 directories) with `__init__.py` in each, plus `airembr/system/command/v1/list/__init__.py`.
2. For each of the 17 source files, cut the "moves" functions (and any private helper used solely by them) from the CRUD file and paste them into the domain's `list.py`, carrying over only the imports each moved function actually needs (most source files import things used by both staying and moving functions — e.g. `entity_object_dao` is needed by both `entity_object.py` and its new `list.py` — so some import lines are duplicated across the split, not deleted).
3. Merge `canonical_entity/entities.py`'s `list_canonical_entities` and `canonical_entity/properties.py`'s `list_entity_properties` into the single `command/v1/list/canonical_entity/list.py`.
4. Update the ~16 affected legacy `gui/routes/...` endpoint files' import statements to point at the new `command/v1/list/<domain>/list.py` paths.
5. Grep the repo for any remaining reference to a moved function's old module path to catch importers outside the two endpoint trees (tests, scripts, other command files).
6. Boot the GUI API app (or run its import-time test/lint) to confirm no `ImportError`/`ModuleNotFoundError` remains, and that both legacy and v1 endpoints still resolve their imports correctly.

No feature flag or staged rollout needed — this is a function move plus import fixes with identical runtime behavior; rollback is `git revert` of the commit.

## Risks / Trade-offs

- **[Risk]** A moved function's exception type or helper is only available via a relative/local import inside the old file that isn't obviously "the errors package" → after the move, that import breaks.
  **Mitigation**: all five domain error modules already live in the separate `command/v1/errors/` package and are imported absolutely everywhere (verified above); no relative imports were found inside any of the 17 files that reference something that isn't also moving with its function.
- **[Risk]** A caller outside the two endpoint trees (a test, a script, another command module) imports a moving function → import breaks at runtime instead of at review time.
  **Mitigation**: migration step 5's exhaustive repo-wide grep before considering the move done (the import inventory in this design was built the same way and found only the two endpoint trees as importers).
- **[Trade-off]** The four edge-case functions (`reinstall_bridges`, `get_entity_object_current_state`, `get_event_type_data_schema`, `get_observation_facts`) are classified by the "not single-item CRUD" rule even though they don't read as textbook "lists." Accepted for consistency with the agreed rule rather than carving out a third category; each is called out explicitly above so a reviewer can override any single one without relitigating the whole rule.
- **[Trade-off]** This change does not wire up any new `list_endpoint.py` routes, so the new `command/v1/list/` modules are only consumed by legacy endpoints immediately after this change — the v1 endpoint layer gains no new routes yet. Accepted per proposal scope; endpoint-side wiring is future work.
