from durable_dot_dict.dotdict import DotDict
from airembr_sdk.core.date import now_in_utc
from airembr.core.data.bulking import async_bulker
from airembr.system.process.logging.log_manager import save_logs
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.logging import extra_info

from airembr.system.adapter.metadata.mysql.service.task_service import background_log

from airembr.system.adapter.bigdata.big_data_adapter import bd_state_adapter

logger = get_logger(__file__)


async def stitch(context, database):
    async with background_log("Entity Stitching Worker", f"Stitching in {context}") as (bts, task_id):
        await bts.task_progress(task_id, 10)
        try:
            now = now_in_utc()
            async for batch in async_bulker(bd_state_adapter.yield_entities_to_update(), batch_size=5000):
                batch = [{
                    "entity_pk": entity_pk,
                    "traits": (DotDict(override_data=True) << traits).to_dict(),
                    "stitch_ts": stitch_ts,
                    "ts": now}
                    for entity_pk, traits, stitch_ts in batch]

                logger.info(f"Stitching {len(batch)} entities.")
                await bd_state_adapter.stream_entity_state(rows=batch)

        except Exception as e:
            logger.error(f"System worker error: {str(e)}",
                         extra=extra_info.build("System worker Worker", error_number='SW-0001'))
        finally:
            logger.info(f"Saving logs.")
            await save_logs()
            # Await to resolve async push to queue
