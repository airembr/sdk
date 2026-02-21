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
        "city": "Paris",
    }
)

person = Init("person").identified_by(["email"]).traits(
    {
        "email": "joe.doe@gmail.com",
        "interested": "sports"
    },
    state={
        "location": location.ref
    }
)

# product1 = Init('Product #1').traits({
#         "name": "Adidas Sneakers",
#         "size": 42,
#     }
# )
#
# product2 = Init('Product #2').id('name', hashed=True).traits({
#         "name": "Logitech Mouse",
#         "price": 40.99,
#     }
# )

# Facts
located = ObservationRelation(
    observer=person,
    actor=person,
    objects=[location],

    type="event",
    label="located",
    traits={"by": "GPS"},
    tags=["prefix:tag"],

    semantic=ObservationSemantic(description="Mark Doe was located at 123 Main Street, Paris, SW1")
)

# Observations
obs1 = Observation(
    id="observation-1",
    name="Location",
    source=Entity(id="cfbfccdb-e513-4632-9232-31b5af2ed94c"),
    session=Session(id="session-1"),
    entities=(person, location),
    relation=[located],
)

# obs2 = Observation(
#     id="observation-1",
#     name="Sales",
#     source=Entity(id="cfbfccdb-e513-4632-9232-31b5af2ed94c"),
#     session=Session(id="session-1"),
#     entities=(product1, product2, person),
#     relation=[
#         ObservationRelation(
#             observer=person,
#             actor=person,
#             type="event",
#             label="purchased",
#             objects=[product1, product2],
#             traits={
#                 "quantity": 1
#             },
#             tags=["prefix:tag"],
#             semantic=ObservationSemantic(description="{{actor.traits.name}} {{actor.traits.surname}} purchased {{object.traits.name}}")
#         )],
# )

# Send observations
client = AirembrClient(
    api="http://localhost:4002",
)
# status, response = client.observe(observations=[obs1, obs2])
status, response = client.observe(observations=[obs1], realtime='collect,store,destination')
print(status)
print(response)
