from typing import Any
from messages.BaseHandler import BaseHandler


class ChunkRequest(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        dimension: str = "",
        cx: int | None = None,
        cz: int | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None or cx is None or cz is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        chunk: tuple[int, int, int, int, int, int, int] | None = self.ws.db.chunks.get(
            server.id,
            self.ws.de.Dimension(self.ws.db, dimension).id,
            cx,
            cz,
        )

        if chunk is None:
            return {
                "id": "ChunkData",
                "ip": ip,
                "dimension": dimension,
                "cx": cx,
                "cz": cz,
            }


class ChunkData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        dimension: str = "",
        cx: int | None = None,
        cz: int | None = None,
        blockKeys: list[str] = [],
        biomeKey: str = "",
        height: int | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None or cx is None or cz is None or height is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        chunk = self.ws.de.Chunk(
            self.ws.db,
            server,
            self.ws.de.Dimension(self.ws.db, dimension),
            self.ws.de.Biome(self.ws.db, biomeKey),
            height,
            cx,
            cz,
        )
        for i, block in enumerate(blockKeys):
            # The blocks are listed like:
            # (x=0, z=0, block=name)
            # (x=0, z=1, block=name)
            # ...
            # (x=0, z=15, block=name)
            # (x=1, z=0, block=name)
            # (x=1, z=1, block=name)
            # ...
            # (x=15, z=15, block=name)
            # but given in an array of just the names

            x = i // 16
            z = i % 16

            self.ws.de.SurfaceBlock(
                self.ws.db,
                chunk,
                self.ws.de.Block(self.ws.db, block),
                height,
                x,
                z,
            )
