from srd.domain.record_mapping import EntityToTableMapping
from airembr.sdk.service.parser.tql.parser import Parser
from airembr.sdk.service.parser.tql.transformer.starrocks_transformer import StarrocksTransformer


class FilterCondition:

    def __init__(self, mapping: EntityToTableMapping):
        self.parser = Parser(Parser.read('grammar/filter_condition.lark'), start='expr')
        self.prop_2_col_mapping = mapping.get_property_to_column()

    def parse(self, condition):
        return self.parser.parse(condition)

    def evaluate(self, condition):
        # todo cache tree
        tree = self.parse(condition)
        return StarrocksTransformer(props_2_cols=self.prop_2_col_mapping).transform(tree)


# x = FilterCondition(event_mapping())
# y = x.evaluate('(session.id = "1" AND event_id!=1) OR actor.type="import"')
# print(y)