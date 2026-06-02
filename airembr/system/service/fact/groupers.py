from durable_dot_dict.dotdict import DotDict


def group_facts_by_observation_id(facts):
    groups: dict = {}
    for fact in facts:
        obs_id = fact.get('observation.id', '')
        if obs_id not in groups:
            groups[obs_id] = []
        if isinstance(fact, DotDict):
            fact = fact.to_dict()
        groups[obs_id].append(fact)

    return groups