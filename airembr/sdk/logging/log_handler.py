import os

import logging
import traceback

import sys

from airembr.sdk.logging.formater import CustomFormatter
from airembr.sdk.logging.tools import Q_INFO_LEVEL, DEV_INFO_LEVEL, Q_STAT_LEVEL, _get_logging_level

_env = os.environ


def stack_trace():
    # Extract the traceback object
    tb = sys.exc_info()[2]

    # Convert the traceback to a list of structured frames
    stack = traceback.extract_tb(tb)

    if not stack:
        stack = traceback.extract_stack()

    # Format the stack trace as a list of dictionaries
    return {
        "stack": [
            {
                "filename": frame.filename,
                "line_number": frame.lineno,
                "function_name": frame.name,
                "code_context": frame.line
            }
            for frame in stack
        ]}


class StackInfoLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = True
        if msg is None:
            msg = "None"
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)

    def q_info(self, msg, *args, **kwargs):
        """
        Logs a message with custom MESSAGE_LEVEL
        """
        if self.isEnabledFor(Q_INFO_LEVEL):
            self._log(Q_INFO_LEVEL, msg, args, **kwargs)

    def dev_info(self, msg, *args, **kwargs):
        """
        Logs a message with custom MESSAGE_LEVEL
        """
        if self.isEnabledFor(DEV_INFO_LEVEL):
            self._log(DEV_INFO_LEVEL, msg, args, **kwargs)

    def stat(self, msg, *args, **kwargs):
        if self.isEnabledFor(Q_STAT_LEVEL):
            self._log(Q_STAT_LEVEL, msg, args, **kwargs)


logging.setLoggerClass(StackInfoLogger)
logging.basicConfig(level=logging.INFO)
logging.addLevelName(Q_INFO_LEVEL, "Q_INFO")
logging.addLevelName(DEV_INFO_LEVEL, "DEV_INFO")
logging.addLevelName(Q_STAT_LEVEL, "STAT")
_logging_level = _get_logging_level(_env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in _env else logging.WARNING


def get_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(CustomFormatter())
    logger.addHandler(clh)

    return logger
