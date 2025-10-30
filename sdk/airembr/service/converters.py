from typing import List

from durable_dot_dict.dotdict import DotDict

from sdk.airembr.model.fact import EntityObject, DotDictFact
from sdk.airembr.model.instance_link import InstanceLink
from sdk.airembr.model.observation import Observation


def _to_entity_object(entity):
    return EntityObject(
        id=entity.instance.id,
        pk=entity.instance.id,
        type=entity.instance.kind,
        role=entity.instance.role,
        is_a=entity.is_a.id if entity.is_a else None,
        part_of=entity.part_of.id if entity.part_of else None,
        traits=entity.traits,
    )


def yield_facts(observation: Observation):
    context_entities = [_to_entity_object(entity).model_dump(mode='json') for entity in observation.entities.root.values()]

    for relation in observation.relation:
        fact = DotDictFact()

        fact['session.id'] = observation.session.id
        fact['source.id'] = observation.source.id
        fact['relation.id'] = relation.id
        fact['relation.type'] = relation.type
        fact['relation.label'] = relation.label
        fact['relation.traits'] = relation.traits
        fact['relation.metadata.create'] = relation.ts
        fact['context'] = context_entities

        if relation.semantic:
            fact['relation.semantic.summary'] = relation.semantic.summary
            fact['relation.semantic.description'] = relation.semantic.description

        actor_link = relation.get_actor()

        if actor_link:
            actor = observation.entities.get(actor_link.link)
            if actor:
                fact['actor'] = _to_entity_object(actor).model_dump(mode='json')

        object_links: List[InstanceLink] = list(relation.get_objects())
        if object_links:
            for object_link in object_links:
                object = observation.entities.get(object_link.link)
                if object:
                    fact['relation.object'] = _to_entity_object(object).model_dump(mode='json')
                    yield fact
        else:
            # No objects
            yield fact
