import asyncio

from airembr.sdk.common.singleton import Singleton
from airembr.sdk.service.dot_accessor import DotAccessor

from airembr.sdk.service.parser.tql.parser import Parser
from airembr.sdk.service.parser.tql.transformer.expr_transformer import ExprTransformer


class Condition(metaclass=Singleton):

    def __init__(self):
        self.parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def parse(self, condition: str):
        try:
            return self.parser.parse(condition)
        except Exception as e:
            raise ValueError(f"Could not parse condition {condition}, details: {str(e)}")

    async def evaluate(self, condition: str, dot: DotAccessor):
        # todo cache tree
        tree = self.parse(condition)
        await asyncio.sleep(0)
        return ExprTransformer(dot=dot).transform(tree)

#
# async def main():
#     x = await Condition().evaluate("param@a = 2", DotAccessor(param={"a": 1}))
#     print(x)
#
# import asyncio
# asyncio.run(main())