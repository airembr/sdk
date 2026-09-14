from typing import Optional

from airembr.system.config.sys_config import sys_config
from fastapi import APIRouter, Depends, HTTPException
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema
from airembr.system.command.v1.errors.reshaping_schema_errors import EventReshapingError
from airembr.system.command.v1.meta.reshaping_schema.reshaping_schema import (
    add_reshape_schema as add_reshape_schema_cmd,
    delete_reshape_schema as delete_reshape_schema_cmd,
    get_reshape_schema as get_reshape_schema_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.post("/v1/reshaping-schema", tags=["reshaping"], include_in_schema=sys_config.expose_gui_api,
             response_model=dict)
async def save_reshaping_schema(data: EventReshapingSchema):
    """
    Adds new event reshaping schema.
    """
    await add_reshape_schema_cmd(data)
    return {"saved": True}


@router.delete("/v1/reshaping-schema/{id}", tags=["reshaping"], include_in_schema=sys_config.expose_gui_api)
async def delete_reshaping_schema_by_id(id: str):
    """
    Deletes event reshaping schema.
    """
    return await delete_reshape_schema_cmd(id)


@router.get("/v1/reshaping-schema/{id}", tags=["reshaping"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=Optional[EventReshapingSchema])
async def get_reshaping_schema_by_id(id: str):
    try:
        return await get_reshape_schema_cmd(id)
    except EventReshapingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
