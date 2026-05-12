DROP VIEW IF EXISTS {|database|}.sys_v_ent_state;

CREATE VIEW {|database|}.sys_v_ent_state AS (
SELECT s.entity_pk, MAX(s.ts), s.entity_type, MAP_AGG(s.property_name, s.property_value) AS traits
FROM {|database|}.sys_ent_property_state s
GROUP BY s.entity_pk, s.entity_type
)