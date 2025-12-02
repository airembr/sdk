import os

import logging
import traceback

import sys

from airembr.sdk.logging.formater import CustomFormatter

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
        kwargs['exc_info'] = True
        if msg is None:
            msg = "None"
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)


logging.setLoggerClass(StackInfoLogger)
logging.basicConfig(level=logging.INFO)


def get_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or logging.WARNING)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(CustomFormatter())
    logger.addHandler(clh)

    return logger
