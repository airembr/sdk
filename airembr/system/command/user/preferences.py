from typing import Any, Optional

from airembr.model.metadata.sys_user import User
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.auth.token_store import token2user
from airembr.system.command.user.errors import UserError


async def get_user_preference(user: User, key: str) -> Optional[Any]:
    return user.preference.get(key, None)


async def set_user_preference(user: User, key: str, preference) -> Any:
    user.set_preference(key, preference)

    us = UserService()
    result = await us.upsert(user)

    token2user.set(user)

    return result


async def delete_user_preference(user: User, key: str) -> Any:
    if key not in user.preference:
        raise UserError(detail=f"Preference {key} not found", status_code=404)

    user.delete_preference(key)

    us = UserService()
    result = await us.upsert(user)

    token2user.set(user)

    return result


async def get_all_user_preferences(user: User) -> dict:
    return user.preference
