from messages.base import BaseHandler
from definitions import Server, ServerPlayer, Coordinate
from datetime import timezone, datetime

# class ServerUpdate(BaseHandler):
#     async def act(self, ip, uuid, location):
#         server: Server = Server(self.websocket, ip)
#         self.datastore.add_server(server)

#         player: Player = None
#         for p in self.datastore.players:
#             if p.uuid.hex == uuid.replace("-", ""):
#                 player = p
#                 break

#         if player is None:
#             return

#         server = None
#         for s in self.datastore.servers:
#             if s.ip == ip:
#                 server = s

#         if server is None:
#             return

#         found = False
#         for p in server.players:
#             if p.player.uuid.hex == uuid.replace("-", ""):
#                 p.set_seen(self.websocket, datetime.now(timezone.utc))
#                 p.set_location(self.websocket, Coordinate(0, 0, 0).load(location))
#                 found = True
#                 break

#         if not found:
#             server.add_player(
#                 self.websocket,
#                 ServerPlayer(
#                     self.websocket,
#                     player,
#                     Coordinate(0, 0, 0).load(location),
#                 ),
#             )


class NetworkData(BaseHandler):
    async def act(self, ip=None, user_agent=None, encoding=None, mime=None, via=None, forwarded=None, language=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        self.player.add_network_data(
            {
                "ip": ip,
                "user_agent": user_agent,
                "encoding": encoding,
                "mime": mime,
                "via": via,
                "forwarded": forwarded.split(","),
            }
        )


class PositionData(BaseHandler):
    async def act(self, ip=None, dimension=None, x=None, y=None, z=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        server: Server = Server(self.websocket, ip)
        self.datastore.add_server(server)

        server = None
        for s in self.datastore.servers:
            if s.ip == ip:
                server = s

        if server is None:
            return

        found = False
        for p in server.players:
            if p.player.uuid == self.player.uuid:
                p.set_location(self.websocket, Coordinate(dimension, x, y, z))
                p.set_seen(self.websocket, datetime.now(timezone.utc))

                found = True
                break

        if not found and self.player is not None:
            server.add_player(
                self.websocket,
                ServerPlayer(
                    self.websocket,
                    self.player,
                    Coordinate(dimension, x, y, z),
                ),
            )


class ChatData(BaseHandler):
    async def act(self, ip=None, message=None, sender=None, recipient=None, **kwargs):
        if self.session is None or self.session == "":
            return None


class SystemChatData(BaseHandler):
    async def act(self, ip=None, message=None, recipient=None, **kwargs):
        if self.session is None or self.session == "":
            return None


class DataRequest(BaseHandler):
    async def act(self, **kwargs):
        if self.session is None or self.session == "":
            return None

        response = {
            "id": "DataResponse",
        }

        response.update(self.datastore.dump())
        return response
