from typing import Optional, AsyncGenerator

from contextlib import asynccontextmanager

from airembr.system.config.log_config import logging_config
from airembr.system.logging.log_handler import SystemLogHandler


@asynccontextmanager
async def log_controller(log_handler: SystemLogHandler, min_size=1) -> AsyncGenerator[Optional[list], None]:
    if logging_config.save_logs and log_handler.has_logs(min_log_size=min_size):
        try:
            # Check global settings
            yield log_handler.collection

        finally:
            log_handler.reset()
    else:
        yield None
