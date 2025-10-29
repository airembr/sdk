import hashlib

from lib.common.singleton import Singleton
from fastembed.sparse.bm25 import Bm25
from sentence_transformers import SentenceTransformer

from tracardi.domain.flat_event import FlatEvent


def _uuid_to_int(uuid):
    return int.from_bytes(hashlib.sha256(uuid.encode()).digest()[:8], 'big')


def get_text(data):
    id = data | FlatEvent.ID

    text = data | FlatEvent.SEMANTIC_SUMMARY
    if text:
        yield id, 'summary', text

    description = data | FlatEvent.SEMANTIC_DESCRIPTION
    if description:
        yield id, 'description', description


class Embeddings(metaclass=Singleton):

    def __init__(self):
        # model=("sentence-transformers/LaBSE", 768)
        self.model = ('paraphrase-multilingual-MiniLM-L12-v2', 384)

        self.dense_embedder = SentenceTransformer(self.model[0])
        self.bm25_embedder = Bm25('Qdrant/bm25')

    def get_vectors(self, texts):
        dense_vectors = self.dense_embedder.encode(texts)
        parse_bm25 = list(self.bm25_embedder.passage_embed(texts))
        return dense_vectors, parse_bm25

    def get_embed_query(self, query):
        dense_query_vector = self.dense_embedder.encode(query).tolist()
        b25_query_vector = list(self.bm25_embedder.passage_embed(query))
        b25_query_vector = b25_query_vector[0]

        return dense_query_vector, b25_query_vector

