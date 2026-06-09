from typing import List

from airembr.model.bigdata.flat_text_vector import FlatTextVector
from srd.domain.sql import Sql, Param
from airembr.model.bigdata.flat_text import FlatText
from airembr.model.bigdata.flat_ent_2_text import FlatEnt2Text
from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_mapping, sys_ent_2_text_mapping, \
    sys_text_vector_mapping, entity_property
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


def load_all_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT *"
            + f"  FROM {database}.{sys_text}"
    )


def count_not_embedded_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    sys_text_vector = sys_text_vector_mapping()
    return (
            Sql()
            + "  SELECT COUNT(*) as count"
            + f"  FROM {database}.{sys_text}"
            + f"  LEFT JOIN {database}.{sys_text_vector} v ON {sys_text | FlatText.ID} = {sys_text_vector | FlatTextVector.TEXT_ID}"
            + f"  WHERE v.{sys_text_vector | FlatTextVector.VECTOR} IS NULL"
    )


def load_not_embedded_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    sys_text_vector = sys_text_vector_mapping()
    return (
            Sql()
            + f"  SELECT {sys_text | FlatText.ID} as id, {sys_text | FlatText.TEXT} as text_string"
            + f"  FROM {database}.{sys_text}"
            + f"  LEFT JOIN {database}.{sys_text_vector} v ON {sys_text | FlatText.ID} = {sys_text_vector | FlatTextVector.TEXT_ID}"
            + f"  WHERE v.{sys_text_vector | FlatTextVector.VECTOR} IS NULL"
    )


def count_texts_by_source_sql(source_id: str):
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT COUNT(*) as count"
            + f"  FROM {database}.{sys_text}"
            + f"  WHERE {sys_text | FlatText.SOURCE_ID} = :source_id"
            + Param({"source_id": source_id})
    )


def load_texts_by_source_sql(source_id: str, start: int = 0, limit: int = 10000):
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT *"
            + f"  FROM {database}.{sys_text}"
            + f"  WHERE {sys_text | FlatText.SOURCE_ID} = :source_id"
            + Param({"source_id": source_id})
            + f"  LIMIT :start, :limit"
            + Param({"start": start, "limit": limit})
    )


def load_not_summarized_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT root.*, parent.id as ref_id"
            + f"  FROM {database}.{sys_text} root"
            + f"  LEFT JOIN {database}.{sys_text} parent ON parent.{sys_text | FlatText.PARENT_ID} = root.{sys_text | FlatText.ID}"
            + f"  WHERE root.{sys_text | FlatText.PARENT_ID} IS NULL AND parent.{sys_text | FlatText.ID} IS NULL"
    )


def count_not_summarized_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT COUNT(*) as count"
            + f"  FROM {database}.{sys_text} root"
            + f"  LEFT JOIN {database}.{sys_text} parent ON parent.{sys_text | FlatText.PARENT_ID} = root.{sys_text | FlatText.ID}"
            + f"  WHERE root.{sys_text | FlatText.PARENT_ID} IS NULL AND parent.{sys_text | FlatText.ID} IS NULL"
    )


def count_to_ner_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    sys_text_vector = sys_text_vector_mapping()
    return (
            Sql()
            + "  SELECT COUNT(*) count"
            + f"  FROM {database}.{sys_text} t"
            + f"   LEFT JOIN {database}.{sys_text_vector} as v ON v.{sys_text_vector | FlatTextVector.TEXT_ID} = t.{sys_text | FlatText.ID}"
            + f"  WHERE t.{sys_text | FlatText.REQUIRE_NER} = true AND t.{sys_text | FlatText.MODEL} IS NULL AND t.{sys_text | FlatText.OBSERVATION_ID} IS NOT NULL"
    )


def load_to_ner_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    sys_text_vector = sys_text_vector_mapping()

    return (
            Sql()
            + "  SELECT *"
            + f"  FROM {database}.{sys_text} t"
            + f"   LEFT JOIN {database}.{sys_text_vector} as v ON v.{sys_text_vector | FlatTextVector.TEXT_ID} = t.{sys_text | FlatText.ID}"
            + f"  WHERE t.{sys_text | FlatText.REQUIRE_NER} = true AND t.{sys_text | FlatText.MODEL} IS NULL AND t.{sys_text | FlatText.OBSERVATION_ID} IS NOT NULL"
    )


def update_required_ner_texts_sql(text_id: str, model: str):
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + f"UPDATE {database}.{sys_text}"
            + f"SET {sys_text | FlatText.REQUIRE_NER} = false, {sys_text | FlatText.MODEL} = :model"
            + f"  WHERE {sys_text | FlatText.ID} = :text_id"
            + Param({"text_id": text_id, "model":model})
    )


def similar_texts_sql(query_vector: List[float], limit: int = 10):
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    sys_text_vector = sys_text_vector_mapping()
    vector_str = f"[{', '.join(str(float(v)) for v in query_vector)}]"
    return (
            Sql()
            + f"  SELECT v.{sys_text_vector | FlatTextVector.TEXT_ID} AS text_id,"
            + f"         t.{sys_text | FlatText.TEXT} AS text_string,"
            + f"         approx_l2_distance(v.{sys_text_vector | FlatTextVector.VECTOR}, {vector_str}) AS distance"
            + f"  FROM {database}.{sys_text_vector} v"
            + f"  JOIN {database}.{sys_text} t ON v.{sys_text_vector | FlatTextVector.TEXT_ID} = t.{sys_text | FlatText.ID}"
            + f"  ORDER BY approx_l2_distance(v.{sys_text_vector | FlatTextVector.VECTOR}, {vector_str})"
            + f"  LIMIT :limit"
            + Param({"limit": limit})
    )


def count_not_embedded_property_values_sql():
    database = current_bd_database_name()
    sys_ent_property = entity_property()
    sys_text_vector = sys_text_vector_mapping()
    return (
            Sql()
            + "  SELECT COUNT(DISTINCT p.property_value_id) as count"
            + f"  FROM {database}.{sys_ent_property} p"
            + f"  LEFT JOIN {database}.{sys_text_vector} v ON p.property_value_id = v.{sys_text_vector | FlatTextVector.TEXT_ID}"
            + "  WHERE p.property_value_id IS NOT NULL"
            + f"  AND v.{sys_text_vector | FlatTextVector.VECTOR} IS NULL"
    )


def load_not_embedded_property_values_sql():
    database = current_bd_database_name()
    sys_ent_property = entity_property()
    sys_text_vector = sys_text_vector_mapping()
    return (
            Sql()
            + "  SELECT DISTINCT p.property_value_id as id, p.property_value as text_string"
            + f"  FROM {database}.{sys_ent_property} p"
            + f"  LEFT JOIN {database}.{sys_text_vector} v ON p.property_value_id = v.{sys_text_vector | FlatTextVector.TEXT_ID}"
            + "  WHERE p.property_value_id IS NOT NULL"
            + f"  AND v.{sys_text_vector | FlatTextVector.VECTOR} IS NULL"
    )
