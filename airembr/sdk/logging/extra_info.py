def build(origin,
          error_number,
          object=None,
          event_id=None,
          entity_id=None,
          entity_type=None,
          flow_id=None,
          node_id=None,
          user_id=None,
          traceback=None) -> dict:
    return dict(
        origin=origin,
        class_name=object.__class__.__name__ if object else None,
        package=object.__class__.__module__ if object else None,
        event_id=event_id,
        entity_id=entity_id,
        entity_type=entity_type,
        flow_id=flow_id,
        node_id=node_id,
        user_id=user_id,
        error_number=error_number
    )


def exact(origin,
          error_number,
          event_id=None,
          entity_id=None,
          entity_type=None,
          flow_id=None,
          node_id=None,
          class_name=None,
          package=None,
          user_id=None,
          traceback=None) -> dict:
    return dict(
        origin=origin,
        class_name=class_name,
        package=package,
        event_id=event_id,
        entity_id=entity_id,
        entity_type=entity_type,
        flow_id=flow_id,
        node_id=node_id,
        user_id=user_id,
        error_number=error_number
    )
