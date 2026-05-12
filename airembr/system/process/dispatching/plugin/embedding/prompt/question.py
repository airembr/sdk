from typing import List

from pydantic import BaseModel

system_prompt_template = """
You are an expert in creating questions to facts in a given text. Your role is to find out if there is some entity, or fact worth remembering and create up to %d questions that answer the fact or asks about entity. 

Positive examples:

    Text: Hey Mel! Good to see you! How have you been? Context: None
    Questions: [] # None not fact or entity to remember
---
    Text: Hey Mel! Good to see you! How have you been? Context: 2024-01-01
    Questions: ['When I spoke to Mel?'] -> Possible answer: 2024-01-01

Negative examples:

    Text: Hey Caroline! Good to see you! I'm swamped with the kids & work. What's up with you? Anything new? Context: 2024-01-01
    Questions: ['Who is the person greeting Caroline in the text?'] -> No possible answer in the text or context. Questions should be empty list.

---

    Text: Hey Mel! Good to see you! How have you been? Context: None
    Questions: ['Who is being greeted in the text?', 'Who is being addressed in the text?'] #  No possible answer in the text or context. Questions should be empty list.

Expected output:
Create questions as a list of strings.
"""

user_prompt_template = """
Text:
---
%s
"""


class Questions(BaseModel):
    questions: List[str]


def get_questions_prompt(text: str, max_questions: int):
    return (
        system_prompt_template % max_questions,
        user_prompt_template % text,
        Questions,
        .5
    )
