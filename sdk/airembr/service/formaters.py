import sys

from sdk.airembr.model.observation import Observation
from durable_dot_dict.dotdict import DotDict


def terminal_supports_colors() -> bool:
    """Return True if stdout is a terminal that supports ANSI escapes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _format_header(text: str) -> str:
    """
    Return `text` styled like selected (reverse video) when printed to terminal.
    Falls back to an ASCII boxed header when stdout is not a TTY (e.g. logs/files).
    """
    if terminal_supports_colors():
        # Use reverse video + bright for clearer visual
        return text
    # Fallback boxed header (no ANSI codes)
    border = "─" * (len(text) + 4)
    return f"┌{border}┐\n│  {text}  │\n└{border}┘"


def _clean_value(value):
    """Remove newlines and truncate long values safely for tree output."""
    if isinstance(value, str):
        # Replace any line breaks or tabs with a single space
        value = " ".join(value.split())
        if len(value) > 100:
            value = value[:100] + "..."
    return str(value)


def _format_traits_tree(traits: dict, prefix: str, is_last: bool) -> list[str]:
    """Format traits as a subtree."""
    lines = []
    if traits:
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}traits:")
        flat = DotDict(traits).flat()
        items = list(flat.items())
        for i, (k, v) in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            lines.append(f"{prefix}{'│   ' if not is_last else '    '}{connector}{k}: {_clean_value(v)}")
    return lines


def format_observation(observation: Observation) -> str:
    """Visual tree representation of Observation."""
    lines = []
    lines.append(_format_header(f"Observation: {observation.name or observation.id}"))
    lines.append(f"├── ID: {observation.id or 'N/A'}")
    lines.append(f"├── Aspect: {observation.aspect or 'N/A'}")
    source_label = observation.source.label() if hasattr(observation.source, 'label') else observation.source.id
    lines.append(f"├── Source: {source_label}")

    # --- Entities ---
    if observation.entities and observation.entities.root:
        lines.append("├── Entities:")
        entity_items = list(observation.entities.items())
        for e_idx, (link, entity) in enumerate(entity_items):
            is_last_entity = e_idx == len(entity_items) - 1
            connector = "└── " if is_last_entity else "├── "
            label = entity.instance.label() if hasattr(entity.instance, "label") else entity.instance.id
            lines.append(f"│   {connector}{link}: {label}")
            lines += _format_traits_tree(entity.traits, "│   │   ", is_last_entity)
            if entity.consents:
                lines.append(f"│   │   └── Consent: {'allowed' if entity.consents.allow else 'denied'}")

    # --- Consents (Observation level) ---
    if observation.consents:
        lines.append("├── Consents:")
        lines.append(f"│   ├── Allow: {observation.consents.allow}")
        granted = observation.consents.granted or set()
        if granted:
            lines.append(f"│   └── Granted: {', '.join(sorted(granted))}")
        else:
            lines.append(f"│   └── Granted: None")

    # --- Relations ---
    for r_idx, relation in enumerate(observation.relation):
        is_last_relation = (
                r_idx == len(observation.relation) - 1
                and not observation.context
                and not observation.metadata
                and not observation.aux
        )
        connector = "└── " if is_last_relation else "├── "
        lines.append(
            f"{connector}Facts: \"{relation.label}\" ({relation.type}) @ {relation.ts.strftime('%Y-%m-%d %H:%M:%S UTC') if relation.ts else 'Unknown time'}"
        )

        rel_prefix = "    " if is_last_relation else "│   "
        # Traits
        if relation.traits:
            lines += _format_traits_tree(relation.traits, rel_prefix, False)

        # Actor
        actor_link = relation.get_actor()
        if actor_link:
            actor_entity = observation.entities.get(actor_link.link)
            if actor_entity:
                lines.append(f"{rel_prefix}├── Actor: {actor_entity.instance.label()}")
                lines += _format_traits_tree(actor_entity.traits, rel_prefix + "│   ", False)

        # Objects
        object_links = list(relation.get_objects())
        if object_links:
            for o_idx, obj_link in enumerate(object_links):
                obj_entity = observation.entities.get(obj_link.link)
                if obj_entity:
                    obj_is_last = (o_idx == len(object_links) - 1)
                    connector = "└── " if obj_is_last else "├── "
                    lines.append(f"{rel_prefix}{connector}Object: {obj_entity.instance.label()}")
                    lines += _format_traits_tree(
                        obj_entity.traits,
                        rel_prefix + ("    " if obj_is_last else "│   "),
                        obj_is_last,
                    )
        else:
            lines.append(f"{rel_prefix}├── Object: None")

        # Semantic
        if relation.semantic:
            lines.append(f"{rel_prefix}├── Semantic:")
            if relation.semantic.summary:
                lines.append(f"{rel_prefix}│   ├── Summary: {_clean_value(relation.semantic.summary)}")
            if relation.semantic.description:
                lines.append(f"{rel_prefix}│   └── Description: {_clean_value(relation.semantic.description)}")

        # Timer
        if relation.timer:
            lines.append(f"{rel_prefix}└── Timer:")
            lines.append(f"{rel_prefix}    ├── Status: {relation.timer.status}")
            lines.append(f"{rel_prefix}    ├── Timeout: {relation.timer.timeout}")
            lines.append(f"{rel_prefix}    └── Event: {relation.timer.event}")

    # --- Context ---
    if observation.context:
        lines.append("├── Context:")
        if isinstance(observation.context, list):
            for link in observation.context:
                lines.append(f"│   ├── {link.link}")
        else:
            lines.append(f"│   └── {observation.context.link}")

    # --- Metadata ---
    meta = observation.metadata
    if meta:
        lines.append("├── Metadata:")
        if meta.application:
            app = meta.application
            lines.append(f"│   ├── App: {app.name or 'unknown'} {app.version or ''} ({app.agent})")
        if meta.device:
            dev = meta.device
            lines.append(f"│   ├── Device:")
            lines.append(f"│   │   ├── Name: {_clean_value(dev.name or dev.model or 'unknown')}")
            lines.append(f"│   │   ├── Brand: {_clean_value(dev.brand or 'unknown')}")
            if dev.ip:
                lines.append(f"│   │   ├── IP: {dev.ip}")
            if dev.resolution:
                lines.append(f"│   │   ├── Resolution: {dev.resolution}")
            if dev.orientation:
                lines.append(f"│   │   └── Orientation: {dev.orientation}")
        if meta.os:
            os = meta.os
            lines.append(
                f"│   ├── OS: {_clean_value(os.name or '')} {_clean_value(os.version or '')} ({_clean_value(os.platform or '')})"
            )
        if meta.location:
            loc = meta.location
            loc_desc = ", ".join(filter(None, [loc.city, loc.country.name if loc.country else None]))
            if loc.latitude and loc.longitude:
                loc_desc += f" ({loc.latitude:.4f}, {loc.longitude:.4f})"
            lines.append(f"│   └── Location: {_clean_value(loc_desc)}")

    # --- Aux (custom additional data) ---
    if observation.aux:
        lines.append("└── Aux:")
        aux_flat = DotDict(observation.aux).flat()
        aux_items = list(aux_flat.items())
        for i, (k, v) in enumerate(aux_items):
            connector = "└── " if i == len(aux_items) - 1 else "├── "
            lines.append(f"    {connector}{k}: {_clean_value(v)}")

    return "\n".join(lines)


def _get_traits(dot_dict):
    x = ["=".join(item) for item in dot_dict.items()]
    return ", ".join(x)


def format_dotdict(dot_dict_fact):
    """
    Formats a DotDict-like object into a readable string for embedding.
    Handles nested dot-accessible keys (e.g. 'relation.object.traits.name')
    and lists/dicts gracefully.
    """
    lines = []

    # Extract top-level information
    relation_type = dot_dict_fact.get('relation.type', '')
    relation_label = dot_dict_fact.get('relation.label', '')
    summary = dot_dict_fact.get('relation.semantic.summary', '')
    description = dot_dict_fact.get('relation.semantic.description', '')

    # Actor and Object (human readable)
    lines.append(f"\nActor: {dot_dict_fact.get('actor.type', '')}({_get_traits(dot_dict_fact.get('actor.traits', {}))})")

    lines.append(f"\nRelation to objects: {relation_type}: {relation_label}")
    lines.append(f"Summary: {summary}")
    if description:
        lines.append(f"Description: {description}")

    lines.append(f"\nObject: {dot_dict_fact.get('relation.object.type', '')}({_get_traits(dot_dict_fact.get('relation.object.traits', {}))})")

    # Contexts (if present)
    context_list = dot_dict_fact.get('context', [])
    if context_list:
        lines.append("\nContext:")
        for ctx in context_list:
            name = ctx.get('traits', {}).get('name', '')
            surname = ctx.get('traits', {}).get('surname', '')
            email = ctx.get('traits', {}).get('email', '')
            lines.append(f"  - {ctx.get('type', '')} {name} {surname} ({email})")

    # Join all lines into one string
    formatted = "\n".join(line for line in lines if line.strip())
    return formatted
