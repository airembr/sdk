from datetime import datetime
from typing import Optional, Any

from airembr.model.system.named_entity import NamedEntityInContext
from airembr.sdk.common.date import now_in_utc


class Setting(NamedEntityInContext):
    timestamp: Optional[datetime] = None
    description: Optional[str] = ""
    enabled: Optional[bool] = False
    type: str
    content: dict
    config: dict

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = now_in_utc()
