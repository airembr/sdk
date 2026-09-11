from airembr.system.adapter.bigdata.big_data_adapter import bd_count_adapter, bd_metadata_adapter


async def count_online_resources() -> dict:
    observations_count, events_count, actor_types, actors_count = await bd_count_adapter.count_online_observations()
    return {
        "events": events_count,
        "observations": observations_count,
        "actors": actors_count,
        "actor_types": actor_types
    }


async def get_table_stats():
    return await bd_metadata_adapter.list_table_stats()
