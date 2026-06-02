import os.path
from typing import Optional, List, LiteralString

from srd.domain.record_mapping import EntityToTableMapping, ObjectPropertyMapping

from airembr.system.decorator.run_once import run_once
from airembr.core.file.file import read_json
from airembr.model.entity_object import EntityPropertyPayload
from airembr.system.config.sys_config import sys_config
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name

from airembr.system.adapter.metadata.mysql.service.entity_object_service import EntityObjectService
from airembr.system.adapter.metadata.mysql.interface import entity_object_dao

_local_dir = os.path.dirname(__file__)
eos = EntityObjectService()

_schema_dir = '../../../../schema/mapping'

def _read_mapping_records(file_path: LiteralString | str | bytes) -> EntityToTableMapping:
    """
    Reads a JSON file that is a list of record definitions and converts
    them into a list of RecordMapping objects.
    """
    data = read_json(file_path)

    column_type_location = sys_config.db_adapter_column_type()

    for row in data.get('columns',[]):
        row['column_type'] = row[column_type_location]

    # Expecting a list of dictionaries
    return EntityToTableMapping(**data)


def _get_property_mapping(entity_payload_properties: List[EntityPropertyPayload]):
    for property in entity_payload_properties:
        if property.column is None:
            continue
        column, column_type = property.column.split('|')
        yield ObjectPropertyMapping(
            property=property.name,
            column=column,
            column_type=column_type,
            default_value=property.default_value
        )


async def get_entity_mapping(entity_type: str) -> Optional[EntityToTableMapping]:
    entity_payload = await entity_object_dao.load_entity_object_by_type(entity_type)
    if not entity_payload or not entity_payload.table:
        return None

    return EntityToTableMapping(
        database=current_bd_database_name(),
        table=entity_payload.table,
        columns=list(_get_property_mapping(entity_payload.properties))
    )


# System
@run_once
def event_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_evt.json'))

@run_once
def sys_observation_trigger() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_obs_trigger.json'))


@run_once
def sys_obs_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_obs.json'))

@run_once
def observation_2_entity_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_obs_2_entity.json'))

@run_once
def event_job_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_evt_job.json'))

@run_once
def entity_history_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir,f'{_schema_dir}/sys_ent_history.json'))

@run_once
def entity_property() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir,f'{_schema_dir}/sys_ent_property.json'))

@run_once
def sys_ent_property_state() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir,f'{_schema_dir}/sys_ent_property_state.json'))

@run_once
def sys_ent_2_obs() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir,f'{_schema_dir}/sys_ent_2_obs.json'))

@run_once
def sys_ent_2_gid() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir,f'{_schema_dir}/sys_ent_2_gid.json'))

@run_once
def sys_ent_state() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir,f'{_schema_dir}/sys_ent_state.json'))

@run_once
def log_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_log.json'))

@run_once
def sys_timer_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_timer.json'))

@run_once
def sys_text_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_text.json'))

@run_once
def sys_text_vector_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_text_vector.json'))


@run_once
def sys_ent_2_text_mapping() -> EntityToTableMapping:
    return _read_mapping_records(os.path.join(_local_dir, f'{_schema_dir}/sys_ent_2_text.json'))
