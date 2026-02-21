import os


class SqlLiteConfig:
    def __init__(self, env):
        self.sqlite_schema = env.get('SQLITE_SCHEMA', "sqlite+aiosqlite://")
        self.sqlite_host = env.get('SQLITE_HOST', "//db/airembr.sqlite")

sqlite_config = SqlLiteConfig(os.environ)