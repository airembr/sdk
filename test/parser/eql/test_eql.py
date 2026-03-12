import pytest
from lark import Lark

from airembr.sdk.model.meta_language.meta_lang_model import (
    MetaLangEntity,
    MetaLangGroup,
    MetaLangLogic,
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
        assert result.query.properties == [("name", "Alice")]

    def test_string_unquoted(self, parse):
        result = parse('Person(status: active)')
        assert result.query.properties == [("status", "active")]

    def test_integer(self, parse):
        result = parse('Person(age: 30)')
        assert result.query.properties == [("age", 30)]
        assert isinstance(result.query.properties[0][1], int)

    def test_negative_integer(self, parse):
        result = parse('Person(score: -5)')
        assert result.query.properties == [("score", -5)]
        assert isinstance(result.query.properties[0][1], int)

    def test_float(self, parse):
        result = parse('Person(score: 3.14)')
        assert result.query.properties == [("score", 3.14)]
        assert isinstance(result.query.properties[0][1], float)

    def test_negative_float(self, parse):
        result = parse('Person(score: -1.5)')
        assert result.query.properties == [("score", -1.5)]
        assert isinstance(result.query.properties[0][1], float)

    def test_bool_true(self, parse):
        result = parse('Person(active: true)')
        assert result.query.properties == [("active", True)]
        assert isinstance(result.query.properties[0][1], bool)

    def test_bool_false(self, parse):
        result = parse('Person(active: false)')
        assert result.query.properties == [("active", False)]
        assert isinstance(result.query.properties[0][1], bool)

    def test_escaped_string(self, parse):
        result = parse('Person(note: "hello\\nworld")')
        assert result.query.properties == [("note", "hello\nworld")]


# ---------------------------------------------------------------------------
# Property name tests
# ---------------------------------------------------------------------------

class TestPropertyNames:

    def test_simple_property(self, parse):
        result = parse('Person(name: "Alice")')
        assert result.query.properties[0][0] == "name"

    def test_dot_notation_two_levels(self, parse):
        result = parse('Person(address.city: "Berlin")')
        assert result.query.properties[0][0] == "address.city"

    def test_dot_notation_three_levels(self, parse):
        result = parse('Person(a.b.c: 1)')
        assert result.query.properties[0][0] == "a.b.c"

    def test_equals_sign_assignment(self, parse):
        result = parse('Person(name = "Carol")')
        assert result.query.properties == [("name", "Carol")]

    def test_multiple_properties(self, parse):
        result = parse('Person(name: "Alice", age: 30, active: true)')
        assert result.query.properties == [
            ("name", "Alice"),
            ("age", 30),
            ("active", True),
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
        assert entities[0].properties == [("x.a", True)]
        assert entities[1].properties == [("y.c.d", 2)]
        assert entities[2].properties == [("z", 3.5)]

    def test_mixed_assign_operators(self, parse):
        q = 'Person(name: "Alice", age = 30)'
        result = parse(q)
        assert result.query.properties == [("name", "Alice"), ("age", 30)]