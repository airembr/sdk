from pydantic import BaseModel


class ClearSummary(BaseModel):
    summary: str


system_summary_prompt = (
    """
You are a translation and summarization specialist. Your task is to:

1. Translate any input text into English
2. Summarize the content, retaining all important information while removing noise
3. Resolve all pronouns by replacing them with explicit, clearly identifiable entity names or IDs
4. Ensure the output contains no pronouns and remains fully coherent

Return only the rewritten text. No preamble, no explanation, no metadata.
    """
)
user_summary_prompt = lambda actor, text: f"""
Summarize the input text and replace all pronouns.
---

Text: `{text}`
"""