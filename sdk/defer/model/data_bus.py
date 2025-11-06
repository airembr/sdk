from dataclasses import dataclass, asdict
from typing import Optional, Any, Union
from uuid import uuid4

from pararun.protocol.model_factory_protocol import SerializerProtocol


@dataclass
class DataBusSubscription:
    subscription_name: str
    consumer_name: str
    receiver_queue_size: int
    consumer_type:  Optional[Union[int,str]]
    initial_position: Optional[Union[int,str]]


@dataclass
class DataBus:
    topic: str
    factory: Optional[SerializerProtocol]
    subscription: DataBusSubscription

    def get_subscription_settings_as_dict(self) -> dict:
        _dict = asdict(self.subscription)
        _dict['consumer_name'] = f"{self.subscription.consumer_name}-{str(uuid4())[:6]}"
        if self.factory:
            _dict['schema'] = self.factory.schema()

        return _dict
