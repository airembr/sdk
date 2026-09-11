from airembr.model.metadata.sys_user import User
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.command.auth.errors import AuthError
from airembr.system.command.auth.token_store import token2user
from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)


async def _authenticate(username, password) -> User:
    logger.debug(
        f"Authenticating {username}...",
        extra=extra_info.exact(
            "Authentication",
            error_number="ATH-0001",
            class_name="Authentication",
            package=__name__,
            user_id=username
        )
    )

    try:
        us = UserService()
        user: User = await us.load_by_credentials(
                email=username,
                password=password
            )
    except Exception as e:
        raise AuthError(detail=f"System not installed. Got error {str(e)}", status_code=400)

    if user is None:
        logger.warning(
            "Incorrect username or password.",
            extra=extra_info.exact(
                error_number="ATH-0002",
                origin="Authentication",
                class_name="Authentication",
                package=__name__,
                user_id=username
            )
        )
        raise AuthError(detail="Incorrect username or password.", status_code=400)

    if not user.enabled:
        logger.warning(
            "This account was disabled.",
            extra=extra_info.exact(
                error_number="ATH-0003",
                origin="Authentication",
                class_name="Authentication",
                package=__name__,
                user_id=username
            )
        )
        raise AuthError(detail="This account was disabled", status_code=400)

    if user.is_expired():
        logger.warning(
            "This account has expired.",
            extra=extra_info.exact(
                error_number="ATH-0004",
                origin="Authentication",
                class_name="Authentication",
                package=__name__,
                user_id=username
            )
        )
        raise AuthError(detail="This account has expired.", status_code=400)

    logger.info(
        "User logged-in.",
        extra=extra_info.exact(
            error_number="ATH-0005",
            origin="Authentication",
            class_name="Authentication",
            package=__name__,
            user_id=username
        )
    )
    return user


async def login(email, password) -> dict:
    user = await _authenticate(email, password)

    # save token, match token with user in token2user
    token = token2user.set(user)

    return {"access_token": token, "token_type": "bearer", "roles": user.roles, "preference": user.preference}


def logout(token):
    token2user.delete(token)
