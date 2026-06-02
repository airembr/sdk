from collections import defaultdict

from durable_dot_dict.dotdict import DotDict
from typing import Dict


def group_by_observation_id(rows):
    observations = {}

    for row in rows:
        obs_id = row["observation_id"]

        if obs_id not in observations:
            observations[obs_id] = {
                "observation_id": obs_id,
                "description": row["description"],
                "summary": row["summary"],
                "label": row["label"],
                "metadata_time_create": row["metadata_time_create"],
                "metadata_time_insert": row["metadata_time_insert"],
                "entities": []
            }

        observations[obs_id]["entities"].append({
            "entity_pk": row["entity_pk"],
            "entity_type": row["entity_type"],
            "traits": row["traits"],
            "stitch_ts": row["stitch_ts"],
        })

    return observations


def enrich_observations_with_descriptions(
        grouped_observations: dict,
        entity_descriptions: list,
        grouped_facts: Dict[str, dict]
) -> dict:
    """
    Adds matching origin/text_string descriptions to each entity
    in grouped_observations.

    Returns the modified grouped_observations.
    """

    descriptions_by_entity = defaultdict(list)

    for desc in entity_descriptions:
        descriptions_by_entity[desc["entity_pk"]].append({
            "origin": desc["origin"],
            "text": desc["text_string"]
        })

    for obs_id, observation in grouped_observations.items():
        facts = grouped_facts.get(obs_id, [])
        _facts = []
        for fact in facts:
            fact = DotDict(fact)
            _facts.append({
                "ts_create": fact.get('metadata.time.create', None),
                "type": fact.get('rel.type',None),
                "summary": fact.get('semantic.summary', None),
                "description": fact.get('semantic.description', None),
            })
        observation["facts"] = _facts
        for entity in observation.get("entities", []):
            entity["descriptions"] = descriptions_by_entity.get(
                entity["entity_pk"],
                []
            )

    return grouped_observations
