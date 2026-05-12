from typing import List, Optional

from durable_dot_dict.dotdict import DotDict

from airembr.system.adapter.bigdata.general.bd_entity_property_state_adapter import BdEntityPropertyStateAdapter
from airembr.system.adapter.bigdata.general.utils.mapping import entity_history_mapping

_ent_history_mapping = entity_history_mapping()


class StarrocksEntityPropertyStateAdapter(BdEntityPropertyStateAdapter):

    async def load_entity_state_by_entity_pk(self, entity_pk, observer_pk: Optional[str] = None):
        result = await self.load_entity_property_state_by_entity_pk(entity_pk, observer_pk)
        object = {}
        for item in result:
            object[item['name']] = item['value']
        return DotDict() << object

    async def load_entity_state_by_entity_pks(self, entity_pks: List[str], observer_pk: Optional[str] = None):
        result = await self.load_entity_property_state_by_entity_pks(entity_pks, observer_pk)
        object = {}
        for item in result:
            object[item['name']] = item['value']
        return DotDict() << object

    async def load_entity_state_by_entity_iid(self, entity_iids: List[str], observer_pk: Optional[str] = None):
        result = await self.load_entity_property_state_by_entity_iid(entity_iids, observer_pk)
        object = {}
        for item in result:
            object[item['name']] = item['value']
        return DotDict() << object
