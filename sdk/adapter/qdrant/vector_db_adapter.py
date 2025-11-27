import binascii
import hashlib
from typing import List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, Modifier, Filter
from qdrant_client import models

from qdrant_client.models import PointStruct


def _uuid_to_int(uuid):
    return int.from_bytes(hashlib.sha256(uuid.encode()).digest()[:8], 'big')


def _md5_to_int(hex_hash: str):
    digest = binascii.unhexlify(hex_hash)
    return int.from_bytes(digest[:8], 'big')


class VectorDbAdapter:

    def __init__(self, qdrant_host: str, qdrant_port: int = 6333):
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self._vectors_config = {
            'dense': VectorParams(
                size=384,  # e.g. 384-dimensional vectors
                distance=Distance.COSINE
            )
        }
        self._sparse_vector_config = {
            'sparse': SparseVectorParams(
                modifier=Modifier.IDF
            )
        }

    def index(self, index: str):
        if not self.client.collection_exists(index):
            self.client.create_collection(
                collection_name=index,
                vectors_config=self._vectors_config,
                sparse_vectors_config=self._sparse_vector_config
            )

    def insert(self, index: str, records: List[Tuple[str, str, List[float], str]]):

        points = []
        for cluster_id, relation_id, hash, vector, text in records:
            vector = {
                "dense": vector
            }

            payload = {
                "rel_id": relation_id,
                "text": text,
            }

            if cluster_id:
                payload["cluster_id"] = cluster_id

            p = PointStruct(
                id=_md5_to_int(hash),
                vector=vector,
                payload=payload
            )
            points.append(p)

        self.client.upload_points(
            collection_name=index,
            points=points
        )

    def insert_cluster(self, index: str, records: List[Tuple[str, List[float]]]):

        points = []
        for cluster_id, vector in records:
            vector = {
                "dense": vector
            }

            payload = {
                "cluster_id": cluster_id,
            }

            p = PointStruct(
                id=_uuid_to_int(cluster_id),
                vector=vector,
                payload=payload
            )
            points.append(p)

        self.client.upload_points(
            collection_name=index,
            points=points
        )

    def upsert(self, index: str, points):
        self.client.upload_points(
            collection_name=index,
            points=points
        )

    def search(self, index: str, dense_vector):

        prefetch = [
            models.Prefetch(
                query=dense_vector,
                using='dense',
                limit=15,
            )
        ]

        search_result = self.client.query_points(
            collection_name=index,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=15,
            with_payload=True
        )

        # Fix: Proper iteration over search results
        for hit in search_result.points:  # Changed from `for c, hits in search_result:`
            # Send each word/token separately for streaming effect
            text = hit.payload.get('text', '')
            rel_id = hit.payload.get('rel_id', None)

            yield hit.score, rel_id, text

    def search_cluster(self, index: str, dense_vector: List[float], limit: int = 10):
        result = self.client.query_points(
            collection_name=index,
            query=dense_vector,
            limit=limit,
            with_payload=True,
            with_vectors=["dense"],
            using="dense"  # <-- specify the named vector
        )

        for point in result.points:
            yield point.score, point.payload, point.vector['dense']

    def scroll(self, index: str, filter: Filter = None, with_payload=False, with_vectors=True, limit: int = 100):

        scroll_cursor = None

        while True:
            result, scroll_cursor = self.client.scroll(
                collection_name=index,
                limit=limit,
                scroll_filter=filter,
                with_vectors=with_vectors,
                with_payload=with_payload,
                offset=scroll_cursor
            )

            for point in result:
                yield point

            if scroll_cursor is None:
                break
