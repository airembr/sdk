from airembr.system.adapter.bigdata.starrocks.starrocks_base_adapter import StarrocksBaseAdapter
from airembr.system.config.sys_config import sys_config


class AdapterRouter:

    def __init__(self):
        if sys_config.big_data_adapter == 'starrocks':
            self.adapter = StarrocksBaseAdapter()
        else:
            raise ValueError("Unknown big data adapter")

