from typing import Any, Dict

from pydantic import BaseModel

from airembr.sdk.ai.taxonomy.entity_taxonomy import taxonomy
from airembr.sdk.ai.taxonomy.entity_taxonomy_converter import flatten_taxonomy
from airembr.sdk.ai.taxonomy.entity_taxonomy_printer import get_unique_categories_md, get_category_entities

flat_taxonomy = flatten_taxonomy(taxonomy)


class ExtractedEntity(BaseModel):
    id: int
    classification: str
    type: str
    attributes: Dict[str, Any]


class ExtractedEntities(BaseModel):
    entities: list[ExtractedEntity]


system_prompt = ("You specialize in extracting entities and its directly related attributes from given text. "
                 "Output should of your job be in JSON format holding all possible extracted entities. "
                 "Example {{\"entities\":[{{\"id\":1,\"type\":\"<abstract-entity>\",\"attributes\":{{\"name\":\"<entity-name>\"}}}}, more...]}}"),
user_prompt = lambda text: f"""
Your task is to extract entities classes, entity types together with their attributes from the text below. 

Follow these rules carefully:

1. Use only this entity classification

Entity classes + their definition should guide you how to classify entity:
{get_unique_categories_md(flat_taxonomy)}

2. Entity type extraction - use the following rules to extract entity types:

Here are some entities and examples for each class. Use this as guidance.

{get_category_entities(flat_taxonomy)}

3. Identify entities according to this rules:

   * Assign a unique `Id` to each entity.
   * Identify an abstract entity type aligned with to Entity classification provided above.
   * Resolve pronouns and references: if a pronoun or description refers to an already-mentioned entity, include its attribute under the same `Id`. For example, in "Adam is a child. He is 7 years old," `He` refers to `Adam`.

4. Entity Attributes Extraction

   * Group all attributes under the entity they belong to.
   * Each attribute should be precise and self-contained.
   * Attribute should not rate to other entity, e.g. NOT allowed attribute example belongs_to: some-organization.
   * Include numeric values, measurements, dates, locations, and descriptive characteristics.
   * Avoid merging multiple attributes into one field; keep them separate.
   * Use clear labels for attributes (e.g., `type`, `name`, `age`, `size`, `version`,etc.).
   * Labels which should not to be added as attributes: verbs, separate entities: like `location` , `organization`, `product`, etc. which should be separate entities

5. Formatting

   * Use the following JSON-like format:

```json
Id: <unique_number>
classification: <Entity class according to classification>
type: <entity_type>
Attributes:
- <attribute_label>: <attribute_value>
- <attribute_label>: <attribute_value>

---

<attribute-label> should NOT include verb
Attributes should NOT include relations to other entities. 
```

6. Additional Guidelines

   * Focus on core attributes of the entity mentioned in the text. 
   * Omit emotional statements and other non-essential information.
   * If multiple entities are present, extract each separately with a unique `Id`.
   * Include location, date, size, weight, appearance, behavior, and other key attributes when available.
   * Avoid including irrelevant information not directly describing the entity.

6. Pronouns and references example

Text:
Adam is a child. He is 7 years old and loves soccer. He lives in Paris.

Output:

```json
Id: 1
classification: Entity > Continuant > PhysicalObject > Agent
type: Person
Attributes:
- name: Adam
- age: 7 years


Id: 2
classification: Entity > Continuant > PhysicalObject > Location
type: City
Attributes:
- type: City
- name: Paris


Id: 3
classification: Entity > Occurrent > Process > Sport
type: Soccer
Attributes:
- type: soccer
```

7. Simple Example

Text:
The European ground squirrel (Spermophilus citellus), also known as the European souslik, is a species in the squirrel
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

```json
Id: 1
classification: Entity > Continuant > PhysicalObject > NaturalEntity
type: Animal
Attributes:
- name: European ground squirrel
- scientific_name: Spermophilus citellus
- common_name: European souslik
- family: Sciuridae
- order: Rodentia
- habitat: Central and Southeastern Europe, steppes, pastures, dry banks, sports fields, parks, lawns
- behavior: Colonial, diurnal
- burrow_depth: Up to 2 metres (6 ft)
- size: 20–23 cm (8–9 in)
- weight: 240–340 g (8.5–12 oz)
- fur: Short, dense, yellowish grey tinged with red, with pale and dark spots
- tail: Short, bushy

Id: 2
classification: Entity > Continuant > PhysicalObject > Location
type: Park
Attributes:
- address: Obrovisko Family Park, near Muráň, Slovakia

```

8. Extend the number of entities if possible

For the text: I hid the invoice for the coffee machine in the drawer.
Output should look for all possible entities:

```json
Id: 1
classification: Entity > Informational > Document
type: Invoice
Attributes:
- for: coffee machine

Id: 2
classification: Entity > Continuant > PhysicalObject > Artifact
type: Home Appliance
Attributes:
- type: coffee machine

Id: 3
classification: Entity > Continuant > PhysicalObject > Artifact
type: Furniture
Attributes:
- type: drawer
```

9. Strict relevance of attribute to entity

For text: The second son of Krishna Prasad Koirala, a follower of Mahatma Gandhi, Bishweshwar Prasad Koirala was raised in Banaras, Krishna Prasad Koirala was chairman of Fed. 
Incorrect output:
```json
Id: 1
classification: Entity > Continuant > PhysicalObject > Agent
type: Person
Attributes:
- name: Krishna Prasad Koirala
- follower: "Krishna Prasad Koirala"  <- DO NOT include relations to other entities. This is irrelevant information for the attributes, as it does not directly describe the entity attribute, attibute or property.
- chariman_of: "Fed"

Id: 2
type: Person
classification: Entity > Continuant > PhysicalObject > Agent
Attributes:
- name: "Bishweshwar Prasad Koirala"
- raised_in: "Banaras" <- DO NOT include relations to other entities. This is irrelevant information for the attributes, as it does not directly describe the entity attribute, attibute or property.
```

Correct OUTPUT:
``json
Id: 1
classification: Entity > Continuant > PhysicalObject > Agent
type: Person
Attributes:
- name: Krishna Prasad Koirala

Id: 2
classification: Entity > Continuant > PhysicalObject > Agent
type: Person
Attributes:
- name: "Bishweshwar Prasad Koirala"

Id: 3
classification: Entity > Continuant > PhysicalObject > Agent
type: Person
Attributes:
- name: "Mahatma Gandhi"

Id: 4
classification: Entity > Continuant > NonPhysicalObject > Organization
type: Organization
Attributes:
- name: "Fed"
```
Now it's your turn!

Text: {text}"""
