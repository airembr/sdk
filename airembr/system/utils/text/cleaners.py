def clean_text(text: str) -> str:
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        stripped = line.rstrip()  # remove trailing spaces
        if stripped:  # skip empty lines (optional)
            cleaned.append(stripped.lstrip())  # remove leading spaces too

    return "\n".join(cleaned)