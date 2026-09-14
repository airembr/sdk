from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from airembr.system.command.auth.errors import AuthError
from airembr.system.command.auth.token import decode_access_token, is_jwt_auth_enabled
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)

security = HTTPBearer(auto_error=False)


class JWTAuth:

    async def __call__(self, credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict | None:
        if not is_jwt_auth_enabled():
            # No JWT_SECRET_KEY configured: JWT auth is disabled, rely on other security controls.
            return None

        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            return decode_access_token(credentials.credentials)
        except AuthError as e:
            logger.warning(f"Unauthorized access. {e}")
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
