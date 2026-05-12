from typing import Protocol, TypeVar, Generator, Optional, List, Dict, Union, runtime_checkable
from collections.abc import Iterator

from srd.domain.record_mapping import EntityToTableMapping, ColumnValue

from durable_dot_dict.collection import DotDictStream
from durable_dot_dict.dotdict import DotDict

T = TypeVar("T")


@runtime_checkable
class ResultProtocol(Protocol):
    result: any  # underlying result object with mappings() and fetch_all()

    def map(self, mapping: EntityToTableMapping, cast_to: Optional[type[T]] = ...) -> Generator[T, None, None]:
        ...

    def first(self) -> Optional[list]:
        ...

    def first_as(self, mapping: EntityToTableMapping) -> Optional[T]:
        ...

    def all(self) -> Generator[ColumnValue, None, None]:
        ...

    def list(self) -> List:
        ...

    def row_count(self) -> int:
        ...

    def __iter__(self) -> Iterator:
        ...

    def __rshift__(self, mapping: Union[EntityToTableMapping, Dict[str, str]]) -> DotDictStream:
        ...

    @staticmethod
    def _map_columns(row: dict, mapping_values: Dict[str, str]) -> DotDict:
        ...
