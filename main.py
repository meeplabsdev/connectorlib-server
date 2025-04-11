import asyncio
import json

import websockets
from definitions import DataStore
from handlers import HANDLERS
from messages.base import BaseHandler
from colorama import init, Fore

init()

DATASTORE = DataStore().loadfile("datastore.json")


async def save_datastore():
    while True:
        await asyncio.sleep(30)
        DATASTORE.dumpfile("datastore.json")


async def prune_sessions(server):
    while True:
        await asyncio.sleep(30)
        if len(server.websockets) == 0:
            DATASTORE.sessions = []


async def handler(websocket):
    async for message in websocket:
        data: dict = json.loads(message)
        id = data.pop("id", "")
        session = data.pop("session", "")

        if session not in DATASTORE.sessions:
            session = ""

        try:
            extra = ""
            if session != "":
                extra += "(Authenticated)"

            print(f"{Fore.LIGHTBLUE_EX}|← {id}{Fore.LIGHTBLACK_EX} {extra}{Fore.RESET}")
            for k in data.keys():
                if k != "authRequired":
                    print(f"   {k}: {data.get(k)}")

            resp = await HANDLERS.get(
                id,
                BaseHandler,
            )(
                DATASTORE,
                websocket,
                session,
            ).act(**data)

            if resp is not None:
                id = resp.get("id", "")

                print(f"{Fore.LIGHTRED_EX}|→ {id}{Fore.RESET}")
                for k in resp.keys():
                    if k != "authRequired":
                        print(f"   {k}: {resp.get(k)}")

                resp: dict = json.dumps(resp)
                await websocket.send(resp)

        except Exception as _:
            pass


async def main():
    server = await websockets.serve(handler, "localhost", 3000)
    prune_task = asyncio.create_task(prune_sessions(server))
    save_task = asyncio.create_task(save_datastore())
    print(f"{Fore.LIGHTGREEN_EX}Server Ready!{Fore.RESET}")

    await asyncio.gather(server.wait_closed(), prune_task, save_task)


if __name__ == "__main__":
    asyncio.run(main())
