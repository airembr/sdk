import pytest
from airembr.sdk.service.parser.tql.parser import Parser
from lark import Tree

def test_parser_read():
    content = Parser.read('grammar/uql_expr.lark')
    assert "start: expr" in content or "expr:" in content
    assert "AND" in content or "OR" in content

def test_parser_init():
    grammar = "start: WORD\n%import common.WORD"
    p = Parser(grammar, start='start')
    assert p.base_parser is not None

def test_parser_parse():
    grammar = "start: WORD\n%import common.WORD"
    p = Parser(grammar, start='start')
    tree = p.parse("hello")
    assert isinstance(tree, Tree)
    assert tree.data == 'start'

def test_parser_with_uql_grammar():
    grammar = Parser.read('grammar/uql_expr.lark')
    p = Parser(grammar, start='expr')
    tree = p.parse("param@a = 1")
    assert isinstance(tree, Tree)
    assert tree.data == 'expr'
