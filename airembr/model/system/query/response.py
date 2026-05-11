from typing import Optional, List

from durable_dot_dict.dotdict import DotDict

from airembr.sdk.service.format.formaters import format_traits


class QueryResponse:

    def __init__(self, result: List[dict], total: Optional[int] = None):
        self.result = [DotDict(item) for item in result]
        if total:
            self.total = total
        else:
            self.total = len(result)

    def __repr__(self):
        return f"QueryResponse(result={self.result}, total={self.total})"


class EntityDotDict(DotDict):

    def __init__(self, data: dict, fit: Optional[float]=None):
        super().__init__(data)
        self._fit = fit

    def format_traits(self) -> Optional[str]:
        if 'traits' not in self:
            return None
        return format_traits(self['traits'])

    def format_entity(self, entity_type: str):
        return f"{entity_type} {self.format_traits()}"

    @property
    def fit(self):
        return self._fit



class QueryEntityResponse:
    def __init__(self, result: List[dict], total: Optional[int] = None):
        self.result = [EntityDotDict(item, fit=item.get('fit', None)) for item in result]
        if total:
            self.total = total
        else:
            self.total = len(result)

    def __repr__(self):
        return f"QueryEntityResponse(result={self.result}, total={self.total})"
