import logging

DEV_INFO_LEVEL = 13
Q_INFO_LEVEL = 15
Q_STAT_LEVEL = 25

def _get_logging_level(level: str) -> int:
    level = level.upper()
    if level == 'DEBUG':
        return logging.DEBUG
    if level == 'DEV_INFO':
        return DEV_INFO_LEVEL
    if level == 'Q_INFO':
        return Q_INFO_LEVEL
    if level == 'INFO':
        return logging.INFO
    if level == 'STAT':
        return Q_STAT_LEVEL
    if level == 'WARNING' or level == "WARN":
        return logging.WARNING
    if level == 'ERROR':
        return logging.ERROR
    if level == 'CRITICAL':
        return logging.CRITICAL

    return logging.WARNING