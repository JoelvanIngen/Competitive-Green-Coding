import asyncio
import os
import shutil
import tempfile

from loguru import logger

from execution_engine.config import TEMP_DIR_PREFIX


async def create_tmp_dir() -> str:
    """
    Creates a unique, temporary directory without blocking the main thread
    """
    return await asyncio.to_thread(
        lambda: tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX))


async def delete_tmp_dir(path: str) -> None:
    if os.path.exists(path):
        await asyncio.to_thread(shutil.rmtree, path)
    else:
        logger.warning(f"Attempted to delete {path} but it does not exist")
