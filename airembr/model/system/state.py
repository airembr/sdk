
from pydantic import BaseModel

from airembr.model.system.enum.yes_no import YesNo


class Settings(BaseModel):
    enabled: bool = True
    hidden: bool = False

    @staticmethod
    def as_bool(state: YesNo):
        return state.value == state.yes