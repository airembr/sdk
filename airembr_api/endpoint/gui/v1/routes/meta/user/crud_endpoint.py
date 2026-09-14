from fastapi import APIRouter, Depends, HTTPException, Response

from typing import Union

from airembr.model.metadata.sys_user import User
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.user_payload import UserPayload
from airembr.system.command.v1.errors.user_errors import UserError
from airembr.system.command.v1.meta.user.preferences import (
    get_user_preference as get_user_preference_cmd,
    set_user_preference as set_user_preference_cmd,
    delete_user_preference as delete_user_preference_cmd,
)
from airembr.system.command.v1.meta.user.add_user import add_user as add_user_cmd
from airembr.system.command.v1.meta.user.delete_user import delete_user as delete_user_cmd
from airembr.system.command.v1.meta.user.get_user import get_user as get_user_cmd
from airembr.system.command.v1.meta.user.edit_user import edit_user as edit_user_cmd
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin"]))]
)


@router.get("/v1/user-preference/{key}", tags=["v1/user"], include_in_schema=sys_config.expose_gui_api)
@router.get("/user/preference/{key}", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def get_user_preference_by_id(key: str,
                                    response: Response,
                                    user=Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Returns user preference
    """

    pref = await get_user_preference_cmd(user, key)

    if pref is None:
        response.status_code = 404
        return None

    return pref


@router.post("/v1/user-preference/{key}",
             tags=["v1/user"],
             include_in_schema=sys_config.expose_gui_api)
@router.post("/user/preference/{key}",
             tags=["user"],
             include_in_schema=sys_config.expose_gui_api)
async def save_user_preference(key: str, preference: Union[dict, str, int, float],
                               user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Sets user preference.Uses key to set the preference
    """

    return await set_user_preference_cmd(user, key, preference)


@router.delete("/v1/user-preference/{key}", tags=["v1/user"], include_in_schema=sys_config.expose_gui_api)
@router.delete("/user/preference/{key}", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def delete_user_preference_by_id(key: str,
                                       user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Deletes user preference
    """

    try:
        return await delete_user_preference_cmd(user, key)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/v1/user", tags=["v1/user"],
             include_in_schema=sys_config.expose_gui_api)
async def save_user(user_payload: UserPayload):
    """
    Creates new user in database
    """

    try:
        return await add_user_cmd(user_payload)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.delete("/v1/user/{id}", tags=["v1/user"], include_in_schema=sys_config.expose_gui_api)
async def delete_user_by_id(id: str, user: User = Depends(Permissions(["admin"]))):
    """
    Deletes user with given ID
    """

    try:
        return await delete_user_cmd(id, user)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/v1/user/{id}", tags=["v1/user"], include_in_schema=sys_config.expose_gui_api)
async def get_user_by_id(id: str):
    """
    Returns user with given ID
    """

    try:
        return await get_user_cmd(id)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/v1/user/{id}", tags=["v1/user"], include_in_schema=sys_config.expose_gui_api, response_model=dict)
async def update_user(id: str, user_payload: UserPayload, user=Depends(Permissions(["admin"]))):
    """
    Edits existing user with given ID
    """

    try:
        saved, updated_user = await edit_user_cmd(id, user_payload, user)
        return {"inserted": saved}
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
