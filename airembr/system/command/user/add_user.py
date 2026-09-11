from uuid import uuid4

from airembr.model.metadata.sys_user import User
from airembr.model.metadata.user_payload import UserPayload
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.user.errors import UserError


async def add_user(user_payload: UserPayload) -> str:
    expiration_timestamp = user_payload.get_expiration_date()
    user = User(
        **user_payload.model_dump(),
        id=str(uuid4()),
        expiration_timestamp=expiration_timestamp
    )

    user.password = User.encode_password(user.password)

    us = UserService()

    user_id = await us.insert_if_none(user)

    if user_id is None:
        raise UserError(detail=f"User with email '{user_payload.email}' already exists.", status_code=409)

    return user_id
