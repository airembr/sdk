import dateparser
from .function_transformer import FunctionTransformer
from .transformer_namespace import TransformerNamespace
from ..domain.sql_field_condition import SqlFieldCondition


class StarrocksTransformer(TransformerNamespace):

    def __init__(self, props_2_cols, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props_2_cols = props_2_cols
        self.namespace('uql_function__', FunctionTransformer())

    def expr(self, args):
        return args[0]

    def and_expr(self, args):
        value1, _, value2 = args
        return f"{value1} AND {value2}"

    def or_expr(self, args):
        value1, _, value2 = args
        return f"{value1} OR {value2}"

    def OP_FIELD(self, args):
        value = self.props_2_cols.get(args.value, None)
        if value is not None:
            return SqlFieldCondition(value)
        return SqlFieldCondition(args.value)

    def OP(self, args):
        return args.value

    def OP_INTEGER(self, args):
        return int(args.value)

    def OP_TIME(self, args):
        return args.value

    def OP_STRING(self, args):
        return args.value.strip('"')

    @staticmethod
    def _compare(operation, value1, value2):
        if operation == '=':
            if isinstance(value1, list) and not isinstance(value2, list):
                return value2 in value1
            return value1 == value2
        elif operation == 'is':
            if isinstance(value1, list) and not isinstance(value2, list):
                return value2 in value1
            return value1 == value2
        elif operation == '!=':
            return value1 != value2
        elif operation == '>':
            return value1 > value2
        elif operation == '>=':
            return value1 >= value2
        elif operation == '<':
            return value1 < value2
        elif operation == '<=':
            return value1 <= value2
        else:
            raise ValueError(f"Unexpected operation: {operation}")

    def op_condition(self, args):
        value1, operation, value2 = args
        return self._compare(operation, value1, value2)

    def op_array(self, args):
        return args

    def OP_BOOL(self, args):
        return args.lower() == 'true'

    def OP_NULL(self, args):
        return None

    def OP_FLOAT(self, args):
        return float(args.value)

    def op_range(self, args):
        return args

    def op_between(self, args):
        elastic_field, _, values = args  # type: SqlFieldCondition, str, list
        value1, value2 = values
        return f"BETWEEN {value1} AND {value2}"

    def op_field_eq_field(self, args):
        value1, operation, value2 = args
        return self._compare(operation, value1, value2)

    def op_exact_match(self, args):
        value1, _, value2 = args
        return f"{value1.field} = '{value2}'"

    def op_fulltext_match(self, args):
        value1, operation, value2 = args
        return f"{value1.field} LIKE '{value2}'"

    def op_in(self, args):
        value1, operation, value2 = args
        return f"{value1.field} IN {tuple(value2)}"

    def OP_VALUE_TYPE(self, args):
        return args.value

    def op_compound_value(self, args):
        value_type, value = args
        if value_type == 'datetime':

            if not isinstance(value, str):
                raise ValueError(
                    "Value of `{}` must be string to compare it with datetime. Type of {} given".format(value,
                                                                                                        type(value)))

            date = dateparser.parse(value)

            if not date:
                raise ValueError("Could not parse date `{}`".format(value))
            return date
        raise ValueError("Unknown type `{}`".format(value_type))

    @staticmethod
    def op_compound_field(args):
        value_type, field = args  # type: str, SqlFieldCondition
        raise ValueError("Functions on fields are not permitted. Unknown function `{}`".format(value_type))

    def op_field_sig(self, args):
        return args[0]  # type: SqlFieldCondition

    def op_value_sig(self, args):
        return args[0]

    def op_is_null(self, args):
        field = args[0]  # type: SqlFieldCondition
        return f"{field.field} IS NULL"

    def op_exists(self, args):
        field = args[0]  # type: SqlFieldCondition

        return f"{field.field} IS NOT NULL"

    def op_not_exists(self, args):
        field = args[0]  # type: SqlFieldCondition
        return f"{field.field} IS NULL"
