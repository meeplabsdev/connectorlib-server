from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerPing(BaseHandler):
    async def act(
        self,
        ping: int = 0,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
