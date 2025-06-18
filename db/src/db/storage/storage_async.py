import asyncio
import io
from typing import AsyncGenerator


async def tar_stream_generator(
    buff: io.BytesIO, chunk_size: int = 8192
) -> AsyncGenerator[bytes, None]:
    """
    Splits the contents into chunks of size chunk_size.
    """

    while True:
        chunk = buff.read(chunk_size)
        if not chunk:
            break
        yield chunk

        # Yield control to event loop to prevent blockage of main thread
        await asyncio.sleep(0)
