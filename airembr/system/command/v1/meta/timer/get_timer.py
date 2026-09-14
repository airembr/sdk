from typing import Optional

from srd.domain.result import Row
from airembr.system.adapter.bigdata.big_data_adapter import bd_timer_adapter


async def get_timer(timer_id: str) -> Optional[Row]:
    return await bd_timer_adapter.load_timer(timer_id)
