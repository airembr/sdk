import json
import logging

from airembr_sdk.logging.log_level import DEV_INFO_LEVEL, Q_INFO_LEVEL, Q_STAT_LEVEL


class CustomFormatter(logging.Formatter):
    white = "\x1b[97m"
    grey = "\x1b[37m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    lavender = "\x1b[38;5;183m"

    _format_str = "%(asctime)s [%(levelname)s] [%(error_number)s] %(message)s | %(name)s | %(filename)s | %(lineno)d"

    FORMATS = {
        logging.DEBUG: grey + _format_str + reset,
        DEV_INFO_LEVEL: magenta + _format_str + reset,
        Q_INFO_LEVEL: blue + _format_str + reset,
        Q_STAT_LEVEL: lavender + _format_str + reset,
        logging.INFO: white + _format_str + reset,
        logging.WARNING: yellow + _format_str + reset,
        logging.ERROR: red + _format_str + reset,
        logging.CRITICAL: bold_red + _format_str + reset
    }

    def format(self, record):
        if not hasattr(record, "error_number") or record.error_number is None:
            record.error_number = "N/A"
        # fallback to _format_str instead of self.format
        log_fmt = self.FORMATS.get(record.levelno, self._format_str)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class ConsoleFormatter(logging.Formatter):
    _format_str = "%(asctime)s [%(levelname)s] [%(error_number)s] %(message)s | %(name)s | %(filename)s | %(lineno)d"

    FORMATS = {
        logging.DEBUG: _format_str,
        logging.INFO: _format_str,
        logging.WARNING: _format_str,
        logging.ERROR: _format_str,
        logging.CRITICAL: _format_str
    }

    def format(self, record):
        if not hasattr(record, "error_number") or record.error_number is None:
            record.error_number = "N/A"
        log_fmt = self.FORMATS.get(record.levelno, self._format_str)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        # Ensure asctime and message are computed
        record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()

        log_record = {
            "timestamp": record.asctime,
            "level": record.levelname,
            "message": record.message,
            "name": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        return json.dumps(log_record)
