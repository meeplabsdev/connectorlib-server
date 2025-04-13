from messages.base import BaseHandler
from definitions import Coordinate, Server, Chunk


class ChunkRequest(BaseHandler):
    async def act(self, ip=None, dimension=None, cx=None, cz=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        needThatChunk = True
        if needThatChunk:
            return {
                "id": "ChunkData",
                "ip": ip,
                "dimension": dimension,
                "cx": cx,
                "cz": cz,
            }


class ChunkData(BaseHandler):
    async def act(self, ip=None, dimension=None, cx=None, cz=None, blockKeys=None, biomeKey=None, height=None, **kwargs):
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

        server.set_chunk(Coordinate(dimension, cx, height, cz), Chunk(blockKeys, biomeKey))
