import hashlib
from typing import List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, Modifier
from qdrant_client import models

from qdrant_client.models import PointStruct


def _uuid_to_int(uuid):
    return int.from_bytes(hashlib.sha256(uuid.encode()).digest()[:8], 'big')


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

    def insert(self, index: str, facts, dense_vectors, bm25_vectors):
        points = [
            PointStruct(
                id=_uuid_to_int(event.id),
                vector={
                    "dense": dense_vectors[i],
                    "sparse": bm25_vectors[i]
                },
                payload={
                    "fact": text,
                    "fact_id": fact.id,
                    "event_id": event.id,
                    "actor": {"pk": fact.actor.pk, "type": fact.actor.type, "traits": fact.actor.traits},
                    "sources": fact.sources,
                    "event_label": event.label,
                    "time_insert": event.metadata.insert,
                    "time_create": event.metadata.create,
                }
            )
            for i, (fact, event, text) in enumerate(facts)
        ]

        self.client.upload_points(
            collection_name=index,
            points=points
        )
        print("Inserted points", len(points))
        print('fact_id', [p.payload['fact_id'] for p in points])
        print('event_id', [p.payload['event_id'] for p in points])

    def upsert(self, index: str, points):
        self.client.upload_points(
            collection_name=index,
            points=points
        )

    def search(self, index: str,  dense_query_vector, b25_query_vector):

        prefetch = [
            models.Prefetch(
                query=dense_query_vector,
                using='dense',
                limit=15,
            ),
            models.Prefetch(
                using='sparse',
                limit=15,
                query=models.SparseVector(**b25_query_vector.as_object())
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

            yield hit.score, text
