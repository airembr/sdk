def _clean_value(value):
    """Remove newlines and truncate long values safely for tree output."""
    if isinstance(value, str):
        # Replace any line breaks or tabs with a single space
        value = " ".join(value.split())
        if len(value) > 100:
            value = value[:100] + "..."
    return str(value)