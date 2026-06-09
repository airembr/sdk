from typing import Optional

from datetime import datetime

from pydantic import BaseModel, Field

from airembr.system.utils.text.cleaners import clean_text


class ExtractedFact(BaseModel):
    fact: str = Field(..., description="Short fact description")
    type:  str = Field(..., description="Type: event, conference, appointment, deadline, holiday, incident, etc.")
    started_at: Optional[datetime] = Field(None, description="If fact mentions start date")
    ended_at: Optional[datetime] =  Field(None, description="If fact mentions end date")

class ExtractedEvents(BaseModel):
    events: list[ExtractedFact]


def _clean_text(text: str) -> str:
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        stripped = line.rstrip()  # remove trailing spaces
        if stripped:  # skip empty lines (optional)
            cleaned.append(stripped.lstrip())  # remove leading spaces too

    return "\n".join(cleaned)


def event_extraction_system_prompt():
    prompt = f"""
You specialize in extracting discrete events from longer observation text. Each event is described in a single, self-contained sentence capturing who did what to whom, including time and location if available.
Example input:

"At 9am on Monday, John entered the warehouse in Berlin and moved a crate to shelf B, while the security system logged an alert."

Example output:

John entered the warehouse in Berlin at 9am on Monday.
John moved a crate to shelf B at 9am on Monday.
The security system logged an alert at 9am on Monday in Berlin.

Extract each event as an atomic, self-contained sentence. Infer shared time and location from context when not explicitly stated per event.

## Methodology
- Always reference each entity in a way that distinguishes it from others — by name, surname, short name, or abbreviation (e.g. for companies)
- If needed add reference ids to make entities unique
- Make events/facts rather simple
- Split complex sentences into simple, atomic events or facts

## Output 
Structured JSON: {{"events": {{"fact":"John entered the warehouse in Berlin at 9am on Monday.", "type": "event"}}, ...]}}
"""

    return clean_text(prompt)


def event_extraction_user_prompt(text):
    return f"Text to process:\n{text}"
