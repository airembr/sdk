This is a spec-only step: it defines the rules and produces a concrete route classification. **No endpoint files are moved or edited yet** — that is a later, separate task that will execute this spec mechanically.

## Implementation notes (added after execution)

This spec has been implemented. Two corrections surfaced while reading the actual source files, applied during implementation:

1. `entity_object_endpoint.py` lives directly at `airembr_api/endpoint/gui/routes/entity_object_endpoint.py`, not under a `routes/data/` subfolder as this spec originally stated — there is no such subfolder for it.
2. `gui/setting_endpoint.py` was reclassified from "split" to **leave entirely in place**: every one of its five handlers immediately raises `NotImplementedError("Do not use. Use audiences instead.")`, with the real logic commented out below. There is no live CRUD there to migrate.

All other routes moved exactly as classified below. The new `airembr_api/endpoint/gui/routes/crud/` folder is flat (one file per resource, same basename as the original file, regardless of which subfolder the original lived in) and `airembr_api/endpoint/gui/main.py` was rewired with aliased imports (`crud_<name>`) for every split file to avoid colliding with the still-existing original module of the same basename.

# Goal

`airembr_api/endpoint/gui/routes/` (the GUI API, port 4001) has grown to ~45 endpoint files. Most are thin FastAPI wrappers that delegate one-for-one to `airembr/system/command/<domain>/` — that layering is already enforced (see `.spec/done/move_form_bizmory_to_airembr_api/SPEC.md`). But routes of very different natures (plain single-record CRUD, list/filter queries, aggregation/histograms, semantic/LLM queries, workflow orchestration, system bootstrap) are mixed together in the same files with no structural distinction between "this is just CRUD" and "this has real logic."

This spec defines what counts as "simple CRUD" here, introduces a new `crud/` folder, and lists exactly which routes belong there. A later step will use this list to actually move the code.

Scope: **GUI API only** (`airembr_api/endpoint/gui/routes/`). The Collector API (`airembr_api/endpoint/collector/`) has no CRUD-shaped endpoints — it's ingestion/webhook/auth-token logic only — and is out of scope.

# What counts as "simple CRUD"

A route qualifies **only** if it is exactly one of these four, and nothing more:

- **Create** — `POST` where the request body is the resource itself, no filter/query semantics.
- **Read one** — `GET .../{id}` returning a single record identified by its own id.
- **Update one** — `PUT` or `POST .../{id}` updating a single record by id.
- **Delete one** — `DELETE .../{id}`.

And it must also:

- Delegate to a single command-layer call with no branching, aggregation, filtering, or multi-step orchestration inside the endpoint function itself.
- Have no side effects beyond that single record's persistence — no cache broadcasts, no external triggers, no re-install/redeploy actions.

A route is explicitly **excluded**, no matter how simple it looks, if it:

- Returns a collection: any `list`, a plural-named route, or a paged `/page/{page}` route.
- Is filtered/scoped by a secondary key: `/type/{x}`, `/by_tag`, `/by_type`, `/{x}/entities`, etc. (example: `GET /v2/event-sources/type` is a lookup filtered by type, not single-record CRUD — it stays out).
- Does histogram/aggregation/count.
- Is a "meta"/introspection endpoint.
- Does dynamic branching on a query param (e.g. `output=meta`).
- Triggers a side effect (`reinstall`, `deploy`, cluster-settings broadcast, etc.).
- Is a search/autocomplete endpoint.
- Is deprecated or marked for removal.

If a route doesn't unambiguously match one of the four verbs above, leave it out and flag it for human review — don't guess.

# Target structure

New folder: `airembr_api/endpoint/gui/routes/crud/`, mirroring the existing subfolder convention (`data/`, `management/`, `workflow/`, etc.). One file per resource, same filename as today's endpoint file.

# File-by-file classification

## Move the whole file into `crud/`

Every route in these files is clear single-record CRUD:

- `timer_endpoint.py` — `GET /v2/timer/{timer_id}`
- `user_account_endpoint.py` — `GET /user-account`, `POST /user-account` (both operate on the single calling user's account, not a list)

## Split — move only the listed routes, leave the rest of the file in place

- **`canonical_entity_endpoint.py`**
  - Move: `GET /v2/canonical/entity/{id}`, `POST /v2/canonical/entity`, `DELETE /v2/canonical/entity/{id}`, `GET /v2/canonical/entity/property/{id}`, `POST /v2/canonical/entity/{entity_id}/property`, `DELETE /v2/canonical/entity/property/{id}`
  - Keep: `GET /v2/canonical/entities` (list), `GET /v2/canonical/entity/{entity_id}/properties` (list)

- **`embedding_setting_endpoint.py`**
  - Move: `GET /v2/embedding/{embedding_id}`, `POST /v2/embedding`, `DELETE /v2/embedding/{embedding_id}`
  - Keep: `GET /v2/embeddings` (list)

- **`data/entity_object_endpoint.py`**
  - Move: `POST /v2/entity/object`, `GET /v2/entity/object/{entity_type_id}`, `DELETE /v2/entity/object/{entity_type_id}`
  - Keep: `GET /v2/entity/observations`, `GET /v2/entity/objects/list`, `GET /v2/entity/texts`, `GET /v2/entity/tables` (all lists), `GET /v2/entity/{entity_id}/history`, `GET /v2/entity/history/use/{data_hash}`, `GET /v2/entity/{entity_pk}/traits/state` (derived reads)

- **`event_reshaping_schema_endpoint.py`**
  - Move: `POST /event-reshape-schema`, `GET /event-reshape-schema/{id}`, `DELETE /event-reshape-schema/{id}`
  - Keep: `GET /event-reshape-schemas/by_type/{event_type}`, `GET /event-reshape-schema` (lists)

- **`event_validator_endpoint.py`**
  - Move: `POST /v2/event-config`, `GET /v2/event-config/{id}`, `DELETE /v2/event-config/{id}`
  - Keep: `GET /v2/event-configs` (list)

- **`management/configuration_endpoint.py`**
  - Move: `GET /configuration/{id}`, `POST /configuration`, `DELETE /configuration/{id}`
  - Keep: `GET /configuration` (list), `GET /configuration-type` (list)

- **`gui/setting_endpoint.py`**
  - Move: `GET /setting/{type}/{id}`, `POST /setting/{type}`, `DELETE /setting/{type}/{id}`
  - Keep: `GET /settings/{type}/entities` (list), `GET /settings/{type}` (list)

- **`mapping/event_mapping_endpoint.py`**
  - Move: `POST /mapping`, `GET /mapping/{event_type_id}`, `DELETE /mapping/{event_type_id}`
  - Keep: `GET /mappings/{event_type}` (list), `GET /search/mappings` (search)

- **`ontology_endpoint.py`**
  - Move: `GET /v2/ontology/{id}`, `POST /v2/ontology`, `DELETE /v2/ontology/{id}`
  - Keep: `GET /v2/ontologies` (list)

- **`outbound/destination_endpoint.py`**
  - Move: `POST /v2/destination`, `GET /destination/{destination_id}`, `DELETE /destination/{destination_id}`
  - Keep: `GET /destinations/type`, `GET /destinations/by_tag` (filtered lists), `GET /v2/destinations/meta`, `GET /v2/destinations/trigger/meta`, `GET /v2/destination/trigger/{trigger_id}`, `GET /v2/destination/resources/meta`

- **`resource_endpoint.py`**
  - Move: `GET /resource/{id}`, `POST /resource`, `DELETE /resource/{id}`
  - Keep: `GET /resources/type/{type}`, `GET /resources/entity/tag/{tag}`, `GET /resources/entity`, `GET /resources`, `GET /resources/by_type` (all lists)

- **`segment_endpoint.py`**
  - Move: `POST /v2/segment`, `GET /v2/segment/{segment_id}`, `DELETE /segment/{segment_id}`
  - Keep: `GET /v2/segments` (list), `GET /v2/segments/meta`

- **`inbound/event_source_endpoint.py`**
  - Move: `GET /v2/event-source/{id}`, `POST /v2/event-source`, `DELETE /v2/event-source/{source_id}`
  - Keep: `GET /v2/event-sources` (branches on `output=meta`), `GET /v2/event-sources/running`, `GET /v2/event-sources/type`, `GET /v2/event-sources/entity` (all lists)

- **`inbound/bridge_endpoint.py`**
  - Move: `GET /v2/bridge/{bridge_id}` only
  - Keep: `GET /v2/bridges` (list), `GET /v2/bridges/meta`, `GET /v2/bridge/reinstall` (side effect)

- **`data/event_endpoint.py`**
  - Move: `GET /v2/event/{id}`, `DELETE /v2/event/{id}`
  - Keep: `POST /v2/events/list`, `POST /v2/events/list/page/{page}`, `POST /v2/events/histogram`, `GET /v2/actor/{entity_pk}/events/`, `GET /v2/object/{entity_pk}/events/`, `GET /event/type/{event_type}/schema/{entity_name}`

- **`data/observation_endpoint.py`**
  - Move: `GET /v2/observation/{observation_id}`, `DELETE /v2/observation/{observation_id}`
  - Keep: `GET /v2/observation/{observation_id}/facts/`, `GET /v2/observers`, `GET /v2/observations`, `POST /v2/observations/list/page/{page}`, `POST /v2/observations/histogram`

- **`task_endpoint.py`**
  - Move: `POST /v2/task`, `DELETE /v2/task/{id}`
  - Keep: `GET /v2/tasks`, `GET /v2/tasks/type/{type}` (lists), `GET /v2/task/{task_id}/status` (derived, not the stored record)

- **`user_endpoint.py`**
  - Move: `GET /user/preference/{key}`, `POST /user/preference/{key}`, `DELETE /user/preference/{key}`, `POST /user`, `GET /user/{id}`, `DELETE /user/{id}`, `POST /user/{id}` (edit)
  - Keep: `POST /user/token`, `POST /user/logout` (auth), `GET /user/preferences` (list), `GET /users` (list), `GET /users/{start}/{limit}` (legacy paged list, marked "TODO remove in 1.0.0" — flag for deletion rather than migration)

## Leave entirely in place

No route in these files meets the strict CRUD bar, or the file is fully non-CRUD in nature:

`console_log_endpoint.py`, `data/dashboard_endpoint.py`, `data/actor_endpoint.py`, `data/autocomplete_endpoint.py`, `data/entity_endpoint.py`, `data/log_endpoint.py`, `data/_generic_endpoint.py` (dead/commented-out code — flag for deletion), `eql_endpoint.py`, `debug_endpoint.py`, `deploy_endpoint.py`, `enhancer_endpoint.py`, `gui/feed_endpoint.py`, `import_endpoint.py` (marked "TODO Not used probably"), `install/install_endpoint.py`, `tenant_install_endpoint.py`, `management/migration_endpoint.py`, `management/health_endpoint.py`, `management/info_endpoint.py`, `metadata_endpoint.py`, `pill/pill_endpoint.py`, `settings_endpoint.py` (cluster settings with broadcast side effects, not a per-record resource), `workflow/*` (commercial/licensed only).

# Process notes for the migration step that will follow this spec

- When a file is split, routes moving to `crud/` keep their existing path, permissions, and response shape unchanged — this is a file-organization move, not an API contract change.
- `airembr_api/endpoint/gui/main.py`'s `include_router(...)` calls must be updated to import from the new `crud/` module paths (and to include both the old and new router when a file is split into two).
- Any route whose classification turns out to be ambiguous during implementation should be flagged for a human decision rather than guessed.

# How to verify this spec

1. The classification above is readable and complete enough that the migration step can execute from it alone, without re-deriving which routes qualify.
2. Cross-check the file list against `airembr_api/endpoint/gui/main.py`'s `include_router(...)` calls — every currently-registered router should appear in exactly one of the three lists above (whole-move, split, or leave-in-place).
3. This step makes no code or behavior changes — there is nothing to run or test yet.
