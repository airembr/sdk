import requests

from airembr.sdk.logging.log_handler import get_logger

logger = get_logger(__name__)


class RecallApiClient:

    def __init__(self, url: str, api_key: str):
        self.url = url.strip('/')
        self.api_key = api_key
        self.response = None

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "text/plain"
        }

    def call(self, observer_id: str, text: str) -> 'RecallApiClient':
        _endpoint = f"{self.url}/recall/{observer_id}"
        print(1, _endpoint)
        self.response = requests.post(_endpoint, data=text, headers=self.headers)
        return self
