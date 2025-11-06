import os

from pararun.service.logger.formater import ConsoleFormatter, JSONFormatter, CustomFormatter


def log_format_adapter():
    type = os.environ.get('LOGGING_FORMAT', 'console')
    if type == 'console':
        return ConsoleFormatter()
    elif type == 'json':
        return JSONFormatter()
    else:
        return CustomFormatter()