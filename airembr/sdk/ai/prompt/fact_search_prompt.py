import json
import yaml
from durable_dot_dict.dotdict import DotDict


def _render_dict_tree(data, indent):
    lines = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{indent}├── {key}")
                lines.extend(_render_dict_tree(value, indent + "│   "))
            else:
                lines.append(f"{indent}├── {key}: {value}")

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{indent}├── Item")
                lines.extend(_render_dict_tree(item, indent + "│   "))
            else:
                lines.append(f"{indent}├── {item}")

    return lines


def _render_yaml(observations: dict) -> str:
    result = {"observations": []}

    for observation_id, obs in observations.items():
        observation = {
            "id": observation_id,
            "summary": obs.get("summary"),
            "description": obs.get("description"),
            "entities": [],
            "facts": [],
        }

        # Entities
        for entity in obs.get("entities", []):
            try:
                traits = json.loads(entity.get("traits", "{}"))
            except Exception:
                traits = {"raw": entity.get("traits")}

            entity_node = {
                "pk": entity.get("entity_pk"),
                "type": entity.get("entity_type"),
                "traits": traits,
                "descriptions": [
                    {
                        "text": desc.get("text"),
                        "origin": desc.get("origin"),
                    }
                    for desc in entity.get("descriptions", [])
                ],
            }

            observation["entities"].append(entity_node)

        # Facts
        for fact in obs.get("facts", []):
            fact_node = {
                "actor": {
                    "pk": fact.get("actor.pk"),
                    "type": fact.get("actor.type"),
                },
                "relation": {
                    "pk": fact.get("rel.pk"),
                    "label": fact.get("rel.label"),
                },
                "object": {
                    "pk": fact.get("object.pk"),
                    "type": fact.get("object.type"),
                },
            }

            if fact.get("semantic.summary"):
                fact_node["summary"] = fact["semantic.summary"]

            description = fact.get("description")
            if description and description != fact.get("semantic.summary"):
                fact_node["description"] = description

            observation["facts"].append(fact_node)

        result["observations"].append(observation)

    return yaml.safe_dump(
        result,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )


def observations_to_prompt(observations: dict) -> str:
    blocks = []

    for observation_id, obs in observations.items():
        lines = [
            f"Observation: ID: {observation_id}",
            f"├── Summary: {obs.get('summary', '')}",
            f"├── Description: {obs.get('description', '')}",
            "├── Observed Entities",
        ]

        entities = obs.get("entities", [])

        if not entities:
            lines.append("│   └── None")

        for entity in entities:
            entity_id = entity.get("entity_pk")
            entity_type = entity.get("entity_type")
            stitch_ts = entity.get("stitch_ts")

            try:
                traits = json.loads(entity.get("traits", "{}"))
            except Exception:
                traits = {"raw": entity.get("traits")}

            lines.extend([
                f"│   ├── {entity_type} (PK: {entity_id})",
                f"│   │   ├── When Created: {stitch_ts}",
                "│   │   ├── Traits",
            ])

            trait_lines = _render_dict_tree(traits, "│   │   │   ")
            lines.extend(trait_lines or ["│   │   │   └── None"])

            descriptions = entity.get("descriptions", [])

            if descriptions:
                lines.append("│   │   └── Description:")

                if descriptions:
                    for desc in descriptions:
                        lines.append(
                            f"│   │       ├── {desc.get('text', '')}"
                        )
                else:
                    lines.append("│   │       └── None")

        facts = obs.get("facts", [])

        lines.append("└── Facts")

        if facts:
            for fact in facts:
                fact = DotDict(fact)
                ts = fact.get('ts_create', 'Unknown')
                summary = fact.get(".summary", None)
                description = fact.get("description", None)

                if not summary and not description:
                    continue

                lines.extend([
                    f"    ├── {ts}",
                ])

                if fact.get(".summary", None):
                    lines.append(
                    f"    │   ├── Summary: {fact['summary']}"
                    )

                if (
                        fact.get("description", None)
                        and fact.get("description") != fact.get("summary")
                ):
                    lines.append(
                    f"    │    └── Description: {fact['description']}"
                    )
        else:
            lines.append("    └── None")

        blocks.append("\n".join(lines))

    return "\n\n" + ("\n\n" + "=" * 80 + "\n\n").join(blocks)
