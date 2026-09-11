from fastapi import APIRouter, Depends, HTTPException

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.log.errors import LogError
from airembr.system.command.log.event_logs import get_event_logs as get_event_logs_cmd
from airembr.system.command.log.node_logs import get_node_logs as get_node_logs_cmd
from airembr.system.command.log.flow_logs import get_flow_logs as get_flow_logs_cmd
from airembr.system.command.log.profile_logs import get_profile_logs as get_profile_logs_cmd
from airembr.system.command.log.log_alerts import get_log_alerts as get_log_alerts_cmd

router = APIRouter()


@router.get("/event/logs/{event_id}", tags=["log"], include_in_schema=sys_config.expose_gui_api)
async def get_event_logs(event_id: str, sort: str = None):
    """
    Returns event logs for event with given ID
    """

    try:
        return await get_event_logs_cmd(event_id, sort=sort)
    except LogError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/node/logs/{node_id}", tags=["log"],
            include_in_schema=sys_config.expose_gui_api)
async def get_node_logs(node_id: str, sort: str = None):
    """
    Returns node console log.
    """

    try:
        return await get_node_logs_cmd(node_id, sort=sort)
    except LogError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/flow/logs/{flow_id}", tags=["log"],
            include_in_schema=sys_config.expose_gui_api)
async def get_flow_logs(flow_id: str, sort: str = None):
    """
    Returns flow console log.
    """

    try:
        return await get_flow_logs_cmd(flow_id, sort=sort)
    except LogError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/profile/logs/{entity_id}", tags=["log"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def get_profile_logs(entity_id: str, sort: str = None):
    """
    Gets logs for profile with given ID (str)
    """

    try:
        return await get_profile_logs_cmd(entity_id, sort=sort)
    except LogError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/log/alerts", tags=["log"], include_in_schema=sys_config.expose_gui_api)
async def get_log_alerts():
    """
    Returns list of all Tracardi API logs counts.
    """
    try:
        return await get_log_alerts_cmd()
    except LogError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)
