from typing import Any, Dict, Optional, List, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field

from airembr.sdk.ai.taxonomy.entity_ontology import ontology, render_ontology, yield_entity_types
from airembr.sdk.ai.taxonomy.entity_taxonomy import taxonomy
from airembr.sdk.ai.taxonomy.entity_taxonomy_converter import flatten_taxonomy
from airembr.sdk.db.aspects import aspects, render_aspects_sorted
from airembr.sdk.service.hashes.hash import md5

flat_taxonomy = flatten_taxonomy(taxonomy)


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

        return None


class ExtractedEntities(BaseModel):
    entities: list[ExtractedEntity]

    def yield_entities(self):
        for ent in self.entities:
            for key, value in ent.traits.items():
                if key in ['$type', '$id']:
                    ent.traits[key] = value.lower()
            yield ent

class SummarizedExtractedEntities(ExtractedEntities):
    summary: str = Field(..., description="Plain text summary in English.")


def _clean_text(text: str) -> str:
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        stripped = line.rstrip()  # remove trailing spaces
        if stripped:  # skip empty lines (optional)
            cleaned.append(stripped.lstrip())  # remove leading spaces too

    return "\n".join(cleaned)


def system_prompt(summary: bool, identification: bool):
    prompt = "You specialize in extracting key information as entities and its directly related traits/attributes from given text. "
    prompt += "Output should of your job be in JSON format holding all possible extracted entities."
    if summary:
        prompt += "You also specialize in summarization of the texts."
        prompt += "Example {{\"entities\":[{{\"type\": Person, \"traits\":{{\"$name\":\"<entity-name>\"}}, \"summary\": \"Summary of the text. Max 5 sentences.\"}}, more...]}}"
    else:
        prompt += "Example {{\"entities\":[{{\"type\": Person, \"traits\":{{\"$name\":\"<entity-name>\"}}}}, more...]}}"

    prompt += f"""
    Your task is to extract, from the text below, key information that can serve as hooks for information retrival. In order to do that use predefined 
    entities classes, entity types together with their traits.

    Follow these rules carefully:

    ## Use only this entities and its traits from this list. 

    {render_ontology(ontology)}

    ## Entity Types
    - Extraction must be done in English
    - Use only the entity types and traits defined above.
    - Allowed entity types: {list(yield_entity_types())}
    - Always extract at least one Topic entity with $name. If there are many topic extract many.
    - Always extract all possible aspects that are covered in text. 
      Available aspect $type: {render_aspects_sorted(aspects)}
    - Extract entities at every applicable level of abstraction (e.g., a Company is also an Organization and an Agent — extract whichever levels add meaningful information).
    - If multiple instances of the same type appear (e.g., several people or locations), extract each as a separate entity.

    ## Attributes
    - Use only traits listed for the entity's type.
    - Do not remove $ from traits keys.
    - Trait $type value is a subtype of entity type.
    - Attribute values must match the declared data type. 
    - Not all traits are required, if you do not know the value of trait do not include it.
    - One identified entity must have all its traits in this identified entity.
    - Do not use attributes to reference other entities (e.g., do not add belongs_to: some-organization). Relations between entities are not captured in attributes.
    - Keep attributes separate — do not merge multiple values into one field.
    
    ## What to do when some keywords can not be matched with entities.
    In this case lower the abstraction for entity. Each key information can be extracted as type  Entity so there is always way to 
    extract some key meaning as Entity or other lower entityt type. Example: I paid for my English course yesterday. There is not Payment entity type. The closest to Payment is Process. Because Payment is Process. The use Process and set $type = "payment". 
    Extract as many as possible key infromations that could server as a hook for information retrival.

"""

    if identification:
        prompt += """## Identification, Pronoun and Reference Resolution
    - Assign a unique $id (random string) to every entity but keep the identification conistant, meaning identified entity must have all its traits. Incorrect exmaple: 
       entities = [
        ExtractedEntity(
         type='Person',
            traits={{
                '$id': '8f9a0f4e-5b2a-4b3e-9e6a-1d2c3b4a5f6e',
                '$name': 'John Smith'
            }}
        ),
        ExtractedEntity(
         type='Person',
            traits={{
                '$id': '1a2b3c4d-5e6f-7081-92a3-b4c5d6e7f809',
                '$email': 'John.Smith@linkedunion.com'
            }}
        )
    ] - Extracted entities have different id but it is the same person. 

    Correct extraction will have all traits belonging to entity under one entity:

    entities = [
        ExtractedEntity(
        type='Person',
            traits={{
                '$id': '8f9a0f4e-5b2a-4b3e-9e6a-1d2c3b4a5f6e',
                '$name': 'John Smith',
                '$email': 'John.Smith@linkedunion.com'
            }},
        )
    ]
    - When a pronoun or description refers to a previously mentioned entity, assign the resolved information to the same entity ID.
    - Example: "Adam is a child. He is 7 years old." — both sentences describe entity Id: abc1 (Adam).

    ## Formatting

       * Use the following JSON-like format:

    ```json
    Type: <entity-type>
    Attributes:
    - <attribute_label>: <attribute_value>
    - <attribute_label>: <attribute_value>
    ---

    <attribute-label> should NOT include verb
    Attributes should NOT include relations to other entities. 
    ```

    ### Pronouns and references example

    Text:
    Adam is a child. He is 7 years old and loves soccer. He lives in Paris.

    Output:

    ```json
    Type: Person
    Attributes:
    - $id: as5hs34d98g2
    - $name: Adam  # No age as there is not age trait for person.
    ---
    Type: City
    Attributes:
    - $id: abs34d98g2
    - $type: Capital
    - $name: Paris
    ---
    Type: Sport
    Attributes:
    - $id: 3ask93jdnfur6
    - $type: soccer
    ---
    Type: Topic
    Attributes:
    - $id: aeafd996-9893-4f48-4504--40d95410e057
    - $type: personal
    ---
    Type: Aspect
    Attributes:
    - $id: 4dffd996-6663-4128-45564--40d9560e057
    - $type: informational
    ---
    Type: Aspect
    Attributes:
    - $id: aa23996-9893-4f48-4504--40d95410e057
    - $type: personal
    ```
   
    ## Simple Example

    Text:
    The European ground squirrel (Spermophilus citellus), ID: sq1984, also known as the European souslik, is a species in the squirrel
    family, Sciuridae. Like all squirrels, it is a member of the order of rodents, and it is found in central
    and southeastern Europe, with its range divided into two parts by the Carpathian Mountains. It is a colonial animal
    and mainly diurnal. The European ground squirrel excavates a branching system of tunnels up to 2 metres (6 ft) deep,
    with several entrances. This requires a habitat of short turf, such as on steppes, pasture, dry banks, sports fields,
    parks and lawns. Its short, dense fur is yellowish grey, tinged with red, with a few indistinct pale and dark spots
    on the back. Adults typically measure 20 to 23 centimetres (8 to 9 in) with a weight of 240 to 340 grams (8.5 to 12.0 oz).
    It has a slender build with a short, bushy tail, and makes a shrill alarm call that causes all other individuals
    in the vicinity to dive for cover. This European ground squirrel was photographed in Obrovisko Family Park,
    near Muráň, Slovakia.

    Output:
    Type: Animal
    Attributes:
    - $id: sq1984
    - $name: European ground squirrel
    - $species: Spermophilus citellus
    - $age: adult (20–23 cm body length, 240–340 g weight)

    -- 
    Type: Topic
    Attributes:
    - $id: aeafd996-4f48-4504-9893-50d954410e056
    - $name: Zoology
    ---
    Type: Aspect
    Attributes:
    - $id: aeafd996-9893-4f48-4504--40d95410e057
    - $type: environmental
    ---
    Type: Concept
    Attributes:
    - $id: 59afd996-4504-4f48-9893-30d95410e057
    - $name: Sciuridae
    - $domain: zoological taxonomy
    ---
    Type: Concept
    Attributes:
    - $id: 5e8c309b-f2a0-4363-af1f-5d51ac7ef2bc
    - $type: zoological
    - $name: Rodentia
    - $domain: zoological taxonomy
    ---
    Type: NaturalEntity
    Attributes:
    - $id: 4f7ab51d-f5e3-44bd-97a9-ecb5f275ad68
    - $type: mountain range
    - $name: Carpathian Mountains
    ---
    Type: Location
    Attributes:
    - $id: cc13f689-af87-4366-bbb6-6b21f99bd550
    - $type: region
    - $address: central and southeastern Europe

    ---
    Type: Place
    Attributes:
    - $id: 756598ce-a8d1-4e5b-8d75-72e4ee316988
    - $type: park
    - $name: Obrovisko Family Park
    - $address: near Muráň, Slovakia

    ---
    Type: City
    Attributes:
    - $id: d56ef58a-16e1-4bf3-8e20-71ea74aaf60e
    - $name: Muráň
    ---
    Type: Country
    Attributes:
    - $id: d23e1b44-0092-4460-9cdc-15b376ec75fb
    - $name: Slovakia
    ---
"""
    else:
        prompt += """
            ## Identification
            Add $id trait only if the text the ID of the entity is available in the text.
        
            ## Simple Example

            Text:
            The European ground squirrel (Spermophilus citellus) ID: sq1984, also known as the European souslik, is a species in the squirrel
            family, Sciuridae. Like all squirrels, it is a member of the order of rodents, and it is found in central
            and southeastern Europe, with its range divided into two parts by the Carpathian Mountains. It is a colonial animal
            and mainly diurnal. The European ground squirrel excavates a branching system of tunnels up to 2 metres (6 ft) deep,
            with several entrances. This requires a habitat of short turf, such as on steppes, pasture, dry banks, sports fields,
            parks and lawns. Its short, dense fur is yellowish grey, tinged with red, with a few indistinct pale and dark spots
            on the back. Adults typically measure 20 to 23 centimetres (8 to 9 in) with a weight of 240 to 340 grams (8.5 to 12.0 oz).
            It has a slender build with a short, bushy tail, and makes a shrill alarm call that causes all other individuals
            in the vicinity to dive for cover. This European ground squirrel was photographed in Obrovisko Family Park,
            near Muráň, Slovakia.

            Output:
            Type: Animal
            Attributes:
            - $id: sq1984   # Add only if id is available in text.
            - $name: European ground squirrel
            - $species: Spermophilus citellus
            - $age: adult (20–23 cm body length, 240–340 g weight)

            -- 
            Type: Topic
            Attributes:
            - $name: Zoology
            ---
            Type: Aspect
            Attributes:
            - $type: environmental
            ---
            Type: Concept
            Attributes:
            - $name: Sciuridae
            - $domain: zoological taxonomy
            ---
            Type: Concept
            Attributes:
            - $type: zoological
            - $name: Rodentia
            - $domain: zoological taxonomy
            ---
            Type: NaturalEntity
            Attributes:
            - $type: mountain range
            - $name: Carpathian Mountains
            ---
            Type: Location
            Attributes:
            - $type: region
            - $address: central and southeastern Europe

            ---
            Type: Place
            Attributes:
            - $type: park
            - $name: Obrovisko Family Park
            - $address: near Muráň, Slovakia

            ---
            Type: City
            Attributes:
            - $name: Muráň
            ---
            Type: Country
            Attributes:
            - $name: Slovakia
            ---
        """

    if summary:
        prompt += f"## Summarization\nSummarize the text in the English language. Keep the most relevant information in teh summary in a factual manner. Just pure facts in triplet from: Subject predicate object. Use plain text NO MARKUP."

    return _clean_text(prompt)


def user_prompt(text):
    return f"Text to process:\n{text}"
