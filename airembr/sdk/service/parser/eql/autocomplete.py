from typing import Tuple, List

from lark import Lark, UnexpectedCharacters, UnexpectedToken, Token
from pydantic import BaseModel

from airembr.sdk.common.singleton import Singleton
from airembr.sdk.service.parser.eql.grammar.eql_grammar import eql_grammar

class CurrToken(BaseModel):
    type: str
    value: str

class EQLNextToken(BaseModel):
    current: CurrToken
    property: str | None
    next: List[str] | None

class EQLCompletion(BaseModel):
    current: CurrToken
    property: str | None = None
    query: str
    completion: List[str] = []

class EQLAutocomplete(metaclass=Singleton):
    def __init__(self):
        self.parser = Lark(eql_grammar, parser="lalr")

    def next_token(self, text: str) -> EQLNextToken:
        """
        Returns a list of terminal names valid at the current cursor position.
        """
        ip = self.parser.parse_interactive(text)
        curr_token: Token = Token("NAME", "")
        curr_property: Token = Token("VALUE", None)
        try:

            for _curr in ip.iter_parse():
                curr_token = _curr
                if curr_token.type == "NAME":
                    curr_property = _curr
                elif curr_token.type in ["COMMA", "_SEP", "_WS"]:
                    curr_property = Token("VALUE", None)

            accepts = ip.accepts()
            return EQLNextToken(
                current = CurrToken(type=curr_token.type, value = curr_token.value.strip('"')),
                property = curr_property.value,
                next = sorted(accepts)
            )

        except UnexpectedCharacters as e:
            return  EQLNextToken(**{"current": {"type": curr_token.type, "value": curr_token.value}, "property": curr_property.value, "next":  sorted(e.allowed)})

        except UnexpectedToken as e:
            return  EQLNextToken(**{"current": {"type": curr_token.type, "value": curr_token.value}, "property": curr_property.value, "next": sorted(e.expected)})
