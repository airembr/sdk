# Metadata Storage

Metadata (system configuration, sources, resources, users, etc.) is persisted in either MySQL or SQLite via SQLAlchemy async. The storage spans seven layers across separate directories. This document traces the full path from a domain model to the database and back.

---

## Layer 1 — Domain models (`airembr/model/metadata/`)

Plain Pydantic `BaseModel` classes with no SQLAlchemy knowledge. They inherit from shared base classes:

- `NamedEntity` — provides `id`, `name`
- `NamedEntityInContext` — adds `production: bool` and `running: bool` (`running` is a runtime flag; it is never persisted)

All thirteen metadata types and their corresponding DB tables:

| Model class | File | DB table |
|---|---|---|
| `Bridge` | `sys_bridge.py` | `sys_bridge` |
| `EventSource` | `sys_source.py` | `sys_source` |
| `Resource` | `sys_resource.py` | `sys_resource` |
| `Destination` | `sys_destination.py` | `sys_destination` |
| `EventValidator` | `sys_evt_validation.py` | `sys_evt_validation` |
| `EventReshapingSchema` | `sys_evt_reshaping.py` | `sys_evt_reshaping` |
| `EventTypeMetadata` | `sys_event_mapping.py` | `sys_evt_mapping` |
| `Task` | `sys_task.py` | `sys_task` |
| `Setting` | `sys_setting.py` | `sys_setting` |
| `Configuration` | `sys_configuration.py` | `sys_configuration` |
| `User` | `sys_user.py` | `sys_user` |
| `EntitySegment` | `sys_ent_segment.py` | `sys_ent_segment` |
| `EmbeddingSetting` | `sys_embedding_setting.py` | `sys_embedding_setting` |

---

## Layer 2 — ORM table definitions (`airembr/system/adapter/metadata/mysql/schema/table.py`)

One class inheriting from `Base` (from `airembr/sdk/storage/metadata/db_base.py`) per entity. All tables are multi-tenant by design.

**Two composite primary key patterns:**

Tenant-global entities (e.g. `BridgeTable`) — `production` is not relevant, PK is `(id, tenant)`:
```python
class BridgeTable(Base):
    __tablename__ = 'sys_bridge'
    id = Column(String(40))
    tenant = Column(String(40))
    ...
    __table_args__ = (PrimaryKeyConstraint('id', 'tenant'),)
```

Deployment-scoped entities (e.g. `EventSourceTable`) — have a `production` column that separates test and production datasets, PK is `(id, tenant, production)`:
```python
class EventSourceTable(Base):
    __tablename__ = 'sys_source'
    id = Column(String(40))
    tenant = Column(String(40))
    production = Column(Boolean)
    ...
    running: bool = False          # Python-only attribute, not a DB column
    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_tenant', 'tenant', 'production', 'enabled')
    )
```

The `running` Python attribute is set at query time by deployment-mode queries (see Layer 4) to indicate that a record is the currently active version.

---

## Layer 3 — Mapping functions (`airembr/system/adapter/metadata/mysql/mapping/`)

One file per entity (e.g. `bridge_mapping.py`), always containing exactly two functions — one in each direction:

```python
# Domain model → ORM row (for writes)
def map_to_bridge_table(bridge: Bridge) -> BridgeTable:
    context = get_context()          # tenant (and production) injected from request context
    return BridgeTable(
        id=bridge.id,
        tenant=context.tenant,
        name=bridge.name,
        form=from_model(bridge.form),   # Pydantic sub-object → JSON
        ...
    )

# ORM row → Domain model (for reads)
def map_to_bridge(bridge_table: BridgeTable) -> Bridge:
    return Bridge(
        id=bridge_table.id,
        name=bridge_table.name,
        form=to_model(bridge_table.form, Form),   # JSON → Pydantic sub-object
        ...
    )   # tenant is not included in the domain model
```

Key responsibilities of the mapping layer:
- **Context injection**: `get_context()` provides `tenant` (and `production` for deployment-scoped tables). Callers never pass these explicitly.
- **Sub-object serialization**: `from_model()` / `to_model()` in `mysql/utils/serilizer.py` handle Pydantic objects stored as JSON columns (e.g. `Form`, `DestinationConfig`).
- **Encryption**: Credentials fields on `Resource` and `User` are encrypted when writing and decrypted when reading.
- **Tag lists**: `tags` and `groups` fields are stored as comma-joined strings and split on read.

---

## Layer 4 — Service classes (`airembr/system/adapter/metadata/mysql/service/`)

One class per entity (e.g. `BridgeService`). Each instantiates a `TableServiceProxy` and calls the appropriate mapping functions:

```python
class BridgeService:
    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self) -> SelectResult:
        return await self.proxy.base_load_all(BridgeTable, server_context=False)

    async def load_by_id(self, bridge_id: str) -> SelectResult:
        return await self.proxy.load_by_id(BridgeTable, primary_id=bridge_id, server_context=False)

    async def insert(self, bridge: Bridge):
        return await self.proxy.insert_if_none(BridgeTable, map_to_bridge_table(bridge), server_context=False)

    async def replace(self, bridge: Bridge):
        return await self.proxy.replace(BridgeTable, map_to_bridge_table(bridge))

    async def delete_by_id(self, bridge_id: str):
        return await self.proxy.delete_by_id(BridgeTable, primary_id=bridge_id, server_context=False)
```

**Two query families:**

| Variant | Proxy method | Behaviour |
|---|---|---|
| Deployment mode | `load_by_id_in_deployment_mode`, `load_all_in_deployment_mode`, etc. | Queries both `production=True` and `production=False` rows. Merges results — test row wins when IDs match. Sets `running=True` on production rows. |
| Plain | `base_load_all`, `load_by_id`, `field_filter`, etc. | Queries a single context. Pass `server_context=False` to bypass production filtering entirely (used for tenant-global tables like `BridgeTable`). |

**Write operations:**

| Method | SQL behaviour |
|---|---|
| `insert_if_none` | INSERT — skips silently if row already exists (used for bootstrap) |
| `replace` | Upsert — `ON DUPLICATE KEY UPDATE` (MySQL) or `ON CONFLICT DO UPDATE` (SQLite) |
| `insert` | Plain INSERT |
| `update_by_id` | UPDATE WHERE id = ? |
| `delete_by_id` | DELETE WHERE id = ? |

---

## Layer 5 — TableServiceProxy (`airembr/sdk/storage/metadata/proxy/table_service_proxy.py`)

Strategy pattern. Instantiated by every service class. Routes all calls to either `MysqlTableService` or `SqliteTableService` based on the `META_DATA_ADAPTER` environment variable:

```python
class TableServiceProxy:
    def __init__(self):
        if meta_data_adapter == 'mysql':
            self.ts = MysqlTableService()    # aiomysql async driver
        else:
            self.ts = SqliteTableService()   # aiosqlite async driver
```

Every public method on `TableServiceProxy` is a thin pass-through to `self.ts._method(...)`. The entire service layer above is therefore backend-agnostic.

**Backend details:**

- **MySQL** (`proxy/mysql/`): `AsyncMySqlEngine` is a singleton that caches one `AsyncEngine` per database name. Database name is `md_{tenant}_{APP_NAME}`, constructed by `current_md_database_name()` in `db_context.py`. Each tenant gets its own MySQL database.
- **SQLite** (`proxy/sqlite/`): Single file at path from `SQLITE_HOST` env var (default `//db/airembr.sqlite`). `create_database()` just ensures the directory exists.

---

## Layer 6 — SelectResult (`airembr/sdk/storage/metadata/query/select_result.py`)

Every proxy load method returns a `SelectResult` wrapping the raw ORM rows. Mapping from ORM rows to domain models is deferred to the caller:

```python
# Single record
result = await service.load_by_id(id)
if result.exists():
    domain_obj = result.map_to_object(map_to_bridge)

# Multiple records
records = await service.load_all()
objs = list(records.map_to_objects(map_to_bridge))
objs = list(records.map_to_objects(map_to_bridge, filter=lambda r: r.enabled))

# Lightweight list of name/id pairs (no full mapping needed)
entities = records.as_named_entities()
entities = records.as_named_entities(rewriter=lambda r: f"{r.name} ({r.type})")

count = records.count()
```

`map_first_to_object` handles the case where a query may return either a single row or a list (picks the first element from a list).

---

## Layer 7 — DAO functions (`airembr/system/adapter/metadata/mysql/interface/dao/`)

The top-level interface used by application logic. One module per entity type. Each module holds a module-level service instance (e.g. `ess = EventSourceService()`) and exposes plain `async` functions.

The critical pattern: **preconfigured data is checked before the database**. Preconfigured metadata is static JSON loaded at startup into in-memory objects (e.g. `pc_event_sources`). These represent built-in, non-editable records:

```python
async def load_event_source_by_id(source_id) -> Optional[EventSource]:
    # 1. Check preconfig (in-memory, fastest path)
    event_source = pc_event_sources.get_by_id(source_id, EventSource)
    if event_source:
        return event_source

    # 2. Fall back to database
    record = await ess.load_by_id_in_deployment_mode(source_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_event_source)
```

For list queries, preconfig records are prepended to the DB result set. Mutating functions are decorated with `@invalidate_cache_proxy` to bust the Redis query cache.

---

## Bootstrap and preconfig

`mysql_installation.py` → `install_metadata_database()` runs on startup:
1. `DatabaseServiceProxy.bootstrap()` calls `Base.metadata.create_all()` — creates all tables declared in `schema/table.py` that don't yet exist.
2. `BridgeService.bootstrap(os_default_bridges)` inserts the 5 built-in bridge types using `insert_if_none` (idempotent).
3. A default admin user is inserted in the staging context if no users exist.

Built-in defaults are defined in `airembr/system/preconfig/`:
- `setup_bridges.py` — 5 bridge types (REST API, JavaScript, Webhook, Redirect, IMAP)
- `setup_configuration.py` — GitHub and log configuration templates
- `setup_resources.py` — built-in resource type templates

---

## Multi-tenancy and deployment mode summary

Every DB write injects `tenant` from `get_context()` at the mapping layer. Every read filters by the current tenant. The `production` boolean creates two parallel datasets for the same tenant — one for production traffic, one for test/staging. Deployment-mode queries transparently merge both, with test records taking precedence over production records when IDs match.

```
write path:   domain model → map_to_*_table() [injects tenant, production] → upsert to DB
read path:    DB rows → SelectResult → map_to_*() [strips tenant] → domain model
```
