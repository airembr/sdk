import os
import redis

from airembr.sdk.service.environment import get_env_as_int


class RedisConfig:

    def __init__(self, env):
        self.env = env
        self.host = env.get('REDIS_HOST', 'redis://localhost')
        self.port = get_env_as_int('REDIS_PORT', 6379)
        self.database = get_env_as_int('REDIS_DATABASE', 0)
        self.password = env.get('REDIS_PASSWORD', None)
        self.username = env.get('REDIS_USERNAME', None)

        connection = redis.from_url(self.host)
        c = connection.connection_pool.connection_kwargs

        self.redis_protocol = 'rediss' if self.host.startswith('rediss') else 'redis'
        self.redis_user = c['username'] if 'username' in c else self.username
        self.redis_password = c['password'] if 'password' in c else self.password
        self.redis_host = c['host'] if 'host' in c else 'localhost:6379'
        self.redis_port = c['port'] if 'port' in c else self.port
        self.redis_db = c['db'] if 'db' in c else self.database

    def recreate_redis_uri(self, database=None):
        if self.redis_user and self.redis_password:
            host = f"{self.redis_protocol}://{self.redis_user}:{self.redis_password}@{self.redis_host}"
        elif self.redis_password:
            host = f"{self.redis_protocol}://:{self.redis_password}@{self.redis_host}"
        else:
            host = f"{self.redis_protocol}://{self.redis_host}"

        if database:
            host = f"{host}/{database}"

        return host


redis_config = RedisConfig(os.environ)
