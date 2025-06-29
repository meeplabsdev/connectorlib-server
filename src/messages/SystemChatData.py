from typing import Any
import uuid

from messages.BaseHandler import BaseHandler


class SystemChatData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        message: str = "",
        recipient: dict[str, str] = {},
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        s_player = self.ws.de.ServerPlayer(
            self.ws.db,
            self.ws.session.player,
            server,
        )

        self.ws.de.Message(
            self.ws.db,
            s_player,
            message,
            uuid.UUID(int=0),
            uuid.UUID(list(recipient.values())[0]),
        )
