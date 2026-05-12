from airembr.system.logging.log_controller import log_controller
from airembr.system.logging.log_handler import log_handler, get_installation_logger
from airembr.system.process.logging.log_saver import log_saver_worker

logger = get_installation_logger(__name__)

# TODO Check if used
def logger_guard(logs):
    return bool(logs)


async def save_logs():
    async with log_controller(log_handler, min_size=None) as logs:
        if logs:
            # Runs only if there are logs (see logger_guard) and it is deferred.
            return await log_saver_worker(logs)
        return None
