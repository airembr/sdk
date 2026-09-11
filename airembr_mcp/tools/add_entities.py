from typing import Any

from airembr_sdk.client.airembr_chat import entity

from airembr_mcp import clients, config


def add_entities_to_observation(
    observation_id: str,
    observer_type: str,
    observer_id: str,
    entities: list[dict[str, Any]],
) -> dict[str, Any]:
    """Attach new entities to an existing observation.

    Args:
        observation_id: id of the observation to update.
        observer_type: type of the entity performing this update.
        observer_id: unique id of the observer.
        entities: list of {"type", "id", "traits", "label"} dicts describing the
            entities to add.
    """
    built_entities = [
        entity(item["type"], id=item.get("id"), traits=item.get("traits"), label=item.get("label")).entity
        for item in entities
    ]

    status, body = clients.call_collector_with_reauth(
        "add_entities_to_observation", observation_id, observer_type, observer_id, built_entities,
        realtime=config.REALTIME_ALL if config.X_REALTIME else None,
    )

    if not status.ok():
        raise RuntimeError(f"Failed to add entities to observation {observation_id}: {status} {body}")

    return {"status": "ok"}
