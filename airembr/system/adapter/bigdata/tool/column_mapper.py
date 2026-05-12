from typing import Generator

from airembr.system.logging.log_handler import get_logger

from srd.domain.record_mapping import EntityToTableMapping
from srd.mapping.data_mapping import map_object_to_column

logger = get_logger(__name__)


def _any_column_empty(data: dict, columns_to_check: list) -> bool:
    return any(data.get(col) is None for col in columns_to_check)


def map_to_table_columns(data, mapping: EntityToTableMapping, required_columns=None) -> Generator[dict, None, None]:
    if required_columns is None:
        required_columns = []

    for flat_row in data:
        table_values = {}
        for object_property_mapping in mapping.columns:
            result = map_object_to_column(flat_row, object_property_mapping, json_as_string=False)
            if result is not None:
                column, _, value = result
                table_values[column] = value
        if _any_column_empty(table_values, required_columns):
            logger.error(f"Row {table_values} has missing column. Required: {required_columns}")
            continue
        yield table_values
