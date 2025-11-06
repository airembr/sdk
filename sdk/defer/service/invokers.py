import inspect
from contextlib import contextmanager

from pararun.model.transport_context import TransportContext
from pararun.service.converters.time_converters import pretty_time_format
from time import time
from importlib import import_module

from pararun.service.logger.extra_info import exact
from pararun.service.logger.log_handler import get_logger

logger = get_logger(__name__)
_cached_function_references = {}


@contextmanager
def single_function_reference(module, name):
    key = (module, name)
    if key not in _cached_function_references:
        module_ref = import_module(module)
        func_ref = getattr(module_ref, name)
        _cached_function_references[key] = func_ref

    yield _cached_function_references[key]


def invoke(context: TransportContext, module, name, args, kwargs=None):
    with single_function_reference(module, name) as func_ref:
        if kwargs is None:
            kwargs = {}
        # This is the signature of a function
        return func_ref(context, *args, **kwargs)


async def async_invoke(context: TransportContext, module, name, args, kwargs=None):
    t = time()

    result = invoke(context, module, name, args, kwargs)
    if inspect.iscoroutine(result):
        result = await result

    logger.debug(f"Invoked {module}.{name}. Finished in {pretty_time_format(time() - t)}",
                 extra=exact(origin="background-worker", package=__name__, class_name='invoke'))

    return result


async def raw_func_invoke(module, name, args=None, kwargs=None):
        t = time()

        with single_function_reference(module, name) as func_ref:
            if kwargs is None:
                kwargs = {}
            # This is the signature of a function
            result = func_ref(*args, **kwargs)

        if inspect.iscoroutine(result):
            result = await result

        logger.debug(f"Invoked {module}.{name}. Finished in {pretty_time_format(time() - t)}",
                     extra=exact(origin="background-worker", package=__name__, class_name='invoke'))

        return result