import asyncio

from colorama import Fore, init

from db import DB, Definitions
from websocket import Websocket

if __name__ == "__main__":
    init()

    try:
        db = DB()
        websocket = Websocket(db, Definitions())
        asyncio.run(websocket.serve())
    except KeyboardInterrupt as _:
        print(f"{Fore.RESET}Ending due to KeyboardInterrupt")
