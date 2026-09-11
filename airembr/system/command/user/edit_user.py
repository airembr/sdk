from typing import Tuple

from airembr.model.metadata.sys_user import User
from airembr.model.metadata.user_payload import UserPayload
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.auth.token_store import token2user
from airembr.system.command.user.errors import UserError


async def edit_user(user_id: str, user_payload: UserPayload, requesting_user: User) -> Tuple[bool, User]:
    if requesting_user.is_the_same_user(user_id) and not user_payload.has_admin_role() and requesting_user.is_admin():
        raise UserError(detail="You cannot remove the role of admin from your own account", status_code=403)

    try:
        if user_payload.password and user_payload.password.strip() != "":
            user_payload.password = user_payload.password
        else:
            user_payload.password = None

        us = UserService()

        saved, updated_user = await us.update_if_exist(user_id, user_payload)
        token2user.set(updated_user)
        return saved, updated_user

    except LookupError as e:
        raise UserError(detail=str(e), status_code=404)
