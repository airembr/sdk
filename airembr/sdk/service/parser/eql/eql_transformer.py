from typing import Any, Optional
from lark import Transformer, Token

from airembr.sdk.model.meta_language.meta_lang_model import MetaLangEntity, MetaLangGroup, MetaLangLogic, MetaLangQuery



def _is_valid_operand(a) -> bool:
    """Reject Tokens and un-transformed Trees — keep only AST nodes."""
    return isinstance(a, (MetaLangEntity, MetaLangLogic))


class EQLTransformer(Transformer):

    # ---- Values ------------------------------------------------------------

    def string(self, args):
        token = args[0]
        if token.type == "STRING_CONTENT":
            return str(token)
        if token.type == "UNQUOTED_STRING":
            return str(token)
        # ESCAPED_STRING — strip surrounding quotes and unescape
        raw = str(token)
        return (raw[1:-1]
                .replace('\\"', '"')
                .replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace("\\\\", "\\"))

    def number(self, args):
        val = float(args[0])
        return int(val) if val.is_integer() else val

    def true(self, _args):
        return True

    def false(self, _args):
        return False

    # ---- Pairs / Entities --------------------------------------------------

    def pair(self, args):
        # args: [PROPERTY_NAME, ASSIGN, value]
        return (str(args[0]), args[2])

    def sep(self, _args):
        return None

    def entity(self, args):
        name = str(args[0])
        pairs = [a for a in args[1:] if isinstance(a, tuple)]
        return MetaLangEntity(type=name, properties=pairs)

    def atom(self, args):
        # Unwrap parenthesised expression: LPAR expr RPAR → just the expr
        operands = [a for a in args if _is_valid_operand(a)]
        return operands[0]

    # ---- Boolean expressions -----------------------------------------------

    def not_expr(self, args):
        operands = [a for a in args if _is_valid_operand(a)]
        operand = operands[0]
        if isinstance(operand, MetaLangEntity):
            operand.negation = True
            return operand
        group = MetaLangGroup(entities=[operand])
        return MetaLangLogic(operator="NOT", group=group)

    def and_expr(self, args):
        operands = [a for a in args if _is_valid_operand(a)]
        left, right = operands[0], operands[1]
        if isinstance(left, MetaLangLogic) and left.operator == "AND":
            left.group.entities.append(right)
            return left
        group = MetaLangGroup(entities=[left, right])
        return MetaLangLogic(operator="AND", group=group)

    def or_expr(self, args):
        operands = [a for a in args if _is_valid_operand(a)]
        left, right = operands[0], operands[1]
        if isinstance(left, MetaLangLogic) and left.operator == "OR":
            left.group.entities.append(right)
            return left
        group = MetaLangGroup(entities=[left, right])
        return MetaLangLogic(operator="OR", group=group)

    # ---- Return clause -----------------------------------------------------

    def return_entity(self, args):
        return str(args[0]).lower()

    def return_entities(self, args):
        return [a for a in args if isinstance(a, str)]

    def return_clause(self, args):
        return [a for a in args if isinstance(a, list)][0]

    # ---- Top-level statement -----------------------------------------------

    def statement(self, args):
        clause = "WHERE"
        expr = None
        returns: Optional[list] = None

        for arg in args:
            if isinstance(arg, Token):
                if arg.type == "CLAUSE":
                    clause = str(arg)
                # Skip RETURN token and any other stray tokens
            elif isinstance(arg, list):
                returns = arg
            elif _is_valid_operand(arg):
                expr = arg

        return MetaLangQuery(clause=clause, query=expr, returns=returns)

    def start(self, args):
        return args[0]