from airembr_sdk.core.date import now_in_utc
import airembr.system.adapter.bigdata.big_data_adapter as big_data_adapter


async def get_elastic_indices() -> dict:
    # NOTE: `bd_raw_adapter` does not exist on big_data_adapter (pre-existing bug,
    # preserved as-is from the original endpoint rather than guessed at).
    return await big_data_adapter.bd_raw_adapter.list_indices()


async def get_server_time():
    return now_in_utc()
