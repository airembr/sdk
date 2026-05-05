import json
import os

def load_ontology(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def yield_entity_types():
    for item in ontology:
        yield item.get("subtype").lower()

def render_ontology(ontology: list[dict]) -> str:
    output = []

    for item in ontology:
        subtype = item.get("subtype")
        parent = item.get("parent_id")
        level = item.get("level")
        definition = item.get("definition")
        traits = item.get("traits", {})

        traits_str = ", ".join(f"{k}: {v}" for k, v in traits.items())

        block = (
            f"Entity Type: {subtype}\n"
            f"  Parent: {parent}\n"
            f"  Level: {level}\n"
            f"  Definition: {definition}\n"
            f"  Traits and trait type: {traits_str}\n"
        )

        output.append(block)

    return "---\n".join(output)

ontology = load_ontology(os.path.join(os.path.dirname(__file__), "ontology.json"))
