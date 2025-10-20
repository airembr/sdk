from typing import Optional, Protocol, Dict, Any

import requests

class ApiProtocol(Protocol):
    url: str
    headers: Dict[str, str]
    response: bool
    skip: Optional[str]
    realtime: Optional[str]

    def __init__(
        self,
        url: str,
        realtime: Optional[str] = None,
        skip: Optional[str] = None,
        response: bool = True,
        context: Optional[str] = None,
    ) -> None: ...

    def remember(self, data: Dict[str, Any]) -> None: ...

class SyncApi:

    def __init__(self, url: str, realtime: Optional[str] = None, skip: Optional[str] = None, response: bool = True, context: Optional[str] = None ):
        self.response = response
        self.skip = skip
        self.realtime = realtime

        self.url = url
        headers = {
             "user-agent": "AiRembrSdkClient/0.0.1"
        }

        if self.skip:
            headers["x-skip"] = self.skip

        if self.realtime:
            headers["x-realtime"] = self.realtime

        if self.response:
            headers["x-conversation-response"] = "1"

        headers["x-context"] = context if context else "staging"

        self.headers = headers

    def remember(self, data):

        response = requests.post(self.url, headers=self.headers, json=data)

        return response.status_code, response.json()
