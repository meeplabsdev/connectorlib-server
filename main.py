import asyncio
import websockets
import websockets.server

from definitions import DataStore
from handlers import HANDLERS

DATASTORE = DataStore().loadfile("datastore.json")


async def save_datastore():
    while True:
        DATASTORE.dumpfile("datastore.json")
        await asyncio.sleep(30)


async def handler(websocket):
    async for message in websocket:
        opcode, *args = message.split("|")
        try:
            print(f"{opcode=}, {args=}")
            await HANDLERS[int(opcode)](DATASTORE, websocket).act(*args)
        except Exception as e:
            print(e)


async def main():
    hello_world_task = asyncio.create_task(save_datastore())
    server = await websockets.serve(handler, "localhost", 3000)

    await asyncio.gather(server.wait_closed(), hello_world_task)


if __name__ == "__main__":
    asyncio.run(main())
