import os

meta_data_adapter = os.environ.get('META_DATA_ADAPTER', 'mysql')  # sqlite, mysql

if meta_data_adapter not in ['sqlite', 'mysql']:
    raise ValueError("META_DATA_ADAPTER must be either sqlite or mysql")