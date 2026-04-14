from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from airembr.sdk.service.time.time import now_in_utc


class ExtractedTimeRange(BaseModel):
    start: datetime
    end: datetime


class ExtractedTimeSpan(BaseModel):
    is_question: bool
    is_time_scoped: bool
    time_expression_detected: Optional[str] = None
    time_range: Optional[ExtractedTimeRange] = None


system_time_span_prompt = ("""
You are a Time Scope Extraction Engine.
Your task is to determine whether a user's question requires filtering facts by a specific time constraint.
A question is TIME-SCOPED only if answering it requires limiting facts to a specific date, datetime, or time range.
If the question merely mentions time narratively but does not restrict required facts, it is NOT time-scoped.

You must:
1. Detect if the text is rather a question or a statement.
2. Detect whether the question is time-scoped. Meaning asks for more information that is time restricted.
3. Extract the time expression if present.
4. Normalize it into an exact datetime range.
5. Resolve relative expressions using CURRENT_DATETIME.
6. Return STRICT JSON ONLY.
7. Do NOT include explanations.
8. Do NOT include reasoning.
9. Do NOT include any text outside JSON.

---

TIME-SCOPED if examples:

Question ask about facts from:

* today
* yesterday
* last week/month/year
* between X and Y
* in 2020
* during 1890–1921
* this morning
* so far today
* before/after a date
* specific date
* specific datetime

NOT time-scoped examples:
* Text is not a question.
* Text is timestamped but question does not ask for some time span, eg. 2012-02-01: Have I arrived home already? 
* "Where is Paris located?"
* "When was I last time in Paris, where is Paris located?"
  (These do not restrict facts by time.)

---

NORMALIZATION RULES

All time ranges must be returned as:

{
"start": "YYYY-MM-DD HH:MM:SS",
"end":   "YYYY-MM-DD HH:MM:SS"
}

Rules:

* today →
  00:00:00 to 23:59:59 of CURRENT_DATE
* yesterday →
  previous calendar day 00:00:00 to 23:59:59
* specific year (e.g., 2020) →
  2020-01-01 00:00:00
  2020-12-31 23:59:59
* between 1890–1921 →
  1890-01-01 00:00:00
  1921-12-31 23:59:59
* exact date →
  full-day range
* if exact time provided →
  use exact boundary
* if partial date given →
  infer broadest valid range

---

OUTPUT FORMAT (STRICT)

Return ONLY:

{{
"is_question": true
"is_time_scoped": true
"time_expression_detected": string | null,
"time_range": {{
    "start": "YYYY-MM-DD HH:MM:SS",
    "end": "YYYY-MM-DD HH:MM:SS"
  }}
}}- For found time scope 

OR

{{
"is_question": false
"is_time_scoped": false
"time_expression_detected": null,
"time_range": null
}} - If no time scope is detected.

---

NO additional fields.
NO comments.
NO explanations.
NO markdown.
"""),

user_time_span_prompt = lambda text: f"""
CURRENT_DATETIME: {now_in_utc()}

QUESTION:
{text}

Return JSON only.
"""
