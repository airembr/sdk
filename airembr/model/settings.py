from typing import Any, Optional

from pydantic import BaseModel


class SystemSettings(BaseModel):
    label: str
    value: Any = None
    desc: str
    expose: Optional[bool] = False
    cluster_wide: Optional[bool] = False
