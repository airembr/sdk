from typing import List, Optional, Dict, Tuple, Generator

from pydantic import BaseModel


class Embedding(BaseModel):
    text: str
    sparse: Optional[dict] = {}
    dense: List[float]


class EmbeddingResponse(BaseModel):
    sparse: Optional[Dict[str, dict]] = {}
    dense: Dict[str, List[float]]
    model: str
    elapsed: float

    def yield_dense_source(self, source_mapping: Dict[str, str]) -> Generator[Tuple[str, List[float]], None, None]:
        for key, vector in self.dense.items():
            if key in source_mapping:
                yield source_mapping[key], vector
