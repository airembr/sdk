"""EQL → StarRocks SQL compiler.

This module translates a flat AND-group of EQL (Entity Query Language) entity
clauses into a StarRocks CTE-based SQL query. The entry point is one of the
four public ``build_select_*`` functions; all other symbols are internal.

─── What EQL looks like ─────────────────────────────────────────────────────

    location($name~"Wroclaw", $type="city") AND person($name="Todd")
    location($name="Kazimierz Dolny") AND person()

Each clause in the AND-group is called an *entity group* and maps to a
``MetaLangEntityBase`` in Python. The query above has two groups:
  • group 1 — entity_type="location", two properties
  • group 2 — entity_type="person", one property (or none)

─── What we are searching for ───────────────────────────────────────────────

The database stores *observations* — timestamped records each containing one
or more entities. An entity carries typed property values (e.g. $name="Todd").

The query ``location(...) AND person(...)`` asks:
  "Find every observation that contains (a) a location entity satisfying ALL
   location predicates AND (b) a person entity satisfying ALL person predicates."

Two critical semantic invariants that the SQL must enforce:
  1. Per-entity completeness — ALL properties of a group must be satisfied by
     the SAME entity_pk.  If location_A matches $name and location_B matches
     $type, that does NOT satisfy one group.
  2. Per-observation cross-group coverage — every query group must be satisfied
     by at least one entity within the SAME observation.

─── How the SQL is structured ───────────────────────────────────────────────

All four ``build_select_*`` functions emit a StarRocks WITH-query whose CTE
chain is identical up to the last CTE (``entity_matches``).  This shared part
is called the *preamble* and is built by ``_build_eql_preamble``.

Preamble CTE order (some CTEs are optional):

  traits_conditions        -- query-time inline table: exact-match property spec
  entity_conditions        -- query-time inline table: property-less entity spec
  last_property_values     -- deduped latest property per (entity_pk, prop_name)
  entities_with_exact_traits  ─┐ emitted only when ~ props + embeddings present
  vector_top_k_t_N_M          ─┤ one per ~ property with a known embedding
  entities_with_vector_traits ─┘
  entities_with_traits     -- union of exact + vector arms (or just one)
  entities_without_traits  -- property-less entity matches
  entities                 -- UNION ALL of the above two
  group_requirements       -- query-time inline table: group_id → required count
  entity_matches           -- COUNT matched props per (obs, entity_pk, group)

After the preamble each ``build_select_*`` appends a different terminal SELECT.

─── Two-level aggregation ───────────────────────────────────────────────────

The two semantic invariants are enforced by a two-level aggregation:

  Level 1 — entity_matches groups by (observation_id, entity_pk, group_id) and
             counts how many property rows matched for that specific entity.
             Combined with group_requirements, this filters out entities that
             only partially satisfy a group's predicates.

  Level 2 — The terminal SELECT (or matching_entities CTE) groups by
             observation_id and counts distinct satisfied group_ids.  Only
             observations where every query group is satisfied pass the HAVING.

─── Property assignment operators ───────────────────────────────────────────

  =  or  :   exact match (case-insensitive) via traits_conditions JOIN
  ~          ANN vector similarity via sys_text_vector; requires that
             property_value_id in sys_ent_property_state points to a stored
             vector in sys_text_vector, and that the caller supplies a
             pre-computed query embedding in the ``embeddings`` argument.
"""

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

# Maps (entity_type, property_name, value) → dense embedding vector.
# Built by the caller (starrocks_entity_property_adapter) from the ~ properties
# in the query before the SQL is generated.
EmbeddingMap = Dict[Tuple[str, str, str], List[float]]

# Cosine similarity threshold for vector search (approx_cosine_similarity).
# Candidates whose similarity is below this value are excluded.
# Higher = stricter; 0.7 works well for normalised sentence embeddings.
DEFAULT_MIN_VECTOR_SIMILARITY: float = 0.7

# Number of ANN candidates fetched per ~ property via the HNSW index.
# ORDER BY dist DESC LIMIT top_k engages StarRocks's HNSW index; a plain
# WHERE dist >= threshold would fall back to a brute-force scan.
# Filtered further by DEFAULT_MIN_VECTOR_SIMILARITY after the top-k fetch.
DEFAULT_TOP_K: int = 100


# ---------------------------------------------------------------------------
# Query representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QueryGroup:
    """The compiled form of one EQL entity clause within an AND-group.

    A ``QueryGroup`` is created from a ``MetaLangEntityBase`` and carries
    every attribute needed to emit the group's SQL CTEs, without any further
    reference to the original model.

    Attributes
    ----------
    group_id:
        Stable string key used as the ``group_id`` column value throughout
        all CTEs in the same query.  Trait groups use ``"t.N"`` (e.g. ``"t.1"``,
        ``"t.2"``); property-less groups use ``"n.N"`` (e.g. ``"n.1"``).
        These IDs are ephemeral — they appear only within one SQL query and
        are never persisted or returned to callers.
    entity_type:
        Lowercased entity type string, e.g. ``"location"``, ``"person"``.
    properties:
        Immutable tuple of property filters.  Empty for no-trait groups.
    required_props:
        The number of matched property rows an entity_pk must contribute in
        ``entity_matches`` for this group to be considered *satisfied*.
        Normally equals ``len(properties)`` (all must match), but is reduced
        by ``unmatched_traits`` when fuzzy matching is allowed.

    Example
    -------
    For the clause ``location($name~"Wroclaw", $type="city")`` this becomes::

        QueryGroup(
            group_id     = "t.1",
            entity_type  = "location",
            properties   = (
                MetaLangProperty(name="$name", assign="~", value="Wroclaw"),
                MetaLangProperty(name="$type", assign="=", value="city"),
            ),
            required_props = 2,
        )
    """
    group_id: str
    entity_type: str
    properties: Tuple[MetaLangProperty, ...]
    required_props: int


@dataclass
class QueryPlan:
    """Pre-processed view of a flat AND-group of EQL entity clauses.

    ``QueryPlan`` is the single source of truth for the query structure inside
    this module.  It is created once per SQL-build call via ``from_entities``
    and then passed down to every CTE builder, so each builder can read the
    group_ids, entity types, and property lists without re-parsing the raw
    model objects.

    Attributes
    ----------
    trait_groups:
        Groups that have at least one property.  Their matching logic uses
        ``last_property_values`` joined to ``traits_conditions`` (exact) or
        ``sys_text_vector`` (vector).
    no_trait_groups:
        Groups with no properties — ``entity()``-style clauses that assert
        "this observation contains at least one entity of this type".  Their
        matching logic goes directly to ``sys_ent_2_obs``.
    all_groups:
        ``trait_groups + no_trait_groups``.  Used to enumerate all group_ids
        and to compute ``no_of_entities`` (the minimum number of satisfied
        groups required per observation).
    """
    trait_groups: List[QueryGroup]
    no_trait_groups: List[QueryGroup]
    all_groups: List[QueryGroup]

    @staticmethod
    def from_entities(
        entities: List[MetaLangEntityBase],
        unmatched_traits: int = 0,
    ) -> 'QueryPlan':
        """Build a ``QueryPlan`` from a flat AND-group of entity clauses.

        Parameters
        ----------
        entities:
            A flat list of ``MetaLangEntityBase`` objects representing the
            AND-connected entity clauses of one EQL query.  Must NOT contain
            ``MetaLangLogic`` nodes — resolve OR/NOT before calling.
        unmatched_traits:
            Allow up to this many property misses per group.  For example,
            with ``unmatched_traits=1`` a group with 3 properties requires
            only 2 to match (``required_props = max(0, 3 - 1) = 2``).
            Default 0 means all properties must match.

        Raises
        ------
        ValueError
            If ``entities`` contains non-``MetaLangEntityBase`` items
            (e.g. ``MetaLangLogic`` from an OR branch).

        Example
        -------
        Given the EQL query ``location($name~"Wroclaw", $type="city") AND person()``
        the caller passes::

            entities = [
                MetaLangEntity(type="location", properties=[
                    MetaLangProperty(name="$name", assign="~", value="Wroclaw"),
                    MetaLangProperty(name="$type", assign="=",  value="city"),
                ]),
                MetaLangEntity(type="person", properties=[]),
            ]

        This produces::

            QueryPlan(
                trait_groups    = [QueryGroup(group_id="t.1", entity_type="location", ...)],
                no_trait_groups = [QueryGroup(group_id="n.1", entity_type="person",   ...)],
                all_groups      = [<t.1>, <n.1>],
            )
        """
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
    """Join a list of CTE ``Sql`` fragments with comma separators.

    Used instead of chaining ``Sql + None + Sql`` (which relies on the Sql
    class silently ignoring ``None`` operands).  Here each caller explicitly
    filters ``None`` before calling, making the control flow clear.
    """
    result = parts[0]
    for part in parts[1:]:
        result = result + "," + part
    return result


# ---------------------------------------------------------------------------
# Individual CTE builders (internal)
# ---------------------------------------------------------------------------

def _build_traits_conditions_cte(plan: QueryPlan) -> Optional[Sql]:
    """Build the ``traits_conditions`` inline-values CTE for exact-match properties.

    ``traits_conditions`` is a query-time lookup table that the
    ``entities_with_exact_traits`` CTE joins against.  Each row encodes one
    property predicate for one query group:

    .. code-block:: sql

        traits_conditions AS (
          SELECT 'location' AS entity_type, '$name' AS property_name,
                 'Wroclaw'  AS property_value, 't.1' AS group_id
          UNION ALL SELECT 'location', '$type', 'city',  't.1'
          UNION ALL SELECT 'person',   '$name', 'Todd',  't.2'
        )

    Only ``=`` and ``:`` properties are emitted here.  ``~`` (similarity)
    properties are handled by the vector CTEs and must never appear in this
    table — their raw string value is meaningless for an exact match.

    Returns ``None`` when no trait group has any exact-match property, in which
    case the caller omits the CTE entirely (the vector arm alone is sufficient).
    """
    rows: List[str] = []
    params: Dict = {}
    for group in plan.trait_groups:
        for prop in group.properties:
            if prop.assign == "~":
                continue  # vector props are handled by the vector CTE chain

            # Build stable, SQL-safe parameter keys from group_id + prop name.
            # Replace dots and dollar signs which are not valid in :param names.
            safe = f"{group.group_id}_{prop.name}".replace(".", "_").replace("$", "s")
            key_type = f"tc_{safe}_type"
            key_prop = f"tc_{safe}_prop"
            key_val  = f"tc_{safe}_val"

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
            params[key_val]  = prop.value

    if not rows:
        return None
    return Sql("traits_conditions AS (\n  " + "\n  ".join(rows) + "\n)") + Param(params)


def _build_entity_conditions_cte(plan: QueryPlan) -> Optional[Sql]:
    """Build the ``entity_conditions`` inline-values CTE for property-less groups.

    ``entity_conditions`` is a query-time lookup table used by
    ``entities_without_traits``.  Unlike ``traits_conditions``, it stores only
    ``(entity_type, group_id)`` — no property columns — because a property-less
    clause ``person()`` asserts only that some person entity exists in the
    observation, not what properties it has.

    .. code-block:: sql

        entity_conditions AS (
          SELECT 'person' AS entity_type, 'n.1' AS group_id
          UNION ALL SELECT 'aspect', 'n.2'
        )

    Returns ``None`` when ``plan.no_trait_groups`` is empty (nothing to emit).
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
    """Build the ``last_property_values`` deduplication CTE.

    ``sys_ent_property_state`` is a primary-key table keyed on
    ``(observer_pk, entity_pk, entity_type, property_name)``.  Multiple
    observers may write different values for the same property; ``MAX_BY``
    picks the one with the latest timestamp.

    The resulting CTE has one row per ``(entity_pk, property_name)`` and
    exposes the columns used by the downstream JOIN CTEs:

    .. code-block:: sql

        last_property_values AS (
          SELECT entity_pk, entity_type, property_name,
                 MAX_BY(property_value,    ts) AS property_value,
                 MAX_BY(property_value_id, ts) AS property_value_id
          FROM testdb.sys_ent_property_state
          WHERE entity_type IN ('location', 'person')  -- BITMAP index hit
          GROUP BY entity_pk, entity_type, property_name
        )

    ``property_value_id`` is the FK into ``sys_text_vector`` used by the
    vector similarity arm.  It is NULL when the value has not been embedded yet.

    Notes
    -----
    • Always targets ``sys_ent_property_state`` (the current-state table), NOT
      ``sys_ent_property`` (the historical append log).  The append log has a
      much higher NULL rate for ``property_value_id`` and different semantics.
    • The ``WHERE entity_type IN`` clause converts a full table scan into an
      indexed lookup via StarRocks's BITMAP index on ``entity_type``.
    • ``start_date`` / ``end_date`` filter which property writes are considered:
      only writes in the time window contribute to the MAX_BY aggregation.
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
    """Build the ``entities_with_exact_traits`` CTE for exact-match (= or :) properties.

    Joins ``last_property_values`` to ``traits_conditions`` (case-insensitive)
    and then to ``sys_ent_2_obs`` to obtain the observation_id.  The result is
    one row per ``(property_name, property_value, entity_pk, observation_id,
    entity_type, group_id)`` for every entity_pk that has at least one exact
    property match in the query.

    .. code-block:: sql

        entities_with_exact_traits AS (
          SELECT p.property_name, p.property_value,
                 o.entity_pk, o.observation_id, o.entity_type, c.group_id
          FROM last_property_values p
          JOIN testdb.sys_ent_2_obs o ON p.entity_pk = o.entity_pk
          LEFT JOIN traits_conditions c
            ON  LOWER(p.entity_type)    = LOWER(c.entity_type)
            AND p.property_name          = c.property_name
            AND LOWER(p.property_value)  = LOWER(c.property_value)
          WHERE c.group_id IS NOT NULL
            AND p.entity_type IN ('location', 'person')
        )

    The LEFT JOIN + ``WHERE c.group_id IS NOT NULL`` pattern means: keep only
    those property rows that match at least one query predicate.  Non-matching
    property rows (e.g. $email for a person query) are silently dropped.

    Returns ``None`` when no trait group has any ``=`` or ``:`` property, so
    the caller can omit this CTE and use the vector arm alone.
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
        + "  o.entity_pk, o.observation_id, o.entity_type, c.group_id, 1.0 AS dist"
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
    min_similarity: float,
) -> List[Tuple[str, str, str, float]]:
    """Build one ANN top-k CTE per ``~`` property that has a known embedding.

    For each ``~`` property whose ``(entity_type, prop_name, value)`` key
    appears in ``embeddings``, one CTE is emitted.  The CTE uses
    ``approx_cosine_similarity`` with ``ORDER BY dist DESC LIMIT top_k`` to engage
    StarRocks's HNSW vector index (a bare ``WHERE dist >= threshold`` would
    fall back to a full brute-force scan of ``sys_text_vector``).

    The query embedding vector is inlined directly into the SQL string rather
    than being passed as a parameter, because StarRocks does not support array
    literals as bind parameters in this context.

    Example CTE for ``location($name~"Wroclaw")`` with a 3-dim stub vector::

        vector_top_k_t_1_1 AS (
          SELECT p.entity_pk, p.property_name, p.property_value,
                 approx_cosine_similarity(sv.vector, [0.1, 0.2, 0.3]) AS dist
          FROM last_property_values p
          JOIN testdb.sys_text_vector sv ON p.property_value_id = sv.text_id
          WHERE LOWER(p.entity_type) = LOWER('location')
            AND p.property_name = '$name'
          ORDER BY dist DESC
          LIMIT 100
        )

    CTE naming: ``vector_top_k_{safe_group_id}_{prop_idx}`` where
    ``safe_group_id`` is the group_id with dots replaced by underscores
    (e.g. ``"t.1"`` → ``"t_1"``).  ``prop_idx`` is the 1-based index of the
    ``~`` property within the group (so two ``~`` props in the same group get
    ``_1`` and ``_2`` suffixes).

    Returns a list of ``(cte_sql_string, cte_name, group_id, distance)`` 4-tuples.
    The caller assembles them into a ``Sql`` object and builds the
    ``entities_with_vector_traits`` UNION on top.

    Properties whose embedding key is absent from ``embeddings`` are silently
    skipped (no CTE emitted for them).  This can happen when the embedding
    service has not yet indexed a particular value.
    """
    database = current_bd_database_name()
    tv_map = sys_text_vector_mapping()
    tv_text_id = tv_map | FlatTextVector.TEXT_ID
    tv_vector  = tv_map | FlatTextVector.VECTOR

    entries: List[Tuple[str, str, str, float]] = []
    for group in plan.trait_groups:
        prop_idx = 0
        for prop in group.properties:
            if prop.assign != "~":
                continue
            prop_idx += 1

            vector = embeddings.get((group.entity_type, prop.name, str(prop.value)))
            if vector is None:
                # Embedding not available for this value — skip silently.
                # The property will not contribute any rows to entity_matches,
                # so this group's required_props may not be satisfiable.
                continue

            safe_gid  = group.group_id.replace(".", "_")
            cte_name  = f"vector_top_k_{safe_gid}_{prop_idx}"
            vector_str = f"[{', '.join(str(float(v)) for v in vector)}]"
            dist_expr  = f"approx_cosine_similarity(sv.{tv_vector}, {vector_str})"

            cte_sql = (
                f"{cte_name} AS ("
                f"SELECT p.entity_pk, p.property_name, p.property_value, {dist_expr} AS dist "
                f"FROM {view} p "
                f"JOIN {database}.{tv_map} sv ON p.property_value_id = sv.{tv_text_id} "
                f"WHERE LOWER(p.entity_type) = LOWER('{group.entity_type}') "
                f"AND p.property_name = '{prop.name}' "
                f"ORDER BY dist DESC "      # triggers HNSW index
                f"LIMIT {top_k})"         # cap candidates before distance filter
            )
            distance = prop.distance if prop.distance is not None else min_similarity
            entries.append((cte_sql, cte_name, group.group_id, distance))
    return entries


def _build_vector_traits_cte(
    top_k_entries: List[Tuple[str, str, str, float]],
) -> Optional[Sql]:
    """Build ``entities_with_vector_traits`` as a UNION ALL of top-k results.

    Each arm in the UNION joins one ``vector_top_k_*`` CTE (which already
    holds ``entity_pk, property_name, property_value, dist``) to
    ``sys_ent_2_obs`` to obtain ``observation_id``.  The distance threshold
    filter ``WHERE t.dist >= min_similarity`` is applied here (after the top-k
    HNSW fetch) to drop candidates that are close in rank but below the cosine
    similarity threshold.

    Example for two ~ properties in two groups::

        entities_with_vector_traits AS (
          SELECT t.property_name, t.property_value,
                 o.entity_pk, o.observation_id, o.entity_type, 't.1' AS group_id
          FROM vector_top_k_t_1_1 t
          JOIN testdb.sys_ent_2_obs o ON t.entity_pk = o.entity_pk
          WHERE t.dist >= 0.7
          UNION ALL
          SELECT t.property_name, t.property_value,
                 o.entity_pk, o.observation_id, o.entity_type, 't.2' AS group_id
          FROM vector_top_k_t_2_1 t
          JOIN testdb.sys_ent_2_obs o ON t.entity_pk = o.entity_pk
          WHERE t.dist >= 0.7
        )

    Output schema matches ``entities_with_exact_traits`` exactly so they can
    be UNIONed into ``entities_with_traits``:
    ``(property_name, property_value, entity_pk, observation_id, entity_type, group_id)``

    Returns ``None`` when ``top_k_entries`` is empty.
    """
    if not top_k_entries:
        return None
    database = current_bd_database_name()
    sys_ent_2_obs_map = sys_ent_2_obs()

    union_parts = []
    for _cte_sql, cte_name, group_id, distance in top_k_entries:
        union_parts.append(
            f"SELECT t.property_name, t.property_value,"
            f" o.entity_pk, o.observation_id, o.entity_type, '{group_id}' AS group_id, t.dist"
            f" FROM {cte_name} t"
            f" JOIN {database}.{sys_ent_2_obs_map} o ON t.entity_pk = o.entity_pk"
            f" WHERE t.dist >= {distance}"
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
    min_similarity: float,
    top_k: int,
) -> Optional[Sql]:
    """Build the complete trait-match CTE chain and return it as one Sql block.

    This is the coordinator that decides which arms (exact, vector, or both)
    are needed and emits all associated CTEs in dependency order:

    1. ``entities_with_exact_traits`` — when any trait group has ``=``/``:`` props
    2. ``vector_top_k_t_N_M`` — one per ``~`` prop with a known embedding
    3. ``entities_with_vector_traits`` — UNION of the top-k arms
    4. ``entities_with_traits`` — final union of the exact and vector arms

    Possible output shapes
    ~~~~~~~~~~~~~~~~~~~~~~
    Only exact props (no ``~`` or no embeddings):
        ``entities_with_exact_traits, entities_with_traits AS SELECT * FROM ...``

    Only vector props (no ``=``/``:``):
        ``vector_top_k_*, entities_with_vector_traits, entities_with_traits AS SELECT * FROM ...``

    Mixed (both ``=``/``:`` and ``~``):
        ``entities_with_exact_traits, vector_top_k_*, entities_with_vector_traits,
        entities_with_traits AS (... UNION ALL ...)``

    Returns ``None`` when:
    • ``plan.trait_groups`` is empty (no property clauses at all), OR
    • all properties are ``~`` but ``embeddings`` is ``None`` (no vector arm
      can be built and there are no exact props either).
    In both cases ``_build_eql_preamble`` skips the CTE entirely.

    Embeddings and the ``~`` operator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    If a query has ``~`` properties but ``embeddings is None`` (e.g. the
    embedding service is unconfigured), a warning is logged and the ``~``
    properties are silently skipped.  If a group has ONLY ``~`` props this
    means the group cannot match anything, and the query will return 0 results
    for that group.
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

    top_k_entries: List[Tuple[str, str, str, float]] = []
    if embeddings is not None:
        top_k_entries = _build_vector_top_k_ctes(view, plan, embeddings, top_k, min_similarity)
    vector_cte = _build_vector_traits_cte(top_k_entries) if top_k_entries else None

    has_exact  = exact_cte is not None
    has_vector = vector_cte is not None

    if not has_exact and not has_vector:
        return None

    # Assemble all CTEs in dependency order: exact arm → per-prop top-k CTEs
    # → vector union → final entities_with_traits union.
    cte_sqls: List[Sql] = []
    if exact_cte is not None:
        cte_sqls.append(exact_cte)
    for cte_sql_str, _name, _gid, _dist in top_k_entries:
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
    """Build ``entities_without_traits`` directly from ``sys_ent_2_obs``.

    Property-less clauses like ``person()`` assert only that *some* person
    entity exists in the observation; no property values need to be read.
    Going directly to ``sys_ent_2_obs`` (rather than through
    ``last_property_values``) emits exactly one row per
    ``(obs_id, entity_pk, group_id)`` — no fanout regardless of how many
    properties the entity has.

    .. code-block:: sql

        entities_without_traits AS (
          SELECT NULL AS property_name, NULL AS property_value,
                 o.entity_pk, o.observation_id, o.entity_type, c.group_id
          FROM testdb.sys_ent_2_obs o
          JOIN entity_conditions c ON LOWER(o.entity_type) = LOWER(c.entity_type)
          WHERE c.group_id IS NOT NULL AND o.entity_type IN ('person')
        )

    The ``NULL`` columns ensure the output schema matches
    ``entities_with_traits`` so both can be UNIONed into ``entities``.

    In ``entity_matches``, these rows contribute ``matched_props = 1`` for each
    entity_pk.  Since ``required_props = 0`` for no-trait groups, the condition
    ``matched_props >= required_props`` (i.e. ``1 >= 0``) always passes, which
    is the intended semantics: any entity of the right type satisfies the group.

    Returns ``None`` when ``plan.no_trait_groups`` is empty.
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
        + "  o.entity_pk, o.observation_id, o.entity_type, c.group_id, NULL AS dist"
        + f"FROM {database}.{sys_ent_2_obs_map} o"
        + "JOIN entity_conditions c ON LOWER(o.entity_type) = LOWER(c.entity_type)"
        + "WHERE c.group_id IS NOT NULL AND o.entity_type IN :no_trait_filter"
        + Param({"no_trait_filter": entity_filter})
        + ")"
    )


def _build_entities_union_cte(has_traits: bool, has_no_traits: bool) -> Sql:
    """Build the ``entities`` CTE as a UNION ALL of the trait and no-trait arms.

    ``entities`` is the single feed into ``entity_matches``.  Its schema is:
    ``(property_name, property_value, entity_pk, observation_id, entity_type, group_id)``

    Only the arms that were actually built are included:

    ============  ==============  =============================================
    has_traits    has_no_traits   entities body
    ============  ==============  =============================================
    True          True            UNION ALL of both
    True          False           SELECT * FROM entities_with_traits
    False         True            SELECT * FROM entities_without_traits
    False         False           raises ValueError (no matchable groups)
    ============  ==============  =============================================

    Raises ``ValueError`` when both arms are absent, which happens when all
    properties are ``~`` but no embeddings are available.
    """
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
    """Build the ``group_requirements`` inline-values CTE.

    This CTE encodes the per-group satisfaction threshold derived from the
    query at Python time.  It is JOINed against ``entity_matches`` to enforce
    the *per-entity completeness* invariant:

    .. code-block:: sql

        group_requirements AS (
          SELECT 't.1' AS group_id, 2 AS required_props
          UNION ALL SELECT 't.2', 1
          UNION ALL SELECT 'n.1', 0
        )

    For the query ``location($name~"Wroclaw", $type="city") AND person()``:
    • ``t.1`` (location) requires 2 matched properties
    • ``n.1`` (person, no-trait) requires 0 (any person entity satisfies it)

    When ``unmatched_traits > 0`` the ``required_props`` values are already
    reduced by ``QueryPlan.from_entities``; this CTE simply reads them out.
    """
    rows: List[str] = []
    for group in plan.all_groups:
        if not rows:
            row = f"SELECT '{group.group_id}' AS group_id, {group.required_props} AS required_props"
        else:
            row = f"UNION ALL SELECT '{group.group_id}', {group.required_props}"
        rows.append(row)
    return Sql("group_requirements AS (\n  " + "\n  ".join(rows) + "\n)")


def _build_entity_matches_cte() -> Sql:
    """Build the ``entity_matches`` CTE — the first level of the two-level aggregation.

    Groups ``entities`` by ``(observation_id, entity_pk, group_id)`` and counts
    how many property rows each entity_pk contributed for each query group:

    .. code-block:: sql

        entity_matches AS (
          SELECT observation_id, entity_pk, group_id, COUNT(*) AS matched_props
          FROM entities
          GROUP BY observation_id, entity_pk, group_id
        )

    This count is then compared against ``group_requirements.required_props``
    in the terminal SELECT (or ``matching_entities`` CTE).  Only entity_pks
    where ``matched_props >= required_props`` are counted toward satisfying
    a group — enforcing that a SINGLE entity must hold ALL required properties.

    Example: for ``location($name="Wroclaw", $type="city")``
    • location_A contributes $name → ``matched_props = 1``, required = 2 → fails
    • location_B contributes $name and $type → ``matched_props = 2`` → passes
    So only observations containing location_B are returned.
    """
    return Sql(
        "entity_matches AS ("
        "SELECT observation_id, entity_pk, group_id, COUNT(*) AS matched_props, MAX(dist) AS max_similarity "
        "FROM entities "
        "GROUP BY observation_id, entity_pk, group_id)"
    )


def _build_eql_preamble(
    plan: QueryPlan,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    embeddings: Optional[EmbeddingMap],
    min_similarity: float = DEFAULT_MIN_VECTOR_SIMILARITY,
    top_k: int = DEFAULT_TOP_K,
) -> Sql:
    """Build the shared CTE chain that all four ``build_select_*`` functions start with.

    Returns a ``Sql`` object that begins with ``WITH`` and ends at
    ``entity_matches``.  Each caller appends its own terminal SELECT (or a
    few more CTEs followed by a SELECT) to produce the final query.

    CTE emission order
    ------------------
    ============================  ====  =========================================
    CTE                           Opt?  Condition for inclusion
    ============================  ====  =========================================
    ``traits_conditions``         yes   any trait group has ``=``/``:`` props
    ``entity_conditions``         yes   any no-trait group exists
    ``last_property_values``      no    always
    ``entities_with_exact_traits``yes   any trait group has ``=``/``:`` props
    ``vector_top_k_t_N_M``        yes   one per ``~`` prop with an embedding
    ``entities_with_vector_traits``yes  any ``~`` prop had an embedding
    ``entities_with_traits``      yes   any trait group is matchable
    ``entities_without_traits``   yes   any no-trait group exists
    ``entities``                  no    always (UNION ALL of the two arms)
    ``group_requirements``        no    always
    ``entity_matches``            no    always
    ============================  ====  =========================================

    The ``Optional`` CTEs are included only when needed; ``None``-valued parts
    are filtered before the list is passed to ``_join_ctes``, making the
    control flow explicit rather than relying on the ``Sql +`` operator to
    silently skip ``None``.
    """
    entity_types = tuple({g.entity_type for g in plan.all_groups})

    # Build the two major arms first so we know which ones exist before
    # constructing the entities UNION CTE.
    traits_chain = _build_entities_with_traits_cte(
        "last_property_values", plan, embeddings, min_similarity, top_k
    )
    no_traits_cte = _build_entities_without_traits_cte(plan)
    entities_cte  = _build_entities_union_cte(
        has_traits=traits_chain is not None,
        has_no_traits=no_traits_cte is not None,
    )

    cte_parts: List[Sql] = []
    for part in [
        _build_traits_conditions_cte(plan),
        _build_entity_conditions_cte(plan),
        _build_last_property_values_cte("last_property_values", entity_types, start_date, end_date),
        traits_chain,           # may be None → filtered out
        no_traits_cte,          # may be None → filtered out
        entities_cte,
        _build_group_requirements_cte(plan),
        _build_entity_matches_cte(),
    ]:
        if part is not None:
            cte_parts.append(part)

    return Sql("WITH\n") + _join_ctes(cte_parts)


def _build_qualifying_observations_ctes(no_of_entities: int) -> Sql:
    """Build ``qualifying_observations`` + ``all_obs_entities`` — shared by two public functions.

    ``qualifying_observations`` applies the second level of the two-level
    aggregation: filter observations where every query group is satisfied by at
    least one entity_pk, then collect all entity_pks in those observations
    (regardless of entity type) into ``all_obs_entities`` for the caller to
    project or aggregate further.

    .. code-block:: sql

        qualifying_observations AS (
          SELECT em.observation_id
          FROM entity_matches em
          JOIN group_requirements gr ON em.group_id = gr.group_id
          WHERE em.matched_props >= gr.required_props   -- per-entity completeness
          GROUP BY em.observation_id
          HAVING COUNT(DISTINCT em.group_id) >= 2       -- all query groups satisfied
        ),
        all_obs_entities AS (
          SELECT eo.observation_id, eo.entity_pk, eo.entity_type
          FROM testdb.sys_ent_2_obs eo
          JOIN qualifying_observations q ON eo.observation_id = q.observation_id
        )

    ``all_obs_entities`` contains every entity in every qualifying observation,
    not just the entities that matched the query.  The callers filter further
    (by ``entity_type IN :entity_types`` or via ``GROUP BY entity_type``).
    """
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
# Public API
# ---------------------------------------------------------------------------

def build_select_observation_will_all_entities(
    entities: List[MetaLangEntityBase],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
) -> Sql:
    """Return a query that finds qualifying observations and their matched entity_pks.

    This is the lightest of the four public functions — it returns only
    ``(observation_id, no_of_entities, no_of_matched_props, entity_pks)``
    without joining the full observation metadata table.  Useful for fast
    existence checks or when the caller fetches observation details separately.

    The terminal SELECT applies the second aggregation level directly (without
    a ``matching_entities`` CTE), grouping ``entity_matches`` by
    ``observation_id`` and using ``GROUP_CONCAT`` to collect entity_pks:

    .. code-block:: sql

        SELECT em.observation_id,
               COUNT(DISTINCT em.group_id) AS no_of_entities,
               SUM(em.matched_props)       AS no_of_matched_props,
               GROUP_CONCAT(DISTINCT em.entity_pk) AS entity_pks
        FROM entity_matches em
        JOIN group_requirements gr ON em.group_id = gr.group_id
        WHERE em.matched_props >= gr.required_props
        GROUP BY em.observation_id
        HAVING no_of_entities >= 2          -- e.g. for a 2-group query
        ORDER BY no_of_matched_props DESC

    Parameters
    ----------
    entities:
        Flat AND-group of entity clauses from the parsed EQL query.
    unmatched_entities:
        How many entity groups are allowed to be absent from the observation.
        E.g. ``unmatched_entities=1`` with a 2-group query requires only 1
        group to be satisfied (``no_of_entities >= 1``).
    unmatched_traits:
        Allow each group to miss up to this many of its required properties.
    start_date / end_date:
        Restrict property reads to writes in this time window.
    embeddings:
        Pre-computed query embeddings for ``~`` properties.  Build with
        ``StarrocksEntityPropertyAdapter._prepare_embeddings``.
    """
    plan = QueryPlan.from_entities(entities, unmatched_traits)
    no_of_entities = max(0, len(plan.all_groups) - unmatched_entities)
    preamble = _build_eql_preamble(plan, start_date, end_date, embeddings)
    return (
        preamble
        + "SELECT em.observation_id,"
        + "  COUNT(DISTINCT em.group_id) AS no_of_entities,"
        + "  SUM(em.matched_props) AS no_of_matched_props,"
        + "  GROUP_CONCAT(DISTINCT em.entity_pk) AS entity_pks,"
        + "  MAX(em.max_similarity) AS max_similarity"
        + "FROM entity_matches em"
        + "JOIN group_requirements gr ON em.group_id = gr.group_id"
        + "WHERE em.matched_props >= gr.required_props"
        + "GROUP BY em.observation_id"
        + f"HAVING no_of_entities >= {no_of_entities}"
        + "ORDER BY max_similarity DESC NULLS LAST, no_of_matched_props DESC"
    )

# TODO add limit to SQL
def build_select_observations_with_eql(
    entities: List[MetaLangEntityBase],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
) -> Sql:
    """Return a query that yields full observation records matching the EQL query.

    Compared to ``build_select_observation_will_all_entities``, this function
    adds a ``matching_entities`` CTE that consolidates qualified observations,
    then JOINs ``sys_obs`` to return the full observation metadata:
    id, timestamps, summary, description, entities JSON, match counters.

    Terminal CTE and SELECT:

    .. code-block:: sql

        matching_entities AS (
          SELECT em.observation_id,
                 COUNT(DISTINCT em.group_id) AS no_of_entities,
                 SUM(em.matched_props)       AS no_of_matched_props
          FROM entity_matches em
          JOIN group_requirements gr ON em.group_id = gr.group_id
          WHERE em.matched_props >= gr.required_props
          GROUP BY em.observation_id
          HAVING no_of_entities >= 2
        )
        SELECT o.id, o.metadata_time_insert, o.metadata_time_create,
               o.summary, o.description, o.entities,
               matched.no_of_entities, matched.no_of_matched_props
        FROM matching_entities AS matched
        JOIN testdb.sys_obs AS o ON o.id = matched.observation_id
        ORDER BY matched.no_of_matched_props DESC

    Parameters are the same as ``build_select_observation_will_all_entities``.
    """
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
        + "  SUM(em.matched_props) AS no_of_matched_props,"
        + "  MAX(em.max_similarity) AS max_similarity"
        + "FROM entity_matches em"
        + "JOIN group_requirements gr ON em.group_id = gr.group_id"
        + "WHERE em.matched_props >= gr.required_props"
        + "GROUP BY em.observation_id"
        + f"HAVING no_of_entities >= {no_of_entities})"
    )

    return (
        preamble + "," + matching_cte
        + "SELECT"
        + f"  o.{sys_obs | FlatObs.ID} AS id,"
        + f"  o.{sys_obs | FlatObs.METADATA_TIME_INSERT} AS metadata_time_insert,"
        + f"  o.{sys_obs | FlatObs.METADATA_TIME_CREATE} AS metadata_time_create,"
        + f"  o.{sys_obs | FlatObs.SUMMARY} AS summary,"
        + f"  o.{sys_obs | FlatObs.DESCRIPTION} AS description,"
        + f"  o.{sys_obs | FlatObs.LABEL} AS label,"
        + f"  o.{sys_obs | FlatObs.ENTITIES} AS entities,"
        + "  matched.no_of_entities, matched.no_of_matched_props, matched.max_similarity"
        + "FROM matching_entities AS matched"
        + f"JOIN {database}.{sys_obs} AS o ON o.{sys_obs | FlatObs.ID} = matched.observation_id"
        + "ORDER BY matched.max_similarity DESC NULLS LAST, matched.no_of_matched_props DESC"
    )


def build_select_expanded_entities_from_observations(
    entities: List[MetaLangEntityBase],
    entity_types: List[str],
    unmatched_entities: int = 0,
    unmatched_traits: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    embeddings: Optional[EmbeddingMap] = None,
    traits_source: str = "ent_state",
) -> Sql:
    """Return a query that yields entity state rows for entities inside qualifying observations.

    Use this when you need the full entity data, not just observation metadata.
    The query finds qualifying observations via the standard two-level aggregation,
    then collects ALL entities linked to those observations via ``sys_ent_2_obs``,
    and finally fetches traits according to ``traits_source``.

    Only entities whose ``entity_type`` appears in ``entity_types`` are returned.
    This lets callers request a subset (e.g. only ``["location", "person"]``) from
    an observation that may contain many more entity types.

    Parameters
    ----------
    traits_source:
        ``"ent_state"`` (default) — LEFT JOIN ``sys_ent_state`` for stitched,
        cross-observer traits.  Traits are NULL until the background stitching
        worker has run for a given entity.

        ``"property_state"`` — build traits inline from ``last_property_values``
        using ``TO_JSON(MAP_AGG(property_name, property_value))``.  Traits are
        available immediately after ingestion but reflect only the current
        observer window used by the preamble CTE.
    entity_types:
        Allowlist of entity types to include in the output.  Independent of
        the entity types in the EQL query.
    All other parameters are the same as ``build_select_observation_will_all_entities``.
    """
    plan = QueryPlan.from_entities(entities, unmatched_traits)
    no_of_entities = max(0, len(plan.all_groups) - unmatched_entities)
    preamble = _build_eql_preamble(plan, start_date, end_date, embeddings)

    database = current_bd_database_name()
    qualifying_ctes = _build_qualifying_observations_ctes(no_of_entities)

    if traits_source == "property_state":
        entity_props_agg_cte = (
            Sql()
            + "entity_props_agg AS ("
            + "SELECT lpv.entity_pk,"
            + "       TO_JSON(MAP_AGG(lpv.property_name, lpv.property_value)) AS traits"
            + "FROM last_property_values lpv"
            + "GROUP BY lpv.entity_pk)"
        )
        return (
            preamble + ","
            + qualifying_ctes + ","
            + entity_props_agg_cte
            + "SELECT"
            + "  a.observation_id,"
            + "  a.entity_pk,"
            + "  a.entity_type,"
            + "  NULL AS ts,"
            + "  epa.traits"
            + "FROM all_obs_entities a"
            + "LEFT JOIN entity_props_agg epa ON epa.entity_pk = a.entity_pk"
            + "WHERE a.entity_type IN :entity_types"
            + "ORDER BY a.observation_id, a.entity_type, a.entity_pk"
            + Param({"entity_types": tuple(entity_types)})
        )
    else:  # "ent_state"
        sys_ent_state_map = sys_ent_state()
        return (
            preamble + ","
            + qualifying_ctes
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
    """Return a query that counts distinct entity types across qualifying observations.

    Useful for building facet counts or exploring what co-occurs with the
    query predicates.  The query finds qualifying observations (same logic as
    the other functions) and then counts distinct entity types across all
    entities in those observations.

    Terminal section:

    .. code-block:: sql

        qualifying_observations AS ( ... ),
        all_obs_entities AS ( ... )
        SELECT entity_type, COUNT(*) AS count
        FROM all_obs_entities
        GROUP BY entity_type
        ORDER BY count DESC
        LIMIT 100

    The LIMIT 100 caps the facet list to the 100 most frequent entity types.

    Parameters are the same as ``build_select_observation_will_all_entities``.
    """
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
