from json import JSONDecodeError
from fastapi import APIRouter, Request, HTTPException

from airembr_api.service import state
from airembr.system.config.sys_config import sys_config
from airembr.model.system.context import get_context

router = APIRouter()


@router.get("/ping", tags=["health"], include_in_schema=sys_config.expose_gui_api)
async def get_healthcheck():
    if state.server_ready:
        return 'pong'
    raise HTTPException(
        status_code=404, detail="Not ready."
    )

@router.get("/healthcheck", tags=["health"], include_in_schema=sys_config.expose_gui_api)
async def get_healthcheck(r: Request):
    """
       Enables you to see if API responds to HTTP GET requests
    """

    context = get_context()

    if state.server_ready:
        return {
            "headers": r.headers,
            "context": context.dict(without_user=True)
        }
    raise HTTPException(
        status_code=404, detail="Not ready."
    )

