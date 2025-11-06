import json
import os
import sys

import logging
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from logging import Handler, LogRecord
from time import time

from pararun.service.logger.logger_adapter import log_format_adapter
from pararun.service.logger.logging_config import log_stack_trace_as, log_stack_trace_for
from pararun.service.logger.tools import _get_logging_level
import traceback

_env = os.environ
_logging_level = _get_logging_level(_env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in _env else logging.WARNING
_save_logs_on = _env.get('SAVE_LOGS', 'yes').lower() == 'yes'
_log_format_adapter = log_format_adapter()

def now_in_utc():
    return datetime.utcnow().replace(tzinfo=ZoneInfo('UTC'))


def stack_trace(level):
    if level not in log_stack_trace_for:
        return {}

    # Extract the traceback object
    tb = sys.exc_info()[2]

    # Convert the traceback to a list of structured frames
    stack = traceback.extract_tb(tb)

    if not stack:
        stack = traceback.extract_stack()

    metadata = {}

    # Format the stack trace as a list of dictionaries
    return {
        "context": metadata,
        "stack": [
            {
                "filename": frame.filename,
                "line_number": frame.lineno,
                "function_name": frame.name,
                "code_context": frame.line
            }
            for frame in stack
        ]}


class DeferLogHandler(Handler):

    def __init__(self, level=0, collection=None):
        super().__init__(level)
        if collection is None:
            collection = []
        self.collection: List = collection
        self.last_save = time()

    @staticmethod
    def _get(record, value, default_value):
        return record.__dict__.get(value, default_value)

    def emit(self, record: LogRecord):

        # Skip info and debug.
        if record.levelno <= logging.INFO:
            return

        _trace = stack_trace(record.levelname)
        if log_stack_trace_as == 'json':
            if _trace:
                stack_trace_str = f"JSON:{json.dumps(_trace)}"
            else:
                stack_trace_str = None
        else:
            stack_trace_str = record.stack_info

        log = {  # Maps to tracardi-log index
            "date": now_in_utc(),
            "message": record.msg,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "level": record.levelname,
            "stack_info": stack_trace_str,
            # "exc_info": record.exc_info  # Can not save this to TrackerPayload
            "module": self._get(record, "package", record.module),
            "class_name": self._get(record, "class_name", record.funcName),
            "origin": self._get(record, "origin", "root"),
            "event_id": self._get(record, "event_id", None),
            "profile_id": self._get(record, "profile_id", None),
            "flow_id": self._get(record, "flow_id", None),
            "node_id": self._get(record, "node_id", None),
            "user_id": self._get(record, "user_id", None),
        }

        if _save_logs_on:
            self.collection.append(log)

    def has_logs(self, min_log_size=None):
        if min_log_size is None:
            min_log_size = 100
        if not isinstance(self.collection, list):
            return False
        return len(self.collection) >= min_log_size or (time() - self.last_save) > 60

    def reset(self):
        self.collection = []
        self.last_save = time()


class StackInfoLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
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
    logger.setLevel(level or _logging_level)

    # Elastic log formatter

    logger.addHandler(log_handler)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(_log_format_adapter)
    logger.addHandler(clh)

    return logger


log_handler = DeferLogHandler()
