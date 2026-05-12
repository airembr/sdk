from typing import List

from pydantic import BaseModel, Field


class SummaryOutput(BaseModel):
    summaries: List[str] = Field(..., description="List of facts as summary of the conversation.")
    topics: List[str] = Field(..., description="List of lowercase one-word topics in the conversation, max 5")

    def summaries_as_text(self) -> str:
        return "\n".join(self.summaries)


class SummaryPayload(SummaryOutput):
    ttl: int
    no_of_passages: int