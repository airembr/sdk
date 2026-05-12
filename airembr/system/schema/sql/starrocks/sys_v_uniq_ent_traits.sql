CREATE VIEW IF NOT EXISTS {|database|}.sys_v_uniq_ent_traits AS
WITH hashes as (
    SELECT "actor" AS type, sys_evt.rel_label, actor_schema_hash AS schema_hash, ANY_VALUE(actor_data_hash) AS data_hash
         FROM {|database|}.sys_evt
         WHERE actor_data_hash IS NOT NULL
         GROUP BY actor_schema_hash, sys_evt.rel_label

    UNION ALL

    SELECT "object" AS type, sys_evt.rel_label,object_schema_hash AS schema_hash, ANY_VALUE(object_data_hash) AS data_hash
         FROM {|database|}.sys_evt
         WHERE object_data_hash IS NOT NULL
         GROUP BY object_schema_hash, sys_evt.rel_label

    UNION ALL

    SELECT "rel" AS type, sys_evt.rel_label, rel_schema_hash AS schema_hash, ANY_VALUE(rel_data_hash) AS data_hash
         FROM {|database|}.sys_evt
         WHERE rel_data_hash IS NOT NULL
         GROUP BY rel_schema_hash, sys_evt.rel_label
    )

    SELECT hashes.type, hashes.rel_label, hashes.schema_hash, ANY_VALUE(history.entity_traits) AS traits FROM hashes
    JOIN sys_ent_history AS history ON hashes.data_hash = history.data_hash
    GROUP BY hashes.schema_hash, hashes.rel_label, hashes.type;