from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from airembr.system.command.auth.errors import AuthError
from airembr.system.command.auth.permissions import authorize

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


class Permissions:

    def __init__(self, roles):
        self.roles = roles

    async def __call__(self, request: Request, token: str = Depends(oauth2_scheme)):
        try:
            return await authorize(token, self.roles, request_path=str(request.url))
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))
