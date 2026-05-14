from typing import Union
from collections.abc import Mapping, Sequence

from durable_dot_dict.collection import DotDict

from airembr_sdk.model.core.instance import Instance, OBJECT_TAG_PATTERN

from airembr.model.api.request.observation import ObservationEntity

def extract_entity_link(text):
    match = OBJECT_TAG_PATTERN.search(text)
    if match:
        obj_type = match.group(1)
        obj_id = match.group(2)
        entity = f"{obj_type}#{obj_id}"
        remaining = text[match.end():]  # Everything after the closing ')'
        return entity, remaining
    return None, text  # If no match, return None and original text


def resolve_dot_dict_values(data: Union[dict, DotDict], context: DotDict):
    if isinstance(data, Mapping):
        return {k: resolve_dot_dict_values(v, context) for k, v in data.items()}
    elif isinstance(data, Sequence) and not isinstance(data, str):
        return [resolve_dot_dict_values(v, context) for v in data]
    elif isinstance(data, str) and data.startswith('$'):
        try:

            link, path = extract_entity_link(data)
            if link:
                instance = Instance(link)

                entity: ObservationEntity = context[f"entities.['{instance.link()}']"]
                if path.startswith('.'):
                    if isinstance(entity.traits, dict):
                        entity.traits = DotDict(entity.traits)
                    return entity.traits[path[1:].strip()]
                return entity.traits
            return data

        except Exception:
            return data
    else:
        return data
