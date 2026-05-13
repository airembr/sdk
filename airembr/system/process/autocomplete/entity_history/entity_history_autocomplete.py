from typing import Tuple

from airembr.system.adapter.bigdata.general.utils.mapping import entity_history_mapping
from airembr.system.process.autocomplete.primitive import values, columns
from airembr.system.process.autocomplete.autocomplete_service import AutocompleteService, Value


class EntityHistoryAutoComplete:

    def __init__(self):
        self.table_mapping = entity_history_mapping()

    async def columns(self):
        return columns(self.table_mapping)

    async def values(self, column, limit=100):
        return await values(self.table_mapping, column, limit)


async def entity_history_autocomplete(query) -> Tuple[list, Value]:
    ac = AutocompleteService(autocomplete=EntityHistoryAutoComplete())
    return await ac.autocomplete(query)