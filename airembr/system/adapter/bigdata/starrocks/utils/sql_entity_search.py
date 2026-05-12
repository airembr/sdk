from typing import Optional, Tuple, List
from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import entity_property
from airembr.model.bigdata.flat_ent_property import FlatEntityProperty


def _compose_properties(entity_properties: List[Tuple[str, str]]):
    sys_ent_property = entity_property()
    for key, value in entity_properties:
        if key.lower() == "$id":
            # (prop.property_name = "id" AND prop.entity_id = "28589d3458887ca438f772c573b96af6")
            yield  f'prop.entity_id = "{value}"'
        elif key.lower() == "$pk":
            # (prop.property_name = "id" AND prop.entity_id = "28589d3458887ca438f772c573b96af6")
            yield  f'prop.entity_pk = "{value}"'
        elif isinstance(value, (int, float)):
            yield f'(prop.{sys_ent_property | FlatEntityProperty.NAME} = "{key}" AND prop.{sys_ent_property | FlatEntityProperty.NUMBER} = "{value}")'
        else:
            yield f'(prop.{sys_ent_property | FlatEntityProperty.NAME} = "{key}" AND LOWER(prop.{sys_ent_property | FlatEntityProperty.TEXT}) = "{value.lower()}")'


def _query_1(entity_type, entity_properties, observer_pk):
    if bool(entity_type) and bool(entity_properties) and bool(observer_pk):
        sql = (
                Sql()
                + "prop.entity_type = :entity_type" + Param({"entity_type": entity_type})
                + f"AND ({' OR '.join(_compose_properties(entity_properties))})"
                + f"AND prop.observer_pk = :observer_pk" + Param({"observer_pk": observer_pk})
        )
    elif bool(entity_type) and bool(observer_pk):
        sql = (
                Sql()
                + "prop.entity_type = :entity_type" + Param({"entity_type": entity_type})
                + f"AND prop.observer_pk = :observer_pk" + Param({"observer_pk": observer_pk})
        )
    elif bool(observer_pk):
        sql = (
                Sql()
                + "prop.observer_pk = :observer_pk" + Param({"observer_pk": observer_pk})
        )
    elif bool(entity_type) and bool(entity_properties):
        sql = (
                Sql()
                + f"prop.entity_type = :entity_type AND ({' OR '.join(_compose_properties(entity_properties))})" + Param(
            {"entity_type": entity_type})
        )
    elif bool(entity_type):
        sql = (
                Sql()
                + "prop.entity_type = :entity_type" + Param({"entity_type": entity_type})
        )
    elif bool(entity_properties):
        sql = (
                Sql()
                + f"{' OR '.join(_compose_properties(entity_properties))}"
        )
    else:
        sql = None

    return sql


def sql_entity_by_properties(entity_properties: List[Tuple[str, str]],
                             entity_type: Optional[str] = None,
                             observer_pk: Optional[str] = None):
    database = current_bd_database_name()
    sys_ent_property = entity_property()

    sql = (
            Sql()
            + "WITH queried_entity_properties AS ("
            + f"SELECT {sys_ent_property | FlatEntityProperty.PK} AS entity_pk, "
            + f"{sys_ent_property | FlatEntityProperty.TYPE} AS entity_type, "
         + "COUNT(*) as count"
            + f"FROM {database}.{sys_ent_property} AS prop"
    )

    if bool(entity_type) or bool(entity_properties) or (bool(observer_pk)):
        sql += Sql("WHERE")
        _sub_query = _query_1(entity_type, entity_properties, observer_pk)
        if _sub_query:
            sql += _sub_query

    sql += (
            Sql()
            + f"GROUP BY prop.{sys_ent_property | FlatEntityProperty.PK}, prop.{sys_ent_property | FlatEntityProperty.TYPE}"
            + ")"  # With end
    )
    return sql


def sql_entities_by_properties(entity_queries: List[Tuple[str, List[Tuple[str, str]]]],
                               observer_pk: Optional[str] = None):
    sys_ent_property = entity_property()
    database = current_bd_database_name()
    sql = (
            Sql()
            + "WITH queried_entity_properties AS ("
            + f"SELECT {sys_ent_property | FlatEntityProperty.PK} AS entity_pk, "
              f"{sys_ent_property | FlatEntityProperty.TYPE} AS entity_type, "
              "COUNT(*) as count"
            + f"FROM {database}.{sys_ent_property} AS prop"
    )

    if bool(entity_queries):
        sql += Sql("WHERE")
        _ents = []
        for entity_type, entity_properties in entity_queries:
            _sub_sql = _query_1(entity_type, entity_properties, observer_pk)
            if _sub_sql:
                _ents.append(f"({_sub_sql.literal()})")

        sql += " OR ".join(_ents)

        sql += f"GROUP BY prop.{sys_ent_property | FlatEntityProperty.PK}, prop.{sys_ent_property | FlatEntityProperty.TYPE}"
        sql += ")"  # With end
