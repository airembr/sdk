class EventMappingError(Exception):
    def __init__(self, detail: str, status_code):
        super().__init__(detail)
        self.status_code = status_code
