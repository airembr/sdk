import os

_env = os.environ

LOGGING_LEVEL = _env.get('LOGGING_LEVEL', 'warning')
LOGGING_FORMAT = _env.get('LOGGING_FORMAT', 'console')