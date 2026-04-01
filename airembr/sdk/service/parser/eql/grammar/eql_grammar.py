eql_grammar = r"""
%import common.ESCAPED_STRING    -> ESCAPED_STRING
%import common.SIGNED_NUMBER     -> SIGNED_NUMBER
%import common.CNAME             -> CNAME

start: statement

// ---------------- Keywords ----------------
CLAUSE.10: /WHEN|WHERE|WHO/i
RETURN.10: /RETURN/i
AND.10: /AND/i
OR.10: /OR/i
NOT.10: /NOT/i

// ---------------- Statement ----------------
statement: CLAUSE? expr return_clause?

return_clause: RETURN return_entities
return_entities: return_entity ("," return_entity)*
return_entity: ENTITY_NAME

// ---------------- Expressions ----------------
?expr: or_expr
?or_expr: and_expr | or_expr OR and_expr   -> or_expr
?and_expr: not_expr | and_expr AND not_expr -> and_expr
?not_expr: NOT not_expr -> not_expr | atom
?atom: entity | LPAR expr RPAR

// ---------------- Entities ----------------
entity: ENTITY_NAME LPAR [pair (sep pair)*] RPAR
sep: ","
pair: PROPERTY_NAME ASSIGN value

ENTITY_NAME: CNAME
PROPERTY_NAME: /[a-zA-Z_$!][a-zA-Z0-9_$!]*/ ("." /[a-zA-Z_$!][a-zA-Z0-9_$!]*/)*
ASSIGN: ":" | "="

// ---------------- Values ----------------
TRUE.2: "true"
FALSE.2: "false"
NUMBER.2: /-?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?/

value: ESCAPED_STRING  -> string
     | QUOTED_STRING   -> string
     | NUMBER          -> number
     | TRUE            -> true
     | FALSE           -> false
     | UNQUOTED_STRING -> string

// -------- Custom string implementation --------
QUOTED_STRING: START_QUOTE STRING_CONTENT END_QUOTE
START_QUOTE: "\""
END_QUOTE: "\""
STRING_CONTENT: /(?:\\.|[^"\\])*/
UNQUOTED_STRING.1: /[a-zA-Z0-9]+/

// ---------------- Parentheses ----------------
LPAR: "("
RPAR: ")"

// ---------------- Whitespace ----------------
%ignore /[ \t\n\r\f]+/
"""