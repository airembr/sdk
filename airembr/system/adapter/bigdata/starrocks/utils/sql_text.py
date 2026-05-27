from srd.domain.sql import Sql, Param
from airembr.model.bigdata.flat_text import FlatText
from airembr.model.bigdata.flat_ent_2_text import FlatEnt2Text
from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_mapping, sys_ent_2_text_mapping
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
    return (
            Sql()
            + "  SELECT COUNT(*) as count"
            + f"  FROM {database}.{sys_text}"
            + f"  WHERE {sys_text | FlatText.VECTOR} IS NULL"
    )


def load_not_embedded_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT *"
            + f"  FROM {database}.{sys_text}"
            + f"  WHERE {sys_text | FlatText.VECTOR} IS NULL"
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


def count_no_ner_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT COUNT(*) count"
            + f"  FROM {database}.{sys_text}"
            + f"  WHERE {sys_text | FlatText.REQUIRE_NER} = true AND {sys_text | FlatText.OBSERVATION_ID} IS NOT NULL"
    )


def load_no_ner_texts_sql():
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + "  SELECT *"
            + f"  FROM {database}.{sys_text}"
            + f"  WHERE {sys_text | FlatText.REQUIRE_NER} = true AND {sys_text | FlatText.OBSERVATION_ID} IS NOT NULL"
    )


def update_required_ner_texts_sql(text_id: str):
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    return (
            Sql()
            + f"UPDATE {database}.{sys_text}"
            + f"SET {sys_text | FlatText.REQUIRE_NER} = false"
            + f"  WHERE {sys_text | FlatText.ID} = :text_id"
            + Param({"text_id": text_id})
    )


def load_texts_by_entity_pk_sql(entity_pk: str):
    database = current_bd_database_name()
    sys_text = sys_text_mapping()
    sys_ent_2_text = sys_ent_2_text_mapping()
    return (
            Sql()
            + f"  SELECT t.*, e2t.{sys_ent_2_text | FlatEnt2Text.SOURCE_ID}, e2t.{sys_ent_2_text | FlatEnt2Text.ORIGIN}, e2t.{sys_ent_2_text | FlatEnt2Text.ENTITY_PK}"
            + f"  FROM {database}.{sys_ent_2_text} e2t"
            + f"  JOIN {database}.{sys_text} t ON e2t.{sys_ent_2_text | FlatEnt2Text.TEXT_ID} = t.{sys_text | FlatText.ID}"
            + f"  WHERE e2t.{sys_ent_2_text | FlatEnt2Text.ENTITY_PK} = :entity_pk"
            + f"  ORDER BY t.ts DESC"
            + Param({"entity_pk": entity_pk})
    )
