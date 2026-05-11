from pydantic import Field
from datetime import datetime
from typing import Optional, Any

from airembr.model.system.named_entity import NamedEntityInContext, NamedEntity
from airembr.sdk.service.time.time import now_in_utc


class EmbeddingSetting(NamedEntityInContext):
    timestamp: Optional[datetime] = Field(None, description="Timestamp when the embedding was created or updated")
    description: Optional[str] = Field(None, description="Description of the embedding setting")
    event_type: NamedEntity = Field(None, description="Associated event type")
    enabled: bool = Field(default=False, description="Whether the embedding setting is active")
    source: Optional[NamedEntity] = None
    tags: Optional[list] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = now_in_utc()
