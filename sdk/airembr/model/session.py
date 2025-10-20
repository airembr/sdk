from typing import Optional, Any

from pydantic import BaseModel

from sdk.airembr.service.uuid.uuid_generator import get_time_based_uuid

class ChatSession(BaseModel):
    ttl: Optional[int] = 0
    ttl_type: Optional[str] = 'keep'
    compress_after: Optional[int] = 100 * 1024  # 100KB

class Session(BaseModel):
    id: Optional[str] = None
    chat: Optional[ChatSession] = None


    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if not self.id:
            self.id = get_time_based_uuid()
