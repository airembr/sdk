from typing import List, Tuple, Any, Optional, Union, Iterator
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
    returns: Optional[List[str]] = None

    @staticmethod
    def _iter_and_queries(node: Union[MetaLangEntity, MetaLangLogic], operator: str) -> Iterator[MetaLangLogic]:
        if isinstance(node, MetaLangLogic):
            if node.operator == operator:
                yield node

            for entity in node.group.entities:
                yield from MetaLangQuery._iter_and_queries(entity, operator)


    def yield_queries(self, operator: str):
        yield from MetaLangQuery._iter_and_queries(self.query, operator)


    def yield_leafs(self, operator: str):

        if isinstance(self.query, MetaLangEntity):
            yield [self.query]

        for query in self.yield_queries(operator):
            if isinstance(query, MetaLangLogic):
                query_ents = []
                for entity in query.group.entities:
                    if isinstance(entity, MetaLangEntity):
                        query_ents.append(entity)
                if query_ents:
                    yield query_ents


MetaLangGroup.model_rebuild()
