import logging
import traceback
import sys

from logging import Handler, LogRecord
from time import time

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from airembr_sdk.logging.log_config import LOGGING_LEVEL
from airembr_sdk.logging.log_level import get_logging_level, Q_INFO_LEVEL, DEV_INFO_LEVEL, Q_STAT_LEVEL
from airembr_sdk.logging.log_format_adapter import log_format_adapter


_logging_level = get_logging_level(LOGGING_LEVEL)

logging.addLevelName(Q_INFO_LEVEL, "Q_INFO")
logging.addLevelName(DEV_INFO_LEVEL, "DEV_INFO")
logging.addLevelName(Q_STAT_LEVEL, "STAT")


def now_in_utc(delay=None) -> datetime:
    now = datetime.utcnow().replace(tzinfo=ZoneInfo('UTC'))

    if delay is None:
        return now

    if delay < 0:
        return now - timedelta(seconds=-1 * delay)

    return now + timedelta(seconds=delay)


def stack_trace(level):
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
_log_format_adapter = log_format_adapter()


def get_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # System log formatter

    logger.addHandler(log_handler)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(_log_format_adapter)
    logger.addHandler(clh)

    return logger


def get_installation_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(_log_format_adapter)
    logger.addHandler(clh)

    return logger


class SystemLogHandler(Handler):

    def __init__(self, level=0, collection=None):
        super().__init__(level)
        if collection is None:
            collection = []
        self.collection = collection
        self.last_save = time()

    def _get(self, record, value, default_value):
        return record.__dict__.get(value, default_value)

    def emit(self, record: LogRecord):

        # Skip info and debug.
        if record.levelno <= logging.INFO:
            return

        _trace = stack_trace(record.levelname)
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
            "entity_id": self._get(record, "entity_id", None),
            "entity_type": self._get(record, "entity_type", None),
            "flow_id": self._get(record, "flow_id", None),
            "node_id": self._get(record, "node_id", None),
            "user_id": self._get(record, "user_id", None),
            "error_number": self._get(record, "error_number", None),
        }

        self.collection.append(log)

    def reset(self):
        self.collection = []
        self.last_save = time()

    def add(self, logs: list):
        self.collection.extend(logs)


log_handler = SystemLogHandler()
