from typing import Optional

from pydantic import BaseModel

class IChatSession(BaseModel):
    ttl: Optional[int] = 0
    ttl_type: Optional[str] = 'keep'
    compress_after: Optional[int] = 100 * 1024  # 100KB


class ISession(BaseModel):
    id: Optional[str] = None
    chat: Optional[IChatSession] = None
