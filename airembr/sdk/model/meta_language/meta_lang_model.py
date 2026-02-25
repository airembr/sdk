from typing import List, Tuple, Any, Optional, Union
from pydantic import BaseModel

class MetaLangEntityBase(BaseModel):
    type: str
    properties: Optional[List[Tuple[str, Any]]] = []

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.type = self.type.lower()

class MetaLangEntity(MetaLangEntityBase):
    negation: Optional[bool] = False

class MetaLangGroup(BaseModel):
    entities: List[Union["MetaLangEntity", "MetaLangLogic"]] = []

class MetaLangLogic(BaseModel):
    operator: str  # AND, OR, NOT
    group: MetaLangGroup

class MetaLangQuery(BaseModel):
    clause: str
    query: Union[MetaLangEntity, MetaLangLogic]
    returns: Optional[List[MetaLangEntity]] = None


MetaLangGroup.model_rebuild()
