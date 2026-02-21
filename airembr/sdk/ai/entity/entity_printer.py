def entities_to_string(entities):
    output = []
    for entity in entities:
        output.append(f"Entity: {entity.type}")
        output.append(f"Classification: {entity.classification}")
        output.append("Attributes:")
        for key, value in entity.attributes.items():
            output.append(f" - {key}: {value}")
        output.append("")  # blank line between entities
    return "\n".join(output)

