import inspect

from time import time
from pickle import UnpicklingError
from typing import Optional, List, Tuple, Callable, Dict, Any, Awaitable, Union

import sdk.defer.service.logger.extra_info as ExtraInfo
from sdk.defer.consumer.batcher import BatcherMetadata, BatchStatus, Batcher
from sdk.defer.error.client_timeout import ClientTimeOutError
from sdk.defer.model.adapter import Adapter
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.model.worker_capsule import WorkerCapsule, FunctionCapsule
from sdk.defer.protocol.queue_consumer_protocol import ConsumerProtocol
from sdk.defer.protocol.model_factory_protocol import SerializerProtocol
from sdk.defer.protocol.queue_message_protocol import MessageProtocol
from sdk.defer.service.invokers import async_invoke, raw_func_invoke
from sdk.defer.service.logger.log_handler import get_logger, log_handler, DeferLogHandler
from sdk.defer.service.profiler import profiler
from sdk.defer.transport.default import DefaultSerializer
from sdk.defer_adapter.adaper_selector import DeferAdapterSelector

logger = get_logger(__name__)
ack_the_whole_batch = True

_default_serializers: Dict[str, SerializerProtocol] = {
    "DefaultSerializer": DefaultSerializer(schema=None)
}


class BatcherDB:
    def __init__(self):
        self.db = {}

    def add(self, function_name, function_module, value):
        self.db[(function_name, function_module)] = value

    def get(self, function_name, function_module) -> Optional[str]:
        return self.db.get((function_name, function_module), None)


def _ack(consumer: ConsumerProtocol, messages: List[MessageProtocol]):
    for message in messages:
        consumer.acknowledge(message)


async def _invoke_batch(
        times: Tuple[float, float, float],
        reason,
        batcher_func,
        batch,
        consumer: ConsumerProtocol,
        messages: List[MessageProtocol],
        context: TransportContext,
        ack_messages: bool = True
):
    batcher_module, batcher_function = batcher_func

    try:

        t1 = time()
        # This executes batched result function
        await async_invoke(context, batcher_module, batcher_function, [batch])
        t2 = time()

        _speed, _bulking_time, _not_consumed_time = times

        _save_time = t2 - t1
        _messages_in_bulk = len(messages)
        _records_in_bulk = len(batch)

        # TODO fall back
        _ack_time = 0
        if ack_messages:
            t1 = time()
            _ack(consumer, messages)
            _ack_time = time() - t1

        logger.info(
            f"{context.tenant}: {reason}: "
            f"{_records_in_bulk}/{_messages_in_bulk}: "
            f"Bulking {_bulking_time:.5f}s (left: {_not_consumed_time:.3f}s): "
            f"Running +{_save_time:.3f}s: "
            f"Ack +{_ack_time:.3f}s: "
            f"Full {_bulking_time + _save_time + _ack_time:.2f}s: "
            f"Speed {_messages_in_bulk / (_bulking_time + _save_time + _ack_time):.2f}rps / {_speed:.3f}mps: "
            f"Batch \"{batcher_module}.{batcher_function}\". "
        )

    except Exception as e:
        logger.error(f"Batch invoke error: Details: {str(e)}", e,
                     extra=ExtraInfo.exact(
                         origin="background-worker",
                         package=batcher_module,
                         class_name=batcher_function))
        raise e


async def _invoke_batches(times: Tuple[float, float, float], batcher_db, batches: List[tuple], consumer,
                          ack_messages) -> bool:
    _batch_invoked = False

    # Iterate over all batches and check if any needs flushing

    for batch, key, messages, reason in batches:
        # batch will be false if still accumulating

        # Accept only lists
        if isinstance(batch, list) and len(batch) > 0:
            # This executes batched result function if batch is ready
            (function_module, function_name, tenant, mode) = key

            batcher_func = batcher_db.get(function_module, function_name)

            # The may be no batcher for given function
            if batcher_func:
                await _invoke_batch(
                    times,
                    reason,
                    batcher_func,
                    batch,
                    consumer,
                    messages,
                    context=TransportContext(tenant=tenant, production=mode),
                    ack_messages=ack_messages
                )
                _batch_invoked = True

    return _batch_invoked


def _get_batcher(properties) -> Tuple[str, str, int, int, float]:
    # Get the bulker name
    batcher_function = properties.get('batcher.name', None)
    batcher_module = properties.get('batcher.module', None)
    batcher_min_buffer_size = int(properties.get('batcher.min_buffer', 0))
    batcher_max_buffer_size = int(properties.get('batcher.max_buffer', 0))
    batcher_time_out = float(properties.get('batcher.timeout', 0))

    # If none fallback to old properties
    if not batcher_module and not batcher_function:
        batcher_function = properties.get('name', None)
        batcher_module = properties.get('module', None)

    return batcher_module, batcher_function, batcher_min_buffer_size, batcher_max_buffer_size, batcher_time_out


def _get_function(properties) -> Tuple[str, str]:
    function_name = properties.get('function.name', None)
    function_module = properties.get('function.module', None)

    return function_module, function_name


def _get_metadata(msg: MessageProtocol, available_serializers: Dict[str, SerializerProtocol]) -> Tuple[
    SerializerProtocol, Any, tuple, dict, TransportContext, str, str, str, str, BatcherMetadata]:

    properties = msg.properties()

    _data_serializer: Optional[str] = properties.get('data_bus.factory', None)

    if _data_serializer is None:
        # Default factory
        raise ValueError("Serializer not set.")

    _selected_serializer = available_serializers.get(_data_serializer, None)
    if _selected_serializer is None:
        _selected_serializer = _default_serializers.get(_data_serializer, None)
        if _selected_serializer is None:
            raise ValueError(
                f"Unknown serializer {_data_serializer}. Available serializers: {available_serializers.keys()}")

    serializer: SerializerProtocol = _selected_serializer

    record = msg.value()

    # Get Params
    args, kwargs, context = serializer.deserialize(record)

    # Get executed function
    function_module, function_name = _get_function(properties)

    # Get batcher
    batcher_module, batcher_function, min_buffer_size, max_buffer_size, timeout = _get_batcher(properties)

    metadata = BatcherMetadata(
        min_batch_size=min_buffer_size,
        max_batch_size=max_buffer_size,
        max_time_without_flash=timeout
    )

    return (serializer,
            record,
            args, kwargs, TransportContext(**context),
            function_name, function_module,
            batcher_module, batcher_function, metadata)


async def _batch_flushing(consumer, msg: MessageProtocol, batch_status: BatchStatus, times, batcher_db):
    if not ack_the_whole_batch:
        _ack(consumer, [msg])

    if batch_status.needs_flushing:
        # Will run if batch need to be flushed
        await _invoke_batches(
            times,
            batcher_db,
            batch_status.batch,
            consumer,
            ack_messages=ack_the_whole_batch)


async def run(function_module: str, function_name: str, args: tuple, kwargs: dict, context: TransportContext):
    capsule = WorkerCapsule(
        function=FunctionCapsule(name=function_name, module=function_module),
        args=args,
        kwargs=kwargs
    )
    return await capsule.run(context)


async def start_worker(inactivity_time_out=3000,
                       log_processor: Optional[Callable[[DeferLogHandler, TransportContext], Awaitable[None]]] = None,
                       adapter: Optional[Adapter] = None
                       ):
    if log_processor is not None:
        if not inspect.iscoroutinefunction(log_processor):
            raise AssertionError("log_processor is not  an async function.")

    if adapter.init_function and isinstance(adapter.init_function, tuple):
        init_package, init_function = adapter.init_function
        if init_package and init_function:
            await raw_func_invoke(init_package, init_function, args=[])

    consumer = adapter.adapter_protocol.consumer()

    data_bus = adapter.adapter_protocol.data_bus()
    logger.info(f"Logging level {logger.level}")
    logger.info(
        f"Consumer: {data_bus.subscription.consumer_name.upper()} with subscription {data_bus.subscription.subscription_name.upper()} "
        f"is waiting for first message at {data_bus.topic}...",
        extra=ExtraInfo.exact(origin="background-worker", package=__name__, class_name='start_worker'))

    batcher = Batcher()
    batcher_db = BatcherDB()

    _global_timer = time()
    _start_time = time()
    _speed = 1
    no_of_messages = 0
    _end_time = time()
    context = None

    while True:
        try:

            # Iterate over messages until timeout

            for msg_protocol in consumer.receive(timeout_millis=inactivity_time_out):

                try:

                    # This point may be not reachable if receive fails

                    with (profiler() as _metadata_timer):
                        no_of_messages += 1
                        _speed = no_of_messages / (time() - _start_time)

                        try:
                            (serializer,
                             record,
                             args, kwargs, context,
                             function_name, function_module,
                             batcher_module, batcher_function, metadata) = _get_metadata(msg_protocol,
                                                                                         adapter.serializers)

                            if adapter.override_function:
                                # Run only if a function override is set
                                if isinstance(adapter.override_function, tuple):
                                    function_module, function_name = adapter.override_function
                                elif isinstance(adapter.override_function, Callable):
                                    # Run as a router, pass job tag and function
                                    result = adapter.override_function(record.type, f"{function_module}.{function_name}")
                                    if result:
                                        function_module, function_name = result
                                    else:
                                        logger.info(f"Execution of message with function {function_module}.{function_name} is skipped.")
                                        # Ack functions that are skipped. If function is overriden. It is expected that it will be acked.
                                        consumer.acknowledge(msg_protocol)
                                        continue
                                else:
                                    raise ValueError(f"Unknown override function {adapter.override_function}. Expected tuple or callable.")

                            if adapter.override_batcher:
                                # Run only if batcher override is set
                                if isinstance(adapter.override_batcher, tuple):
                                    (batcher_module, batcher_function,
                                     metadata.min_batch_size,
                                     metadata.max_batch_size,
                                     metadata.max_time_without_flash) = adapter.override_batcher
                                elif isinstance(adapter.override_batcher, Callable):
                                    # Run as a router, pass job tag and function
                                    result = adapter.override_batcher(record.type, f"{batcher_module}.{batcher_function}")
                                    if result:
                                        (batcher_module, batcher_function,
                                         metadata.min_batch_size,
                                         metadata.max_batch_size,
                                         metadata.max_time_without_flash) = result
                                else:
                                    raise ValueError(f"Unknown batcher override function {adapter.override_function}. Expected tuple or callable.")

                        except (RecursionError, UnpicklingError) as e:
                            logger.critical(
                                f"ACK: Failed to deserialize message. Reason: {str(e)}. Message {msg_protocol.value()} is acked.",
                                e,
                                extra=ExtraInfo.exact(origin="function-worker"))

                            # TODO could do some recording of failed messages.
                            consumer.acknowledge(msg_protocol)
                            continue
                        except Exception as e:
                            logger.error(
                                f"UNACK: Could not load functions {msg_protocol.properties()}. Details: {str(e)}.", e,
                                extra=ExtraInfo.exact(origin="function-worker"))
                            # Not Ack
                            consumer.negative_acknowledge(msg_protocol)
                            continue

                    with profiler() as exec_timer:
                        # Run function
                        result = await run(function_module, function_name, args, kwargs, context)

                    if not (batcher_function and batcher_module):
                        # No need to bulk. Batch function is not executed. ACK now

                        with profiler() as ack_timer:
                            _ack(consumer, [msg_protocol])

                        _metadata_time = _metadata_timer['duration']
                        _ack_time = ack_timer['duration']
                        _exec_time = exec_timer['duration']
                        _full_time = _metadata_time + _exec_time + _ack_time
                        _process_time = _metadata_time + _exec_time + _ack_time
                        _max_process = 1 / _process_time

                        _ack(consumer, [msg_protocol])

                        # Run batch check every 10 sec.
                        if time() - _global_timer >= 10:
                            _global_timer = time()

                            async for batch_status in batcher.check_if_any_of_batches_needs_a_flush():
                                await _batch_flushing(consumer,
                                                      msg_protocol,
                                                      batch_status,
                                                      (_speed, _time_passed, _time_not_consumed_time),
                                                      batcher_db)
                            logger.info(
                                f"single-message-stats: "
                                f"1/1: "
                                f"Metadata {_metadata_time:.6f}: "
                                f"Running +{_exec_time:.3f}s: "
                                f"Ack +{_ack_time:.4f}s: "
                                f"Full {_full_time:.2f}s: "
                                f"Speed {_speed:.2f}mps of {_max_process:.2f}mps ({(_speed / _max_process) * 100:.1f}%) "
                                f"Single \"{function_module}.{function_name}\" "
                                f"In context: {context}",
                                extra=ExtraInfo.exact(origin="background-worker", package=__name__,
                                                      class_name='start_worker')
                            )

                        continue

                    # Store batcher for this function
                    batcher_db.add(function_module, function_name, (batcher_module, batcher_function))

                    key = (function_module, function_name, context.tenant, context.production)

                    # Times must be fetched before adding.
                    _, _time_passed, _time_not_consumed_time = batcher.get_stats(
                        key,
                        max_time_without_flash=metadata.max_time_without_flash)

                    # Add to batch
                    with batcher.add(
                            result,
                            key=key,
                            message=msg_protocol,
                            metadata=metadata
                    ) as batch_status:

                        logger.debug(f"{context.tenant}, Batching result of {function_module}:{function_name}",
                                     extra=ExtraInfo.exact(origin="background-worker", package=__name__,
                                                           class_name='start_worker'))

                        await _batch_flushing(consumer,
                                              msg_protocol,
                                              batch_status,
                                              (_speed, _time_passed, _time_not_consumed_time),
                                              batcher_db)

                except Exception as e:
                    logger.error(f"Message: {str(e)}, Payload {record}, Function: {function_module}.{function_name}", e,
                                 extra=ExtraInfo.exact(origin="function-worker",
                                                       package=function_module,
                                                       class_name=function_name))
                    # TODO fall back
                    _ack(consumer, [msg_protocol])

                finally:
                    if log_processor:
                        await log_processor(log_handler, context)

        except ClientTimeOutError as e:
            logger.debug("Time-out")
            await _invoke_batches(
                (_speed, 1, 1),
                batcher_db,
                batcher.flush_all(),
                consumer,
                ack_messages=ack_the_whole_batch)
            # reset counters
            _start_time = time()
            no_of_messages = 0
        except Exception as e:
            logger.error(str(e), extra=ExtraInfo.exact(origin="background-worker", package=__name__,
                                                       class_name='start_worker'))

        finally:
            logger.debug(f"Finished with {no_of_messages} messages")
            _end_time = time()
            if no_of_messages > 10000:
                # reset counters
                _start_time = time()
                no_of_messages = 0


def get_consumer_adapter(queue_tenant,
                         subscription_name: str,
                         consumer_name: str,
                         queue_type_name: str,
                         message_function: Optional[Union[Callable,Tuple[str, str]]]=None,
                         batch_function: Union[Callable, Optional[Tuple[Optional[str], Optional[str], int, int, int]]] = None,
                         init_function: Optional[Tuple[str, str]] = None):

    adapter = DeferAdapterSelector().get(queue_type_name, queue_tenant)

    data_bus = adapter.adapter_protocol.data_bus()
    data_bus.subscription.subscription_name = subscription_name
    data_bus.subscription.consumer_name = consumer_name

    if init_function is not None:
        adapter.init_function = init_function

    if message_function is not None:
        adapter.override_function = message_function

    if batch_function is not None:
        adapter.override_batcher = batch_function

    return adapter


def get_consumer_function_setting(function):
    if not isinstance(function, Callable):
        raise ValueError("Function must be callable.")
    return (function.__module__, function.__name__)