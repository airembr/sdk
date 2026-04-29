from typing import List

from pydantic import BaseModel, Field

from airembr.sdk.db.topic import topic_tags


class ClearSummary(BaseModel):
    summary: str
    topics: List[str] | None = Field(None, description="List of topics matching the text")
    keywords: List[str] | None = Field(None, description="List of single-word keywords extracted from the text.")



system_summary_prompt = (
    f"""
You are a translation and summarization specialist. Your task is to:

1. Translate any input text into English
2. Summarize the content, retaining all important information while removing noise. If no summarization can be mage leave summary as empty string. 
3. Resolve all pronouns by replacing them with explicit, clearly identifiable entity names or IDs
4. Extract around 5 topics tags that are related to the subject of the text. Place them under topics. Allowed topics are: {topic_tags}. If not topic can be selected leave topics as None.
5. Extract about 8 single-word keywords that capture its core meaning. Place them under keywords.  Focus on high-signal words that reflect the underlying ideas. Use only lowercase words, prefer generalizable, domain-relevant terms.
6. Ensure the summary contains no pronouns and remains fully coherent
7. Do not use md markdown like **, __, etc. 

Return only the rewritten text + topics + keywords. No preamble, no explanation, no metadata.
    """
)

user_summary_prompt = lambda actor, text: f"""
Summarize the input text and replace all pronouns.
---

Text: `{text}`
"""