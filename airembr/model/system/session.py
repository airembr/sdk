from typing import Any

from airembr.core.hash.uuid_generator import get_time_based_uuid
from airembr_sdk.model.interface.i_session import ISession, IChatSession


class ChatSession(IChatSession):
    pass

class Session(ISession):
    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if not self.id:
            self.id = get_time_based_uuid()
