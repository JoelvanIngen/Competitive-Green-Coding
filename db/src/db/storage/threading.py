import asyncio


def to_thread(func):
    async def decorator(*args, **kwargs):
        await asyncio.to_thread(func, *args, **kwargs)

    return decorator
