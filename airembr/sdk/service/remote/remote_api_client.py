import requests

class RemoteApiClient:

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.response = None

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.request = requests
