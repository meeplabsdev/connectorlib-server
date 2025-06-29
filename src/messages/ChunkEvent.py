from typing import Any
from messages.BaseHandler import BaseHandler


class ChunkData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        cx: int | None = None,
        cz: int | None = None,
        dimension: str = "",
        biomeKey: str = "",
        height: int | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None or cx is None or cz is None or height is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.Chunk(
            self.ws.db,
            server,
            self.ws.de.Dimension(self.ws.db, dimension),
            self.ws.de.Biome(self.ws.db, biomeKey),
            height,
            cx,
            cz,
        )
