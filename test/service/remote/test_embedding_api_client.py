import unittest
from unittest.mock import patch, MagicMock
from airembr.sdk.service.remote.embedding_api_client import EmbeddingApiClient

class TestEmbeddingApiClient(unittest.TestCase):
    def setUp(self):
        self.client = EmbeddingApiClient("http://embed-api.com", "api-key-123")

    @patch("requests.post")
    def test_call(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        texts = {"t1": "text one"}
        self.client.call(texts, normalize=True, add_bm25=True)
        
        expected_url = "http://embed-api.com/embeddings/?normalize=true&bm25=true"
        mock_post.assert_called_once_with(expected_url, json=texts, headers=self.client.headers)
        self.assertEqual(self.client.get_response(), mock_response)

    @patch("requests.put")
    def test_call_list(self, mock_put):
        mock_response = MagicMock()
        mock_put.return_value = mock_response
        
        texts = ["text one", "text two"]
        self.client.call_list(texts, normalize=False)
        
        expected_url = "http://embed-api.com/embeddings/?normalize=false"
        mock_put.assert_called_once_with(expected_url, json=texts, headers=self.client.headers)

    @patch("requests.post")
    def test_get_mapped_embeddings(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "dense": {"t1": [0.1, 0.2]},
            "model": "test-model",
            "elapsed": 0.1
        }
        mock_post.return_value = mock_response
        
        self.client.call({"t1": "text"})
        
        # We need EmbeddingResponse model to work, let's assume it's correctly imported
        result = self.client.get_mapped_embeddings()
        self.assertIsNotNone(result)
        # result should be an EmbeddingResponse instance
        self.assertEqual(result.dense["t1"], [0.1, 0.2])
