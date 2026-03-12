from lark import Lark

from airembr.sdk.common.singleton import Singleton
from airembr.sdk.model.meta_language.meta_lang_model import MetaLangQuery
from airembr.sdk.service.parser.eql.eql_transformer import EQLTransformer
from airembr.sdk.service.parser.eql.grammar.eql_grammar import eql_grammar


class EQLParser(metaclass=Singleton):
    def __init__(self):
        self.parser = Lark(eql_grammar, parser="earley")
        self.transformer = EQLTransformer()

    def ast(self, query):
        return self.parser.parse(query)

    def parse(self, query: str) -> MetaLangQuery:
        tree = self.ast(query)
        return self.transformer.transform(tree)
