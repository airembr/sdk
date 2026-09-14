from airembr.system.adapter.bigdata.big_data_adapter import bd_event_adapter


async def get_event(event_id: str):
    return await bd_event_adapter.load_event_by_id(event_id)


async def delete_event(event_id: str):
    """
    Deletes event with given ID
    """
    return await bd_event_adapter.delete_event_from_db(event_id)
