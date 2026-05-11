from typing import Any, Dict
from durable_dot_dict.dotdict import DotDict


def deep_merge_dicts(old: Dict[Any, Any], new: Dict[Any, Any]) -> Dict[Any, Any]:
    old = DotDict(old).flat()
    new = DotDict(new).flat()
    old.update(new)
    old = DotDict() << old
    return old.to_dict()
