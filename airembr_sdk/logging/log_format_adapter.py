from airembr_sdk.logging.log_config import LOGGING_FORMAT
from airembr_sdk.logging.log_format import CustomFormatter, JSONFormatter, ConsoleFormatter


def log_format_adapter():
    if LOGGING_FORMAT == 'console':
        return ConsoleFormatter()
    elif LOGGING_FORMAT == 'json':
        return JSONFormatter()
    else:
        return CustomFormatter()