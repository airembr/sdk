from typing import Optional, Tuple

from pydantic import ValidationError

from airembr.model.metadata.sys_user import User
from airembr.model.metadata.user_payload import UserPayload
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.auth.token_store import token2user
from airembr.system.command.user.errors import UserError


async def edit_user_account(user: User, name: Optional[str], password: Optional[str]) -> Tuple[bool, User]:
    try:
        existing_user = user.model_copy()

        if password and password.strip() != "":
            password = password
        else:
            password = None

        if name:
            existing_user.name = name

        us = UserService()

        saved, new_user = await us.update_if_exist(
            user.id,
            UserPayload(
                name=existing_user.name,
                password=password,  # None password will leave old one
                roles=existing_user.roles,
                enabled=existing_user.enabled,
                email=existing_user.email
            )
        )

        token2user.set(new_user)

        return saved, new_user
    except LookupError as e:
        raise UserError(detail=str(e), status_code=404)
    except ValidationError as e:
        raise UserError(detail=e.errors()[0]["msg"], status_code=403)
