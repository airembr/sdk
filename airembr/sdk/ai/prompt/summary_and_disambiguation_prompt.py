from typing import List

from pydantic import BaseModel, Field

from airembr.db.topic import topic_tags


class ClearSummary(BaseModel):
    summary: str
    topics: List[str] | None = Field(None, description="List of topics matching the text")
    keywords: List[str] | None = Field(None, description="List of single-word keywords extracted from the text.")



system_summary_prompt = (
    f"""
Claude responded: You are a translation and summarization specialist.You are a translation and summarization specialist. For any input text:

Translate it into English.
Summarize the content, retaining all important information while removing noise. If no summarization is possible, return an empty string.
Resolve all pronouns by replacing them with explicit, clearly identifiable entity names or IDs.
Extract around 5 topic tags related to the subject. Allowed topics: {topic_tags}. If none apply, leave topics as None.
Extract about 8 single-word keywords capturing the core meaning. Use only lowercase, generalized, domain-relevant terms that reflect underlying ideas.
Ensure the summary contains no pronouns and remains fully coherent.
Use no markdown formatting such as **, __, or similar.

Return only the rewritten summary, topics, and keywords. No preamble, explanation, or metadata.
    """
)

user_summary_prompt = lambda actor, text: f"""
Summarize the input text and replace all pronouns.
---

Text: `{text}`
"""