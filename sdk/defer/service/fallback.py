import random

from pararun.service.timed_flag import TimedFlags
from pararun.service.logger.log_handler import get_logger
from pararun.service.singleton import Singleton

logger = get_logger(__name__)

class FallbackManager(metaclass=Singleton):

    KEY = 'pulsar_error'

    def __init__(self):
        self.flags = TimedFlags()

    def set_error_mode(self, message):
        fallback_time = random.uniform(15, 30)
        logger.warning(
            f"Falling to inline invocation due to queue error. Next check if service is back: {fallback_time}s. Details: {message}")
        self.flags.set(FallbackManager.KEY, True, fallback_time)

    def is_in_error_mode(self):
        return self.flags.get(FallbackManager.KEY)
