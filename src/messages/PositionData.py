from datetime import datetime, timezone
from typing import Any

from messages.BaseHandler import BaseHandler


class PositionData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        dimension: str = "",
        pos: list[int] | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None or pos is None or len(pos) != 3:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        s_player = self.ws.de.ServerPlayer(
            self.ws.db,
            self.ws.session.player,
            server,
        )
        # TODO: update the last seen of the server_player and player
        self.ws.de.Location(
            self.ws.db,
            s_player,
            self.ws.de.Dimension(self.ws.db, dimension),
            pos[0],
            pos[1],
            pos[2],
        )
        # TODO: update the last seen of the location
