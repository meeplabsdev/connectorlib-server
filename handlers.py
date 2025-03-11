import json
from datetime import datetime, timezone

from definitions import Coordinate, DataStore, Player, Server, ServerPlayer


class BaseHandler:
    datastore: DataStore

    def __init__(self, datastore: DataStore, websocket):
        self.datastore = datastore
        self.websocket = websocket


class GetDataStore(BaseHandler):
    async def act(self):
        await self.websocket.send(json.dumps(self.datastore.dump()))


class PlayerLoad(BaseHandler):
    async def act(self, uuid, name):
        player: Player = Player(self.websocket, uuid, name)
        self.datastore.add_player(player)


class ServerUpdate(BaseHandler):
    async def act(self, ip, uuid, location):
        server: Server = Server(self.websocket, ip)
        self.datastore.add_server(server)

        player: Player = None
        for p in self.datastore.players:
            if p.uuid.hex == uuid.replace("-", ""):
                player = p
                break

        if player is None:
            return

        server = None
        for s in self.datastore.servers:
            if s.ip == ip:
                server = s

        if server is None:
            return

        found = False
        for p in server.players:
            if p.player.uuid.hex == uuid.replace("-", ""):
                p.set_seen(self.websocket, datetime.now(timezone.utc))
                p.set_location(self.websocket, Coordinate(0, 0, 0).load(location))
                found = True
                break

        if not found:
            server.add_player(
                self.websocket,
                ServerPlayer(
                    self.websocket,
                    player,
                    Coordinate(0, 0, 0).load(location),
                ),
            )


HANDLERS = [GetDataStore, PlayerLoad, ServerUpdate]
