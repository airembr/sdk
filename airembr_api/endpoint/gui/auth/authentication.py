from fastapi.security import OAuth2PasswordBearer

from airembr.system.command.auth import login as login_cmd

_singleton = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


class Authentication:

    async def login(self, email, password):
        return await login_cmd.login(email, password)

    @staticmethod
    def logout(token):
        login_cmd.logout(token)


def get_authentication():
    global _singleton

    def get_auth():
        return Authentication()

    if _singleton is None:
        _singleton = get_auth()

    return _singleton
