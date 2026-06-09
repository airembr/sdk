"""Ontology display functions.

Usage
-----
    from display_ontology import load_ontology, display_entity, display_ontology

    ont = load_ontology("ontology.json")

    person = next(e for e in ont if e["type"] == "person")

    print(display_entity(person))                                          # both
    print(display_entity(person, show_refs=False))                         # properties only
    print(display_entity(person, show_properties=False))                   # refs only

    print(display_ontology(ont, only="task"))                              # one type
    print(display_ontology(ont, only=["task", "project"], show_refs=False))# several
"""

import json


def load_ontology(path):
    """Load an ontology JSON file and return the list of entity dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def display_entity(entity, show_properties=True, show_refs=True):
    """Return a formatted string for a single ontology entity.

    The header (type, domain, description) is always included. Use the flags
    to choose what appears underneath it:

        show_properties=True,  show_refs=False  -> properties only
        show_properties=False, show_refs=True   -> refs only
        show_properties=True,  show_refs=True   -> both (default)
    """
    lines = []

    etype  = entity.get("type", "?")
    domain = entity.get("domain", "?")
    desc   = entity.get("description", "")
    parent = entity.get("parent")

    header = etype if not parent else f"{etype} (extends {parent})"
    lines.append(f"---")
    lines.append(f"* entity: {header}")
    lines.append(f"  domain:      {domain}")
    lines.append(f"  description: {desc}")

    if show_properties:
        props = entity.get("properties", {})
        if props:
            w = max(len(k) for k in props)
            lines.append("  traits:")
            for name, pdesc in props.items():
                lines.append(f"    {name:<{w}}  {pdesc}")

    if show_refs:
        refs = entity.get("ref", {})
        if refs:
            w = max(len(k) for k in refs)
            lines.append("  relations:")
            for target, meta in refs.items():
                phrase = f"[{meta.get('verb', '')} {meta.get('relation', '')}]"
                lines.append(f"    {target:<{w}}  {phrase}  {meta.get('description', '')}")

    return "\n".join(lines)


def display_ontology(ontology, only=None, show_properties=True, show_refs=True):
    """Return a formatted string for entities in the ontology.

    Parameters
    ----------
    ontology : list
        The loaded ontology (result of load_ontology).
    only : str or list of str, optional
        Restrict output to these entity type name(s). None means show all.
    show_properties : bool
        Include the properties block under each entity.
    show_refs : bool
        Include the refs block under each entity.
    """
    if only is not None:
        wanted = {only} if isinstance(only, str) else set(only)
        ontology = [e for e in ontology if e.get("type") in wanted]
    return "\n\n".join(
        display_entity(e, show_properties=show_properties, show_refs=show_refs)
        for e in ontology
    )


def get_entities(ontology):
    return [e.get("type") for e in ontology]


