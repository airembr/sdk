from unittest.mock import MagicMock
from datetime import datetime
from airembr.sdk.model.observation import Observation, ObservationRelation, ObservationEntity, EntityRefs
from airembr.sdk.model.instance_link import InstanceLink
from airembr.sdk.service.format.formaters import (
    format_observation, format_dotdict_fact, format_traits, format_semantic_description
)
from durable_dot_dict.dotdict import DotDict

def test_format_traits():
    traits = {"name": "John", "age": 30, "meta": {"city": "New York"}}
    formatted = format_traits(traits)
    # Expected: '(name="John", age=30, meta.city="New York")' or similar depending on DotDict.flat()
    assert 'name="John"' in formatted
    assert 'age=30' in formatted
    assert 'meta.city="New York"' in formatted

def test_format_semantic_description():
    fact = DotDict({
        "relation": {
            "type": "message",
            "label": "chat",
            "semantic": {
                "summary": "Greeting",
                "description": "User says hello",
                "context": "Room 1"
            }
        }
    })
    formatted = format_semantic_description(fact)
    assert "User says hello" in formatted
    assert "Metadata:\nFact: MESSAGE: chat" in formatted
    assert "Summary: Greeting" in formatted
    assert "Context: Room 1" in formatted

def test_format_dotdict_fact():
    fact = DotDict({
        "actor": {
            "type": "Person",
            "traits": {"name": "Alice", "_state": {"status": "online"}}
        },
        "relation": {
            "type": "speaks",
            "label": "talk",
            "semantic": {
                "summary": "Brief talk",
                "description": "Alice talking to Bob"
            },
            "object": {
                "type": "Person",
                "traits": {"name": "Bob"}
            }
        }
    })
    formatted = format_dotdict_fact(fact)
    assert "Actor: Person(name=Alice)" in formatted
    assert "Current state: (status=online)" in formatted
    assert "Relation to objects: speaks: talk" in formatted
    assert "Summary: Brief talk" in formatted
    assert "Description: Alice talking to Bob" in formatted
    assert "Object: Person(name=Bob)" in formatted

def test_format_observation():
    # Minimal mock observation for formatting test
    obs = MagicMock(spec=Observation)
    obs.id = "obs-123"
    obs.name = "Test Observation"
    obs.source = MagicMock()
    obs.source.id = "source-1"
    obs.source.label.return_value = "source-1"
    obs.entities = MagicMock()
    
    observer_link = InstanceLink.create("observer")
    entity = MagicMock()
    entity.instance.id = "o1"
    entity.instance.label.return_value = "o1"
    entity.traits = {}
    entity.consents = None
    
    obs.entities.items.return_value = [(observer_link, entity)]
    obs.entities.get.return_value = entity
    obs.entities.root = True
    
    fact = MagicMock()
    fact.label = "sent"
    fact.type = "action"
    fact.ts = datetime(2023, 1, 1, 12, 0, 0)
    fact.traits = {}
    fact.get_actor.return_value = observer_link
    fact.get_objects.return_value = []
    fact.semantic.summary = None
    fact.semantic.description = "Hello world"
    fact.semantic.context = None
    fact.timer = None
    
    obs.relation = [fact]
    obs.consents = None
    obs.context = None
    obs.metadata = None
    obs.aux = None

    formatted = format_observation(obs)
    assert "Observation: Test Observation" in formatted
    assert "ID: obs-123" in formatted
    assert "Source: source-1" in formatted
    assert "Entities:" in formatted
    assert "observer" in formatted
    assert "Fact: \"sent\" (action) @ 2023-01-01 12:00:00 UTC" in formatted
    assert "Description: Hello world" in formatted
