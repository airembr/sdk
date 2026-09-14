from fastapi import APIRouter, Depends, HTTPException

from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_evt_validation import EventValidator
from airembr.system.command.v1.errors.validator_errors import EventValidationError
from airembr.system.command.v1.meta.validator.validator import (
    add_validator as add_validator_cmd,
    delete_validator as delete_validator_cmd,
    get_validator as get_validator_cmd,
)

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.post("/v1/validator", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api)
async def save_validator(data: EventValidator):
    await add_validator_cmd(data)
    return {"saved": True}


@router.delete("/v1/validator/{id}", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api)
async def delete_validator_by_id(id: str):
    return await delete_validator_cmd(id)


@router.get("/v1/validator/{id}", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api,
            response_model=EventValidator)
async def get_validator_by_id(id: str):
    try:
        return await get_validator_cmd(id)
    except EventValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
