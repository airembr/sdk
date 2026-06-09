from typing import List, Tuple, Any, Optional, Union, Iterator
from pydantic import BaseModel


class MetaLangProperty(BaseModel):
    name: str
    assign: str  # "=", "~", or ":"
    value: Any
    distance: Optional[float] = None  # only for ~; None means use DEFAULT_MAX_VECTOR_DISTANCE

    def __str__(self) -> str:
        dist = f"[{self.distance}]" if self.distance is not None else ""
        if isinstance(self.value, bool):
            return f'{self.name}{self.assign}{dist}{"true" if self.value else "false"}'
        if isinstance(self.value, (int, float)):
            return f'{self.name}{self.assign}{dist}{self.value}'
        return f'{self.name}{self.assign}{dist}"{self.value}"'


class MetaLangEntityBase(BaseModel):
    type: str
    properties: Optional[List[MetaLangProperty]] = []

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.type = self.type.lower()

    def __str__(self) -> str:
        inner = ", ".join(str(prop) for prop in (self.properties or []))
        prefix = "NOT " if getattr(self, "negation", False) else ""
        return f'{prefix}{self.type}({inner})'


class MetaLangEntity(MetaLangEntityBase):
    negation: Optional[bool] = False

class MetaLangGroup(BaseModel):
    entities: List[Union["MetaLangEntity", "MetaLangLogic"]] = []

class MetaLangLogic(BaseModel):
    operator: str  # AND, OR, NOT
    group: MetaLangGroup

    def __str__(self) -> str:
        parts = [str(e) for e in self.group.entities]
        if len(parts) == 1:
            return parts[0]
        return f'({f" {self.operator} ".join(parts)})'



class MetaLangQuery(BaseModel):
    clause: str
    query: Union[MetaLangEntity, MetaLangLogic]
    returns: Optional[List[str]] = None

    def __str__(self) -> str:
        return str(self.query)

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
