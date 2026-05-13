import os

from airembr.system.process.logging.log_format import CustomFormatter, JSONFormatter, ConsoleFormatter


def log_format_adapter():
    type = os.environ.get('LOGGING_FORMAT', 'console')
    if type == 'console':
        return ConsoleFormatter()
    elif type == 'json':
        return JSONFormatter()
    else:
        return CustomFormatter()