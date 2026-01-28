from typing import Optional

from pydantic import BaseModel


class IdentificationId(BaseModel):
    iid: Optional[str] = None
    type: Optional[str] = None

    def is_empty(self) -> bool:
        return self.iid is None