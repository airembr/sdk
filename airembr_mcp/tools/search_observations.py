from datetime import datetime
from typing import Any, Optional

from airembr_mcp import clients

MAX_RESULTS = 200

SEARCH_OBSERVATIONS_DESCRIPTION = """Search observations using EQL (Entity Query Language).

EQL finds observations (events/facts) containing typed entities with named
property values.

Grammar:
  type($prop="value")       exact match (case-insensitive)
  type($prop:"value")       exact match (same as =)
  type($prop~"value")       vector similarity search (requires embeddings)
  type()                    entity of this type present, no property constraint
  A AND B                   both A and B present in the SAME observation, matched
                             independently (does NOT mean one entity satisfies both)
  NOT type(prop: value)     negation

Examples:
  location($name="Wroclaw", $type="city")
  location($name~"Wroclaw") AND person($name="Todd")
  location($name~"Wroclaw") AND person()
  NOT person(banned: true)

Notes:
- Multiple properties inside one entity predicate must all match on the SAME
  entity instance, e.g. location($name="Wroclaw", $type="city") requires one
  location entity with both properties.
- An entity with no stored properties cannot be found, even by a bare type()
  presence check.
"""


def search_observations(
    eql: str,
    start: int = 0,
    limit: int = 500,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict[str, Any]:
    status, payload = clients.call_gui_with_reauth(
        "search_observations",
        eql,
        start=start,
        limit=limit,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
    )

    if not status.ok():
        raise RuntimeError(f"search_observations failed: {status} {payload}")

    results = payload if isinstance(payload, list) else []
    truncated = len(results) > MAX_RESULTS

    return {
        "observations": results[:MAX_RESULTS],
        "truncated": truncated,
    }


search_observations.__doc__ = SEARCH_OBSERVATIONS_DESCRIPTION
