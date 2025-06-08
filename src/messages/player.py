from typing import Any
from messages.base import BaseHandler


class PlayerJoin(BaseHandler):
    async def act(self, ip: str = "Unknown", uuid: str | None = None, **kwargs: list[Any]):
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.ServerPlayer(self.ws.db, self.ws.session.player, server)
        # TODO: Update last seen of server player
        # TODO: Server uptime here maybe?


class PlayerQuit(BaseHandler):
    async def act(self, ip: str = "Unknown", uuid: str | None = None, **kwargs: list[Any]):
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.ServerPlayer(self.ws.db, self.ws.session.player, server)
        # TODO: Update last seen of server player


class PlayerRespawn(BaseHandler):
    async def act(self, ip: str = "Unknown", uuid: str | None = None, **kwargs: list[Any]):
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.ServerPlayer(self.ws.db, self.ws.session.player, server)
        # TODO: Update last seen of server player
        # TODO: Maybe add a death counter to ServerPlayer?


# class PlayerAdvancement(BaseHandler):
#     async def act(self, ip=None, uuid=None, advancement=None, **kwargs):
#         if self.session is None or self.session == "":
#             return None

#         server: Server = Server(self.websocket, ip)
#         self.datastore.add_server(server)

#         server = None
#         for s in self.datastore.servers:
#             if s.ip == ip:
#                 server = s

#         if server is None:
#             return

#         sPlayer = None
#         for p in server.players:
#             if p.player.uuid == uuid:
#                 sPlayer = p
#                 break

#         if sPlayer is None:
#             return

#         sPlayer.add_advancement(advancement)
