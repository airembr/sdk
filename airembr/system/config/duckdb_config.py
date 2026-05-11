import os

from airembr.core.singleton import Singleton


class DuckDbConfig(metaclass=Singleton):
    def __init__(self, ):
        env = os.environ
        self.duckdb_host = env.get('DUCKDB_HOST', "/db/airembr.duckdb")


duckdb_config = DuckDbConfig()