import unittest
from unittest.mock import patch, MagicMock
from airembr_sdk.client.airembr_api import AirembrApi

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

    @patch("airembr_sdk.client.airembr_api.QueryEntityResponse")
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

    @patch("requests.post")
    def test_remember_sends_authorization_when_token_set(self, mock_post):
        self.api.token = "token123"
        self.api.token_type = "Bearer"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        self.api.remember({"facts": []})

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"].get("Authorization"), "Bearer token123")

    @patch("requests.post")
    def test_authenticate_with_secret(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "secret-token",
            "token_type": "bearer",
        }
        mock_post.return_value = mock_response

        status, payload = self.api.authenticate_with_secret("shared-secret")

        self.assertEqual(status, 200)
        self.assertEqual(self.api.token, "secret-token")
        self.assertEqual(self.api.token_type, "bearer")
        mock_post.assert_called_once_with(
            "http://test-api.com/auth",
            headers={"Content-Type": "application/json"},
            json={"secret": "shared-secret"},
        )

    @patch("requests.patch")
    def test_add_entities_to_observation(self, mock_patch):
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {}
        mock_patch.return_value = mock_response

        status, _ = self.api.add_entities_to_observation(
            "obs-1", "assistant", "a1", [{"instance": "*person#p1"}]
        )

        self.assertEqual(status, 202)
        mock_patch.assert_called_once()
        url = mock_patch.call_args.args[0]
        self.assertEqual(url, "http://test-api.com/observation/obs-1/entities/observer/assistant/a1")
        self.assertEqual(mock_patch.call_args.kwargs["json"], [{"instance": "*person#p1"}])

    @patch("requests.get")
    def test_ask_requires_authentication(self, mock_get):
        with self.assertRaises(Exception):
            self.api.ask("what happened?")
        mock_get.assert_not_called()

    @patch("requests.get")
    def test_ask(self, mock_get):
        self.api.token = "token123"
        self.api.token_type = "Bearer"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "yes", "query": "q", "eql": "", "memory": {}}
        mock_get.return_value = mock_response

        status, payload = self.api.ask("what happened?")

        self.assertEqual(status, 200)
        self.assertEqual(payload["answer"], "yes")
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["headers"].get("Authorization"), "Bearer token123")

    @patch("requests.get")
    def test_search_observations(self, mock_get):
        self.api.token = "token123"
        self.api.token_type = "Bearer"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "obs-1"}]
        mock_get.return_value = mock_response

        status, payload = self.api.search_observations('person($name="Todd")')

        self.assertEqual(status, 200)
        self.assertEqual(payload, [{"id": "obs-1"}])
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["query"], 'person($name="Todd")')
