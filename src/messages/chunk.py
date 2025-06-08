from typing import Any
from messages.base import BaseHandler


class ChunkRequest(BaseHandler):
    async def act(self, ip: str = "Unknown", dimension: str = "", cx: int | None = None, cz: int | None = None, **kwargs: list[Any]) -> dict[str, Any] | None:
        if self.ws.session is None or cx is None or cz is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        chunk: tuple[int, int, int, int, int, int, int] | None = self.ws.db.chunks.get(server.id, self.ws.de.Dimension(self.ws.db, dimension).id, cx, cz)

        if chunk is None:
            return {
                "id": "ChunkData",
                "ip": ip,
                "dimension": dimension,
                "cx": cx,
                "cz": cz,
            }


# class ChunkData(BaseHandler):
#     async def act(self, ip=None, dimension=None, cx=None, cz=None, blockKeys=None, biomeKey=None, height=None, **kwargs) -> dict[str, Any] | None:
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

#         server.set_chunk(Coordinate(dimension, cx, height, cz), Chunk(blockKeys, biomeKey))
