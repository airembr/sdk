from typing import List, Optional, Dict, Tuple

from pydantic import BaseModel


class Embedding(BaseModel):
    text: str
    sparse: Optional[dict] = {}
    dense: List[float]


class EmbeddingResponse(BaseModel):
    sparse: Optional[List[Tuple[str,dict]]] = []
    dense: List[Tuple[str,List[float]]]
    model: str
    elapsed: float

    def yield_embedding(self, texts):
        dense_size = 0 if not self.dense else len(self.dense)
        sparse_size = 0 if not self.sparse else len(self.sparse)

        for i, text in enumerate(texts):
            if dense_size > 0 and i < dense_size:
                dense = self.dense[i]
            else:
                dense = []

            if sparse_size and i < sparse_size:
                sparse = self.sparse[i]
            else:
                sparse = {}

            yield Embedding(text=text, sparse=sparse, dense=dense)
