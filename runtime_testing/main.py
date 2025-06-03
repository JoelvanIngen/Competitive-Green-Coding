import asyncio

from config import HOST, PORT
from server import handle_client


async def run_server() -> None:
    server = await asyncio.start_server(handle_client, HOST, PORT)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server())
