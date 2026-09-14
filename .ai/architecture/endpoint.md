# API Endpoint Architecture

Scope: this document describes the endpoint architecture under
`airembr_api/endpoint/gui/v1/`. This is the **only structure to follow for
new work** — the sibling `airembr_api/endpoint/gui/routes/` tree (flat,
per-concern folders: `crud/`, `data/`, `mapping/`, `inbound/`, `outbound/`,
`management/`, `install/`, `workflow/`, `gui/`) is the legacy layout and is
out of scope here, referenced only where it is still wired into the running
app.

Status legend used below: **[implemented]** exists in code today,
**[planned]** described in design notes / this doc but not yet built.

## 1. Directory layout

```
airembr_api/endpoint/gui/v1/
├── routes/
│   ├── meta/                    [implemented — pattern only, one domain object so far]
│   │   └── bridge/              [implemented]
│   │       ├── crud_endpoint.py [implemented]
│   │       └── list_endpoint.py [implemented as a file, body not yet written]
│   ├── data/                    [planned]
│   └── operation/               [planned]
└── tools/
    └── auth/                    [implemented]
        ├── authentication.py
        ├── permissions.py
        └── user_db.py
```

`v1` is a **version root**: everything that belongs to major API version 1
lives under it. A future breaking version is expected to live in a sibling
`airembr_api/endpoint/gui/v2/` root, mirroring the same internal shape
(`routes/{meta,data,operation}` + `tools/`) rather than branching inside
`v1`.

## 2. `routes/` — the three endpoint categories

`routes/` splits endpoints into three categories by *what kind of thing*
they act on, not by domain object:

- **`meta/`** [implemented] — endpoints for objects that configure the
  system itself (system/domain configuration, metadata). One subfolder per
  domain object (see §3). Today this holds `bridge/` only.
- **`data/`** [planned] — endpoints for the data the system stores and
  processes (business/runtime data), as opposed to system configuration.
  Expected to follow the same per-domain-object subfolder pattern as
  `meta/`.
- **`operation/`** [planned] — endpoints for global, cross-object
  operations that don't belong to a single domain object, e.g. import,
  export, migration-style actions.

These three folders are peers directly under `routes/`; a domain object's
endpoints live under whichever category folder matches what the object
represents (e.g. `routes/meta/bridge/` for the bridge configuration object).

## 3. `meta/<domain>/` — per-domain-object endpoint folder

Each domain object gets its own folder named after it (e.g. `bridge`).
Inside, endpoints are split by concern into separate files:

- **`crud_endpoint.py`** [implemented] — single-resource operations: get by
  id, create, update, delete. One `APIRouter` per file.
- **`list_endpoint.py`** [implemented as a stub] — collection endpoints:
  list/search/filter over the domain object. Intended contract (not yet
  implemented for `bridge`): a `GET` collection route returning a paged/
  filtered list, following the same router + `Permissions` + command-layer
  delegation pattern as `crud_endpoint.py` (see §4).
- **Additional files as needed** — any other endpoint category specific to
  that one domain object gets its own file in the same folder (e.g. a
  hypothetical `stats_endpoint.py` for bridge-specific statistics), rather
  than being folded into `crud_endpoint.py` or `list_endpoint.py`.

Each file defines its own `router = APIRouter(...)`; these are included
individually into the app (see §6), not aggregated at the domain-folder
level.

### Reference implementation — `meta/bridge/crud_endpoint.py`

```python
from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.bridge.bridge import (
    get_data_bridge_by_id as get_data_bridge_by_id_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/bridge/{bridge_id}", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridge_by_id(bridge_id: str):
    """
    Returns data bridge
    """
    return await get_data_bridge_by_id_cmd(bridge_id)
```

This is the template for every new `crud_endpoint.py` / `list_endpoint.py`:

1. `router = APIRouter(dependencies=[Depends(Permissions(roles=[...]))])` —
   authorization is declared once per router, at router-construction time,
   not per-route.
2. Each route is tagged with the domain object name (`tags=["bridge"]`) so
   it groups correctly in the generated OpenAPI docs.
3. `include_in_schema=sys_config.expose_gui_api` gates whether the route is
   visible in the docs/schema based on the `EXPOSE_GUI_API` feature flag.
4. The route handler body only calls into the `airembr.system.command.*`
   layer and returns its result — no business logic lives in the endpoint
   module itself.

Known inconsistency (flagged, not fixed here per your instruction — you're
handling it separately): the route path above is `/v2/bridge/{bridge_id}`
even though the module lives under the `v1` package. Whatever the resolved
convention turns out to be, keep it consistent across all `meta/`, `data/`
and `operation/` endpoints — the path version prefix and the folder version
should not silently diverge.

## 4. `tools/` — cross-cutting infrastructure

`tools/` holds infrastructure that endpoints depend on but that isn't an
endpoint itself. Today it has one subfolder:

### `tools/auth/`

- **`authentication.py`** — `Authentication` class wrapping
  `airembr.system.command.auth.login` (`login` / `logout`); exposed via a
  module-level singleton accessor `get_authentication()`. Also defines the
  `oauth2_scheme` (`OAuth2PasswordBearer(tokenUrl="/user/token")`) used for
  extracting the bearer token.
- **`permissions.py`** — `Permissions`, a callable FastAPI dependency class
  constructed with a list of allowed roles (`Permissions(roles=["admin",
  "developer"])`). When invoked as a dependency it extracts the bearer
  token, calls `airembr.system.command.auth.permissions.authorize(token,
  roles, request_path=...)`, and converts an `AuthError` into an
  `HTTPException` with the error's status code. This is the standard,
  and only, way v1 endpoints declare access control — attach it at the
  router level (as in §3), not ad hoc per route.
- **`user_db.py`** — thin re-export of `TokenDb` and `token2user` from
  `airembr.system.command.auth.token_store`, so endpoint code under `v1`
  imports auth internals through `tools/auth` rather than reaching into
  `airembr.system.command.auth` directly.

Future non-auth cross-cutting concerns (e.g. rate limiting, request
context helpers specific to v1) would follow the same pattern: a new
subfolder under `tools/`.

## 5. Authorization model (as implemented)

`authorize()` (`airembr/system/command/auth/permissions.py`) is the actual
policy enforced behind `Permissions`:

1. If the `EXPOSE_GUI_API` feature flag is off, or no token is present,
   access is denied (`403`).
2. The token must resolve to a known user via `token2user` (`401` if not).
3. The token is refreshed on each check; a mismatch after refresh
   invalidates both the old and new token and denies access (`401`).
4. The resolved user must have at least one of the router's required
   roles (`user.has_roles(roles)`), else `401`.

Implication for new endpoints: role lists passed to `Permissions(roles=[...])`
are an "any of" check, not "all of".

## 6. App wiring — current state and planned direction

**Current state [implemented]:** there is no `main.py` under `v1` yet.
All routers — legacy and v1 alike — are registered on one flat `FastAPI`
app in `airembr_api/endpoint/gui/main.py`:

```python
from airembr_api.endpoint.gui.v1.routes.meta.bridge import crud_endpoint as crud_bridge_endpoint
...
application.include_router(crud_bridge_endpoint.router)
```

The v1 `bridge` CRUD router is included the same way as every legacy
router, side by side with the old `routes/crud`, `routes/inbound`, etc.
routers for other domain objects that haven't been migrated yet.

**Planned direction [planned]:** each version root (`v1`, later `v2`, ...)
gets its own `main.py` that builds a version-scoped `APIRouter`/sub-app by
aggregating that version's `routes/{meta,data,operation}` routers. The
top-level `airembr_api/endpoint/gui/main.py` then mounts each version's
aggregate (e.g. under `/v1`, `/v2`) instead of importing individual
per-domain routers directly. Until that aggregator exists, new domain
objects added under `v1` must still be wired into the top-level
`gui/main.py` by hand, following the existing `crud_bridge_endpoint`
example.

## 7. Checklist — adding a new domain object under v1

1. Decide the category: does it configure the system (`meta/`), represent
   stored/runtime data (`data/`, once created), or is it a global
   cross-object operation (`operation/`, once created)?
2. Create `routes/<category>/<domain>/` with an empty `__init__.py`.
3. Add `crud_endpoint.py` for single-resource operations, following the
   template in §3.
4. Add `list_endpoint.py` for collection/search operations, same template.
5. Add further `*_endpoint.py` files in the same folder for any other
   concern specific to that domain object.
6. Pick the required roles for `Permissions(roles=[...])` per router.
7. Register every new router in `airembr_api/endpoint/gui/main.py` via
   `application.include_router(...)` (until the planned per-version
   `main.py` aggregator in §6 exists).
8. Keep the route path version prefix consistent with the folder version
   root (see the flagged inconsistency in §3).
