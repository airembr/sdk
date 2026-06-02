from datetime import datetime

from typing import Dict, List, Optional, Tuple

from srd.domain.sql import Sql, Param

from airembr.model.system.meta_language.meta_lang_model import MetaLangEntityBase
from airembr.model.bigdata.flat_ent_property_state import FlatEntityPropertyState
from airembr.model.bigdata.flat_obs import FlatObs
from airembr.model.bigdata.flat_text_vector import FlatTextVector
from airembr.system.adapter.bigdata.general.utils.mapping import (
    sys_ent_2_obs, sys_ent_property_state, sys_ent_state,
    entity_property, sys_obs_mapping, sys_text_vector_mapping,
)
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name

# (entity_type, property_name, value) → embedding vector
EmbeddingMap = Dict[Tuple[str, str, str], List[float]]

DEFAULT_MAX_VECTOR_DISTANCE: float = 0.3


def build_last_property_values(view: str):
    database = current_bd_database_name()
    sys_ent_property_state_map = sys_ent_property_state()
    value_id_col = sys_ent_property_state_map | FlatEntityPropertyState.VALUE_ID
    return (
            Sql()
            + f"{view} AS ("
            + f"SELECT "
            + f"{sys_ent_property_state_map | FlatEntityPropertyState.ENTITY_PK}, "
            + f"  entity_type, property_name, MAX_BY(property_value, ts) AS property_value,"
            + f"  MAX_BY({value_id_col}, ts) AS property_value_id"
            + f"FROM {database}.{sys_ent_property_state_map}"
            + "GROUP BY entity_pk, entity_type, property_name)"
    )


def build_last_property_values_by_date(view: str,
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None):
    database = current_bd_database_name()
    sys_ent_property_map = entity_property()

    def between(start_date, end_date):
        if start_date and end_date:
            return f"WHERE ts BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'"
        elif start_date:
            return f"WHERE ts >= '{start_date.isoformat()}'"
        elif end_date:
            return f"WHERE ts <= '{end_date.isoformat()}'"
        else:
            return ""

    value_id_col = sys_ent_property_map | FlatEntityPropertyState.VALUE_ID
    return (
            Sql()
            + f"{view} AS ("
            + f"SELECT "
            + f"{sys_ent_property_map | FlatEntityPropertyState.ENTITY_PK}, "
            + f"  entity_type, property_name, MAX_BY(property_value, ts) AS property_value,"
            + f"  MAX_BY({value_id_col}, ts) AS property_value_id"
            + f"FROM {database}.{sys_ent_property_map}"
            + between(start_date, end_date)
            + "GROUP BY entity_pk, entity_type, property_name)"

    )


def _has_exact_props(entities: List[MetaLangEntityBase]) -> bool:
    return any(p.assign != "~" for e in entities for p in (e.properties or []))


def _has_vector_props(entities: List[MetaLangEntityBase]) -> bool:
    return any(p.assign == "~" for e in entities for p in (e.properties or []))


def build_conditions_sql(
    entities: List[MetaLangEntityBase],
    name: str = "conditions",
    entity_prefix: int = 1,
    skip_vector: bool = False,
) -> Optional[Sql]:
    """Build an exact-match conditions CTE.

    When ``skip_vector=True`` properties with assign "~" are omitted (they are
    handled by the vector CTEs instead).  Returns ``None`` when nothing would
    be emitted, so callers can guard with ``if result:``.
    """
    sql_parts = []
    params = {}

    property_idx = 0
    entity_start_idx = 0
    for entity in entities:
        entity_start_idx += 1

        group_id = f"{entity_prefix}.{entity_start_idx}"

        if not entity.properties:
            type_param = f"{entity_start_idx}_type"
            if not sql_parts:
                sql = f"SELECT {group_id} AS group_id, :{type_param} AS entity_type"
            else:
                sql = f"UNION ALL SELECT {group_id} AS group_id, :{type_param} AS entity_type"

            sql_parts.append(sql)
            params[type_param] = entity.type
            continue

        for prop in (entity.properties or []):
            if skip_vector and prop.assign == "~":
                continue

            prop_name, prop_value = prop.name, prop.value
            property_idx += 1
            group_ref = f"{entity_start_idx}_{property_idx}"

            type_param = f"{group_ref}_type"
            prop_param = f"{group_ref}_prop"
            value_param = f"{group_ref}_value"

            if not sql_parts:
                sql = (
                    f"SELECT {group_id} AS group_id, "
                    f":{type_param} AS entity_type, "
                    f":{prop_param} AS property_name, "
                    f":{value_param} AS property_value"
                )
            else:
                sql = (
                    f"UNION ALL SELECT {group_id} AS group_id, "
                    f":{type_param}, "
                    f":{prop_param}, "
                    f":{value_param}"
                )

            sql_parts.append(sql)
            params[type_param] = entity.type
            params[prop_param] = prop_name
            params[value_param] = prop_value

    if not sql_parts:
        return None

    sql = f"{name} AS (\n    " + "\n    ".join(sql_parts) + "\n) \n\n"
    return Sql(sql) + Param(params)


#
# def build_entities_cte(entities: List[MetaLangEntityBase], unmatched_entities: int = 0, unmatched_traits: int = 0):
#     database = current_bd_database_name()
#     sys_ent_property_state_map = sys_ent_property_state()
#     sys_ent_2_obs_map = sys_ent_2_obs()
#
#     entity_filter = {entity.type for entity in entities}
#
#     no_of_props = sum(len(entity.properties) for entity in entities)
#     no_of_entities = max(0, len(entity_filter) - unmatched_entities)
#     no_of_traits = max(0, no_of_props - unmatched_traits)
#     no_property_join_entities = {entity.type for entity in entities if not entity.properties}
#
#     sql = (
#             Sql()
#             + "entities AS ( "
#             + "SELECT "
#             + "  o.observation_id, "
#             + "  COUNT(DISTINCT c.group_id) AS no_of_entities,"
#             + "  COUNT(o.observation_id) AS no_of_matched_props,"
#             + "  GROUP_CONCAT(DISTINCT o.entity_pk) AS entity_pks"
#             + f"FROM {database}.{sys_ent_property_state_map} p "
#             + f"JOIN {database}.{sys_ent_2_obs_map} o "
#             + "  ON p.entity_pk = o.entity_pk "
#             + "LEFT JOIN conditions c "
#             + "  ON (p.entity_type = c.entity_type AND p.property_name = c.property_name AND p.property_value = c.property_value)"
#             + (bool(no_property_join_entities), f"OR p.entity_type IN :no_prop_join",
#                Param({"no_prop_join": tuple(no_property_join_entities)}))
#             + f"WHERE c.group_id IS NOT NULL AND p.entity_type IN :entity_filter" + Param(
#         {"entity_filter": tuple(entity_filter)})
#             + "GROUP BY o.observation_id"
#             + f"HAVING no_of_entities >= {no_of_entities} AND no_of_matched_props >= {no_of_traits}"
#             + f"ORDER BY no_of_matched_props DESC"
#             + ")\n"
#     )
#
#     return sql


def build_entities_with_traits_cte(
    view: str,
    entities: List[MetaLangEntityBase],
    entity_prefix: int = 1,
    embeddings: Optional[EmbeddingMap] = None,
    max_distance: float = DEFAULT_MAX_VECTOR_DISTANCE,
) -> Sql:
    """Build the entities_with_traits CTE (and helper CTEs when using vector search).

    When ``embeddings`` is ``None`` the original single-CTE behaviour is
    preserved (backward compat).  When ``embeddings`` is provided, ``~``
    properties are matched by ANN similarity against ``sys_text_vector`` and
    ``=``/``:`` properties are matched by exact value; both are unioned into
    ``entities_with_traits``.
    """
    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()

    # --- Backward compat: no embeddings → single exact-match CTE (unchanged) ---
    if embeddings is None:
        entity_filter = {entity.type for entity in entities if entity.properties}
        return (
            Sql()
            + "entities_with_traits AS ( "
            + "SELECT "
            + "  p.property_name, p.property_value, o.*, c.group_id "
            + f"FROM {view} p "
            + f"JOIN {database}.{sys_ent_2_obs_map} o "
            + "  ON p.entity_pk = o.entity_pk "
            + "LEFT JOIN traits_conditions c "
            + "  ON (LOWER(p.entity_type) = LOWER(c.entity_type) AND p.property_name = c.property_name AND LOWER(p.property_value) = LOWER(c.property_value))"
            + f"WHERE c.group_id IS NOT NULL AND p.entity_type IN :traits_filter"
            + Param({"traits_filter": tuple(entity_filter)})
            + ")\n"
        )

    # --- With embeddings: build exact + vector CTEs, union into entities_with_traits ---
    sys_tv_map = sys_text_vector_mapping()
    tv_text_id = sys_tv_map | FlatTextVector.TEXT_ID
    tv_vector = sys_tv_map | FlatTextVector.VECTOR

    cte_strings: List[str] = []
    params: Dict = {}

    has_exact = _has_exact_props(entities)

    # Exact match CTE (references traits_conditions built by build_conditions_sql)
    if has_exact:
        exact_filter = tuple({
            entity.type for entity in entities
            if any(p.assign != "~" for p in (entity.properties or []))
        })
        params["exact_traits_filter"] = exact_filter
        cte_strings.append(
            "entities_with_exact_traits AS ("
            "SELECT p.property_name, p.property_value, o.*, c.group_id "
            f"FROM {view} p "
            f"JOIN {database}.{sys_ent_2_obs_map} o ON p.entity_pk = o.entity_pk "
            "LEFT JOIN traits_conditions c "
            "ON (LOWER(p.entity_type) = LOWER(c.entity_type) "
            "AND p.property_name = c.property_name "
            "AND LOWER(p.property_value) = LOWER(c.property_value)) "
            "WHERE c.group_id IS NOT NULL AND p.entity_type IN :exact_traits_filter)"
        )

    # Vector top-k CTEs — one per ~ property with a known embedding
    top_k_parts: List[Tuple[str, str, str, str]] = []  # (cte_name, entity_type, prop_name, group_id)

    entity_start_idx = 0
    for entity in entities:
        entity_start_idx += 1
        group_id = f"{entity_prefix}.{entity_start_idx}"
        local_prop_idx = 0

        for prop in (entity.properties or []):
            if prop.assign != "~":
                continue
            local_prop_idx += 1

            vector = embeddings.get((entity.type, prop.name, prop.value))
            if vector is None:
                continue

            cte_name = f"vector_top_k_{entity_prefix}_{entity_start_idx}_{local_prop_idx}"
            vector_str = f"[{', '.join(str(float(v)) for v in vector)}]"
            dist_expr = f"approx_l2_distance(sv.{tv_vector}, {vector_str})"

            cte_strings.append(
                f"{cte_name} AS ("
                f"SELECT p.entity_pk "
                f"FROM {view} p "
                f"JOIN {database}.{sys_tv_map} sv ON p.property_value_id = sv.{tv_text_id} "
                f"WHERE LOWER(p.entity_type) = LOWER('{entity.type}') "
                f"AND p.property_name = '{prop.name}' "
                f"AND {dist_expr} <= {max_distance})"
            )
            top_k_parts.append((cte_name, entity.type, prop.name, group_id))

    if top_k_parts:
        union_selects = []
        for cte_name, entity_type, prop_name, group_id in top_k_parts:
            union_selects.append(
                f"SELECT p.property_name, p.property_value, o.*, '{group_id}' AS group_id "
                f"FROM {cte_name} t "
                f"JOIN {view} p ON t.entity_pk = p.entity_pk "
                f"AND LOWER(p.entity_type) = LOWER('{entity_type}') AND p.property_name = '{prop_name}' "
                f"JOIN {database}.{sys_ent_2_obs_map} o ON t.entity_pk = o.entity_pk"
            )
        cte_strings.append(
            "entities_with_vector_traits AS (" + " UNION ALL ".join(union_selects) + ")"
        )

    # Final union CTE
    if has_exact and top_k_parts:
        cte_strings.append(
            "entities_with_traits AS ("
            "SELECT * FROM entities_with_exact_traits UNION ALL SELECT * FROM entities_with_vector_traits)"
        )
    elif has_exact:
        cte_strings.append("entities_with_traits AS (SELECT * FROM entities_with_exact_traits)")
    else:
        cte_strings.append("entities_with_traits AS (SELECT * FROM entities_with_vector_traits)")

    return Sql(",\n".join(cte_strings)) + Param(params)


def build_entities_without_traits_cte(view: str, entities: List[MetaLangEntityBase]):
    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()

    entity_filter = {entity.type for entity in entities if not entity.properties}

    sql = (
            Sql()
            + "entities_without_traits AS ( "
            + "SELECT "
            + "  NULL AS property_name, NULL AS property_value, o.*, c.group_id "
            + f"FROM {view} p "
            + f"JOIN {database}.{sys_ent_2_obs_map} o "
            + "  ON p.entity_pk = o.entity_pk "
            + "LEFT JOIN entity_conditions c "
            + "  ON p.entity_type = c.entity_type"
            + f"WHERE c.group_id IS NOT NULL AND p.entity_type IN :entity_filter" + Param(
        {"entity_filter": tuple(entity_filter)})
            + ")\n"
    )

    return sql


def build_joined_entities_cte():
    return Sql("entities AS (SELECT * FROM entities_with_traits UNION ALL SELECT * FROM entities_without_traits)")


def build_traits_entities_cte():
    return Sql("entities AS (SELECT * FROM entities_with_traits)")


def build_no_traits_entities_cte():
    return Sql("entities AS (SELECT * FROM entities_without_traits)")


def build_sub_select_entities_cte(must_match_entities, must_matched_traits):
    return (
            Sql("matching_entities AS (")
            + "SELECT observation_id,"
            + "       COUNT(DISTINCT group_id) AS no_of_entities,"
            + "       COUNT(observation_id)    AS no_of_matched_props"
            + f"  FROM entities"
            + "  GROUP BY observation_id, entity_pk"
            + f" HAVING no_of_entities >= {must_match_entities} AND no_of_matched_props >= {must_matched_traits}"
            + ")"
    )


def build_select_observation_will_all_entities(entities: List[MetaLangEntityBase],
                                               unmatched_entities: int = 0,
                                               unmatched_traits: int = 0,
                                               start_date: Optional[datetime] = None,
                                               end_date: Optional[datetime] = None,
                                               embeddings: Optional[EmbeddingMap] = None):
    entities_with_traits = [item for item in entities if item.properties]
    entities_without_traits = [item for item in entities if not item.properties]

    entity_filter = [entity.type for entity in entities]

    # Tolerance
    no_of_query_props = sum(len(entity.properties) for entity in entities)
    no_of_query_entities = len(entity_filter)
    no_of_entities = max(0, no_of_query_entities - unmatched_entities)
    no_of_traits = max(0, no_of_query_props - unmatched_traits)

    _skip_vec = embeddings is not None
    _cond1 = build_conditions_sql(entities_with_traits, "traits_conditions", 1, skip_vector=_skip_vec)
    sql1 = (_cond1 + ",") if _cond1 else None
    sql2 = build_conditions_sql(entities_without_traits, "entity_conditions", 2) + "," if entities_without_traits else None

    if start_date or end_date:
        sql6 = build_last_property_values_by_date("last_property_values", start_date, end_date) + ","
    else:
        sql6 = build_last_property_values("last_property_values") + ","
    sql3 = (
        build_entities_with_traits_cte(
            "last_property_values", entities_with_traits,
            entity_prefix=1, embeddings=embeddings,
        ) + ","
    ) if entities_with_traits else None
    sql4 = build_entities_without_traits_cte("last_property_values",
                                             entities_without_traits) + "," if entities_without_traits else None
    if entities_with_traits and entities_without_traits:
        sql5 = build_joined_entities_cte()
    elif entities_with_traits:
        sql5 = build_traits_entities_cte()
    elif entities_without_traits:
        sql5 = build_no_traits_entities_cte()
    else:
        raise ValueError("entities_with_traits and entities_without_traits cannot be both empty")

    sql = (
            Sql("WITH ")
            + sql1
            + sql2
            + sql6
            + sql3
            + sql4
            + sql5
            + "SELECT "
            + "  observation_id, "
            + "  COUNT(DISTINCT group_id) AS no_of_entities,"
            + "  COUNT(observation_id) AS no_of_matched_props,"
            + "  GROUP_CONCAT(DISTINCT entity_pk) AS entity_pks"
            + f"FROM entities "
            + "GROUP BY observation_id, entity_pk"
            + f"HAVING no_of_entities >= {no_of_entities} AND no_of_matched_props >= {no_of_traits}"
            + f"ORDER BY no_of_matched_props DESC"
    )

    print(400, sql.literal())
    return sql


def build_select_observations_with_eql(entities: List[MetaLangEntityBase],
                                       unmatched_entities: int = 0,
                                       unmatched_traits: int = 0,
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None,
                                       embeddings: Optional[EmbeddingMap] = None):
    entities_with_traits = [item for item in entities if item.properties]
    entities_without_traits = [item for item in entities if not item.properties]

    entity_filter = [entity.type for entity in entities]

    # Tolerance
    no_of_query_props = sum(len(entity.properties) for entity in entities)
    no_of_query_entities = len(entity_filter)
    no_of_traits = max(0, no_of_query_props - unmatched_traits)
    no_of_entities = max(0, no_of_query_entities - unmatched_entities)

    _skip_vec = embeddings is not None
    _cond1 = build_conditions_sql(entities_with_traits, "traits_conditions", 1, skip_vector=_skip_vec)
    sql1 = (_cond1 + ",") if _cond1 else None
    sql2 = build_conditions_sql(entities_without_traits, "entity_conditions",
                                2) + "," if entities_without_traits else None
    if start_date or end_date:
        sql6 = build_last_property_values_by_date("last_property_values", start_date, end_date) + ","
    else:
        sql6 = build_last_property_values("last_property_values") + ","
    sql3 = (
        build_entities_with_traits_cte(
            "last_property_values", entities_with_traits,
            entity_prefix=1, embeddings=embeddings,
        ) + ","
    ) if entities_with_traits else None
    sql4 = build_entities_without_traits_cte("last_property_values",
                                             entities_without_traits) + "," if entities_without_traits else None
    if entities_with_traits and entities_without_traits:
        sql5 = build_joined_entities_cte()
    elif entities_with_traits:
        sql5 = build_traits_entities_cte()
    elif entities_without_traits:
        sql5 = build_no_traits_entities_cte()
    else:
        raise ValueError("entities_with_traits and entities_without_traits cannot be both empty")

    sql7 = build_sub_select_entities_cte(must_match_entities=no_of_entities,
                                         must_matched_traits=no_of_traits)

    database = current_bd_database_name()
    sys_obs = sys_obs_mapping()

    sql = (
            Sql("WITH ")
            + sql1
            + sql2
            + sql6
            + sql3
            + sql4
            + sql5 + ","
            + sql7
            + "SELECT"
            + f"  o.{sys_obs | FlatObs.ID},"
            + f"  o.{sys_obs | FlatObs.METADATA_TIME_INSERT},"
            + f"  o.{sys_obs | FlatObs.METADATA_TIME_CREATE},"
            + f"  o.{sys_obs | FlatObs.SUMMARY} AS summary, "
            + f"  o.{sys_obs | FlatObs.DESCRIPTION} AS description,"
            + f"  o.{sys_obs | FlatObs.ENTITIES},"
            + f"  matched.no_of_entities, matched.no_of_matched_props"
            + "FROM matching_entities AS matched"
            + f"JOIN {database}.{sys_obs} AS o ON o.{sys_obs | FlatObs.ID} = matched.observation_id"
            + "ORDER BY matched.no_of_matched_props DESC"
    )
    print(500, sql.literal())
    return sql


def build_select_expanded_entities_from_observations(entities: List[MetaLangEntityBase],
                                                     entity_types: List[str],
                                                     unmatched_entities: int = 0,
                                                     unmatched_traits: int = 0,
                                                     start_date: Optional[datetime] = None,
                                                     end_date: Optional[datetime] = None,
                                                     embeddings: Optional[EmbeddingMap] = None,
                                                     ):
    entities_with_traits = [item for item in entities if item.properties]
    entities_without_traits = [item for item in entities if not item.properties]

    # Tolerance
    entity_filter = [entity.type for entity in entities]
    no_of_entities = max(0, len(entity_filter) - unmatched_entities)

    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()
    sys_ent_state_map = sys_ent_state()

    _skip_vec = embeddings is not None
    _cond1 = build_conditions_sql(entities_with_traits, "traits_conditions", 1, skip_vector=_skip_vec)
    sql1 = (_cond1 + ",") if _cond1 else None
    sql2 = build_conditions_sql(entities_without_traits, "entity_conditions",
                                2) + "," if entities_without_traits else None
    if start_date or end_date:
        sql6 = build_last_property_values_by_date("last_property_values", start_date, end_date) + ","
    else:
        sql6 = build_last_property_values("last_property_values") + ","
    sql3 = (
        build_entities_with_traits_cte(
            "last_property_values", entities_with_traits,
            entity_prefix=1, embeddings=embeddings,
        ) + ","
    ) if entities_with_traits else None
    sql4 = build_entities_without_traits_cte("last_property_values",
                                             entities_without_traits) + "," if entities_without_traits else None

    if entities_with_traits and entities_without_traits:
        sql5 = build_joined_entities_cte()
    elif entities_with_traits:
        sql5 = build_traits_entities_cte()
    elif entities_without_traits:
        sql5 = build_no_traits_entities_cte()
    else:
        raise ValueError("entities_with_traits and entities_without_traits cannot be both empty")

    sql = (
            Sql("WITH ")
            + sql1
            + sql2
            + sql6
            + sql3
            + sql4
            + sql5 + ","
            + "qualifying_observations AS ("
            + "SELECT observation_id"
            + "FROM entities"
            + "GROUP BY observation_id, entity_pk"
            + f"HAVING COUNT(DISTINCT group_id) >= {no_of_entities}"
            + "),"
            + "all_obs_entities AS ("
            + "SELECT eo.observation_id, eo.entity_pk, eo.entity_type"
            + f"FROM {database}.{sys_ent_2_obs_map} eo"
            + "JOIN qualifying_observations q ON eo.observation_id = q.observation_id"
            + ")"
            + "SELECT"
            + "a.observation_id,"
            + "a.entity_pk,"
            + "a.entity_type,"
            + "s.ts,"
            + "s.traits"
            + "FROM all_obs_entities a"
            + f"LEFT JOIN {database}.{sys_ent_state_map} s ON s.entity_pk = a.entity_pk"
            + "WHERE a.entity_type IN :entity_types"
            + "ORDER BY a.observation_id, a.entity_type, a.entity_pk"
            + Param({"entity_types": tuple(entity_types)})
    )
    print(1, sql.literal())
    return sql


def build_select_entity_types_from_observations(entities: List[MetaLangEntityBase],
                                                unmatched_entities: int = 0,
                                                unmatched_traits: int = 0,
                                                start_date: Optional[datetime] = None,
                                                end_date: Optional[datetime] = None,
                                                embeddings: Optional[EmbeddingMap] = None):
    entities_with_traits = [item for item in entities if item.properties]
    entities_without_traits = [item for item in entities if not item.properties]

    entity_filter = [entity.type for entity in entities]
    no_of_entities = max(0, len(entity_filter) - unmatched_entities)

    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()

    _skip_vec = embeddings is not None
    _cond1 = build_conditions_sql(entities_with_traits, "traits_conditions", 1, skip_vector=_skip_vec)
    sql1 = (_cond1 + ",") if _cond1 else None
    sql2 = build_conditions_sql(entities_without_traits, "entity_conditions",
                                2) + "," if entities_without_traits else None
    if start_date or end_date:
        sql6 = build_last_property_values_by_date("last_property_values", start_date, end_date) + ","
    else:
        sql6 = build_last_property_values("last_property_values") + ","
    sql3 = (
        build_entities_with_traits_cte(
            "last_property_values", entities_with_traits,
            entity_prefix=1, embeddings=embeddings,
        ) + ","
    ) if entities_with_traits else None
    sql4 = build_entities_without_traits_cte("last_property_values",
                                             entities_without_traits) + "," if entities_without_traits else None

    if entities_with_traits and entities_without_traits:
        sql5 = build_joined_entities_cte()
    elif entities_with_traits:
        sql5 = build_traits_entities_cte()
    elif entities_without_traits:
        sql5 = build_no_traits_entities_cte()
    else:
        raise ValueError("entities_with_traits and entities_without_traits cannot be both empty")

    sql = (
            Sql("WITH ")
            + sql1
            + sql2
            + sql6
            + sql3
            + sql4
            + sql5 + ","
            + "qualifying_observations AS ("
            + "SELECT observation_id"
            + "FROM entities"
            + "GROUP BY observation_id"
            + f"HAVING COUNT(DISTINCT group_id) >= {no_of_entities}"
            + "),"
            + "all_obs_entities AS ("
            + "SELECT eo.observation_id, eo.entity_pk, eo.entity_type"
            + f"FROM {database}.{sys_ent_2_obs_map} eo"
            + "JOIN qualifying_observations q ON eo.observation_id = q.observation_id"
            + ")"
            + "SELECT entity_type, COUNT(*) AS count"
            + "FROM all_obs_entities"
            # + "WHERE entity_type NOT IN :excluded_types" + Param({"excluded_types": tuple(entity_filter)})
            + "GROUP BY entity_type"
            + "ORDER BY count DESC LIMIT 100"
    )
    print(600, sql.literal())
    return sql
