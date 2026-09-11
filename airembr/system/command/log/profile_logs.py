from typing import Optional

from airembr.system.adapter.bigdata.big_data_adapter import bd_log_adapter


async def get_profile_logs(entity_id: str, sort: Optional[str] = None) -> dict:
    records, total = await bd_log_adapter.load_logs_by_profile(entity_id, sort=sort)
    return {
        "result": list(records),
        "total": total
    }
