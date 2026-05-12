from datetime import datetime
from typing import List

from srd.domain.sql import Sql, Param

from airembr.model.bigdata.flat_ent_2_gid import FlatEntity2Gid
from airembr.system.adapter.bigdata.general.utils.mapping import sys_ent_2_gid, sys_ent_property_state, sys_ent_state
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


def sql_pks_stitched_by_iid_for_pk(entity_pk: str) -> Sql:
    """
    This SQL returns all pks that are stitched by iid.
    You will get all ordinary PK that map to the same entity.
    """
    _sys_ent_2_gid = sys_ent_2_gid()

    database = current_bd_database_name()
    return (
            Sql()
            + f"SELECT {_sys_ent_2_gid | FlatEntity2Gid.ENTITY_PK}, {_sys_ent_2_gid | FlatEntity2Gid.ENTITY_GID}"
            + f" FROM {database}.{_sys_ent_2_gid}"
            + f"WHERE {_sys_ent_2_gid | FlatEntity2Gid.ENTITY_GID} IN ("
            + f" SELECT entity_gid FROM {database}.{_sys_ent_2_gid}"
            + f"  WHERE entity_pk = :entity_pk)" + Param({"entity_pk": entity_pk})
    )


def sql_entities_for_stitching(entity_pks: List[str]) -> Sql:
    database = current_bd_database_name()
    sys_ent_property_state_map = sys_ent_property_state()
    sys_ent_2_gid_map = sys_ent_2_gid()

    eps = f"{database}.{sys_ent_property_state_map}"
    egid = f"{database}.{sys_ent_2_gid_map}"

    return (
        Sql()
        + " SELECT COALESCE(egid.entity_gid, eps.entity_pk) as gid, "
        + "        eps.entity_type AS entity_type, "
        + "        eps.entity_pk AS entity_pk, "
        + "        eps.property_name AS property_name, "
        + "        eps.property_value AS property_value, "
        + "        eps.property_text AS property_text, "
        + "        eps.property_number AS property_number, "
        + "        eps.observer_pk AS observer_pk, "
        + "        eps.ts AS ts "
        + f" FROM {eps} AS eps "
        + f" LEFT JOIN {egid} AS egid ON eps.entity_pk = egid.entity_pk"
        + " WHERE eps.entity_pk IN :entity_pks" + Param({"entity_pks": tuple(entity_pks)})
    )


def sql_latest_props(view: str) -> Sql:
    return (
            Sql()
            + " SELECT gid, property_name, MAX_BY(property_value, ts) AS last_property_value "
            + f" FROM {view} "
            + " GROUP BY gid, property_name"
    )

def sql_last_entity_state_change() -> Sql:
    database = current_bd_database_name()
    sys_ent_state_map = sys_ent_state()
    return (
            Sql()
            + " SELECT MAX(stitch_ts) AS last_entity_change "
            + f" FROM {database}.{sys_ent_state_map}"
    )

def sql_last_entity_property_change() -> Sql:
    database = current_bd_database_name()
    sys_ent_property_state_map = sys_ent_property_state()
    return (
            Sql()
            + " SELECT MAX(ts) AS last_property_change "
            + f" FROM {database}.{sys_ent_property_state_map}"
    )

def sql_entities_that_changed(since: datetime, till:datetime) -> Sql:
    database = current_bd_database_name()
    sys_ent_property_state_map = sys_ent_property_state()
    return (
            Sql()
            + " SELECT DISTINCT entity_pk"
            + f" FROM {database}.{sys_ent_property_state_map}"
            + f" WHERE ts > :since AND ts <= :till" + Param({"since": since, "till": till})
    )

def sql_stitched_entities(entity_pks) -> Sql:
    return (
            Sql()
            + "WITH ents_for_stitching AS ("
            + sql_entities_for_stitching(entity_pks)
            + "), "
            + "latest_props AS ("
            + sql_latest_props("ents_for_stitching")
            + ") "
            + "SELECT stitch.gid, "
            + "       GROUP_CONCAT(DISTINCT stitch.entity_pk) AS entity_pks, "
            + "       TO_JSON(MAP_AGG(lp.property_name, lp.last_property_value)) AS traits "
            + "FROM ents_for_stitching stitch "
            + "JOIN latest_props lp ON stitch.gid = lp.gid "
            + "GROUP BY stitch.gid"
    )