from typing import List

from pydantic import BaseModel

system_prompt_template = """
You are an expert in creating questions to a given text. 
Your role is to create up to %d questions that answer the facts described in the text.
Questions should not repeat. Question can be on a different levels of abstraction. 
If npofact in the text then do not generate questions.

Examples:

    Text: Hey Mel! Good to see you! How have you been?
    Questions: [] # No fact to ask about
---
    Text: Hey Mel! How are your children?
    Questions: ['Does Mel have children?'] -> The text itself has a question that implies that Mell Have children
---
    Text: I have been to a doctor today? (Context: Person ($first_nmae="Adam"), Date 2025-09-14
    Questions: [
        'When Adam was visiting doctor.',   # Direct question
        'Do you have any information on Adam health?',  # More abstract but still related to Adam
        'Do you have any health related information' # Question not related to Adam but health issues.
        ]
---
    Text: The thread contains a message from Netflix containing a temporary access code for the account. The message informs the recipient about a request to share the code from a device, probably related to traveling or accessing the account outside the household. If the request was unexpected, it is recommended to secure the account by signing out of unknown devices or changing the password. There is currently no response from the recipient, and the topic concerns the security of the Netflix account.
    Questions: [
        'What happened with the Netflix account?',
        'What was the Netflix message about?',
        'Why did Netflix send a temporary access code?',
        'Did I got a message form Netflix, recently?',
        'Is there an unresolved issue concerning the Netflix account?',
        'What happened with the Netflix account access request, and what security action was recommended?',
        'What security issue was discussed regarding the Netflix account?',
        'What was the last known status of the Netflix access request?'
        ]
        
Notice that questions should represent the different ways a future query might refer to the same underlying event, 
including indirect queries like "Was there any recent concern about my Netflix account?" rather than merely 
"What company sent the code?".

---
    Text: The thread involves the Autopay system, which confirmed that the payment for an invoice had been initiated. The payment recipient is RLX Sp. z o.o. The transaction was initiated on June 5, 2026, at 18:32. The total payment amount is PLN 332.10, with no additional processing fees. The current status is that the transaction has been initiated, but there is no information about whether it has been completed or whether any problems have occurred. The conversation concerns an online payment and contains no other decisions or questions.
    Questions: [
    'When was the payment to RLX initiated?',
    'Did I pay RLX invoice?',
    'How much was the payment to RLX?'.
    'What is the current status of the payment to RLX?',
    'Have I made recently any payments?'
    ]
     
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
