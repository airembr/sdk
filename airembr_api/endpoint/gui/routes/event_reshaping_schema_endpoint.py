from typing import Optional

from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from fastapi import APIRouter, Depends, HTTPException
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema
from airembr.system.command.event_reshaping.errors import EventReshapingError
from airembr.system.command.event_reshaping.reshaping_schema import (
    add_reshape_schema as add_reshape_schema_cmd,
    delete_reshape_schema as delete_reshape_schema_cmd,
    get_reshape_schema as get_reshape_schema_cmd,
    get_reshape_schemas_by_event_type as get_reshape_schemas_by_event_type_cmd,
    load_reshape_schemas as load_reshape_schemas_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.post("/event-reshape-schema", tags=["reshaping"], include_in_schema=sys_config.expose_gui_api,
             response_model=dict)
async def add_reshape_schema(data: EventReshapingSchema):
    """
    Adds new event reshaping schema.
    """
    await add_reshape_schema_cmd(data)
    return {"saved": True}


@router.delete("/event-reshape-schema/{id}", tags=["reshaping"], include_in_schema=sys_config.expose_gui_api)
async def delete_reshape_schema(id: str):
    """
    Deletes event reshaping schema.
    """
    return await delete_reshape_schema_cmd(id)


@router.get("/event-reshape-schema/{id}", tags=["reshaping"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=Optional[EventReshapingSchema])
async def get_reshape_schema(id: str):
    try:
        return await get_reshape_schema_cmd(id)
    except EventReshapingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/event-reshape-schemas/by_type/{event_type}", tags=["reshaping"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=dict)
async def get_reshape_schemas_by_event_type(event_type: str, only_enabled: bool = True):
    try:
        records, total = await get_reshape_schemas_by_event_type_cmd(event_type, only_enabled)
    except EventReshapingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return {
        "total": total,
        "result": records
    }


@router.get("/event-reshape-schema", tags=["reshaping"], include_in_schema=sys_config.expose_gui_api, response_model=dict)
async def load_reshape_schemas(limit: Optional[int] = 100, query: Optional[str] = None):
    records, total = await load_reshape_schemas_cmd(limit, query)
    return {
        "total": total,
        "grouped": {
            "Payload Reshaping": records
        },
        "cache": memory_cache_config.event_reshaping_cache_ttl
    }
