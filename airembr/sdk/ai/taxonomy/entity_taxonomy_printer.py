from typing import List, Dict, Any
from collections import defaultdict


def get_unique_categories_md(flattened: List[Dict[str, Any]]):
    # Use a dict to keep unique categories with their definitions
    category_map = {}
    for item in flattened:
        category = item["path"]
        definition = item["definition"]
        if category not in category_map:
            category_map[category] = definition

    # Prepare Markdown table
    md_lines = ["| Category | Definition |", "|----------|------------|"]
    for category, definition in sorted(category_map.items()):
        # Escape pipe symbols in category/definition to avoid breaking table
        category_safe = category.replace("|", "\\|")
        definition_safe = definition.replace("|", "\\|")
        md_lines.append(f"| {category_safe} | {definition_safe} |")

    return "\n".join(md_lines)


def get_category_entities(flattened: List[Dict[str, Any]]) -> str:
    # Group entities by category path
    category_entities = defaultdict(list)
    for item in flattened:
        category = item["path"]
        entity = item.get("entity")
        examples = item.get("examples", [])
        if entity:
            category_entities[category].append((entity, examples))

    # Build the bullet list as a string
    lines = []
    for category, entities in sorted(category_entities.items()):
        lines.append(f"Category: {category}:")
        lines.append("Example entities:")
        for entity, examples in entities:
            examples_str = ", ".join(examples) if examples else "No examples"
            lines.append(f"  - {entity}: examples({examples_str}, etc.)")
        lines.append("  - more like that...")  # blank line between categories
        lines.append("")
    return "\n".join(lines)
