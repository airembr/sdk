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

def _render_text(observation_id, obs):
    lines = [f"Observation ID: {observation_id}"]

    create_ts = obs.get('metadata_time_create', None)
    insert_ts = obs.get('metadata_time_insert', None)
    score = obs.get('_score') or obs.get('max_similarity')

    if create_ts:
        lines.append(f"Happened: {create_ts}")

    if create_ts != insert_ts:
        lines.append(f"Recorded: {insert_ts}")

    if score:
        lines.append(f"Relevance to question: {score*100:.2f}%")

    summaries = obs.get('summaries') or (
        [{'text': obs['summary'], 'similarity': obs.get('max_similarity')}]
        if obs.get('summary') else []
    )
    descriptions = obs.get('descriptions') or (
        [{'text': obs['description'], 'similarity': obs.get('max_similarity')}]
        if obs.get('description') else []
    )

    if summaries:
        lines.append("Summaries:")
        for s in summaries:
            if isinstance(s, dict):
                sim_str = f" [{s['similarity']*100:.2f}%]" if s.get('similarity') else ''
                lines.append(f"  -{sim_str} {s['text']}")
            else:
                lines.append(f"  - {s}")

    if descriptions:
        lines.append("Descriptions:")
        for d in descriptions:
            if isinstance(d, dict):
                sim_str = f" [{d['similarity']*100:.2f}%]" if d.get('similarity') else ''
                lines.append(f"  -{sim_str} {d['text']}")
            else:
                lines.append(f"  - {d}")

    return lines

def observations_to_prompt(observations: list) -> str:
    blocks = []
    for obs in observations:
        lines = _render_text(obs.get('id', ''), obs)
        blocks.append("\n".join(lines))
    return "\n\n" + ("\n\n" + "---" + "\n\n").join(blocks)
