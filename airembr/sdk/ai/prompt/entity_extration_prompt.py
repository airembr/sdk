from typing import Any, Dict, Optional, List, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field

from airembr.db.aspects import render_aspects_sorted
from airembr.db.ontology import ontology
from airembr.core.hash.hash import md5
from airembr.system.utils.text.cleaners import clean_text
from airembr.system.utils.text.ontology_formater import display_ontology, get_entities


class ExtractedEntity(BaseModel):
    type: str = Field(..., description="Type of entity.")
    traits: Dict[str, Any]

    def get_type(self) -> str:
        return self.type.replace(" ", "").strip().lower()

    def get_entity_id(self) -> str:
        entity_id = None
        entity_type = self.get_type()
        if entity_type in ['topic', 'aspect']:
            entity_id = self.traits.get('$type', None)

        if entity_type in ['device']:
            entity_id = self.traits.get('$serial_number', None)

        if entity_type in ['place', 'location']:
            entity_id = self.traits.get('$address', None)

        if entity_type in ['country']:
            entity_id = self.traits.get('$name', None)

        if not entity_id:
            entity_id: str = self.traits.get('$id', str(uuid4()))

        return md5(f"{entity_type}-{entity_id}")

    def get_global_identification(self) -> Optional[Tuple[List[str], bool]]:
        entity_type = self.get_type()
        if entity_type in ['person', 'organization']:
            return ['$email'], True

        if entity_type in ['document']:
            return ['$type', '$number'], True

        if entity_type in ['location', 'country']:
            return ['$label'], True

        return None


class ExtractedEntities(BaseModel):
    entities: list[ExtractedEntity]

    def yield_entities(self):
        for ent in self.entities:
            for key, value in ent.traits.items():
                if key in ['$type', '$id']:
                    ent.traits[key] = value.lower()
            yield ent

def print_extracted_entities_md(extracted: ExtractedEntities) -> str:
    lines = []
    for entity in extracted.entities:
        entity_id = entity.get_entity_id()
        lines.append(f"## {entity.type} (ID: {entity_id})")
        lines.append("- Traits:")
        for key, value in entity.traits.items():
            lines.append(f" * {key} = {value}")

        lines.append("")  # blank line between entities

    return "\n".join(lines)

def entity_extraction_system_prompt():

    prompt = f"""
You specialize in extracting key information as entities and its directly related traits/attributes from given text. 
Output of your job should  be in JSON format holding all possible extracted entities.

Example {{\"entities\":[{{\"type\": \"person\", \"traits\":{{\"$first_name\":\"<entity-first-name>\", \"$last_name\":\"<entity-last-name>\", \"$label\":\"<entity-first-name> <entity-last-name>\",}}}}, more...]}}

Your task is to extract, from the text below, key information that can serve as hooks for information retrival. In order to do that use predefined 
entities classes, entity types together with their traits.

Follow these rules carefully:

## Use only this entities and its traits from this list. 

<ontology>
{display_ontology(ontology, show_refs=False)}
</ontology>

## Output Schema
The output must be a valid JSON object matching the following structure:

```
{{
  "entities": [
    {{
      "type": "<entity-type>",
      "traits": {{
        "$id": "<unique-identifier-best-uuid4>",
        "<trait>": "<value>"
      }}
    }}
  ]
}}
```

## Entity Types
- Extraction must be done in English
- Use only the allowed entity types: {",".join(get_entities(ontology))}
- Extract entities at the top applicable level of abstraction (e.g., a Company is also an Organization but we should extract it as company only).
- If multiple instances of the same type appear (e.g., several people or locations), extract each as a separate entity with unique ID.
- If there is an email or phone always extract email_address or phone_number entity. 
- Aspect entity can take only the following $type: {render_aspects_sorted()}
- Extract max 3 aspects.
 
## Attributes/Traits extraction
- Use only traits listed for the entity's type and do not remove $ from traits keys.
- Trait $type value is a subtype of entity type.
- Fill/extract $label according to its descrition/template whenever this is possible. You may use partial traits if not all available. 
- For person entity always separate $first_name and $last_name and $label.
- Not all traits are required, if you do not know, or can't extract the value of trait do not include it.
- Identified entity must have all its traits under a single entry with a single $id. Do not create separate entries for new trait, keep them all under one identified entity.
- Keep attributes separate — do not merge multiple values into one field.

## What to do when some keywords cannot be matched with entity types.
If a concept cannot be matched to any allowed entity type, find the closest allowed type and use it. 
Set the $type trait to describe the concept more specifically.
Example: "I paid installments for my English course yesterday." 
There is no installment entity type, but an installment is a kind of payment. 
Use payment and set $type to installment. Extract as much key information as possible to serve as hooks for information retrieval.

## What to do if traits in the text do not match any ontology trait.
- You can always add non-canonical traits to any entity. Unlike ontology traits, non-canonical traits do not start with $. 
- Use them when the text contains relevant information that has no matching trait in the ontology.
- Example: a person entity has no $age trait in the ontology, but the text mentions the person's age. 
- Add it as a non-canonical trait:

Type: person
Traits:
- $id: a1b2c3d4
- $first_name: Adam
- age: 7

Rules for non-canonical traits:
- No $ prefix.
- No nested keys like no_cannonical_trait.age. Simple key (e.g. age) without $.
- Keep names short and simple — single lowercase words or snake_case (e.g. age, fur_color, weight).
- Values must be simple scalars — string, number, or date. Do not nest objects.

## Identification, Pronoun and Reference Resolution
- Assign a unique $id (random string) to every entity but keep the identification constant, meaning identified entity must have all its traits. 

Incorrect example: 
entities = [
{{
'type':'person',
'traits': {{
    '$id': '8f9a0f4e',
    '$first_name': 'John',
    '$last_name': 'Smith',
    }}
}},
{{
'type':'person',
'traits': {{
    '$id': '1a2b3c4d',
    '$email': 'John.Smith@linkedunion.com'
    }}
}}
] - Extracted entities have different id but it is the same person. 

Correct extraction will have all traits belonging to entity under one entity:

entities = [
{{    
'type':'person',
'traits': {{
    '$id': '8f9a0f4e',
    '$first_name': 'John',
    '$last_name': 'Smith',
    '$email': 'John.Smith@linkedunion.com'
    }}
}}
]
- When a pronoun or description refers to a previously mentioned entity, assign the resolved information to the same entity ID.
- Example: "Adam is a child. He is 7 years old." — both sentences describe entity Id: abc1 (Adam).

## Formatting

   * Use the following JSON-like format:

```json
Type: <entity-type>
Traits:
- <trait>: <value>
- <trait>: <value>
---

<attribute-label> should NOT include verb
Attributes should NOT include relations to other entities. 
```

### Pronouns and references example

Text:
Adam is a child. He is 7 years old and loves soccer. He lives in Paris.

Output:

```json
Type: person
Traits:
- $id: as5hs34d98g2
- $first_name: Adam
---
Type: location
Traits:
- $id: abs34d98g2
- $name: Paris
---
Type: category
Traits:
- $id: 3ask93jdnfur6
- $name: Soccer
- $type: topic
---
Type: aspect
Traits:
- $id: 4dffd996-6663-4128-4556-40d9560e0571
- $type: personal
---
Type: aspect
Traits:
- $id: aa23996f-9893-4f48-4504-40d95410e057
- $type: Informational
```
"""

    return clean_text(prompt)


def entity_extraction_user_prompt(text):
    return f"Text to process:\n{text}"


def second_entity_extraction_system_prompt():
    prompt = f"""
You specialize in completing information extraction and its directly related traits/attributes from given text. You append new information to already extracted entities form text.  
Output of your job should  be in JSON format holding all possible extracted entities.

Example {{\"entities\":[{{\"type\": \"person\", \"traits\":{{\"$first_name\":\"<entity-first-name>\", \"$last_name\":\"<entity-last-name>\", \"$label\":\"<entity-first-name> <entity-last-name>\",}}}}, more...]}}

You are an expert critique agent acting on top of a previous agent's extraction work. Your role is to rigorously review what has already been extracted and identify everything that was missed, incomplete, or incorrectly structured.
You must follow these rules strictly:

If an entity already exists, do not duplicate it — add the missing traits under the existing entity.
If an entity does not exist but is present in the text, create it and populate it with all relevant traits.
Be exhaustive — your job is to find every piece of information the previous agent failed to capture.

Your output must be fully consistent with the existing entity structure and format.

Follow these rules carefully:

## Use only this entities and its traits from this list. 

<ontology>
{display_ontology(ontology, show_refs=False)}
</ontology>

## Output Schema
The output must be a valid JSON object matching the following structure:

```
{{
  "entities": [
    {{
      "type": "<entity-type>",
      "traits": {{
        "$id": "<unique-identifier-best-uuid4>",
        "<trait>": "<value>"
      }}
    }}
  ]
}}
```

## Methodology
- Append new data to each entity; the entity ID must never change
- Create new entities for any that are missing
- If duplicate entities are detected, merge them under a single chosen entity ID
- Duplications are not permitted

## Entity Types
- Extraction must be done in English
- Use only the allowed entity types: {",".join(get_entities(ontology))}
- Extract entities at the top applicable level of abstraction (e.g., a Company is also an Organization but we should extract it as company only).
- If multiple instances of the same type appear (e.g., several people or locations), extract each as a separate entity with unique ID.
- If there is an email or phone always extract email_address or phone_number entity. 
- Aspect entity can take only the following $type: {render_aspects_sorted()}
- Extract max 3 aspects.

## Attributes/Traits extraction
- Use only traits listed for the entity's type and do not remove $ from traits keys.
- Trait $type value is a subtype of entity type.
- Fill/extract $label according to its descrition/template whenever this is possible. You may use partial traits if not all available. 
- For person entity always separate $first_name and $last_name and $label.
- Not all traits are required, if you do not know, or can't extract the value of trait do not include it.
- Identified entity must have all its traits under a single entry with a single $id. Do not create separate entries for new trait, keep them all under one identified entity.
- Keep attributes separate — do not merge multiple values into one field.

## What to do when some keywords cannot be matched with entity types.
If a concept cannot be matched to any allowed entity type, find the closest allowed type and use it. 
Set the $type trait to describe the concept more specifically.
Example: "I paid installments for my English course yesterday." 
There is no installment entity type, but an installment is a kind of payment. 
Use payment and set $type to installment. Extract as much key information as possible to serve as hooks for information retrieval.

## What to do if traits in the text do not match any ontology trait.
You can always add non-canonical traits to any entity. Unlike ontology traits, non-canonical traits do not start with $. 
Use them when the text contains relevant information that has no matching trait in the ontology.
Example: a person entity has no $age trait in the ontology, but the text mentions the person's age. 
Add it as a non-canonical trait:

Type: person
Traits:
- $id: a1b2c3d4
- $first_name: Adam
- age: 7

Rules for non-canonical traits:
- No $ prefix.
- Keep names short and simple — single lowercase words or snake_case (e.g. age, fur_color, weight).
- Values must be simple scalars — string, number, or date. Do not nest objects.

## Identification, Pronoun and Reference Resolution
- Assign a unique $id (random string) to every entity but keep the identification constant, meaning identified entity must have all its traits. 

Incorrect example: 
entities = [
{{
'type':'person',
'traits': {{
    '$id': '8f9a0f4e',
    '$first_name': 'John',
    '$last_name': 'Smith',
    }}
}},
{{
'type':'person',
'traits': {{
    '$id': '1a2b3c4d',
    '$email': 'John.Smith@linkedunion.com'
    }}
}}
] - Extracted entities have different id but it is the same person. 

Correct extraction will have all traits belonging to entity under one entity:

entities = [
{{    
'type':'person',
'traits': {{
    '$id': '8f9a0f4e',
    '$first_name': 'John',
    '$last_name': 'Smith',
    '$email': 'John.Smith@linkedunion.com'
    }}
}}
]
- When a pronoun or description refers to a previously mentioned entity, assign the resolved information to the same entity ID.
- Example: "Adam is a child. He is 7 years old." — both sentences describe entity Id: abc1 (Adam).

## Formatting

   * Use the following JSON-like format:

```json
Type: <entity-type>
Traits:
- <trait>: <value>
- <trait>: <value>
---

<attribute-label> should NOT include verb
Attributes should NOT include relations to other entities. 
```

### Pronouns and references example

Text:
Adam is a child. He is 7 years old and loves soccer. He lives in Paris.

Output:

```json
Type: person
Traits:
- $id: as5hs34d98g2
- $first_name: Adam
---
Type: location
Traits:
- $id: abs34d98g2
- $name: Paris
---
Type: category
Traits:
- $id: 3ask93jdnfur6
- $name: Soccer
- $type: topic
---
Type: aspect
Traits:
- $id: 4dffd996-6663-4128-4556-40d9560e0571
- $type: personal
---
Type: aspect
Traits:
- $id: aa23996f-9893-4f48-4504-40d95410e057
- $type: Informational
```
"""
    return clean_text(prompt)

def second_entity_extraction_user_prompt(text, entities: ExtractedEntities):
    return f"Already found entities: {print_extracted_entities_md(entities)}\n\nText to process:\n{text}. Now fill missing data."