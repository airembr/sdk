from typing import Optional, Callable

import functools
import contextlib

from pararun.model.worker_capsule import WorkerCapsule, FunctionCapsule
from pararun.service.logger.log_handler import get_logger

logger = get_logger(__name__)


def deferred_function(module: Optional[str] = None,
                      guard: Optional[Callable] = None,
                      guard_module: Optional[str] = None):
    def decorator_serialize_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            nonlocal module, guard, guard_module

            # Instead of executing the function, return a WorkerCapsule object
            if module is None:
                module = func.__module__

            capsule = WorkerCapsule(
                function=FunctionCapsule(name=func.__name__, module=module),
                args=args,
                kwargs=kwargs
            )

            if guard:
                if guard_module is None:
                    guard_module = guard.__module__
                capsule.guard = FunctionCapsule(name=guard.__name__, module=guard_module)

            return capsule

        return wrapper

    return decorator_serialize_function


def deferred_lazy_function(module: str,
                           func: str,
                           guard: Optional[Callable] = None,
                           guard_module: Optional[str] = None):
    def wrapper(*args, **kwargs):

        nonlocal module, guard, guard_module

        # Instead of executing the function, return a WorkerCapsule object

        capsule = WorkerCapsule(
            function=FunctionCapsule(name=func, module=module),
            args=args,
            kwargs=kwargs
        )

        if guard:
            if guard_module is None:
                guard_module = guard.__module__
            capsule.guard = FunctionCapsule(name=guard.__name__, module=guard_module)

        return capsule

    return wrapper


@contextlib.contextmanager
def deferred_execution(module: Optional[str] = None,
                       guard: Optional[Callable] = None,
                       guard_module: Optional[str] = None):
    yield deferred_function(
        module,
        guard=guard,
        guard_module=guard_module
    )


@contextlib.contextmanager
def deferred_lazy_execution(module: str,
                            func: str,
                            guard: Optional[Callable] = None,
                            guard_module: Optional[str] = None):
    yield deferred_lazy_function(
        module,
        func,
        guard=guard,
        guard_module=guard_module
    )
