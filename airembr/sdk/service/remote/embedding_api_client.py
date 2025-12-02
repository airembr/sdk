import requests
from typing import List, Dict, Optional, Union, Generator, Tuple

from requests import Response

from airembr.sdk.logging.log_handler import get_logger
from airembr.sdk.model.embedding.embedding import EmbeddingResponse

logger = get_logger(__name__)


class EmbeddingApiClient:

    def __init__(self, embedder_api: str, embedder_api_key: str):
        self.embedder_api = embedder_api
        self.embedder_api_key = embedder_api_key
        self.response = None

        self.headers = {
            "Authorization": f"Bearer {self.embedder_api_key}",
            "Content-Type": "application/json"
        }

    def call(self, texts: Dict[str, str],
             normalize: bool = False,
             add_bm25: bool = False) -> 'EmbeddingApiClient':
        _embedder_api = f"{self.embedder_api}/embeddings/?normalize={'true' if normalize else 'false'}&bm25={'true' if add_bm25 else 'false'}"
        self.response = requests.post(_embedder_api, json=texts, headers=self.headers)
        return self

    def get_response(self) -> Response:
        return self.response

    def get_mapped_embeddings(self, source_mapping=None) -> Optional[
        Union[EmbeddingResponse, Generator[Tuple[str, List[float]], None, None]]]:
        if self.response is not None:
            if not self.response.ok:
                raise ConnectionError(f"Error calling embedding API: {self.response.text}")

            data = self.response.json()
            if not data:
                raise ValueError(f"Error calling embedding API: {self.response.text}")

            embedding_response = EmbeddingResponse(**data)
            if source_mapping:
                return embedding_response.yield_dense_source(source_mapping)
            return embedding_response
        return None
