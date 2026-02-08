import pytest
import asyncio
from airembr.sdk.service.parser.tql.condition import Condition
from airembr.sdk.service.dot_accessor import DotAccessor

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
def condition_parser():
    return Condition()

@pytest.fixture
def dot_accessor():
    return DotAccessor(param={"a": 1, "b": 2, "c": "hello"}, payload={"x": 10})

def test_condition_singleton():
    c1 = Condition()
    c2 = Condition()
    assert c1 is c2

def test_parse_valid_condition(condition_parser):
    tree = condition_parser.parse("param@a = 1")
    assert tree is not None
    assert tree.data == 'expr'

def test_parse_invalid_condition(condition_parser):
    with pytest.raises(ValueError) as excinfo:
        condition_parser.parse("invalid condition")
    assert "Could not parse condition" in str(excinfo.value)

@pytest.mark.anyio
async def test_evaluate_simple_eq(condition_parser, dot_accessor):
    result = await condition_parser.evaluate("param@a = 1", dot_accessor)
    assert result is True

@pytest.mark.anyio
async def test_evaluate_simple_neq(condition_parser, dot_accessor):
    result = await condition_parser.evaluate("param@a = 2", dot_accessor)
    assert result is False

@pytest.mark.anyio
async def test_evaluate_and_condition(condition_parser, dot_accessor):
    result = await condition_parser.evaluate("param@a = 1 AND param@b = 2", dot_accessor)
    assert result is True

@pytest.mark.anyio
async def test_evaluate_or_condition(condition_parser, dot_accessor):
    result = await condition_parser.evaluate("param@a = 2 OR param@b = 2", dot_accessor)
    assert result is True

@pytest.mark.anyio
async def test_evaluate_comparison_operators(condition_parser, dot_accessor):
    assert await condition_parser.evaluate("param@a > 0", dot_accessor) is True
    assert await condition_parser.evaluate("param@a < 2", dot_accessor) is True
    assert await condition_parser.evaluate("param@a >= 1", dot_accessor) is True
    assert await condition_parser.evaluate("param@a <= 1", dot_accessor) is True
    assert await condition_parser.evaluate("param@a != 2", dot_accessor) is True

@pytest.mark.anyio
async def test_evaluate_string_comparison(condition_parser, dot_accessor):
    assert await condition_parser.evaluate('param@c = "hello"', dot_accessor) is True
    assert await condition_parser.evaluate('param@c != "world"', dot_accessor) is True

@pytest.mark.anyio
async def test_evaluate_payload_accessor(condition_parser, dot_accessor):
    assert await condition_parser.evaluate("payload@x = 10", dot_accessor) is True
