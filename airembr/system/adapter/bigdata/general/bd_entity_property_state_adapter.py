from typing import Set, Tuple, Optional, List

from airembr.model.bigdata.flat_ent_property_state import FlatEntityPropertyState

from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import sys_ent_property_state


class BdEntityPropertyStateAdapter(AdapterRouter):

    async def load_entity_property_state_by_entity_pk(self, entity_pk: str, observer_pk: Optional[str] = None) -> Set[
        Tuple[str, str]]:
        sys_ent_property_state_map = sys_ent_property_state()
        database = current_bd_database_name()
        name_col = sys_ent_property_state_map | FlatEntityPropertyState.NAME
        value_col = sys_ent_property_state_map | FlatEntityPropertyState.VALUE
        entity_pk_col = sys_ent_property_state_map | FlatEntityPropertyState.ENTITY_PK
        observer_pk_col = sys_ent_property_state_map | FlatEntityPropertyState.OBSERVER_PK
        ts_col = sys_ent_property_state_map | FlatEntityPropertyState.TS

        sql = (
                Sql()
                + f"SELECT * "
                + f"FROM {database}.{sys_ent_property_state_map}"
                + f"WHERE {entity_pk_col} = :entity_pk" + Param({"entity_pk": entity_pk})
                + (bool(observer_pk), f" AND {observer_pk_col} = :observer_pk", Param({"observer_pk": observer_pk}))
                + f"ORDER BY {ts_col} ASC"
        )

        result = await self.adapter.exec(sql)
        return result >> {
            "name": name_col,
            "value": value_col,
        }

    async def load_entity_property_state_by_entity_pks(self, entity_pks: List[str],
                                                       observer_pk: Optional[str] = None) -> Set[
        Tuple[str, str]]:
        sys_ent_property_state_map = sys_ent_property_state()
        database = current_bd_database_name()
        name_col = sys_ent_property_state_map | FlatEntityPropertyState.NAME
        value_col = sys_ent_property_state_map | FlatEntityPropertyState.VALUE
        entity_pk_col = sys_ent_property_state_map | FlatEntityPropertyState.ENTITY_PK
        observer_pk_col = sys_ent_property_state_map | FlatEntityPropertyState.OBSERVER_PK
        ts_col = sys_ent_property_state_map | FlatEntityPropertyState.TS

        sql = (
                Sql()
                + f"SELECT * "
                + f"FROM {database}.{sys_ent_property_state_map}"
                + f"WHERE {entity_pk_col} IN :entity_pks" + Param({"entity_pks": tuple(entity_pks)})
                + (bool(observer_pk), f" AND {observer_pk_col} = :observer_pk", Param({"observer_pk": observer_pk}))
                + f"ORDER BY {ts_col} ASC"
        )

        result = await self.adapter.exec(sql)
        return result >> {
            "name": name_col,
            "value": value_col,
        }

    async def load_entity_property_state_by_entity_iid(self, entity_iid: List[str], observer_pk: Optional[str] = None) -> Set[
        Tuple[str, str]]:
        sys_v_ent_property_global_state = 'sys_v_ent_property_global_state'  # No mapping for views
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT * "
                + f"FROM {database}.{sys_v_ent_property_global_state}"
                + f"WHERE entity_iid IN :entity_iid" + Param({"entity_iid": tuple(entity_iid)})
                + (bool(observer_pk), f" AND observer_pk = :observer_pk", Param({"observer_pk": observer_pk}))
                + f"ORDER BY ts ASC"
        )

        result = await self.adapter.exec(sql)

        return result >> {
            "name": "property_name",
            "value": "property_value",
        }
