from typing import Any, Dict, List

from pydantic import BaseModel, Field

from airembr.sdk.ai.taxonomy.entity_taxonomy import taxonomy
from airembr.sdk.ai.taxonomy.entity_taxonomy_converter import flatten_taxonomy
from airembr.sdk.ai.taxonomy.entity_taxonomy_printer import get_unique_categories_md, get_category_entities


class MemoryAnswer(BaseModel):
    answer: str


system_memory_prompt = (
    "You specialize in extracting information from a list of memory cubes that describe past memories. "
)
user_memory_prompt = lambda text, facts: f"""
Your task is to answer the question below.

Follow these rules carefully:

1. Answer only to the asked question and do not provide any additional information.
2. You can mention that you have additional information but do not reveal details.
3. Each memory code represent a fact or observation that has happened in the past. If not asked about time do not reveal it.  

---

Remembered facts:
{facts}

---

This is the question: `{text}`
"""