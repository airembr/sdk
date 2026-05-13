import json
from datetime import datetime, timezone
from typing import List

from airembr_sdk.core.date import now_in_utc, add_utc_time_zone_if_none
from airembr.core.number.parser import try_number
from airembr.system.process.logging.log_handler import get_logger
from airembr.core.data.chunker import chunk_generator
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter

from airembr.system.adapter.bigdata.general.sql.pks_stitched_by_iid import sql_entities_that_changed, \
    sql_last_entity_state_change, sql_last_entity_property_change, sql_stitched_entities
from airembr.system.adapter.bigdata.general.utils.mapping import sys_ent_state

logger = get_logger(__name__)


class BdStateAdapter(AdapterRouter):

    async def stream_entity_state(self, rows):
        sys_ent_state_map = sys_ent_state()
        return await self.adapter.stream(rows, sys_ent_state_map)

    async def _load_entities_that_changed(self, since: datetime, till: datetime):
        sql = sql_entities_that_changed(since, till)
        result = await self.adapter.exec(sql)
        return [item['entity_pk'] for item in result]

    async def _get_last_entity_state_change(self) -> datetime:
        sql = sql_last_entity_state_change()
        result = await self.adapter.exec(sql)
        if result:
            result = result.first().column(0)
            if result:
                return result

        dt = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt

    async def _get_last_entity_property_change(self) -> datetime:
        sql = sql_last_entity_property_change()
        result = await self.adapter.exec(sql)
        if result:
            result = result.first().column(0)
            if result:
                return result
        return now_in_utc()

    async def _yield_a_chunk_of_entities_to_update(self, start: datetime, end: datetime, batch_size):

        # Now load the entities that changed there properties since last_entity_update
        entity_pks: List[str] = await self._load_entities_that_changed(since=start, till=end)

        for chunk in chunk_generator(entity_pks, batch_size, proceed_if=True):
            yield list(chunk)

    async def yield_entities_to_update(self):

        # From what time we need to update
        last_entity_update = await self._get_last_entity_state_change()

        # What is the latest property thaw we use. This closes the range of updates.
        last_property_update = await self._get_last_entity_property_change()


        last_entity_update = add_utc_time_zone_if_none(last_entity_update)
        last_property_update = add_utc_time_zone_if_none(last_property_update)

        now =  now_in_utc()

        if last_entity_update > now:
            last_entity_update = now

        if last_property_update > now:
            last_property_update = now

        logger.info (f"Selected stitching period from '{last_entity_update}' to '{last_property_update}' ({last_property_update-last_entity_update} seconds)")

        # For testing
        # last_property_update = now
        # dt = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        # dt = dt.replace(tzinfo=timezone.utc)
        # last_entity_update = dt

        if last_entity_update == last_property_update:
            logger.info("No entities to update.")
            return

        async for chunk in self._yield_a_chunk_of_entities_to_update(
                start=last_entity_update,
                end=last_property_update,
                batch_size=1000):

            sql = sql_stitched_entities(entity_pks=tuple(chunk))
            result = await self.adapter.exec(sql)
            for item in result:
                entity_pks = item['entity_pks']

                # Get traits
                traits = item.get('traits', '{}')
                try:
                    traits = json.loads(traits)
                except json.JSONDecodeError:
                    logger.error(f"Could not decode JSON for entity {entity_pks}.")
                    continue

                traits = {trait_name: try_number(trait_value) for trait_name, trait_value in traits.items()}

                for entity_pk in entity_pks.split(','):
                    yield entity_pk, traits, last_property_update
