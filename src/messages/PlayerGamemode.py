from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerGamemode(BaseHandler):
    async def act(
        self,
        gamemode: str = "unknown",
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
