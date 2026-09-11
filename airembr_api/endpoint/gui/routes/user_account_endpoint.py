from fastapi import APIRouter, Depends, HTTPException

from airembr_api.endpoint.gui.routes.user_endpoint import UserSoftEditPayload
from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_user import User
from airembr.system.command.user.errors import UserError
from airembr.system.command.user.get_user_account import get_user_account as get_user_account_cmd
from airembr.system.command.user.edit_user_account import edit_user_account as edit_user_account_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "marketer", "developer", "maintainer"]))]
)


@router.get("/user-account", tags=["user"], include_in_schema=sys_config.expose_gui_api, response_model=dict)
async def get_user_account(user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Returns data of the user who called the endpoint
    """
    return await get_user_account_cmd(user)


@router.post("/user-account", tags=["user"], include_in_schema=sys_config.expose_gui_api)
async def edit_user_account(payload: UserSoftEditPayload,
                            user: User = Depends(Permissions(["admin", "developer", "marketer", "maintainer"]))):
    """
    Edits currently logged user.
    """

    try:
        saved, new_user = await edit_user_account_cmd(user, payload.name, payload.password)
        return {"inserted": saved}
    except UserError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
