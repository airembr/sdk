from typing import Optional, Tuple

from sqlalchemy import Integer, func

from airembr.system.process.logging.log_handler import get_logger

from airembr.model.metadata.sys_setting import Setting
from airembr.system.adapter.metadata.mysql.mapping.setting_mapping import map_to_settings_table, map_to_setting
from airembr.system.adapter.metadata.mysql.schema.table import SettingTable

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context

logger = get_logger(__name__)


class SettingService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(SettingTable, search, limit, offset)

    async def load_by_id(self, setting_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(SettingTable, primary_id=setting_id)

    async def delete_by_id(self, setting_id: str) -> Tuple[bool, Optional[Setting]]:
        return await self.proxy.delete_by_id_in_deployment_mode(SettingTable, map_to_setting,
                                                                primary_id=setting_id)

    async def insert(self, setting: Setting):
        return await self.proxy.replace(SettingTable, map_to_settings_table(setting))

    async def load_new(self) -> SelectResult:

        where = where_tenant_and_mode_context(
            SettingTable,
            func.json_extract(SettingTable.config, '$.metric.new') == True,
            # SettingTable.config['metric']['new'].cast(Boolean) == True,
            SettingTable.enabled == True
        )

        return await self.proxy.select_in_deployment_mode(
            SettingTable,
            where=where)

    async def load_by_type(self, time_based: bool) -> SelectResult:
        if time_based:
            # All metrics that limit time - are time based.

            where = where_tenant_and_mode_context(
                SettingTable,
                func.json_extract(SettingTable.config, '$.metric.span').cast(Integer) != 0,
                # SettingTable.config['metric']['span'].cast(Integer) != 0,
                SettingTable.enabled == True
            )

        else:

            where = where_tenant_and_mode_context(
                SettingTable,
                func.json_extract(SettingTable.config, '$.metric.span').cast(Integer) == 0,
                # SettingTable.config['metric']['span'].cast(Integer) == 0,
                SettingTable.enabled == True
            )

        return await self.proxy.select_in_deployment_mode(
            SettingTable,
            where=where)
