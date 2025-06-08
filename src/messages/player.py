from typing import Any
from messages.base import BaseHandler


class PlayerJoin(BaseHandler):
    async def act(self, ip: str = "Unknown", uuid: str | None = None, **kwargs: list[Any]) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.ServerPlayer(self.ws.db, self.ws.session.player, server)
        # TODO: Update last seen of server player
        # TODO: Server uptime here maybe?


class PlayerQuit(BaseHandler):
    async def act(self, ip: str = "Unknown", uuid: str | None = None, **kwargs: list[Any]) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.ServerPlayer(self.ws.db, self.ws.session.player, server)
        # TODO: Update last seen of server player


class PlayerRespawn(BaseHandler):
    async def act(self, ip: str = "Unknown", uuid: str | None = None, **kwargs: list[Any]) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        self.ws.de.ServerPlayer(self.ws.db, self.ws.session.player, server)
        # TODO: Update last seen of server player
        # TODO: Maybe add a death counter to ServerPlayer?
