import os

from airembr.sdk.storage.metadata.db_config import meta_data_adapter

_local_folder = os.path.dirname(__file__)

def get_md_sql_view_folder():
    return f"{_local_folder}/{meta_data_adapter}/schema/view"