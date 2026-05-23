---
name: create-metadata-table
description: >
  Use this skill whenever the user asks to add a new metadata entity, create a new system
  table, add a new type to the metadata storage, or wire up a new domain model to the database.
  Covers the complete 6-step process: domain model → ORM table → mapping → service → DAO → registration.
  Trigger on phrases like "create a metadata table for", "add a new entity to metadata storage",
  "wire up X to the database", "add a sys_ table", or any new Pydantic model that needs to be
  persisted in the MySQL/SQLite metadata layer.
---

# Creating a Metadata Storage Table

This codebase stores all metadata in MySQL or SQLite via SQLAlchemy async. Every new entity type
requires **6 coordinated pieces** across 6 directories. Miss one and the entity won't be
reachable. This skill walks through all of them in order.

---

## Step 0 — Gather requirements before writing anything

Ask (or infer from context) the following:

1. **Entity name** — e.g. `CanonicalEntity`, `WorkflowStep`. Drives all file names.
2. **Fields** — names, Python types, nullable?, default?. Ask for a rough list; you can refine later.
3. **Scope** — Is this a *tenant-global* entity or a *deployment-scoped* entity?
   - **Tenant-global** (`sys_bridge`, `sys_configuration`, `sys_canonical_entity`): only one copy
     per tenant; no concept of test vs production data. PK = `(id, tenant)`.
   - **Deployment-scoped** (`sys_source`, `sys_resource`, `sys_destination`, …): exists in both
     test and production contexts for the same tenant. PK = `(id, tenant, production)`.
     These tables get a `running: bool = False` Python attribute (not a DB column) set at query time.
4. **Child tables?** — Does this entity own a list of related sub-objects that need their own
   table? (E.g. `CanonicalEntityProperty` belongs to `CanonicalEntity`.) If yes, gather their
   fields too.
5. **Preconfig?** — Are there built-in, non-editable records to seed on startup? If yes, note it
   (handled in `airembr/system/preconfig/` and called from `mysql_installation.py`).

---

## Step 1 — Domain model (`airembr/model/metadata/sys_<snake_name>.py`)

Plain Pydantic `BaseModel`. No SQLAlchemy imports here.

```python
from typing import Optional, List
from airembr.model.system.named_entity import NamedEntity   # provides id, name

class MyEntity(NamedEntity):
    description: Optional[str] = None
    enabled: bool = False
    # … other fields

# Child model if needed:
class MyEntityItem(NamedEntity):
    my_entity_id: str          # FK back to parent
    value: str
```

Key rules:
- Inherit `NamedEntity` (gives `id` + `name`).
- For deployment-scoped entities, also consider inheriting `NamedEntityInContext` (adds `production: bool`, `running: bool`). The `running` field is **never persisted** — it is set at query time by the service layer.
- Sub-objects that will be stored as a JSON column (e.g. a `Form`, a config struct) stay as
  nested Pydantic models — do not flatten them unless the table really needs individual columns.
- Enums should extend `(str, Enum)` so they round-trip cleanly from JSON.

---

## Step 2 — ORM table (`airembr/system/adapter/metadata/mysql/schema/table.py`)

Append new class(es) to this file. Two PK patterns:

### Tenant-global pattern (no `production` column)

```python
class MyEntityTable(Base):
    __tablename__ = 'sys_my_entity'

    id     = Column(String(40), nullable=False, index=True)
    tenant = Column(String(40), nullable=False)
    name   = Column(String(128), nullable=False, index=True)
    # … other columns

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
        UniqueConstraint('name', 'tenant', name='uiq_my_entity_name'),   # if name must be unique
    )
```

### Deployment-scoped pattern (has `production` column)

```python
class MyEntityTable(Base):
    __tablename__ = 'sys_my_entity'

    id         = Column(String(40), index=True)
    tenant     = Column(String(40))
    production = Column(Boolean)
    name       = Column(String(128), index=True)
    enabled    = Column(Boolean, default=False)
    tags       = Column(String(128), nullable=True)   # stored as comma-joined string
    # … other columns

    running: bool = False   # Python-only attribute, NOT a DB column

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_my_entity', 'tenant', 'production', 'enabled'),
    )
```

### Child table with FK to parent

```python
class MyEntityItemTable(Base):
    __tablename__ = 'sys_my_entity_item'

    id           = Column(String(40), nullable=False, index=True)
    tenant       = Column(String(40), nullable=False)
    name         = Column(String(64), nullable=False)
    my_entity_id = Column(String(40), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
        ForeignKeyConstraint(
            ['my_entity_id', 'tenant'],
            ['sys_my_entity.id', 'sys_my_entity.tenant'],
        ),
        UniqueConstraint('my_entity_id', 'name', 'tenant', name='uiq_item_name'),
        Index('idx_item_entity', 'my_entity_id', 'tenant'),
    )

    entity = relationship("MyEntityTable", back_populates="items")
```

Add the corresponding `relationship()` on the parent table too:

```python
items = relationship(
    "MyEntityItemTable",
    back_populates="entity",
    cascade="all, delete-orphan",
    foreign_keys="[MyEntityItemTable.my_entity_id, MyEntityItemTable.tenant]",
)
```

Column type reference:
- `String(40)` — UUIDs/IDs; `String(64/128/255)` — names/labels
- `Text` — long free-form text, descriptions, markdown, JSON stored as text
- `JSON` — structured sub-objects (dicts/lists); prefer over `Text` when the value is always parsed
- `Boolean` — flags; always give a `default=` when it has one
- `DateTime` / `TIMESTAMP` — timestamps (`DateTime` for Python `datetime`, `TIMESTAMP` for DB-native)
- `Integer` / `Float` — numbers

---

## Step 3 — Mapping functions (`airembr/system/adapter/metadata/mysql/mapping/<snake_name>_mapping.py`)

Create a new file. Always two functions — one in each direction.

```python
from airembr.model.metadata.sys_my_entity import MyEntity
from airembr.model.system.context import get_context
from airembr.system.adapter.metadata.mysql.schema.table import MyEntityTable
# If the entity has JSON sub-objects (e.g. a Form or config):
# from airembr.system.adapter.metadata.mysql.utils.serilizer import from_model, to_model

def map_to_my_entity_table(entity: MyEntity) -> MyEntityTable:
    context = get_context()    # injects tenant (and production for scoped entities)
    return MyEntityTable(
        id=entity.id,
        tenant=context.tenant,
        # production=context.production,   # add only for deployment-scoped tables
        name=entity.name,
        description=entity.description,
        enabled=entity.enabled,
        tags=','.join(entity.tags) if entity.tags else None,  # if tags is a list
        # config=from_model(entity.config),   # if config is a Pydantic sub-object
    )

def map_to_my_entity(table: MyEntityTable) -> MyEntity:
    return MyEntity(
        id=table.id,
        name=table.name,
        description=table.description,
        enabled=table.enabled,
        tags=table.tags.split(',') if table.tags else [],  # split back to list
        # config=to_model(table.config, MyConfig),   # deserialize JSON sub-object
    )   # tenant is intentionally excluded from the domain model
```

Important details:
- `get_context()` is the **only** way to inject `tenant` and `production` — callers never pass these.
- Tags/groups are stored as comma-joined strings; split on read, join on write.
- Credentials fields (e.g. on `Resource`, `User`) must use `encrypt()` / `decrypt()` from
  `airembr.core.security`. Check existing `resource_mapping.py` if you need encryption.
- JSON sub-objects: use `from_model(obj)` to serialize a Pydantic model to a JSON-compatible dict
  for storage, and `to_model(raw, ModelClass)` to deserialize on read. Both are in
  `airembr/system/adapter/metadata/mysql/utils/serilizer.py`.

---

## Step 4 — Service class (`airembr/system/adapter/metadata/mysql/service/<snake_name>_service.py`)

Create a new file. Thin wrapper around `TableServiceProxy`.

```python
from airembr.model.metadata.sys_my_entity import MyEntity
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.system.adapter.metadata.mysql.mapping.my_entity_mapping import map_to_my_entity_table
from airembr.system.adapter.metadata.mysql.schema.table import MyEntityTable


class MyEntityService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self) -> SelectResult:
        return await self.proxy.base_load_all(MyEntityTable, server_context=False)

    async def load_by_id(self, entity_id: str) -> SelectResult:
        return await self.proxy.load_by_id(MyEntityTable, primary_id=entity_id, server_context=False)

    async def insert(self, entity: MyEntity):
        return await self.proxy.insert_if_none(MyEntityTable, map_to_my_entity_table(entity), server_context=False)

    async def replace(self, entity: MyEntity):
        return await self.proxy.replace(MyEntityTable, map_to_my_entity_table(entity))

    async def delete_by_id(self, entity_id: str):
        return await self.proxy.delete_by_id(MyEntityTable, primary_id=entity_id, server_context=False)
```

**Proxy method selection:**

| Situation | Method to use |
|---|---|
| Tenant-global table | Always pass `server_context=False` |
| Deployment-scoped, normal load | `load_by_id` / `base_load_all` with default context |
| Deployment-scoped, merge test+production | `load_by_id_in_deployment_mode` / `load_all_in_deployment_mode` |
| Custom WHERE clause | `field_filter(Table, Table.column, value, ...)` |
| Delete by arbitrary field | Build a where clause with `where_only_tenant_context()` + `proxy.delete_query()` |

**Write method selection:**

| Situation | Method |
|---|---|
| Bootstrap / idempotent seed | `insert_if_none` |
| User creates or updates (upsert) | `replace` |
| Plain insert (error on duplicate) | `insert` |
| Update without replace | `update_by_id` |
| Delete | `delete_by_id` |

For child-table services (e.g. `MyEntityItemService`), add a `load_by_entity_id` method using
`field_filter` on the FK column, and a `delete_by_entity_id` method using `where_only_tenant_context`.
See `canonical_entity_service.py` for the exact pattern.

---

## Step 5 — DAO module (`airembr/system/adapter/metadata/mysql/interface/dao/<snake_name>.py`)

Create a new file. This is the public API used by application logic.

```python
from typing import List, Optional, Tuple

from airembr.model.metadata.sys_my_entity import MyEntity
from airembr.system.adapter.metadata.mysql.mapping.my_entity_mapping import map_to_my_entity
from airembr.system.adapter.metadata.mysql.service.my_entity_service import MyEntityService

mes = MyEntityService()   # module-level singleton


async def load_my_entity_by_id(entity_id: str) -> Optional[MyEntity]:
    record = await mes.load_by_id(entity_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_my_entity)


async def load_all_my_entities(query=None, limit=None, start=None) -> Tuple[List[MyEntity], int]:
    records = await mes.load_all()
    if not records.exists():
        return [], 0
    return list(records.map_to_objects(map_to_my_entity)), records.count()


async def insert_my_entity(entity: MyEntity):
    await mes.insert(entity)


async def replace_my_entity(entity: MyEntity):
    await mes.replace(entity)


async def delete_my_entity_by_id(entity_id: str):
    await mes.delete_by_id(entity_id)
```

`SelectResult` API reference:
- `record.exists()` — True if any rows were returned
- `record.map_to_object(fn)` — maps a single row
- `record.map_first_to_object(fn)` — maps first row from a list (for field_filter results)
- `records.map_to_objects(fn)` — generator over all rows
- `records.map_to_objects(fn, filter=lambda r: r.enabled)` — with server-side filter
- `records.as_named_entities()` — lightweight `id`/`name` pairs without full mapping
- `records.count()` — number of rows

**Preconfig check** — if this entity type has built-in non-editable records (seeded at startup),
add a preconfig check *before* the database fallback. See `event_source` DAO for the pattern.

**Cache invalidation** — if query results are Redis-cached, decorate mutating functions with
`@invalidate_cache_proxy`. Check existing DAOs for usage.

---

## Step 6 — Register in `__init__.py`

Edit `airembr/system/adapter/metadata/mysql/interface/__init__.py`:

```python
# Add import:
import airembr.system.adapter.metadata.mysql.interface.dao.my_entity as my_entity_dao

# Add to __all__:
__all__ = [
    ...
    'my_entity_dao',
]
```

---

## Step 7 — CRUD endpoint (`bizmory/api/endpoint/gui/routes/<area>/<snake_name>_endpoint.py`)

Create a new file. All four CRUD routes plus the router definition:

```python
from airembr.system.adapter.metadata.mysql.interface import my_entity_dao
from typing import Optional
from fastapi import APIRouter, Depends, Response
from airembr.system.process.logging.log_handler import get_logger
from api.endpoint.gui.auth.permissions import Permissions
from airembr.model.metadata.sys_my_entity import MyEntity
from airembr.system.config.sys_config import sys_config

logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/my-entities", tags=["my-entity"],
            include_in_schema=sys_config.expose_gui_api)
async def list_my_entities(query: str = None, limit: int = 100):
    records, count = await my_entity_dao.load_all_my_entities(query, limit=limit)
    return {"total": count, "grouped": {"MyEntities": records}}


@router.get("/v2/my-entity/{id}", tags=["my-entity"],
            response_model=Optional[MyEntity],
            include_in_schema=sys_config.expose_gui_api)
async def load_my_entity_by_id(id: str, response: Response):
    record = await my_entity_dao.load_my_entity_by_id(id)
    if not record:
        response.status_code = 404
        return None
    return record


@router.post("/v2/my-entity", tags=["my-entity"],
             include_in_schema=sys_config.expose_gui_api)
async def save_my_entity(entity: MyEntity):
    return await my_entity_dao.insert_my_entity(entity)


@router.delete("/v2/my-entity/{id}", tags=["my-entity"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_my_entity(id: str):
    return await my_entity_dao.delete_my_entity_by_id(id)
```

Key rules:
- All routes use the `v2/` prefix.
- Auth via `Permissions` is declared **once at the router level** — never repeated per route.
- 404 is signalled by setting `response.status_code = 404` and returning `None` — do not raise `HTTPException`.
- `include_in_schema=sys_config.expose_gui_api` goes on every route.
- There is **no PUT** — POST is an upsert (`replace` in the DAO handles both create and update).
- If the entity has a Redis cache TTL, add `"cache": memory_cache_config.<entity>_ttl` to the list response (import `memory_cache_config` from `airembr.system.config.memory_cache_config`).
- `<area>` matches where related endpoints live — e.g. `inbound/` for sources, `outbound/` for destinations. When unsure, put it in `routes/` directly.

Response shape reference (helpers in `bizmory/api/service/grouping.py`):
- List → `{"total": N, "grouped": {"Label": [...]}}` — use for browsable entity lists
- Flat list → `{"total": N, "result": [...]}` — use for lightweight name/id lookups
- Single → return the model directly; set `response.status_code = 404` when missing

---

## Step 8 — Register router in `main.py`

File: `bizmory/api/endpoint/gui/main.py`

1. Add the import in the relevant group at the top of the file:
   ```python
   from api.endpoint.gui.routes.<area> import my_entity_endpoint
   ```
2. Add one line to register the router (near related entities):
   ```python
   application.include_router(my_entity_endpoint.router)
   ```

---

## Checklist

Before declaring done, verify:

- [ ] `sys_<name>.py` domain model created in `airembr/model/metadata/`
- [ ] Table class(es) appended to `schema/table.py`, correct PK pattern
- [ ] Child tables have `ForeignKeyConstraint` that includes `tenant` in both sides
- [ ] `relationship()` added on parent table if there are children
- [ ] Mapping file created with both `map_to_*_table()` and `map_to_*()` functions
- [ ] `get_context()` used in the write-direction mapping — never passed from caller
- [ ] Service file created, correct `server_context` and deployment-mode method choices
- [ ] DAO file created with `load_by_id`, `load_all`, `insert`, `replace`, `delete_by_id`
- [ ] DAO registered in `interface/__init__.py` (import + `__all__`)
- [ ] If deployment-scoped: `production` column in table, `running: bool = False` attribute
- [ ] If tags/groups: stored as comma-joined string, split on read
- [ ] Endpoint file created with all 4 CRUD routes
- [ ] `router = APIRouter(dependencies=[Depends(Permissions(...))])` at module level (not per-route)
- [ ] `include_in_schema=sys_config.expose_gui_api` on every route
- [ ] Router imported and registered in `main.py`

---

## Quick reference: existing entities by pattern

**Tenant-global (no production column):**
- `BridgeTable` / `bridge_mapping.py` / `BridgeService` — simplest possible example
- `CanonicalEntityTable` + `CanonicalEntityPropertyTable` — parent/child with FK, relationship

**Deployment-scoped (has production, running):**
- `EventSourceTable` / `EventSourceService` — uses deployment-mode queries, has preconfig
- `ResourceTable` — has encrypted `credentials` field
- `DestinationTable` — has composite index for query performance
- `EmbeddingTable` — minimal deployment-scoped example
