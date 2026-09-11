"""Round-trip test for the observation exporter.

Drives the public ``export_observations`` async generator through a fake adapter
that returns rows shaped exactly like ``result >> mapping`` output (nested
``DotDict``s keyed by ``FlatObs``/``FlatFact``/``FlatEntityHistory`` property
paths). This exercises the full reconstruction path — paging, the duplicate-id
``seen`` dedup across page boundaries, entity/observer wiring, relation grouping,
and trait clean-up — without needing a live StarRocks instance.

It then dumps each reconstructed ``Observation`` to JSON and reloads it back into
an ``Observation`` to prove the export is replay-shaped (the same form accepted
by the ``POST /`` collection endpoint).

Run: ``cd sdk && .venv/bin/python -m pytest test/system/process/exporting -q``
"""

import json
import asyncio

from durable_dot_dict.dotdict import DotDict

from airembr.model.bigdata.flat_obs import FlatObs
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.model.api.request.observation import Observation
from airembr.system.process.exporting.observation_exporter import export_observations

SOURCE_ID = "source-1"

# Primary keys for the entities in the fixture.
OBSERVER_PK = "pk_user"
PRODUCT_PK = "pk_product"
CART_PK = "pk_cart"
REL_PK = "pk_rel_viewed"


def _row(values: dict) -> DotDict:
    """Build a nested DotDict the same way ``result >> mapping`` does."""
    dot = DotDict({})
    for key, value in values.items():
        dot[key] = value
    return dot


# Two text versions of observation "obs-1" (duplicate id) + a relation-less
# observation "obs-2". Ordered by (id, ts) so the duplicate ids are adjacent.
OBS_ROWS = [
    _row({FlatObs.ID: "obs-1", FlatObs.SOURCE_ID: SOURCE_ID, FlatObs.SESSION_ID: "sess-1",
          FlatObs.LABEL: "page view", FlatObs.SUMMARY: "Bob viewed a widget",
          FlatObs.DESCRIPTION: "first version"}),
    _row({FlatObs.ID: "obs-1", FlatObs.SOURCE_ID: SOURCE_ID, FlatObs.SESSION_ID: "sess-1",
          FlatObs.LABEL: "page view", FlatObs.SUMMARY: "Bob viewed a widget (edited)",
          FlatObs.DESCRIPTION: "second version"}),
    _row({FlatObs.ID: "obs-2", FlatObs.SOURCE_ID: SOURCE_ID, FlatObs.SESSION_ID: "sess-2",
          FlatObs.LABEL: "signup", FlatObs.SUMMARY: "Bob signed up"}),
]

# obs-1 produces two facts for one relation (two objects: product + cart),
# sharing the same rel_pk. obs-2 has no facts (relation-less).
FACT_ROWS = [
    _row({FlatFact.OBS_ID: "obs-1", FlatFact.SOURCE_ID: SOURCE_ID, FlatFact.OBSERVER_PK: OBSERVER_PK,
          FlatFact.ACTOR_PK: OBSERVER_PK, FlatFact.ACTOR_TYPE: "user", FlatFact.ACTOR_ID: "u1",
          FlatFact.OBJECT_PK: PRODUCT_PK, FlatFact.OBJECT_TYPE: "product", FlatFact.OBJECT_ID: "p1",
          FlatFact.REL_PK: REL_PK, FlatFact.REL_LABEL: "viewed", FlatFact.REL_TYPE: "event",
          FlatFact.SEMANTIC_SUMMARY: "Bob viewed Widget", FlatFact.SUBJECTIVE: 1,
          FlatFact.TAGS: ["web"], FlatFact.ID: "fact-1"}),
    _row({FlatFact.OBS_ID: "obs-1", FlatFact.SOURCE_ID: SOURCE_ID, FlatFact.OBSERVER_PK: OBSERVER_PK,
          FlatFact.ACTOR_PK: OBSERVER_PK, FlatFact.ACTOR_TYPE: "user", FlatFact.ACTOR_ID: "u1",
          FlatFact.OBJECT_PK: CART_PK, FlatFact.OBJECT_TYPE: "cart", FlatFact.OBJECT_ID: "c1",
          FlatFact.REL_PK: REL_PK, FlatFact.REL_LABEL: "viewed", FlatFact.REL_TYPE: "event",
          FlatFact.SEMANTIC_SUMMARY: "Bob viewed Widget", FlatFact.SUBJECTIVE: 1,
          FlatFact.TAGS: ["web"], FlatFact.ID: "fact-2"}),
]

ENTITY_ROWS = [
    # obs-1 entities: user (observer + actor), product, cart, and the relation-as-event entity.
    _row({FlatEntityHistory.OBS_ID: "obs-1", FlatEntityHistory.OBSERVER_PK: OBSERVER_PK,
          FlatEntityHistory.ENTITY_PK: OBSERVER_PK, FlatEntityHistory.ENTITY_TYPE: "user",
          FlatEntityHistory.ENTITY_ID: "u1", FlatEntityHistory.ENTITY_LABEL: "Bob",
          FlatEntityHistory.ENTITY_TRAITS: {"name": "Bob"}}),
    _row({FlatEntityHistory.OBS_ID: "obs-1", FlatEntityHistory.OBSERVER_PK: OBSERVER_PK,
          FlatEntityHistory.ENTITY_PK: PRODUCT_PK, FlatEntityHistory.ENTITY_TYPE: "product",
          FlatEntityHistory.ENTITY_ID: "p1", FlatEntityHistory.ENTITY_LABEL: "Widget",
          FlatEntityHistory.ENTITY_TRAITS: {"sku": "X"}}),
    _row({FlatEntityHistory.OBS_ID: "obs-1", FlatEntityHistory.OBSERVER_PK: OBSERVER_PK,
          FlatEntityHistory.ENTITY_PK: CART_PK, FlatEntityHistory.ENTITY_TYPE: "cart",
          FlatEntityHistory.ENTITY_ID: "c1", FlatEntityHistory.ENTITY_TRAITS: {"items": 3}}),
    _row({FlatEntityHistory.OBS_ID: "obs-1", FlatEntityHistory.OBSERVER_PK: OBSERVER_PK,
          FlatEntityHistory.ENTITY_PK: REL_PK, FlatEntityHistory.ENTITY_TYPE: "event",
          FlatEntityHistory.ENTITY_TRAITS: {"$type": "event", "$label": "viewed", "channel": "web"}}),
    # obs-2 (relation-less): only the observer entity stored.
    _row({FlatEntityHistory.OBS_ID: "obs-2", FlatEntityHistory.OBSERVER_PK: OBSERVER_PK,
          FlatEntityHistory.ENTITY_PK: OBSERVER_PK, FlatEntityHistory.ENTITY_TYPE: "user",
          FlatEntityHistory.ENTITY_ID: "u1", FlatEntityHistory.ENTITY_LABEL: "Bob",
          FlatEntityHistory.ENTITY_TRAITS: {"name": "Bob"}}),
]


class _FakeAdapter:
    """Mimics bd_event_adapter, serving the fixture rows with real paging."""

    def __init__(self, obs_rows, fact_rows, entity_rows):
        self._obs_rows = obs_rows
        self._fact_rows = fact_rows
        self._entity_rows = entity_rows

    async def export_observations_by_source(self, source_id, start, limit):
        return [r for r in self._obs_rows if r.get_or_none(FlatObs.SOURCE_ID) == source_id][start:start + limit]

    async def load_facts_by_observation_ids(self, obs_ids):
        ids = set(obs_ids)
        return [r for r in self._fact_rows if r.get_or_none(FlatFact.OBS_ID) in ids]

    async def load_entities_by_observation_ids(self, obs_ids):
        ids = set(obs_ids)
        return [r for r in self._entity_rows if r.get_or_none(FlatEntityHistory.OBS_ID) in ids]


def _collect(batch_size):
    adapter = _FakeAdapter(OBS_ROWS, FACT_ROWS, ENTITY_ROWS)

    async def run():
        return [obs async for obs in export_observations(SOURCE_ID, batch_size=batch_size, adapter=adapter)]

    return asyncio.run(run())


# batch_size=1 forces every fixture row onto its own page, so the obs-1 duplicate
# is split across a page boundary — proving the cross-page ``seen`` dedup.
def test_full_relation_observation_is_reconstructed():
    observations = _collect(batch_size=1)
    by_index = observations  # order preserved: obs-1 (full), obs-1 (text), obs-2

    assert [o.id for o in observations] == ["obs-1", "obs-1", "obs-2"]

    full = by_index[0]
    # Source / session / observation text
    assert full.source.id == SOURCE_ID
    assert full.get_session_id() == "sess-1"
    assert full.label == "page view"
    assert full.text.summary == "Bob viewed a widget"

    # Entities: user + product + cart (the 'event' entity is NOT an observation entity)
    kinds = sorted(e.instance.kind for e in full.entities.list())
    assert kinds == ["cart", "product", "user"]
    assert full.get_observer() is not None  # observer link resolves into entities

    # One relation with two objects, both linking to real entities
    assert len(full.relation) == 1
    relation = full.relation[0]
    assert relation.label == "viewed"
    assert relation.type == "event"
    assert relation.subjective is True
    assert relation.tags == ["web"]
    assert relation.text.summary == "Bob viewed Widget"
    # Injected ontology keys are stripped; real trait is kept
    assert relation.traits == {"channel": "web"}

    links = set(full.entities.links())
    assert relation.actor in links
    assert len(relation.objects) == 2
    assert all(obj in links for obj in relation.objects)


def test_duplicate_id_becomes_text_only():
    observations = _collect(batch_size=1)
    duplicate = observations[1]

    assert duplicate.id == "obs-1"
    assert duplicate.relation == []
    # Only the observer entity is carried, and it resolves
    assert len(list(duplicate.entities.list())) == 1
    assert duplicate.get_observer() is not None
    # Carries the *second* text version
    assert duplicate.text.summary == "Bob viewed a widget (edited)"


def test_relationless_observation_is_reconstructed():
    observations = _collect(batch_size=1)
    relationless = observations[2]

    assert relationless.id == "obs-2"
    assert relationless.relation == []
    assert relationless.text.summary == "Bob signed up"
    assert relationless.get_observer() is not None


def test_paging_yields_same_result_regardless_of_batch_size():
    one = [o.id for o in _collect(batch_size=1)]
    big = [o.id for o in _collect(batch_size=100)]
    assert one == big == ["obs-1", "obs-1", "obs-2"]


def test_exports_are_replayable_observations():
    # Every yielded Observation must round-trip through JSON back into a valid
    # Observation (the shape the POST / collection endpoint accepts).
    for obs in _collect(batch_size=1):
        payload = json.loads(obs.model_dump_json(exclude_none=True))
        reloaded = Observation(**payload)  # raises if links/shape are invalid
        assert reloaded.id == obs.id
        assert reloaded.get_observer() is not None
