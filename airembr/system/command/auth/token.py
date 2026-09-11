import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from airembr.core.env.validator import get_env_as_int
from airembr.system.command.auth.errors import AuthError
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)


class JWTConfig:

    def __init__(self):
        env = os.environ
        self.secret_key = env.get('JWT_SECRET_KEY', None)
        self.algorithm = env.get('JWT_ALGORITHM', 'HS256')
        self.expiration_minutes = get_env_as_int('JWT_EXPIRATION_MINUTES', 60)

        if not self.secret_key:
            logger.warning('Env JWT_SECRET_KEY not set. JWT authorization is disabled.')
        elif len(self.secret_key) < 20:
            logger.warning(
                'Security risk. Env JWT_SECRET_KEY too short. It must be at least 20 chars long.'
            )


jwt_config = JWTConfig()


def is_jwt_auth_enabled() -> bool:
    return bool(jwt_config.secret_key)


def verify_shared_secret(secret: str) -> bool:
    if not jwt_config.secret_key or not secret:
        return False
    return hmac.compare_digest(secret, jwt_config.secret_key)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=jwt_config.expiration_minutes)
    return jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
    except jwt.ExpiredSignatureError:
        raise AuthError(detail="Token has expired", status_code=401)
    except jwt.InvalidTokenError:
        raise AuthError(detail="Invalid authentication credentials", status_code=401)
