---
name: big-data-query
description: >
  Use this skill whenever the user asks to write, fix, explain, or optimise a
  StarRocks SQL query against the AirEmbR analytics (big-data) layer. Trigger on
  phrases like "write a query to find", "how do I query", "give me a SQL to get",
  "join entities with events", "find entity state", "query observations", "look up
  property values", "analyse events in StarRocks", "build a report from sys_evt",
  or any request that involves the sys_ent*, sys_obs*, sys_evt*, sys_log,
  sys_text, or sys_timer tables. Also trigger when the user asks to explain what a
  big-data table contains, how tables relate to each other, or which table holds a
  particular piece of data.
---

# Big-Data Query Skill

This skill produces StarRocks SQL queries against the AirEmbR analytics layer.
It knows the full schema, the relationships between tables, and the StarRocks
features worth exploiting.

---

## Step 0 — Clarify before writing

Ask (or infer from context):

1. **Goal** — what business question is the user answering?
2. **Scope** — which entity types, time range, observer, source?
3. **Output** — aggregation, raw rows, counts, window stats?
4. **Performance sensitivity** — exploratory one-off or production query?

If the user gives enough context, proceed immediately and note any assumptions.

---

## Schema reference

Before writing any query, read `references/schema.md`. It contains the complete
column list for all 16 tables. Always consult it — do not guess column names or
types.

Key conventions across all tables:
- **`entity_pk`** — `VARCHAR(48)` hash of `entity_type + entity_id`. The stable
  cross-table join key for entities.
- **`entity_iid` / `entity_gid`** — identification id and global id. The `*_type`
  sibling column explains how they were built (email, phone, username, etc.).
- **`data_hash` / `schema_hash`** — content / schema hash for deduplication.
- **`observer_pk`** — who created or last touched the record.
- **`ts`** — insertion timestamp. Use `metadata_time_create` for the business
  event timestamp when available (e.g. in `sys_evt`).
- **`traits`** — JSON blob. Use StarRocks JSON operators to extract fields.

---

## Table selection guide

| Need | Primary table(s) |
|------|-----------------|
| Current entity state (latest traits) | `sys_ent_state` |
| All versions of an entity over time | `sys_ent_history` |
| Simple entity existence / id lookup | `sys_ent` |
| Entity ↔ observation membership | `sys_ent_2_obs` |
| Entity mapped to global id | `sys_ent_2_gid` |
| Current property value per entity | `sys_ent_property_state` |
| Full property history | `sys_ent_property` |
| Observation list | `sys_obs` |
| Which entities were in an observation | `sys_obs_2_entity` |
| Observation hierarchy | `sys_obs_2_obs` |
| Observations linked to a trigger | `sys_obs_trigger` |
| Event stream (actor→object relations) | `sys_evt` |
| Job status for a relation | `sys_evt_job` |
| Semantic text / embeddings | `sys_text` |
| Timers / scheduled events | `sys_timer` |
| Application logs | `sys_log` |

---

## StarRocks-specific patterns

### Partition pruning — always filter on the partition column first

`sys_evt` partitions on `metadata_time_insert`; `sys_obs` partitions on `ts`.
Without a range filter, StarRocks scans all partitions.

```sql
-- Good: partition pruning kicks in
WHERE metadata_time_insert >= '2025-01-01'
  AND metadata_time_insert <  '2026-01-01'

-- Bad: full scan across all monthly partitions
WHERE YEAR(metadata_time_insert) = 2025
```

### BITMAP indexes — push equality / IN filters on indexed columns early

The BITMAP-indexed columns (see schema reference) are cheapest for equality
filters and `IN (...)` clauses. Place them first in the WHERE clause.

Indexed columns include: `rel_label`, `actor_id`, `text_ssid`, `text_sdid` in
`sys_evt`; `entity_pk`, `observer_pk`, `data_hash`, `entity_id` in
`sys_ent_history`; `property_name`, `property_value` in `sys_ent_property_state`.

### JSON extraction

StarRocks uses `->` / `->>` operators and `json_query()` for JSON columns
(`traits` in `sys_ent_state`, `sys_ent_history`, `sys_timer`; `entity_traits`
in `sys_ent_history`).

```sql
-- Extract a string field from JSON
SELECT entity_pk,
       traits->>'$.email'        AS email,
       traits->>'$.first_name'   AS first_name
FROM   sys_ent_state
WHERE  traits->>'$.email' IS NOT NULL;
```

### ARRAY columns

`tags`, `consents_granted`, `metadata_context_entities`, `field_hash` are
`ARRAY` types. Use `array_contains()`, `array_length()`, and `unnest()`.

```sql
-- Events that include a specific consent grant
SELECT id, actor_pk, metadata_time_insert
FROM   sys_evt
WHERE  array_contains(consents_granted, 'gdpr_marketing')
  AND  metadata_time_insert >= '2025-01-01';

-- Expand tags into rows
SELECT id, tag
FROM   sys_evt, unnest(tags) AS t(tag)
WHERE  metadata_time_insert >= '2025-01-01';
```

### Window functions over entity history

```sql
-- Latest record per entity (cheaper than a subquery MAX)
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY entity_pk ORDER BY ts DESC) AS rn
    FROM   sys_ent_history
) t
WHERE rn = 1;
```

### Joining events to current entity state

```sql
SELECT e.id,
       e.metadata_time_insert,
       e.rel_label,
       s.traits->>'$.email' AS actor_email
FROM   sys_evt   e
JOIN   sys_ent_state s ON s.entity_pk = e.actor_pk
WHERE  e.metadata_time_insert >= '2025-01-01'
  AND  e.rel_label = 'purchase';
```

### Counting entities per observation

```sql
SELECT o.id,
       o.label,
       COUNT(DISTINCT oe.entity_pk) AS entity_count
FROM   sys_obs          o
JOIN   sys_obs_2_entity oe ON oe.observation_id = o.id
WHERE  o.ts >= '2025-01-01'
GROUP BY o.id, o.label
ORDER BY entity_count DESC
LIMIT  50;
```

### Property lookup with current state

```sql
SELECT ps.entity_pk,
       ps.property_name,
       ps.property_value,
       ps.property_number
FROM   sys_ent_property_state ps
WHERE  ps.entity_type  = 'Customer'
  AND  ps.property_name = 'lifetime_value'
  AND  ps.property_number > 1000
ORDER BY ps.property_number DESC;
```

---

## Output conventions

- Write complete, runnable SQL — no placeholders like `<table>` unless the user
  must supply a literal value that cannot be inferred.
- Add a brief comment above each major section (`-- filter partition`, `-- join
  to entity state`, etc.) when the query is non-trivial.
- If a query could be slow, note the performance concern and suggest the fix
  (partition filter, index hint, limit on rows scanned).
- Wrap the final SQL in a fenced code block labelled `sql`.
- After the SQL, add a short **Notes** section if there are assumptions,
  limitations, or alternative approaches worth mentioning.

---

## Common mistakes to avoid

- Filtering on derived expressions (`YEAR(ts) = 2025`) instead of range
  predicates — defeats partition pruning.
- Joining `sys_ent` when `sys_ent_state` or `sys_ent_history` is what the user
  actually needs (`sys_ent` has no traits).
- Forgetting that `sys_ent_property_state` is keyed on
  `(observer_pk, entity_pk, entity_type, property_name)` — queries without an
  `observer_pk` filter return one row per observer per property.
- Using `COUNT(*)` on `sys_evt` for deduplication — the table uses `DUPLICATE
  KEY`, so the same event can appear multiple times. Use `COUNT(DISTINCT id)`.
- Extracting JSON with bare `->` without `->>` when you need a string — `->>`
  returns the string value; `->` returns a JSON fragment.
