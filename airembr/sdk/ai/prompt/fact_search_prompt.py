import datetime

import json
import yaml
from dateutil.parser import parse


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


def _render_observation_text(observation_id, observations):
    score = observations.get('_score', None)

    lines = [f"Observation ID: {observation_id}"]
    if score:
        lines.append(f"Relevance: {score * 100:.2f}%")

    sorted_observations = sorted(observations.get('items', []), key=lambda x: x['metadata_time_create'], reverse=False)

    for observation in sorted_observations:
        summary = observation.get("summary", None)
        description = observation.get("description", None)
        create_ts = observation.get('metadata_time_create', None)
        if create_ts:
            create_ts = parse(str(create_ts)).strftime("%Y-%d-%m %H:%M")

        text = [f"[{create_ts}]"]

        has_text = False
        if summary:
            has_text = True
            text.append(summary)
        if description:
            has_text = True
            text.append(description)

        if not has_text:
            continue

        lines.append(" ".join(text))

    return lines

def _render_observation_hit_text(observation_id, observations):
    score = observations.get('_score', None)

    lines = [f"Observation ID: {observation_id}"]
    if score:
        lines.append(f"Relevance: {score * 100:.2f}%")

    sorted_hits = sorted(observations.get('_hits', []), key=lambda x: x[0], reverse=True)

    for hit in sorted_hits:
        create_ts = hit[2]
        if create_ts:
            create_ts = parse(str(create_ts)).strftime("%Y-%d-%m %H:%M")

        lines.append(f"[{create_ts}] {hit[1]}")

    return lines


def observations_to_prompt(observations: dict) -> str:
    blocks = []
    for obs_id, _observations in observations.items():
        lines = _render_observation_text(obs_id, _observations)
        blocks.append("\n".join(lines))
    return "\n\n" + ("\n\n" + "---" + "\n\n").join(blocks)

def observation_hits_to_prompt(observations: dict) -> str:
    blocks = []
    for obs_id, _observations in observations.items():
        lines = _render_observation_hit_text(obs_id, _observations)
        blocks.append("\n".join(lines))
    return "\n\n" + ("\n\n" + "---" + "\n\n").join(blocks)
