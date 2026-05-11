from pydantic import BaseModel
from typing import Optional


class ProcessStatus(BaseModel):
    error: bool
    message: Optional[str] = None
    trace: Optional[list] = []

    def is_valid(self) -> bool:
        return self.error is False
