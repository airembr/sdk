import os

from airembr.sdk.service.environment import get_env_as_int


class RedisConfig:

    def __init__(self, env):
        self.env = env
        self.host = env.get('REDIS_HOST', 'localhost')
        self.port = get_env_as_int('REDIS_PORT', 6379)
        self.redis_host = env.get('REDIS_HOST', 'redis://localhost:6379')
        self.redis_password = env.get('REDIS_PASSWORD', None)

        if self.host.startswith("redis://"):
            self.host = self.host[8:]

        if self.host.startswith("rediss://"):
            self.host = self.host[9:]

        if ":" in self.host:
            self.host = self.host.split(":")[0]

    def get_redis_with_password(self):
        if self.redis_password:
            return self.get_redis_uri(self.redis_host, password=self.redis_password)
        return self.get_redis_uri(self.redis_host)

    @staticmethod
    def get_redis_uri(host, user=None, password=None, protocol="redis", database="0"):
        if not host.startswith('redis://'):
            host = f"{protocol}://{host}"

        if user and password:
            host = f"{protocol}://{user}:{password}@{host[8:]}/{database}"
        elif password:
            host = f"{protocol}://:{password}@{host[8:]}/{database}"

        return host


redis_config = RedisConfig(os.environ)