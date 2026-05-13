from typing import Tuple

from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping
from airembr.system.process.autocomplete.primitive import values, columns
from airembr.system.process.autocomplete.autocomplete_service import AutocompleteService, Value


class FactAutoComplete:

    def __init__(self):
        self.table_mapping = event_mapping()

    async def columns(self):
        return columns(self.table_mapping)

    async def values(self, column, limit=100):
        return await values(self.table_mapping, column, limit)


async def fact_autocomplete(query) -> Tuple[list, Value]:
    ac = AutocompleteService(autocomplete=FactAutoComplete())
    return await ac.autocomplete(query)
