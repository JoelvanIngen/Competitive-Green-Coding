import asyncio
import os

from execution_engine.docker_handler import run
from execution_engine.docker_handler.runconfig import RunConfig

_N_WORKERS = os.cpu_count()
_WORKER_QUEUE: asyncio.Queue[int] = asyncio.Queue()


def init():
    for worker_id in range(_N_WORKERS):
        _WORKER_QUEUE.put_nowait(worker_id)


async def schedule_run(config: RunConfig):
    # Get available worker or wait for one
    cpu_id = await _WORKER_QUEUE.get()
    config.cpu = cpu_id

    # Run task and ensure worker return
    try:
        return await run(config)
    finally:
        _WORKER_QUEUE.put_nowait(cpu_id)
