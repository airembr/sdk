from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema
from airembr.system.adapter.metadata.mysql.interface import event_reshaping_dao
from airembr.system.command.v1.errors.reshaping_schema_errors import EventReshapingError


async def add_reshape_schema(data: EventReshapingSchema):
    await event_reshaping_dao.insert_event_reshaping(data)


async def delete_reshape_schema(reshaping_id: str):
    return await event_reshaping_dao.delete_event_reshaping_by_id(reshaping_id)


async def get_reshape_schema(reshaping_id: str) -> EventReshapingSchema:
    record = await event_reshaping_dao.load_event_reshaping_by_id(reshaping_id)
    if not record:
        raise EventReshapingError(f"No event reshaping with ID {reshaping_id} found.", 404)
    return record
