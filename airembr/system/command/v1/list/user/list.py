from airembr.model.metadata.sys_user import User


async def get_all_user_preferences(user: User) -> dict:
    return user.preference
