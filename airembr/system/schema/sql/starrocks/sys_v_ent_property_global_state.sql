DROP VIEW IF EXISTS {|database|}.sys_v_ent_property_global_state;

CREATE VIEW {|database|}.sys_v_ent_property_global_state
AS
    SELECT COALESCE(gid.entity_gid, s.entity_pk) AS entity_iid,
           gid.ts AS iid_ts,
           gid.entity_gid_type,
           s.*
    FROM {|database|}.sys_ent_property_state s
    LEFT JOIN {|database|}.sys_ent_2_gid gid ON s.entity_pk = gid.entity_pk;