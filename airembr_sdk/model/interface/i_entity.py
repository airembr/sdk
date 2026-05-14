from pydantic import BaseModel
from uuid import uuid4


class IEntity(BaseModel):
    id: str

    @staticmethod
    def new() -> 'IEntity':
        return IEntity(id=str(uuid4()))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, IEntity) else False
