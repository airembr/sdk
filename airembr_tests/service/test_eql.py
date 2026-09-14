import pytest
from lark import Lark

from airembr.model.system.meta_language.meta_lang_model import (
    MetaLangEntity,
    MetaLangGroup,
    MetaLangLogic,
    MetaLangProperty,
    MetaLangQuery,
)
from airembr.sdk.service.parser.eql.eql_transformer import EQLTransformer
from airembr.sdk.service.parser.eql.grammar.eql_grammar import eql_grammar


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def parse():
    parser = Lark(eql_grammar, parser="earley")
    transformer = EQLTransformer()

    def _parse(query: str) -> MetaLangQuery:
        tree = parser.parse(query)
        return transformer.transform(tree)

    return _parse


# ---------------------------------------------------------------------------
# Clause tests
# ---------------------------------------------------------------------------

class TestClauses:

    def test_when_clause(self, parse):
        result = parse('WHEN Person(name: "Alice")')
        assert result.clause == "WHEN"

    def test_where_clause(self, parse):
        result = parse('WHERE Person(name: "Alice")')
        assert result.clause == "WHERE"

    def test_who_clause(self, parse):
        result = parse('WHO Person(name: "Alice")')
        assert result.clause == "WHO"

    def test_no_clause_defaults_to_where(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.clause == "WHERE"


# ---------------------------------------------------------------------------
# Value type tests
# ---------------------------------------------------------------------------

class TestValueTypes:

    def test_string_double_quoted(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.query.properties == [MetaLangProperty(name="name", assign=":", value="Alice")]

    def test_string_unquoted(self, parse):
        result = parse('Person(status: active)')
        assert result.query.properties == [MetaLangProperty(name="status", assign=":", value="active")]

    def test_integer(self, parse):
        result = parse('Person(age: 30)')
        assert result.query.properties == [MetaLangProperty(name="age", assign=":", value=30)]
        assert isinstance(result.query.properties[0].value, int)

    def test_negative_integer(self, parse):
        result = parse('Person(score: -5)')
        assert result.query.properties == [MetaLangProperty(name="score", assign=":", value=-5)]
        assert isinstance(result.query.properties[0].value, int)

    def test_float(self, parse):
        result = parse('Person(score: 3.14)')
        assert result.query.properties == [MetaLangProperty(name="score", assign=":", value=3.14)]
        assert isinstance(result.query.properties[0].value, float)

    def test_negative_float(self, parse):
        result = parse('Person(score: -1.5)')
        assert result.query.properties == [MetaLangProperty(name="score", assign=":", value=-1.5)]
        assert isinstance(result.query.properties[0].value, float)

    def test_bool_true(self, parse):
        result = parse('Person(active: true)')
        assert result.query.properties == [MetaLangProperty(name="active", assign=":", value=True)]
        assert isinstance(result.query.properties[0].value, bool)

    def test_bool_false(self, parse):
        result = parse('Person(active: false)')
        assert result.query.properties == [MetaLangProperty(name="active", assign=":", value=False)]
        assert isinstance(result.query.properties[0].value, bool)

    def test_escaped_string(self, parse):
        result = parse('Person(note: "hello\\nworld")')
        assert result.query.properties == [MetaLangProperty(name="note", assign=":", value="hello\nworld")]


# ---------------------------------------------------------------------------
# Property name tests
# ---------------------------------------------------------------------------

class TestPropertyNames:

    def test_simple_property(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.query.properties[0].name == "name"

    def test_dot_notation_two_levels(self, parse):
        result = parse('Person(address.city: "Berlin")')
        assert result.query.properties[0].name == "address.city"

    def test_dot_notation_three_levels(self, parse):
        result = parse('Person(a.b.c: 1)')
        assert result.query.properties[0].name == "a.b.c"

    def test_equals_sign_assignment(self, parse):
        result = parse('Person(name = "Carol")')
        assert result.query.properties == [MetaLangProperty(name="name", assign="=", value="Carol")]

    def test_multiple_properties(self, parse):
        result = parse('Person(name: "Alice", age: 30, active: true)')
        assert result.query.properties == [
            MetaLangProperty(name="name", assign=":", value="Alice"),
            MetaLangProperty(name="age", assign=":", value=30),
            MetaLangProperty(name="active", assign=":", value=True),
        ]


# ---------------------------------------------------------------------------
# Entity tests
# ---------------------------------------------------------------------------

class TestEntities:

    def test_entity_type_lowercased(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.query.type == "person"

    def test_entity_no_properties(self, parse):
        result = parse('Person()')
        assert result.query.type == "person"
        assert result.query.properties == []

    def test_entity_negation_false_by_default(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.query.negation is False


# ---------------------------------------------------------------------------
# Boolean logic tests
# ---------------------------------------------------------------------------

class TestBooleanLogic:

    def test_and_two_entities(self, parse):
        result = parse('Person(age: 30) AND Pet(type: "cat")')
        assert isinstance(result.query, MetaLangLogic)
        assert result.query.operator == "AND"
        assert len(result.query.group.entities) == 2

    def test_or_two_entities(self, parse):
        result = parse('Pet(type: "cat") OR Pet(type: "dog")')
        assert isinstance(result.query, MetaLangLogic)
        assert result.query.operator == "OR"
        assert len(result.query.group.entities) == 2

    def test_and_flattened(self, parse):
        result = parse('A(x: 1) AND B(y: 2) AND C(z: 3)')
        assert result.query.operator == "AND"
        assert len(result.query.group.entities) == 3

    def test_or_flattened(self, parse):
        result = parse('A(x: 1) OR B(y: 2) OR C(z: 3)')
        assert result.query.operator == "OR"
        assert len(result.query.group.entities) == 3

    def test_not_entity(self, parse):
        result = parse('NOT Person(active: false)')
        assert isinstance(result.query, MetaLangEntity)
        assert result.query.negation is True

    def test_not_compound(self, parse):
        result = parse('NOT (Person(active: false) OR Person(banned: true))')
        assert isinstance(result.query, MetaLangLogic)
        assert result.query.operator == "NOT"

    def test_and_or_precedence(self, parse):
        # A AND B OR C should parse as (A AND B) OR C
        result = parse('A(x: 1) AND B(y: 2) OR C(z: 3)')
        assert result.query.operator == "OR"
        left = result.query.group.entities[0]
        assert isinstance(left, MetaLangLogic)
        assert left.operator == "AND"

    def test_parentheses_override_precedence(self, parse):
        # A AND (B OR C)
        result = parse('A(x: 1) AND (B(y: 2) OR C(z: 3))')
        assert result.query.operator == "AND"
        right = result.query.group.entities[1]
        assert isinstance(right, MetaLangLogic)
        assert right.operator == "OR"

    def test_nested_logic(self, parse):
        result = parse('WHEN (A(x: 1) AND B(y: 2)) OR (C(z: 3) AND NOT D(w: 4)) RETURN A, C')
        assert result.query.operator == "OR"
        left, right = result.query.group.entities
        assert left.operator == "AND"
        assert right.operator == "AND"
        # D should be negated
        d_entity = right.group.entities[1]
        assert isinstance(d_entity, MetaLangEntity)
        assert d_entity.negation is True


# ---------------------------------------------------------------------------
# Return clause tests
# ---------------------------------------------------------------------------

class TestReturnClause:

    def test_no_return(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.returns is None

    def test_single_return(self, parse):
        result = parse('WHERE Person(name: "Alice") RETURN Person')
        assert result.returns == ["person"]

    def test_multiple_returns(self, parse):
        result = parse('WHEN Person(age: 30) AND Address(city: "Paris") RETURN Person, Address')
        assert result.returns == ["person", "address"]

    def test_return_entities_lowercased(self, parse):
        result = parse('WHERE Person(name: "Alice") RETURN Person, Address')
        assert all(r == r.lower() for r in result.returns)


# ---------------------------------------------------------------------------
# Full query integration tests
# ---------------------------------------------------------------------------

class TestFullQueries:

    def test_complex_query(self, parse):
        q = 'WHEN Person(age: 30) AND (Address(city: "Paris") OR Address(city: "Rome")) RETURN Person, Address'
        result = parse(q)
        assert result.clause == "WHEN"
        assert result.query.operator == "AND"
        assert len(result.returns) == 2

    def test_dot_notation_with_types(self, parse):
        q = 'WHERE A(x.a: true) OR B(y.c.d: 2) OR C(z: 3.5)'
        result = parse(q)
        assert result.query.operator == "OR"
        entities = result.query.group.entities
        assert entities[0].properties == [MetaLangProperty(name="x.a", assign=":", value=True)]
        assert entities[1].properties == [MetaLangProperty(name="y.c.d", assign=":", value=2)]
        assert entities[2].properties == [MetaLangProperty(name="z", assign=":", value=3.5)]

    def test_mixed_assign_operators(self, parse):
        q = 'Person(name: "Alice", age = 30)'
        result = parse(q)
        assert result.query.properties == [
            MetaLangProperty(name="name", assign=":", value="Alice"),
            MetaLangProperty(name="age", assign="=", value=30),
        ]


# ---------------------------------------------------------------------------
# Assign operator tests
# ---------------------------------------------------------------------------

class TestAssignOperators:

    def test_colon_assign(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.query.properties[0].assign == ":"

    def test_equals_assign(self, parse):
        result = parse('Person(name = "Alice")')
        assert result.query.properties[0].assign == "="

    def test_tilde_assign(self, parse):
        result = parse('location($name~"Kazimierz Dolny")')
        assert result.query.properties[0].assign == "~"

    def test_all_three_operators_distinct(self, parse):
        result = parse('Entity(a: 1, b = 2, c ~ 3)')
        props = result.query.properties
        assert props[0].assign == ":"
        assert props[1].assign == "="
        assert props[2].assign == "~"

    def test_tilde_operator_name_and_value(self, parse):
        result = parse('location($name~"Kazimierz Dolny", $type="city")')
        props = result.query.properties
        assert props[0].name == "$name"
        assert props[0].assign == "~"
        assert props[0].value == "Kazimierz Dolny"
        assert props[1].name == "$type"
        assert props[1].assign == "="
        assert props[1].value == "city"


# ---------------------------------------------------------------------------
# Similarity distance tests
# ---------------------------------------------------------------------------

class TestSimilarityDistance:

    def test_distance_before_value(self, parse):
        result = parse('location($name~[0.5]"Wroclaw")')
        prop = result.query.properties[0]
        assert prop.assign == "~"
        assert prop.distance == 0.5
        assert prop.value == "Wroclaw"

    def test_distance_after_value(self, parse):
        result = parse('location($name~"Wroclaw"[.32])')
        prop = result.query.properties[0]
        assert prop.assign == "~"
        assert prop.distance == pytest.approx(0.32)
        assert prop.value == "Wroclaw"

    def test_no_distance_defaults_to_none(self, parse):
        result = parse('location($name~"Wroclaw")')
        prop = result.query.properties[0]
        assert prop.assign == "~"
        assert prop.distance is None

    def test_exact_match_has_no_distance(self, parse):
        result = parse('location($name="Wroclaw")')
        prop = result.query.properties[0]
        assert prop.assign == "="
        assert prop.distance is None

    def test_colon_match_has_no_distance(self, parse):
        result = parse('location($name:"Wroclaw")')
        prop = result.query.properties[0]
        assert prop.assign == ":"
        assert prop.distance is None

    def test_distance_boundary_zero(self, parse):
        result = parse('location($name~[0]"Wroclaw")')
        assert result.query.properties[0].distance == 0.0

    def test_distance_boundary_one(self, parse):
        result = parse('location($name~[1]"Wroclaw")')
        assert result.query.properties[0].distance == 1.0

    def test_distance_out_of_range_raises(self, parse):
        with pytest.raises((ValueError, Exception)):
            parse('location($name~[1.5]"Wroclaw")')

    def test_per_property_distances_independent(self, parse):
        result = parse('location($name~[0.4]"Wroclaw", $type~"city"[0.2])')
        props = result.query.properties
        assert props[0].distance == pytest.approx(0.4)
        assert props[1].distance == pytest.approx(0.2)

    def test_distance_on_vector_exact_mix(self, parse):
        result = parse('location($name~[0.4]"Wroclaw") AND person($age=30)')
        from airembr.model.system.meta_language.meta_lang_model import MetaLangLogic
        assert isinstance(result.query, MetaLangLogic)
        loc_entity = result.query.group.entities[0]
        person_entity = result.query.group.entities[1]
        assert loc_entity.properties[0].distance == pytest.approx(0.4)
        assert person_entity.properties[0].distance is None