from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from sdk.defer.protocol.model_factory_protocol import SerializerProtocol
from sdk.defer.protocol.queue_client_protocol import QueueProtocol


@dataclass
class Adapter:
    adapter_protocol: QueueProtocol
    serializers: Optional[Dict[str, SerializerProtocol]] = None
    override_function: Optional[Tuple[str,str]] = None
    override_batcher: Optional[Tuple[Optional[str],Optional[str], int, int, int]] = None
    init_function: Optional[Tuple[str, str]] = None
    name: Optional[str] = None
