# Goal

Detect drift between the GUI backend API surface and the console frontend's usage of it:

1. Backend routes that no frontend code calls anymore (dead-code candidates).
2. Frontend calls that target a backend route which no longer exists (stale/broken calls).
3. Frontend code that calls the backend directly instead of going through the `src/remote_api/endpoints/` layer (technical debt — inconsistent auth/base-URL/error handling).

This is a documentation/analysis task. No endpoint files are moved, deleted, or rewritten as part of this spec — that is a later, separate task that will consume the findings table this spec produces.

# Scope

- **Backend**: `airembr_api/endpoint/gui/` only (GUI API, port 4001). The Collector API (`airembr_api/endpoint/collector/`) is out of scope — it's ingestion/webhook/auth-token logic with no frontend consumer (same exclusion as `.spec/done/create_crud_routes_folder/SPEC.md`).
- **Frontend**: all of `/home/risto/WebstormProjects/console/src/`, not just `src/remote_api/endpoints/` — the wider scope is required to catch direct/inline bypass calls that skip the endpoints layer entirely.

# Methodology

## 1. Enumerate backend routes

- Canonical source of truth: `airembr_api/endpoint/gui/main.py`, which `include_router(...)`s every route module. Note that `routes/workflow/*` (flow, flow_action, plugins) is only included `if system_license.valid:` — a commercial-only feature gate.
- Enumerate every live (non-commented-out) `@router.<method>(...)` and `@auth_router.<method>(...)` decorator under `airembr_api/endpoint/gui/routes/**`.
- The full list gathered for this spec (207 routes, listed below in "Known backend inventory") can be reused as-is; re-run the grep only to catch drift since this spec was written:
  ```
  grep -rn '@\(router\|auth_router\)\.\(get\|post\|put\|delete\|patch\)(' airembr_api/endpoint/gui/routes/
  ```

## 2. Enumerate frontend endpoint definitions

- `src/remote_api/endpoints/*.jsx` is a flat directory (31 files) of plain functions returning `{url, method, data?, headers?}` config objects, consumed via `src/hooks/useRequest.jsx`'s `request()` (a `fetch()` wrapper) — no axios anywhere in the frontend.
- `method` defaults to `GET` when omitted from the returned object.
- The full list gathered for this spec (~110 functions, listed below in "Known frontend inventory") can be reused as-is; re-scan only to catch drift.

## 3. Find direct/inline bypasses (frontend calling the backend without going through `remote_api/endpoints`)

- Grep the rest of `src/` (outside `remote_api/endpoints/`) for: raw `fetch(`, `new EventSource(`, `new WebSocket(`, and any literal path string (`"/..."` or template literal starting with `/`) passed straight into `useRequest()`'s `request({url: ...})` instead of through an imported endpoint function.
- 3 such bypasses were already found and verified during this spec's research — see "Known findings" below. Confirm they still exist, then continue scanning for any others not yet caught.

## 4. Normalize and match

- Strip query strings from both sides before comparing.
- Collapse path parameters to a single wildcard token: `{id}`, `${var}`, and FastAPI's `{name}` all normalize the same way, e.g. `/v2/entity/{id}/history` and `` `/v2/entity/${entityId}/history` `` both become `/v2/entity/*/history`.
- Compare on **method + normalized path**.
- **Legacy vs v2-CRUD duplicates**: some resources have two backend files serving overlapping paths — a legacy top-level file (e.g. `routes/canonical_entity_endpoint.py`) and a `routes/crud/` file (e.g. `routes/crud/canonical_entity_endpoint.py`) for the same resource. Treat a frontend call as satisfied if it matches a route in *either* file; do not double-flag the pair.
- **Commercially-gated routes** (`routes/workflow/*`, 16 routes): if a frontend call matches one of these, it's fine. If one appears backend-only, don't treat it the same as a normal dead-route finding — flag it separately, since it may only be exercised when the commercial license/module is active.

# Known backend inventory (207 routes across 40 files)

FastAPI. Pattern:
```python
router = APIRouter(dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))])

@router.get("/v2/canonical/entity/{id}", tags=["ontology"], response_model=Optional[CanonicalEntity])
async def load_canonical_entity_by_id(id: str, response: Response):
    ...
```

## routes/ (top-level, legacy files)
- GET /v2/canonical/entities — canonical_entity_endpoint.py
- GET /v2/canonical/entity/{entity_id}/properties — canonical_entity_endpoint.py
- GET /event/logs/{event_id} — console_log_endpoint.py
- GET /node/logs/{node_id} — console_log_endpoint.py
- GET /flow/logs/{flow_id} — console_log_endpoint.py
- GET /profile/logs/{entity_id} — console_log_endpoint.py
- GET /log/alerts — console_log_endpoint.py
- GET /v2/count/online — dashboard_endpoint.py
- GET /v2/system/table/stats — dashboard_endpoint.py
- GET /debug/es/indices — debug_endpoint.py
- GET /debug/server/time — debug_endpoint.py
- GET /deploy/{table_name}/{id} — deploy_endpoint.py
- GET /undeploy/{table_name}/{id} — deploy_endpoint.py
- GET /v2/production/{table_name}/{id} — deploy_endpoint.py
- GET /v2/embeddings — embedding_setting_endpoint.py
- GET /enhancer/source/{type} — enhancer_endpoint.py
- GET /v2/entity/observations — entity_object_endpoint.py
- GET /v2/entity/objects/list — entity_object_endpoint.py
- GET /v2/entity/texts — entity_object_endpoint.py
- GET /v2/entity/tables — entity_object_endpoint.py
- GET /v2/entity/{entity_id}/history — entity_object_endpoint.py
- GET /v2/entity/history/use/{data_hash} — entity_object_endpoint.py
- GET /v2/entity/{entity_pk}/traits/state — entity_object_endpoint.py
- GET /v2/eql/text — eql_endpoint.py
- GET /v2/eql/facts — eql_endpoint.py
- GET /v2/eql/entity/locations — eql_endpoint.py
- GET /v2/eql/observations — eql_endpoint.py
- GET /v2/eql/entity-types — eql_endpoint.py
- GET /v2/eql/autocomplete — eql_endpoint.py
- GET /event-reshape-schemas/by_type/{event_type} — event_reshaping_schema_endpoint.py
- GET /event-reshape-schema — event_reshaping_schema_endpoint.py
- GET /v2/event-configs — event_validator_endpoint.py
- GET /import/task/{task_id}/status — import_endpoint.py
- GET /v2/named/event/entities — metadata_endpoint.py
- GET /v2/named/entities/2 — metadata_endpoint.py
- GET /v2/named/entities/1 — metadata_endpoint.py
- GET /v2/named/entity/{entity_type}/properties — metadata_endpoint.py
- GET /v2/named/event/types — metadata_endpoint.py
- GET /v2/named/event/actors — metadata_endpoint.py
- GET /v2/named/table/{table_name}/columns — metadata_endpoint.py
- GET /v2/named/tables — metadata_endpoint.py
- GET /v2/fact/traits/by/type — metadata_endpoint.py
- GET /v2/ontologies — ontology_endpoint.py
- GET /resources/type/{type} — resource_endpoint.py
- GET /resources/entity/tag/{tag} — resource_endpoint.py
- GET /resources/entity — resource_endpoint.py
- GET /resources — resource_endpoint.py
- GET /resources/by_type — resource_endpoint.py
- GET /v2/segments — segment_endpoint.py
- GET /v2/segments/meta — segment_endpoint.py
- GET /system/settings — settings_endpoint.py
- GET /system/envs — settings_endpoint.py
- PUT /cluster/settings/{key} — settings_endpoint.py
- GET /cluster/settings/{key} — settings_endpoint.py
- GET /v2/tasks — task_endpoint.py
- GET /v2/tasks/type/{type} — task_endpoint.py
- GET /v2/task/{task_id}/status — task_endpoint.py
- POST /tenant/install — tenant_install_endpoint.py
- GET /users/{start}/{limit} — user_endpoint.py (legacy, marked "TODO remove in 1.0.0" per prior spec)
- POST /user/token — user_endpoint.py (auth_router)
- POST /user/logout — user_endpoint.py (auth_router)
- GET /user/preferences — user_endpoint.py
- GET /users — user_endpoint.py

## routes/crud/ (v2 CRUD, 44 routes)
- GET /v2/bridge/{bridge_id} — crud/bridge_endpoint.py
- GET /v2/canonical/entity/{id} — crud/canonical_entity_endpoint.py
- POST /v2/canonical/entity — crud/canonical_entity_endpoint.py
- DELETE /v2/canonical/entity/{id} — crud/canonical_entity_endpoint.py
- GET /v2/canonical/entity/property/{id} — crud/canonical_entity_endpoint.py
- POST /v2/canonical/entity/{entity_id}/property — crud/canonical_entity_endpoint.py
- DELETE /v2/canonical/entity/property/{id} — crud/canonical_entity_endpoint.py
- GET /configuration/{id} — crud/configuration_endpoint.py
- POST /configuration — crud/configuration_endpoint.py
- DELETE /configuration/{id} — crud/configuration_endpoint.py
- POST /v2/destination — crud/destination_endpoint.py
- GET /destination/{destination_id} — crud/destination_endpoint.py
- DELETE /destination/{destination_id} — crud/destination_endpoint.py
- GET /v2/embedding/{embedding_id} — crud/embedding_setting_endpoint.py
- POST /v2/embedding — crud/embedding_setting_endpoint.py
- DELETE /v2/embedding/{embedding_id} — crud/embedding_setting_endpoint.py
- POST /v2/entity/object — crud/entity_object_endpoint.py
- GET /v2/entity/object/{entity_type_id} — crud/entity_object_endpoint.py
- DELETE /v2/entity/object/{entity_type_id} — crud/entity_object_endpoint.py
- GET /v2/event/{id} — crud/event_endpoint.py
- DELETE /v2/event/{id} — crud/event_endpoint.py
- POST /mapping — crud/event_mapping_endpoint.py
- GET /mapping/{event_type_id} — crud/event_mapping_endpoint.py
- DELETE /mapping/{event_type_id} — crud/event_mapping_endpoint.py
- POST /event-reshape-schema — crud/event_reshaping_schema_endpoint.py
- DELETE /event-reshape-schema/{id} — crud/event_reshaping_schema_endpoint.py
- GET /event-reshape-schema/{id} — crud/event_reshaping_schema_endpoint.py
- GET /v2/event-source/{id} — crud/event_source_endpoint.py
- POST /v2/event-source — crud/event_source_endpoint.py
- DELETE /v2/event-source/{source_id} — crud/event_source_endpoint.py
- POST /v2/event-config — crud/event_validator_endpoint.py
- DELETE /v2/event-config/{id} — crud/event_validator_endpoint.py
- GET /v2/event-config/{id} — crud/event_validator_endpoint.py
- GET /v2/observation/{observation_id} — crud/observation_endpoint.py
- DELETE /v2/observation/{observation_id} — crud/observation_endpoint.py
- GET /v2/ontology/{id} — crud/ontology_endpoint.py
- POST /v2/ontology — crud/ontology_endpoint.py
- DELETE /v2/ontology/{id} — crud/ontology_endpoint.py
- GET /resource/{id} — crud/resource_endpoint.py
- POST /resource — crud/resource_endpoint.py
- DELETE /resource/{id} — crud/resource_endpoint.py
- POST /v2/segment — crud/segment_endpoint.py
- GET /v2/segment/{segment_id} — crud/segment_endpoint.py
- DELETE /segment/{segment_id} — crud/segment_endpoint.py
- DELETE /v2/task/{id} — crud/task_endpoint.py
- POST /v2/task — crud/task_endpoint.py
- GET /v2/timer/{timer_id} — crud/timer_endpoint.py
- GET /user-account — crud/user_account_endpoint.py
- POST /user-account — crud/user_account_endpoint.py
- POST /user/{id} — crud/user_endpoint.py
- GET /user/preference/{key} — crud/user_endpoint.py
- POST /user/preference/{key} — crud/user_endpoint.py
- DELETE /user/preference/{key} — crud/user_endpoint.py
- POST /user — crud/user_endpoint.py
- DELETE /user/{id} — crud/user_endpoint.py
- GET /user/{id} — crud/user_endpoint.py

## routes/data/ (29 routes)
- POST /v2/actors/list/page/{page} — data/actor_endpoint.py
- POST /v2/actors/list — data/actor_endpoint.py
- POST /v2/actors/histogram — data/actor_endpoint.py
- GET /v2/observation/query/autocomplete — data/autocomplete_endpoint.py
- GET /v2/event/query/autocomplete — data/autocomplete_endpoint.py
- GET /v2/actor/query/autocomplete — data/autocomplete_endpoint.py
- GET /v2/log/query/autocomplete — data/autocomplete_endpoint.py
- GET /entity/{entity_name}/logs/{entity_id} — data/entity_endpoint.py
- GET /entity/{entity_name}/count — data/entity_endpoint.py
- GET /entity/{entity_type}/hash/{hash} — data/entity_endpoint.py
- GET /v2/entity/pk/{entity_pk}/data_hash/{data_hash} — data/entity_endpoint.py
- GET /v2/entity/{table_name}/columns — data/entity_endpoint.py
- GET /v2/entities/{entity_type}/page/{page} — data/entity_endpoint.py
- GET /v2/entities/observation/{observation_id}/observer/{observer_pk} — data/entity_endpoint.py
- GET /v2/entities/observation/{observation_id} — data/entity_endpoint.py
- GET /v2/entity/1/list — data/entity_endpoint.py
- POST /v2/events/list — data/event_endpoint.py
- POST /v2/events/list/page/{page} — data/event_endpoint.py
- POST /v2/events/histogram — data/event_endpoint.py
- GET /v2/actor/{entity_pk}/events/ — data/event_endpoint.py
- GET /v2/object/{entity_pk}/events/ — data/event_endpoint.py
- GET /event/type/{event_type}/schema/{entity_name} — data/event_endpoint.py
- POST /log/range/page/{page} — data/log_endpoint.py
- POST /log/histogram — data/log_endpoint.py
- GET /v2/observation/{observation_id}/facts/ — data/observation_endpoint.py
- GET /v2/observers — data/observation_endpoint.py
- GET /v2/observations — data/observation_endpoint.py
- POST /v2/observations/list/page/{page} — data/observation_endpoint.py
- POST /v2/observations/histogram — data/observation_endpoint.py

(`data/_generic_endpoint.py` has only commented-out/dead code — not counted.)

## routes/gui/ (6 routes)
- GET /feed — gui/feed_endpoint.py
- GET /settings/{type}/entities — gui/setting_endpoint.py
- GET /setting/{type}/{id} — gui/setting_endpoint.py
- GET /settings/{type} — gui/setting_endpoint.py
- POST /setting/{type} — gui/setting_endpoint.py
- DELETE /setting/{type}/{id} — gui/setting_endpoint.py

## routes/inbound/ (7 routes)
- GET /v2/bridge/reinstall — inbound/bridge_endpoint.py
- GET /v2/bridges — inbound/bridge_endpoint.py
- GET /v2/bridges/meta — inbound/bridge_endpoint.py
- GET /v2/event-sources — inbound/event_source_endpoint.py
- GET /v2/event-sources/running — inbound/event_source_endpoint.py
- GET /v2/event-sources/type — inbound/event_source_endpoint.py
- GET /v2/event-sources/entity — inbound/event_source_endpoint.py

## routes/install/ (2 routes)
- GET /v2/install — install/install_endpoint.py
- POST /v2/install — install/install_endpoint.py

## routes/management/ (12 routes)
- GET /configuration — management/configuration_endpoint.py
- GET /configuration-type — management/configuration_endpoint.py
- GET /ping — management/health_endpoint.py
- POST /healthcheck — management/health_endpoint.py
- GET /healthcheck — management/health_endpoint.py
- PUT /healthcheck — management/health_endpoint.py
- DELETE /healthcheck — management/health_endpoint.py
- GET /info/versions — management/info_endpoint.py
- GET /info/version — management/info_endpoint.py
- GET /info/version/details — management/info_endpoint.py
- GET / — management/info_endpoint.py (root)
- POST /migration/mysql/upgrade — management/migration_endpoint.py

## routes/mapping/ (2 routes)
- GET /mappings/{event_type} — mapping/event_mapping_endpoint.py
- GET /search/mappings — mapping/event_mapping_endpoint.py

## routes/outbound/ (6 routes)
- GET /destinations/type — outbound/destination_endpoint.py
- GET /destinations/by_tag — outbound/destination_endpoint.py
- GET /v2/destinations/meta — outbound/destination_endpoint.py
- GET /v2/destinations/trigger/meta — outbound/destination_endpoint.py
- GET /v2/destination/trigger/{trigger_id} — outbound/destination_endpoint.py
- GET /v2/destination/resources/meta — outbound/destination_endpoint.py

## routes/pill/ (5 routes)
- POST /v2/texts/import — pill/pill_endpoint.py
- GET /v2/facts/source/{source_id}/count — pill/pill_endpoint.py
- GET /v2/texts/source/{source_id}/count — pill/pill_endpoint.py
- GET /v2/texts/source/{source_id}/page/{page}/export — pill/pill_endpoint.py
- GET /v2/facts/source/{source_id}/page/{page}/export — pill/pill_endpoint.py

## routes/workflow/ (commercial-license-gated, 19 routes — see matching note above)
- GET /flow/action/plugin/{plugin_id} — workflow/flow_action_endpoint.py
- GET /flow/action/plugin/{plugin_id}/hide/{state} — workflow/flow_action_endpoint.py
- GET /flow/action/plugin/{plugin_id}/enable/{state} — workflow/flow_action_endpoint.py
- PUT /flow/action/plugin/{plugin_id}/icon/{icon} — workflow/flow_action_endpoint.py
- PUT /flow/action/plugin/{plugin_id}/name/{name} — workflow/flow_action_endpoint.py
- DELETE /flow/action/plugin/{plugin_id} — workflow/flow_action_endpoint.py
- GET /flow/action/plugins — workflow/flow_action_endpoint.py
- GET /v2/install/plugins — workflow/flow_action_endpoint.py
- POST /v2/workflow/rearrange — workflow/flow_endpoint.py
- POST /v2/workflow/dag — workflow/flow_endpoint.py
- GET /v2/workflow/dag/{workflow_id} — workflow/flow_endpoint.py
- GET /v2/workflow/{workflow_id} — workflow/flow_endpoint.py
- POST /v2/workflow — workflow/flow_endpoint.py
- POST /v2/workflow/debug — workflow/flow_endpoint.py
- DELETE /v2/workflow/{workflow_id} — workflow/flow_endpoint.py
- GET /v2/workflows/meta — workflow/flow_endpoint.py
- GET /v2/workflows — workflow/flow_endpoint.py
- POST /plugin/{module}/{endpoint_function} — workflow/plugins_endpoint.py
- POST /plugin/{plugin_id}/config/validate — workflow/plugins_endpoint.py

**Note**: per-group subtotals above sum to slightly less than 207 due to manual transcription; treat a fresh grep of `routes/**` as authoritative if a discrepancy matters for the final count.

# Known frontend inventory (~110 endpoint functions across 31 files)

`src/remote_api/endpoints/*.jsx`, each function returns `{url, method, data?, headers?}`. Consumed via `src/hooks/useRequest.jsx` (`fetch()` wrapper, prepends the configured base URL, adds auth/tenant headers) and `src/remote_api/submit.jsx` (uniform 422-error handling). `src/hooks/useFetch.jsx` layers react-query's `useQuery` on top but still sources URLs from these same endpoint functions.

**activation.jsx** — POST /v2/activation; GET /v2/activations/meta/segment/{segmentId}; GET /v2/activation/{activationId}; GET /v2/activation/{activationId}/trigger; GET /v2/activations; DELETE /v2/activation/{id}

**actors.jsx** — POST /v2/actors/list; POST /v2/actors/histogram

**audience.jsx** — POST /v2/audience; GET /v2/audience/{audienceId}; POST /v2/audience/compute; GET /audience; DELETE /audience/{id}

**bridge.jsx** — GET /v2/bridge/{id}; GET /v2/bridges/meta

**configuration.jsx** — POST /configuration; GET /configuration/{configurationId}; GET /configuration; DELETE /configuration/{id}; GET /configuration-type

**counters.jsx** — GET /v2/count/online

**deployment.jsx** — GET /v2/production/{tableName}/{id}?action=...

**destination.jsx** — GET /destinations/by_tag; GET /v2/destinations/meta; GET /v2/destinations/trigger/meta; GET /v2/destination/trigger/{id}; POST /v2/destination; GET /v2/destination/resources/meta; DELETE /destination/{id}; GET /destination/{id}

**embedding.jsx** — GET /v2/embedding/{embeddingId}; POST /v2/embedding; GET /v2/embeddings; DELETE /v2/embedding/{id}

**entity.jsx** — GET /v2/entity/pk/{eventEntityPk}/data_hash/{dataHash}; GET /v2/entities/observation/{observationId}/observer/{observerPk}; GET /v2/entities/observation/{observationId}; GET /entity/{entityType}/hash/{hash}; GET /entity/{entityType}/logs/{entityId}; GET /v2/named/entities/1; GET /v2/named/entities/2; GET /v2/named/event/entities; GET /v2/entity/1/list; GET /v2/entity/2/list; GET /v2/entity/2/snapshot/autocomplete; GET /v2/entity/snapshot/autocomplete; GET /v2/actor/{entityPk}/events/; GET /v2/object/{entityPk}/events/; GET /v2/entity/{entityId}/history; GET /v2/entity/history/use/{dataHash}; GET /v2/entity/{entityPk}/traits/state; GET /v2/entity/texts; GET /v2/entity/observations

**entityObject.jsx** — GET /v2/entity/object/{entityId}; GET /v2/named/entity/{entityType}/properties; GET /v2/fact/traits/by/type; POST /v2/entity/object; GET /v2/entity/objects/list; DELETE /v2/entity/object/{id}

**eql.jsx** — GET /v2/eql/entity-types; GET /v2/eql/entity/locations; GET /v2/eql/facts; GET /v2/eql/observations; GET /v2/eql/text; GET /v2/eql/autocomplete; GET /v2/{index}/query/autocomplete

**event.jsx** — GET /v2/event/{id}; GET /event/logs/{eventId}; POST /v2/events/list; DELETE /v2/event/{id}; GET /v2/named/event/types; GET /v2/named/event/actors; POST /v2/events/histogram; (dead/commented: `getStitchEventsSearch` → /v2/events/stitch/list)

**eventMapping.jsx** — GET /event-type/search/mappings; DELETE /event-type/mapping/{id}; GET /event-type/mapping/{id}; POST /event-type/mapping

**eventReshaping.jsx** — GET /event-reshape-schema; DELETE /event-reshape-schema/{id}; GET /event-reshape-schema/{id}; POST /event-reshape-schema

**eventSource.jsx** — GET /v2/event-sources/running; GET /v2/event-sources; DELETE /v2/event-source/{id}; GET /v2/event-source/{id}; POST /v2/event-source; GET /v2/event-sources/type; GET /v2/event-sources?output=meta

**eventValidation.jsx** — GET /v2/event-configs; DELETE /v2/event-config/{id}; GET /v2/event-config/{id}; POST /v2/event-config

**feed.jsx** — GET /feed

**flow.jsx** — POST /v2/workflow/debug; GET /v2/workflows; GET /v2/workflow/{workflowId}; POST /v2/workflow; POST /v2/workflow/dag; GET /v2/workflow/dag/{workflowId}; POST /v2/workflow/rearrange; DELETE /v2/workflow/{id}

**github.jsx** — POST /github/workflow/{id}; GET /github/list; GET /github/load

**logs.jsx** — GET /log/alerts; POST /log/range; POST /log/histogram; GET /node/logs/{nodeId}

**observation.jsx** — GET /v2/observation/{observationId}; POST /v2/observations/list; GET /v2/observation/{observationId}/facts; DELETE /v2/observation/{observationId}; GET /v2/observers; POST /v2/observations/histogram

**plugin.jsx** — GET /flow/action/plugins; DELETE /flow/action/plugin/{id}; GET /flow/action/plugin/{id}; GET /flow/action/plugin/{id}/enable/{yes|no}; GET /flow/action/plugin/{id}/hide/{yes|no}; PUT /flow/action/plugin/{id}/icon/{icon}; PUT /flow/action/plugin/{id}/name/{name}; POST /plugin/{pluginId}/config/validate; GET /flow/action/plugins?flow_type=...; GET /plugin/form; GET /tpro/plugin/{module}; GET /actions?service_id=...

**report.jsx** — GET /reports/entities

**resource.jsx** — GET /resources/by_type; DELETE /resource/{id}; GET /resource/{id}; POST /resource; GET /resources/type/name; GET /resources/type/configuration; GET /resources/entity[/tag/{tag}]

**segment.jsx** — POST /v2/segment; GET /v2/segment/{segmentId}; POST /v2/segment/estimate; POST /v2/segment/sample; GET /v2/segment/sample/{segmentId}; GET /v2/segments/meta; GET /v2/segments; DELETE /segment/{id}

**system.jsx** — GET /; GET /v2/install; POST /v2/install; GET /v2/install/plugins; GET /system/settings; GET /info/version/details; GET /v2/system/table/stats

**task.jsx** — GET /v2/task/{taskId}/status; GET /v2/tasks[/type/{type}]

**timer.jsx** — GET /v2/timer/{timerId}

**tracker.jsx** — POST https://track.tracardi.com/track (external, not a backend GUI route — exclude from matching)

**user.jsx** — POST /user/token; GET /user/{id}; GET /users; DELETE /user/{id}; POST /user/{id}; POST /user; POST /user/logout; GET /user-account; POST /user-account

# Known findings (already verified — confirm still true, don't re-derive)

## (a) Frontend-only calls with no obvious backend match
- `entity.jsx` → `getEntities2List` → `GET /v2/entity/2/list` — the backend inventory above only has `GET /v2/entity/1/list` (`data/entity_endpoint.py`). No `/v2/entity/2/list` route was found. **Confirm during execution** (re-grep backend) before concluding it's genuinely missing — the backend transcription had a minor unreconciled subtotal, so double check this specific one rather than trusting the initial pass blindly.
- `report.jsx` → `getReportEntities` → `GET /reports/entities` — no matching backend route found in the inventory above.
- `plugin.jsx` → `getMicroservicePluginForm` (`GET /plugin/form`), `getTproPlugin` (`GET /tpro/plugin/{module}`), `getMicroserviceActions` (`GET /actions?service_id=...`) — none of these paths appear in the backend route inventory; may hit a different service (microservice plugin host) rather than the GUI API — confirm the base URL used for these calls before flagging as broken.
- `github.jsx` (all 3 routes: `/github/workflow/{id}`, `/github/list`, `/github/load`) — no matching backend route found; likely hits a different backend service — confirm before flagging.

## (b) Direct/inline bypasses of `remote_api/endpoints` (frontend calling the backend directly)
1. `src/components/elements/tui/TuiSelectMultiConsentType.jsx:18` — hardcodes `url="/consents/type/ids"` passed straight into `useRequest().request()`. No `consent.jsx` endpoint file exists, and no matching backend route was found in the inventory above either — this may be entirely dead/broken.
2. `src/components/pages/Chat.jsx:31` — `new EventSource('http://127.0.0.1:8585/ai/chat?query=...')`. Hardcoded absolute localhost URL, bypasses both the endpoints layer and the configurable API base URL (`getApiUrl()`). Looks like leftover dev/debug code pointing at a local server that isn't part of the GUI API on port 4001.
3. `src/misc/location.jsx:3` — `fetch('https://geolocation-db.com/json/')`. Third-party geolocation service, not the app's own backend — lower priority than #1/#2, but still a raw inline `fetch()` outside the endpoints layer.

# Explicit exclusions from "dead code" flagging

Some backend routes are legitimately not called from `remote_api/endpoints` and should not be flagged as dead:

- Health/readiness/introspection: `management/health_endpoint.py` (`/ping`, `/healthcheck`), `management/info_endpoint.py`, `debug_endpoint.py` — likely used by infra/ops tooling, load balancers, or monitoring, not the GUI itself.
- `management/migration_endpoint.py` (`/migration/mysql/upgrade`) — likely an ops/CLI-triggered action.
- `install/install_endpoint.py` is used (`system.jsx` calls `/v2/install`), so it's covered — listed here only as a reminder to check other install-adjacent routes similarly.
- `routes/workflow/*` — only flag as dead if the commercial workflow module itself is confirmed unused in this deployment, not by the same bar as regular routes (see Methodology).

# Output format

Produce a findings table (markdown or CSV) with columns: `method`, `normalized_path`, `backend_file(s)`, `frontend_file(s) / call_site`, `status` where `status` is one of:
- `matched` — appears on both sides.
- `backend_only` — dead-code candidate (needs human review; skip anything in "Explicit exclusions" above).
- `frontend_only` — stale/broken call, or hits a non-GUI-API service (confirm base URL before concluding "broken").
- `bypass` — frontend call site that skips `remote_api/endpoints` (list the 3 known ones plus any newly found).

# How to verify this spec

1. The findings table's `matched` + `backend_only` row count should equal the backend route count (re-grep `routes/**` to get the authoritative number; this spec's own pass found 207 but flagged a minor unreconciled subtotal — resolve that first).
2. The findings table's `matched` + `frontend_only` row count should equal the frontend endpoint-function count (~110, re-scan `remote_api/endpoints/*.jsx` to confirm).
3. All 3 known bypasses above appear in the table with `status = bypass`.
4. This step makes no code or behavior changes — there is nothing to run or test beyond confirming the table is complete and internally consistent.
