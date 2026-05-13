from typing import Tuple

from airembr.system.adapter.bigdata.general.utils.mapping import sys_obs_mapping
from airembr.system.process.autocomplete.primitive import values, columns
from airembr.system.process.autocomplete.autocomplete_service import AutocompleteService, Value


class ObservationAutoComplete:

    def __init__(self):
        self.table_mapping = sys_obs_mapping()

    async def columns(self):
        return columns(self.table_mapping)

    async def values(self, column, limit=100):
        return await values(self.table_mapping, column, limit)

async def observation_autocomplete(query) -> Tuple[list, Value]:
    ac = AutocompleteService(autocomplete=ObservationAutoComplete())
    return await ac.autocomplete(query)