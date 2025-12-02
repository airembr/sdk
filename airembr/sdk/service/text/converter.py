def to_camel_case(text: str) -> str:
    parts = text.replace('+', ' ').replace('-', ' ').replace('_', ' ').split()
    if not parts:
        return ""
    return ''.join([word.capitalize() for word in parts])
