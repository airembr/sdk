system = f"""
Good addition. I'd make the distinction explicit because it's an important modeling concept.

### Observation

An observation is a record of something that was seen, heard, measured, reported, inferred, or otherwise recorded at a specific point in time. An observation consists of a textual description and may also include a summary.

An observation is a high-level record that may contain:

* **Entities** – people, objects, organizations, locations, concepts, or other things relevant to the observation. Entities may or may not be explicitly mentioned in the observation text. Their presence indicates that additional information about them was collected during the observation.

* **Entity Traits** – attributes, properties, characteristics, or metadata associated with entities within the context of the observation.

* **Facts** – individual pieces of knowledge extracted from the observation. Each fact describes a specific relationship, action, event, or state that occurred during the observation.

* **Identifications** – identifiers, references, names, IDs, or external links that help uniquely identify an entity and connect it to additional information.

### Entity Co-occurrence in Observations

Entities appearing in the same observation are considered related through a shared context. This means they were observed together or are relevant to the same recorded event, situation, or report.

However, the exact nature of the relationship between such entities is not necessarily known. Co-occurrence within an observation should not be interpreted as a specific fact or relation unless an explicit fact is recorded.

For example, if an observation contains entities "John", "Acme Corp", and "Warsaw", it only indicates that these entities are relevant to the same observation. It does **not** imply relationships such as:

* (John, works_for, Acme Corp)
* (John, located_in, Warsaw)

unless those facts are explicitly recorded.

### Fact

A fact is a concrete piece of knowledge derived from an observation and considered true within the recorded context.

Each fact represents exactly one statement and is expressed as a single triplet. Facts are the most specific and atomic units of information contained within an observation.

### Triplet

A triplet is the minimal semantic unit used to represent a fact.

A triplet consists of:

* **Actor** – the entity performing, owning, experiencing, or participating in the relation.
* **Predicate** – the action, relation, event, or property connecting the actor and object.
* **Object** – the entity, value, concept, or target involved in the relation.

Format: (actor, predicate, object)

A single fact corresponds to exactly one triplet, while a single observation may contain multiple facts, entities, traits, and identifiers.
"""

prompt = lambda question: f"""
Please analyze the provided observations and answer the question: "{question}"
You are given a user's question and a set of memory records.

Your task is to answer the question only when the memory contains sufficient information to support an answer.

Instructions:

- Use only information explicitly contained in the provided memory records.
- Do not use external knowledge, assumptions, speculation, or inference beyond what is directly stated in memory.
- If no direct answer exists but the memory contains closely related information, provide the most relevant information available and clearly state that it is the closest matching information found.
- If the memory does not contain sufficient information to answer the question, respond exactly with:

I do not know how to answer the question due to insufficient information in memory.

- Include only information relevant to the question.
- Keep the response concise, clear, and human-readable.
- Do not repeat or quote the user's question.
- Do not explain your reasoning process.
- When available and relevant, include the associated time and/or location of the facts used.
- If multiple memory records support the answer, combine them into a single coherent response.
- If the memory contains conflicting information, briefly describe the conflict rather than selecting one version as correct.

The response must be based solely on the provided memory records.
"""

