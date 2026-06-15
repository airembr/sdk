from pararun.model.transport_context import TransportContext
from pararun.service.logger.log_handler import DeferLogHandler

from airembr.model.system.context import ServerContext, Context
from airembr.system.process.logging.log_controller import log_controller
from airembr.system.process.logging.log_handler import log_handler as sys_log_handler
from airembr.system.adapter.bigdata.big_data_adapter import *


async def _get_logs(handler):
    async with log_controller(handler, min_size=None) as deferpy_logs:

        if not deferpy_logs:
            deferpy_logs = []

        # Handles System Logs (all  libs, etc)
        async with log_controller(sys_log_handler, min_size=None) as system_logs:

            if system_logs:
                return system_logs + deferpy_logs
            return deferpy_logs


async def logging(handler: DeferLogHandler, context: TransportContext):
    if context is None:
        print(handler.collection)
    else:
        with ServerContext(Context(**context.as_context())):
            async with log_controller(handler, min_size=None) as deferpy_logs:

                if not deferpy_logs:
                    deferpy_logs = []

                # Handles System Logs (all  libs, etc)
                async with log_controller(sys_log_handler, min_size=None) as system_logs:

                    if system_logs:
                        logs = system_logs + deferpy_logs
                        # TODO save in queue
                        await bd_log_adapter.save_logs(logs)
                    else:
                        # TODO save in queue
                        await bd_log_adapter.save_logs(deferpy_logs)
