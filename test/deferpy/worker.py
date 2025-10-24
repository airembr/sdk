from typing import List

from sdk.airembr.model.observation import Observation
from sdk.defer.model.transport_context import TransportContext


async def run_function(transport_context: TransportContext, observations: List[Observation]):
    print(transport_context)
    for obs in observations:
        print(obs)