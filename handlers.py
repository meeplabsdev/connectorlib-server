import json
from datetime import datetime, timezone

from definitions import Coordinate, Player, Server, ServerPlayer
from messages import auth, data

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


HANDLERS = {"IdentityRequest": auth.IdentityRequest, "IdentityChallenge": auth.IdentityChallenge, "DataRequest": data.DataRequest, "NetworkData": data.NetworkData, "PositionData": data.PositionData}
