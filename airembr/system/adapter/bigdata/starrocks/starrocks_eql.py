import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from srd.domain.sql import Sql, Param

from airembr.model.system.meta_language.meta_lang_model import MetaLangEntityBase, MetaLangProperty
from airembr.model.bigdata.flat_ent_property_state import FlatEntityPropertyState
from airembr.model.bigdata.flat_obs import FlatObs
from airembr.model.bigdata.flat_text_vector import FlatTextVector
from airembr.system.adapter.bigdata.general.utils.mapping import (
    sys_ent_2_obs, sys_ent_property_state, sys_ent_state,
    sys_obs_mapping, sys_text_vector_mapping,
)
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name

logger = logging.getLogger(__name__)

# (entity_type, property_name, value) → embedding vector
EmbeddingMap = Dict[Tuple[str, str, str], List[float]]

DEFAULT_MAX_VECTOR_DISTANCE: float = 0.3
DEFAULT_TOP_K: int = 100


# ---------------------------------------------------------------------------
# Query representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QueryGroup:
    """One entity clause from a flat AND-group EQL query."""
    group_id: str                        # "t.1", "t.2" for trait; "n.1", "n.2" for no-trait
    entity_type: str
    properties: Tuple[MetaLangProperty, ...]  # empty tuple for no-trait groups
    required_props: int                  # number of properties that must all match


@dataclass
class QueryPlan:
    """Pre-processed view of a flat AND-group of EQL entity clauses."""
    trait_groups: List[QueryGroup]       # clauses with at least one property
    no_trait_groups: List[QueryGroup]    # clauses with no properties (entity() style)
    all_groups: List[QueryGroup]         # trait_groups + no_trait_groups

    @staticmethod
    def from_entities(
        entities: List[MetaLangEntityBase],
        unmatched_traits: int = 0,
    ) -> 'QueryPlan':
        if any(not isinstance(e, MetaLangEntityBase) for e in entities):
            raise ValueError(
                "build_select_* expects a flat AND-group of MetaLangEntityBase instances; "
                "resolve OR/NOT logic before calling."
            )
        trait_groups: List[QueryGroup] = []
        no_trait_groups: List[QueryGroup] = []
        for i, entity in enumerate((e for e in entities if e.properties), start=1):
            props = tuple(entity.properties)
            trait_groups.append(QueryGroup(
                group_id=f"t.{i}",
                entity_type=entity.type,
                properties=props,
                required_props=max(0, len(props) - unmatched_traits),
            ))
        for i, entity in enumerate((e for e in entities if not e.properties), start=1):
            no_trait_groups.append(QueryGroup(
                group_id=f"n.{i}",
                entity_type=entity.type,
                properties=(),
                required_props=0,
            ))
        return QueryPlan(
            trait_groups=trait_groups,
            no_trait_groups=no_trait_groups,
            all_groups=trait_groups + no_trait_groups,
        )


# ---------------------------------------------------------------------------
# SQL assembly helpers
# ---------------------------------------------------------------------------

def _join_ctes(parts: List[Sql]) -> Sql:
    """Join CTE Sql objects with comma separators."""
    result = parts[0]
    for part in parts[1:]:
        result = result + "," + part
    return result


# ---------------------------------------------------------------------------
# Individual CTE builders (internal)
# ---------------------------------------------------------------------------

def _build_traits_conditions_cte(plan: QueryPlan) -> Optional[Sql]:
    """Inline VALUES table: (entity_type, property_name, property_value, group_id) for exact props.

    Skips ~ (vector) properties — those are handled by vector CTEs.
    Returns None when no exact-match properties exist across all trait groups.
    """
    rows: List[str] = []
    params: Dict = {}
    for group in plan.trait_groups:
        for prop in group.properties:
            if prop.assign == "~":
                continue
            safe = f"{group.group_id}_{prop.name}".replace(".", "_").replace("$", "s")
            key_type = f"tc_{safe}_type"
            key_prop = f"tc_{safe}_prop"
            key_val = f"tc_{safe}_val"
            if not rows:
                row = (
                    f"SELECT :{key_type} AS entity_type, :{key_prop} AS property_name,"
                    f" :{key_val} AS property_value, '{group.group_id}' AS group_id"
                )
            else:
                row = f"UNION ALL SELECT :{key_type}, :{key_prop}, :{key_val}, '{group.group_id}'"
            rows.append(row)
            params[key_type] = group.entity_type
            params[key_prop] = prop.name
            params[key_val] = prop.value
    if not rows:
        return None
    return Sql("traits_conditions AS (\n  " + "\n  ".join(rows) + "\n)") + Param(params)


def _build_entity_conditions_cte(plan: QueryPlan) -> Optional[Sql]:
    """Inline VALUES table: (entity_type, group_id) for property-less entity groups.

    Returns None when plan.no_trait_groups is empty.
    """
    if not plan.no_trait_groups:
        return None
    rows: List[str] = []
    params: Dict = {}
    for group in plan.no_trait_groups:
        safe = group.group_id.replace(".", "_")
        key_type = f"ec_{safe}_type"
        if not rows:
            row = f"SELECT :{key_type} AS entity_type, '{group.group_id}' AS group_id"
        else:
            row = f"UNION ALL SELECT :{key_type}, '{group.group_id}'"
        rows.append(row)
        params[key_type] = group.entity_type
    return Sql("entity_conditions AS (\n  " + "\n  ".join(rows) + "\n)") + Param(params)


def _build_last_property_values_cte(
    view: str,
    entity_types: Tuple[str, ...],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Sql:
    """Deduplicated latest property value per (entity_pk, property_name).

    Always uses sys_ent_property_state (not the append log). Filtered by
    entity_type to avoid a full-table scan (BITMAP index on entity_type).
    """
    database = current_bd_database_name()
    table_map = sys_ent_property_state()
    value_id_col = table_map | FlatEntityPropertyState.VALUE_ID

    if start_date and end_date:
        date_clause = f"AND ts BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'"
    elif start_date:
        date_clause = f"AND ts >= '{start_date.isoformat()}'"
    elif end_date:
        date_clause = f"AND ts <= '{end_date.isoformat()}'"
    else:
        date_clause = ""

    return (
        Sql()
        + f"{view} AS ("
        + "SELECT entity_pk, entity_type, property_name,"
        + "  MAX_BY(property_value, ts) AS property_value,"
        + f"  MAX_BY({value_id_col}, ts) AS property_value_id"
        + f"FROM {database}.{table_map}"
        + "WHERE entity_type IN :lpv_filter"
        + date_clause
        + "GROUP BY entity_pk, entity_type, property_name)"
        + Param({"lpv_filter": entity_types})
    )


def _build_exact_traits_cte(view: str, plan: QueryPlan) -> Optional[Sql]:
    """Build entities_with_exact_traits by joining last_property_values to traits_conditions.

    Returns None when no trait group has any exact-match (= or :) properties.
    """
    exact_types = tuple({
        g.entity_type for g in plan.trait_groups
        if any(p.assign != "~" for p in g.properties)
    })
    if not exact_types:
        return None

    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()

    return (
        Sql()
        + "entities_with_exact_traits AS ("
        + "SELECT p.property_name, p.property_value,"
        + "  o.entity_pk, o.observation_id, o.entity_type, c.group_id"
        + f"FROM {view} p"
        + f"JOIN {database}.{sys_ent_2_obs_map} o ON p.entity_pk = o.entity_pk"
        + "LEFT JOIN traits_conditions c"
        + "  ON (LOWER(p.entity_type) = LOWER(c.entity_type)"
        + "  AND p.property_name = c.property_name"
        + "  AND LOWER(p.property_value) = LOWER(c.property_value))"
        + "WHERE c.group_id IS NOT NULL AND p.entity_type IN :exact_filter"
        + Param({"exact_filter": exact_types})
        + ")"
    )


def _build_vector_top_k_ctes(
    view: str,
    plan: QueryPlan,
    embeddings: EmbeddingMap,
    top_k: int,
) -> List[Tuple[str, str, str]]:
    """Build one ANN top-k CTE per ~ property that has a known embedding.

    Returns list of (cte_sql_string, cte_name, group_id) triples.
    Uses ORDER BY dist LIMIT top_k to engage the StarRocks HNSW vector index.
    """
    database = current_bd_database_name()
    tv_map = sys_text_vector_mapping()
    tv_text_id = tv_map | FlatTextVector.TEXT_ID
    tv_vector = tv_map | FlatTextVector.VECTOR

    entries: List[Tuple[str, str, str]] = []
    for group in plan.trait_groups:
        prop_idx = 0
        for prop in group.properties:
            if prop.assign != "~":
                continue
            prop_idx += 1
            vector = embeddings.get((group.entity_type, prop.name, str(prop.value)))
            if vector is None:
                continue
            safe_gid = group.group_id.replace(".", "_")
            cte_name = f"vector_top_k_{safe_gid}_{prop_idx}"
            vector_str = f"[{', '.join(str(float(v)) for v in vector)}]"
            dist_expr = f"approx_l2_distance(sv.{tv_vector}, {vector_str})"
            cte_sql = (
                f"{cte_name} AS ("
                f"SELECT p.entity_pk, p.property_name, p.property_value, {dist_expr} AS dist "
                f"FROM {view} p "
                f"JOIN {database}.{tv_map} sv ON p.property_value_id = sv.{tv_text_id} "
                f"WHERE LOWER(p.entity_type) = LOWER('{group.entity_type}') "
                f"AND p.property_name = '{prop.name}' "
                f"ORDER BY dist "
                f"LIMIT {top_k})"
            )
            entries.append((cte_sql, cte_name, group.group_id))
    return entries


def _build_vector_traits_cte(
    top_k_entries: List[Tuple[str, str, str]],
    max_distance: float,
) -> Optional[Sql]:
    """Build entities_with_vector_traits as UNION ALL of top-k results filtered by max_distance."""
    if not top_k_entries:
        return None
    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()

    union_parts = []
    for _cte_sql, cte_name, group_id in top_k_entries:
        union_parts.append(
            f"SELECT t.property_name, t.property_value,"
            f" o.entity_pk, o.observation_id, o.entity_type, '{group_id}' AS group_id"
            f" FROM {cte_name} t"
            f" JOIN {database}.{sys_ent_2_obs_map} o ON t.entity_pk = o.entity_pk"
            f" WHERE t.dist <= {max_distance}"
        )
    return Sql(
        "entities_with_vector_traits AS ("
        + " UNION ALL ".join(union_parts)
        + ")"
    )


def _build_entities_with_traits_cte(
    view: str,
    plan: QueryPlan,
    embeddings: Optional[EmbeddingMap],
    max_distance: float,
    top_k: int,
) -> Optional[Sql]:
    """Build the complete trait-match CTE chain.

    When embeddings is None: only exact-match props are matched. ~ props are
    ignored (with a warning).
    When embeddings provided: builds exact + vector arms and unions them.
    Returns None when plan.trait_groups is empty or when all are ~ with no embeddings.
    """
    if not plan.trait_groups:
        return None

    has_vector_props = any(p.assign == "~" for g in plan.trait_groups for p in g.properties)
    if has_vector_props and embeddings is None:
        logger.warning(
            "EQL query contains ~ (similarity) properties but no embeddings were provided. "
            "Those properties will be ignored and will not match any entity."
        )

    exact_cte = _build_exact_traits_cte(view, plan)

    top_k_entries: List[Tuple[str, str, str]] = []
    if embeddings is not None:
        top_k_entries = _build_vector_top_k_ctes(view, plan, embeddings, top_k)
    vector_cte = _build_vector_traits_cte(top_k_entries, max_distance) if top_k_entries else None

    has_exact = exact_cte is not None
    has_vector = vector_cte is not None

    if not has_exact and not has_vector:
        return None

    cte_sqls: List[Sql] = []
    if exact_cte is not None:
        cte_sqls.append(exact_cte)
    for cte_sql_str, _name, _gid in top_k_entries:
        cte_sqls.append(Sql(cte_sql_str))
    if vector_cte is not None:
        cte_sqls.append(vector_cte)

    if has_exact and has_vector:
        final = Sql(
            "entities_with_traits AS ("
            "SELECT * FROM entities_with_exact_traits "
            "UNION ALL SELECT * FROM entities_with_vector_traits)"
        )
    elif has_exact:
        final = Sql("entities_with_traits AS (SELECT * FROM entities_with_exact_traits)")
    else:
        final = Sql("entities_with_traits AS (SELECT * FROM entities_with_vector_traits)")

    cte_sqls.append(final)
    return _join_ctes(cte_sqls)


def _build_entities_without_traits_cte(plan: QueryPlan) -> Optional[Sql]:
    """Build entities_without_traits CTE directly from sys_ent_2_obs (no last_property_values join).

    Emits exactly one row per (obs_id, entity_pk, group_id) regardless of property count.
    Returns None when plan.no_trait_groups is empty.
    """
    if not plan.no_trait_groups:
        return None
    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()
    entity_filter = tuple({g.entity_type for g in plan.no_trait_groups})

    return (
        Sql()
        + "entities_without_traits AS ("
        + "SELECT NULL AS property_name, NULL AS property_value,"
        + "  o.entity_pk, o.observation_id, o.entity_type, c.group_id"
        + f"FROM {database}.{sys_ent_2_obs_map} o"
        + "JOIN entity_conditions c ON LOWER(o.entity_type) = LOWER(c.entity_type)"
        + "WHERE c.group_id IS NOT NULL AND o.entity_type IN :no_trait_filter"
        + Param({"no_trait_filter": entity_filter})
        + ")"
    )


def _build_entities_union_cte(has_traits: bool, has_no_traits: bool) -> Sql:
    if has_traits and has_no_traits:
        return Sql(
            "entities AS ("
            "SELECT * FROM entities_with_traits UNION ALL SELECT * FROM entities_without_traits)"
        )
    elif has_traits:
        return Sql("entities AS (SELECT * FROM entities_with_traits)")
    elif has_no_traits:
        return Sql("entities AS (SELECT * FROM entities_without_traits)")
    else:
        raise ValueError(
            "EQL query has no matchable entity groups. "
            "Check that ~ properties have embeddings available."
        )


def _build_group_requirements_cte(plan: QueryPlan) -> Sql:
    """Inline VALUES: (group_id, required_props) for each query group."""
    rows: List[str] = []
    for group in plan.all_groups:
        if not rows:
            row = f"SELECT '{group.group_id}' AS group_id, {group.required_props} AS required_props"
        else:
            row = f"UNION ALL SELECT '{group.group_id}', {group.required_props}"
        rows.append(row)
    return Sql("group_requirements AS (\n  " + "\n  ".join(rows) + "\n)")


def _build_entity_matches_cte() -> Sql:
    return Sql(
        "entity_matches AS ("
        "SELECT observation_id, entity_pk, group_id, COUNT(*) AS matched_props "
        "FROM entities "
        "GROUP BY observation_id, entity_pk, group_id)"
    )


def _build_eql_preamble(
    plan: QueryPlan,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    embeddings: Optional[EmbeddingMap],
    max_distance: float = DEFAULT_MAX_VECTOR_DISTANCE,
    top_k: int = DEFAULT_TOP_K,
) -> Sql:
    """Build the shared CTE chain: WITH ... entity_matches.

    Each of the four public build_select_* functions appends its own
    terminal SELECT after this preamble.
    """
    entity_types = tuple({g.entity_type for g in plan.all_groups})

    traits_chain = _build_entities_with_traits_cte(
        "last_property_values", plan, embeddings, max_distance, top_k
    )
    no_traits_cte = _build_entities_without_traits_cte(plan)
    entities_cte = _build_entities_union_cte(
        has_traits=traits_chain is not None,
        has_no_traits=no_traits_cte is not None,
    )

    cte_parts: List[Sql] = []
    for part in [
        _build_traits_conditions_cte(plan),
        _build_entity_conditions_cte(plan),
        _build_last_property_values_cte("last_property_values", entity_types, start_date, end_date),
        traits_chain,
        no_traits_cte,
        entities_cte,
        _build_group_requirements_cte(plan),
        _build_entity_matches_cte(),
    ]:
        if part is not None:
            cte_parts.append(part)

    return Sql("WITH\n") + _join_ctes(cte_parts)


def _build_qualifying_observations_ctes(no_of_entities: int) -> Sql:
    """Build qualifying_observations + all_obs_entities CTEs (shared by expanded/entity-type selects)."""
    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()
    return (
        Sql()
        + "qualifying_observations AS ("
        + "SELECT em.observation_id"
        + "FROM entity_matches em"
        + "JOIN group_requirements gr ON em.group_id = gr.group_id"
        + "WHERE em.matched_props >= gr.required_props"
        + "GROUP BY em.observation_id"
        + f"HAVING COUNT(DISTINCT em.group_id) >= {no_of_entities}"
        + "),"
        + "all_obs_entities AS ("
        + "SELECT eo.observation_id, eo.entity_pk, eo.entity_type"
        + f"FROM {database}.{sys_ent_2_obs_map} eo"
        + "JOIN qualifying_observations q ON eo.observation_id = q.observation_id"
        + ")"
    )


# ---------------------------------------------------------------------------
# Public API — signatures unchanged from previous version
# ---------------------------------------------------------------------------

def build_select_observation_will_all_entities(
    entities: List[MetaLangEntityBase],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
) -> Sql:
    plan = QueryPlan.from_entities(entities, unmatched_traits)
    no_of_entities = max(0, len(plan.all_groups) - unmatched_entities)
    preamble = _build_eql_preamble(plan, start_date, end_date, embeddings)
    return (
        preamble
        + "SELECT em.observation_id,"
        + "  COUNT(DISTINCT em.group_id) AS no_of_entities,"
        + "  SUM(em.matched_props) AS no_of_matched_props,"
        + "  GROUP_CONCAT(DISTINCT em.entity_pk) AS entity_pks"
        + "FROM entity_matches em"
        + "JOIN group_requirements gr ON em.group_id = gr.group_id"
        + "WHERE em.matched_props >= gr.required_props"
        + "GROUP BY em.observation_id"
        + f"HAVING no_of_entities >= {no_of_entities}"
        + "ORDER BY no_of_matched_props DESC"
    )


def build_select_observations_with_eql(
    entities: List[MetaLangEntityBase],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
) -> Sql:
    plan = QueryPlan.from_entities(entities, unmatched_traits)
    no_of_entities = max(0, len(plan.all_groups) - unmatched_entities)
    preamble = _build_eql_preamble(plan, start_date, end_date, embeddings)

    database = current_bd_database_name()
    sys_obs = sys_obs_mapping()

    matching_cte = (
        Sql()
        + "matching_entities AS ("
        + "SELECT em.observation_id,"
        + "  COUNT(DISTINCT em.group_id) AS no_of_entities,"
        + "  SUM(em.matched_props) AS no_of_matched_props"
        + "FROM entity_matches em"
        + "JOIN group_requirements gr ON em.group_id = gr.group_id"
        + "WHERE em.matched_props >= gr.required_props"
        + "GROUP BY em.observation_id"
        + f"HAVING no_of_entities >= {no_of_entities})"
    )

    return (
        preamble + "," + matching_cte
        + "SELECT"
        + f"  o.{sys_obs | FlatObs.ID},"
        + f"  o.{sys_obs | FlatObs.METADATA_TIME_INSERT},"
        + f"  o.{sys_obs | FlatObs.METADATA_TIME_CREATE},"
        + f"  o.{sys_obs | FlatObs.SUMMARY} AS summary,"
        + f"  o.{sys_obs | FlatObs.DESCRIPTION} AS description,"
        + f"  o.{sys_obs | FlatObs.ENTITIES},"
        + "  matched.no_of_entities, matched.no_of_matched_props"
        + "FROM matching_entities AS matched"
        + f"JOIN {database}.{sys_obs} AS o ON o.{sys_obs | FlatObs.ID} = matched.observation_id"
        + "ORDER BY matched.no_of_matched_props DESC"
    )


def build_select_expanded_entities_from_observations(
    entities: List[MetaLangEntityBase],
    entity_types: List[str],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
) -> Sql:
    plan = QueryPlan.from_entities(entities, unmatched_traits)
    no_of_entities = max(0, len(plan.all_groups) - unmatched_entities)
    preamble = _build_eql_preamble(plan, start_date, end_date, embeddings)

    database = current_bd_database_name()
    sys_ent_state_map = sys_ent_state()

    return (
        preamble + ","
        + _build_qualifying_observations_ctes(no_of_entities)
        + "SELECT"
        + "  a.observation_id,"
        + "  a.entity_pk,"
        + "  a.entity_type,"
        + "  s.ts,"
        + "  s.traits"
        + "FROM all_obs_entities a"
        + f"LEFT JOIN {database}.{sys_ent_state_map} s ON s.entity_pk = a.entity_pk"
        + "WHERE a.entity_type IN :entity_types"
        + "ORDER BY a.observation_id, a.entity_type, a.entity_pk"
        + Param({"entity_types": tuple(entity_types)})
    )


def build_select_entity_types_from_observations(
    entities: List[MetaLangEntityBase],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
) -> Sql:
    plan = QueryPlan.from_entities(entities, unmatched_traits)
    no_of_entities = max(0, len(plan.all_groups) - unmatched_entities)
    preamble = _build_eql_preamble(plan, start_date, end_date, embeddings)

    return (
        preamble + ","
        + _build_qualifying_observations_ctes(no_of_entities)
        + "SELECT entity_type, COUNT(*) AS count"
        + "FROM all_obs_entities"
        + "GROUP BY entity_type"
        + "ORDER BY count DESC LIMIT 100"
    )
