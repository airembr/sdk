from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from airembr.system.command.auth.token import create_access_token, verify_shared_secret
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)

router = APIRouter()


class AuthRequest(BaseModel):
    secret: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/auth", tags=['auth'], response_model=TokenResponse)
async def issue_token(payload: AuthRequest):
    if not verify_shared_secret(payload.secret):
        logger.warning("Unauthorized token request. Invalid shared secret.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    token = create_access_token({"airembr": 1})
    return TokenResponse(access_token=token)
