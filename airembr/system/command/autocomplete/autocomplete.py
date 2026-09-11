from typing import Optional

from airembr.system.process.autocomplete.observation.observation_autocomplete import observation_autocomplete
from airembr.system.process.autocomplete.entity_history.entity_history_autocomplete import entity_history_autocomplete
from airembr.system.process.autocomplete.fact.fact_autocomplete import fact_autocomplete
from airembr.system.process.autocomplete.log.log_autocomplete import log_autocomplete


async def autocomplete_observation(query: Optional[str]) -> dict:
    try:
        next_values, current = await observation_autocomplete(query)
        return {
            "next": next_values,
            "current": current
        }
    except Exception as e:
        print(e)
        return []


async def autocomplete_fact(query: Optional[str]) -> dict:
    try:
        next_values, current = await fact_autocomplete(query)
        return {
            "next": next_values,
            "current": current
        }
    except Exception as e:
        print(e)
        return []


async def autocomplete_entity_history(query: Optional[str]) -> dict:
    try:
        next_values, current = await entity_history_autocomplete(query)
        return {
            "next": next_values,
            "current": current
        }
    except Exception as e:
        print(e)
        return []


async def autocomplete_log(query: Optional[str]) -> dict:
    try:
        next_values, current = await log_autocomplete(query)
        return {
            "next": next_values,
            "current": current
        }
    except Exception as e:
        print(e)
        return []
