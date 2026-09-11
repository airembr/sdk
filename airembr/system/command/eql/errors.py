from airembr.model.system.meta_language.meta_lang_model import MetaLangQuery
from airembr.sdk.service.parser.eql.eql_parser import EQLParser
from lark.exceptions import LarkError


class EqlError(Exception):
    def __init__(self, detail: str, status_code):
        super().__init__(detail)
        self.status_code = status_code


_parser = EQLParser()


def parse_eql(query: str) -> MetaLangQuery:
    try:
        return _parser.parse(query)
    except LarkError as e:
        raise EqlError(detail=str(e), status_code=400)
