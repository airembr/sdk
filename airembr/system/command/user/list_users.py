from typing import Optional

from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.system.adapter.metadata.mysql.service.user_service import UserService


async def list_users(query: Optional[str], start: int, limit: int) -> SelectResult:
    us = UserService()
    return await us.load_all(query, limit, start)
