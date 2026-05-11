import os

from airembr.core.singleton import Singleton


class ServerConfig(metaclass=Singleton):
    def __init__(self):
        env = os.environ
        self.x_forwarded_ip_header = env.get('USE_X_FORWARDED_IP', None)
        self.api_docs = (env['API_DOCS'].lower() == "yes") if 'API_DOCS' in env else True
        self.performance_tracking = env.get('PERFORMANCE_TRACKING', None)
        self.server_logging_level = env.get('SERVER_LOGGING_LEVEL', 'warning')


server_config = ServerConfig()
