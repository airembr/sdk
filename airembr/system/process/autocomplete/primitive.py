from airembr.system.adapter.bigdata.big_data_adapter import bd_search_adapter

def columns(table_mapping):
    return sorted(set(table_mapping.get_properties()))


async def values(table_mapping, column, limit=100):
    return await bd_search_adapter.get_column_values(table_mapping, column, limit)


async def json_values(table_mapping, entity_type, column, limit=100):
    return await bd_search_adapter.get_json_field_values(table_mapping, entity_type, column, limit)