import asyncio
import struct

from .config import MAX_STREAM_SIZE, SIZE_BYTES, SIZE_FMT


def size_valid(size: int) -> bool:
    return size <= MAX_STREAM_SIZE


async def receive_size(reader: asyncio.StreamReader) -> int:
    """
    Reads and returns the size of an incoming stream
    """

    data = await reader.readexactly(SIZE_BYTES)

    try:
        size = struct.unpack(SIZE_FMT, data)[0]
        if not isinstance(size, int):
            raise TypeError(f"Size {data.decode()} is not an integer")
        return size
    except Exception as e:
        # TODO: Find out possible errors
        raise e


async def receive_data(reader: asyncio.StreamReader) -> bytes:
    """
    Reads incoming data from stream reader
    """

    size = await receive_size(reader)
    if not size_valid(size):
        # TODO: Error, send error code, whatever
        raise Exception(f'Invalid size of {size}')

    return await reader.readexactly(size)


async def send_data(writer: asyncio.StreamWriter, data: bytes) -> None:
    writer.write(data)
    await writer.drain()
