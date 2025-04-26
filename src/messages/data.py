from datetime import datetime, timezone

from messages.base import BaseHandler


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


# class PositionData(BaseHandler):
#     async def act(self, ip=None, dimension=None, x=None, y=None, z=None, **kwargs):
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

#         found = False
#         for p in server.players:
#             if p.player.uuid == self.player.uuid:
#                 p.set_location(self.websocket, Coordinate(dimension, x, y, z))
#                 p.set_seen(self.websocket, datetime.now(timezone.utc))

#                 found = True
#                 break

#         if not found and self.player is not None:
#             server.add_player(
#                 ServerPlayer(
#                     self.websocket,
#                     self.player,
#                     Coordinate(dimension, x, y, z),
#                 ),
#             )


# class ChatData(BaseHandler):
#     async def act(self, ip=None, message=None, sender=None, recipient=None, **kwargs):
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
#             if p.player.uuid == self.player.uuid:
#                 sPlayer = p
#                 break

#         if sPlayer is None:
#             return

#         if recipient != "":
#             sPlayer.add_pm(f"{sender} -> {recipient}: {message}")
#             sPlayer.add_chat(f"{sender} -> {recipient}: {message}")
#         else:
#             sPlayer.add_chat(f"{sender}: {message}")


# class SystemChatData(BaseHandler):
#     async def act(self, ip=None, message=None, recipient=None, **kwargs):
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
#             if p.player.uuid == self.player.uuid:
#                 sPlayer = p
#                 break

#         if sPlayer is None:
#             return

#         sPlayer.add_pm(f"!! -> {recipient}: {message}")
#         sPlayer.add_chat(f"!! -> {recipient}: {message}")
