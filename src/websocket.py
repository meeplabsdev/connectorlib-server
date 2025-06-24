import json
from typing import Any

import websockets
from colorama import Fore
from websockets import server as wserver
from messages.base import BaseHandler
from handlers import HANDLERS

from db import DB, Definitions


class Websocket:
    db: DB
    de: Definitions
    server: wserver.WebSocketServer
    session: Definitions.Session | None = None

    def __init__(self, db: DB, definitions: Definitions):
        self.db = db
        self.de = definitions

    async def handler(self, websocket: wserver.WebSocketServerProtocol):
        async for message in websocket:
            data: dict[str, Any] = json.loads(message)
            id = data.pop("id", "")
            sess = data.pop("session", "")

            try:
                # TODO: check session
                if False:
                    sess = ""

                extra = ""
                if sess != "":
                    extra += "(Authenticated)"

                print(f"{Fore.LIGHTBLUE_EX}|← {id}{Fore.LIGHTBLACK_EX} {extra}{Fore.RESET}")
                for k in data.keys():
                    if k != "authRequired":
                        item: dict[str, Any] | list[dict[str, Any]] = data.get(k, {})
                        if type(item) is list and len(item) > 1:
                            r = f"[{item[0]}, ...]"
                        else:
                            r = item
                        print(f"   {k}: {r}")

                resp: dict[str, Any] = await HANDLERS.get(  # type: ignore
                    id,
                    BaseHandler,
                )(
                    self,
                ).act(**data)

                if resp is not None:  # type: ignore
                    id = resp.pop("id", "")

                    print(f"{Fore.LIGHTRED_EX}|→ {id}{Fore.RESET}")
                    for k in resp.keys():
                        if k != "authRequired":
                            item: dict[str, Any] | list[dict[str, Any]] = resp.get(k, {})
                            if type(item) is list and len(item) > 1:
                                r = f"[{item[0]}, ...]"
                            else:
                                r = item
                            print(f"   {k}: {r}")

                    resp["id"] = id
                    await websocket.send(json.dumps(resp))

            except Exception as e:
                raise e

    async def serve(self):
        self.server = await websockets.serve(self.handler, "localhost", 3000)  # type: ignore
        print(f"{Fore.LIGHTGREEN_EX}Server Ready!{Fore.RESET}")
        await self.server.wait_closed()  # type: ignore
