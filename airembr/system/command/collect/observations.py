from typing import List, Optional, Tuple

from pararun.model.status import DispatchStatus

from airembr.system.command.collect.errors import CollectorError
from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation
from airembr.system.process.logging.log_handler import get_logger
from airembr.core.exception.exception import InvalidBotTrafficException
from airembr.system.process.logging import extra_info
from airembr.system.process.collection.collector import _observe

logger = get_logger(__name__)


async def collect_observations(observations: List[Observation] | Observation, headers: Headers) -> Tuple[
    Optional[dict], DispatchStatus | None]:
    try:
        return await _observe(observations, headers)

    except InvalidBotTrafficException as e:
        message = str(e)
        logger.info(message)
        raise CollectorError(detail=message,
                             status_code=406)
    except Exception as e:
        message = str(e)

        logger.error(f"Error when processing {observations}. Details: {message}",
                     extra=extra_info.build(origin='Collector', error_number="COL-0001")
                     )
        raise CollectorError(detail=message,
                             status_code=500)

