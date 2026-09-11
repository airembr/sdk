from airembr.system.adapter.bigdata.big_data_adapter import bd_log_adapter


async def get_log_alerts() -> dict:
    return await bd_log_adapter.aggr_group_logs_by_level()
