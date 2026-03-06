eql_grammar = r"""
%import common.ESCAPED_STRING    -> ESCAPED_STRING
%import common.SIGNED_NUMBER    -> SIGNED_NUMBER
%import common.CNAME            -> CNAME

start: pair (sep pair)*

sep: ("," _WS?) | _WS+

pair: NAME ASSIGN value

NAME: CNAME ("." CNAME)*

ASSIGN: ":" | "="

TRUE: "true"
FALSE: "false"

value: ESCAPED_STRING    -> string
     | QUOTED_STRING     -> string
     | UNQUOTED_STRING   -> string
     | SIGNED_NUMBER     -> number
     | TRUE              -> true
     | FALSE             -> false
     
// -------- Custom string implementation --------
QUOTED_STRING: START_QUOTE STRING_CONTENT
START_QUOTE: "\""
STRING_CONTENT: /(?:\\.|[^"\\])*/
UNQUOTED_STRING: /[a-zA-Z0-9]+/

_WS: /[ \t\n\r]+/
%ignore /[ \t\f\r]+/
"""