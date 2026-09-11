from datetime import datetime
from typing import Any, Optional

from airembr_mcp import clients


def ask(
    query: str,
    min_score: float = 0.65,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict[str, Any]:
    """Ask a natural-language question over remembered facts (semantic recall).

    Args:
        query: the natural-language question to answer from memory.
        min_score: minimum similarity score (0-1) for a memory to be considered relevant.
        start_date: optional ISO-8601 lower bound on observation time.
        end_date: optional ISO-8601 upper bound on observation time.
    """
    status, payload = clients.call_gui_with_reauth(
        "ask",
        query,
        min_score=min_score,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
    )

    if not status.ok():
        raise RuntimeError(f"ask failed: {status} {payload}")

    return {
        "answer": payload.get("answer"),
        "sources": list((payload.get("memory") or {}).keys()),
    }
