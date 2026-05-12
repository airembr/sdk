CREATE VIEW IF NOT EXISTS {|database|}.sys_v_evt_ent AS
    SELECT fact.id,
           fact.metadata_time_create,
           fact.metadata_time_insert,
           fact.tags,
           fact.subjective,
           -- Observation
           fact.obs_id,
           fact.obs_label,
           -- Source
           fact.source_id,
           -- Observer
           fact.observer_id,
           fact.observer_pk,
           fact.observer_type,
           fact.observer_role,
           -- Actor
           fact.actor_id,
           fact.actor_pk,
           fact.actor_iid,
           fact.actor_type,
           fact.actor_role,
           actor_state.ts as actor_state_ts,
           actor_state.traits as actor_traits,
           -- Relation
           fact.rel_id,
           fact.rel_pk,
           fact.rel_type,
           fact.rel_label,
           -- Object
           fact.object_id,
           fact.object_pk,
           fact.object_iid,
           fact.object_type,
           fact.object_role,
           object_state.ts as object_state_ts,
           object_state.traits as object_traits,
           -- Semantic
           fact.semantic_summary,
           fact.semantic_description,
           -- Context
           fact.metadata_context_entities
    FROM {|database|}.sys_evt fact
    LEFT JOIN {|database|}.sys_ent_state actor_state ON fact.actor_pk=actor_state.entity_pk
    LEFT JOIN {|database|}.sys_ent_state object_state ON fact.object_pk=object_state.entity_pk;