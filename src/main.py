import asyncio
import json

import websockets
from colorama import Fore, init

from definitions import DataStore
from handlers import HANDLERS
from messages.base import BaseHandler

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
                    if type(data.get(k)) is list and len(data.get(k)) > 1:
                        r = f"[{data.get(k)[0]}, ...]"
                    else:
                        r = data.get(k)
                    print(f"   {k}: {r}")

            resp = await HANDLERS.get(
                id,
                BaseHandler,
            )(
                DATASTORE,
                websocket,
                session,
            ).act(**data)

            if resp is not None:
                id = resp.pop("id", "")

                print(f"{Fore.LIGHTRED_EX}|→ {id}{Fore.RESET}")
                for k in resp.keys():
                    if k != "authRequired":
                        if type(resp.get(k)) is list and len(resp.get(k)) > 1:
                            r = f"[{resp.get(k)[0]}, ...]"
                        else:
                            r = resp.get(k)
                        print(f"   {k}: {r}")

                resp["id"] = id
                resp: str = json.dumps(resp)
                await websocket.send(resp)

        except Exception as e:
            print(e)


async def main():
    server = await websockets.serve(handler, "localhost", 3000)
    prune_task = asyncio.create_task(prune_sessions(server))
    save_task = asyncio.create_task(save_datastore())
    print(f"{Fore.LIGHTGREEN_EX}Server Ready!{Fore.RESET}")

    await asyncio.gather(server.wait_closed(), prune_task, save_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as _:
        print(f"{Fore.RESET}Ending due to KeyboardInterrupt")
