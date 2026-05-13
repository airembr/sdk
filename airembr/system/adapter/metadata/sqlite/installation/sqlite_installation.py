from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)

def wait_for_sqlite_connection():
    # No need to wait for sqlite
    logger.dev_info(f"SQLite connected.")
    return True