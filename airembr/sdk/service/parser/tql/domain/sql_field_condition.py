from types import NoneType


class SqlFieldCondition:
    def __init__(self, field):
        self.field = field

    def __repr__(self):
        return f"SqlFieldCondition({self.field})"

    def __eq__(self, other):
        if isinstance(other, SqlFieldCondition):
            # This is when two fields are compared (field1=field2)
            return f"{self.field} = {other.field}"
        else:
            if isinstance(other, NoneType):
                return f"{self.field} IS NULL"

            if isinstance(other, str):
                if other.lower() in ["null", "none", "*"]:
                    return f"{self.field} IS NOT NULL"

                return f"{self.field} = '{other}'"

            if isinstance(other, list):
                return f"{self.field} IN {tuple(other)}"

            if isinstance(other, bool):
                return f"{self.field} = {other}"

            if isinstance(other, (int, float)):
                return f"{self.field} = {other}"

            raise ValueError(f"Value is incorrect. Expected type: string, list, Null, or True/False, int, float"
                             f"got {type(other)}.")

    def __ne__(self, other):
        if isinstance(other, SqlFieldCondition):
            # This is when two fields are compared (field1=field2)
            return f"{self.field} != {other.field}"
        else:
            # field != NULL
            if isinstance(other, NoneType):
                return f"{self.field} IS NOT NULL"

            if isinstance(other, str):
                return f"{self.field} != '{other}'"
            return f"{self.field} != {other}"

    def __gt__(self, other):
        # TODO This is when field and value are compared (field1=1). Add field to field comparator

        return f"{self.field} > {other}"

    def __ge__(self, other):
        # TODO This is when field and value are compared (field1=1). Add field to field comparator

        return f"{self.field} >= {other}"

    def __lt__(self, other):

        # TODO This is when field and value are compared (field1=1). Add field to field comparator
        return f"{self.field} < {other}"

    def __le__(self, other):

        # TODO This is when field and value are compared (field1=1). Add field to field comparator
        return f"{self.field} <= {other}"

    def __str__(self):
        return self.field
