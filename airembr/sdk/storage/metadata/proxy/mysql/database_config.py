import os

from airembr.sdk.service.environment import get_env_as_int


class MysqlConfig:

    def __init__(self, env):
        self.env = env
        self.mysql_host = env.get('MYSQL_HOST', "localhost")
        self.mysql_username = env.get('MYSQL_USERNAME', "root")
        self.mysql_password = env.get('MYSQL_PASSWORD', "root")
        self.mysql_schema_async = env.get('MYSQL_SCHEMA_ASYNC', "mysql+aiomysql://")
        self.mysql_schema_sync = env.get('MYSQL_SCHEMA_SYNC', "mysql+pymysql://")

        self.mysql_port = env.get('MYSQL_PORT', 3306)
        self.mysql_echo = env.get('MYSQL_ECHO', "no") == "yes"

        self.pool_size = get_env_as_int('MYSQL_POOL_SIZE', 5)
        self.pool_max_overflow = get_env_as_int('MYSQL_POOL_MAX_OVERFLOW', 2)
        self.pool_timeout = get_env_as_int('MYSQL_POOL_TIMEOUT', 3)
        self.pool_recycle = get_env_as_int('MYSQL_RECYCLE', 1800)

        self.mysql_database_uri = self.uri(async_driver=True)

    def _get_schema(self, async_driver: bool = True):
        if async_driver:
            return self.mysql_schema_async
        return self.mysql_schema_sync

    def uri(self, async_driver: bool = True) -> str:
        if self.mysql_username and self.mysql_password:
            _creds = f"{self.mysql_username}:{self.mysql_password}"
        elif self.mysql_username:
            _creds = f"{self.mysql_username}:"
        else:
            _creds = ""

        if _creds:
            uri = f"{self._get_schema(async_driver)}{_creds}@{self.mysql_host}:{self.mysql_port}"
        elif self.mysql_port:
            uri = f"{self._get_schema(async_driver)}{self.mysql_host}:{self.mysql_port}"
        else:
            uri = f"{self._get_schema(async_driver)}{self.mysql_host}"

        return uri.strip(" /")


mysql_config = MysqlConfig(os.environ)
