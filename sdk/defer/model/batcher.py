from dataclasses import dataclass
from typing import Callable, Optional, Tuple, Union


@dataclass
class BatcherConfig:
    func: Union[Callable, str]
    timeout: float
    module: Optional[str] = None
    min_size: Optional[int] = 0
    max_size: Optional[int] = 0

    def get_module_and_function(self) -> Tuple[str, str]:
        if self.module is None:
            batcher_module = self.func.__module__
        else:
            batcher_module = self.module

        if isinstance(self.func, Callable):
            batcher_func = self.func.__name__
        else:
            batcher_func = self.func


        return batcher_module, batcher_func
