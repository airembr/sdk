from airembr.system.adapter.metadata.mysql.schema.table import UserTable
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.user.errors import UserError


async def get_user(user_id: str) -> UserTable:
    us = UserService()
    record = await us.load_by_id(user_id)

    if not record.exists():
        raise UserError(detail=f"User {user_id} not found.", status_code=404)

    if record.has_multiple_records():
        raise UserError(detail=f"User {user_id} has multiple rows in database.", status_code=500)

    user_table: UserTable = record.rows
    user_table.password = None

    return user_table
