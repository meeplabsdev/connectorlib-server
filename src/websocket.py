import json
from typing import Any

import websockets
from colorama import Fore
from websockets import server as wserver

from db import DB


class Websocket:
    db: DB
    server: wserver.WebSocketServer

    def __init__(self, db: DB):
        self.db = db

    async def handler(self, websocket: wserver.WebSocketServerProtocol):
        async for message in websocket:
            data: dict[str, Any] = json.loads(message)
            id = data.pop("id", "")
            session = data.pop("session", "")

            try:
                # TODO: check session
                if False:
                    session = ""

                extra = ""
                if session != "":
                    extra += "(Authenticated)"

                print(f"{Fore.LIGHTBLUE_EX}|← {id}{Fore.LIGHTBLACK_EX} {extra}{Fore.RESET}")
                for k in data.keys():
                    if k != "authRequired":
                        item: Any = data.get(k)
                        if type(item) is list and len(item) > 1:
                            r = f"[{item[0]}, ...]"
                        else:
                            r = item
                        print(f"   {k}: {r}")

                resp: dict[str, Any] | None = None
                # resp = await HANDLERS.get(
                #     id,
                #     BaseHandler,
                # )(
                #     DATASTORE,
                #     websocket,
                #     session,
                # ).act(**data)

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
                    await websocket.send(json.dumps(resp))

            except Exception as e:
                print(e)

    async def serve(self):
        self.server = await websockets.serve(self.handler, "localhost", 3000)  # type: ignore
        print(f"{Fore.LIGHTGREEN_EX}Server Ready!{Fore.RESET}")
        await self.server.wait_closed()  # type: ignore
