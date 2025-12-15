from airembr.sdk.client import AirembrClient
from airembr.sdk.model.entity import Entity
from airembr.sdk.model.observation import Observation, ObservationEntity, EntityIdentification, ObservationRelation, \
    Init
from airembr.sdk.model.session import Session

client = AirembrClient(
    api="http://localhost:4002",
)

location = Init('location').identified_by(["address", "code", "city"]).traits(
    {
        "address": "123 Main Street",
        "code": "SW1",
        "city": "London",
    }
)

person = ObservationEntity(
    instance="person",
    identification=EntityIdentification.by(["email"]),
    traits={
        "name": "Mark",
        "surname": "Doe",
        "email": "joe.doe@gmail.com",
        "age": 61,
    },
    state={
        "location": location.ref
    }
)

product = ObservationEntity(
    instance="product #1",
    traits={
        "name": "Adidas Sneakers",
        "size": 42,
    }
)

located = ObservationRelation(

    observer=person.ref,
    actor=person.ref,
    objects=[location.ref],

    type="event",
    label="located",
    traits={"by": "GPS"},
    tags=["prefix:tag"]
)

obs1 = Observation(
    id="observation-1",
    name="New Observation",
    source=Entity(id="8351737-a9ad-4c29-a01b-2f3180bec592"),
    session=Session(id="session-1"),
    entities=(location, person),
    relation=[located],
)

obs2 = Observation(
    id="observation-1",
    name="New Observation",
    source=Entity(id="8351737-a9ad-4c29-a01b-2f3180bec592"),
    session=Session(id="session-1"),
    entities=(product, person),
    relation=[
        ObservationRelation(
            observer=person.ref,
            actor=person.ref,
            type="event",
            label="purchased",
            objects=[product.ref],
            traits={
                "quantity": 1
            },
            tags=["prefix:tag"]
        )],
)

status, response = client.observe(observations=[obs1, obs2])
# status, response = client.observe(observations=[obs2], realtime='collect,store,destination')
print(status)
print(response)
