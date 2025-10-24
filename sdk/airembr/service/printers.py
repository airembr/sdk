from typing import Any

def format_facts(facts: dict) -> str:
    """Return a human-readable string representation of a dict of Fact objects."""
    lines = []
    for fact_id, fact in facts.items():
        actor = fact.actor
        lines.append(f"\n[{actor.id}] ({actor.type})")

        # --- Actor ---
        traits_str = _format_traits(getattr(actor, "traits", {}))
        lines.append(f"  Actor: {actor.type} ({traits_str})")

        # --- Sources, Sessions ---
        lines.append(_format_field("Sources", fact.sources))
        lines.append(_format_field("Sessions", fact.sessions))

        # --- Events ---
        events = getattr(fact, "events", [])
        if events:
            lines.append(f"  Events:")
            for e in events:
                obj_info = ""
                if getattr(e, "object", None):
                    obj_traits = getattr(e.object, "traits", {})
                    obj_desc = _format_traits(obj_traits)
                    obj_info = f" → Object [{e.object.id}] ({e.object.type}, {obj_desc})"
                lines.append(f"    • {e.label} [{e.type}]{obj_info}")
        else:
            lines.append(f"  Events: None")

        # --- Context ---
        context = getattr(fact, "context", None)
        if isinstance(context, list) and context:
            lines.append(f"  Context:")
            for obj in context:
                if hasattr(obj, "type") and hasattr(obj, "id"):
                    traits_str = _format_traits(getattr(obj, "traits", {}))
                    lines.append(f"    • {obj.type} [{obj.id}] ({traits_str})")
                else:
                    lines.append(f"    • {_safe_str(obj)}")
        else:
            lines.append(f"  Context: None")

    return "\n".join(lines)


# ---------- Helpers ----------

def _format_field(label: str, value: Any) -> str:
    """Return a line for a single field."""
    if not value:
        return f"  {label}: None"
    if isinstance(value, (set, list, tuple)):
        val = ", ".join(str(v) for v in value)
        return f"  {label}: {val}"
    return f"  {label}: {value}"


def _format_traits(traits: Any) -> str:
    """Format a traits dict (or DotDict) cleanly."""
    if not traits:
        return "-"
    if isinstance(traits, dict):
        items = []
        for k, v in traits.items():
            if isinstance(v, dict):
                inner = ", ".join(f"{ik}={iv}" for ik, iv in v.items())
                items.append(f"{k}={{ {inner} }}")
            else:
                items.append(f"{k}={_safe_str(v)}")
        return ", ".join(items)
    return str(traits)


def _safe_str(value: Any) -> str:
    """Safely stringify nested or Pydantic values without printing internals."""
    if isinstance(value, (dict, list, set, tuple)):
        return str(value)
    if hasattr(value, "__dict__"):
        attrs = {
            k: v
            for k, v in vars(value).items()
            if not k.startswith("_") and "pydantic" not in k
        }
        return ", ".join(f"{k}={v}" for k, v in attrs.items())
    return str(value)
