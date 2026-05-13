class QueryStatus(int):

    def ok(self) -> bool:
        return 200 <= self <= 299
