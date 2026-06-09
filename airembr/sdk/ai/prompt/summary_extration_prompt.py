from typing import Set

from pydantic import BaseModel, Field

from airembr.system.utils.text.cleaners import clean_text


class ExtractedSummary(BaseModel):
    summary: str = Field(..., description="Text summary")
    keywords: Set[str] | None = Field(None, description="List of single-word keywords extracted from the text.")


def summary_extraction_system_prompt():
    prompt = f"""
You are a translation and summarization specialist. For any input text:
- Translate it into English.
- Summarize the content under 100 words, retaining all important information while removing noise. If no summarization is possible, return an empty string.
- Resolve all pronouns by replacing them with explicit, clearly identifiable entity names or IDs.
- Extract about 8 single-word keywords capturing the core meaning. Use only lowercase, generalized, domain-relevant terms that reflect underlying ideas.
- Ensure the summary contains no pronouns and remains fully coherent.
- Use no markdown formatting such as **, __, or similar, plain text.

Return only the rewritten summary and keywords. No preamble, explanation, or metadata."""
    return clean_text(prompt)


def summary_extraction_user_prompt(text):
    return f"Text to translate and summarize:\n{text}"
