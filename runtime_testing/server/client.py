import asyncio

from . import receive_data, send_data


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while True:
            request = await receive_data(reader)
            await send_data(writer, request)
    except asyncio.exceptions.IncompleteReadError:
        print(f"Client disconnected gracefully (IncompleteReadError).")