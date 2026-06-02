import json
import os.path
from typing import Generator

from srd.domain.table import Table
from srd.singleton import Singleton

from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.bigdata.starrocks.utils.sql_table_generator import generate_create_table_sql as sr_generate_create_table_sql
from airembr.system.config.sys_config import sys_config

_local_dir = os.path.dirname(__file__)
logger = get_logger(__name__)

class Resource(metaclass=Singleton):

    def __init__(self):

        self.system_tables = {
            "sys_evt": Table(name='sys_evt'),
            "sys_text": Table(name='sys_text'),
            "sys_text_vector": Table(name='sys_text_vector'),
            "sys_ent": Table(name='sys_ent'),
            "sys_evt_job": Table(name='sys_evt_job'),
            "sys_ent_history": Table(name='sys_ent_history'),
            "sys_ent_property": Table(name='sys_ent_property'),
            "sys_ent_property_state": Table(name='sys_ent_property_state'),
            "sys_ent_2_obs": Table(name='sys_ent_2_obs'),
            "sys_ent_state": Table(name='sys_ent_state'),
            "sys_log": Table(name='sys_log'),
            'sys_timer': Table(name='sys_timer'),
            'sys_obs_trigger': Table(name='sys_obs_trigger'),
            'sys_obs': Table(name='sys_obs'),
            'sys_obs_2_entity': Table(name='sys_obs_2_entity'),
            'sys_obs_2_obs': Table(name='sys_obs_2_obs'),
            "sys_ent_2_gid": Table(name='sys_ent_2_gid'),
            "sys_ent_2_text": Table(name='sys_ent_2_text'),
        }

        self.sql = [
            'sys_v_uniq_ent_traits',
            'sys_v_evt_ent',
            'sys_v_ent_state',
            'sys_v_ent_obs_state',
            'sys_v_ent_property_global_state'
        ]

    def get_tenant_table_names(self) -> Generator[str, None, None]:
        for table in self.system_tables.values():
            yield table.name

    def get_create_view_stmts(self, location: str):
        for sql in self.sql:
            file = os.path.join(_local_dir, f"sql/{location}/{sql}.sql")
            try:
                with open(file, "r") as fp:  # Save the JSON into schema.json or adjust the path
                    yield fp.read()
            except FileNotFoundError:
                logger.warning(f"No view {file}")

    def get_create_table_stmts(self):
        for system_table in self.system_tables:
            file = os.path.join(_local_dir, f"mapping/{system_table}.json")
            with open(file, "r") as fp:  # Save the JSON into schema.json or adjust the path
                schema = json.load(fp)
            if sys_config.big_data_adapter == 'starrocks':
                yield sr_generate_create_table_sql(schema)
            else:
                raise ValueError(f"Unknown adapter {sys_config.big_data_adapter}")
