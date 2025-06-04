import asyncio
import os
import tempfile


async def create_tmp_dir() -> str:
    """
    Creates a unique, temporary directory without blocking the main thread
    """
    return await asyncio.to_thread(tempfile.mkdtemp)


async def delete_tmp_dir(tmp_dir: str) -> None:
    await asyncio.to_thread(os.remove, tmp_dir)
