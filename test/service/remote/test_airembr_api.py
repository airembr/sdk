import unittest
from unittest.mock import patch, MagicMock
from airembr.sdk.service.remote.airembr_api import AirembrApi
from airembr.sdk.model.query.status import QueryStatus

class TestAirembrApi(unittest.TestCase):
    def setUp(self):
        self.api = AirembrApi("http://test-api.com", context="test", tenant="tenant-1")

    @patch("requests.post")
    def test_authenticate(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token123",
            "token_type": "Bearer"
        }
        mock_post.return_value = mock_response

        status, payload = self.api.authenticate("user", "pass")
        
        self.assertEqual(status, 200)
        self.assertEqual(self.api.token, "token123")
        self.assertEqual(self.api.token_type, "Bearer")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_remember(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "session1": {
                "id": "s1",
                "ttl": 3600,
                "passages": []
            }
        }
        mock_post.return_value = mock_response

        data = {"facts": []}
        status, sessions = self.api.remember(data)
        
        self.assertEqual(status, 200)
        self.assertIn("session1", sessions) # MemorySessions is a dict
        mock_post.assert_called_once()

    @patch("airembr.sdk.service.remote.airembr_api.QueryEntityResponse")
    @patch("requests.get")
    def test_query_stitched_entity(self, mock_get, mock_query_resp):
        self.api.token = "token123"
        self.api.token_type = "Bearer"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": "e1"}],
            "total": 1
        }
        mock_get.return_value = mock_response
        
        expected_response = MagicMock()
        mock_query_resp.return_value = expected_response

        status, response = self.api.query_stitched_entity("query string", entity_type="person")
        
        self.assertEqual(status, 200)
        self.assertEqual(response, expected_response)
        mock_get.assert_called_once()

    @patch("requests.post")
    def test_query_facts(self, mock_post):
        self.api.token = "token123"
        self.api.token_type = "Bearer"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": "f1"}],
            "total": 1
        }
        mock_post.return_value = mock_response

        status, response = self.api.query_facts("query string")
        
        self.assertEqual(status, 200)
        self.assertEqual(len(response.result), 1)
        mock_post.assert_called_once()
