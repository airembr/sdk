from typing import Optional

from airembr.system.adapter.bigdata.big_data_adapter import bd_log_adapter


async def get_node_logs(node_id: str, sort: Optional[str] = None) -> dict:
    records, total = await bd_log_adapter.load_logs_by_node(node_id, sort=sort)
    return {
        "result": records,
        "total": total
    }
