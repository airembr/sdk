import re
from typing import Optional


def capitalize_event_type_id(event_type_id: Optional[str]) -> str:
    if not event_type_id:
        return ""
    words = [word.capitalize() for word in event_type_id.split('-')]
    return " ".join(words)


def slugify(text):
    # Convert to lowercase
    text = text.strip().lower()
    # Keep only alphanumeric characters and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Replace spaces (one or more) with a single dash
    text = re.sub(r'\s+', '-', text)
    return text