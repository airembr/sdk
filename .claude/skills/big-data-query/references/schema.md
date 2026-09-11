# StarRocks Schema Reference

Full column listings for all 16 AirEmbR big-data tables.

## Table of Contents

- [sys_ent](#sys_ent)
- [sys_ent_state](#sys_ent_state)
- [sys_ent_history](#sys_ent_history)
- [sys_ent_2_gid](#sys_ent_2_gid)
- [sys_ent_2_obs](#sys_ent_2_obs)
- [sys_ent_property](#sys_ent_property)
- [sys_ent_property_state](#sys_ent_property_state)
- [sys_obs](#sys_obs)
- [sys_obs_2_entity](#sys_obs_2_entity)
- [sys_obs_2_obs](#sys_obs_2_obs)
- [sys_obs_trigger](#sys_obs_trigger)
- [sys_evt](#sys_evt)
- [sys_evt_job](#sys_evt_job)
- [sys_log](#sys_log)
- [sys_text](#sys_text)
- [sys_timer](#sys_timer)

---

## sys_ent

Core entity registry. One row per unique entity (type + id + optional instance id).

**Key:** `PRIMARY KEY(entity_pk)`  **Distribution:** `HASH(entity_pk)` Buckets 10

| Column | Type | Nullable |
|--------|------|----------|
| entity_pk | VARCHAR(48) | NOT NULL |
| entity_type | VARCHAR(64) | NOT NULL |
| entity_id | VARCHAR(48) | NOT NULL |
| entity_iid | VARCHAR(48) | NULL |
| entity_iid_type | VARCHAR(64) | NULL |
| persona | TEXT | NULL |
| ts | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP |

---

## sys_ent_state

Current stitched traits state per entity.

**Key:** `PRIMARY KEY(entity_pk)`  **Distribution:** `HASH(entity_pk)`

**Indexes:** `idx_pk` → entity_pk (BITMAP)

| Column | Type | Nullable |
|--------|------|----------|
| entity_pk | VARCHAR(48) | NOT NULL |
| traits | JSON | NOT NULL |
| stitch_ts | DATETIME | |
| ts | DATETIME | |

---

## sys_ent_history

Immutable version history — one row per unique data_hash per entity.

**Key:** `PRIMARY KEY(entity_hid)`  **Distribution:** `HASH(entity_hid)` Buckets 20

**Indexes:** `idx_observer_pk` (BITMAP), `idx_entity_pk` (BITMAP), `idx_entity_data_hash` (BITMAP), `idx_entity_id` (BITMAP), `idx_entity_traits_text` (NGRAMBF gram=4)

| Column | Type | Nullable |
|--------|------|----------|
| entity_hid | VARCHAR(32) | NOT NULL |
| entity_pk | VARCHAR(48) | NOT NULL |
| data_hash | VARCHAR(32) | NOT NULL |
| entity_classification | VARCHAR(128) | NOT NULL |
| entity_type | VARCHAR(64) | NOT NULL |
| entity_id | VARCHAR(48) | NOT NULL |
| entity_iid | VARCHAR(48) | NULL |
| entity_iid_type | VARCHAR(64) | NULL |
| entity_label | VARCHAR(96) | NULL |
| entity_traits | JSON | NULL |
| entity_traits_text | TEXT | NULL |
| schema_hash | VARCHAR(32) | NOT NULL |
| field_hash | ARRAY\<VARCHAR(32)\> | NULL |
| observation_id | VARCHAR(48) | NOT NULL |
| observer_pk | VARCHAR(32) | NOT NULL |
| rel_type | VARCHAR(64) | NULL |
| rel_label | VARCHAR(64) | NULL |
| session_id | VARCHAR(48) | NULL |
| context | VARCHAR(16) | NOT NULL |
| consents_granted | ARRAY\<VARCHAR(48)\> | NULL |
| ts | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP |
| time_create | DATETIME | NULL |
| time_merge | DATETIME | NULL |

---

## sys_ent_2_gid

Maps entity_pk → global identifier (gid).

**Key:** `PRIMARY KEY(entity_pk)`  **Distribution:** `HASH(entity_pk)`

**Indexes:** `idx_pk` (entity_pk, BITMAP), `idx_gid` (entity_gid, BITMAP)

| Column | Type | Nullable |
|--------|------|----------|
| entity_pk | VARCHAR(48) | NOT NULL |
| entity_gid | VARCHAR(48) | NOT NULL |
| entity_type | VARCHAR(64) | NOT NULL |
| entity_gid_type | VARCHAR(64) | NULL |
| ts | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP |

---

## sys_ent_2_obs

Junction table: entity ↔ observation membership.

**Key:** `PRIMARY KEY(entity_pk, observation_id)`  **Distribution:** `HASH(entity_pk, observation_id)` Buckets 5

**Indexes:** `idx_id` (observation_id, BITMAP), `idx_entity_pk` (entity_pk, BITMAP)

| Column | Type | Nullable |
|--------|------|----------|
| entity_pk | VARCHAR(48) | NOT NULL |
| observation_id | VARCHAR(64) | NOT NULL |
| entity_type | VARCHAR(48) | NOT NULL |

---

## sys_ent_property

All observed name-value property records per entity (full history).

**Key:** `PRIMARY KEY(property_id)`  **Distribution:** `HASH(property_id)`

**Indexes:** `idx_observer_pk`, `idx_pk` (entity_pk), `idx_content_type` (entity_type), `idx_property_id`, `idx_property_name`, `idx_property_value` — all BITMAP

| Column | Type | Nullable |
|--------|------|----------|
| property_id | VARCHAR(32) | NOT NULL |
| observer_pk | VARCHAR(32) | NOT NULL |
| entity_pk | VARCHAR(48) | NOT NULL |
| entity_type | VARCHAR(64) | NOT NULL |
| property_name | VARCHAR(64) | NOT NULL |
| property_value | STRING | NOT NULL |
| property_text | STRING | NULL |
| property_number | DECIMAL(20,10) | NULL |
| entity_id | VARCHAR(48) | NOT NULL |
| count | INT | |
| ts | DATETIME | |

---

## sys_ent_property_state

Current property state per observer — latest value, text, number and embedding vector.

**Key:** `PRIMARY KEY(observer_pk, entity_pk, entity_type, property_name)`
**Distribution:** `HASH(observer_pk, entity_pk, entity_type, property_name)`

**Indexes:** `idx_observer_pk`, `idx_pk` (entity_pk), `idx_content_type` (entity_type), `idx_property_name`, `idx_property_value` — all BITMAP

| Column | Type | Nullable |
|--------|------|----------|
| observer_pk | VARCHAR(32) | NOT NULL |
| entity_pk | VARCHAR(48) | NOT NULL |
| entity_type | VARCHAR(64) | NOT NULL |
| property_name | VARCHAR(64) | NOT NULL |
| property_value | STRING | NOT NULL |
| property_text | STRING | NULL |
| property_number | DECIMAL(20,10) | NULL |
| ts | DATETIME | |
| property_vector | ARRAY\<FLOAT\> | NULL |

---

## sys_obs

Observation records. Partitioned by month (24-month rolling window).

**Key:** `DUPLICATE KEY(id)`  **Distribution:** `HASH(id)` Buckets 10
**Partition:** `RANGE(ts)` dynamic monthly

**Indexes:** `idx_source` (source_id, BITMAP), `idx_session` (session_id, BITMAP), `idx_label` (label, BITMAP)

| Column | Type | Nullable |
|--------|------|----------|
| id | VARCHAR(64) | NOT NULL |
| source_id | VARCHAR(64) | NOT NULL |
| session_id | VARCHAR(64) | NULL |
| label | VARCHAR(64) | NULL |
| description | TEXT | NULL |
| entities | INTEGER | NULL DEFAULT 0 |
| metadata_time_insert | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| metadata_time_create | DATETIME | NULL |
| ts | DATETIME | DEFAULT CURRENT_TIMESTAMP |

---

## sys_obs_2_entity

Maps observations to the entity data snapshots captured during each observation.

**Key:** `PRIMARY KEY(observation_id, entity_id, entity_data_hash)`
**Distribution:** `HASH(observation_id, entity_id, entity_data_hash)` Buckets 5

**Indexes:** `idx_id` (observation_id, BITMAP), `idx_entity_type` (entity_type, BITMAP)

| Column | Type | Nullable |
|--------|------|----------|
| observation_id | VARCHAR(64) | NOT NULL |
| entity_id | VARCHAR(48) | NOT NULL |
| entity_data_hash | VARCHAR(32) | NOT NULL |
| entity_pk | VARCHAR(48) | NOT NULL |
| session_id | VARCHAR(48) | NULL |
| entity_type | VARCHAR(64) | NOT NULL |

---

## sys_obs_2_obs

Directed relationships between observations (e.g. parent/child, before/after).

**Key:** `PRIMARY KEY(observation_start_id, observation_end_id)`
**Distribution:** `HASH(observation_start_id, observation_end_id)` Buckets 5

**Indexes:** `idx_start`, `idx_end`, `idx_type` — all BITMAP

| Column | Type | Nullable |
|--------|------|----------|
| observation_start_id | VARCHAR(64) | NOT NULL |
| observation_end_id | VARCHAR(64) | NOT NULL |
| type | VARCHAR(64) | NOT NULL |
| abstraction | INTEGER | NOT NULL |

---

## sys_obs_trigger

Associates observations with the triggers that fired them.

**Key:** `PRIMARY KEY(obs_id, trigger_id)`  **Distribution:** `HASH(obs_id, trigger_id)`

| Column | Type | Nullable |
|--------|------|----------|
| obs_id | VARCHAR(64) | NOT NULL |
| trigger_id | VARCHAR(64) | NOT NULL |
| ts_end | DATETIME | |

---

## sys_evt

Main event table — actor→object relationship events with full context.
Partitioned by month (24-month rolling window).

**Key:** `DUPLICATE KEY(actor_pk, actor_data_hash)`
**Distribution:** `HASH(actor_pk, actor_data_hash)` Buckets 10
**Partition:** `RANGE(metadata_time_insert)` dynamic monthly

**Indexes:** `idx_name` (rel_label, BITMAP), `idx_actor_id` (actor_id, BITMAP), `idx_ssid` (text_ssid, BITMAP), `idx_sdid` (text_sdid, BITMAP)

| Column | Type | Nullable |
|--------|------|----------|
| actor_pk | VARCHAR(64) | NULL |
| actor_data_hash | VARCHAR(32) | NULL |
| actor_type | VARCHAR(64) | NULL |
| actor_id | VARCHAR(64) | NULL |
| actor_hid | VARCHAR(32) | NOT NULL |
| actor_iid | VARCHAR(64) | NULL |
| actor_iid_type | VARCHAR(64) | NULL |
| actor_schema_hash | VARCHAR(32) | NULL |
| actor_role | VARCHAR(32) | NULL |
| actor_label | VARCHAR(60) | NULL |
| actor_is_a_id | VARCHAR(40) | NULL |
| actor_is_a_kind | VARCHAR(64) | NULL |
| actor_part_of_kind | VARCHAR(64) | NULL |
| actor_part_of_id | VARCHAR(40) | NULL |
| observer_id | VARCHAR(64) | NULL |
| observer_pk | VARCHAR(64) | NULL |
| observer_type | VARCHAR(64) | NULL |
| observer_role | VARCHAR(32) | NULL |
| observer_data_hash | VARCHAR(32) | NULL |
| observer_schema_hash | VARCHAR(32) | NULL |
| object_type | VARCHAR(64) | NULL |
| object_id | VARCHAR(64) | NULL |
| object_hid | VARCHAR(32) | NULL |
| object_iid | VARCHAR(64) | NULL |
| object_iid_type | VARCHAR(64) | NULL |
| object_pk | VARCHAR(64) | NULL |
| object_role | VARCHAR(64) | NULL |
| object_label | VARCHAR(60) | NULL |
| object_is_a_id | VARCHAR(40) | NULL |
| object_is_a_kind | VARCHAR(64) | NULL |
| object_part_of_kind | VARCHAR(64) | NULL |
| object_part_of_id | VARCHAR(40) | NULL |
| object_data_hash | VARCHAR(32) | NULL |
| object_schema_hash | VARCHAR(32) | NULL |
| rel_label | VARCHAR(64) | NULL |
| rel_type | VARCHAR(64) | NULL |
| rel_id | VARCHAR(64) | NULL |
| rel_tid | VARCHAR(64) | NULL |
| rel_hid | VARCHAR(32) | NOT NULL |
| rel_pk | VARCHAR(64) | NULL |
| rel_data_hash | VARCHAR(32) | NULL |
| rel_schema_hash | VARCHAR(32) | NULL |
| id | VARCHAR(48) | NOT NULL |
| source_id | VARCHAR(64) | NOT NULL |
| obs_id | VARCHAR(64) | NOT NULL |
| obs_label | VARCHAR(64) | NOT NULL |
| session_id | VARCHAR(64) | NULL |
| text_sdid | VARCHAR(32) | NULL |
| text_ssid | VARCHAR(32) | NULL |
| semantic_summary | TEXT | NULL |
| semantic_description | TEXT | NULL |
| subjective | BOOLEAN | NOT NULL DEFAULT '1' |
| tags | ARRAY\<VARCHAR(32)\> | NULL |
| metadata_time_insert | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP |
| metadata_time_create | DATETIME | NULL |
| metadata_time_due | DATETIME | NULL |
| metadata_time_expire | DATETIME | NULL |
| metadata_order | BIGINT | NULL |
| metadata_valid | BOOLEAN | NULL |
| metadata_warning | BOOLEAN | NULL |
| metadata_error | BOOLEAN | NULL |
| metadata_context_count | INTEGER | NULL DEFAULT 0 |
| metadata_context_entities | ARRAY\<VARCHAR(64)\> | NULL |
| consents_granted | ARRAY\<VARCHAR(48)\> | NULL |
| sys_timer_id | VARCHAR(64) | NULL |
| sys_timer_status | INTEGER | NULL |

---

## sys_evt_job

Background job execution status linked to event relations.

**Key:** `PRIMARY KEY(rel_id, job_id)`  **Distribution:** `HASH(rel_id, job_id)`
**Order:** `ORDER BY(ts)`

| Column | Type | Nullable |
|--------|------|----------|
| rel_id | VARCHAR(48) | NOT NULL |
| job_id | VARCHAR(48) | NOT NULL |
| ts | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| job_name | VARCHAR(48) | |
| job_status | VARCHAR(48) | |

---

## sys_log

Application log records with contextual tracing fields.

**Key:** `PRIMARY KEY(id)`  **Distribution:** `HASH(id)`
**Order:** `ORDER BY(date)`

| Column | Type | Nullable |
|--------|------|----------|
| id | VARCHAR(48) | NOT NULL |
| date | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| message | VARCHAR(4092) | |
| logger | VARCHAR(128) | |
| file | VARCHAR(255) | |
| line | INT | NULL |
| level | VARCHAR(48) | |
| exc_info | VARCHAR(10000) | |
| stack_info | VARCHAR(10000) | |
| user_id | VARCHAR(40) | |
| event_id | VARCHAR(40) | |
| entity_name | VARCHAR(64) | |
| entity_id | VARCHAR(40) | |
| flow_id | VARCHAR(40) | |
| node_id | VARCHAR(40) | |
| origin | VARCHAR(40) | |
| class_name | VARCHAR(255) | |
| module | TEXT | |
| error_number | VARCHAR(10) | |

---

## sys_text

Semantic text storage with embedding vectors and NER flags.

**Key:** `PRIMARY KEY(id)`  **Distribution:** `HASH(id)`
**Order:** `ORDER BY(ts)`

| Column | Type | Nullable |
|--------|------|----------|
| id | VARCHAR(32) | NOT NULL |
| parent_id | VARCHAR(32) | NULL |
| observation_id | VARCHAR(64) | NOT NULL |
| source_id | VARCHAR(64) | NOT NULL |
| rel_label | VARCHAR(64) | NULL |
| rel_type | VARCHAR(64) | NULL |
| description | TEXT | NOT NULL |
| origin | VARCHAR(24) | NOT NULL |
| tags | ARRAY\<VARCHAR(64)\> | NULL |
| model | VARCHAR(64) | NULL |
| vector | ARRAY\<FLOAT\> | NULL |
| require_ner | BOOLEAN | DEFAULT '0' |
| ts | DATETIME | DEFAULT CURRENT_TIMESTAMP |

---

## sys_timer

Scheduled timer records with actor/object/traits context.

**Key:** `PRIMARY KEY(id)`  **Distribution:** `HASH(id)`

| Column | Type | Nullable |
|--------|------|----------|
| id | VARCHAR(40) | NOT NULL |
| status | INT | |
| ts | DATETIME | |
| timeout | INTEGER | |
| event | VARCHAR(32) | |
| obs_id | VARCHAR(128) | |
| obs_label | VARCHAR(32) | |
| source_id | VARCHAR(40) | |
| actor_id | VARCHAR(40) | |
| actor_role | VARCHAR(32) | |
| actor_type | VARCHAR(32) | |
| actor_data_hash | VARCHAR(32) | |
| object_id | VARCHAR(40) | |
| object_type | VARCHAR(32) | |
| object_role | VARCHAR(32) | |
| object_data_hash | VARCHAR(32) | |
| traits | JSON | |
