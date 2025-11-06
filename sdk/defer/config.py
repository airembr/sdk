import os

from pararun.service.environment import get_env_as_bool
from pararun.service.singleton import Singleton


class Config(metaclass=Singleton):

    @property
    def fail_over_server_api(self):
        return os.environ.get('FAIL_OVER_SERVER_API', None)

    @property
    def fail_over_server_token(self):
        return os.environ.get('FAIL_OVER_SERVER_TOKEN', None)

    @property
    def queue_enabled(self):
        return get_env_as_bool('QUEUE_ENABLED', 'yes')