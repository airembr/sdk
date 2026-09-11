from lark.exceptions import LarkError

from airembr.sdk.service.parser.eql.autocomplete import EQLAutocomplete, EQLCompletion, CurrToken
from airembr.system.command.eql.errors import EqlError


async def autocomplete_eql(query: str) -> EQLCompletion:
    try:
        ac = EQLAutocomplete()

        next_token = ac.next_token(query)
        curr_token_type = next_token.current.type
        curr_token_value = next_token.current.value
        if curr_token_type in ["ASSIGN"]:
            base_query = query
        else:
            base_query = query.rstrip(curr_token_value)

        complete = []

        if curr_token_type in ["_WS"]:
            complete = EQLCompletion(
                query=base_query,
                current=CurrToken(type="NAME", value=""),
                property=next_token.property,
                completion=[curr_token_value, "name1", "name2"]
            )
        elif curr_token_type in ["NAME"]:  # Continue typing name
            complete = EQLCompletion(
                query=base_query,
                current=next_token.current,
                property=next_token.property,
                completion=[curr_token_value, "name1", "name2"]
            )
        elif curr_token_type == "UNQUOTED_STRING":
            if curr_token_value in ['f', 'fa', 'fal', 'fals']:
                complete = EQLCompletion(
                    query=base_query,
                    current=CurrToken(type="FALSE", value=curr_token_value),
                    property=next_token.property,
                    completion=["false"]
                )
            elif curr_token_value in ['t', 'tr', 'tru', 'true']:
                complete = EQLCompletion(
                    query=base_query,
                    current=CurrToken(type="TRUE", value=curr_token_value),
                    property=next_token.property,
                    completion=["true"]
                )
            else:
                complete = EQLCompletion(
                    query=base_query,
                    current=next_token.current,
                    property=next_token.property,
                    completion=[curr_token_value, "name1", "name2"]
                )
        elif curr_token_type in ["QUOTED_STRING", "ESCAPED_STRING", "SIGNED_NUMBER", "FALSE", "TRUE", "ASSIGN"]:
            # Complete values for

            if curr_token_type == 'ESCAPED_STRING':
                complete = EQLCompletion(
                    query=base_query,
                    current=CurrToken(type="_WS", value=""),
                    property=next_token.property,
                    completion=[]
                )
            elif curr_token_type != "ASSIGN":
                complete = EQLCompletion(
                    query=base_query,
                    current=next_token.current,
                    property=next_token.property,
                    completion=[curr_token_value, "value1"]
                )
            else:
                complete = EQLCompletion(
                    query=base_query,
                    current=next_token.current,
                    property=next_token.property,
                    completion=["value1"])

        return complete

    except LarkError as e:
        raise EqlError(detail=str(e), status_code=400)
