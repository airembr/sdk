from typing import List

from pydantic import BaseModel, Field

system_prompt_template_text = """
You are an advanced information-extraction engine.
Your task is to analyze any input text and produce a dense, noise-free knowledge report containing abstract and non-abstract facts.
Strictly focus on maximum information extraction.
"""

user_prompt_template_text = """
Extract: implicit/inferred facts (when logically supportable) that are not main topic of the text below.
Output result in a structured format the sections Implicit Facts and Intentions:
The Implicit Facts section contains a list of Facts. Each fact must specify in brackets whether it is abstract or non-abstract, and indicate whether it contains any non-abstract entities.
Section Intentions is a list of strings.

General rules:
 - Facts that are likely to happen are also non-abstract if they identify entity by name.
 - Do not confuse likelihood of fact with being abstract.
 - Abstract facts mention only general rules.

How to distinguish abstract and non-abstract facts:
 - Abstract facts: Abstract fact do not mention names, only entity types like using words like: company, client, product, person, invoice, technology, sector, same vogue date or location without details of mentioned entities. 
 - Non-abstract facts:  Non-abstract fact mention identifiable entities (usually with name) like: Clare, Adam, IBM, Invoice number #123, e-mail address, location, Organization name, etc. If any person, organization, location, etc. is named in the fact it is automatically non-abstract. Non-a


What to include in Implicit Facts
 - Logical conclusions inferred from the text supported by the facts
 - Implied relationships, motivations, emotional states
 - Unstated but strongly suggested context
 - Character traits inferred from behavior or statements
 - Implicatures that are not the main topic in text but bring insight, e.g. Clare has to take the children for a walk. Implicatures: Person is woman, mother, has children, is grown-up.
 - Entity interests inferred from behavior or statements
What to Avoid in Implicit Facts:
 - Avoid speculative or unsupported assumptions.

Examples of Implicit Facts:
 - (non-abstract, Iphone) The client can receive an Iphone as a promotional incentive for activating the e-invoice service.
 - (non-abstract, Clare)  Remind Clare to buy a toy for our dog.
 - (abstract) The client is encouraged to transition to e-invoicing for convenience.
 - (abstract) The promotion requires the client to visit the Customer Service Office within 14 days of activation.
 - (abstract) People tent to exaggerate.


What to include in Intentions
 - Future goals, decisions, commitments
 - Implied future directions

Examples of Intentions:
 - Microsoft: To continue research an development in quantum computing.
 - John: To go swimming with her children.
 
Do your job using this text:
---
%s
"""

system_prompt_template_structured = """
You are an advanced information-extraction engine.
Your task is to analyze any input text and produce a dense, noise-free knowledge report containing abstract and non-abstract facts.
Strictly focus on maximum information extraction.
"""

user_prompt_template_structured = """
Extract: implicit/inferred facts (when logically supportable) that are not main topic of the text below.
Output result in a structured format the sections 'implicit_facts' and 'intentions':
The 'implicit_facts' section contains a list of ImplicitFact objects. Each fact must specify whether it is abstract or non-abstract, and indicate whether it contains any non-abstract entities.
Section 'intentions' is a list of strings.

General rules:
 - Facts that are likely to happen are also non-abstract if they identify entity by name.
 - Do not confuse likelihood of fact with being abstract.
 - Abstract facts mention only general rules.

How to distinguish abstract and non-abstract facts:
 - Abstract facts: Abstract fact do not mention names, only entity types like using words like: company, client, product, person, invoice, technology, sector, same vogue date or location without details of mentioned entities. 
 - Non-abstract facts:  Non-abstract fact mention identifiable entities (usually with name) like: Clare, Adam, IBM, Invoice number #123, e-mail address, location, Organization name, etc. If any person, organization, location, etc. is named in the fact it is automatically non-abstract. Non-a

 
What to include in 'implicit_facts'
 - Logical conclusions inferred from the text supported by the facts
 - Implied relationships, motivations, emotional states
 - Unstated but strongly suggested context
 - Character traits inferred from behavior or statements
 - Implicatures that are not the main topic in text but bring insight, e.g. Clare has to take the children for a walk. Implicatures: Person is woman, mother, has children, is grown-up.
 - Entity interests inferred from behavior or statements
What to Avoid in 'implicit_facts':
 - Avoid speculative or unsupported assumptions.

Examples of ImplicitFacts properties in 'implicit_facts':
 - abstract=False, entity=Iphone, fact=The client can receive an Iphone as a promotional incentive for activating the e-invoice service.
 - abstract=False, entity=Clare, fact=Remind Clare to buy a toy for our dog.
 - abstract=True, fact=The client is encouraged to transition to e-invoicing for convenience.
 - abstract=True, fact=The promotion requires the client to visit the Customer Service Office within 14 days of activation.
 - abstract=True, fact=People tent to exaggerate.
    

What to include in 'intentions'
 - Future goals, decisions, commitments
 - Implied future directions

Examples of 'intentions':
 - Microsoft: To continue research an development in quantum computing.
 - John: To go swimming with her children.

Do your job using this text:
---
%s
"""

class ImplicitFact(BaseModel):
    abstract: bool = Field(..., description="Is the fact abstract or non-abstract. True for abstract, False for non-abstract")
    entity: str = Field(..., description="Entity type")
    fact: str = Field(..., description="Fact as a string")

class ImplicitReport(BaseModel):
    implicit_facts: List[ImplicitFact] = Field(..., description="List of implicit facts as list of ImplicitFact objects")
    intentions: List[str] = Field(..., description="List of intentions and plans")

    def format(self):
        lines = []

        # Separate implicit facts
        non_abstract_facts = []
        abstract_facts = []

        for fact in self.implicit_facts:
            if fact.abstract:
                abstract_facts.append(fact)
            else:
                non_abstract_facts.append(fact)

        # Non-abstract facts section
        lines.append("Non-Abstract Implicit Facts:")
        for fact in non_abstract_facts:
            entity = fact.entity if getattr(fact, "entity", None) else "no-entity"
            lines.append(f" - ({entity}): {fact.fact}")

        lines.append("")  # Blank line

        # Abstract facts section
        lines.append("Abstract Implicit Facts:")
        for fact in abstract_facts:
            entity = fact.entity if getattr(fact, "entity", None) else "no-entity"
            lines.append(f" - ({entity}): {fact.fact}")

        lines.append("")  # Blank line

        # Intentions section
        lines.append("Intentions:")
        for intention in self.intentions:
            lines.append(f" - {intention}")

        return "\n".join(lines)


def get_facts_implicit_summary_prompt(text: str, structured: bool):
    t = user_prompt_template_structured if structured else user_prompt_template_text
    return (
        system_prompt_template_structured if structured else system_prompt_template_text,
        t % text,
        .7
    )
