from fastapi import APIRouter, Depends, HTTPException, Header, Response

from pydantic import BaseModel
from typing import Optional, Union
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from airembr.model.metadata.sys_user import User
from airembr.system.command.auth.errors import AuthError
from airembr.system.config.sys_config import sys_config
from airembr.system.adapter.metadata.mysql.mapping.user_mapping import map_to_user
from airembr.model.metadata.user_payload import UserPayload
from airembr.model.system.context import ServerContext, get_context
from airembr.system.command.user.errors import UserError
from airembr.system.command.user.preferences import (
    get_user_preference as get_user_preference_cmd,
    set_user_preference as set_user_preference_cmd,
    delete_user_preference as delete_user_preference_cmd,
    get_all_user_preferences as get_all_user_preferences_cmd,
)
from airembr.system.command.user.add_user import add_user as add_user_cmd
from airembr.system.command.user.delete_user import delete_user as delete_user_cmd
from airembr.system.command.user.get_user import get_user as get_user_cmd
from airembr.system.command.user.list_users import list_users as list_users_cmd
from airembr.system.command.user.list_users_legacy import list_users_legacy as list_users_legacy_cmd
from airembr.system.command.user.edit_user import edit_user as edit_user_cmd
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr_api.endpoint.gui.auth.authentication import Authentication, get_authentication
from airembr_api.service.grouping import get_grouped_result


class UserSoftEditPayload(BaseModel):
    password: Optional[str] = None
    name: Optional[str] = None


router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin"]))]
)

auth_router = APIRouter()


@auth_router.post("/user/token",
                  tags=["authorization"],
                  include_in_schema=sys_config.expose_gui_api)
async def get_token(login_form_data: OAuth2PasswordRequestForm = Depends(),
                    auth: Authentication = Depends(get_authentication)):
    """
    Returns OAuth2 token for login purposes
    """

    # Always log in the context of staging

    with ServerContext(get_context().switch_context(production=False)):

        if not sys_config.expose_gui_api:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden")

        try:
            token = await auth.login(login_form_data.username, login_form_data.password)
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=f"Authentication error: {str(e)}")

        return token


@auth_router.post("/user/logout", tags=["authorization"], include_in_schema=sys_config.expose_gui_api)
async def logout(authorization: Union[str, None] = Header(default=None),
                 auth: Authentication = Depends(get_authentication)):
    """
    Logs out user
    """

    if authorization is None:
        raise HTTPException(status_code=401, detail="No authorization header provided.")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or not parts[1]:
        raise HTTPException(status_code=401, detail="Malformed authorization header.")

    auth.logout(parts[1])


@router.get("/user/preference/{key}", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def get_user_preference(key: str,
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


@router.post("/user/preference/{key}",
             tags=["user"],
             include_in_schema=sys_config.expose_gui_api)
async def set_user_preference(key: str, preference: Union[dict, str, int, float],
                              user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Sets user preference.Uses key to set the preference
    """

    return await set_user_preference_cmd(user, key, preference)


@router.delete("/user/preference/{key}", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def delete_user_preference(key: str,
                                 user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Deletes user preference
    """

    try:
        return await delete_user_preference_cmd(user, key)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/user/preferences", tags=["user"], include_in_schema=sys_config.expose_gui_api,
            response_model=Optional[dict])
async def gets_all_user_preferences(
        user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Returns all user preferences
    """

    return await get_all_user_preferences_cmd(user)


@router.post("/user", tags=["user"],
             include_in_schema=sys_config.expose_gui_api)
async def add_user(user_payload: UserPayload):
    """
    Creates new user in database
    """

    try:
        return await add_user_cmd(user_payload)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.delete("/user/{id}", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def delete_user(id: str, user: User = Depends(Permissions(["admin"]))):
    """
    Deletes user with given ID
    """

    try:
        return await delete_user_cmd(id, user)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/user/{id}", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def get_user(id: str):
    """
    Returns user with given ID
    """

    try:
        return await get_user_cmd(id)
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/users", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def get_users(start: int = 0, limit: int = 500, query: Optional[str] = ""):
    """
    Lists users according to given query (str), start (int) and limit (int) parameters
    """

    result = await list_users_cmd(query, start, limit)

    return get_grouped_result("Users", result, map_to_user)


# TODO remove in 1.0.0
@router.get("/users/{start}/{limit}", tags=["user"], include_in_schema=sys_config.expose_gui_api, response_model=list)
async def get_users_legacy(start: int = 0, limit: int = 500, query: Optional[str] = ""):
    """
    Lists users according to given query (str), start (int) and limit (int) parameters
    """

    return await list_users_legacy_cmd(query, start, limit)


@router.post("/user/{id}", tags=["user"], include_in_schema=sys_config.expose_gui_api, response_model=dict)
async def edit_user(id: str, user_payload: UserPayload, user=Depends(Permissions(["admin"]))):
    """
    Edits existing user with given ID
    """

    try:
        saved, updated_user = await edit_user_cmd(id, user_payload, user)
        return {"inserted": saved}
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
