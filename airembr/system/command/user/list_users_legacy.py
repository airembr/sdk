from typing import Optional

from airembr.system.adapter.metadata.mysql.mapping.user_mapping import map_to_user
from airembr.system.adapter.metadata.mysql.service.user_service import UserService


async def list_users_legacy(query: Optional[str], start: int, limit: int) -> list:
    us = UserService()
    if len(query) > 0:
        users = await us.load_by_name(query, limit, start)
    else:
        users = (await us.load_all(limit, start)).map_to_objects(map_to_user)

    result = []
    for user in users:
        result.append({**user.model_dump(), "expired": user.is_expired()})

    return result
