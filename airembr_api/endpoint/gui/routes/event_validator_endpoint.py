from fastapi import APIRouter, Depends, HTTPException

from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.model.metadata.sys_evt_validation import EventValidator
from airembr.system.command.event_validation.errors import EventValidationError
from airembr.system.command.event_validation.validator import (
    load_validators as load_validators_cmd,
    add_validator as add_validator_cmd,
    delete_validator as delete_validator_cmd,
    get_validator as get_validator_cmd,
)

from airembr_api.endpoint.gui.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/event-configs", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api,
            response_model=dict)
# @router.get("/event-validator/list", tags=["validation"], include_in_schema=sys_config.expose_gui_api,
#             response_model=dict)
async def load_validators(limit: int = 100, query: str = None):
    validators, total = await load_validators_cmd(limit, query)

    return {
        "total": total,
        "grouped": {
            "Payload Validation": validators
        },
        "cache": memory_cache_config.event_validation_cache_ttl
    }


@router.post("/v2/event-config", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api)
# @router.post("/event-validator", tags=["validation"], include_in_schema=sys_config.expose_gui_api)
async def add_validator(data: EventValidator):
    await add_validator_cmd(data)
    return {"saved": True}


@router.delete("/v2/event-config/{id}", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api)
# @router.delete("/event-validator/{id}", tags=["validation"], include_in_schema=sys_config.expose_gui_api)
async def delete_validator(id: str):
    return await delete_validator_cmd(id)


@router.get("/v2/event-config/{id}", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api,
            response_model=EventValidator)
# @router.get("/event-validator/{id}", tags=["validation"], include_in_schema=sys_config.expose_gui_api,
#             response_model=EventValidator)
async def get_validator(id: str):
    try:
        return await get_validator_cmd(id)
    except EventValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
