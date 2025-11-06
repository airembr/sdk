from pararun.config import Config
import requests
from pararun.service.logger.log_handler import get_logger

config = Config()

logger = get_logger(__name__)

def fallback_on_error(payload, adapter_name: str):
    fail_over_server_api = config.fail_over_server_api
    fail_over_server_token = config.fail_over_server_token

    if fail_over_server_api is None or fail_over_server_token is None:
        logger.info("Fail-over server not configured.")
        return

    response = requests.post(
        fail_over_server_api,
        headers={'Authorization': f'Bearer {fail_over_server_token}'},
        json={
            "headers": {
                'x-adapter': adapter_name,
                'x-restore': 'pulsar'
            },
            "payload": payload.model_dump(mode='json')
        }
    )

    if response.status_code != 200:
        raise ConnectionError(f"Could not connect to fail over server {fail_over_server_api}.")