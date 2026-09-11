from typing import Any, Optional
from uuid import uuid4

from airembr_sdk.client.airembr_chat import AiRembrChatClient, entity, event

from airembr_mcp import clients, config


def _build_entities(items: Optional[list[dict[str, Any]]]) -> list:
    built = []
    for item in items or []:
        built.append(entity(
            item["type"],
            id=item.get("id"),
            traits=item.get("traits"),
            label=item.get("label"),
        ))
    return built


def remember(
    observer_type: str,
    observer_id: str,
    fact_description: str,
    actor_type: str,
    actor_id: str,
    relation: str,
    object_entities: Optional[list[dict[str, Any]]] = None,
    context_entities: Optional[list[dict[str, Any]]] = None,
    summary: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Remember a new fact as an observation.

    Args:
        observer_type: type of the entity recording this observation (e.g. "assistant").
        observer_id: unique id of the observer.
        fact_description: free-text description of what happened.
        actor_type: entity type of the actor performing the action (e.g. "person").
        actor_id: unique id of the actor.
        relation: short verb/label describing the action (e.g. "said", "did", "noted").
        object_entities: optional list of {"type", "id", "traits", "label"} dicts the
            action is directed at.
        context_entities: optional list of {"type", "id", "traits", "label"} dicts of
            other entities present in this observation.
        summary: optional short summary of the fact.
        tags: optional list of free-text tags.
    """
    observation_id = str(uuid4())

    observer = entity(observer_type, id=observer_id)
    actor = entity(actor_type, id=actor_id)
    objects = _build_entities(object_entities)
    context = _build_entities(context_entities)

    all_entities = {observer, actor, *objects, *context}

    client = AiRembrChatClient(clients.get_collector_client())
    observation = client.observation(
        observer=observer,
        source_id=config.AIREMBR_SOURCE_ID,
        id=observation_id,
        description=fact_description,
        tags=list(tags) if tags else None,
    ).context(all_entities)

    observation.fact(
        actor=actor,
        relation=event(relation, label=relation),
        objects=objects,
        description=fact_description,
        summary=summary,
        tags=set(tags) if tags else None,
    )

    status, payload = observation.remember(
        realtime=config.REALTIME_ALL if config.X_REALTIME else None
    )

    if not status.ok():
        raise RuntimeError(f"Failed to remember observation: {status} {payload}")

    return {"observation_id": observation_id, "status": "ok"}
