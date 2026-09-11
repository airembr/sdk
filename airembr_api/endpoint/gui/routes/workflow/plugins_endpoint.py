from json import JSONDecodeError
from typing import Optional

from starlette.responses import JSONResponse
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.config.sys_config import sys_config
from dagor.domain.config_validation_payload import ConfigValidationPayload
from airembr.system.command.plugin.errors import PluginError
from airembr.system.command.plugin.plugin_helper import (
    call_plugin_helper as call_plugin_helper_cmd,
    check_plugin_configuration as check_plugin_configuration_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)

logger = get_logger(__name__)


def convert_errors(e: ValidationError):
    response = {}
    for error in e.errors():
        if 'loc' not in error or 'msg' not in error:
            continue
        field = ".".join(error['loc']) if isinstance(error['loc'], tuple) else error['loc']
        response[field] = error['msg'].capitalize()
    return response


@router.post("/plugin/{module}/{endpoint_function}", tags=["action"], include_in_schema=sys_config.expose_gui_api)
async def get_data_for_plugin(module: str, endpoint_function: str, request: Request):
    """
    Calls helper method from Endpoint class in plugin's module
    """

    try:
        try:
            body = await request.json()
        except JSONDecodeError:
            body = {}

        return await call_plugin_helper_cmd(module, endpoint_function, body)

    except PluginError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(convert_errors(e))
        )
    except AttributeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/plugin/{plugin_id}/config/validate", tags=["action"], include_in_schema=sys_config.expose_gui_api)
async def check_plugin_configuration(plugin_id: str,
                                        action_id: Optional[str] = "",  # TODO not used
                                        service_id: Optional[str] = "",
                                        config: ConfigValidationPayload = None):
    try:
        return await check_plugin_configuration_cmd(plugin_id, config)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
