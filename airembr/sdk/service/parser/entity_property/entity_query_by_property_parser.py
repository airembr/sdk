from lark import Lark, Transformer, v_args
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedToken,
    UnexpectedInput,
    VisitError,
    LarkError,
)
import ast

from airembr.core.singleton import Singleton

grammar = r"""
%import common.ESCAPED_STRING   -> ESCAPED_STRING
%import common.SIGNED_NUMBER    -> SIGNED_NUMBER
%import common.CNAME            -> CNAME

start: pair (sep pair)*

sep: ("," _WS?) | _WS+

pair: NAME ASSIGN value    // removed _WS? here

NAME: /\$?[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*/

ASSIGN: ":" | "="

value: ESCAPED_STRING    -> string
     | SIGNED_NUMBER     -> number
     | "true"            -> true
     | "false"           -> false

_WS: /[ \t\n\r]+/
%ignore /[ \t\f\r]+/
"""


@v_args(inline=True)
class ToList(Transformer):
    def start(self, first, *rest):
        out = [first] if isinstance(first, tuple) else list(first)
        for item in rest:
            if isinstance(item, tuple):
                out.append(item)
        return out

    # receive all children: NAME, ASSIGN, value
    def pair(self, name, _assign, value):
        return (str(name), value)

    def NAME(self, t):
        return str(t)

    def string(self, s):
        return ast.literal_eval(s)

    def number(self, n):
        s = str(n)
        if any(c in s for c in ".eE"):
            return float(s)
        return int(s)

    def true(self):
        return True

    def false(self):
        return False


class EntityQueryParseError(Exception):
    def __init__(self, message, line=None, column=None, context=None):
        super().__init__(message)
        self.line = line
        self.column = column
        self.context = context

    def __str__(self):
        location = f" (line {self.line}, column {self.column})" if self.line else ""
        ctx = f"\nContext: {self.context}" if self.context else ""
        return f"{self.args[0]}{location}{ctx}"


class EntityQueryByPropertyParser(metaclass=Singleton):

    def __init__(self):
        # build parser
        self.parser = Lark(
            grammar, parser="lalr", transformer=ToList(),
            propagate_positions=False, maybe_placeholders=False
        )

    def parse(self, text: str):
        try:
            return self.parser.parse(text)
        except UnexpectedCharacters as e:
            raise EntityQueryParseError(
                f"Unexpected character '{e.char}'",
                line=e.line, column=e.column, context=e.get_context(text)
            ) from e
        except UnexpectedToken as e:
            raise EntityQueryParseError(
                f"Unexpected token '{e.token}', expected one of: {', '.join(e.expected)}",
                line=e.line, column=e.column, context=e.get_context(text)
            ) from e
        except UnexpectedInput as e:
            raise EntityQueryParseError(
                "Unexpected input",
                line=e.line, column=e.column, context=e.get_context(text)
            ) from e
        except VisitError as e:
            raise EntityQueryParseError(
                f"Transformer error: {str(e)}"
            ) from e
        except LarkError as e:
            raise EntityQueryParseError("General parsing error") from e
