import os

from airembr.core.singleton import Singleton
from airembr.core.env.validator import get_env_as_int, get_env_as_bool

class LoggingConfig(metaclass=Singleton):
    def __init__(self):
        env = os.environ
        self.save_logs = get_env_as_bool('SAVE_LOGS', 'yes')
        self.log_stack_trace_as = env.get('LOG_STACK_TRACE_AS', 'json')
        self.log_stack_trace_for = env.get('LOG_STACK_TRACE_AS', 'CRITICAL,ERROR,WARNING,INFO').split(',')
        self.log_bulk_size = get_env_as_int('LOG_BULK_SIZE', 1)

logging_config = LoggingConfig()