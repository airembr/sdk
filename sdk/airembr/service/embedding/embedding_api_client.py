import requests
from typing import List, Dict, Optional, Union, Generator, Tuple

from requests import Response

from sdk.airembr.model.embedding.embedding import EmbeddingResponse


def call_embedding_api(embedder_api: str, embedder_api_key: str, texts: Dict[str, str],
                       add_bm25: bool = False) -> Response:
    headers = {
        "Authorization": f"Bearer {embedder_api_key}",
        "Content-Type": "application/json"
    }

    _embedder_api = f"{embedder_api}/embeddings/?bm25={'true' if add_bm25 else 'false'}"
    return requests.post(_embedder_api, json=texts, headers=headers)


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

    def get_mapped_embeddings(self, source_mapping=None) -> Optional[Union[EmbeddingResponse,Generator[Tuple[str, List[float]], None, None]]]:
        if self.response is not None and self.response.ok:
            data = self.response.json()
            if not data:
                return None

            embedding_response = EmbeddingResponse(**data)
            if source_mapping:
                return embedding_response.yield_dense_source(source_mapping)
            return embedding_response
        return None
