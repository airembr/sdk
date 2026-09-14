## 1. Pre-flight

- [x] 1.1 For every legacy function name being renamed (full list in design.md's mapping table), grep the repo for imports/references outside its own `list_endpoint.py` file and confirm none exist before renaming it
- [x] 1.2 Confirm no route path collisions: grep all `list_endpoint.py` files plus their sibling `routes/<domain>_endpoint.py` list files for any existing use of each new `/v1/...` path before adding it

## 2. Per-domain canonical routes (add v1 decorator + rename handler, one file per task)

- [x] 2.1 `bridge/crud_endpoint.py`: add `/v1/bridge/{bridge_id}` GET, rename `get_data_bridge_by_id` -> `get_bridge_by_id`; verify `openspec` app import (`python -c "import airembr_api.endpoint.gui.main"`) succeeds and `GET /v1/bridge/{id}` appears in the OpenAPI schema
- [x] 2.2 `canonical_entity/crud_endpoint.py`: add `/v1/canonical-entity` (POST), `/v1/canonical-entity/{id}` (GET, DELETE) with renames per design.md mapping; verify app import succeeds and all three v1 routes appear in the OpenAPI schema
- [x] 2.3 `canonical_entity/crud_endpoint.py` (property sub-resource): add `/v1/canonical-entity/{entity_id}/property` (POST) and `/v1/canonical-entity-property/{id}` (GET, DELETE) with renames per design.md mapping; verify app import succeeds and all three v1 routes appear in the OpenAPI schema
- [x] 2.4 `configuration/crud_endpoint.py`: add `/v1/configuration` (POST) and `/v1/configuration/{id}` (GET, DELETE) with renames; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.5 `destination/crud_endpoint.py`: add `/v1/destination` (POST) and `/v1/destination/{destination_id}` (GET, DELETE) with rename of `get_destination` -> `get_destination_by_id`; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.6 `embedding_setting/crud_endpoint.py`: add `/v1/embedding-setting` (POST) and `/v1/embedding-setting/{embedding_id}` (GET, DELETE), fixing the copy-pasted `get_segment`/`save_segment`/`delete_segment` names to `get_embedding_setting_by_id`/`save_embedding_setting`/`delete_embedding_setting_by_id`; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.7 `entity_object/crud_endpoint.py`: add `/v1/entity-object` (POST) and `/v1/entity-object/{entity_type_id}` (GET, DELETE) with renames; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.8 `ontology/crud_endpoint.py`: add `/v1/ontology` (POST) and `/v1/ontology/{id}` (GET, DELETE) with rename of `load_ontology_by_id` -> `get_ontology_by_id`; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.9 `payload_mapping/crud_endpoint.py`: add `/v1/payload-mapping` (POST) and `/v1/payload-mapping/{event_type_id}` (GET, DELETE) with renames, including `del_event_type_metadata` -> `delete_payload_mapping_by_id`; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.10 `reshaping_schema/crud_endpoint.py`: add `/v1/reshaping-schema` (POST) and `/v1/reshaping-schema/{id}` (GET, DELETE) with renames; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.11 `resource/crud_endpoint.py`: add `/v1/resource` (POST) and `/v1/resource/{id}` (GET, DELETE) with rename of `upsert_resource` -> `save_resource`; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.12 `segment/crud_endpoint.py`: add `/v1/segment` (POST) and `/v1/segment/{segment_id}` (GET, DELETE) with renames; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.13 `source/crud_endpoint.py`: add `/v1/source` (POST) and `/v1/source/{id}` (GET, DELETE) with renames (`load_source_by_id` -> `get_source_by_id`, `save_event_source` -> `save_source`, `delete_event_source` -> `delete_source_by_id`); verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.14 `task/crud_endpoint.py`: add `/v1/task` (POST) and `/v1/task/{id}` (DELETE) with renames (`upsert_task` -> `save_task`, `delete_task` -> `delete_task_by_id`); verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.15 `timer/crud_endpoint.py`: add `/v1/timer/{timer_id}` (GET) with rename `load_timer_by_id` -> `get_timer_by_id`; verify app import succeeds and route appears in the OpenAPI schema
- [x] 2.16 `user_account/crud_endpoint.py`: add `/v1/user-account` (GET, POST) with rename `edit_user_account` -> `update_user_account`; verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.17 `user/crud_endpoint.py`: add `/v1/user` (POST create), `/v1/user/{id}` (GET, POST edit, DELETE) with renames (`add_user`->`save_user`, `get_user`->`get_user_by_id`, `edit_user`->`update_user`, `delete_user`->`delete_user_by_id`); verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.18 `user/crud_endpoint.py` (preference sub-resource): add `/v1/user-preference/{key}` (GET, POST, DELETE) with renames (`get_user_preference`->`get_user_preference_by_id`, `set_user_preference`->`save_user_preference`, `delete_user_preference`->`delete_user_preference_by_id`); verify app import succeeds and routes appear in the OpenAPI schema
- [x] 2.19 `validator/crud_endpoint.py`: add `/v1/validator` (POST) and `/v1/validator/{id}` (GET, DELETE) with renames (`add_validator`->`save_validator`, `delete_validator`->`delete_validator_by_id`, `get_validator`->`get_validator_by_id`); verify app import succeeds and routes appear in the OpenAPI schema

## 3. Documentation

- [x] 3.1 Write `sdk/ENDPOINT_MAPPING.md` with the full old-path/old-fn -> new-path/new-fn table from design.md, grouped by domain; verify every one of the 45 mapped endpoints from design.md appears in the file

## 4. Verification

- [x] 4.1 Start the GUI API app (or run its test suite if one covers route registration) and verify both legacy and new v1 routes resolve to a 200/expected response for at least one representative request per domain
- [x] 4.2 Diff the generated OpenAPI schema before/after and verify every legacy operation is still present unchanged, with only new `/v1/...` operations added
- [x] 4.3 Run `openspec validate canonical-v1-endpoints --strict` and fix any reported issues
