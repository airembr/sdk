import unittest
from unittest.mock import patch, MagicMock
from airembr.sdk.service.remote.recall_api_client import RecallApiClient

class TestRecallApiClient(unittest.TestCase):
    def test_call(self):
        client = RecallApiClient("http://recall-api.com/", "api-key-456")
        self.assertEqual(client.url, "http://recall-api.com") # Should be stripped
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_post.return_value = mock_response
            
            client.call("obs1", "some text")
            
            mock_post.assert_called_once_with(
                "http://recall-api.com/recall/obs1",
                data="some text",
                headers=client.headers
            )
            self.assertEqual(client.response, mock_response)
