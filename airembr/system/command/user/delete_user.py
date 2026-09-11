from airembr.model.metadata.sys_user import User
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.user.errors import UserError


async def delete_user(user_id: str, requesting_user: User) -> tuple:
    if user_id == requesting_user.id:
        raise UserError(detail="You cannot delete your own account", status_code=403)

    us = UserService()
    return await us.delete_by_id(user_id)
