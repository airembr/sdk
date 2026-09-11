from typing import List

from airembr.model.metadata.sys_user import User
from airembr.system.command.auth.errors import AuthError
from airembr.system.command.auth.token_store import token2user
from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)


async def authorize(token: str, roles: List[str], request_path: str = "") -> User:
    if not sys_config.expose_gui_api or token is None:
        if not sys_config.expose_gui_api:
            logger.warning("Unauthorized access to disabled API.")
        else:
            logger.warning("Unauthorized access with empty token.")

        raise AuthError(detail="Access forbidden", status_code=403)

    user = token2user.get(token)

    # Not authenticated if no user or insufficient roles

    if not user:
        logger.warning(f"Unauthorized access. User not available for {token}")
        raise AuthError(detail="Invalid authentication credentials", status_code=401)

    refreshed_token = token2user.refresh(user)

    if refreshed_token != token:
        token2user.delete(token)
        token2user.delete(refreshed_token)

        logger.warning(f"Unauthorized access. User token mismatch {token} != {refreshed_token}")
        raise AuthError(detail="Invalid authentication credentials", status_code=401)

    if not user.has_roles(roles):
        logger.warning(f"User {user.email}. Unauthorized access to {request_path}. Required roles {roles}, "
                       f"granted {user.roles} ")

        raise AuthError(detail="Invalid authentication credentials", status_code=401)

    return user
