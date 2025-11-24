import copy
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Set, Tuple

from durable_dot_dict.dotdict import DotDict


def deep_merge_dicts(old: Dict[Any, Any], new: Dict[Any, Any]) -> Dict[Any, Any]:
    old = DotDict(old).flat()
    new = DotDict(new).flat()
    old.update(new)
    old = DotDict() << old
    return old.to_dict()


# Small helpers for relation sorting keys
def _relation_sort_key(rel) -> Tuple[datetime, int]:
    """
    Return a tuple (ts, order) for sorting relations.
    If rel.ts is None, treat as datetime.min (so it sorts first).
    If rel.order is None, treat as 0.
    """
    ts = rel.ts if getattr(rel, "ts", None) is not None else datetime.min
    order = rel.order if getattr(rel, "order", None) is not None else 0
    return (ts, order)


def _observation_earliest_relation_key(obs) -> Tuple[datetime, int]:
    """
    Determine the earliest relation timestamp and smallest order for an Observation.
    If there are no relations, treat as (datetime.min, 0).
    """
    if not getattr(obs, "relation", None):
        return (datetime.min, 0)
    # compute min by relation sort key
    keys = [_relation_sort_key(rel) for rel in obs.relation]
    return min(keys)


def _ensure_list_of_links(val) -> List:
    """
    Normalize context to a list of InstanceLink objects.
    Accepts None, single InstanceLink, or list of InstanceLink.
    """
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def merge_observation_entities(old_entity, new_entity):
    """
    Merge two ObservationEntity objects:
    - instance: newer (new_entity) wins
    - identification: newer wins if present
    - part_of/is_a: newer wins if present
    - has_a: union (by items equality) if both present
    - traits: deep merge (deep_merge_dicts), with new overriding old at leaves
    - state: shallow merge with new overriding (but if state values are dict-like, merge them)
    - measurements: concatenated (older first)
    - consents: if any disallow (allow==False) -> final allow False; else True/None
    - other fields: prefer newer if provided
    """
    import copy
    merged = copy.deepcopy(old_entity)

    # instance & identification & basic single fields -> newer wins if exists
    merged.instance = new_entity.instance or merged.instance
    merged.identification = new_entity.identification or merged.identification
    merged.part_of = new_entity.part_of or merged.part_of
    merged.is_a = new_entity.is_a or merged.is_a

    # has_a -> merge lists uniquely by value (keep order: old then new)
    if merged.has_a is None:
        merged.has_a = []
    if new_entity.has_a:
        # append those not already present (simple equality)
        for item in new_entity.has_a:
            if item not in merged.has_a:
                merged.has_a.append(item)

    # traits -> deep merge with new overwriting leaves
    merged_traits = merged.traits or {}
    new_traits = new_entity.traits or {}
    merged.traits = deep_merge_dicts(merged_traits, new_traits)

    # state -> shallow merge; if values are dicts, use deep_merge_dicts
    merged_state = merged.state or {}
    new_state = new_entity.state or {}
    result_state = {}
    for k in set(list(merged_state.keys()) + list(new_state.keys())):
        if k in merged_state and k in new_state:
            old_val = merged_state[k]
            new_val = new_state[k]
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                result_state[k] = deep_merge_dicts(old_val, new_val)
            else:
                result_state[k] = new_val
        elif k in new_state:
            result_state[k] = new_state[k]
        else:
            result_state[k] = merged_state[k]
    merged.state = result_state

    # measurements -> concat (older first)
    merged.measurements = (merged.measurements or []) + (new_entity.measurements or [])

    # consents -> if any False -> False; else if any True -> True; else None
    cons_old = getattr(merged, "consents", None)
    cons_new = getattr(new_entity, "consents", None)
    if cons_old is None and cons_new is None:
        merged.consents = None
    else:
        # If either explicitly False -> final False
        if (cons_old is not None and cons_old.allow is False) or (cons_new is not None and cons_new.allow is False):
            merged.consents = type(cons_new or cons_old)(allow=False)
        else:
            # if any True -> True, else None
            allow_val = (cons_old.allow if cons_old is not None else None) or (
                cons_new.allow if cons_new is not None else None)
            merged.consents = type(cons_new or cons_old)(allow=bool(allow_val)) if allow_val is not None else None

    # any aux or other fields we didn't explicitly handle -> prefer newer if present
    if getattr(new_entity, "aux", None) is not None:
        merged.aux = deep_merge_dicts(getattr(merged, "aux", {}) or {}, new_entity.aux or {})

    return merged


def merge_observations(observations: Iterable) -> List:
    """
    Merge a list (or iterable) of Observation objects, grouped by observation.id.

    Returns a list of merged Observation objects (one per id). The order of returned
    merged observations is arbitrary (we return in the order of group keys).
    """
    from copy import deepcopy

    # 1) Group by id
    groups = defaultdict(list)
    for obs in observations:
        if obs is None:
            continue
        if not hasattr(obs, "id") or obs.id is None:
            continue
        groups[(obs.id, obs.session.id)].append(obs)


    merged_results = []

    for (obs_id, session_id), group in groups.items():
        # 2) Sort group by earliest relation ts (and order tie-breaker)
        group_sorted = sorted(group, key=_observation_earliest_relation_key)

        # We'll process oldest -> newest so that newer values override older ones.
        base = deepcopy(group_sorted[0])

        # Start with empty containers to accumulate
        # Entities: we want to build a mapping InstanceLink -> ObservationEntity
        merged_entities_map = {}
        for obs in group_sorted:
            # Merge entities per InstanceLink
            # normalize: obs.entities is an EntityRefs (RootModel) wrapping dict
            entities_dict = getattr(obs.entities, "root", obs.entities) if obs.entities is not None else {}
            for link, entity in (entities_dict or {}).items():
                if link not in merged_entities_map:
                    # first time -> deep copy
                    merged_entities_map[link] = copy.deepcopy(entity)
                else:
                    # merge existing with new one
                    merged_entities_map[link] = merge_observation_entities(merged_entities_map[link], entity)

        # Merge relations: gather all relations from all obs, then sort by (ts, order)
        all_relations = []
        all_aspects = []
        for obs in group_sorted:
            if obs.aspects:
                all_aspects.extend(obs.aspects)
            if getattr(obs, "relation", None):
                for rel in obs.relation:
                    all_relations.append(rel)

        # sort relations by their ts/order
        all_relations_sorted = sorted(all_relations, key=_relation_sort_key)

        # Merge context: union of InstanceLinks
        context_links: List = []
        for obs in group_sorted:
            ctx_list = _ensure_list_of_links(getattr(obs, "context", None))
            for link in ctx_list:
                if link not in context_links:
                    context_links.append(link)

        # Merge metadata: newest wins (i.e., from last observation in group_sorted)
        newest_obs = group_sorted[-1]
        merged_metadata = getattr(newest_obs, "metadata", None)

        # Merge consents: Observation.consents is ObservationConsents (allow + granted set)
        final_consents = None
        # If any observation has consents.allow False -> final allow False
        any_false = False
        granted_union: Set[str] = set()
        any_consents = False
        for obs in group_sorted:
            cons = getattr(obs, "consents", None)
            if cons is None:
                continue
            any_consents = True
            if getattr(cons, "allow", None) is False:
                any_false = True
            # if granted present (set)
            if getattr(cons, "granted", None):
                granted_union.update(cons.granted)

        if any_consents:
            # build ObservationConsents object. We assume ObservationConsents ctor accepts allow and granted
            # prefer: if any_false -> allow False, else if any True -> True, else None
            if any_false:
                final_consents = type(group_sorted[0].consents or group_sorted[-1].consents)(allow=False,
                                                                                             granted=granted_union)
            else:
                # if any allow True -> True, else None
                any_true = any(
                    getattr(obs, "consents", None) is not None and getattr(obs.consents, "allow", None) is True for obs
                    in group_sorted)
                allow_val = True if any_true else None
                # create object with allow (if not None) and granted union if any
                final_consents = type(group_sorted[0].consents or group_sorted[-1].consents)(
                    allow=bool(allow_val) if allow_val is not None else False, granted=granted_union) if (
                            granted_union or allow_val is not None) else None

        # Merge aux: deep merge across observations (older -> newer)
        merged_aux = {}
        for obs in group_sorted:
            aux = getattr(obs, "aux", None)
            if aux is not None:
                merged_aux = deep_merge_dicts(merged_aux, aux)

        # Name/aspect/source/session/other top-level fields: use newest wins (from newest_obs),
        # except id which is the group id
        merged_obs = deepcopy(newest_obs)
        merged_obs.id = obs_id
        merged_obs.aspects = list(set(all_aspects)) if all_aspects else None
        merged_obs.entities = type(newest_obs.entities)(merged_entities_map) if getattr(newest_obs, "entities",
                                                                                        None) is not None else merged_entities_map
        merged_obs.relation = all_relations_sorted
        merged_obs.context = context_links if context_links else None
        merged_obs.metadata = merged_metadata
        merged_obs.consents = final_consents
        merged_obs.aux = merged_aux if merged_aux else getattr(newest_obs, "aux", None)

        # Optionally you may want to merge name, aspect, source differently; current logic uses newest wins for those.
        merged_results.append(merged_obs)

    return merged_results
