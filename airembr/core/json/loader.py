import json
from json import JSONDecodeError

from airembr.sdk.logging.log_handler import get_logger

logger = get_logger(__name__)

def try_json(data: str):
    try:
        return json.loads(data)
    except JSONDecodeError as e:
        logger.warning(f"Could not deserialize the JSON. Details {str(e)}. ")
        return None
