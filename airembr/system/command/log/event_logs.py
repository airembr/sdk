from typing import Optional

from airembr.system.adapter.bigdata.big_data_adapter import bd_log_adapter


async def get_event_logs(event_id: str, sort: Optional[str] = None) -> dict:
    records, total = await bd_log_adapter.load_logs_by_event(event_id, sort=sort)
    return {
        "result": records,
        "total": total
    }
