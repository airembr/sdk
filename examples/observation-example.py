from airembr.sdk.client import AirembrClient
from airembr.sdk.model.entity import Entity
from airembr.sdk.model.observation import Observation, ObservationRelation, Init, ObservationSemantic
from airembr.sdk.model.session import Session
from airembr.sdk.service.format.formaters import format_observation

# Entities
location = Init('location').identified_by(["address", "code", "city"]).traits(
    {
        "address": "123 Main Street",
        "code": "SW1",
        "city": "London",
    }
)

person = Init("person").identified_by(["email"]).traits(
    {
        "name": "Mark",
        "surname": "Doe",
        "email": "joe.doe@gmail.com",
        "age": 61,
    },
    state={
        "location": location.ref
    }
)

product1 = Init('Product #1').traits({
        "name": "Adidas Sneakers",
        "size": 42,
    }
)

product2 = Init('Product #2').id('name', hashed=True).traits({
        "name": "Logitech Mouse",
        "price": 40.99,
    }
)

# Facts
located = ObservationRelation(
    observer=person,
    actor=person,
    objects=[location],

    type="event",
    label="located",
    traits={"by": "GPS"},
    tags=["prefix:tag"],

    semantic=ObservationSemantic(description="Mark Doe was located at 123 Main Street, London, SW1")
)

# Observations
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
    entities=(product1, product2, person),
    relation=[
        ObservationRelation(
            observer=person,
            actor=person,
            type="event",
            label="purchased",
            objects=[product1, product2],
            traits={
                "quantity": 1
            },
            tags=["prefix:tag"],
            semantic=ObservationSemantic(description="{{actor.traits.name}} {{actor.traits.surname}} Purchased {{object.traits.name}}")
        )],
)

print(format_observation(obs2))

# Send observations
client = AirembrClient(
    api="http://localhost:4002",
)
# status, response = client.observe(observations=[obs1, obs2])
status, response = client.observe(observations=[obs1, obs2], realtime='collect,store,destination')
print(status)
print(response)
