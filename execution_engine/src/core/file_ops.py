import asyncio
import tempfile


async def create_tmp_dir() -> str:
    """
    Creates a unique, temporary directory without blocking the main thread
    """

    return await asyncio.to_thread(tempfile.mkdtemp)
