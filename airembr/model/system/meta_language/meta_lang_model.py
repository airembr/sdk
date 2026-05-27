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

    def add(self, logic: Union[MetaLangEntity, 'MetaLangLogic']):
        if  isinstance(self.query, MetaLangLogic):
            self.query.group.entities.append(logic)
        else:
            group = MetaLangGroup(entities=[self.query, logic])
            self.query = MetaLangLogic(operator='AND', group=group)

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

    def has_and_entity(self, entity_type:str):
        for and_query in self.yield_leafs(operator='AND'):
            for q in and_query:
                if q.type.lower() == entity_type:
                    return True
        return False


MetaLangGroup.model_rebuild()
