from airembr.model.metadata.sys_user import User


async def get_user_account(user: User) -> dict:
    return user.model_dump(mode='json', exclude={"password": ...})
